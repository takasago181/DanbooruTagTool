#!/usr/bin/env python3
"""Build v3 identity/root nodes and non-authoritative structure candidates."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import *

GRAPH = OUT / "structure_graph_v3.csv"
MANIFEST = OUT / "source_manifest_v3.json"
GRAPH_FIELDS = ["subject_type", "subject_key", "relation_type", "object_type", "object_key", "review_state", "evidence_id", "derivation"]

def main() -> None:
    characters, copyrights, _ = load_catalog()
    candidates = canonical_family_candidates(characters)
    char_keys = {r["canonical_tag"] for r in characters}
    # Name-shape relations are deliberately candidate-only. They are useful for batching review,
    # but can never become VARIANT_OF authority without a separately validated evidence row.
    for character in characters:
        tag = character["canonical_tag"]
        match = re.match(r"^(.*)_\(([^()]*)\)_\(([^()]*)\)$", tag)
        if match:
            base = f"{match.group(1)}_({match.group(3)})"
            if base in char_keys:
                candidates.append({"subject_type": "Character", "subject_key": tag, "relation_type": "VARIANT_OF",
                                  "object_type": "Character", "object_key": base, "review_state": "CANDIDATE",
                                  "evidence_id": "", "derivation": "nested qualifier base hypothesis; candidate only"})
        elif tag.endswith(")") and "_(" in tag:
            base = tag.rsplit("_(", 1)[0]
            if base in char_keys:
                candidates.append({"subject_type": "Character", "subject_key": tag, "relation_type": "VARIANT_OF",
                                  "object_type": "Character", "object_key": base, "review_state": "CANDIDATE",
                                  "evidence_id": "", "derivation": "terminal qualifier base hypothesis; candidate only"})
    # Explicit base references in validated variant-decision records are still candidates here;
    # only a validated Evidence Ledger edge can promote them to authority.
    for d in load_decisions():
        if d.get("validation_state") == "PASS" and d.get("scope") in {"DIRECT_CHARACTER", "FAMILY_QUALIFIER", "VARIANT_CHARACTER"} and d.get("home_copyright"):
            candidates.append({"subject_type": "Character" if d.get("scope") != "FAMILY_QUALIFIER" else "Family",
                              "subject_key": d.get("key", ""), "relation_type": "DIRECT_HOME" if d.get("scope") != "FAMILY_QUALIFIER" else "FAMILY_HOME",
                              "object_type": "Copyright", "object_key": d.get("home_copyright", ""),
                              "review_state": "CANDIDATE", "evidence_id": "",
                              "derivation": "decision target inspected for current-root integrity; not authority"})
        if d.get("scope") != "VARIANT_CHARACTER" or not d.get("base_character"):
            continue
        candidates.append({
            "subject_type": "Character", "subject_key": d.get("key", ""),
            "relation_type": "VARIANT_OF", "object_type": "Character",
            "object_key": d.get("base_character", ""), "review_state": "CANDIDATE",
            "evidence_id": "", "derivation": "explicit decision base field; evidence validation occurs in migration",
        })
    candidates.sort(key=lambda r: (r["subject_type"], r["subject_key"], r["relation_type"], r["object_key"]))
    write_csv(GRAPH, candidates, GRAPH_FIELDS)
    input_paths = [CATALOG, ORIGIN, ORIGIN_META]
    if V2_APPLIED.exists(): input_paths.append(V2_APPLIED)
    if V2_MASTER.exists(): input_paths.append(V2_MASTER)
    input_paths += [DECISION_DIR / n for n in DECISION_FILES if (DECISION_DIR / n).exists()]
    input_paths += sorted(EVIDENCE_DIR.glob("*.csv"))
    manifest = {
        "schema_version": 3,
        "purpose": "research/build-time only; candidate graph is never HOME authority",
        "inputs": [{"path": relpath(p), "sha256": sha256_file(p)} for p in sorted(set(input_paths))],
        "character_count": len(characters),
        "copyright_root_count": len(copyrights),
        "character_keys_sha256": sha256_text("\n".join(sorted(r["canonical_tag"] for r in characters))),
        "copyright_keys_sha256": sha256_text("\n".join(sorted(r["canonical_tag"] for r in copyrights))),
        "candidate_relation_counts": dict(sorted(__import__("collections").Counter(r["relation_type"] for r in candidates).items())),
        "candidate_graph_path": relpath(GRAPH),
        "source_policy": "Issue #70 accepted Character/Copyright catalog, Issue #179 origin handoff, Issue #180 evidence and validated decisions; generated queues are excluded as authority.",
        "legacy_data_migration": {"applied_authority_ledger": relpath(V2_APPLIED), "used_for": "traceability only; values are not authority", "v2_master": relpath(V2_MASTER), "used_for_master": "migration regression baseline only"},
    }
    write_json(MANIFEST, manifest)
    print(json.dumps({"characters": len(characters), "copyright_roots": len(copyrights), "candidate_edges": len(candidates), "manifest": relpath(MANIFEST)}, indent=2))

if __name__ == "__main__":
    main()
