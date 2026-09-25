#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from parallel_overlay import load_checkpoint_union, apply_corrections
from staging_repair_overlay import resolve_repair_overlay, git_blob_sha
from staging_v2 import ROUTE_REASON_JA, compact_row_to_full
from validate_luna_pass_a import FIELDS, validate_row
from rebuild_manual_audit_structural_repairs import build_pool, build_effective, read_neutral

ROOT=Path(__file__).resolve().parents[2]
PARALLEL=ROOT/"docs/issue132/parallel"
MANIFEST=PARALLEL/"manual_audit_semantic_patches_v1.json"
WINDOW_RE=re.compile(r"window_(\d{6})_(\d{6})\.json$")

def jlist(v):
    return json.dumps(list(v),ensure_ascii=False,separators=(",",":"))

def full_to_compact(row, expected, idx):
    routes=[]
    for n in (1,2,3):
        rid=row.get(f"route_{n}_id","").strip()
        if rid:
            routes.append({"id":rid,"strength":row[f"route_{n}_strength"]})
    return {
        "lane_local_index":idx,
        "review_seq":int(expected["review_seq"]),
        "identity_sha256":hashlib.sha256(expected["identity_key"].encode()).hexdigest(),
        "discovery_mode":row["discovery_mode"],
        "routes":routes,
        "local_refinement_ids":json.loads(row.get("local_refinement_ids") or "[]"),
        "body_site_ids":json.loads(row.get("body_site_ids") or "[]"),
        "theme_ids":json.loads(row.get("theme_ids") or "[]"),
        "route_vocabulary_gap":row["route_vocabulary_gap"],
        "review_depth":row["review_depth"],
        "evidence_urls":json.loads(row.get("evidence_urls") or "[]"),
    }

def apply_ops(compact,ops):
    c=json.loads(json.dumps(compact))
    if "set_mode" in ops:
        c["discovery_mode"]=ops["set_mode"]
    if "set_routes" in ops:
        c["routes"]=[{"id":x[0],"strength":x[1]} for x in ops["set_routes"]]
    if "remove_routes" in ops:
        rm=set(ops["remove_routes"])
        c["routes"]=[r for r in c["routes"] if r["id"] not in rm]
    if "set_local" in ops:
        c["local_refinement_ids"]=list(ops["set_local"])
    if "set_body" in ops:
        c["body_site_ids"]=list(ops["set_body"])
    if "add_body" in ops:
        c["body_site_ids"]=list(dict.fromkeys(c["body_site_ids"]+list(ops["add_body"])))
    if "remove_body" in ops:
        rm=set(ops["remove_body"]); c["body_site_ids"]=[x for x in c["body_site_ids"] if x not in rm]
    if "set_theme" in ops:
        c["theme_ids"]=list(ops["set_theme"])
    if "add_theme" in ops:
        c["theme_ids"]=list(dict.fromkeys(c["theme_ids"]+list(ops["add_theme"])))
    if "remove_theme" in ops:
        rm=set(ops["remove_theme"]); c["theme_ids"]=[x for x in c["theme_ids"] if x not in rm]
    if "set_gap" in ops:
        c["route_vocabulary_gap"]=ops["set_gap"]
    if "set_depth" in ops:
        c["review_depth"]=ops["set_depth"]
    if "set_evidence" in ops:
        c["evidence_urls"]=list(ops["set_evidence"])
    if c["discovery_mode"]=="SEARCH_ORIENTED":
        c["routes"]=[]; c["local_refinement_ids"]=[]; c["body_site_ids"]=[]; c["theme_ids"]=[]
        c["route_vocabulary_gap"]="NO"
    return c

