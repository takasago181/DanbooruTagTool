#!/usr/bin/env python3
"""Build complete human-readable pre-freeze review for all Character rows. Research only."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]; A=R/"artifacts/issue180-full-preflight"
C=A/"CHARACTER_QUALIFIER_CENSUS.csv"; O=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
P1=A/"P1_P3_AUTHORITY_SECOND_REVIEW_V1.csv"; B1=A/"ROOT_REVIEW_BATCH_A_SECOND_REVIEW_V1.csv"; B2=A/"BATCH_A_REMAINING_7_SECOND_REVIEW_V2.csv"
OUT=A/"ISSUE180_ALL_35890_USER_REVIEW.txt"; SUM=A/"issue180_all_35890_user_review_summary.json"
def load_dec(path):
 d={}
 if not path.exists(): return d
 for r in csv.DictReader(path.open(encoding="utf-8-sig",newline="")):
  q=r.get("qualifier","")
  if not q: continue
  passed=(r.get("second_review")=="PASS" or r.get("authority_decision")=="SECOND_REVIEW_PASS_RESEARCH_ONLY")
  if passed:
   d[q]=(r.get("candidate_root") or r.get("proposed_root") or "", "HOME_CONFIRMED_RESEARCH")
 return d
def main():
 overlay={}
 for r in csv.DictReader(O.open(encoding="utf-8-sig",newline="")):
  if r.get("category_name")=="Character": overlay[r["canonical_tag"]]=r
 dec={}
 for p in (B1,B2,P1): dec.update(load_dec(p))
 rows=list(csv.DictReader(C.open(encoding="utf-8-sig",newline="")))
 counts={"HOME_CONFIRMED_RESEARCH":0,"HOME_UNRESOLVED":0}
 with OUT.open("w",encoding="utf-8",newline="\n") as f:
  f.write("Issue #180 Character→本家Copyright フリーズ前 全件確認\n")
  f.write("対象: 35,890 Character / production未変更 / 未確定は推測で埋めない\n\n")
  for i,r in enumerate(rows,1):
   tag=r["canonical_tag"]; ov=overlay.get(tag,{})
   ja=(ov.get("display_ja") or tag).strip(); q=(r.get("final_qualifier") or "").strip()
   home,state=dec.get(q,("","HOME_UNRESOLVED"))
   counts[state]+=1
   if state=="HOME_CONFIRMED_RESEARCH":
    reason=f"公式一次情報＋二次レビューPASS（qualifier: {q}）"
   elif q:
    reason=f"【未確定】qualifier '{q}' から唯一の本家HOMEを安全に確定できない"
   else:
    reason="【未確定】末尾qualifierなし。推測・旧RelatedCopyrightでは確定しない"
   f.write(f"{i:05d}. {ja}\n  Danbooru: {tag}\n  本家作品: {home or '【未確定】'}\n  判定: {state}\n  理由: {reason}\n\n")
 summary={"character_rows":len(rows),**counts,"home_count_invariant":"0..1","user_review_required_before_freeze":True,"accepted_source_modified":False,"production_modified":False}
 SUM.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
