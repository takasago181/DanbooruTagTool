"""Build only the current-dictionary overlay; never rebuilds raw postings."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from danbooru_tag_tool.canonical_overlay import OVERLAY_FORMAT_VERSION, CanonicalOverlay
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.runtime_index import RuntimeIndex


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(root: Path, index_path: Path, output: Path) -> None:
    index = RuntimeIndex(index_path, verify_hashes=True)
    core = TagKnowledgeCore.load(root)
    identities = []
    canonical_to_source: dict[str, list[int]] = {}
    counts = {"exact_current_general": 0, "unique_alias_to_current_general": 0,
              "runtime_only": 0, "exact_current_non_general": 0,
              "unique_alias_to_current_non_general": 0, "ambiguous": 0,
              "normalization_collision": 0}
    for source_id, source_tag in enumerate(index.tags):
        resolution = core.resolve_exact(source_tag)
        canonical = None
        if source_tag in core.canonical:
            canonical = source_tag
            identity = "exact_current_general" if core.canonical[source_tag].category == 0 else "exact_current_non_general"
        elif resolution.match_type == "canonical":
            # A normalized canonical collision is retained as an unresolved identity.
            if len(resolution.canonical_candidates) == 1:
                canonical = resolution.canonical_candidates[0]
                identity = "exact_current_general" if core.canonical[canonical].category == 0 else "exact_current_non_general"
            else:
                identity = "normalization_collision"
        elif resolution.match_type == "alias":
            if len(resolution.canonical_candidates) != 1:
                identity = "ambiguous"
            else:
                canonical = resolution.canonical_candidates[0]
                identity = ("unique_alias_to_current_general" if core.canonical[canonical].category == 0
                            else "unique_alias_to_current_non_general")
        else:
            identity = "runtime_only"
        counts[identity] += 1
        identities.append({"source_tag": source_tag, "identity": identity, "canonical": canonical})
        if canonical is not None:
            canonical_to_source.setdefault(canonical, []).append(source_id)
    payload = {"canonical_to_source_tag_ids": {key: value for key, value in sorted(canonical_to_source.items())},
               "source_tag_identities": identities}
    payload_hash = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    alias_count = counts["unique_alias_to_current_general"] + counts["unique_alias_to_current_non_general"]
    merge_groups = sum(len(ids) > 1 for ids in canonical_to_source.values())
    metadata = {"overlay_format_version": OVERLAY_FORMAT_VERSION,
                "statistics_dataset_snapshot_id": index.snapshot_id,
                "tag_dictionary_snapshot": "2026-09-02",
                "tag_dictionary_sha256": sha256(root / "data/source/danbooru-2026-09-02.csv"),
                "mapping_build_timestamp": datetime.now(timezone.utc).isoformat(),
                "exact_count": counts["exact_current_general"] + counts["exact_current_non_general"],
                "alias_count": alias_count,
                "runtime_only_count": counts["runtime_only"],
                "merge_group_count": merge_groups,
                "statistics_tag_scope": "general",
                "model_agnostic_statistics": True,
                "identity_counts": counts,
                "overlay_payload_sha256": payload_hash}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"metadata": metadata, **payload}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    loaded = CanonicalOverlay(index, output, expected_snapshot_id=index.snapshot_id)
    loaded.validate()
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(ROOT, args.index, args.output)
