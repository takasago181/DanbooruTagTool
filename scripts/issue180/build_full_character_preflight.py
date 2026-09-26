#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"docs/issue70/data/runtime/issue70_catalog_overlay.csv"
OUTDIR=ROOT/"artifacts/issue180-full-preflight"
OUT=OUTDIR/"CHARACTER_QUALIFIER_CENSUS.csv"
SUMMARY=OUTDIR/"summary.json"
FINAL=re.compile(r"_\(([^()]+)\)$")
APPROVED={
"pokemon":"pokemon","vocaloid":"vocaloid","fate":"fate_(series)","umamusume":"umamusume",
"blue_archive":"blue_archive","honkai:_star_rail":"honkai:_star_rail","honkai_star_rail":"honkai:_star_rail",
"arknights":"arknights","kancolle":"kantai_collection","kantai_collection":"kantai_collection",
"touhou":"touhou","hololive":"hololive","wuthering_waves":"wuthering_waves",
"azur_lane":"azur_lane","girls_und_panzer":"girls_und_panzer","princess_connect!":"princess_connect!"
}
def main():
    if not SRC.exists(): raise SystemExit(f"missing source: {SRC}")
    with SRC.open("r",encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))
    chars=[r for r in rows if (r.get("category_name") or "").lower()=="character"]
    if len(chars)!=35890: raise SystemExit(f"expected 35890 Character rows, got {len(chars)}")
    OUTDIR.mkdir(parents=True,exist_ok=True)
    result=[]; states=Counter(); quals=Counter()
    for r in chars:
        tag=r.get("canonical_tag") or ""
        m=FINAL.search(tag); q=m.group(1).lower() if m else ""; root=APPROVED.get(q,"")
        state="APPROVED_QUALIFIER_CANDIDATE" if root else ("UNKNOWN_QUALIFIER" if q else "UNQUALIFIED")
        states[state]+=1
        if q: quals[q]+=1
        result.append({"canonical_tag":tag,"final_qualifier":q,"candidate_home_copyright":root,"preflight_state":state})
    with OUT.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=result[0].keys(),lineterminator="\n"); w.writeheader(); w.writerows(result)
    unknown=[{"qualifier":q,"count":n} for q,n in quals.most_common() if q not in APPROVED]
    summary={"character_rows":len(chars),"state_counts":dict(states),"approved_root_count":len(APPROVED),
      "top_unknown_qualifiers":unknown[:100],"relation_data_used_as_authority":False,
      "accepted_source_modified":False,"production_modified":False}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
