#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAT=ROOT/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
GATE=ROOT/"artifacts/issue180-full-preflight/P1_P3_CATALOG_SEMANTIC_GATE_V1.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/P1_P3_JAPANESE_DISPLAY_AUDIT_V2.csv"
SUM=ROOT/"artifacts/issue180-full-preflight/p1_p3_japanese_display_audit_v2_summary.json"
JP=re.compile(r"[ぁ-んァ-ヶ一-龯々〆ヵヶ]")
def main():
 with CAT.open("r",encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
 fields=list(rows[0].keys())
 display_field="display_ja" if "display_ja" in fields else None
 search_field="search_ja" if "search_ja" in fields else None
 bytag={r["canonical_tag"]:r for r in rows if r["category_name"]=="Copyright"}
 out=[]
 for g in csv.DictReader(GATE.open("r",encoding="utf-8-sig",newline="")):
  root=g["candidate_root"];r=bytag.get(root,{})
  display=(r.get(display_field,"") if display_field else "").strip()
  search=(r.get(search_field,"") if search_field else "").strip()
  display_jp=bool(JP.search(display)); search_jp=bool(JP.search(search))
  if display_jp: state="JP_DISPLAY_PRESENT"
  elif search_jp: state="JP_SEARCH_PRESENT_DISPLAY_REVIEW"
  elif display or search: state="NON_JP_SURFACE_REVIEW"
  else: state="JP_SURFACE_MISSING"
  authority_relevant=(g["gate_state"]!="HOME_UNRESOLVED" and bool(root))
  out.append({**g,"display_field":display_field or "","search_field":search_field or "","copyright_display_ja":display,
   "copyright_search_ja":search,"japanese_surface_state":state,"authority_relevant":str(authority_relevant).lower(),"japanese_review_required":str(authority_relevant and not display_jp).lower()})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"display_field":display_field,"search_field":search_field,
    "jp_display_present":sum(r["japanese_surface_state"]=="JP_DISPLAY_PRESENT" for r in out),
    "jp_search_present_display_review":sum(r["japanese_surface_state"]=="JP_SEARCH_PRESENT_DISPLAY_REVIEW" for r in out),
    "non_jp_or_missing_surface":sum(r["japanese_surface_state"] in ("NON_JP_SURFACE_REVIEW","JP_SURFACE_MISSING") for r in out),
    "authority_relevant_families":sum(r["authority_relevant"]=="true" for r in out),
    "authority_relevant_jp_display_present":sum(r["authority_relevant"]=="true" and r["japanese_surface_state"]=="JP_DISPLAY_PRESENT" for r in out),
    "japanese_review_required":sum(r["japanese_review_required"]=="true" for r in out),
    "relation_authority_changed":False,"production_modified":False}
 SUM.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
