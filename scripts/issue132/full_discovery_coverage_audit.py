#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

GENERAL_ROUTE = {
    "PERSON_COUNT":"PEOPLE_COUNT",
    "BODY_PART":"BODY_SITE",
    "HAIR_FACE":"HAIR_FACE",
    "EXPRESSION_EMOTION":"EXPRESSION_GAZE",
    "GAZE_ORIENTATION":"EXPRESSION_GAZE",
    "POSE_MOVEMENT":"POSE_POSITION",
    "COMPOSITION_CAMERA":"COMPOSITION_CAMERA",
    "CLOTHING":"CLOTHING_EXPOSURE",
    "CLOTHING_STATE_EXPOSURE":"CLOTHING_EXPOSURE",
    "ACTION_CONTACT":"ACTION_CONTACT",
    "OBJECT_PROP":"TOOL_OBJECT",
    "LIVING_NATURE":"LIVING",
    "PLACE_BACKGROUND":"SCENE_BACKGROUND",
    "LIGHT_TIME_WEATHER":"LIGHT_TIME_WEATHER",
    "COLOR_APPEARANCE":"COLOR_PATTERN_SHAPE",
    "STYLE_QUALITY_META":"STYLE_PROCESSING",
    "TEXT_SYMBOL":"TEXT_SYMBOL",
}
SPECIAL_ROUTE = {
    "ACTION_CONTACT":"ACTION_CONTACT",
    "CLOTHING_EXPOSURE":"CLOTHING_EXPOSURE",
    "TOOL_OBJECT":"TOOL_OBJECT",
    "BODY_STATE":"BODY_SITE",
    "FLUID_EXCRETION":"FLUID_EXCRETION",
    "PERSON_RELATION":"RELATION_ROLE",
    "NONHUMAN_TRANSFORMATION":"NONHUMAN_TRANSFORM",
    "META_EXPRESSION":"CONTENT_RATING",
}
TYPE_MAP = {
    "BODY_ANATOMY":"BODY_STATE",
    "NUDITY_CLOTHING_EXPOSURE":"CLOTHING_EXPOSURE",
    "POSE_POSITION_COMPOSITION":"POSE_SCENE",
    "SEXUAL_ACTIVITY_STIMULATION":"ACTION_CONTACT",
    "CONTACT_INSERTION_BODY_SITE":"ACTION_CONTACT",
    "TOOLS_TOYS_MACHINES":"TOOL_OBJECT",
    "FLUID_EXCRETION_SOILING":"FLUID_EXCRETION",
    "NONHUMAN_TENTACLE_TRANSFORMATION":"NONHUMAN_TRANSFORMATION",
    "PERSON_RELATION_ROLE":"PERSON_RELATION",
    "SITUATION_SCENE":"POSE_SCENE",
    "META_RATING":"META_EXPRESSION",
}
BDSM_FALLBACK = {
    "":"ACTION_CONTACT","BONDAGE_STATE":"ACTION_CONTACT","BONDAGE_POSITION":"POSE_SCENE",
    "RESTRAINT_DEVICE":"TOOL_OBJECT","GAG_MOUTH_RESTRAINT":"TOOL_OBJECT",
    "CHASTITY_CONTROL":"TOOL_OBJECT","PAIN_TORTURE":"ACTION_CONTACT",
    "DOMINATION_SUBMISSION":"PERSON_RELATION","FORCE_NONCONSENT":"ACTION_CONTACT",
}
BODY_FACET = {
    ("BODY_ANATOMY","BREAST_NIPPLE"):"BREAST_NIPPLE",
    ("BODY_ANATOMY","FEMALE_GENITAL"):"FEMALE_GENITAL",
    ("BODY_ANATOMY","MALE_GENITAL"):"MALE_GENITAL",
    ("BODY_ANATOMY","BUTTOCK_ANUS"):"BUTTOCK_ANAL",
    ("CONTACT_INSERTION_BODY_SITE","ANAL_SITE"):"BUTTOCK_ANAL",
    ("CONTACT_INSERTION_BODY_SITE","FEMALE_GENITAL_SITE"):"FEMALE_GENITAL",
    ("CONTACT_INSERTION_BODY_SITE","URETHRAL_SITE"):"URETHRA",
    ("SEXUAL_ACTIVITY_STIMULATION","ORAL_ACTIVITY"):"MOUTH_ORAL",
    ("BONDAGE_BDSM_DOMINATION","GAG_MOUTH_RESTRAINT"):"MOUTH_ORAL",
}
THEME_FACET = {
    "BONDAGE_BDSM_DOMINATION":"BDSM_RESTRAINT",
    "INJURY_R18G":"INJURY_R18G",
    "REPRODUCTION_PREGNANCY_LACTATION":"REPRO_PREGNANCY_LACTATION",
}
KIND_LABEL_TO_ID = {
    "行為・接触":"ACTION_CONTACT","衣服・露出":"CLOTHING_EXPOSURE","道具・物":"TOOL_OBJECT",
    "身体・状態":"BODY_STATE","体液・排泄":"FLUID_EXCRETION","ポーズ・構図・場面":"POSE_SCENE",
    "人物・関係":"PERSON_RELATION","異形・変形":"NONHUMAN_TRANSFORMATION","表現・メタ":"META_EXPRESSION",
}
BODY_LABEL_TO_ID = {
    "男性器":"MALE_GENITAL","乳房・乳首":"BREAST_NIPPLE","女性器":"FEMALE_GENITAL",
    "口・口内":"MOUTH_ORAL","尻・肛門":"BUTTOCK_ANAL","尿道":"URETHRA",
}

