#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def read(rel: str) -> str:
    p=ROOT/rel
    if not p.is_file():
        raise SystemExit(f"missing pre-handoff authority: {rel}")
    return p.read_text(encoding="utf-8")

def need(text: str, needle: str, label: str):
    if needle not in text:
        raise SystemExit(f"{label}: required text missing: {needle}")

def forbid(text: str, needle: str, label: str):
    if needle in text:
        raise SystemExit(f"{label}: stale/forbidden text present: {needle}")

def load_validator():
    path=ROOT/"scripts/issue132/validate_luna_pass_a.py"
    spec=importlib.util.spec_from_file_location("issue132_validator_consistency",path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load Pass A validator")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    current=read("docs/issue132/CURRENT_RECOMMENDED_DIRECTION.md")
    protocol=read("docs/issue132/FULL_SEMANTIC_REVIEW_PROTOCOL.md")
    neutral=read("docs/issue132/LUNA_NEUTRAL_INPUT_CONTRACT.md")
    route=read("docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md")
    ledger=read("docs/issue132/LUNA_PASS_A_LEDGER_CONTRACT.md")
    handoff=read("docs/issue132/CODEX_FULL_SEMANTIC_REVIEW_HANDOFF.md")
    workflow=read(".github/workflows/issue132_full_discovery_audit.yml")
    v=load_validator()

    if len(v.FIELDS)!=22:
        raise SystemExit(f"Pass A ledger field count drift: {len(v.FIELDS)} != 22")

    for label,text in (("current",current),("protocol",protocol),("ledger",ledger),("handoff",handoff)):
        forbid(text,"R001",label)
        forbid(text,"codex_full_review_queue.csv",label)
        forbid(text,"KEEP_STRONG",label)
        forbid(text,"SECONDARY_CANDIDATE",label)

    need(current,"31,003 identities","current")
    need(current,"Pass A — independent Luna discovery map","current")
    need(current,"Status: **READY FOR CODEX LUNA PASS A / NO PRODUCTION CHANGE**","current")
    need(current,"**READY FOR CODEX LUNA PASS A**","current")
    need(current,"New top-level route IDs or new facet axes are **default-deny**","current")
    need(protocol,"local_refinement_ids","protocol")
    need(protocol,"MISSING_LOCAL_REFINEMENT","protocol")
    need(neutral,"review_seq","neutral")
    need(neutral,"identity_key","neutral")
    need(neutral,"source_surfaces","neutral")
    need(neutral,"current Unified route IDs","neutral")
    need(route,"## 4.5. Existing local refinement vocabulary","route")
    need(ledger,"22. `uncertainty_note`","ledger")
    need(ledger,"pass_a_contract_manifest_v1.json","ledger")
    need(ledger,"pass_a_progress_summary.json","ledger")
    need(handoff,"Status: **READY FOR CODEX LUNA PASS A**","handoff")
    need(handoff,"python scripts/issue132/bootstrap_luna_pass_a.py","handoff")
    need(handoff,"python scripts/issue132/finalize_luna_pass_a.py","handoff")
    need(handoff,"reviewed identities = **31,003**","handoff")

    for script in (
        "scripts/issue132/full_discovery_coverage_audit.py",
        "scripts/issue132/build_luna_neutral_input.py",
        "scripts/issue132/check_review_vocabulary_against_code.py",
        "scripts/issue132/build_pass_a_contract_manifest.py",
        "scripts/issue132/test_validate_luna_pass_a.py",
        "scripts/issue132/test_build_pass_b_diff.py",
    ):
        need(workflow,script,"workflow")

    print("PASS Issue132 final handoff authority consistency")

if __name__=="__main__":
    main()
