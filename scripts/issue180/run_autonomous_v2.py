#!/usr/bin/env python3
"""One-command local bootstrap/recompile helper for Issue #180 autonomous v2."""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPT_DIR=ROOT/"scripts/issue180"
PREP=["build_single_home_pilot.py","prepare_diverse_pilot.py","validate_authority_policy.py","build_authority_candidates.py","build_full_character_preflight.py","triage_unknown_qualifiers.py","build_root_review_batch_a.py","prefill_root_review_batch_a.py","check_root_review_batch_a_catalog.py","gate_root_review_batch_a.py","build_next_root_review_backlog.py","check_next_root_review_catalog.py","build_unqualified_review_sample.py","prioritize_next_root_review.py","analyze_unqualified_sample_structure.py","build_batch_a_authority_worklist.py","apply_batch_a_authority_evidence_v1.py","second_review_batch_a_v1.py","build_batch_a_remaining_research.py","apply_batch_a_remaining_evidence_v2.py","second_review_batch_a_remaining_v2.py","build_next_p1_review_batch.py","build_next_p3_research_batch.py","review_p1_conservative_v1.py","review_p3_conservative_v1.py","gate_p1_p3_catalog_semantics_v1.py","audit_p1_p3_japanese_display_v1.py","audit_p1_p3_japanese_display_v2.py","apply_p1_p3_authority_evidence_v1.py","second_review_p1_p3_authority_v1.py","build_all_character_user_review.py","full_character_regression_v1.py","build_unqualified_authority_worklist.py","shard_p1_authority_review.py","shard_p3_semantic_research.py","shard_unqualified_controls.py","shard_p1_authority_review_x2.py","shard_p3_semantic_research_x2.py","shard_unqualified_controls_x2.py","validate_parallel_precision_gate.py","build_global_approved_qualifier_home_v1.py","build_global_unresolved_backlog_v1.py","shard_global_unresolved_families_v1.py","build_global_family_review_packets_v1.py","build_global_exact_copyright_candidates_v1.py","second_review_global_exact_copyright_v1.py","build_global_approved_qualifier_home_v1.py","build_post_exact_review_worklists_v1.py","build_remaining_normalized_candidates_v1.py","second_review_remaining_normalized_candidates_v1.py","build_global_approved_qualifier_home_v1.py","build_post_normalized_worklists_v1.py","build_unqualified_roster_candidates_v1.py","review_unqualified_exact_overlap_v1.py","shard_unqualified_roster_128_v1.py","build_attribute_variant_base_inheritance_v1.py","apply_splatoon_official_roster_v1.py","build_megabatch_authority_queues_v1.py","build_official_roster_batch01_v1.py","apply_exact_root_semantic_batch02_v1.py","apply_high_yield_official_root_batch03_v1.py","apply_official_root_batch04_v1.py","apply_direct_official_character_roster_batch05_v1.py","apply_official_root_batch06_v1.py","apply_official_root_batch07_v1.py","build_megabatch_authority_ledger_v1.py","build_major_roster_expansion_v1.py","build_character_home_master_v1.py","build_unresolved_priority_v1.py","validate_autonomous_policy_v2.py","build_autonomous_foundation_v2.py"]
RECOMPILE=["validate_autonomous_policy_v2.py","validate_authority_decisions_v2.py","compile_character_home_v2.py","validate_autonomous_completion_v2.py","build_user_review_v2.py"]

def run(names):
    for i,name in enumerate(names,1):
        path=SCRIPT_DIR/name
        if not path.exists():
            raise SystemExit(f"missing script: {path}")
        print(f"[{i:02d}/{len(names):02d}] {name}",flush=True)
        subprocess.run([sys.executable,str(path)],cwd=ROOT,check=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--recompile",action="store_true",help="reuse existing generated queues; validate decisions and rebuild v2 master/review only")
    args=ap.parse_args()
    if args.recompile:
        run(RECOMPILE)
    else:
        run(PREP)
        run(RECOMPILE)
    print("Issue #180 autonomous v2 local pipeline: PASS")

if __name__=="__main__":
    main()
