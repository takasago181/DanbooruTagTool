#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARALLEL = ROOT / "docs/issue132/parallel"
NEUTRAL = PARALLEL / "input/luna_neutral_review_input_v2.csv"

MISSING_DECISIONS = {
    (1,800): {
        "discovery_mode":"BROWSE_WORTHY",
        "routes":[{"id":"BODY_SITE","strength":"CORE"},{"id":"TOOL_OBJECT","strength":"SUPPORTING"}],
        "local_refinement_ids":["OBJECT_PROP/FOOD"],
        "body_site_ids":["MOUTH_ORAL"],
        "theme_ids":[],
        "route_vocabulary_gap":"NO",
        "review_depth":"RESEARCHED",
        "evidence_urls":["https://safebooru.donmai.us/wiki_pages/toast"],
    },
    (2,525): {
        "discovery_mode":"BROWSE_WORTHY",
        "routes":[{"id":"CLOTHING_EXPOSURE","strength":"CORE"},{"id":"COLOR_PATTERN_SHAPE","strength":"SUPPORTING"}],
        "local_refinement_ids":["CLOTHING/EVERYDAY"],
        "body_site_ids":[],
        "theme_ids":[],
        "route_vocabulary_gap":"NO",
        "review_depth":"CHECKED",
        "evidence_urls":[],
    },
    (2,650): {
        "discovery_mode":"BROWSE_WORTHY",
        "routes":[{"id":"POSE_POSITION","strength":"CORE"},{"id":"LIVING","strength":"SUPPORTING"}],
        "local_refinement_ids":["LIVING_NATURE/PLANT"],
        "body_site_ids":[],
        "theme_ids":[],
        "route_vocabulary_gap":"NO",
        "review_depth":"RESEARCHED",
        "evidence_urls":["https://safebooru.donmai.us/wiki_pages/sitting_in_tree"],
    },
    (2,950): {
        "discovery_mode":"BROWSE_WORTHY",
        "routes":[{"id":"COLOR_PATTERN_SHAPE","strength":"CORE"}],
        "local_refinement_ids":[],
        "body_site_ids":[],
        "theme_ids":[],
        "route_vocabulary_gap":"NO",
        "review_depth":"RESEARCHED",
        "evidence_urls":["https://tags.latent.moe/en/t/flower_knot"],
    },
}

TARGETS = {
    1: [(751,775),(776,800)],
    2: [(501,525),(526,550),(551,575),(626,650),(651,675),(676,700),
        (726,750),(751,775),(776,800),(926,950),(976,1000),(1101,1125),(1126,1150)],
    3: [(851,875),(951,975),(1026,1050),(1051,1075)],
}

EXPECTED_PARENT_SHA = "ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d"
EXPECTED_ORDER_SHA = "f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b"
SCHEMA_V2 = "issue132-pass-a-staging-window-v2"
OVERLAY_SCHEMA = "issue132-pass-a-staging-repair-overlay-v1"
WINDOW_RE = re.compile(r"window_(\d{6})_(\d{6})\.json$")

FIELDS = [
    "review_seq","identity_key","manual_seen","semantic_summary_ja","discovery_mode",
    "route_1_id","route_1_strength","route_1_reason_ja",
    "route_2_id","route_2_strength","route_2_reason_ja",
    "route_3_id","route_3_strength","route_3_reason_ja",
    "local_refinement_ids","body_site_ids","theme_ids",
    "route_vocabulary_gap","route_vocabulary_gap_note",
    "review_depth","evidence_urls","uncertainty_note"
]

def identity_sha(identity: str) -> str:
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()

def read_neutral():
    with NEUTRAL.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 31003:
        raise RuntimeError(f"neutral count {len(rows)} != 31003")
    return {
        lane: [r for r in rows if ((int(r["review_seq"]) - 1) % 3) + 1 == lane]
        for lane in (1,2,3)
    }

def parse_source(path: Path):
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw), False
    except json.JSONDecodeError:
        repaired = raw.replace(
            '"local_refinement_ids":"[\\\"CLOTHING/ACCESSORY"]"',
            '"local_refinement_ids":"[\\\"CLOTHING/ACCESSORY\\\"]"'
        )
        return json.loads(repaired), True

def parse_list(value):
    if isinstance(value, list):
        return list(value)
    if value in (None, ""):
        return []
    out = json.loads(value)
    if not isinstance(out, list):
        raise RuntimeError(f"expected list, got {type(out)}")
    return out

