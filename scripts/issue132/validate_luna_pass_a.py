#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROUTES = {
    "PEOPLE_COUNT","RELATION_ROLE","BODY_SITE","HAIR_FACE","CLOTHING_EXPOSURE",
    "TOOL_OBJECT","LIVING","NONHUMAN_TRANSFORM","ACTION_CONTACT","POSE_POSITION",
    "EXPRESSION_GAZE","FLUID_EXCRETION","COMPOSITION_CAMERA","SCENE_BACKGROUND",
    "LIGHT_TIME_WEATHER","COLOR_PATTERN_SHAPE","STYLE_PROCESSING","TEXT_SYMBOL","CONTENT_RATING"
}
STRENGTHS = {"CORE","SUPPORTING"}
MODES = {"BROWSE_WORTHY","MIXED","SEARCH_ORIENTED","SEMANTIC_UNRESOLVED"}
DEPTHS = {"CHECKED","RESEARCHED"}
BODY = {"MALE_GENITAL","BREAST_NIPPLE","FEMALE_GENITAL","MOUTH_ORAL","BUTTOCK_ANAL","URETHRA"}
THEMES = {"BDSM_RESTRAINT","INJURY_R18G","REPRO_PREGNANCY_LACTATION"}

FIELDS = [
    "review_seq","identity_key","manual_seen","semantic_summary_ja","discovery_mode",
    "route_1_id","route_1_strength","route_1_reason_ja",
    "route_2_id","route_2_strength","route_2_reason_ja",
    "route_3_id","route_3_strength","route_3_reason_ja",
    "body_site_ids","theme_ids",
    "route_vocabulary_gap","route_vocabulary_gap_note",
    "review_depth","evidence_urls","uncertainty_note"
]

