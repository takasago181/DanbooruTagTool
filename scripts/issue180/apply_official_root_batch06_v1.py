#!/usr/bin/env python3
"""Issue #180 official-root authority batch 06.

Research-only / fail-closed.
Consumes manually reviewed official franchise/character authority for a
high-yield set of remaining IP qualifier families. Exact qualifier roots are
accepted only when the canonical Copyright root exists. Explicit nested
variants remain unresolved pending separate officiality review.
"""
import csv,json,re
from pathlib import Path

R=Path(__file__).resolve().parents[2]
A=R/"artifacts/issue180-full-preflight"
D=A/"POST_NORMALIZED_REVIEW"
IP=D/"IP_REMAINING.csv"
CAT=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
EV=R/"docs/issue180/evidence/official_root_authority_batch06.csv"
OUT=D/"OFFICIAL_ROOT_BATCH06_V1.csv"
SUMMARY=D/"official_root_batch06_v1_summary.json"

EXPECTED_FAMILIES=6
EXPECTED_ROWS=196
EXPECTED_VARIANTS=29
EXPECTED_PASS=167

def read_csv(p): return list(csv.DictReader(p.open(encoding="utf-8-sig",newline="")))

def nested_variant(tag,family):
    suffix=f"_({family})"
    if not tag.endswith(suffix): return False
    return re.search(r"_\([^()]+\)$",tag[:-len(suffix)]) is not None

def main():
    evrows=read_csv(EV); evidence={r["family"]:r for r in evrows}
    if len(evrows)!=EXPECTED_FAMILIES or len(evidence)!=EXPECTED_FAMILIES:
        raise SystemExit(f"evidence family count drift: {len(evrows)}")
    if any(r.get("root_review")!="PASS" for r in evrows):
        raise SystemExit("batch06 evidence contains non-PASS root")
    catalog=read_csv(CAT)
    roots={r["canonical_tag"] for r in catalog if r.get("category_name")=="Copyright"}
    missing=sorted({r["home_copyright"] for r in evrows if r["home_copyright"] not in roots})
    if missing: raise SystemExit("missing Copyright roots: "+",".join(missing))
    rows=[r for r in read_csv(IP) if r.get("final_qualifier") in evidence]
    if len(rows)!=EXPECTED_ROWS:
        raise SystemExit(f"batch06 population drift: expected {EXPECTED_ROWS}, got {len(rows)}")
    counts={}
    for r in rows: counts[r["final_qualifier"]]=counts.get(r["final_qualifier"],0)+1
    for family,e in evidence.items():
        if counts.get(family,0)!=int(e["expected_rows"]):
            raise SystemExit(f"family row count drift {family}: expected {e['expected_rows']}, got {counts.get(family,0)}")
    out=[]; per={}
    for r in rows:
        family=r["final_qualifier"]; e=evidence[family]; variant=nested_variant(r["canonical_tag"],family)
        review="UNRESOLVED" if variant else "PASS"
        row=dict(r); row.update({
          "candidate_root_hint":e["home_copyright"],"evidence_url":e["evidence_url"],
          "evidence_type":e["evidence_type"],"root_review":e["root_review"],
          "authority_decision":"VARIANT_OFFICIALITY_PENDING" if variant else "QUALIFIER_PLUS_OFFICIAL_ROOT_AUTHORITY",
          "variant_gate":"NESTED_VARIANT_REQUIRES_OFFICIALITY" if variant else "DIRECT_TAG",
          "second_review":review,"production_approved":"false"})
        out.append(row)
        x=per.setdefault(family,{"rows":0,"pass":0,"unresolved":0});x["rows"]+=1;x["pass" if review=="PASS" else "unresolved"]+=1
    variants=sum(r["second_review"]=="UNRESOLVED" for r in out); passed=sum(r["second_review"]=="PASS" for r in out)
    if (passed,variants)!=(EXPECTED_PASS,EXPECTED_VARIANTS):
        raise SystemExit(f"batch06 pass/variant drift: expected {(EXPECTED_PASS,EXPECTED_VARIANTS)}, got {(passed,variants)}")
    with OUT.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    summary={"families":len(evidence),"family_rows":len(out),"second_review_pass":passed,
      "variant_officiality_pending":variants,"missing_roots":len(missing),"multi_home_conflicts":0,
      "auto_inferred":0,"legacy_relation_used":False,"accepted_source_modified":False,
      "production_modified":False,"per_family":per}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
