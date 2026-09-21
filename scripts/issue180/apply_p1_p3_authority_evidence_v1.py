#!/usr/bin/env python3
"""Issue #180 P1/P3 first-party authority evidence batch v1. Research only."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
IN=R/"artifacts/issue180-full-preflight/P1_P3_CATALOG_SEMANTIC_GATE_V1.csv"
OUT=R/"artifacts/issue180-full-preflight/P1_P3_AUTHORITY_EVIDENCE_V1.csv"
SUM=R/"artifacts/issue180-full-preflight/p1_p3_authority_evidence_v1_summary.json"
# Only first-party/official evidence verified in this batch. Absence means unresolved, never rejection.
E={
"overwatch":("https://overwatch.blizzard.com/ja-jp/heroes/","OFFICIAL_ROSTER","Blizzard official Heroes roster identifies Overwatch heroes."),
"chainsaw_man":("https://chainsawman.dog/tvseries/character/","OFFICIAL_ROSTER","Official Chainsaw Man anime character page identifies the cast."),
"elsword":("https://elsword.koggames.com/characters/","OFFICIAL_ROSTER","KOG official Elsword character roster."),
"stella_sora":("https://stellasora.global/","OFFICIAL_ROSTER","Official Stella Sora site exposes its character roster."),
"deltarune":("https://deltarune.com/","OFFICIAL_TITLE_CHARACTER_CONTEXT","Official DELTARUNE site describes its main characters and title context."),
}
def main():
 rows=list(csv.DictReader(IN.open(encoding="utf-8-sig",newline="")))
 out=[]
 for r in rows:
  q=r["qualifier"]; url,kind,claim=E.get(q,("","",""))
  eligible=r["gate_state"] in ("CATALOG_OK_AUTHORITY_PENDING","NORMALIZATION_ROOT_EXISTS_AUTHORITY_PENDING")
  state="FIRST_PARTY_EVIDENCE_FOUND_PENDING_SECOND_REVIEW" if eligible and url else ("HOME_UNRESOLVED" if r["gate_state"]=="HOME_UNRESOLVED" else "FIRST_PARTY_EVIDENCE_PENDING")
  out.append({**r,"official_source_url":url,"evidence_kind":kind,"official_source_claim":claim,
              "authority_state":state,"second_review":"PENDING" if url else "NOT_READY",
              "production_approved":"false"})
 with OUT.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"families":len(out),"first_party_evidence_found":sum(bool(r["official_source_url"]) for r in out),
    "still_authority_pending":sum(r["authority_state"]=="FIRST_PARTY_EVIDENCE_PENDING" for r in out),
    "home_unresolved":sum(r["authority_state"]=="HOME_UNRESOLVED" for r in out),
    "authority_approved":0,"production_modified":False}
 SUM.write_text(json.dumps(x,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,indent=2))
if __name__=="__main__":main()