COLOR_PREFIXES = {
    "black","blue","brown","green","grey","gray","orange","pink","purple","red","white","yellow",
    "aqua","gold","silver","blonde","multicolored","rainbow"
}
BODY_TOKENS = {
    "arm","arms","armpit","armpits","ass","back","belly","breast","breasts","butt","buttocks","cheek","cheeks",
    "chest","crotch","ear","ears","eye","eyes","face","finger","fingers","foot","feet","genital","genitals",
    "hair","hand","hands","head","leg","legs","mouth","navel","neck","nipple","nipples","penis","pussy","shoulder",
    "shoulders","thigh","thighs","tongue","torso","vagina","wrist","wrists","anus"
}
FIXTURE_TOKENS = {"door","window","counter","bedside","fence","gate","wall","stairs","staircase","balcony","railing"}
PLACEMENT_TOKENS = {"around","between","under","over","off","open","lift","pull","aside","down"}

def norm(value: str) -> str:
    return "_".join(value.strip().lower().replace("_"," ").split())

def rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def split_pipe(value: str):
    return [x.strip() for x in (value or "").split("|") if x.strip()]

def parse_secondary(value: str):
    value=(value or "").strip()
    if not value: return []
    try:
        obj=json.loads(value)
        if isinstance(obj,list): return [str(x) for x in obj]
    except Exception:
        pass
    return split_pipe(value)

def general_route_for_path(path: str):
    genre=(path or "").split("/",1)[0]
    return GENERAL_ROUTE.get(genre)

def load_issue56_paths(root: Path):
    cs=(root/"src/DanbooruTagTool.Data/Issue56Inputs.cs").read_text(encoding="utf-8")
    files=re.findall(r'\["([^"]+\.csv)"\]\s*=\s*"[0-9a-f]+"', cs)
    result={}
    for rel in files:
        for r in rows(root/rel):
            sid=int(r["special_id"])
            status=r.get("classification_status","")
            primary=r.get("primary_genre_id","").strip()
            sub=r.get("primary_subgenre_id","").strip()
            paths=[]
            if primary:
                paths.append((primary,sub))
            for sec in split_pipe(r.get("secondary_paths","")):
                if ">" in sec:
                    g,s=sec.split(">",1)
                else:
                    g,s=sec,""
                paths.append((g.strip(),s.strip()))
            if not primary and status in {"REVIEW_REQUIRED","AMBIGUOUS"}:
                paths=[]
            if sid in result:
                raise RuntimeError(f"duplicate #56 special_id {sid}")
            result[sid]=paths
    if len(result)!=2788:
        raise RuntimeError(f"#56 mapping count drift: {len(result)} != 2788")
    return result

