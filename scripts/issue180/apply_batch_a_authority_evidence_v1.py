#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_AUTHORITY_WORKLIST.csv"
OUT=ROOT/"artifacts/issue180-full-preflight/ROOT_REVIEW_BATCH_A_AUTHORITY_EVIDENCE_V1.csv"
SUMMARY=ROOT/"artifacts/issue180-full-preflight/root_review_batch_a_authority_evidence_v1_summary.json"
# Evidence entered only where an official/first-party source directly supports franchise character membership.
E={
"fire_emblem":("https://www.nintendo.com/us/store/characters/fire-emblem/","Nintendo identifies Fire Emblem as a character/game franchise.","EVIDENCE_FOUND_HOME_SEMANTICS_PENDING"),
"granblue_fantasy":("https://anime.granbluefantasy.jp/1st/character/","Official Granblue anime character page lists Gran and other Granblue characters.","EVIDENCE_FOUND_HOME_SEMANTICS_PENDING"),
"kemono_friends":("https://kemono-friends.jp/","Official Kemono Friends project site has a Friends character directory.","EVIDENCE_FOUND_HOME_SEMANTICS_PENDING"),
"one_piece":("https://one-piece.com/character/index.html","Official ONE PIECE site provides a character directory.","EVIDENCE_FOUND_HOME_SEMANTICS_PENDING"),
"zenless_zone_zero":("https://zenless.hoyoverse.com/ja-jp/character","Official HoYoverse ZZZ site provides character introductions.","EVIDENCE_FOUND_HOME_SEMANTICS_PENDING"),
}
def main():
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh: rows=list(csv.DictReader(fh))
    out=[]
    for r in rows:
        q=r["qualifier"]
        if q in E:
            url,claim,state=E[q]
            r["official_source_url"]=url;r["official_source_claim"]=claim;r["root_semantics"]=state;r["authority_decision"]="EVIDENCE_FOUND_PENDING_SECOND_REVIEW"
        out.append(r)
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
    found=sum(bool(r["official_source_url"]) for r in out)
    summary={"families":len(out),"first_party_evidence_found":found,"still_pending":len(out)-found,
      "home_approved":0,"second_review_required":len(out),"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