def normalize_v1_row(raw):
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list) and len(raw) == len(FIELDS):
        return dict(zip(FIELDS, (str(x) for x in raw)))
    raise RuntimeError("unsupported v1 row shape")

def v1_to_compact(row, expected, idx):
    routes=[]
    for n in (1,2,3):
        rid=str(row.get(f"route_{n}_id","")).strip()
        if rid:
            routes.append({"id":rid,"strength":str(row.get(f"route_{n}_strength","")).strip()})
    return {
        "lane_local_index":idx,
        "review_seq":int(expected["review_seq"]),
        "identity_sha256":identity_sha(expected["identity_key"]),
        "discovery_mode":row["discovery_mode"],
        "routes":routes,
        "local_refinement_ids":parse_list(row.get("local_refinement_ids","[]")),
        "body_site_ids":parse_list(row.get("body_site_ids","[]")),
        "theme_ids":parse_list(row.get("theme_ids","[]")),
        "route_vocabulary_gap":row.get("route_vocabulary_gap","NO"),
        "review_depth":row.get("review_depth","CHECKED"),
        "evidence_urls":parse_list(row.get("evidence_urls","[]")),
    }

def compact_hold(expected, idx, source_hold):
    if isinstance(source_hold, dict) and "identity_sha256" in source_hold:
        reason = source_hold.get("reason_code","OTHER_UNRESOLVED")
        attempts = source_hold.get("research_attempt_codes") or ["OTHER_DIRECT_SOURCE"]
    else:
        reason = "OTHER_UNRESOLVED"
        attempts = ["OTHER_DIRECT_SOURCE"]
    return {
        "lane_local_index":idx,
        "review_seq":int(expected["review_seq"]),
        "identity_sha256":identity_sha(expected["identity_key"]),
        "reason_code":reason,
        "research_attempt_codes":attempts,
    }

def candidate_compact(candidate, expected, idx):
    if candidate["kind"] == "hold":
        return "hold", compact_hold(expected, idx, candidate["raw"])
    raw=candidate["raw"]
    schema=candidate["schema"]
    if schema == SCHEMA_V2 and isinstance(raw, dict):
        out=dict(raw)
        out["lane_local_index"]=idx
        out["review_seq"]=int(expected["review_seq"])
        out["identity_sha256"]=identity_sha(expected["identity_key"])
        return "row", out
    return "row", v1_to_compact(normalize_v1_row(raw), expected, idx)

