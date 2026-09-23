#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
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
ROOT = Path(__file__).resolve().parents[2]
LOCAL_PARENT = {
    "ACTION_CONTACT/INTERACTION":"ACTION_CONTACT",
    "ACTION_CONTACT/INTIMATE":"ACTION_CONTACT",
    "ACTION_CONTACT/OBJECT_USE":"ACTION_CONTACT",
    "CLOTHING/ACCESSORY":"CLOTHING_EXPOSURE",
    "CLOTHING/COSTUME":"CLOTHING_EXPOSURE",
    "CLOTHING/EVERYDAY":"CLOTHING_EXPOSURE",
    "CLOTHING/UNIFORM":"CLOTHING_EXPOSURE",
    "CLOTHING_STATE_EXPOSURE/":"CLOTHING_EXPOSURE",
    "LIVING_NATURE/CREATURE":"LIVING",
    "LIVING_NATURE/PLANT":"LIVING",
    "OBJECT_PROP/DAILY":"TOOL_OBJECT",
    "OBJECT_PROP/FOOD":"TOOL_OBJECT",
    "OBJECT_PROP/VEHICLE":"TOOL_OBJECT",
    "OBJECT_PROP/WEAPON":"TOOL_OBJECT",
    "TEXT_SYMBOL/LAYOUT":"TEXT_SYMBOL",
    "TEXT_SYMBOL/SYMBOL":"TEXT_SYMBOL",
    "TEXT_SYMBOL/TEXT":"TEXT_SYMBOL",
    "EXPRESSION_EMOTION/":"EXPRESSION_GAZE",
    "GAZE_ORIENTATION/":"EXPRESSION_GAZE",
}

FIELDS = [
    "review_seq","identity_key","manual_seen","semantic_summary_ja","discovery_mode",
    "route_1_id","route_1_strength","route_1_reason_ja",
    "route_2_id","route_2_strength","route_2_reason_ja",
    "route_3_id","route_3_strength","route_3_reason_ja",
    "local_refinement_ids","body_site_ids","theme_ids",
    "route_vocabulary_gap","route_vocabulary_gap_note",
    "review_depth","evidence_urls","uncertainty_note"
]

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def identity_order_sha(rows) -> str:
    text="".join(r["identity_key"]+"\n" for r in rows).encode("utf-8")
    return hashlib.sha256(text).hexdigest()