def read_csv(path: Path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def parse_json_list(value: str, field: str, identity: str) -> list[str]:
    try:
        obj=json.loads(value or "[]")
    except Exception as e:
        raise ValueError(f"{identity}: {field} invalid JSON: {e}")
    if not isinstance(obj,list) or any(not isinstance(x,str) for x in obj):
        raise ValueError(f"{identity}: {field} must be JSON string array")
    if len(obj)!=len(set(obj)):
        raise ValueError(f"{identity}: {field} contains duplicates")
    return obj

def validate_row(row, expected_seq):
    ident=row["identity_key"]
    errs=[]
    def need(cond,msg):
        if not cond: errs.append(f"{ident}: {msg}")

    try:
        seq=int(row["review_seq"])
        need(seq==expected_seq, f"review_seq {seq} != neutral {expected_seq}")
    except Exception:
        errs.append(f"{ident}: invalid review_seq")

    need(row["manual_seen"]=="YES","manual_seen must be YES")
    need(bool(row["semantic_summary_ja"].strip()),"semantic_summary_ja blank")
    need(row["discovery_mode"] in MODES,"invalid discovery_mode")
    need(row["review_depth"] in DEPTHS,"invalid review_depth")
    need(row["route_vocabulary_gap"] in {"YES","NO"},"route_vocabulary_gap must be YES/NO")
    if row["route_vocabulary_gap"]=="YES":
        need(bool(row["route_vocabulary_gap_note"].strip()),"vocabulary gap requires note")
    else:
        need(not row["route_vocabulary_gap_note"].strip(),"vocabulary gap NO requires blank note")

    routes=[]
    for i in range(1,4):
        rid=row[f"route_{i}_id"].strip()
        strength=row[f"route_{i}_strength"].strip()
        reason=row[f"route_{i}_reason_ja"].strip()
        if rid:
            need(rid in ROUTES,f"route_{i}_id invalid: {rid}")
            need(strength in STRENGTHS,f"route_{i}_strength invalid")
            need(bool(reason),f"route_{i}_reason_ja blank")
            routes.append(rid)
        else:
            need(not strength,f"route_{i}_strength set without route")
            need(not reason,f"route_{i}_reason_ja set without route")
    need(len(routes)==len(set(routes)),"duplicate route IDs")

    try:
        body=parse_json_list(row["body_site_ids"],"body_site_ids",ident)
        need(set(body)<=BODY,"invalid body_site_ids")
    except ValueError as e:
        errs.append(str(e)); body=[]
    try:
        themes=parse_json_list(row["theme_ids"],"theme_ids",ident)
        need(set(themes)<=THEMES,"invalid theme_ids")
    except ValueError as e:
        errs.append(str(e)); themes=[]
    try:
        evidence=parse_json_list(row["evidence_urls"],"evidence_urls",ident)
    except ValueError as e:
        errs.append(str(e)); evidence=[]

    if row["review_depth"]=="RESEARCHED":
        need(bool(evidence),"RESEARCHED requires at least one evidence URL")
    if row["discovery_mode"]=="SEARCH_ORIENTED":
        need(not routes and not body and not themes,
             "SEARCH_ORIENTED must not carry routes/body/theme; use MIXED if both apply")
    if row["discovery_mode"]=="SEMANTIC_UNRESOLVED":
        need(not routes and not body and not themes,
             "SEMANTIC_UNRESOLVED must not carry routes/body/theme")
        need(row["review_depth"]=="RESEARCHED","SEMANTIC_UNRESOLVED must be RESEARCHED")
        need(bool(row["uncertainty_note"].strip()),"SEMANTIC_UNRESOLVED requires uncertainty_note")
    if row["discovery_mode"] in {"BROWSE_WORTHY","MIXED"}:
        need(bool(routes or body or themes or row["route_vocabulary_gap"]=="YES"),
             "browse-capable mode requires route/facet or vocabulary gap")

    return errs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,help="luna neutral input CSV")
    ap.add_argument("--ledger",required=True,help="Pass A output ledger CSV")
    ap.add_argument("--require-complete",action="store_true")
    ap.add_argument("--summary",default="")
    args=ap.parse_args()

    neutral=read_csv(Path(args.input))
    ledger=read_csv(Path(args.ledger))
    if list(ledger[0].keys()) != FIELDS if ledger else False:
        raise SystemExit("ledger header mismatch")

    neutral_by={r["identity_key"]:int(r["review_seq"]) for r in neutral}
    if len(neutral_by)!=31003 or len(neutral)!=31003:
        raise SystemExit(f"neutral input count mismatch: rows={len(neutral)} unique={len(neutral_by)}")

    seen=set()
    errors=[]
    last_seq=0
    for row in ledger:
        ident=row["identity_key"]
        if ident not in neutral_by:
            errors.append(f"{ident}: not in neutral input")
            continue
        if ident in seen:
            errors.append(f"{ident}: duplicate ledger row")
            continue
        seen.add(ident)
        seq=int(row["review_seq"]) if row["review_seq"].isdigit() else -1
        if seq <= last_seq:
            errors.append(f"{ident}: ledger order is not strictly increasing")
        last_seq=seq
        errors.extend(validate_row(row,neutral_by[ident]))

    expected_prefix=[r["identity_key"] for r in neutral[:len(ledger)]]
    actual=[r["identity_key"] for r in ledger]
    if actual != expected_prefix:
        errors.append("ledger must be an exact prefix of neutral review order; no skipping/reordering")

    if args.require_complete and len(ledger)!=len(neutral):
        errors.append(f"incomplete ledger: {len(ledger)} != {len(neutral)}")

    stats={
        "schema_version":"issue132-pass-a-ledger-validation-v1",
        "neutral_count":len(neutral),
        "reviewed_count":len(ledger),
        "remaining_count":len(neutral)-len(ledger),
        "complete":len(ledger)==len(neutral),
        "error_count":len(errors),
        "discovery_mode":dict(Counter(r["discovery_mode"] for r in ledger)),
        "review_depth":dict(Counter(r["review_depth"] for r in ledger)),
        "route_vocabulary_gap":dict(Counter(r["route_vocabulary_gap"] for r in ledger)),
        "route_strength_counts":dict(Counter(
            (r[f"route_{i}_id"],r[f"route_{i}_strength"])
            for r in ledger for i in range(1,4) if r[f"route_{i}_id"]
        )),
        "body_site_counts":dict(Counter(
            x for r in ledger for x in parse_json_list(r["body_site_ids"],"body_site_ids",r["identity_key"])
        )),
        "theme_counts":dict(Counter(
            x for r in ledger for x in parse_json_list(r["theme_ids"],"theme_ids",r["identity_key"])
        ))
    }
    if args.summary:
        Path(args.summary).write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(stats,ensure_ascii=False,indent=2))
    if errors:
        for e in errors[:100]:
            print("ERROR:",e)
        if len(errors)>100:
            print(f"... {len(errors)-100} more errors")
        raise SystemExit(1)

if __name__=="__main__":
    main()
