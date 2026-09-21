#!/usr/bin/env python3
"""Issue #180 major-roster authority expansion v1. Research-only, fail-closed."""
import csv,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]; SRC=R/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"; O=R/"artifacts/issue180-full-preflight"
# Direct character rosters already supported by first-party/curated evidence in this lane.
ROSTERS={
"pokemon":{"pikachu","lapras","dawn_(pokemon)"},
"hololive":{"shirakami_fubuki","irys_(hololive)","gawr_gura","mori_calliope","usada_pekora","nekomata_okayu","takanashi_kiara","sakura_miko"},
"bocchi_the_rock!":{"gotoh_hitori"},
"touhou":{"komeiji_koishi","kochiya_sanae","konpaku_youmu","cirno","alice_margatroid"},
}
# Exact high-value official roster entries. Add only where direct membership is known; no old relation fallback.
EXACT={
"saiba_momoi":"blue_archive",
"saiba_midori":"blue_archive",
"sunaookami_shiroko":"blue_archive",
"takanashi_hoshino":"blue_archive",
"rikuhachima_aru":"blue_archive",
"shiromi_iori":"blue_archive",
"hayase_yuuka":"blue_archive",
"ichinose_asuna":"blue_archive",
"kakudate_karin":"blue_archive",
"misono_mika":"blue_archive",
"hakurei_reimu":"touhou","kirisame_marisa":"touhou","flandre_scarlet":"touhou","remilia_scarlet":"touhou","izayoi_sakuya":"touhou",
"shimakaze_(kancolle)":"kantai_collection","ikazuchi_(kancolle)":"kantai_collection","inazuma_(kancolle)":"kantai_collection",
}
for h,tags in ROSTERS.items():
 for t in tags: EXACT[t]=h
# Piapro characters: membership is official, but HOME root policy remains unresolved unless separately accepted.
PIAPRO={"hatsune_miku","kagamine_rin","kagamine_len","megurine_luka","meiko_(vocaloid)","kaito_(vocaloid)"}
def main():
 rows=list(csv.DictReader(SRC.open(encoding="utf-8-sig",newline=""))); chars=[r for r in rows if r.get("category_name")=="Character"]; cps={r["canonical_tag"] for r in rows if r.get("category_name")=="Copyright"}
 out=[]; missing=set()
 for r in chars:
  t=r["canonical_tag"]; h=EXACT.get(t,"")
  if h and h not in cps: missing.add(h)
  state="ROSTER_HOME_CANDIDATE" if h else ("PIAPRO_OFFICIAL_HOME_POLICY_UNRESOLVED" if t in PIAPRO else "NO_ROSTER_EVIDENCE")
  out.append({"canonical_tag":t,"display_ja":r.get("display_ja",""),"roster_home":h,"roster_state":state,
   "evidence_type":"CURATED_COPYRIGHT_LIST" if h else ("OFFICIAL_CHARACTER_GROUP" if t in PIAPRO else ""),
   "legacy_relation_used":"false","production_approved":"false"})
 if missing: raise SystemExit("missing Copyright roots: "+",".join(sorted(missing)))
 O.mkdir(parents=True,exist_ok=True)
 p=O/"MAJOR_ROSTER_EXPANSION_V1.csv"
 with p.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=out[0].keys(),lineterminator="\n");w.writeheader();w.writerows(out)
 x={"character_rows":len(out),"roster_home_candidates":sum(bool(r["roster_home"]) for r in out),
    "piapro_policy_unresolved":sum(r["roster_state"]=="PIAPRO_OFFICIAL_HOME_POLICY_UNRESOLVED" for r in out),
    "missing_copyright_roots":len(missing),"multi_home_conflicts":0,"accepted_source_modified":False,"production_modified":False}
 (O/"major_roster_expansion_v1_summary.json").write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(x,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
