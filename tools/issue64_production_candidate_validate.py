#!/usr/bin/env python3
"""Validate the clean Issue #64 General taxonomy integration candidate."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_path(value: str) -> tuple[str, str | None] | None:
    if not value:
        return None
    parts = value.split("/")
    if len(parts) == 1:
        return parts[0], None
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ValueError(f"taxonomy path has depth greater than two: {value!r}")


def path_exists(path: tuple[str, str | None] | None, taxonomy: dict[str, Any]) -> bool:
    if path is None or path[0] not in taxonomy["genres"]:
        return False
    return path[1] is None or path[1] in taxonomy["genres"][path[0]]["subgenres"]


def validate(root: Path = ROOT) -> dict[str, Any]:
    candidate = root / "docs/issue64/production_candidate"
    manifest_path = candidate / "manifest.json"
    taxonomy_path = candidate / "general_taxonomy.json"
    sidecar_path = candidate / "effective_sidecar.csv"
    errors: list[str] = []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    taxonomy_bytes = taxonomy_path.read_bytes()
    sidecar_bytes = sidecar_path.read_bytes()
    taxonomy = json.loads(taxonomy_bytes.decode("utf-8"))
    if sha256(taxonomy_bytes) != manifest["taxonomy"]["sha256"]:
        errors.append("taxonomy SHA-256 mismatch")
    if sha256(sidecar_bytes) != manifest["effective_sidecar"]["sha256"]:
        errors.append("effective sidecar SHA-256 mismatch")

    rows: list[dict[str, str]] = []
    with sidecar_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    population = manifest["population"]
    if len(rows) != int(manifest["effective_sidecar"]["row_count"]):
        errors.append("effective sidecar row count differs from manifest")
    if len(rows) != int(population["count"]):
        errors.append("effective sidecar count differs from fixed target population")

    canonicals: list[str] = []
    statuses: Counter[str] = Counter()
    confidences: Counter[str] = Counter()
    for index, row in enumerate(rows, start=1):
        canonical = row.get("canonical", "")
        canonicals.append(canonical)
        if not canonical:
            errors.append(f"row {index}: canonical is empty")
        if row.get("global_row") != str(index):
            errors.append(f"row {index}: global_row is not in canonical order")
        status = row.get("classification_status", "")
        confidence = row.get("confidence", "")
        statuses[status] += 1
        confidences[confidence] += 1
        primary = parse_path(row.get("primary_path", ""))
        try:
            secondary = json.loads(row.get("secondary_paths", "[]"))
        except json.JSONDecodeError:
            errors.append(f"row {index}: invalid secondary_paths JSON")
            secondary = []
        if status == "PROPOSED":
            if confidence not in {"HIGH", "MEDIUM"} or not path_exists(primary, taxonomy):
                errors.append(f"row {index}: proposed row has invalid confidence/path")
        elif status == "UNRESOLVED":
            if confidence != "LOW" or primary is not None or secondary:
                errors.append(f"row {index}: unresolved row must be LOW and pathless")
        else:
            errors.append(f"row {index}: invalid classification status {status!r}")
        for serialized in secondary:
            if not isinstance(serialized, str) or not path_exists(parse_path(serialized), taxonomy):
                errors.append(f"row {index}: invalid secondary taxonomy path {serialized!r}")

    if len(set(canonicals)) != len(rows):
        errors.append("effective sidecar has duplicate canonicals")
    population_bytes = ("\n".join(canonicals) + "\n").encode("utf-8")
    population_hash = sha256(population_bytes)
    if population_hash != population["canonical_sequence_sha256_utf8_lf"]:
        errors.append("canonical sequence hash differs from the fixed target population")

    totals = {
        "proposed": statuses.get("PROPOSED", 0),
        "unresolved": statuses.get("UNRESOLVED", 0),
        "confidence": {
            "HIGH": confidences.get("HIGH", 0),
            "MEDIUM": confidences.get("MEDIUM", 0),
            "LOW": confidences.get("LOW", 0),
        },
    }
    expected = manifest["effective_sidecar"]
    if totals["proposed"] != int(expected["proposed"]):
        errors.append("proposed count differs from manifest")
    if totals["unresolved"] != int(expected["unresolved"]):
        errors.append("unresolved count differs from manifest")
    if totals["confidence"] != expected["confidence"]:
        errors.append("confidence counts differ from manifest")

    return {
        "validator": "issue64-production-candidate-validator-v1",
        "pass": not errors,
        "population_count": len(rows),
        "population_sha256": population_hash,
        "taxonomy_sha256": sha256(taxonomy_bytes),
        "effective_sidecar_sha256": sha256(sidecar_bytes),
        "totals": totals,
        "errors": errors,
    }


def main() -> int:
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
