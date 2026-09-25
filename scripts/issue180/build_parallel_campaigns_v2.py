#!/usr/bin/env python3
"""Build Issue #180 v2 authority campaigns from the current v3 residual census."""
from __future__ import annotations
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import OUT, ROOT, read_csv, write_csv, sha256_text

CONFIG = ROOT / "docs/issue180/parallel/PARALLEL_EXECUTION_V2.json"
UNITS = OUT / "research_units_v3.csv"
CLOSURE = ROOT / "docs/issue180/v3/reports/RESEARCH_UNIT_CLOSURE_SWEEP_V3.csv"
CAMPAIGNS = OUT / "parallel_authority_campaigns_v2.csv"
SUMMARY = OUT / "parallel_authority_campaigns_summary_v2.json"

FIELDS = [
    "queue_id","campaign_id","owner_role","owner_slot","owner_branch","campaign_key",
    "work_buckets","source_units","member_count","member_ids/tags","priority","queue_fingerprint",
]

def config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))

def owner_slot(campaign_key: str, slots: int) -> int:
    return int(sha256_text(campaign_key)[:16], 16) % slots

def member_hash(tags: list[str]) -> str:
    return sha256_text("\n".join(sorted(tags)))

def normalize_campaign_key(unit: dict[str,str], tag: str | None = None) -> str:
    subject = unit["subject"]
    if tag is not None:
        return "direct:" + tag
    if subject.startswith("discovery-hint:"):
        return "roster:" + subject.split(":", 1)[1]
    if subject and subject != "__UNGROUPED__":
        return subject
    return "unit:" + unit["unit_id"]

def _priority_value(p: str) -> int:
    return {"P1": 1, "P2": 2, "P3": 3}.get(p, 9)

def build_campaigns(units: list[dict[str,str]], closures: list[dict[str,str]], cfg: dict) -> list[dict[str,str]]:
    by_id = {u["unit_id"]: u for u in units}
    forward = set(cfg["forward_buckets"])
    qa = set(cfg["qa_buckets"])
    slots = int(cfg["forward_slots"])
    branches = cfg["forward_branches"]

    grouped: dict[tuple[str,str], list[dict[str,object]]] = defaultdict(list)

    for closure in closures:
        uid = closure["unit_id"]
        unit = by_id.get(uid)
        if not unit or unit.get("status") != "OPEN":
            raise SystemExit(f"closure row is not an exact current OPEN unit: {uid}")
        tags = json.loads(unit["member_ids/tags"])
        if closure["member_ids_sha256"] != member_hash(tags):
            raise SystemExit(f"closure fingerprint drift: {uid}")
        bucket = closure["work_bucket"]
        if bucket not in forward | qa:
            raise SystemExit(f"unowned work_bucket: {bucket}")

        if bucket in qa:
            key = f"qa:{bucket}:{uid}"
            grouped[("QA", key)].append({"unit":unit,"closure":closure,"tags":tags})
            continue

        # Only truly structure-free ungrouped work falls back to one direct campaign per Character.
        # Known family/roster/base subjects stay intact so one reusable authority is never split across lanes.
        if unit["subject"] == "__UNGROUPED__" and len(tags) > 1:
            for tag in tags:
                key = normalize_campaign_key(unit, tag)
                grouped[("FORWARD", key)].append({"unit":unit,"closure":closure,"tags":[tag]})
        else:
            key = normalize_campaign_key(unit)
            grouped[("FORWARD", key)].append({"unit":unit,"closure":closure,"tags":tags})

    queue_material = []
    for (role,key), items in grouped.items():
        for item in items:
            queue_material.append(
                f"{role}|{key}|{item['unit']['unit_id']}|{item['closure']['member_ids_sha256']}|{','.join(sorted(item['tags']))}"
            )
    queue_id = "q2-" + sha256_text("\n".join(sorted(queue_material)))[:20]

    rows=[]
    for (role,key), items in grouped.items():
        tags=sorted({t for item in items for t in item["tags"]})
        buckets=sorted({str(item["closure"]["work_bucket"]) for item in items})
        source_units=sorted(
            {
                (str(item["unit"]["unit_id"]), str(item["closure"]["member_ids_sha256"]))
                for item in items
            }
        )
        source_units_json=json.dumps(
            [{"unit_id":u,"member_ids_sha256":h} for u,h in source_units],
            ensure_ascii=False,separators=(",",":")
        )
        priority=min((str(item["unit"]["priority"]) for item in items), key=_priority_value)
        qfp=sha256_text(source_units_json+"\n"+"\n".join(tags))
        if role=="QA":
            slot=""
            branch=cfg["qa_branch"]
        else:
            n=owner_slot(key,slots)
            slot=str(n)
            branch=branches[n]
        rows.append({
            "queue_id":queue_id,
            "campaign_id":"pc2-"+sha256_text(key)[:24],
            "owner_role":role,
            "owner_slot":slot,
            "owner_branch":branch,
            "campaign_key":key,
            "work_buckets":json.dumps(buckets,separators=(",",":")),
            "source_units":source_units_json,
            "member_count":str(len(tags)),
            "member_ids/tags":json.dumps(tags,ensure_ascii=False,separators=(",",":")),
            "priority":priority,
            "queue_fingerprint":qfp,
        })
    return sorted(rows,key=lambda r:(r["owner_role"],r["owner_slot"],r["priority"],-int(r["member_count"]),r["campaign_key"]))

def main() -> None:
    if not UNITS.exists() or not CLOSURE.exists():
        raise SystemExit("run scripts/issue180/run_issue180_v3.py first")
    cfg=config()
    rows=build_campaigns(read_csv(UNITS),read_csv(CLOSURE),cfg)
    write_csv(CAMPAIGNS,rows,FIELDS)
    by_owner={}
    members_by_owner={}
    for r in rows:
        by_owner[r["owner_branch"]]=by_owner.get(r["owner_branch"],0)+1
        members_by_owner[r["owner_branch"]]=members_by_owner.get(r["owner_branch"],0)+int(r["member_count"])
    summary={
        "queue_id":rows[0]["queue_id"] if rows else "",
        "campaign_count":len(rows),
        "campaign_counts_by_owner":dict(sorted(by_owner.items())),
        "member_counts_by_owner":dict(sorted(members_by_owner.items())),
        "positive_evidence_global_sha_bound":False,
        "terminal_review_exact_fingerprint_required":True,
    }
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