def compact_into_full(current, compact):
    out=dict(current)
    out["discovery_mode"]=compact["discovery_mode"]
    for n in (1,2,3):
        out[f"route_{n}_id"]=""
        out[f"route_{n}_strength"]=""
        out[f"route_{n}_reason_ja"]=""
    for n,r in enumerate(compact["routes"],1):
        out[f"route_{n}_id"]=r["id"]
        out[f"route_{n}_strength"]=r["strength"]
        out[f"route_{n}_reason_ja"]=ROUTE_REASON_JA.get(r["id"],"独立した閲覧軸として探すのが自然")
    out["local_refinement_ids"]=jlist(compact["local_refinement_ids"])
    out["body_site_ids"]=jlist(compact["body_site_ids"])
    out["theme_ids"]=jlist(compact["theme_ids"])
    out["route_vocabulary_gap"]=compact["route_vocabulary_gap"]
    out["route_vocabulary_gap_note"]="既存の閲覧ルート語彙では対象を十分に表現できない" if compact["route_vocabulary_gap"]=="YES" else ""
    out["review_depth"]=compact["review_depth"]
    out["evidence_urls"]=jlist(compact["evidence_urls"])
    if compact["discovery_mode"]!="SEMANTIC_UNRESOLVED":
        out["uncertainty_note"]=""
    return out

def find_window(lane,idx):
    stage=PARALLEL/f"lane-{lane}/staging"
    for p in sorted(stage.glob("window_*.json")):
        m=WINDOW_RE.match(p.name)
        if not m: continue
        a,b=map(int,m.groups())
        if a<=idx<=b:
            return p,a,b
    raise RuntimeError(f"lane {lane} index {idx}: staging window not found")

def existing_patch_fields(lane,review_seq):
    out=set()
    d=PARALLEL/f"lane-{lane}/corrections"
    if not d.exists(): return out
    for p in d.glob(f"correction_{review_seq:06d}_*.json"):
        try: obj=json.loads(p.read_text(encoding="utf-8"))
        except Exception: continue
        if isinstance(obj.get("patch"),dict):
            out.update(obj["patch"])
    return out

def source_checkpoint_name(ranges,idx):
    for a,b,p in ranges:
        if a<=idx<=b: return p.name
    raise RuntimeError(f"checkpoint source missing for {idx}")

def write_checkpoint_correction(lane,idx,expected,raw,current,desired,ranges):
    review_seq=int(expected["review_seq"])
    changed={k:v for k,v in desired.items() if k in FIELDS and k not in {"review_seq","identity_key"} and raw.get(k,"")!=v}
    already=existing_patch_fields(lane,review_seq)
    patch={}
    expected_before={}
    for k,v in changed.items():
        if k in already:
            if current.get(k,"")!=v:
                raise RuntimeError(f"lane {lane} idx {idx}: existing correction conflicts on {k}")
            continue
        patch[k]=v
        expected_before[k]=raw.get(k,"")
    if not patch:
        return None
    out={
        "schema_version":"issue132-pass-a-correction-v1",
        "lane":lane,
        "lane_local_index":idx,
        "review_seq":review_seq,
        "identity_key":expected["identity_key"],
        "source_checkpoint":source_checkpoint_name(ranges,idx),
        "qa_boundary":idx,
        "reason":"Manual semantic audit remediation; code-only patch authority joined to frozen neutral identity.",
        "expected_before":expected_before,
        "patch":patch,
    }
    d=PARALLEL/f"lane-{lane}/corrections"; d.mkdir(parents=True,exist_ok=True)
    p=d/f"correction_{review_seq:06d}_manual_audit_v1.json"
    if p.exists():
        old=json.loads(p.read_text(encoding="utf-8"))
        if old!=out: raise RuntimeError(f"{p.name}: existing content mismatch")
        return None
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return p

def effective_window_for(lane,path,a,b,assigned,pools):
    repaired,_,errs=resolve_repair_overlay(path,lane,a,b)
    if errs: raise RuntimeError("; ".join(errs))
    if repaired is not None:
        return json.loads(json.dumps(repaired))
    effective,_=build_effective(lane,a,b,assigned,pools[lane],path)
    return effective

