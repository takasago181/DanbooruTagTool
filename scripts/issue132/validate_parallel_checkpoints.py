#!/usr/bin/env python3
from __future__ import annotations
import csv, importlib.util, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LANES=(1,2,3)
PAT=re.compile(r"^checkpoint_(\d{6})_(\d{6})\.csv$")

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
    neutral=read_csv(ROOT/"artifacts/issue132/luna-neutral/luna_neutral_review_input_v2.csv")
    contract=ROOT/"docs/issue132/parallel/pass_a_contract_manifest_v1.json"
    _,errs=base.verify_contract_manifest(contract,ROOT/"artifacts/issue132/luna-neutral/luna_neutral_review_input_v2.csv",neutral)
    total=0; summary={}
    for lane in LANES:
        assigned=[r for r in neutral if ((int(r["review_seq"])-1)%3)+1==lane]
        rows=[]; expect=1; count=0
        d=ROOT/f"docs/issue132/parallel/lane-{lane}/checkpoints"
        if d.exists():
            for p in sorted(d.glob("checkpoint_*.csv")):
                m=PAT.match(p.name)
                if not m:
                    errs.append(f"lane {lane}: invalid checkpoint filename {p.name}"); continue
                a,b=map(int,m.groups())
                if a!=expect:
                    errs.append(f"lane {lane}: checkpoint {p.name} starts {a}, expected {expect}")
                with p.open("r",encoding="utf-8-sig",newline="") as f:
                    r=csv.DictReader(f); header=r.fieldnames or []; data=list(r)
                if header!=base.FIELDS: errs.append(f"lane {lane}: {p.name} header mismatch")
                if not data: errs.append(f"lane {lane}: {p.name} empty")
                if b-a+1!=len(data): errs.append(f"lane {lane}: {p.name} range/count mismatch")
                rows.extend(data); expect=b+1; count+=1
        if len(rows)>len(assigned): errs.append(f"lane {lane}: too many rows")
        expected=[r["identity_key"] for r in assigned[:len(rows)]]
        actual=[r.get("identity_key","") for r in rows]
        if actual!=expected: errs.append(f"lane {lane}: checkpoint union is not exact assigned prefix")
        seen=set()
        for row in rows:
            ident=row.get("identity_key","")
            if ident in seen: errs.append(f"lane {lane}: duplicate {ident}")
            seen.add(ident)
            seq=next((int(x["review_seq"]) for x in assigned if x["identity_key"]==ident),None)
            if seq is None: errs.append(f"lane {lane}: unassigned identity {ident}")
            else: errs.extend(base.validate_row(row,seq))
        total+=len(rows)
        summary[str(lane)]={"reviewed":len(rows),"assigned":len(assigned),"checkpoints":count}
    result={"schema_version":"issue132-parallel-repo-validation-v1","reviewed_total":total,"lanes":summary,"error_count":len(errs)}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errs:
        for e in errs[:100]: print("ERROR:",e)
        raise SystemExit(1)

if __name__=="__main__": main()
