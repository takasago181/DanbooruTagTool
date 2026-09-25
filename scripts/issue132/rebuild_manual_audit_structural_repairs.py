#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARALLEL = ROOT / "docs/issue132/parallel"
NEUTRAL = PARALLEL / "input/luna_neutral_review_input_v2.csv"

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
        # Historical Lane-2 526-550 has one known broken escaped JSON-list string.
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

def v1_to_compact(row, expected, idx):
    routes=[]
    for n in (1,2,3):
        rid=str(row.get(f"route_{n}_id","")).strip()
        if rid:
            routes.append({"id":rid,"strength":str(row.get(f"route_{n}_strength","")).strip()})
    return {
        "lane_local_index": idx,
        "review_seq": int(expected["review_seq"]),
        "identity_sha256": identity_sha(expected["identity_key"]),
        "discovery_mode": row["discovery_mode"],
        "routes": routes,
        "local_refinement_ids": parse_list(row.get("local_refinement_ids","[]")),
        "body_site_ids": parse_list(row.get("body_site_ids","[]")),
        "theme_ids": parse_list(row.get("theme_ids","[]")),
        "route_vocabulary_gap": row.get("route_vocabulary_gap","NO"),
        "review_depth": row.get("review_depth","CHECKED"),
        "evidence_urls": parse_list(row.get("evidence_urls","[]")),
    }

def normalize_v1_row(raw):
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list) and len(raw) == len(FIELDS):
        return dict(zip(FIELDS, (str(x) for x in raw)))
    raise RuntimeError("unsupported v1 row shape")

def compact_hold(expected, idx, source_hold):
    if isinstance(source_hold, dict) and "identity_sha256" in source_hold:
        return {
            "lane_local_index": idx,
            "review_seq": int(expected["review_seq"]),
            "identity_sha256": identity_sha(expected["identity_key"]),
            "reason_code": source_hold.get("reason_code","OTHER_UNRESOLVED"),
            "research_attempt_codes": source_hold.get("research_attempt_codes") or ["OTHER_DIRECT_SOURCE"],
        }
    return {
        "lane_local_index": idx,
        "review_seq": int(expected["review_seq"]),
        "identity_sha256": identity_sha(expected["identity_key"]),
        "reason_code": "OTHER_UNRESOLVED",
        "research_attempt_codes": ["OTHER_DIRECT_SOURCE"],
    }

def build_effective(lane, start, end, obj, assigned):
    expected = {i: assigned[i-1] for i in range(start,end+1)}
    by_key = {r["identity_key"]: i for i,r in expected.items()}
    by_hash = {identity_sha(r["identity_key"]): i for i,r in expected.items()}
    out_rows = {}
    out_holds = {}

    for raw in obj.get("rows", []):
        if isinstance(raw, dict) and obj.get("schema_version") == SCHEMA_V2:
            h = raw.get("identity_sha256")
            idx = by_hash.get(h)
            if idx is None:
                raise RuntimeError(f"lane {lane} {start}-{end}: compact row hash not in target")
            if idx in out_rows or idx in out_holds:
                raise RuntimeError(f"lane {lane} {start}-{end}: duplicate identity at {idx}")
            r = dict(raw)
            r["lane_local_index"] = idx
            r["review_seq"] = int(expected[idx]["review_seq"])
            r["identity_sha256"] = identity_sha(expected[idx]["identity_key"])
            out_rows[idx] = r
        else:
            row = normalize_v1_row(raw)
            idx = by_key.get(row.get("identity_key",""))
            if idx is None:
                raise RuntimeError(f"lane {lane} {start}-{end}: row identity not in target: {row.get('identity_key')}")
            if idx in out_rows or idx in out_holds:
                raise RuntimeError(f"lane {lane} {start}-{end}: duplicate identity at {idx}")
            out_rows[idx] = v1_to_compact(row, expected[idx], idx)

    for h in obj.get("holds", []):
        if not isinstance(h, dict):
            raise RuntimeError(f"lane {lane} {start}-{end}: non-object hold")
        if "identity_sha256" in h:
            idx = by_hash.get(h.get("identity_sha256"))
        else:
            idx = by_key.get(h.get("identity_key",""))
        if idx is None:
            raise RuntimeError(f"lane {lane} {start}-{end}: hold identity not in target")
        if idx in out_rows or idx in out_holds:
            raise RuntimeError(f"lane {lane} {start}-{end}: duplicate row/hold identity at {idx}")
        out_holds[idx] = compact_hold(expected[idx], idx, h)

    covered = set(out_rows) | set(out_holds)
    wanted = set(range(start,end+1))
    if covered != wanted:
        missing = sorted(wanted-covered)
        extra = sorted(covered-wanted)
        names = [expected[i]["identity_key"] for i in missing]
        raise RuntimeError(
            f"lane {lane} {start}-{end}: cannot losslessly repair; "
            f"missing={list(zip(missing,names))} extra={extra}"
        )

    return {
        "schema_version": SCHEMA_V2,
        "lane": lane,
        "lane_local_start": start,
        "lane_local_end": end,
        "parent_neutral_sha256": EXPECTED_PARENT_SHA,
        "parent_identity_order_sha256": EXPECTED_ORDER_SHA,
        "rows": [out_rows[i] for i in sorted(out_rows)],
        "holds": [out_holds[i] for i in sorted(out_holds)],
    }

def next_overlay_path(repair_dir: Path, start:int, end:int):
    existing = sorted(repair_dir.glob(f"repair_{start:06d}_{end:06d}_v*.json"))
    if not existing:
        return repair_dir / f"repair_{start:06d}_{end:06d}_v001.json", []
    nums=[]
    for p in existing:
        try: nums.append(int(p.stem.rsplit("_v",1)[1]))
        except Exception: pass
    n=max(nums or [0])+1
    return repair_dir / f"repair_{start:06d}_{end:06d}_v{n:03d}.json", [p.name for p in existing]

def main():
    assigned = read_neutral()
    written=[]
    failures=[]
    for lane,ranges in TARGETS.items():
        for start,end in ranges:
            source = PARALLEL / f"lane-{lane}/staging/window_{start:06d}_{end:06d}.json"
            raw_bytes = source.read_bytes()
            try:
                obj, was_malformed = parse_source(source)
                effective = build_effective(lane,start,end,obj,assigned[lane])
                repair_dir = source.parent / "repairs"
                repair_dir.mkdir(parents=True, exist_ok=True)
                out_path, supersedes = next_overlay_path(repair_dir,start,end)
                reasons=["STRUCTURAL_REBUILD","IDENTITY_REBIND"]
                if was_malformed:
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
            except Exception as exc:
                failures.append(f"L{lane} {start}-{end}: {exc}")
    print(json.dumps({"written":written,"failures":failures},ensure_ascii=False,indent=2))
    if failures:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