def write_staging_overlay(lane,path,a,b,effective,supersedes):
    raw=path.read_bytes()
    d=path.parent/"repairs"; d.mkdir(parents=True,exist_ok=True)
    nums=[]
    for p in d.glob(f"repair_{a:06d}_{b:06d}_v*.json"):
        try: nums.append(int(p.stem.rsplit("_v",1)[1]))
        except Exception: pass
    n=max(nums or [0])+1
    outp=d/f"repair_{a:06d}_{b:06d}_v{n:03d}.json"
    obj={
        "schema_version":"issue132-pass-a-staging-repair-overlay-v1",
        "lane":lane,
        "lane_local_start":a,
        "lane_local_end":b,
        "source_staging_path":path.relative_to(ROOT).as_posix(),
        "source_staging_blob_sha":git_blob_sha(raw),
        "source_staging_sha256":hashlib.sha256(raw).hexdigest(),
        "repair_reason_codes":["SEMANTIC_LINT","ROUTE_FAMILY_REMEDIATION"],
        "supersedes":supersedes,
        "effective_window":effective,
    }
    outp.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    return outp

def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries=manifest["entries"]
    neutral=read_neutral()
    raw_by_lane={}; effective_cp={}; ranges_by_lane={}; prefix={}
    for lane in (1,2,3):
        raw,ranges,errs=load_checkpoint_union(ROOT,lane,FIELDS)
        if errs: raise RuntimeError(str(errs))
        eff,_,corr_errs=apply_corrections(ROOT,lane,raw,ranges,FIELDS)
        if corr_errs: raise RuntimeError(str(corr_errs))
        raw_by_lane[lane]=raw; effective_cp[lane]=eff; ranges_by_lane[lane]=ranges; prefix[lane]=len(raw)
    pools={lane:build_pool(lane) for lane in (1,2,3)}
    written=[]
    staging_groups={}
    for ent in entries:
        lane=int(ent["lane"]); idx=int(ent["lane_local_index"]); ops=ent["ops"]
        expected=neutral[lane][idx-1]
        if idx<=prefix[lane]:
            raw=raw_by_lane[lane][idx-1]
            current=effective_cp[lane][idx-1]
            compact=full_to_compact(current,expected,idx)
            desired_compact=apply_ops(compact,ops)
            desired=compact_into_full(current,desired_compact)
            errs=validate_row(desired,int(expected["review_seq"]))
            if errs: raise RuntimeError(f"lane {lane} idx {idx}: {errs}")
            p=write_checkpoint_correction(lane,idx,expected,raw,current,desired,ranges_by_lane[lane])
            if p: written.append(p.relative_to(ROOT).as_posix())
        else:
            path,a,b=find_window(lane,idx)
            key=(lane,path.as_posix(),a,b)
            staging_groups.setdefault(key,[]).append((idx,ops))
    for (lane,path_s,a,b),patches in staging_groups.items():
        path=Path(path_s)
        effective=effective_window_for(lane,path,a,b,neutral[lane],pools)
        rows={int(r["lane_local_index"]):r for r in effective["rows"]}
        holds={int(h["lane_local_index"]):h for h in effective["holds"]}
        changed=False
        for idx,ops in patches:
            if idx in holds: raise RuntimeError(f"lane {lane} idx {idx}: semantic patch targets hold")
            if idx not in rows: raise RuntimeError(f"lane {lane} idx {idx}: row absent")
            expected=neutral[lane][idx-1]
            desired=apply_ops(rows[idx],ops)
            full=compact_row_to_full(desired,expected,FIELDS)
            errs=validate_row(full,int(expected["review_seq"]))
            if errs: raise RuntimeError(f"lane {lane} idx {idx}: {errs}")
            if desired != rows[idx]:
                rows[idx]=desired
                changed=True
        if not changed:
            continue
        effective["rows"]=[rows[i] for i in sorted(rows)]
        existing=sorted((path.parent/"repairs").glob(f"repair_{a:06d}_{b:06d}_v*.json"))
        p=write_staging_overlay(lane,path,a,b,effective,[x.name for x in existing])
        written.append(p.relative_to(ROOT).as_posix())
    report=PARALLEL/"manual-audit-semantic-repair-report.json"
    report.write_text(json.dumps({"entry_count":len(entries),"written":written},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(report.read_text(encoding="utf-8"))

if __name__=="__main__":
    main()
