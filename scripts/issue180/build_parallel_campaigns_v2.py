#!/usr/bin/env python3
"""Build Issue #180 v2 reusable-authority campaigns from the current v3 residual census."""
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
LEDGER = ROOT / "docs/issue180/parallel/QA_REVIEW_LEDGER_V2.csv"
CAMPAIGNS = OUT / "parallel_authority_campaigns_v2.csv"
TERMINAL_CANDIDATES = OUT / "parallel_terminal_candidates_v2.csv"
SUMMARY = OUT / "parallel_authority_campaigns_summary_v2.json"

FIELDS = [
    "queue_id","campaign_id","owner_role","owner_slot","owner_branch","campaign_key",
    "campaign_fingerprint","research_state","work_buckets","source_units",
    "member_count","member_ids/tags","priority",
]
TERMINAL_FIELDS = [
    "unit_id","member_ids_sha256","campaign_count","exhausted_campaign_count","all_campaigns_exhausted",
]

def config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))

def owner_slot(campaign_key: str, slots: int) -> int:
    return int(sha256_text(campaign_key)[:16], 16) % slots

def member_hash(tags: list[str]) -> str:
    return sha256_text("\n".join(sorted(tags)))

def normalize_campaign_key(unit: dict[str,str], tag: str | None = None) -> str:
    """Normalize leads that can share the same reusable authority into one stable campaign key."""
    subject = unit["subject"]
    if tag is not None:
        return "direct:" + tag
    if subject.startswith("family:"):
        return "authority:" + subject.split(":", 1)[1]
    if subject.startswith("discovery-hint:"):
        return "authority:" + subject.split(":", 1)[1]
    if subject and subject != "__UNGROUPED__":
        return subject
    return "unit:" + unit["unit_id"]

def _priority_value(p: str) -> int:
    return {"P1": 1, "P2": 2, "P3": 3}.get(p, 9)

def load_research_accounting() -> tuple[set[tuple[str,str]], set[tuple[str,str]]]:
    if not LEDGER.exists():
        return set(), set()
    rows=read_csv(LEDGER)
    outcomes={
        (r.get("campaign_key",""),r.get("campaign_fingerprint",""))
        for r in rows
        if r.get("decision")=="ACCEPT_OUTCOME" and r.get("campaign_key") and r.get("campaign_fingerprint")
    }
    progress={
        (r.get("campaign_key",""),r.get("campaign_fingerprint",""))
        for r in rows
        if r.get("decision")=="ACCEPT_PROGRESS" and r.get("campaign_key") and r.get("campaign_fingerprint")
    }
    return outcomes, progress

def build_campaigns(
    units: list[dict[str,str]],
    closures: list[dict[str,str]],
    cfg: dict,
    accepted_outcomes: set[tuple[str,str]] | None = None,
    accepted_progress: set[tuple[str,str]] | None = None,
) -> list[dict[str,str]]:
    accepted_outcomes=accepted_outcomes or set()
    accepted_progress=accepted_progress or set()
    by_id={u["unit_id"]:u for u in units}
    forward=set(cfg["forward_buckets"])
    qa=set(cfg["qa_buckets"])
    slots=int(cfg["forward_slots"])
    branches=cfg["forward_branches"]
    grouped: dict[tuple[str,str], list[dict[str,object]]] = defaultdict(list)

    for closure in closures:
        uid=closure["unit_id"]
        unit=by_id.get(uid)
        if not unit or unit.get("status")!="OPEN":
            raise SystemExit(f"closure row is not an exact current OPEN unit: {uid}")
        tags=json.loads(unit["member_ids/tags"])
        if closure["member_ids_sha256"]!=member_hash(tags):
            raise SystemExit(f"closure fingerprint drift: {uid}")
        bucket=closure["work_bucket"]
        if bucket not in forward|qa:
            raise SystemExit(f"unowned work_bucket: {bucket}")

        if bucket in qa:
            key=f"qa:{bucket}:{uid}"
            grouped[("QA",key)].append({"unit":unit,"closure":closure,"tags":tags})
            continue

        if unit["subject"]=="__UNGROUPED__":
            for tag in tags:
                key=normalize_campaign_key(unit,tag)
                grouped[("FORWARD",key)].append({"unit":unit,"closure":closure,"tags":[tag]})
        else:
            key=normalize_campaign_key(unit)
            grouped[("FORWARD",key)].append({"unit":unit,"closure":closure,"tags":tags})

    queue_material=[]
    for (role,key),items in grouped.items():
        for item in items:
            queue_material.append(
                f"{role}|{key}|{item['unit']['unit_id']}|{item['closure']['member_ids_sha256']}|{','.join(sorted(item['tags']))}"
            )
    queue_id="q2-"+sha256_text("\n".join(sorted(queue_material)))[:20]

    rows=[]
    for (role,key),items in grouped.items():
        tags=sorted({t for item in items for t in item["tags"]})
        buckets=sorted({str(item["closure"]["work_bucket"]) for item in items})
        source_units=sorted({
            (str(item["unit"]["unit_id"]),str(item["closure"]["member_ids_sha256"]))
            for item in items
        })
        source_units_json=json.dumps(
            [{"unit_id":u,"member_ids_sha256":h} for u,h in source_units],
            ensure_ascii=False,separators=(",",":")
        )
        priority=min((str(item["unit"]["priority"]) for item in items),key=_priority_value)
        campaign_fp=sha256_text(key+"\n"+"\n".join(tags))
        if role=="QA":
            slot=""
            branch=cfg["qa_branch"]
            state="QA_OWNED"
        else:
            n=owner_slot(key,slots)
            slot=str(n)
            branch=branches[n]
            if (key,campaign_fp) in accepted_outcomes:
                state="EXHAUSTED_REVIEWED"
            elif (key,campaign_fp) in accepted_progress:
                state="OPEN_WITH_PROGRESS"
            else:
                state="OPEN"
        rows.append({
            "queue_id":queue_id,
            "campaign_id":"pc2-"+sha256_text(key)[:24],
            "owner_role":role,
            "owner_slot":slot,
            "owner_branch":branch,
            "campaign_key":key,
            "campaign_fingerprint":campaign_fp,
            "research_state":state,
            "work_buckets":json.dumps(buckets,separators=(",",":")),
            "source_units":source_units_json,
            "member_count":str(len(tags)),
            "member_ids/tags":json.dumps(tags,ensure_ascii=False,separators=(",",":")),
            "priority":priority,
        })
    return sorted(
        rows,
        key=lambda r:(r["owner_role"],r["owner_slot"],{"OPEN":0,"OPEN_WITH_PROGRESS":1,"EXHAUSTED_REVIEWED":2,"QA_OWNED":3}.get(r["research_state"],9),r["priority"],-int(r["member_count"]),r["campaign_key"])
    )