def candidate_fingerprint(kind, value):
    copy=dict(value)
    copy.pop("lane_local_index",None)
    copy.pop("review_seq",None)
    copy.pop("identity_sha256",None)
    return kind + ":" + json.dumps(copy,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def build_pool(lane):
    stage_dir=PARALLEL / f"lane-{lane}/staging"
    by_key={}
    by_hash={}
    malformed_paths=set()
    for path in sorted(stage_dir.glob("window_*.json")):
        m=WINDOW_RE.match(path.name)
        if not m:
            continue
        start,end=map(int,m.groups())
        obj,malformed=parse_source(path)
        if malformed:
            malformed_paths.add(path.as_posix())
        schema=obj.get("schema_version")
        def add(container,key,c):
            if key:
                container.setdefault(key,[]).append(c)
        for raw in obj.get("rows",[]):
            c={"kind":"row","raw":raw,"schema":schema,"path":path,"start":start,"end":end}
            if schema == SCHEMA_V2 and isinstance(raw,dict):
                add(by_hash,raw.get("identity_sha256"),c)
            else:
                row=normalize_v1_row(raw)
                add(by_key,row.get("identity_key"),c)
        for raw in obj.get("holds",[]):
            c={"kind":"hold","raw":raw,"schema":schema,"path":path,"start":start,"end":end}
            if isinstance(raw,dict) and raw.get("identity_sha256"):
                add(by_hash,raw.get("identity_sha256"),c)
            elif isinstance(raw,dict):
                add(by_key,raw.get("identity_key"),c)
    return by_key,by_hash,malformed_paths

def choose_candidate(candidates, expected, idx, target_path):
    if not candidates:
        raise RuntimeError(f"no historical candidate for {idx}:{expected['identity_key']}")
    def rank(c):
        exact = 0 if c["path"] == target_path else 1
        contains = 0 if c["start"] <= idx <= c["end"] else 1
        distance = min(abs(idx-c["start"]),abs(idx-c["end"]))
        kind = 0 if c["kind"] == "row" else 1
        return (exact,contains,distance,kind,c["path"].name)
    ordered=sorted(candidates,key=rank)
    best_rank=rank(ordered[0])[:4]
    tied=[c for c in ordered if rank(c)[:4] == best_rank]
    normalized=[candidate_compact(c,expected,idx) for c in tied]
    fps={candidate_fingerprint(k,v) for k,v in normalized}
    if len(fps)>1:
        raise RuntimeError(
            f"conflicting historical candidates for {idx}:{expected['identity_key']} "
            f"from {[c['path'].name for c in tied]}"
        )
    return normalized[0], ordered[0]["path"]

def build_effective(lane,start,end,assigned,pool,target_path):
    by_key,by_hash,_=pool
    rows={}
    holds={}
    provenance={}
    for idx in range(start,end+1):
        expected=assigned[idx-1]
        key=expected["identity_key"]
        h=identity_sha(key)
        candidates=list(by_key.get(key,[]))+list(by_hash.get(h,[]))
        if not candidates and (lane,idx) in MISSING_DECISIONS:
            value={
                "lane_local_index":idx,
                "review_seq":int(expected["review_seq"]),
                "identity_sha256":h,
                **MISSING_DECISIONS[(lane,idx)],
            }
            rows[idx]=value
            provenance[idx]="MANUAL_AUDIT_RECOVERY"
            continue
        (kind,value),source_path=choose_candidate(candidates,expected,idx,target_path)
        if kind == "row":
            rows[idx]=value
        else:
            holds[idx]=value
        provenance[idx]=source_path.relative_to(ROOT).as_posix()
    return {
        "schema_version":SCHEMA_V2,
        "lane":lane,
        "lane_local_start":start,
        "lane_local_end":end,
        "parent_neutral_sha256":EXPECTED_PARENT_SHA,
        "parent_identity_order_sha256":EXPECTED_ORDER_SHA,
        "rows":[rows[i] for i in sorted(rows)],
        "holds":[holds[i] for i in sorted(holds)],
    }, provenance

def next_overlay_path(repair_dir,start,end):
    existing=sorted(repair_dir.glob(f"repair_{start:06d}_{end:06d}_v*.json"))
    if not existing:
        return repair_dir/f"repair_{start:06d}_{end:06d}_v001.json",[]
    nums=[]
    for p in existing:
        try: nums.append(int(p.stem.rsplit("_v",1)[1]))
        except Exception: pass
    n=max(nums or [0])+1
    return repair_dir/f"repair_{start:06d}_{end:06d}_v{n:03d}.json",[p.name for p in existing]

def main():
    assigned=read_neutral()
    written=[]
    failures=[]
    provenance_report={}
    for lane,ranges in TARGETS.items():
        pool=build_pool(lane)
        malformed_paths=pool[2]
        for start,end in ranges:
            source=PARALLEL/f"lane-{lane}/staging/window_{start:06d}_{end:06d}.json"
            raw_bytes=source.read_bytes()
            try:
                effective,provenance=build_effective(lane,start,end,assigned[lane],pool,source)
                repair_dir=source.parent/"repairs"
                repair_dir.mkdir(parents=True,exist_ok=True)
                out_path,supersedes=next_overlay_path(repair_dir,start,end)
                reasons=["STRUCTURAL_REBUILD","IDENTITY_REBIND"]
                if source.as_posix() in malformed_paths:
                    reasons.append("MALFORMED_JSON")
                overlay={
                    "schema_version":OVERLAY_SCHEMA,
                    "lane":lane,
                    "lane_local_start":start,
                    "lane_local_end":end,
                    "source_staging_path":source.relative_to(ROOT).as_posix(),
                    "source_staging_blob_sha":git_blob_sha(raw_bytes),
                    "source_staging_sha256":hashlib.sha256(raw_bytes).hexdigest(),
                    "repair_reason_codes":reasons,
                    "supersedes":supersedes,
                    "effective_window":effective,
                }
                out_path.write_text(json.dumps(overlay,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
                written.append(out_path.relative_to(ROOT).as_posix())
                borrowed={str(i):p for i,p in provenance.items() if p != source.relative_to(ROOT).as_posix()}
                if borrowed:
                    provenance_report[f"L{lane}:{start}-{end}"]=borrowed
            except Exception as exc:
                failures.append(f"L{lane} {start}-{end}: {exc}")
    report=PARALLEL/"manual-audit-structural-repair-report.json"
    report.write_text(json.dumps({"written":written,"failures":failures,"borrowed_provenance":provenance_report},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(report.read_text(encoding="utf-8"))
    if failures:
        raise SystemExit(1)

if __name__=="__main__":
    main()
