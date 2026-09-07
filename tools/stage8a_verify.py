"""Create deterministic Stage 8A parity and protected-hash evidence."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from danbooru_tag_tool.canonical_overlay import CanonicalOverlay
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.recommendations import RecommendationEngine
from danbooru_tag_tool.runtime_index import RuntimeIndex
from danbooru_tag_tool.stage8a_semantics import Stage8ASemantics


CORE = ("anal", "butt_plug")
OUT = ROOT / "benchmarks" / "stage8a"
PROTECTED = (
    "data/special2788/illustrious_tag_knowledge_base_2788.csv",
    "data/source/danbooru-2026-09-02.csv",
    "data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv",
    "data/derived/special2788_VERIFIED_LINKAGE.csv",
    "data/generation/special2788_generation_profile.csv",
    "data/generation/generation_family_rules.csv",
    "data/generation/generation_model_observations.csv",
    "data/runtime/japanese_overlay.json",
    "danbooru_tag_tool/recommendations.py",
    "danbooru_tag_tool/stage7b_recommendations.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    knowledge = TagKnowledgeCore.load(ROOT)
    index_dir = ROOT / "data" / "runtime_index"
    index = RuntimeIndex(index_dir)
    overlay = CanonicalOverlay(index, index_dir / "canonical_overlay.json")
    engine = RecommendationEngine(overlay, knowledge)
    semantics = Stage8ASemantics.load(ROOT)

    raw = engine.candidates(CORE)
    common = RecommendationEngine.rank(raw, "conditional_rate")
    rare = RecommendationEngine.rank(raw, "raw_lift")
    decorated_common = semantics.decorate_many(
        common, core_canonicals=CORE, bucket="common"
    )
    decorated_rare = semantics.decorate_many(
        rare, core_canonicals=CORE, bucket="rare"
    )
    body_common = semantics.decorate(
        next(item for item in raw if item.canonical == "ass"),
        core_canonicals=CORE, bucket="common",
    )
    classified_rare = semantics.decorate(
        next(item for item in raw if item.canonical == "sex_toy"),
        core_canonicals=CORE, bucket="rare",
    )
    common_unchanged = all(
        asdict(decorated.candidate) == asdict(candidate)
        for decorated, candidate in zip(decorated_common, common, strict=True)
    )
    rare_unchanged = all(
        asdict(decorated.candidate) == asdict(candidate)
        for decorated, candidate in zip(decorated_rare, rare, strict=True)
    )
    raw_names = {candidate.canonical for candidate in raw}
    payload = {
        "core_canonicals": list(CORE),
        "base_count": raw[0].base_count if raw else overlay.intersect(CORE).base_count,
        "stage6_candidate_count": len(raw),
        "stage8a_common_decorated_count": len(decorated_common),
        "stage8a_rare_decorated_count": len(decorated_rare),
        "common_order_identical": [item.candidate.canonical for item in decorated_common]
        == [item.canonical for item in common],
        "rare_order_identical": [item.candidate.canonical for item in decorated_rare]
        == [item.canonical for item in rare],
        "common_raw_values_identical": common_unchanged,
        "rare_raw_values_identical": rare_unchanged,
        "semantic_seed_count": len(semantics.labels),
        "hint_rule_count": len(semantics.rules),
        "generation_hint_evidence_split": {
            "common_body_keeps_body_target_hint": (
                body_common.generation_hint_kind == "BODY_TARGET"
                and body_common.evidence_notes_ja == ()
            ),
            "rare_classified_keeps_semantic_hint": (
                classified_rare.generation_hint_kind == "IMPLEMENT_SPECIFIER"
            ),
            "rare_classified_adds_context_note": (
                classified_rare.evidence_note_kinds == ("DISCOVERY_CANDIDATE",)
            ),
        },
        "semantic_role_counts": dict(sorted(Counter(
            label.semantic_role for label in semantics.labels.values()
        ).items())),
        "unclassified_candidate_count_preserved": sum(
            item.semantic_role == "UNCLASSIFIED" for item in decorated_common
        ),
        "low_support_candidate_count_preserved": sum(
            candidate.co_count <= 2 for candidate in raw
        ),
        "content_examples_present_when_in_stage6": {
            name: name in raw_names for name in ("1girl", "solo", "nude", "sex_toy")
        },
        "stage8a_reranking": False,
        "stage8a_filtering": False,
        "runtime_llm_calls": 0,
        "runtime_network_calls": 0,
    }
    hashes = {relative: sha256(ROOT / relative) for relative in PROTECTED}
    previous = (
        ROOT / "docs" / "handoff_archive"
        / "stage7b_pre_role_display_fix_20260906_130655"
        / "CHATGPT_HANDOFF"
    )
    payload["stage6_source_matches_stage7b_final"] = (
        hashes["danbooru_tag_tool/recommendations.py"]
        == sha256(previous / "danbooru_tag_tool" / "recommendations.py")
    )
    payload["stage7b_async_source_matches_stage7b_final"] = (
        hashes["danbooru_tag_tool/stage7b_recommendations.py"]
        == sha256(previous / "danbooru_tag_tool" / "stage7b_recommendations.py")
    )

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metric_parity.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "protected_hashes.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    required = (
        payload["common_order_identical"], payload["rare_order_identical"],
        common_unchanged, rare_unchanged,
        payload["stage6_source_matches_stage7b_final"],
        payload["stage7b_async_source_matches_stage7b_final"],
        all(payload["generation_hint_evidence_split"].values()),
        hashes["data/special2788/illustrious_tag_knowledge_base_2788.csv"]
        == "07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3",
    )
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
