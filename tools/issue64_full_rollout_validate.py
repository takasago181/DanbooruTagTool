#!/usr/bin/env python3
"""Deterministic integrity validator for the Issue #64 full-rollout candidate.

This validates persisted evidence; it never classifies or rewrites source rows.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import lzma
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FULL_ROOT = Path("docs/issue64/full_rollout")
POPULATION_PATH = Path("docs/issue64/artifacts/population.txt")
TAXONOMY_PATH = Path("docs/issue64/taxonomy.json")
MANIFEST_PATH = FULL_ROOT / "MANIFEST.json"
PROGRESS_PATH = FULL_ROOT / "PROGRESS.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_path(value: str | None) -> tuple[str, str | None] | None:
    value = (value or "").strip()
    if not value:
        return None
    bits = value.split("/")
    if len(bits) > 2 or not bits[0] or (len(bits) == 2 and not bits[1]):
        raise ValueError(f"invalid path syntax: {value!r}")
    return bits[0], bits[1] if len(bits) == 2 else None


def canonicalize_path(path: tuple[str, str | None], taxonomy: dict[str, Any]) -> tuple[str, str | None]:
    genre_value, subgenre_value = path
    genres = taxonomy.get("genres", {})
    genre_lookup = {key.casefold(): key for key in genres}
    genre_lookup.update({value.get("label_ja", "").casefold(): key for key, value in genres.items()})
    genre = genre_lookup.get(genre_value.casefold(), genre_value.upper())
    if not subgenre_value:
        return genre, None
    known_subgenres = genres.get(genre, {}).get("subgenres", {})
    subgenre_lookup = {key.casefold(): key for key in known_subgenres}
    subgenre_lookup.update({value.casefold(): key for key, value in known_subgenres.items()})
    subgenre = subgenre_lookup.get(subgenre_value.casefold(), subgenre_value.upper())
    return genre, subgenre


def parse_secondary(value: str | None, taxonomy: dict[str, Any] | None = None) -> list[tuple[str, str | None]]:
    value = (value or "").strip()
    if not value:
        return []
    # Batches 1-3 persisted secondary paths as Japanese labels, sometimes with
    # multiple paths separated by `|`; later batches use JSON arrays.
    if not value.startswith(("[", "{")):
        if re.search(r"[|;]", value):
            result: list[tuple[str, str | None]] = []
            for piece in re.split(r"\s*[|;]\s*", value):
                result.extend(parse_secondary(piece, taxonomy))
            return result
        arrow = re.split(r"\s*(?:→|->|⇒)\s*", value)
        if len(arrow) > 1 and taxonomy:
            path = parse_path("/".join(arrow))
            return [canonicalize_path(path, taxonomy)] if path else []
    if taxonomy:
        try:
            lone_path = parse_path(value)
        except ValueError:
            lone_path = None
        if lone_path is None:
            genre_label = value.casefold()
            matches = [
                (genre, None)
                for genre, entry in taxonomy.get("genres", {}).items()
                if entry.get("label_ja", "").casefold() == genre_label
            ]
            if len(matches) == 1:
                return matches

    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        decoded = [part.strip() for part in re.split(r"[;|]", value) if part.strip()]
    if isinstance(decoded, str):
        decoded = [decoded]
    if not isinstance(decoded, list):
        raise ValueError(f"secondary paths must be a JSON list or path string: {value!r}")
    result = []
    for item in decoded:
        if isinstance(item, dict):
            genre = item.get("genre_id") or item.get("genre") or item.get("primary_genre_id")
            subgenre = item.get("subgenre_id") or item.get("subgenre") or item.get("primary_subgenre_id")
            if not isinstance(genre, str) or not genre:
                raise ValueError(f"secondary path has no genre: {item!r}")
            path = (genre, subgenre or None)
            result.append(canonicalize_path(path, taxonomy) if taxonomy else path)
        elif isinstance(item, str):
            parsed = parse_path(item)
            if parsed is None:
                raise ValueError("empty secondary path")
            result.append(canonicalize_path(parsed, taxonomy) if taxonomy else parsed)
        else:
            raise ValueError(f"unsupported secondary path value: {item!r}")
    return result


def normalize_row(row: dict[str, str], implied_global_row: int, taxonomy: dict[str, Any] | None = None) -> dict[str, Any]:
    global_value = row.get("global_row", "").strip()
    global_row = int(global_value) if global_value else implied_global_row
    canonical = row.get("canonical", "").strip()
    status = (row.get("classification_status") or "").strip().upper()
    confidence = (row.get("confidence") or "").strip().upper()

    if "primary_path" in row:
        primary = parse_path(row.get("primary_path"))
    else:
        genre = (row.get("primary_genre_id") or row.get("primary_genre") or "").strip()
        subgenre = (row.get("primary_subgenre_id") or row.get("primary_subgenre") or "").strip()
        primary = (genre, subgenre or None) if genre else None
    if primary and taxonomy:
        primary = canonicalize_path(primary, taxonomy)

    secondary_text = row.get("secondary_paths")
    if secondary_text is None:
        secondary_text = row.get("secondary_path")
    secondary = parse_secondary(secondary_text, taxonomy)

    return {
        "global_row": global_row,
        "canonical": canonical,
        "status": status,
        "primary_path": primary,
        "secondary_paths": secondary,
        "confidence": confidence,
        "reason": row.get("reason_ja") or row.get("classification_reason") or "",
    }


def _ledger_bytes(root: Path, batch: dict[str, Any]) -> tuple[bytes, bytes, list[str]]:
    issues: list[str] = []
    if "parts" in batch:
        encoded = bytearray()
        for part in batch["parts"]:
            text = (root / part["path"]).read_bytes()
            actual_text_hash = sha256(text)
            if actual_text_hash != part.get("base64_text_sha256"):
                issues.append(
                    f"fragment {part['path']} base64_text_sha256 mismatch: "
                    f"expected {part.get('base64_text_sha256')} actual {actual_text_hash}"
                )
            try:
                decoded_part = base64.b64decode(text, validate=True)
            except Exception as exc:
                raise ValueError(f"cannot base64-decode {part['path']}: {exc}") from exc
            if len(decoded_part) != int(part.get("decoded_size", len(decoded_part))):
                issues.append(f"fragment {part['path']} decoded_size mismatch")
            expected_hash = part.get("decoded_sha256")
            if expected_hash and sha256(decoded_part) != expected_hash:
                issues.append(f"fragment {part['path']} decoded_sha256 mismatch")
            encoded.extend(text)
        try:
            xz_data = base64.b64decode(bytes(encoded), validate=True)
        except Exception as exc:
            raise ValueError(f"cannot reconstruct xz from fragments: {exc}") from exc
    else:
        xz_data = (root / batch["path"]).read_bytes()

    expected_xz = batch.get("xz_sha256")
    actual_xz = sha256(xz_data)
    if expected_xz and actual_xz != expected_xz:
        issues.append(f"xz_sha256 mismatch: expected {expected_xz} actual {actual_xz}")
    raw = lzma.decompress(xz_data)
    expected_raw = batch.get("raw_csv_sha256")
    actual_raw = sha256(raw)
    if expected_raw and actual_raw != expected_raw:
        issues.append(f"raw_csv_sha256 mismatch: expected {expected_raw} actual {actual_raw}")
    return xz_data, raw, issues


def _taxonomy_path_error(path: tuple[str, str | None], taxonomy: dict[str, Any]) -> str | None:
    genre, subgenre = path
    genres = taxonomy.get("genres", {})
    if genre not in genres:
        return f"unknown genre {genre}"
    if subgenre and subgenre not in genres[genre].get("subgenres", {}):
        return f"unknown subgenre {genre}/{subgenre}"
    return None


def _validate_summary(
    summary: dict[str, Any], rows: list[dict[str, Any]], batch_no: int, manifest_range: list[int]
) -> list[str]:
    errors: list[str] = []
    declared_count = summary.get("count", summary.get("source_row_count"))
    if declared_count is not None and int(declared_count) != len(rows):
        errors.append(f"summary count {declared_count} != ledger count {len(rows)}")
    status_counts = Counter(row["status"] for row in rows)
    confidence_counts = Counter(row["confidence"] for row in rows)
    for labels, observed in ((("status_counts", "result"), status_counts), (("confidence_counts", "confidence"), confidence_counts)):
        label = next((candidate for candidate in labels if isinstance(summary.get(candidate), dict)), None)
        declared = summary.get(label) if label else None
        if not isinstance(declared, dict):
            errors.append(f"summary has no {labels[0]} or compatible {labels[1]}")
            continue
        normalized = {str(k).upper(): int(v) for k, v in declared.items()}
        actual = {key: observed.get(key, 0) for key in sorted(set(normalized) | set(observed))}
        if normalized != actual:
            errors.append(f"summary {label} mismatch: declared={normalized} actual={actual}")

    unresolved_key = "unresolved" if "unresolved" in summary else "unresolved_canonical" if "unresolved_canonical" in summary else None
    if unresolved_key:
        declared_unresolved = {
            item[-1] if isinstance(item, (list, tuple)) and item else item
            for item in summary[unresolved_key]
        }
        actual_unresolved = {row["canonical"] for row in rows if row["status"] == "UNRESOLVED"}
        if declared_unresolved != actual_unresolved:
            errors.append(
                "summary unresolved set mismatch: "
                f"declared_only={sorted(declared_unresolved - actual_unresolved)[:20]} "
                f"ledger_only={sorted(actual_unresolved - declared_unresolved)[:20]}"
            )

    declared_genres = summary.get("primary_genre_counts")
    if isinstance(declared_genres, dict):
        normalized = {str(k).upper(): int(v) for k, v in declared_genres.items()}
        actual_counts = Counter(row["primary_path"][0] for row in rows if row["primary_path"])
        actual = {key: actual_counts.get(key, 0) for key in sorted(set(normalized) | set(actual_counts))}
        if normalized != actual:
            errors.append(f"summary primary_genre_counts mismatch: declared={normalized} actual={actual}")

    declared_range = summary.get("range", summary.get("source_global_rows"))
    if declared_range is not None:
        if not isinstance(declared_range, list) or len(declared_range) != 2:
            errors.append(f"summary range is malformed: {declared_range!r}")
        else:
            try:
                normalized_range = list(map(int, declared_range))
            except (TypeError, ValueError):
                errors.append(f"summary range contains non-integer values: {declared_range!r}")
            else:
                if normalized_range != manifest_range:
                    errors.append(f"summary range {normalized_range} != manifest range {manifest_range}")
    return errors


def validate(root: Path = REPO_ROOT) -> dict[str, Any]:
    manifest = _read_json(root / MANIFEST_PATH)
    taxonomy = _read_json(root / TAXONOMY_PATH)
    raw_population = (root / POPULATION_PATH).read_bytes()
    population = raw_population.decode("utf-8-sig").splitlines()
    errors: list[str] = []
    warnings: list[str] = []
    if len(population) != int(manifest["population_count"]):
        errors.append(f"population count mismatch: {len(population)} != {manifest['population_count']}")
    if len(set(population)) != len(population):
        errors.append("population contains duplicate canonicals")
    if population != sorted(population):
        errors.append("population is not sorted")

    evidence_path = root / "docs/issue64/artifacts/population_evidence.json"
    if evidence_path.exists():
        evidence = _read_json(evidence_path)
        expected_population_hash = evidence.get("population_sha256_sorted_utf8_lf")
        if expected_population_hash and sha256(raw_population) != expected_population_hash:
            errors.append("population.txt SHA-256 does not match population_evidence.json")

    all_rows: list[dict[str, Any]] = []
    seen_canonicals: Counter[str] = Counter()
    batch_results: list[dict[str, Any]] = []
    expected_start = 1
    observed_totals = {"PROPOSED": 0, "UNRESOLVED": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    invalid_path_counts: Counter[str] = Counter()
    unreadable_batches: list[int] = []

    for batch in manifest["batches"]:
        number = int(batch["batch"])
        start, end = map(int, batch["range"])
        batch_errors: list[str] = []
        if start != expected_start or end - start + 1 != int(batch["count"]):
            batch_errors.append(
                f"range/count discontinuity: range={start}-{end}, count={batch['count']}, expected_start={expected_start}"
            )
        expected_start = end + 1
        expected_slice = population[start - 1 : end]
        if len(expected_slice) != int(batch["count"]):
            batch_errors.append("range extends outside the fixed population")

        try:
            _, raw, decode_issues = _ledger_bytes(root, batch)
            batch_errors.extend(decode_issues)
            text = io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8-sig", newline="")
            parsed = list(csv.DictReader(text))
            rows = [normalize_row(row, start + offset, taxonomy) for offset, row in enumerate(parsed)]
        except Exception as exc:
            unreadable_batches.append(number)
            batch_errors.append(f"ledger unreadable: {type(exc).__name__}: {exc}")
            rows = []

        if rows:
            if len(rows) != int(batch["count"]):
                batch_errors.append(f"ledger row count {len(rows)} != declared {batch['count']}")
            for offset, row in enumerate(rows):
                expected_row = start + offset
                if row["global_row"] != expected_row:
                    batch_errors.append(f"row {offset + 1} global_row {row['global_row']} != {expected_row}")
                if offset < len(expected_slice) and row["canonical"] != expected_slice[offset]:
                    batch_errors.append(
                        f"row {expected_row} canonical {row['canonical']!r} != population {expected_slice[offset]!r}"
                    )
                if not row["canonical"]:
                    batch_errors.append(f"row {expected_row} has empty canonical")
                seen_canonicals[row["canonical"]] += 1
                if row["status"] not in {"PROPOSED", "UNRESOLVED"}:
                    batch_errors.append(f"row {expected_row} has invalid status {row['status']!r}")
                if row["confidence"] not in {"HIGH", "MEDIUM", "LOW"}:
                    batch_errors.append(f"row {expected_row} has invalid confidence {row['confidence']!r}")
                if row["status"] == "UNRESOLVED" and row["confidence"] != "LOW":
                    batch_errors.append(f"row {expected_row} unresolved confidence is not LOW")
                if row["status"] == "PROPOSED" and row["primary_path"] is None:
                    batch_errors.append(f"row {expected_row} proposed row has no primary path")
                if row["status"] == "UNRESOLVED" and (row["primary_path"] or row["secondary_paths"]):
                    batch_errors.append(f"row {expected_row} unresolved row has a taxonomy path")
                for path in ([row["primary_path"]] if row["primary_path"] else []) + row["secondary_paths"]:
                    path_error = _taxonomy_path_error(path, taxonomy)
                    if path_error:
                        invalid_path_counts[path_error] += 1
                        batch_errors.append(f"row {expected_row}: {path_error}")
                if row["status"] in observed_totals:
                    observed_totals[row["status"]] += 1
                if row["confidence"] in observed_totals:
                    observed_totals[row["confidence"]] += 1
            all_rows.extend(rows)

            summary_path = batch.get("summary_path")
            if summary_path:
                try:
                    summary = _read_json(root / summary_path)
                    batch_errors.extend(_validate_summary(summary, rows, number, [start, end]))
                except Exception as exc:
                    batch_errors.append(f"summary unreadable: {type(exc).__name__}: {exc}")

        batch_results.append({
            "batch": number,
            "range": [start, end],
            "expected_rows": int(batch["count"]),
            "read_rows": len(rows),
            "ok": not batch_errors,
            "issues": batch_errors,
        })
        errors.extend(f"batch {number}: {item}" for item in batch_errors)

    if expected_start != int(manifest["population_count"]) + 1:
        errors.append(f"manifest ranges end at {expected_start - 1}, expected {manifest['population_count']}")

    duplicate_canonicals = sorted(key for key, count in seen_canonicals.items() if count > 1)
    if duplicate_canonicals:
        errors.append(f"duplicate canonical rows: {len(duplicate_canonicals)}; examples={duplicate_canonicals[:20]}")
    actual_set = set(seen_canonicals)
    population_set = set(population)
    missing = sorted(population_set - actual_set)
    extra = sorted(actual_set - population_set)
    if missing:
        errors.append(f"population canonicals missing from readable ledgers: {len(missing)}; examples={missing[:20]}")
    if extra:
        errors.append(f"ledger canonicals outside population: {len(extra)}; examples={extra[:20]}")

    declared_totals = manifest.get("totals", {})
    for key, expected in declared_totals.items():
        actual = observed_totals.get(key.upper(), 0)
        if len(all_rows) == int(manifest["population_count"]) and actual != int(expected):
            errors.append(f"manifest total {key}={expected} but ledger observed {actual}")
        elif len(all_rows) != int(manifest["population_count"]):
            warnings.append(f"manifest total {key}={expected} not fully verifiable ({len(all_rows)} readable rows)")

    progress_text = (root / PROGRESS_PATH).read_text(encoding="utf-8-sig")
    progress_checks = {
        "population_count": (r"exact General population:\s*\*\*([\d,]+) rows", int(manifest["population_count"])),
        "proposed": (r"PROPOSED:\s*\*\*([\d,]+)\*\*", int(declared_totals.get("proposed", -1))),
        "unresolved": (r"UNRESOLVED:\s*\*\*([\d,]+)\*\*", int(declared_totals.get("unresolved", -1))),
        "high": (r"HIGH:\s*\*\*([\d,]+)\*\*", int(declared_totals.get("high", -1))),
        "medium": (r"MEDIUM:\s*\*\*([\d,]+)\*\*", int(declared_totals.get("medium", -1))),
        "low": (r"LOW:\s*\*\*([\d,]+)\*\*", int(declared_totals.get("low", -1))),
    }
    for label, (pattern, expected) in progress_checks.items():
        match = re.search(pattern, progress_text)
        if not match:
            errors.append(f"PROGRESS missing {label} checkpoint field")
        elif int(match.group(1).replace(",", "")) != expected:
            errors.append(f"PROGRESS {label}={match.group(1)} != MANIFEST {expected}")

    source_hash = manifest.get("working_source_sha256")
    population_hash = sha256(raw_population)
    if source_hash and source_hash != population_hash:
        warnings.append(
            "working_source_sha256 differs from population.txt bytes; source identity/byte semantics need reconciliation"
        )

    return {
        "validator": "issue64-full-rollout-validator-v1",
        "population_count": len(population),
        "population_sha256": population_hash,
        "readable_rows": len(all_rows),
        "unreadable_batches": unreadable_batches,
        "duplicate_canonical_count": len(duplicate_canonicals),
        "missing_population_count": len(missing),
        "extra_canonical_count": len(extra),
        "invalid_path_counts": dict(invalid_path_counts),
        "observed_totals": observed_totals,
        "manifest_totals": declared_totals,
        "batch_results": batch_results,
        "warnings": warnings,
        "errors": errors,
        "pass": not errors,
    }


def validate_effective(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Validate the superseding full sidecar plus its bounded correction proof."""
    errors: list[str] = []
    warnings: list[str] = []
    effective_path = root / FULL_ROOT / "effective_sidecar.csv"
    correction_path = root / FULL_ROOT / "corrections/CORRECTION_MANIFEST.json"
    summary_path = root / FULL_ROOT / "corrections/effective_batch_summaries.json"
    taxonomy = _read_json(root / TAXONOMY_PATH)
    manifest = _read_json(root / MANIFEST_PATH)
    population_bytes = (root / POPULATION_PATH).read_bytes()
    population = population_bytes.decode("utf-8-sig").splitlines()
    population_hash = sha256(population_bytes)

    for path in (effective_path, correction_path, summary_path):
        if not path.is_file():
            errors.append(f"required effective rework artifact is missing: {path.relative_to(root)}")
    if errors:
        return {"validator": "issue64-effective-sidecar-validator-v1", "pass": False, "errors": errors}

    corrections = _read_json(correction_path)
    batch_summaries = _read_json(summary_path)
    effective_bytes = effective_path.read_bytes()
    actual_sidecar_hash = sha256(effective_bytes)
    expected_sidecar_hash = corrections.get("effective_sidecar", {}).get("sha256")
    if actual_sidecar_hash != expected_sidecar_hash:
        errors.append(f"effective sidecar SHA-256 mismatch: expected {expected_sidecar_hash}, actual {actual_sidecar_hash}")
    if int(corrections.get("effective_population_count", -1)) != len(population):
        errors.append("correction manifest effective population count mismatch")
    if corrections.get("population_sha256_sorted_utf8_lf") != population_hash:
        errors.append("correction manifest population hash mismatch")
    summary_population_hash = batch_summaries.get("population_sha256_sorted_utf8_lf")
    if summary_population_hash != population_hash:
        errors.append("effective batch summaries population hash mismatch")
    if batch_summaries.get("sidecar_sha256") != actual_sidecar_hash:
        errors.append("effective batch summaries sidecar hash mismatch")

    rows: list[dict[str, Any]] = []
    seen: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    invalid_paths: Counter[str] = Counter()
    by_batch: dict[int, list[dict[str, Any]]] = {}
    batches = manifest.get("batches", [])
    try:
        with effective_path.open("r", encoding="utf-8-sig", newline="") as stream:
            parsed = list(csv.DictReader(stream))
        for offset, raw in enumerate(parsed):
            expected_global = offset + 1
            row = normalize_row(raw, expected_global, taxonomy)
            if row["global_row"] != expected_global:
                errors.append(f"effective row {expected_global} has global_row {row['global_row']}")
            if expected_global > len(population):
                errors.append(f"effective sidecar has extra row {expected_global}")
                continue
            expected_canonical = population[offset]
            if row["canonical"] != expected_canonical:
                errors.append(f"effective row {expected_global} canonical differs from population")
            seen[row["canonical"]] += 1
            status_counts[row["status"]] += 1
            confidence_counts[row["confidence"]] += 1
            if row["status"] == "PROPOSED":
                if not row["primary_path"] or row["confidence"] not in {"HIGH", "MEDIUM"}:
                    errors.append(f"effective proposed row {expected_global} violates status/path/confidence invariants")
            elif row["status"] == "UNRESOLVED":
                if row["primary_path"] or row["secondary_paths"] or row["confidence"] != "LOW":
                    errors.append(f"effective unresolved row {expected_global} violates unresolved invariants")
            else:
                errors.append(f"effective row {expected_global} has invalid status {row['status']!r}")
            paths = ([row["primary_path"]] if row["primary_path"] else []) + row["secondary_paths"]
            if len(paths) != len(set(paths)):
                errors.append(f"effective row {expected_global} repeats a taxonomy path")
            for path in paths:
                path_error = _taxonomy_path_error(path, taxonomy)
                if path_error:
                    invalid_paths[path_error] += 1
                    errors.append(f"effective row {expected_global}: {path_error}")
            matching_batch = next(
                (int(item["batch"]) for item in batches if int(item["range"][0]) <= expected_global <= int(item["range"][1])),
                None,
            )
            if matching_batch is None:
                errors.append(f"effective row {expected_global} is outside all MANIFEST ranges")
            else:
                by_batch.setdefault(matching_batch, []).append(row)
            rows.append(row)
    except Exception as exc:
        errors.append(f"effective sidecar cannot be parsed: {type(exc).__name__}: {exc}")

    if len(rows) != len(population):
        errors.append(f"effective row count {len(rows)} != population count {len(population)}")
    if len(seen) != len(population) or any(count != 1 for count in seen.values()):
        errors.append("effective sidecar does not contain exactly one row per canonical")

    expected_batches = {str(int(item["batch"])) for item in batches}
    declared_batches = set(batch_summaries.get("batches", {}))
    if declared_batches != expected_batches:
        errors.append("effective summary batch IDs differ from MANIFEST batch IDs")
    for item in batches:
        batch_no = int(item["batch"])
        start, end = map(int, item["range"])
        batch_rows = by_batch.get(batch_no, [])
        summary = batch_summaries.get("batches", {}).get(str(batch_no), {})
        statuses = Counter(row["status"] for row in batch_rows)
        confidences = Counter(row["confidence"] for row in batch_rows)
        genres = Counter(row["primary_path"][0] for row in batch_rows if row["primary_path"])
        unresolved = [row["canonical"] for row in batch_rows if row["status"] == "UNRESOLVED"]
        expected_summary = {
            "range": [start, end],
            "count": end - start + 1,
            "status_counts": {key: statuses.get(key, 0) for key in ("PROPOSED", "UNRESOLVED")},
            "confidence_counts": {key: confidences.get(key, 0) for key in ("HIGH", "MEDIUM", "LOW")},
            "primary_genre_counts": dict(sorted(genres.items())),
            "unresolved": unresolved,
        }
        if len(batch_rows) != end - start + 1:
            errors.append(f"effective batch {batch_no} row count {len(batch_rows)} != range size {end-start+1}")
        if summary != expected_summary:
            errors.append(f"effective batch {batch_no} summary does not match effective rows")

    totals = {
        "PROPOSED": status_counts.get("PROPOSED", 0),
        "UNRESOLVED": status_counts.get("UNRESOLVED", 0),
        "HIGH": confidence_counts.get("HIGH", 0),
        "MEDIUM": confidence_counts.get("MEDIUM", 0),
        "LOW": confidence_counts.get("LOW", 0),
    }
    if corrections.get("effective_sidecar", {}).get("counts") != totals:
        errors.append("effective totals differ from correction manifest")
    if totals["PROPOSED"] + totals["UNRESOLVED"] != len(population):
        errors.append("effective status totals do not cover the fixed population")
    if totals["UNRESOLVED"] != totals["LOW"]:
        errors.append("effective unresolved count and LOW confidence count differ")

    recovery_path = root / FULL_ROOT / "corrections/recovery_batch009_17.csv"
    if not recovery_path.is_file():
        errors.append("bounded recovery review CSV is missing")
        recovery_count = 0
    else:
        recovery_count = sum(1 for _ in recovery_path.open("r", encoding="utf-8-sig", newline="")) - 1
        declared_recovery = corrections.get("recovery_review", {})
        if recovery_count != int(declared_recovery.get("rows", -1)) or recovery_count != 1200:
            errors.append(f"bounded recovery review contains {recovery_count} rows, expected 1200")
        if sha256(recovery_path.read_bytes()) != declared_recovery.get("sha256"):
            errors.append("bounded recovery review SHA-256 mismatch")

    path_corrections_path = root / FULL_ROOT / "corrections/batch034_path_corrections.csv"
    if path_corrections_path.is_file():
        with path_corrections_path.open("r", encoding="utf-8-sig", newline="") as stream:
            path_correction_count = sum(1 for _ in csv.DictReader(stream))
        if path_correction_count != int(corrections.get("batch034_path_correction", {}).get("corrected_rows", -1)):
            errors.append("Batch 34 path correction count differs from correction manifest")
        if path_correction_count < 721:
            errors.append("Batch 34 correction layer covers fewer than the 721 known invalid-path rows")
    else:
        errors.append("Batch 34 path correction CSV is missing")
        path_correction_count = 0

    hash_provenance = corrections.get("source_hash_provenance", {})
    if hash_provenance.get("verification") == "FAIL":
        errors.append("working-source hash provenance failed local verification")
    elif hash_provenance.get("verification") != "PASS":
        warnings.append("working-source export was not locally available during effective validation")
    else:
        local_source_name = hash_provenance.get("local_materialized_source_path")
        if local_source_name:
            candidates = [root / local_source_name, root.parent.parent / local_source_name]
            local_source = next((candidate for candidate in candidates if candidate.is_file()), None)
            if local_source is None:
                warnings.append("recorded working-source hash was not rechecked because the local export is absent")
            else:
                with local_source.open("r", encoding="utf-8-sig", newline="") as stream:
                    source_rows = list(csv.DictReader(stream))
                source_canonicals = [row.get("canonical", "") for row in source_rows]
                if sha256(local_source.read_bytes()) != hash_provenance.get("local_materialized_source_sha256"):
                    errors.append("local working-source CSV SHA-256 differs from recorded provenance")
                if source_canonicals != population:
                    errors.append("local working-source canonical sequence differs from fixed population")

    original_issues = corrections.get("original_artifact_integrity", [])
    if (
        len(original_issues) != 2
        or {int(x.get("batch", -1)) for x in original_issues} != {9, 17}
        or any(x.get("status") != "RECOVERED_BY_SUPERSEDING_REVIEW" for x in original_issues)
    ):
        errors.append("original corrupt Batch 9/17 evidence is not fully documented as superseded")
    else:
        manifest_batches = {int(batch["batch"]): batch for batch in manifest.get("batches", [])}
        for issue in original_issues:
            batch = manifest_batches.get(int(issue["batch"]))
            artifact_path = issue.get("path")
            artifact = root / artifact_path if artifact_path else None
            if not batch or artifact is None or not artifact.is_file():
                errors.append(f"original Batch {issue['batch']} artifact is unavailable for re-verification")
                continue
            actual_hash = sha256(artifact.read_bytes())
            expected_hash = issue.get("expected_base64_text_sha256") or issue.get("expected_xz_sha256")
            recorded_hash = issue.get("actual_base64_text_sha256") or issue.get("actual_file_sha256")
            if actual_hash != recorded_hash:
                errors.append(f"original Batch {issue['batch']} artifact differs from correction manifest")
            if actual_hash == expected_hash:
                errors.append(f"original Batch {issue['batch']} artifact unexpectedly matches its required source hash")
            try:
                _, _, decode_issues = _ledger_bytes(root, batch)
                if not decode_issues:
                    errors.append(f"original Batch {issue['batch']} ledger unexpectedly decodes cleanly")
            except Exception as exc:
                # A decode failure is the condition this bounded recovery supersedes.
                if not str(exc):
                    errors.append(f"original Batch {issue['batch']} failed without a diagnostic")
    batch8 = corrections.get("batch008_repair", {})
    if len(batch8.get("reindexed_rows", [])) != 198:
        errors.append("Batch 8 correction does not reindex exactly 198 surviving decisions")
    if len(batch8.get("duplicate_decisions_dropped", [])) != 2:
        errors.append("Batch 8 correction does not document the two duplicate decisions")
    if batch8.get("missing_edge_rows_recovered") != [5699, 5700]:
        errors.append("Batch 8 missing edge rows are not explicitly accounted for")

    return {
        "validator": "issue64-effective-sidecar-validator-v1",
        "pass": not errors,
        "population_count": len(population),
        "population_sha256": population_hash,
        "effective_sidecar_sha256": actual_sidecar_hash,
        "effective_row_count": len(rows),
        "status_confidence_totals": totals,
        "invalid_path_counts": dict(invalid_paths),
        "batch_count": len(by_batch),
        "recovered_rows": recovery_count,
        "batch034_path_correction_rows": path_correction_count,
        "source_hash_verification": hash_provenance.get("verification"),
        "warnings": warnings,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository checkout root")
    parser.add_argument("--report", type=Path, help="write complete JSON report to this path")
    parser.add_argument("--effective", action="store_true", help="validate the effective sidecar and bounded correction layer")
    args = parser.parse_args()
    result = validate_effective(args.root) if args.effective else validate(args.root)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8", newline="\n")
    sys.stdout.write(rendered)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