def derive_special_v2(root: Path, production_ids: set[int]):
    old=load_issue56_paths(root)
    state={}
    for sid, paths in old.items():
        primary=paths[0] if paths else None
        kind=None
        if primary:
            g,s=primary
            if g in TYPE_MAP:
                kind=TYPE_MAP[g]
            elif g=="BONDAGE_BDSM_DOMINATION":
                kind=BDSM_FALLBACK.get(s,"ACTION_CONTACT")
            elif g=="REPRODUCTION_PREGNANCY_LACTATION":
                sec={TYPE_MAP.get(pg) for pg,_ in paths[1:]}
                kind=next((x for x in ["CLOTHING_EXPOSURE","ACTION_CONTACT","BODY_STATE"] if x in sec),"BODY_STATE")
            elif g=="INJURY_R18G":
                sec={TYPE_MAP.get(pg) for pg,_ in paths[1:]}
                kind=next((x for x in ["ACTION_CONTACT","FLUID_EXCRETION","PERSON_RELATION","BODY_STATE"] if x in sec),"BODY_STATE")
        body={BODY_FACET[p] for p in paths if p in BODY_FACET}
        themes={THEME_FACET[g] for g,_ in paths if g in THEME_FACET}
        state[sid]={"kind":kind,"body":body,"themes":themes,"status":"AUTO_CANDIDATE"}

    for r in rows(root/"src/DanbooruTagTool.Data/Issue76Data/issue76_chastity_control_patch_v0_4.csv"):
        sid=int(r["special_id"])
        if sid not in state: continue
        state[sid]={"kind":r["resolved_kind_id"] or None,
                    "body":set(split_pipe(r["resolved_body_site_id"])),
                    "themes":set(split_pipe(r["resolved_theme_id"])),
                    "status":"AUTO_CANDIDATE"}

    for r in rows(root/"src/DanbooruTagTool.Data/Issue76Data/issue76_v1_unresolved_audit_v0_5.csv"):
        sid=int(r["special_id"])
        if sid not in state: continue
        smap={"BROWSE_RESOLVED":"HUMAN_RESOLVED","REFERENCE_ONLY_NO_DIRECT_BROWSE":"REFERENCE_ONLY",
              "DEFER_PRODUCT_FIT_REVIEW":"DEFER_REVIEW","OUT_OF_SCOPE_NO_BROWSE":"OUT_OF_SCOPE"}
        state[sid]={"kind":r["v2_kind_id"] or None,"body":set(split_pipe(r["v2_body_sites"])),
                    "themes":set(split_pipe(r["v2_themes"])),"status":smap[r["v2_resolution"]]}

    for r in rows(root/"src/DanbooruTagTool.Data/Issue76Data/issue76_practical_generation_patch_v0_6.csv"):
        sid=int(r["special_id"])
        if sid not in state: continue
        if r["dimension"]=="kind":
            state[sid]["kind"]=KIND_LABEL_TO_ID.get(r["after"].strip()) if r["after"].strip() else None
        elif r["dimension"]=="body_site":
            vals=set()
            for label in split_pipe(r["after"]):
                if label not in BODY_LABEL_TO_ID: raise RuntimeError(f"unknown body label {label}")
                vals.add(BODY_LABEL_TO_ID[label])
            state[sid]["body"]=vals
        else:
            raise RuntimeError(f"unknown issue76 dimension {r['dimension']}")

    for rel in ["docs/issue96/special_expansion_promotion_proposal_v1.csv","docs/issue107/promotion_metadata_v1.csv"]:
        for r in rows(root/rel):
            sid=int(r["proposed_special_id"])
            state[sid]={"kind":r["kind_id"] or None,"body":set(split_pipe(r["body_site_ids"])),
                        "themes":set(split_pipe(r["theme_ids"])),"status":"HUMAN_RESOLVED"}

    return {sid:v for sid,v in state.items() if sid in production_ids}

