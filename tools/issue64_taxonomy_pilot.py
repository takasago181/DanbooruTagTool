"""Offline Issue #64 pilot evidence builder; never writes production data."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "docs/issue64"
SEED = "issue64-pilot-v1:"
EXPECTED_COUNT = 30629
MAX_PILOT = 256
USAGE_SHA256 = "9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b"


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def band(count):
    return "high_usage" if count >= 100000 else "ordinary" if count >= 1000 else "rare"


def load_population(overlay_path, usage_path, source_path, promotion_path):
    promotion = read_json(promotion_path)
    if sha256(overlay_path) != promotion["overlay"]["post_sha256"]:
        raise ValueError("Production overlay hash differs from Issue #55")
    if sha256(source_path) != promotion["source"]["sha256"]:
        raise ValueError("Audited V5 source hash differs from Issue #55")
    if sha256(usage_path) != USAGE_SHA256:
        raise ValueError("Usage snapshot hash changed; pilot sampling must not silently drift")
    document = read_json(overlay_path)
    if set(document) != {"format_version", "entries"} or document["format_version"] != 1:
        raise ValueError("Unexpected overlay schema")
    entries = document["entries"]
    if len(entries) != EXPECTED_COUNT:
        raise ValueError("Wrong target population size")
    with Path(source_path).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != EXPECTED_COUNT or [r["canonical"] for r in rows] != list(entries):
        raise ValueError("V5/overlay canonical identity or order mismatch")
    for row in rows:
        if entries[row["canonical"]] != {"display_ja": row["display_ja"], "search_ja": [row["search_ja"]]}:
            raise ValueError("V5/overlay display or search mismatch")
    usage = {}
    with Path(usage_path).open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.reader(stream):
            # The full CSV is a lookup source only: no non-target identities are materialized.
            if row[0] not in entries:
                continue
            if row[0] in usage:
                raise ValueError("Duplicate target identity in usage source")
            usage[row[0]] = {"category": int(row[1]), "post_count": int(row[2])}
    if set(usage) != set(entries) or any(r["category"] != 0 or r["post_count"] < 0 for r in usage.values()):
        raise ValueError("Missing/non-General/invalid usage target")
    return entries, usage


def select_pilot(entries, usage, challenge_tags):
    if len(challenge_tags) != len(set(challenge_tags)) or set(challenge_tags) - set(entries):
        raise ValueError("Duplicate or non-population challenge tag")
    selected = {}
    def add(tags, reason):
        for tag in tags:
            selected.setdefault(tag, []).append(reason)
    def hashed(tags):
        return sorted(tags, key=lambda tag: (hashlib.sha256((SEED + tag).encode()).hexdigest(), tag))
    add(sorted(entries, key=lambda tag: (-usage[tag]["post_count"], tag))[:16], "high_top16")
    add(hashed(t for t in entries if band(usage[t]["post_count"]) == "high_usage" and t not in selected)[:16], "high_hash16")
    for name in ("ordinary", "rare"):
        add(hashed(t for t in entries if band(usage[t]["post_count"]) == name)[:32], name + "_hash32")
    add(hashed(t for t in entries if t.count("_") >= 2 and t not in selected)[:32], "compound_hash32_disjoint")
    add(challenge_tags, "boundary_challenge")
    if len(selected) > MAX_PILOT:
        raise ValueError("Pilot size cap exceeded; full rollout requires separate accepted work")
    return dict(sorted(selected.items()))


def profile(entries, usage):
    counts = sorted(r["post_count"] for r in usage.values())
    return {
        "population_count": len(entries),
        "category_counts": dict(Counter(str(r["category"]) for r in usage.values())),
        "usage_bands": dict(Counter(band(r["post_count"]) for r in usage.values())),
        "usage_quantiles_floor_index_q_times_n_minus_1": {str(q): counts[int((len(counts)-1)*q)] for q in (0, .25, .5, .75, .9, .99, 1)},
        "underscore_piece_counts_capped_at_5": dict(Counter(str(min(5, t.count("_")+1)) for t in entries)),
        "compound_3plus_pieces": sum(t.count("_") >= 2 for t in entries),
        "parenthesis_qualified": sum("(" in t for t in entries),
        "display_without_kana_or_cjk_heuristic": sum(not any("\u3040" <= c <= "\u30ff" or "\u3400" <= c <= "\u9fff" for c in r["display_ja"]) for r in entries.values()),
        "note": "Usage snapshot 2026-09-02; lexical flags are sampling cues, not semantic classifications or translation verdicts.",
    }


def validate_sidecar(sidecar, selected, taxonomy):
    if set(sidecar) != {"format_version", "stage", "taxonomy_version", "entries"} or sidecar["format_version"] != 1:
        raise ValueError("Invalid sidecar schema")
    if taxonomy["status"] != "PROPOSED_PENDING_DEV_AUDIT" or taxonomy["max_path_depth"] != 2 or taxonomy["no_visible_catch_all"] is not True:
        raise ValueError("Invalid pilot taxonomy contract")
    if sidecar["stage"] != "PILOT_PROPOSAL_PENDING_DEV_AUDIT" or sidecar["taxonomy_version"] != taxonomy["version"]:
        raise ValueError("Pilot stage/version mismatch")
    rows = sidecar["entries"]
    if set(rows) != set(selected):
        raise ValueError("Pilot membership mismatch; full rollout is not allowed")
    genres = taxonomy["genres"]
    if not genres or any(not g["label_ja"].strip() or not g["boundary_ja"].strip() for g in genres.values()):
        raise ValueError("Missing genre label/boundary")
    for tag, row in rows.items():
        expected = {"primary_path", "secondary_paths", "classification_status", "classification_reason", "source", "reviewed", "reviewer", "reviewed_at"}
        if set(row) != expected or row["reviewed"] is not False or row["reviewer"] is not None or row["reviewed_at"] is not None:
            raise ValueError(f"Unexpected schema or unapproved review promotion: {tag}")
        if not isinstance(row["secondary_paths"], list) or len(row["secondary_paths"]) > 2:
            raise ValueError("Invalid/excess secondary paths")
        if not row["classification_reason"].strip() or not row["source"].strip():
            raise ValueError("Missing classification evidence")
        paths = ([row["primary_path"]] if row["primary_path"] else []) + row["secondary_paths"]
        if row["classification_status"] == "UNRESOLVED":
            if paths:
                raise ValueError("Unresolved row must not silently become browsable")
        elif row["classification_status"] == "PROPOSED":
            if not row["primary_path"]:
                raise ValueError("Proposed row missing primary path")
        else:
            raise ValueError("Unknown classification status")
        seen = set()
        for path in paths:
            if set(path) != {"genre_id", "subgenre_id"}:
                raise ValueError("Invalid path shape/depth")
            genre, subgenre = path["genre_id"], path["subgenre_id"]
            if genre not in genres or (subgenre is not None and subgenre not in genres[genre]["subgenres"]):
                raise ValueError("Unknown taxonomy path")
            if (genre, subgenre) in seen:
                raise ValueError("Duplicate browse path")
            seen.add((genre, subgenre))


def audit(sidecar, selected, usage, taxonomy):
    rows = sidecar["entries"]
    primary = Counter(r["primary_path"]["genre_id"] for r in rows.values() if r["primary_path"])
    reachable = sum(primary.values())
    return {
        "pilot_count": len(rows), "proposed_reachable": reachable,
        "unresolved": [t for t,r in rows.items() if r["classification_status"] == "UNRESOLVED"],
        "not_sampled_population_count": EXPECTED_COUNT-len(rows),
        "production_classified_count": 0,
        "primary_counts": dict(primary),
        "primary_path_counts": dict(Counter(r["primary_path"]["genre_id"] + ("/" + r["primary_path"]["subgenre_id"] if r["primary_path"]["subgenre_id"] else "") for r in rows.values() if r["primary_path"])),
        "all_path_counts": dict(Counter(p["genre_id"] for r in rows.values() for p in ([r["primary_path"]] if r["primary_path"] else []) + r["secondary_paths"])),
        "multipath_count": sum(bool(r["secondary_paths"]) for r in rows.values()),
        "selection_reason_counts": dict(Counter(reason for reasons in selected.values() for reason in reasons)),
        "pilot_usage_bands": dict(Counter(band(usage[t]["post_count"]) for t in rows)),
        "unresolved_by_usage_band": dict(Counter(band(usage[t]["post_count"]) for t,r in rows.items() if r["classification_status"] == "UNRESOLVED")),
        "largest_primary_share_of_reachable": max(primary.values(), default=0) / max(1,reachable),
        "visible_catch_all_count": sum(n for g,n in primary.items() if g in {"OTHER", "UNKNOWN", "UNRESOLVED"} or "その他" in taxonomy["genres"][g]["label_ja"]),
        "catch_all_pressure_unresolved_share": (len(rows)-reachable)/len(rows),
        "input_digests": {"sidecar_semantic_sha256": hashlib.sha256(encoded(sidecar)).hexdigest(), "taxonomy_semantic_sha256": hashlib.sha256(encoded(taxonomy)).hexdigest()},
        "reviewed_count": sum(r["reviewed"] for r in rows.values()),
        "warning": "Purposive/stratified pilot, not a prevalence estimate. PROPOSED is not accepted classification. No runtime integration.",
    }


def build(source_path):
    overlay = ROOT / "data/runtime/japanese_overlay.json"
    usage_path = ROOT / "data/source/danbooru-2026-09-02.csv"
    promotion = ROOT / "docs/testing/ISSUE55_PRODUCTION_PROMOTION_MANIFEST.json"
    entries, usage = load_population(overlay, usage_path, source_path, promotion)
    names = ("\n".join(sorted(entries)) + "\n").encode("utf-8")
    selection = read_json(WORK / "selection.json")
    selected = select_pilot(entries, usage, selection["challenge_tags"])
    evidence = {
        "format_version": 1, "base_main": "293181686260a91398334a0fe2d794a5998388cc",
        "source_evidence": {"overlay_sha256": sha256(overlay), "overlay_bytes": overlay.stat().st_size,
                            "v5_sha256": sha256(source_path), "usage_sha256": sha256(usage_path),
                            "promotion_manifest_semantic_sha256": hashlib.sha256(encoded(read_json(promotion))).hexdigest()},
        "population_sha256_sorted_utf8_lf": hashlib.sha256(names).hexdigest(),
        "identity_order_and_display_search_equal_v5": True,
        "target_only_usage_join_missing": 0, "duplicate_canonicals": 0,
        "distribution": profile(entries, usage),
    }
    samples = {t: {"display_ja": entries[t]["display_ja"], "post_count": usage[t]["post_count"],
                   "usage_band": band(usage[t]["post_count"]), "selection_reasons": reasons} for t,reasons in selected.items()}
    outputs = {"population.txt": names, "population_evidence.json": encoded(evidence), "pilot_samples.json": encoded(samples)}
    sidecar_path = WORK / "pilot_sidecar.json"
    sidecar = read_json(sidecar_path)
    taxonomy = read_json(WORK / "taxonomy.json")
    validate_sidecar(sidecar, selected, taxonomy)
    outputs["pilot_audit.json"] = encoded(audit(sidecar, selected, usage, taxonomy))
    lines = ["# Issue #64 pilot discovery catalog", "", "Offline review view only. All paths are proposals; no production/UI integration or accepted review.", "", "| canonical English | production 日本語表示 | usage | 主経路案 | 副経路案 | 状態 |", "| --- | --- | ---: | --- | --- | --- |"]
    def label(path):
        if path is None:
            return "—"
        genre = taxonomy["genres"][path["genre_id"]]
        return genre["label_ja"] + (" → " + genre["subgenres"][path["subgenre_id"]] if path["subgenre_id"] else "")
    def escape(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    for tag, row in sidecar["entries"].items():
        columns = [tag, entries[tag]["display_ja"], usage[tag]["post_count"], label(row["primary_path"]), " / ".join(label(p) for p in row["secondary_paths"]), row["classification_status"]]
        lines.append("| " + " | ".join(escape(c) for c in columns) + " |")
    outputs["pilot_catalog.md"] = ("\n".join(lines) + "\n").encode("utf-8")
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v5-source", type=Path, help="Exact audited #55 source (read only); defaults to promotion manifest location")
    parser.add_argument("--check", action="store_true", help="Compare committed artifacts without writing")
    args = parser.parse_args()
    source = args.v5_source or Path(read_json(ROOT / "docs/testing/ISSUE55_PRODUCTION_PROMOTION_MANIFEST.json")["source"]["path"])
    outputs = build(source)
    target = WORK / "artifacts"
    if not args.check:
        target.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        path = target / name
        if args.check:
            if not path.exists() or path.read_bytes() != content:
                raise ValueError(f"Reproduction mismatch: {name}")
        else:
            path.write_bytes(content)
    print(f"{'Verified' if args.check else 'Built'} {len(outputs)} artifacts; production inputs read only")


if __name__ == "__main__":
    main()
