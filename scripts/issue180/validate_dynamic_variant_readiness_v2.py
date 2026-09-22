#!/usr/bin/env python3
"""Regression gate for dynamically unlocked Issue #180 variant patterns."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

R=Path(__file__).resolve().parents[2]
D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2"
VARIANTS=D/"REMAINING_VARIANT_WORK_V2.csv"
DYNAMIC=D/"DYNAMIC_VARIANT_PATTERN_GROUPS_V2.csv"
REVIEWED=D/"REVIEWED_VARIANT_PATTERNS_V2.csv"
READINESS=D/"autonomous_completion_readiness_v2.json"
POLICY=R/"docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"


def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def pattern_id(row):
    home=(row.get("base_home_candidate") or "").strip()
    outer=(row.get("outer_ip_qualifier") or "").strip() or "-"
    variant=(row.get("variant_qualifier") or "").strip()
    if not home or not variant:
        raise SystemExit(f"ready variant missing dynamic pattern key: {row.get('canonical_tag')}")
    return f"{home}::{outer}::{variant}"


def main():
    variants=read(VARIANTS)
    dynamic=read(DYNAMIC)
    reviewed=read(REVIEWED)
    readiness=json.loads(READINESS.read_text(encoding="utf-8"))
    policy=json.loads(POLICY.read_text(encoding="utf-8"))
    threshold=int(policy["mandatory_variant_pattern_min_rows"])

    expected=Counter()
    for row in variants:
        if row.get("work_state")=="BASE_HOME_READY_OFFICIALITY_REVIEW":
            expected[pattern_id(row)]+=1

    ids=[r["pattern_id"].strip() for r in dynamic]
    if len(ids)!=len(set(ids)):
        raise SystemExit("duplicate pattern_id in DYNAMIC_VARIANT_PATTERN_GROUPS_V2.csv")
    actual={r["pattern_id"].strip():int(r["character_rows"]) for r in dynamic}
    if actual!=dict(expected):
        missing={k:v for k,v in expected.items() if actual.get(k)!=v}
        extra={k:v for k,v in actual.items() if expected.get(k)!=v}
        raise SystemExit(f"dynamic variant registry mismatch missing_or_changed={list(missing.items())[:10]} extra_or_changed={list(extra.items())[:10]}")

    mandatory={k:v for k,v in expected.items() if v>=threshold}
    reviewed_keys={r.get("pattern_id","").strip() for r in reviewed if r.get("pattern_id","").strip()}
    expected_missing={k:v for k,v in mandatory.items() if k not in reviewed_keys}
    reported_missing={str(x[0]):int(x[1]) for x in readiness.get("mandatory_variant_patterns_missing",[])}

    if readiness.get("mandatory_variant_patterns_total")!=len(mandatory):
        raise SystemExit(
            f"readiness mandatory variant total mismatch: {readiness.get('mandatory_variant_patterns_total')} != {len(mandatory)}"
        )
    if reported_missing!=expected_missing:
        raise SystemExit(
            f"readiness missing dynamic pattern mismatch expected={list(expected_missing.items())[:10]} reported={list(reported_missing.items())[:10]}"
        )

    result={
        "ready_variant_rows":sum(expected.values()),
        "dynamic_variant_patterns":len(expected),
        "mandatory_threshold":threshold,
        "mandatory_variant_patterns":len(mandatory),
        "reviewed_variant_patterns":len(reviewed_keys),
        "mandatory_variant_patterns_missing":len(expected_missing),
        "gate":"PASS",
    }
    (D/"dynamic_variant_readiness_validation_v2.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