def parse_sources(value: str):
    value=(value or "").strip()
    if not value: return []
    for parser in (json.loads, ast.literal_eval):
        try:
            obj=parser(value)
            if isinstance(obj,list): return [norm(str(x)) for x in obj]
        except Exception:
            pass
    parts=re.split(r"[|;]", value)
    return [norm(x.strip(" []'\"")) for x in parts if x.strip(" []'\"")]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", required=True)
    args=ap.parse_args()
    root=Path(args.root).resolve()
    out=Path(args.out); out.mkdir(parents=True, exist_ok=True)

    general_rows=rows(root/"docs/issue64/production_candidate/effective_sidecar.csv")
    if len(general_rows)!=30629: raise RuntimeError(f"General count drift {len(general_rows)}")

    intent_rows=rows(root/"docs/issue118/production_candidate/sexual_intent_v2.csv")
    if len(intent_rows)!=31003: raise RuntimeError(f"identity count drift {len(intent_rows)}")
    intents={r["identity_key"]:r for r in intent_rows}
    if len(intents)!=31003: raise RuntimeError("duplicate identity_key")

    profile=rows(root/"data/generation/special2788_generation_profile.csv")
    if len(profile)!=3059: raise RuntimeError(f"production Special profile drift {len(profile)}")
    production_ids={int(r["SpecialID"]) for r in profile}
    special_v2=derive_special_v2(root, production_ids)
    if len(special_v2)!=3059: raise RuntimeError(f"special v2 production count drift {len(special_v2)}")

    # Build source-surface -> identity lookup from #118 authority.
    source_index=defaultdict(set)
    for k,r in intents.items():
        source_index[norm(k)].add(k)
        for s in parse_sources(r.get("source_identities","")):
            source_index[s].add(k)

    identities={k:{
        "identity_key":k,
        "intent":r.get("sexual_intent",""),
        "review_status":r.get("review_status",""),
        "general":False,"special":False,
        "general_statuses":set(),"general_paths":set(),"current_routes":set(),
        "special_ids":[],"special_kinds":set(),"body_sites":set(),"themes":set(),
        "authority_expected_routes":set(),"review_signals":set(),
        "mapping_notes":set(),
    } for k,r in intents.items()}

    # General authority/current projection.
    for r in general_rows:
        key=norm(r["canonical"])
        if key not in identities:
            raise RuntimeError(f"General identity missing from #118: {r['canonical']}")
        d=identities[key]; d["general"]=True
        status=r["classification_status"]; d["general_statuses"].add(status)
        if status=="PROPOSED":
            paths=[r["primary_path"]]+parse_secondary(r["secondary_paths"])
            for p in paths:
                if not p: continue
                d["general_paths"].add(p)
                route=general_route_for_path(p)
                if route: d["current_routes"].add(route)
                else: d["review_signals"].add("GENERAL_PATH_NO_UNIFIED_ROUTE:"+p)
        elif status!="UNRESOLVED":
            d["review_signals"].add("UNKNOWN_GENERAL_STATUS:"+status)

    profile_by_id={int(r["SpecialID"]):r for r in profile}

    # Map special backing surfaces to runtime identity.
    special_unmapped=[]
    special_ambiguous=[]
    special_identity={}
    for sid,r in profile_by_id.items():
        surface=norm(r["Tag"])
        candidates=set(source_index.get(surface,set()))
        if surface in intents: candidates.add(surface)
        if len(candidates)==1:
            key=next(iter(candidates)); special_identity[sid]=key
        elif len(candidates)==0:
            special_unmapped.append((sid,r["Tag"]))
        else:
            # Prefer a direct identity-key match if present.
            if surface in candidates:
                special_identity[sid]=surface
            else:
                special_ambiguous.append((sid,r["Tag"],sorted(candidates)))

    # Fallback for promoted Special IDs whose canonical tag is tracked explicitly.
    promoted={}
    for rel in ["docs/issue96/special_expansion_promotion_proposal_v1.csv","docs/issue107/promotion_metadata_v1.csv"]:
        for r in rows(root/rel):
            promoted[int(r["proposed_special_id"])]=norm(r["canonical_tag"])
    for sid,key in promoted.items():
        if sid in production_ids and key in intents:
            special_identity[sid]=key
            special_unmapped=[x for x in special_unmapped if x[0]!=sid]
            special_ambiguous=[x for x in special_ambiguous if x[0]!=sid]

    # Current explicit Special route overrides.
    override_rows=rows(root/"src/DanbooruTagTool.Data/UnifiedBrowseData/special_route_overrides_v1.csv")
    overrides=defaultdict(set)
    for r in override_rows: overrides[int(r["special_id"])].add(r["route_id"])

    for sid,r in profile_by_id.items():
        if sid not in special_identity: continue
        key=special_identity[sid]; d=identities[key]; d["special"]=True; d["special_ids"].append(sid)
        sv=special_v2[sid]
        if sv["kind"]: d["special_kinds"].add(sv["kind"])
        d["body_sites"].update(sv["body"]); d["themes"].update(sv["themes"])
        browseable=sv["status"] in {"AUTO_CANDIDATE","HUMAN_RESOLVED"}
        if browseable and sv["kind"] in SPECIAL_ROUTE:
            d["current_routes"].add(SPECIAL_ROUTE[sv["kind"]])
        if browseable:
            d["current_routes"].update(overrides.get(sid,set()))

        family=r.get("GenerationFamily","")
        role=r.get("CompositionRoleOverride","")
        genrole=r.get("GenerationRole","")
        if family=="POSE_COMPOSITION" and role=="pose":
            d["authority_expected_routes"].add("POSE_POSITION")
        elif family=="POSE_COMPOSITION" and role=="camera":
            d["authority_expected_routes"].add("COMPOSITION_CAMERA")
        elif family=="SCENE_CONTEXT":
            d["authority_expected_routes"].add("SCENE_BACKGROUND")
        if family=="POSE_COMPOSITION" and (role=="pose_camera" or genrole=="pose_camera"):
            d["review_signals"].add("POSE_CAMERA_COMPOUND_NOT_PROJECTED")
        if sv["kind"]=="POSE_SCENE" and not ({"POSE_POSITION","COMPOSITION_CAMERA","SCENE_BACKGROUND"} & d["current_routes"]):
            d["review_signals"].add("POSE_SCENE_WITHOUT_POSE_CAMERA_SCENE_ROUTE")

    # Existing expected projection must never disappear.
    for d in identities.values():
        missing=d["authority_expected_routes"]-d["current_routes"]
        if missing:
            d["review_signals"].add("PROJECTION_GAP:"+("|".join(sorted(missing))))

    # Full-population heuristic pattern census. These are REVIEW signals only.
    pattern_rows=[]
    for r in general_rows:
        if r["classification_status"]!="PROPOSED": continue
        canonical=r["canonical"]; tokens=set(norm(canonical).split("_"))
        primary=(r["primary_path"] or "").split("/",1)[0]
        secondary=set(parse_secondary(r["secondary_paths"]))
        pats=[]
        if primary=="ACTION_CONTACT" and (tokens & BODY_TOKENS) and not any(p.startswith("BODY_PART") for p in secondary):
            pats.append("ACTION_EXPLICIT_BODY_NO_BODY_SECONDARY")
        first=next(iter(tokens),None)
        if primary in {"CLOTHING","HAIR_FACE","BODY_PART"} and (tokens & COLOR_PREFIXES) and not any(p.startswith("COLOR_APPEARANCE") for p in secondary):
            pats.append("COLOR_MODIFIER_NO_COLOR_SECONDARY")
        if primary=="OBJECT_PROP" and (tokens & FIXTURE_TOKENS) and not any(p.startswith("PLACE_BACKGROUND") for p in secondary):
            pats.append("OBJECT_FIXTURE_NO_PLACE_SECONDARY")
        if primary=="PLACE_BACKGROUND" and (tokens & FIXTURE_TOKENS) and not any(p.startswith("OBJECT_PROP") for p in secondary):
            pats.append("PLACE_FIXTURE_NO_OBJECT_SECONDARY")
        if primary=="CLOTHING" and (tokens & PLACEMENT_TOKENS) and not any(p.startswith("CLOTHING_STATE_EXPOSURE") for p in secondary):
            pats.append("CLOTHING_PLACEMENT_NO_STATE_SECONDARY")
        for p in pats:
            pattern_rows.append({"pattern":p,"canonical":canonical,"primary_path":r["primary_path"],
                                 "secondary_paths":r["secondary_paths"],"confidence":"REVIEW_ONLY"})

    # Classify every #118 identity.
    audit=[]
    for key,d in identities.items():
        browse_authority=(d["general"] and "PROPOSED" in d["general_statuses"]) or bool(d["special_ids"] and (d["special_kinds"] or d["body_sites"] or d["themes"]))
        projection=[x for x in d["review_signals"] if x.startswith("PROJECTION_GAP:")]
        if projection:
            bucket="PROJECTION_GAP"
        elif d["review_signals"]:
            bucket="REVIEW"
        elif not browse_authority or not d["current_routes"] and not d["body_sites"] and not d["themes"]:
            bucket="NO_AUTHORITY"
        else:
            bucket="OK"
        audit.append({
            "identity_key":key,"bucket":bucket,"sexual_intent":d["intent"],"review_status":d["review_status"],
            "is_general":"YES" if d["general"] else "NO","is_special":"YES" if d["special"] else "NO",
            "current_routes":"|".join(sorted(d["current_routes"])),"general_paths":"|".join(sorted(d["general_paths"])),
            "special_ids":"|".join(map(str,sorted(d["special_ids"]))),"special_kinds":"|".join(sorted(d["special_kinds"])),
            "body_sites":"|".join(sorted(d["body_sites"])),"themes":"|".join(sorted(d["themes"])),
            "review_signals":"|".join(sorted(d["review_signals"]))
        })

    # Route load by identity and intent.
    route_counts=defaultdict(Counter)
    for d in audit:
        routes=split_pipe(d["current_routes"])
        for route in routes:
            route_counts[route]["ALL"]+=1
            intent=d["sexual_intent"] or "UNCLASSIFIED"
            route_counts[route][intent]+=1
    route_rows=[]
    for route,c in sorted(route_counts.items()):
        route_rows.append({"route":route,"all":c["ALL"],"sexual":c["SEXUAL"],"contextual":c["CONTEXTUAL"],
                           "non_sexual":c["NON_SEXUAL"],"unclassified":c["UNCLASSIFIED"]})

    # Summary / invariants.
    bucket_counts=Counter(x["bucket"] for x in audit)
    pattern_counts=Counter(x["pattern"] for x in pattern_rows)
    membership=Counter(
        "OVERLAP" if x["is_general"]=="YES" and x["is_special"]=="YES" else
        "GENERAL_ONLY" if x["is_general"]=="YES" else "SPECIAL_ONLY" if x["is_special"]=="YES" else "NEITHER"
        for x in audit
    )
    summary={
        "schema_version":1,
        "population":{"identity_count":len(audit),"general_rows":len(general_rows),"special_profile_rows":len(profile),
                      "special_identity_mapped":len(special_identity),"special_identity_unmapped":len(special_unmapped),
                      "special_identity_ambiguous":len(special_ambiguous),"membership":dict(membership)},
        "buckets":dict(bucket_counts),
        "pattern_candidate_counts":dict(pattern_counts),
        "route_load":{r:dict(c) for r,c in sorted(route_counts.items())},
        "notes":[
            "Identity universe is Issue #118 v2 (31,003).",
            "General current routes are projected from accepted #64 primary+secondary paths using current UnifiedBrowseTaxonomy mapping.",
            "Special v2 is reconstructed from tracked #56/#76/#96/#107 authorities and restricted to the production 3,059-ID profile.",
            "Heuristic pattern candidates are REVIEW_ONLY and never automatic route changes.",
            "NO_AUTHORITY is not an error; it means no sufficiently trusted browse route is available from tracked authority."
        ],
        "special_mapping_issues":{"unmapped":special_unmapped[:200],"ambiguous":special_ambiguous[:200]},
    }

    def write_csv(path, data):
        if not data:
            path.write_text("",encoding="utf-8"); return
        with path.open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)

    write_csv(out/"identity_audit.csv", sorted(audit,key=lambda x:x["identity_key"]))
    write_csv(out/"pattern_candidates.csv", sorted(pattern_rows,key=lambda x:(x["pattern"],x["canonical"])))
    write_csv(out/"route_load.csv", route_rows)
    (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if len(audit)!=31003: raise SystemExit("identity population mismatch")
    if special_unmapped or special_ambiguous:
        # Keep audit usable but fail closed so mapping quality cannot be silently ignored.
        raise SystemExit(f"special identity mapping incomplete: unmapped={len(special_unmapped)} ambiguous={len(special_ambiguous)}")

if __name__=="__main__":
    main()
