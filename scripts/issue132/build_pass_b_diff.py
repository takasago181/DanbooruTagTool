#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

EXPECTED=31_003

def read_csv(path: Path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def json_list(value: str, field: str, ident: str) -> list[str]:
    try:
        obj=json.loads(value or "[]")
    except Exception as e:
        raise SystemExit(f"{ident}: invalid JSON in {field}: {e}")
    if not isinstance(obj,list) or any(not isinstance(x,str) for x in obj):
        raise SystemExit(f"{ident}: {field} must be JSON string array")
    if len(obj)!=len(set(obj)):
        raise SystemExit(f"{ident}: duplicate value in {field}")
    return obj

def pipe_set(value: str) -> set[str]:
    return {x.strip() for x in (value or "").split("|") if x.strip()}

def dump(values) -> str:
    return json.dumps(sorted(set(values)),ensure_ascii=False,separators=(",",":"))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pass-a",required=True)
    ap.add_argument("--current-audit",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--summary",required=True)
    args=ap.parse_args()

    pass_a=read_csv(Path(args.pass_a))
    current=read_csv(Path(args.current_audit))

    if len(pass_a)!=EXPECTED:
        raise SystemExit(f"Pass A must be complete: {len(pass_a)} != {EXPECTED}")
    if len(current)!=EXPECTED:
        raise SystemExit(f"current audit population mismatch: {len(current)} != {EXPECTED}")

    pa_by={r["identity_key"]:r for r in pass_a}
    cur_by={r["identity_key"]:r for r in current}
    if len(pa_by)!=EXPECTED or len(cur_by)!=EXPECTED:
        raise SystemExit("duplicate identity_key in Pass A/current audit")
    if pa_by.keys()!=cur_by.keys():
        missing=sorted(set(pa_by)-set(cur_by))[:20]
        extra=sorted(set(cur_by)-set(pa_by))[:20]
        raise SystemExit(f"identity set mismatch: pass_a_only={missing} current_only={extra}")

    output=[]
    flag_counts=Counter()
    missing_route_counts=Counter()
    missing_local_counts=Counter()
    missing_body_counts=Counter()
    missing_theme_counts=Counter()
    extra_current_route_counts=Counter()

    for pa in pass_a:
        ident=pa["identity_key"]
        cur=cur_by[ident]

        core=set()
        supporting=set()
        all_natural=set()
        for i in range(1,4):
            rid=(pa.get(f"route_{i}_id") or "").strip()
            strength=(pa.get(f"route_{i}_strength") or "").strip()
            if not rid:
                continue
            all_natural.add(rid)
            if strength=="CORE":
                core.add(rid)
            elif strength=="SUPPORTING":
                supporting.add(rid)
            else:
                raise SystemExit(f"{ident}: invalid route strength at route_{i}: {strength}")

        luna_local=set(json_list(pa.get("local_refinement_ids","[]"),"local_refinement_ids",ident))
        luna_body=set(json_list(pa.get("body_site_ids","[]"),"body_site_ids",ident))
        luna_theme=set(json_list(pa.get("theme_ids","[]"),"theme_ids",ident))

        current_routes=pipe_set(cur.get("current_routes",""))
        current_local=pipe_set(cur.get("local_paths",""))
        current_body=pipe_set(cur.get("body_sites",""))
        current_theme=pipe_set(cur.get("themes",""))

        missing_core=core-current_routes
        missing_supporting=supporting-current_routes
        current_not_reproduced=current_routes-all_natural
        missing_local=luna_local-current_local
        missing_body=luna_body-current_body
        missing_theme=luna_theme-current_theme

        flags=[]
        if not (missing_core or missing_supporting or missing_local or missing_body or missing_theme) \
                and pa.get("route_vocabulary_gap")!="YES" \
                and pa.get("discovery_mode") not in {"SEARCH_ORIENTED","SEMANTIC_UNRESOLVED"}:
            flags.append("COVERED")
        if missing_core:
            flags.append("MISSING_CORE_ROUTE")
        if missing_supporting:
            flags.append("MISSING_SUPPORTING_ROUTE")
        if current_not_reproduced:
            flags.append("CURRENT_ROUTE_NOT_REPRODUCED")
        if missing_local:
            flags.append("MISSING_LOCAL_REFINEMENT")
        if missing_body:
            flags.append("MISSING_BODY_FACET")
        if missing_theme:
            flags.append("MISSING_THEME_FACET")
        if pa.get("discovery_mode")=="SEARCH_ORIENTED":
            flags.append("SEARCH_ORIENTED")
        if pa.get("discovery_mode")=="SEMANTIC_UNRESOLVED":
            flags.append("SEMANTIC_UNRESOLVED")
        if pa.get("route_vocabulary_gap")=="YES":
            flags.append("ROUTE_VOCABULARY_GAP")

        flag_counts.update(flags)
        missing_route_counts.update(missing_core)
        missing_route_counts.update(missing_supporting)
        missing_local_counts.update(missing_local)
        missing_body_counts.update(missing_body)
        missing_theme_counts.update(missing_theme)
        extra_current_route_counts.update(current_not_reproduced)

        output.append({
            "identity_key":ident,
            "discovery_mode":pa.get("discovery_mode",""),
            "luna_core_routes":dump(core),
            "luna_supporting_routes":dump(supporting),
            "current_routes":dump(current_routes),
            "missing_core_routes":dump(missing_core),
            "missing_supporting_routes":dump(missing_supporting),
            "current_routes_not_reproduced":dump(current_not_reproduced),
            "luna_local_refinements":dump(luna_local),
            "current_local_refinements":dump(current_local),
            "missing_local_refinements":dump(missing_local),
            "luna_body_sites":dump(luna_body),
            "current_body_sites":dump(current_body),
            "missing_body_sites":dump(missing_body),
            "luna_themes":dump(luna_theme),
            "current_themes":dump(current_theme),
            "missing_themes":dump(missing_theme),
            "route_vocabulary_gap":pa.get("route_vocabulary_gap",""),
            "diff_flags":dump(flags),
            "sexual_intent":cur.get("sexual_intent",""),
            "is_general":cur.get("is_general",""),
            "is_special":cur.get("is_special",""),
            "machine_bucket":cur.get("bucket",""),
        })

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(output[0].keys()),lineterminator="\n")
        w.writeheader()
        w.writerows(output)

    summary={
        "schema_version":"issue132-pass-b-diff-v1",
        "population":len(output),
        "flag_counts":dict(sorted(flag_counts.items())),
        "missing_route_counts":dict(sorted(missing_route_counts.items())),
        "missing_local_refinement_counts":dict(sorted(missing_local_counts.items())),
        "missing_body_facet_counts":dict(sorted(missing_body_counts.items())),
        "missing_theme_facet_counts":dict(sorted(missing_theme_counts.items())),
        "current_route_not_reproduced_counts":dict(sorted(extra_current_route_counts.items())),
        "semantic_decisions_made":False,
        "note":"Pass B is deterministic comparison only. Product acceptance occurs in Pass C/D."
    }
    sp=Path(args.summary)
    sp.parent.mkdir(parents=True,exist_ok=True)
    sp.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
