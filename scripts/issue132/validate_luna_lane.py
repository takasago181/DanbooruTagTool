#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LANE_COUNT=3

def load_base():
    path=ROOT/"scripts/issue132/validate_luna_pass_a.py"
    spec=importlib.util.spec_from_file_location("issue132_base_validator",path)
    if spec is None or spec.loader is None:
        raise SystemExit("unable to load base validator")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def read_csv(path: Path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def lane_for_seq(seq: int) -> int:
    return ((seq-1) % LANE_COUNT) + 1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--ledger",required=True)
    ap.add_argument("--lane",required=True,type=int,choices=range(1,LANE_COUNT+1))
    ap.add_argument("--contract-manifest",required=True)
    ap.add_argument("--summary",default="")
    ap.add_argument("--require-complete",action="store_true")
    args=ap.parse_args()

    base=load_base()
    neutral_path=Path(args.input)
    ledger_path=Path(args.ledger)
    neutral=read_csv(neutral_path)
    ledger=read_csv(ledger_path)

    with ledger_path.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        header=reader.fieldnames or []
    if header != base.FIELDS:
        raise SystemExit("lane ledger header mismatch")

    if len(neutral)!=31_003:
        raise SystemExit(f"neutral input count mismatch: {len(neutral)}")

    _, contract_errors=base.verify_contract_manifest(
        Path(args.contract_manifest), neutral_path, neutral
    )

    assigned=[
        r for r in neutral
        if lane_for_seq(int(r["review_seq"]))==args.lane
    ]
    assigned_by={r["identity_key"]:int(r["review_seq"]) for r in assigned}
    if len(assigned_by)!=len(assigned):
        raise SystemExit("assigned lane contains duplicate identities")

    errors=list(contract_errors)
    seen=set()
    last_seq=0
    for row in ledger:
        ident=row["identity_key"]
        if ident not in assigned_by:
            errors.append(f"{ident}: not assigned to lane {args.lane}")
            continue
        if ident in seen:
            errors.append(f"{ident}: duplicate lane row")
            continue
        seen.add(ident)
        seq=int(row["review_seq"]) if row["review_seq"].isdigit() else -1
        if seq<=last_seq:
            errors.append(f"{ident}: lane ledger order is not strictly increasing")
        last_seq=seq
        errors.extend(base.validate_row(row,assigned_by[ident]))

    expected_prefix=[r["identity_key"] for r in assigned[:len(ledger)]]
    actual=[r["identity_key"] for r in ledger]
    if actual!=expected_prefix:
        errors.append(f"lane {args.lane} ledger must be an exact prefix of its deterministic assignment")

    if args.require_complete and len(ledger)!=len(assigned):
        errors.append(f"incomplete lane {args.lane}: {len(ledger)} != {len(assigned)}")

    stats={
        "schema_version":"issue132-parallel-lane-validation-v1",
        "lane":args.lane,
        "lane_count":LANE_COUNT,
        "assignment_rule":"((review_seq-1)%3)+1",
        "assigned_count":len(assigned),
        "reviewed_count":len(ledger),
        "remaining_count":len(assigned)-len(ledger),
        "complete":len(ledger)==len(assigned),
        "error_count":len(errors),
        "ledger_sha256":base.sha256_file(ledger_path),
        "contract_manifest_sha256":base.sha256_file(Path(args.contract_manifest)),
        "discovery_mode":dict(Counter(r["discovery_mode"] for r in ledger)),
        "review_depth":dict(Counter(r["review_depth"] for r in ledger)),
        "route_vocabulary_gap":dict(Counter(r["route_vocabulary_gap"] for r in ledger)),
    }
    if args.summary:
        Path(args.summary).parent.mkdir(parents=True,exist_ok=True)
        Path(args.summary).write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(stats,ensure_ascii=False,indent=2))
    if errors:
        for e in errors[:100]:
            print("ERROR:",e)
        if len(errors)>100:
            print(f"... {len(errors)-100} more errors")
        raise SystemExit(1)

if __name__=="__main__":
    main()