def build_terminal_candidates(rows, units, closures, cfg):
    forward=set(cfg["forward_buckets"])
    closure_by_id={r["unit_id"]:r for r in closures}
    campaigns_by_unit=defaultdict(list)
    for row in rows:
        if row["owner_role"]!="FORWARD":
            continue
        for src in json.loads(row["source_units"]):
            campaigns_by_unit[(src["unit_id"],src["member_ids_sha256"])].append(row)

    out=[]
    for unit in units:
        if unit.get("status")!="OPEN":
            continue
        closure=closure_by_id.get(unit["unit_id"])
        if not closure or closure["work_bucket"] not in forward:
            continue
        tags=json.loads(unit["member_ids/tags"])
        fp=member_hash(tags)
        campaigns=campaigns_by_unit.get((unit["unit_id"],fp),[])
        if not campaigns:
            continue
        exhausted=sum(r["research_state"]=="EXHAUSTED_REVIEWED" for r in campaigns)
        out.append({
            "unit_id":unit["unit_id"],
            "member_ids_sha256":fp,
            "campaign_count":str(len(campaigns)),
            "exhausted_campaign_count":str(exhausted),
            "all_campaigns_exhausted":"YES" if exhausted==len(campaigns) else "NO",
        })
    return sorted(out,key=lambda r:(r["all_campaigns_exhausted"]!="YES",r["unit_id"]))

def main() -> None:
    if not UNITS.exists() or not CLOSURE.exists():
        raise SystemExit("run scripts/issue180/run_issue180_v3.py first")
    cfg=config()
    units=read_csv(UNITS)
    closures=read_csv(CLOSURE)
    accepted_outcomes, accepted_progress=load_research_accounting()
    rows=build_campaigns(units,closures,cfg,accepted_outcomes,accepted_progress)
    write_csv(CAMPAIGNS,rows,FIELDS)
    terminal=build_terminal_candidates(rows,units,closures,cfg)
    write_csv(TERMINAL_CANDIDATES,terminal,TERMINAL_FIELDS)

    by_owner={}
    open_by_owner={}
    members_by_owner={}
    for r in rows:
        by_owner[r["owner_branch"]]=by_owner.get(r["owner_branch"],0)+1
        members_by_owner[r["owner_branch"]]=members_by_owner.get(r["owner_branch"],0)+int(r["member_count"])
        if r["research_state"] in {"OPEN","OPEN_WITH_PROGRESS"}:
            open_by_owner[r["owner_branch"]]=open_by_owner.get(r["owner_branch"],0)+1
    summary={
        "queue_id":rows[0]["queue_id"] if rows else "",
        "campaign_count":len(rows),
        "open_forward_campaign_count":sum(r["research_state"] in {"OPEN","OPEN_WITH_PROGRESS"} and r["owner_role"]=="FORWARD" for r in rows),
        "progressed_forward_campaign_count":sum(r["research_state"]=="OPEN_WITH_PROGRESS" for r in rows),
        "reviewed_exhausted_forward_campaign_count":sum(r["research_state"]=="EXHAUSTED_REVIEWED" for r in rows),
        "terminal_candidate_unit_count":sum(r["all_campaigns_exhausted"]=="YES" for r in terminal),
        "campaign_counts_by_owner":dict(sorted(by_owner.items())),
        "open_campaign_counts_by_owner":dict(sorted(open_by_owner.items())),
        "member_counts_by_owner":dict(sorted(members_by_owner.items())),
        "positive_evidence_global_sha_bound":False,
        "campaign_outcome_fingerprint_bound":True,
        "terminal_review_exact_unit_fingerprint_required":True,
    }
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
