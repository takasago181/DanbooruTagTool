"""Issue #36 Phase 0 read-only coverage inventory.

The production root is an explicit input and is never written.  This script
only writes the two durable Phase 0 artifacts beside itself.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from typing import Iterable


PROBE_CORE = ("anal", "butt_plug")
COMMON_LIMIT = 8
RARE_LIMIT = 5
HIGH_USAGE_LIMIT = 1000
RUNTIME_INDEX_SNAPSHOT = (
    "nyanko-devs/danbooru2026@ebb02a630201c7b51487e45fb90b3fcf4cbedc20:"
    "metadata/posts-snapshot.parquet"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _rate(covered: int, total: int) -> float:
    return (covered / total) if total else 0.0


def _coverage(canonicals: Iterable[str], entries: dict[str, dict]) -> dict:
    names = tuple(sorted(set(canonicals)))
    display = sum(bool((entries.get(name, {}).get("display_ja") or "").strip()) for name in names)
    search = sum(bool(entries.get(name, {}).get("search_ja")) for name in names)
    return {
        "entries": len(names),
        "display_ja": {"covered": display, "missing": len(names) - display,
                       "rate": _rate(display, len(names))},
        "search_ja": {"covered": search, "missing": len(names) - search,
                      "rate": _rate(search, len(names))},
    }


def _state(canonical: str, entries: dict[str, dict]) -> dict:
    value = entries.get(canonical, {})
    display = (value.get("display_ja") or "").strip()
    search = tuple(value.get("search_ja") or ())
    return {
        "display": "covered" if display else "missing",
        "display_ja": display or None,
        "search": "covered" if search else "missing",
        "search_terms": list(search),
    }


def _git_show(repo: Path, ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={repo}", "show", f"{ref}:{path}"],
        cwd=repo, check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return result.stdout


def _read_csv_text(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def _metric(canonicals: Iterable[str], entries: dict[str, dict]) -> dict:
    result = _coverage(canonicals, entries)
    # Japaneseあり/なし in the requested lane totals is display coverage.
    result["japanese"] = {
        "covered": result["display_ja"]["covered"],
        "missing": result["display_ja"]["missing"],
        "rate": result["display_ja"]["rate"],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--production-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    parser.add_argument("--issue32-ref", default="origin/dict-validation/quarantine")
    args = parser.parse_args()

    production = args.production_root.resolve()
    output_dir = args.output_dir.resolve()
    script_root = Path(__file__).resolve().parents[1]
    if output_dir != Path(__file__).resolve().parent:
        raise SystemExit("Refusing output outside translation_quarantine")
    sys.path.insert(0, str(script_root))

    from danbooru_tag_tool.canonical_overlay import CanonicalOverlay
    from danbooru_tag_tool.knowledge import TagKnowledgeCore
    from danbooru_tag_tool.recommendations import RecommendationEngine
    from danbooru_tag_tool.runtime_index import RuntimeIndex
    from danbooru_tag_tool.search import TagSearchEngine

    overlay_path = production / "data/runtime/japanese_overlay.json"
    runtime_dir = production / "data/runtime_index"
    knowledge = TagKnowledgeCore.load(production, japanese_overlay_path=overlay_path)
    runtime_index = RuntimeIndex(runtime_dir, expected_snapshot_id=RUNTIME_INDEX_SNAPSHOT)
    canonical_overlay = CanonicalOverlay(runtime_index, runtime_dir / "canonical_overlay.json",
                                         expected_snapshot_id=RUNTIME_INDEX_SNAPSHOT)
    canonical_overlay.validate()

    overlay_document = json.loads(overlay_path.read_text(encoding="utf-8"))
    entries = overlay_document["entries"]
    display_by_canonical = {
        key: value["display_ja"] for key, value in entries.items()
        if (value.get("display_ja") or "").strip()
    }
    search_by_canonical = {
        key: tuple(value.get("search_ja") or ()) for key, value in entries.items()
        if value.get("search_ja")
    }

    runtime_general = {
        canonical for canonical, source_ids in canonical_overlay.canonical_to_source_tag_ids.items()
        if canonical in knowledge.canonical
        and knowledge.canonical[canonical].category == 0
        and source_ids
    }
    runtime_general = frozenset(runtime_general)

    # This is the documented Stage 8B parity probe, not an exhaustive
    # recommendation universe.  It is reproducible and uses production stats.
    recommendation_engine = RecommendationEngine(canonical_overlay, knowledge)
    raw_probe = recommendation_engine.candidates(PROBE_CORE)
    common = RecommendationEngine.rank(raw_probe, "conditional_rate")[:COMMON_LIMIT]
    rare = RecommendationEngine.rank(raw_probe, "raw_lift")[:RARE_LIMIT]
    recommendation_pool = frozenset(item.canonical for item in raw_probe)
    common_surface = frozenset(item.canonical for item in common)
    rare_surface = frozenset(item.canonical for item in rare)
    auxiliary_surface = common_surface | rare_surface

    profile_store = knowledge.load_generation_profile_store(production)
    from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore
    support_store = SupportKnowledgeStore.load(production, knowledge, profile_store)
    semantic_support = frozenset(
        candidate.canonical
        for special_id in sorted(knowledge.special)
        for candidate in support_store.candidates((special_id,))
    )

    runtime_counts = {}
    for canonical in runtime_general | recommendation_pool | semantic_support:
        if canonical in canonical_overlay.canonical_to_source_tag_ids:
            runtime_counts[canonical] = canonical_overlay.global_count(canonical)
        elif canonical in knowledge.canonical:
            runtime_counts[canonical] = knowledge.canonical[canonical].current_post_count

    high_usage = frozenset(sorted(
        runtime_general,
        key=lambda name: (-runtime_counts.get(name, -1), name),
    )[:HIGH_USAGE_LIMIT])

    lanes = {
        "general_or_proxy": runtime_general,
        "statistical_recommendation": recommendation_pool,
        "semantic_support": semantic_support,
        "manual_auxiliary_or_proxy": auxiliary_surface,
    }
    lane_union = frozenset().union(*lanes.values())
    missing_union = frozenset(
        name for name in lane_union
        if not ((entries.get(name, {}).get("display_ja") or "").strip())
        or not entries.get(name, {}).get("search_ja")
    )

    queue_rows = []
    for canonical in sorted(missing_union):
        memberships = []
        if canonical in runtime_general:
            memberships.append("general_or_proxy")
        if canonical in recommendation_pool:
            memberships.append("statistical_recommendation")
        if canonical in semantic_support:
            memberships.append("semantic_support")
        if canonical in auxiliary_surface:
            memberships.append("manual_auxiliary_or_proxy")

        evidence = []
        if canonical in high_usage:
            evidence.append("general_runtime_top1000_by_runtime_global_count")
        if canonical in common_surface:
            evidence.append("recommendation_probe_common_surface:anal+butt_plug")
        if canonical in rare_surface:
            evidence.append("recommendation_probe_rare_surface:anal+butt_plug")
        if canonical in recommendation_pool and canonical not in auxiliary_surface:
            evidence.append("recommendation_probe_reachable_pool:anal+butt_plug")
        if canonical in semantic_support:
            evidence.append("production_semantic_support_reachable_union")

        priority = "P0" if (canonical in high_usage
                             or canonical in common_surface
                             or canonical in rare_surface
                             or canonical in semantic_support) else (
            "P1" if canonical in recommendation_pool else "P2"
        )
        queue_rows.append({
            "canonical": canonical,
            "lanes": ";".join(memberships),
            "current_display_state": "covered" if (entries.get(canonical, {}).get("display_ja") or "").strip() else "missing",
            "current_search_state": "covered" if entries.get(canonical, {}).get("search_ja") else "missing",
            "post_count_or_reference": str(runtime_counts.get(canonical, "")),
            "priority": priority,
            "proposed_display_ja": "",
            "proposed_search_ja": "",
            "source_evidence": ";".join(evidence),
            "review_state": "NOT_TRANSLATED_PHASE0",
        })

    specific_terms = ("1girl", "penis", "sex", "blush", "nipples")
    ranking_terms = ("piano", "analog_clock", "analogous_colors", "canal")
    ranking_results = TagSearchEngine(knowledge).search_one("anal", limit=50)
    ranking_positions = {
        result.canonical: {
            "rank_in_limit_50": index,
            "match_type": result.match_type,
            "group": result.group,
        }
        for index, result in enumerate(ranking_results, start=1)
        if result.canonical in ranking_terms
    }

    issue32_support_rows = _read_csv_text(
        _git_show(production, args.issue32_ref, "validation_quarantine/semantic_support_results.csv")
    )
    issue32_canonicals = frozenset(
        row["candidate_canonical"].strip()
        for row in issue32_support_rows if row.get("candidate_canonical", "").strip()
    )
    issue32_overlap = sorted(issue32_canonicals & missing_union)

    hashes = {
        "data/runtime/japanese_overlay.json": _sha256(overlay_path),
        "data/runtime_index/canonical_overlay.json": _sha256(runtime_dir / "canonical_overlay.json"),
        "data/runtime_index/BUILD_MANIFEST.json": _sha256(runtime_dir / "BUILD_MANIFEST.json"),
        "data/semantic/semantic_support_profiles.csv": _sha256(production / "data/semantic/semantic_support_profiles.csv"),
        "data/semantic/family_support_rules.csv": _sha256(production / "data/semantic/family_support_rules.csv"),
    }

    summary = {
        "issue": 36,
        "rule_version": "R1",
        "status": "PHASE0_COMPLETE",
        "production_modified": False,
        "protected_data_read_path": str(production),
        "measurement": {
            "runtime_index_snapshot_id": RUNTIME_INDEX_SNAPSHOT,
            "runtime_total_posts": runtime_index.total_posts,
            "canonical_total": len(knowledge.canonical),
            "special_total": len(knowledge.special),
            "semantic_total": len(knowledge.semantic),
            "general_proxy_definition": "category=0 canonicals with nonempty canonical_overlay source_tag_ids in protected Stage 5 runtime index",
            "general_proxy": _metric(runtime_general, entries),
            "recommendation_proxy_definition": "full RecommendationEngine candidate pool for the documented production parity probe anal AND butt_plug; not exhaustive",
            "recommendation_probe": {
                "core": list(PROBE_CORE),
                "base_count": raw_probe[0].base_count if raw_probe else 0,
                "full_pool": _metric(recommendation_pool, entries),
                "common_surface_limit": COMMON_LIMIT,
                "common_surface": _metric(common_surface, entries),
                "common_surface_canonicals": [item.canonical for item in common],
                "rare_surface_limit": RARE_LIMIT,
                "rare_surface": _metric(rare_surface, entries),
                "rare_surface_canonicals": [item.canonical for item in rare],
            },
            "semantic_support": {
                "definition": "unique canonicals returned by the production SupportKnowledgeStore for every Special ID; enabled explicit/family rows only at runtime",
                "special_rows_total": len(support_store.special_rows),
                "special_rows_enabled": sum(row.enabled for row in support_store.special_rows),
                "family_rows_total": len(support_store.family_rows),
                "family_rows_enabled": sum(row.enabled for row in support_store.family_rows),
                "unique_candidate_canonicals": _metric(semantic_support, entries),
            },
            "manual_auxiliary_or_proxy": {
                "definition": "union of rows actually surfaced by the documented probe's common/rare UI limits; each is manually addable in the current UI",
                "surface": _metric(auxiliary_surface, entries),
                "canonicals": sorted(auxiliary_surface),
            },
        },
        "overlay": {
            "display_by_canonical": {
                "canonical_entries": len(display_by_canonical),
                "japanese_present": len(display_by_canonical),
                "japanese_missing_in_overlay_entries": len(entries) - len(display_by_canonical),
            },
            "search_by_canonical": {
                "canonical_entries": len(search_by_canonical),
                "search_terms": sum(len(values) for values in search_by_canonical.values()),
            },
        },
        "lanes": {name: _metric(values, entries) for name, values in lanes.items()},
        "union": {
            "canonical_entries": len(lane_union),
            "missing_total_deduplicated": len(missing_union),
            "missing_display": sum(not (entries.get(name, {}).get("display_ja") or "").strip() for name in lane_union),
            "missing_search": sum(not entries.get(name, {}).get("search_ja") for name in lane_union),
        },
        "priority_queue": {
            "rows": len(queue_rows),
            "counts": {priority: sum(row["priority"] == priority for row in queue_rows)
                       for priority in ("P0", "P1", "P2")},
            "high_usage_general_definition": f"top {HIGH_USAGE_LIMIT} by protected runtime_global_count descending, canonical ascending tie-break",
            "high_usage_general_count": len(high_usage),
            "p0_surface_seed_canonicals": {
                "common": [item.canonical for item in common],
                "rare": [item.canonical for item in rare],
                "semantic_support_count": len(semantic_support),
            },
        },
        "specific_coverage": {term: _state(term, entries) for term in specific_terms},
        "ranking_issue_separated": {
            "query": "anal",
            "classification": "SEARCH_RANKING_ISSUE_NOT_TRANSLATION_COVERAGE",
            "returned_count": len(ranking_results),
            "terms": {term: {**_state(term, entries), **ranking_positions.get(term, {"rank_in_limit_50": None})}
                      for term in ranking_terms},
            "note": "These results are recorded as the requested ranking/noise separation. No search or recommendation logic was changed, and their appearance for anal did not assign translation priority.",
        },
        "issue32_overlap": {
            "source_ref": args.issue32_ref,
            "source_path": "validation_quarantine/semantic_support_results.csv",
            "source_rows": len(issue32_support_rows),
            "unique_candidate_canonicals": len(issue32_canonicals),
            "overlap_with_phase0_missing_union": len(issue32_overlap),
            "overlap_canonicals": issue32_overlap,
            "meaning_unchanged": True,
            "note": "Overlap is a Japanese coverage intersection only; #32 verdicts, meaning, and validation state are not modified or reinterpreted.",
        },
        "protected_input_sha256": hashes,
        "notes": [
            "No translation text was generated; proposal columns remain blank.",
            "General coverage is a deterministic runtime/canonical proxy, not an exhaustive search reachability claim for all raw runtime tags.",
            "Recommendation coverage beyond the documented probe is unmeasured in Phase 0; the full probe pool is a reachable-candidate proxy.",
            "Japaneseあり/なし lane totals are display coverage; search coverage is reported separately in every lane.",
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "coverage_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    fields = [
        "canonical", "lanes", "current_display_state", "current_search_state",
        "post_count_or_reference", "priority", "proposed_display_ja",
        "proposed_search_ja", "source_evidence", "review_state",
    ]
    with (output_dir / "missing_candidates.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(queue_rows)
    print(json.dumps({
        "status": summary["status"],
        "missing_total_deduplicated": summary["union"]["missing_total_deduplicated"],
        "queue_counts": summary["priority_queue"]["counts"],
        "output_files": [str(output_dir / "coverage_summary.json"), str(output_dir / "missing_candidates.csv")],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
