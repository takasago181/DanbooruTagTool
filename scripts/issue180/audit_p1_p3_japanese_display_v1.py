#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAT=ROOT/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
GATE=ROOT/"artifacts/issue180-full-preflight/P1_P3_CATALOG_SEMANTIC_GATE_V1.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/P1_P3_JAPANESE_DISPLAY_AUDIT_V1.csv"
SUM=ROOT/"artifacts/issue180-full-preflight/p1_p3_japanese_display_audit_v1_summary.json"
JP=re.compile(r"[ぁ-んァ-ヶ一-龯々〆ヵヶ]")
def main():
 with CAT.open("r",encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
 fields=rows[0].keys(); display_field=next((x for x in fields if x.lower() in ("display_name","display","japanese_name","name_ja","ja")),None)
 bytag={r["canonical_tag"]:r for r in rows if r["category_name"]=="Copyright"}
 out=[]
 for g in csv.DictReader(GATE.open("r",encoding="utf-8-sig",newline="")):
  root=g["candidate_root"];r=bytag.get(root,{})
  display=(r.get(display_field,"") if display_field else "")
  state="JP_DISPLAY_PRESENT" if display and JP.search(display) else ("DISPLAY_PRESENT_NON_JP" if display else "JP_DISPLAY_MISSING_OR_FIELD_UNAVAILABLE")
  out.append({**g,"display_field":display_field or "","copyright_display":display,"japanese_display_state":state,"japanese_review_required":str(state!="JP_DISPLAY_PRESENT").lower()})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"jp_display_present":sum(r["japanese_display_state"]=="JP_DISPLAY_PRESENT" for r in out),
    "japanese_review_required":sum(r["japanese_review_required"]=="true" for r in out),"display_field":display_field,
    "relation_authority_changed":False,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
