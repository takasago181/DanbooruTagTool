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
"last_origin":("https://www.last-origin.com/bio.html","OFFICIAL_ROSTER","Official LAST ORIGIN site exposes its Bioroid/character roster."),
"apex_legends":("https://www.ea.com/ja/games/apex-legends/apex-legends/characters-hub","OFFICIAL_ROSTER","EA official Apex Legends character hub identifies playable Legends."),
"guilty_gear":("https://www.guiltygear.com/ggst/sw/jp/","OFFICIAL_SERIES_CHARACTER_CONTEXT","Arc System Works official Guilty Gear site identifies series/game characters and Japanese names."),
"street_fighter":("https://www.streetfighter.com/6/ja-jp/character","OFFICIAL_ROSTER","Capcom official Street Fighter 6 character page identifies franchise characters."),
"elden_ring":("https://www.eldenring.jp/","OFFICIAL_TITLE_CONTEXT","Official ELDEN RING site provides title/world/character context."),
"sousou_no_frieren":("https://frieren-anime.jp/character/","OFFICIAL_ROSTER","Official Frieren anime character page identifies the cast."),
"infinity_nikki":("https://infinitynikki.infoldgames.com/","OFFICIAL_TITLE_CONTEXT","Official Infinity Nikki site identifies the title and its character context."),
"trickcal":("https://trickcal.com/","OFFICIAL_TITLE_CONTEXT","Official Trickcal site identifies the title/character context."),
"ragnarok_online":("https://ragnarokonline.gungho.jp/","OFFICIAL_TITLE_CONTEXT","Official Ragnarok Online site establishes the title and game character context."),
"senran_kagura":("https://senrankagura.marv.jp/series/kaguraPBS/character/","OFFICIAL_ROSTER","Marvelous official Senran Kagura character page identifies franchise characters."),
"omori":("https://www.omori-game.com/","OFFICIAL_TITLE_CONTEXT","Official OMORI game site establishes the title/character context."),
"warship_girls_r":("https://www.moefantasy.co.jp/","OFFICIAL_PUBLISHER_CONTEXT","Official publisher site establishes Warship Girls R product context."),
"path_to_nowhere":("https://ptn.aisnogames.com/","OFFICIAL_TITLE_CONTEXT","Official Path to Nowhere site establishes title/character context."),
"animal_crossing":("https://www.nintendo.com/jp/character/mori/index.html","OFFICIAL_FRANCHISE_CONTEXT","Nintendo official Animal Crossing page establishes franchise character context."),
"disgaea":("https://disgaea.jp/","OFFICIAL_FRANCHISE_CONTEXT","Nippon Ichi official Disgaea portal establishes franchise/character context."),
"skullgirls":("https://skullgirls.com/characters/","OFFICIAL_ROSTER","Official Skullgirls character roster identifies franchise characters."),
"dungeon_and_fighter":("https://www.dfoneople.com/gameinfo/character","OFFICIAL_ROSTER","Official Dungeon Fighter Online character page identifies game characters."),
"brown_dust":("https://www.browndust2.com/","OFFICIAL_TITLE_CONTEXT","Official Brown Dust 2 site establishes title/character context."),
"black_survival":("https://playeternalreturn.com/","OFFICIAL_SUCCESSOR_CONTEXT_REVIEW","Official Nimble Neuron site provides franchise character context; root semantics still require caution."),
"queen's_blade":("https://queensblade.net/","OFFICIAL_FRANCHISE_CONTEXT","Official Queen's Blade portal establishes franchise character context."),
"league":("https://www.leagueoflegends.com/ja-jp/champions/","OFFICIAL_ROSTER","Riot official League of Legends champion roster supports league -> league_of_legends normalization."),
"housamo":("https://housamo.jp/","OFFICIAL_TITLE_CONTEXT","Official Tokyo Afterschool Summoners site supports housamo normalization."),
"girls'_frontline_2":("https://gf2.haoplay.com/","OFFICIAL_TITLE_CONTEXT","Official Girls' Frontline 2: Exilium site supports normalized root."),
"p&d":("https://pad.gungho.jp/member/","OFFICIAL_TITLE_CONTEXT","GungHo official Puzzle & Dragons site supports p&d normalization."),
"sao":("https://sao-game.jp/","OFFICIAL_FRANCHISE_CONTEXT","Official Sword Art Online game portal supports sao -> sword_art_online normalization."),
"tf2":("https://www.teamfortress.com/","OFFICIAL_TITLE_CONTEXT","Valve official Team Fortress site supports tf2 -> team_fortress_2 normalization."),
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
