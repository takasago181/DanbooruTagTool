#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

COUNT=31_003

PASS_A_FIELDS=[
    "review_seq","identity_key","manual_seen","semantic_summary_ja","discovery_mode",
    "route_1_id","route_1_strength","route_1_reason_ja",
    "route_2_id","route_2_strength","route_2_reason_ja",
    "route_3_id","route_3_strength","route_3_reason_ja",
    "local_refinement_ids","body_site_ids","theme_ids",
    "route_vocabulary_gap","route_vocabulary_gap_note",
    "review_depth","evidence_urls","uncertainty_note"
]

CURRENT_FIELDS=[
    "identity_key","bucket","sexual_intent","review_status","is_general","is_special",
    "current_routes","general_paths","local_paths","special_ids","special_kinds",
    "generation_signals","body_sites","themes","review_signals"
]

def pass_a_row(i: int):
    ident=f"synthetic_identity_{i:05d}"
    return {
        "review_seq":str(i),"identity_key":ident,"manual_seen":"YES",
        "semantic_summary_ja":"synthetic","discovery_mode":"BROWSE_WORTHY",
        "route_1_id":"ACTION_CONTACT","route_1_strength":"CORE","route_1_reason_ja":"synthetic",
        "route_2_id":"","route_2_strength":"","route_2_reason_ja":"",
        "route_3_id":"","route_3_strength":"","route_3_reason_ja":"",
        "local_refinement_ids":"[]","body_site_ids":"[]","theme_ids":"[]",
        "route_vocabulary_gap":"NO","route_vocabulary_gap_note":"",
        "review_depth":"CHECKED","evidence_urls":"[]","uncertainty_note":""
    }

def current_row(i: int):
    ident=f"synthetic_identity_{i:05d}"
    return {
        "identity_key":ident,"bucket":"OK","sexual_intent":"NON_SEXUAL","review_status":"AUTO_HIGH_CONF",
        "is_general":"YES","is_special":"NO","current_routes":"ACTION_CONTACT",
        "general_paths":"ACTION_CONTACT/INTERACTION","local_paths":"",
        "special_ids":"","special_kinds":"","generation_signals":"",
        "body_sites":"","themes":"","review_signals":""
    }

def write_csv(path: Path, fields, rows):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def main():
    root=Path(__file__).resolve().parents[2]
    builder=root/"scripts/issue132/build_pass_b_diff.py"
    with tempfile.TemporaryDirectory(prefix="issue132-pass-b-") as td:
        t=Path(td)
        pa=t/"pass_a.csv"; cur=t/"current.csv"; out=t/"diff.csv"; summary=t/"summary.json"

        pa_rows=[pass_a_row(i) for i in range(1,COUNT+1)]
        cur_rows=[current_row(i) for i in range(1,COUNT+1)]

        # 1: missing CORE route.
        pa_rows[0].update({
            "route_2_id":"POSE_POSITION","route_2_strength":"CORE","route_2_reason_ja":"second natural axis"
        })

        # 2: search-oriented; current route is not independently reproduced.
        pa_rows[1].update({
            "discovery_mode":"SEARCH_ORIENTED",
            "route_1_id":"","route_1_strength":"","route_1_reason_ja":""
        })

        # 3: missing local refinement.
        pa_rows[2]["local_refinement_ids"]=json.dumps(["ACTION_CONTACT/INTIMATE"])

        # 4: missing body + theme refinement.
        pa_rows[3]["body_site_ids"]=json.dumps(["BREAST_NIPPLE"])
        pa_rows[3]["theme_ids"]=json.dumps(["BDSM_RESTRAINT"])

        # 5: true/possible route vocabulary gap flag.
        pa_rows[4]["route_vocabulary_gap"]="YES"
        pa_rows[4]["route_vocabulary_gap_note"]="synthetic gap"

        # 6: missing SUPPORTING route.
        pa_rows[5].update({
            "route_2_id":"TOOL_OBJECT","route_2_strength":"SUPPORTING","route_2_reason_ja":"secondary intent"
        })

        write_csv(pa,PASS_A_FIELDS,pa_rows)
        write_csv(cur,CURRENT_FIELDS,cur_rows)

        r=subprocess.run(
            [sys.executable,str(builder),"--pass-a",str(pa),"--current-audit",str(cur),
             "--out",str(out),"--summary",str(summary)],
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8"
        )
        if r.returncode!=0:
            print(r.stdout); raise SystemExit("Pass B builder failed")

        s=json.loads(summary.read_text(encoding="utf-8"))
        expected={
            "MISSING_CORE_ROUTE":1,
            "MISSING_SUPPORTING_ROUTE":1,
            "CURRENT_ROUTE_NOT_REPRODUCED":1,
            "MISSING_LOCAL_REFINEMENT":1,
            "MISSING_BODY_FACET":1,
            "MISSING_THEME_FACET":1,
            "SEARCH_ORIENTED":1,
            "ROUTE_VOCABULARY_GAP":1,
            "COVERED":COUNT-6,
        }
        for k,v in expected.items():
            actual=s["flag_counts"].get(k,0)
            if actual!=v:
                print(json.dumps(s,indent=2))
                raise SystemExit(f"{k}: {actual} != {v}")
        if s["semantic_decisions_made"] is not False:
            raise SystemExit("Pass B must not make semantic decisions")

        with out.open("r",encoding="utf-8",newline="") as f:
            rows=list(csv.DictReader(f))
        if len(rows)!=COUNT:
            raise SystemExit("Pass B output population drift")

        by={r["identity_key"]:r for r in rows}
        if json.loads(by["synthetic_identity_00001"]["missing_core_routes"])!=["POSE_POSITION"]:
            raise SystemExit("missing core route mismatch")
        if json.loads(by["synthetic_identity_00003"]["missing_local_refinements"])!=["ACTION_CONTACT/INTIMATE"]:
            raise SystemExit("missing local mismatch")
        if json.loads(by["synthetic_identity_00004"]["missing_body_sites"])!=["BREAST_NIPPLE"]:
            raise SystemExit("missing body mismatch")
        if json.loads(by["synthetic_identity_00004"]["missing_themes"])!=["BDSM_RESTRAINT"]:
            raise SystemExit("missing theme mismatch")

    print("PASS Issue132 Pass B deterministic diff smoke")

if __name__=="__main__":
    main()