def verify_contract_manifest(path: Path, neutral_path: Path, neutral_rows):
    m=json.loads(path.read_text(encoding="utf-8"))
    errs=[]
    if m.get("schema_version")!="issue132-pass-a-contract-v1":
        errs.append("contract manifest schema mismatch")
    if m.get("population")!=31_003:
        errs.append("contract manifest population mismatch")
    neutral=m.get("neutral",{})
    if neutral.get("identity_count")!=31_003:
        errs.append("contract manifest neutral identity count mismatch")
    if neutral.get("output_sha256")!=sha256_file(neutral_path):
        errs.append("neutral input SHA drift from contract")
    if neutral.get("identity_order_sha256")!=identity_order_sha(neutral_rows):
        errs.append("neutral identity order SHA drift from contract")

    for rel,expected in m.get("contract_files_sha256",{}).items():
        p=ROOT/rel
        if not p.is_file():
            errs.append(f"missing frozen contract file: {rel}")
        elif sha256_file(p)!=expected:
            errs.append(f"frozen contract file changed: {rel}")

    if m.get("ledger_fields")!=FIELDS:
        errs.append("ledger field contract drift")
    if m.get("route_ids")!=sorted(ROUTES):
        errs.append("route vocabulary drift")
    if m.get("local_refinement_parent")!=dict(sorted(LOCAL_PARENT.items())):
        errs.append("local refinement vocabulary drift")
    if m.get("body_site_ids")!=sorted(BODY):
        errs.append("body-site vocabulary drift")
    if m.get("theme_ids")!=sorted(THEMES):
        errs.append("theme vocabulary drift")
    if m.get("allowed_discovery_modes")!=sorted(MODES):
        errs.append("discovery mode vocabulary drift")
    if m.get("allowed_route_strengths")!=sorted(STRENGTHS):
        errs.append("route strength vocabulary drift")
    if m.get("allowed_review_depths")!=sorted(DEPTHS):
        errs.append("review depth vocabulary drift")
    return m, errs

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
        local=parse_json_list(row["local_refinement_ids"],"local_refinement_ids",ident)
        need(set(local)<=set(LOCAL_PARENT),"invalid local_refinement_ids")
        selected_routes=set(routes)
        for local_id in local:
            parent=LOCAL_PARENT.get(local_id)
            need(parent in selected_routes,
                 f"local refinement {local_id} requires selected parent route {parent}")
        by_parent=Counter(LOCAL_PARENT.get(local_id) for local_id in local)
        need(all(count<=1 for count in by_parent.values()),
             "normally at most one local refinement per selected parent route")
    except ValueError as e:
        errs.append(str(e)); local=[]

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
        need(not routes and not local and not body and not themes,
             "SEARCH_ORIENTED must not carry routes/local/body/theme; use MIXED if both apply")
        need(row["route_vocabulary_gap"]=="NO",
             "SEARCH_ORIENTED cannot also claim a missing browse vocabulary; use MIXED/BROWSE_WORTHY")
    if row["discovery_mode"]=="SEMANTIC_UNRESOLVED":
        need(not routes and not local and not body and not themes,
             "SEMANTIC_UNRESOLVED must not carry routes/local/body/theme")
        need(row["route_vocabulary_gap"]=="NO",
             "SEMANTIC_UNRESOLVED cannot establish a route vocabulary gap")
        need(row["review_depth"]=="RESEARCHED","SEMANTIC_UNRESOLVED must be RESEARCHED")
        need(bool(row["uncertainty_note"].strip()),"SEMANTIC_UNRESOLVED requires uncertainty_note")
    if row["discovery_mode"] in {"BROWSE_WORTHY","MIXED"}:
        need(bool(routes or body or themes or row["route_vocabulary_gap"]=="YES"),
             "browse-capable mode requires route/facet or vocabulary gap")
        if routes and row["route_vocabulary_gap"]=="NO":
            need(any(row[f"route_{i}_strength"]=="CORE" for i in range(1,4) if row[f"route_{i}_id"]),
                 "browse-capable mode with existing routes requires at least one CORE route")

    return errs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,help="luna neutral input CSV")
    ap.add_argument("--ledger",required=True,help="Pass A output ledger CSV")
    ap.add_argument("--require-complete",action="store_true")
    ap.add_argument("--summary",default="")
    ap.add_argument("--contract-manifest",default="")
    args=ap.parse_args()

    neutral_path=Path(args.input)
    ledger_path=Path(args.ledger)
    neutral=read_csv(neutral_path)
    ledger=read_csv(ledger_path)

    contract_manifest = None
    contract_errors = []
    if args.contract_manifest:
        contract_manifest, contract_errors = verify_contract_manifest(
            Path(args.contract_manifest), neutral_path, neutral
        )

    # csv.DictReader loses the header when materialized through read_csv on an
    # empty ledger, so validate the declared schema separately.
    with ledger_path.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        header=reader.fieldnames or []
    if header != FIELDS:
        raise SystemExit("ledger header mismatch")

    neutral_by={r["identity_key"]:int(r["review_seq"]) for r in neutral}
    if len(neutral_by)!=31003 or len(neutral)!=31003:
        raise SystemExit(f"neutral input count mismatch: rows={len(neutral)} unique={len(neutral_by)}")

    seen=set()
    errors=list(contract_errors)
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
        "schema_version":"issue132-pass-a-ledger-validation-v2",
        "contract_manifest_sha256": sha256_file(Path(args.contract_manifest)) if args.contract_manifest else "",
        "contract_created_from_commit": contract_manifest.get("created_from_commit","") if contract_manifest else "",
        "neutral_input_sha256": sha256_file(neutral_path),
        "neutral_identity_order_sha256": identity_order_sha(neutral),
        "ledger_sha256": sha256_file(ledger_path),
        "neutral_count":len(neutral),
        "reviewed_count":len(ledger),
        "remaining_count":len(neutral)-len(ledger),
        "complete":len(ledger)==len(neutral),
        "error_count":len(errors),
        "discovery_mode":dict(Counter(r["discovery_mode"] for r in ledger)),
        "review_depth":dict(Counter(r["review_depth"] for r in ledger)),
        "route_vocabulary_gap":dict(Counter(r["route_vocabulary_gap"] for r in ledger)),
        "route_strength_counts":dict(Counter(
            f"{r[f'route_{i}_id']}|{r[f'route_{i}_strength']}"
            for r in ledger for i in range(1,4) if r[f"route_{i}_id"]
        )),
        "local_refinement_counts":dict(Counter(
            x for r in ledger for x in parse_json_list(r["local_refinement_ids"],"local_refinement_ids",r["identity_key"])
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
