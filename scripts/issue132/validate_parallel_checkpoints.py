#!/usr/bin/env python3
from __future__ import annotations
import csv, importlib.util, json
from pathlib import Path
from parallel_overlay import load_checkpoint_union, apply_corrections

ROOT=Path(__file__).resolve().parents[2]
LANES=(1,2,3)

def load_base():
    p=ROOT/"scripts/issue132/validate_luna_pass_a.py"
    s=importlib.util.spec_from_file_location("issue132_parallel_base",p)
    if s is None or s.loader is None: raise SystemExit("cannot load base validator")
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def read_csv(p):
    with Path(p).open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def main():
    base=load_base()
    neutral_path=ROOT/"artifacts/issue132/luna-neutral/luna_neutral_review_input_v2.csv"
    neutral=read_csv(neutral_path)
    contract=ROOT/"docs/issue132/parallel/pass_a_contract_manifest_v1.json"
    _,errs=base.verify_contract_manifest(contract,neutral_path,neutral)
    total=0; summary={}
    for lane in LANES:
        assigned=[r for r in neutral if ((int(r["review_seq"])-1)%3)+1==lane]
        raw,ranges,load_errs=load_checkpoint_union(ROOT,lane,base.FIELDS)
        errs.extend(load_errs)
        if len(raw)>len(assigned): errs.append(f"lane {lane}: too many rows")
        expected=[r["identity_key"] for r in assigned[:len(raw)]]
        actual=[r.get("identity_key","") for r in raw]
        if actual!=expected: errs.append(f"lane {lane}: checkpoint union is not exact assigned prefix")

        effective,correction_count,corr_errs=apply_corrections(ROOT,lane,raw,ranges,base.FIELDS)
        errs.extend(corr_errs)

        seen=set()
        for row in effective:
            ident=row.get("identity_key","")
            if ident in seen: errs.append(f"lane {lane}: duplicate {ident}")
            seen.add(ident)
            seq=next((int(x["review_seq"]) for x in assigned if x["identity_key"]==ident),None)
            if seq is None: errs.append(f"lane {lane}: unassigned identity {ident}")
            else: errs.extend(base.validate_row(row,seq))
        total+=len(effective)
        summary[str(lane)]={
            "reviewed":len(effective),
            "assigned":len(assigned),
            "checkpoints":len(ranges),
            "corrections_applied":correction_count
        }
    result={"schema_version":"issue132-parallel-repo-validation-v2","reviewed_total":total,"lanes":summary,"error_count":len(errs)}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errs:
        for e in errs[:100]: print("ERROR:",e)
        raise SystemExit(1)

if __name__=="__main__": main()
