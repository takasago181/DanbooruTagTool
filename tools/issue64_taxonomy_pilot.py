"""Offline Issue #64 pilot evidence builder; never writes production data."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

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


def select_pilot(entries, usage, challenge_tags, revision_challenges=None):
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
    if revision_challenges is not None:
        added = [tag for tags in revision_challenges.values() for tag in tags]
        if not 64 <= len(added) <= 96:
            raise ValueError("Revision must add 64–96 targeted challenge rows")
        if len(added) != len(set(added)) or set(added) & set(selected) or set(added) - set(entries):
            raise ValueError("Revision challenge must be unique, new and in population")
        for group, tags in sorted(revision_challenges.items()):
            add(tags, "revision2/" + group)
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


def revision_audit(sidecar, selected, baseline, external):
    rows = sidecar["entries"]
    old = baseline["entries"]
    evidence = external["entries"]
    added = set(rows) - set(old)
    required_evidence = added | {t for t,r in old.items() if r["classification_status"] == "UNRESOLVED"}
    if not set(old) <= set(rows) or not 64 <= len(added) <= 96:
        raise ValueError("Revision must preserve original pilot and add only a small supplement")
    selected_added = {t for t,reasons in selected.items() if any(r.startswith("revision2/") for r in reasons)}
    if selected_added != added:
        raise ValueError("Revision selection/baseline mismatch")
    if not required_evidence <= set(evidence) or not set(evidence) <= set(rows):
        raise ValueError("Missing or out-of-pilot external evidence")
    for tag, record in evidence.items():
        if not record["observed_summary_ja"].strip() or not record["classification_inference_ja"].strip():
            raise ValueError("External observation and inference must both be explicit")
        if record["independent_semantic_acceptance"] is not False:
            raise ValueError("External lookup is not independent acceptance")
        if f"external_evidence.json#entries/{tag}" not in rows[tag]["source"]:
            raise ValueError("Sidecar lacks external evidence reference")
        if not record["sources"]:
            raise ValueError("External evidence has no sources")
        for source in record["sources"]:
            kind = source["kind"]
            if kind not in {"danbooru_wiki_definition", "danbooru_wiki_lookup_no_match", "danbooru_post_context"}:
                raise ValueError("Unknown external evidence kind")
            url = source.get("url", source.get("request_url"))
            if not url or urlparse(url).hostname != "danbooru.donmai.us" or not source["retrieved_at_utc"]:
                raise ValueError("External source provenance missing or invalid")
            if kind == "danbooru_wiki_definition":
                digest = source["body_sha256_utf8"]
                if not source["wiki_id"] or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                    raise ValueError("Wiki snapshot identity/hash missing")
            if kind == "danbooru_post_context":
                posts = source["posts"]
                if not posts or len(posts) > 12 or len({p["id"] for p in posts}) != len(posts) or any(not p["target_tag_present"] for p in posts):
                    raise ValueError("Invalid limited post context sample")
    fields = ("classification_status", "primary_path", "secondary_paths")
    current = {t: {f:r[f] for f in fields} for t,r in rows.items()}
    changed = {t: {"before":old[t], "after":current[t]} for t in sorted(old) if old[t] != current[t]}
    resolved = [t for t in sorted(old) if old[t]["classification_status"] == "UNRESOLVED" and rows[t]["classification_status"] == "PROPOSED"]
    return {
        "baseline_commit": baseline["commit"], "baseline_count": len(old), "revised_count": len(rows),
        "added_count": len(added), "added_tags": sorted(added), "removed_count": 0,
        "changed_existing_verdict_or_paths": changed, "changed_existing_count": len(changed),
        "resolved_existing_tags": resolved,
        "remaining_existing_unresolved": [t for t in sorted(old) if rows[t]["classification_status"] == "UNRESOLVED"],
        "new_unresolved": [t for t in sorted(added) if rows[t]["classification_status"] == "UNRESOLVED"],
        "external_rechecked_rows": len(evidence),
        "source_kind_reference_counts": dict(Counter(s["kind"] for r in evidence.values() for s in r["sources"])),
        "unchanged_existing_rows_without_new_external_check": sorted(set(old)-set(evidence)),
        "external_evidence_semantic_sha256": hashlib.sha256(encoded(external)).hexdigest(),
        "baseline_semantic_sha256": hashlib.sha256(encoded(baseline)).hexdigest(),
        "independent_accepted_rows": 0,
    }


def build(source_path):
    overlay = ROOT / "data/runtime/japanese_overlay.json"
    usage_path = ROOT / "data/source/danbooru-2026-09-02.csv"
    promotion = ROOT / "docs/testing/ISSUE55_PRODUCTION_PROMOTION_MANIFEST.json"
    entries, usage = load_population(overlay, usage_path, source_path, promotion)
    names = ("\n".join(sorted(entries)) + "\n").encode("utf-8")
    selection = read_json(WORK / "selection.json")
    selected = select_pilot(entries, usage, selection["challenge_tags"], selection.get("revision_challenges"))
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
    external = read_json(WORK / "external_evidence.json")
    baseline = read_json(WORK / "pilot_v1_baseline.json")
    outputs["revision_audit.json"] = encoded(revision_audit(sidecar, selected, baseline, external))
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
    lines = ["# Issue #64 external definition review — revision 2", "", "Observed source summaries and classification inferences are separate. All rows remain proposals, not independently accepted. Post metadata is a limited context sample; no images were inspected.", "", "| canonical | 観察した根拠（要約） | 分類判断 | 参照元 |", "| --- | --- | --- | --- |"]
    for tag, record in external["entries"].items():
        links = []
        for source in record["sources"]:
            kind = source["kind"]
            url = source.get("url", source.get("request_url"))
            title = source.get("requested_title", "post metadata (12)")
            if kind == "danbooru_wiki_lookup_no_match":
                title += " (wiki未検出)"
            links.append(f"[{escape(title)}]({url})")
        lines.append("| " + " | ".join([escape(tag), escape(record["observed_summary_ja"]), escape(record["classification_inference_ja"]), " / ".join(links)]) + " |")
    outputs["external_review.md"] = ("\n".join(lines) + "\n").encode("utf-8")
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
