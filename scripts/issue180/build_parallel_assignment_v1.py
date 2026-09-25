#!/usr/bin/env python3
"""Build deterministic Issue #180 parallel ownership assignments from the current v3 OPEN-unit census."""
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import OUT, ROOT, read_csv, write_csv, sha256_text

CONFIG = ROOT / "docs/issue180/parallel/PARALLEL_EXECUTION_V1.json"
UNITS = OUT / "research_units_v3.csv"
CLOSURE = ROOT / "docs/issue180/v3/reports/RESEARCH_UNIT_CLOSURE_SWEEP_V3.csv"
ASSIGNMENTS = OUT / "parallel_assignments_v1.csv"
SUMMARY = OUT / "parallel_assignments_summary_v1.json"
FIELDS = [
    "epoch_id","assignment_id","owner_role","owner_slot","owner_branch","work_bucket",
    "ownership_key","source_unit_id","source_member_ids_sha256","assignment_member_ids_sha256",
    "unit_type","subject","priority","member_count","member_ids/tags","canonical_base_sha",
]

def config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))

def git_output(*args: str) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    return p.stdout.strip() if p.returncode == 0 else ""

def canonical_sha(cfg: dict) -> str:
    env = os.environ.get("ISSUE180_CANONICAL_SHA", "").strip()
    if env:
        return env
    remote = git_output("rev-parse", f"origin/{cfg['canonical_branch']}")
    return remote or git_output("rev-parse", "HEAD")

def owner_slot(ownership_key: str, slots: int) -> int:
    return int(sha256_text(ownership_key)[:16], 16) % slots

def member_hash(tags: list[str]) -> str:
    return sha256_text("\n".join(sorted(tags)))

def stable_ownership_key(unit: dict[str,str], tag: str | None = None) -> str:
    subject = unit["subject"]
    if tag is not None:
        return "direct:" + tag
    if subject and subject != "__UNGROUPED__":
        return subject
    return "unit:" + unit["unit_id"]

def build_assignments(units: list[dict[str,str]], closures: list[dict[str,str]], cfg: dict, base_sha: str) -> list[dict[str,str]]:
    by_id = {u["unit_id"]: u for u in units}
    forward = set(cfg["forward_buckets"])
    qa = set(cfg["qa_buckets"])
    slots = int(cfg["forward_slots"])
    branches = cfg["forward_branches"]
    raw_items: list[dict[str,object]] = []
    for closure in closures:
        uid = closure["unit_id"]
        unit = by_id.get(uid)
        if not unit or unit.get("status") != "OPEN":
            raise SystemExit(f"closure row is not an exact current OPEN unit: {uid}")
        bucket = closure["work_bucket"]
        if bucket not in forward | qa:
            raise SystemExit(f"unowned work_bucket: {bucket}")
        tags = json.loads(unit["member_ids/tags"])
        if closure["member_ids_sha256"] != member_hash(tags):
            raise SystemExit(f"closure fingerprint drift: {uid}")
        if bucket in forward and unit["subject"] == "__UNGROUPED__" and len(tags) > 1:
            for tag in tags:
                raw_items.append({"closure": closure, "unit": unit, "tags": [tag], "key": stable_ownership_key(unit, tag)})
        else:
            raw_items.append({"closure": closure, "unit": unit, "tags": tags, "key": stable_ownership_key(unit)})
    census_fingerprint = sha256_text("\n".join(
        sorted(f"{x['closure']['unit_id']}|{x['closure']['member_ids_sha256']}|{x['closure']['work_bucket']}|{x['key']}" for x in raw_items)
    ))
    epoch = "ep1-" + base_sha[:12] + "-" + census_fingerprint[:12]
    out: list[dict[str,str]] = []
    for item in raw_items:
        closure = item["closure"]; unit = item["unit"]; tags = item["tags"]; key = str(item["key"])
        bucket = closure["work_bucket"]
        if bucket in qa:
            role, slot, branch = "QA", "", cfg["qa_branch"]
        else:
            n = owner_slot(key, slots)
            role, slot, branch = "FORWARD", str(n), branches[n]
        ahash = member_hash(tags)
        aid = "pa1-" + sha256_text("\x1f".join([epoch, role, slot, bucket, key, unit["unit_id"], ahash]))[:24]
        out.append({
            "epoch_id": epoch, "assignment_id": aid, "owner_role": role, "owner_slot": slot,
            "owner_branch": branch, "work_bucket": bucket, "ownership_key": key,
            "source_unit_id": unit["unit_id"], "source_member_ids_sha256": closure["member_ids_sha256"],
            "assignment_member_ids_sha256": ahash, "unit_type": unit["unit_type"], "subject": unit["subject"],
            "priority": unit["priority"], "member_count": str(len(tags)),
            "member_ids/tags": json.dumps(tags, ensure_ascii=False, separators=(",",":")),
            "canonical_base_sha": base_sha,
        })
    return sorted(out, key=lambda r: (r["owner_role"], r["owner_slot"], r["work_bucket"], r["ownership_key"], r["assignment_id"]))

def main() -> None:
    if not UNITS.exists() or not CLOSURE.exists():
        raise SystemExit("run scripts/issue180/run_issue180_v3.py first; current v3 census is required")
    cfg = config()
    rows = build_assignments(read_csv(UNITS), read_csv(CLOSURE), cfg, canonical_sha(cfg))
    write_csv(ASSIGNMENTS, rows, FIELDS)
    by_owner: dict[str,int] = {}
    by_bucket: dict[str,int] = {}
    members_by_owner: dict[str,int] = {}
    for r in rows:
        owner = r["owner_branch"]
        by_owner[owner] = by_owner.get(owner, 0) + 1
        members_by_owner[owner] = members_by_owner.get(owner, 0) + int(r["member_count"])
        by_bucket[r["work_bucket"]] = by_bucket.get(r["work_bucket"], 0) + 1
    summary = {
        "epoch_id": rows[0]["epoch_id"] if rows else "",
        "canonical_base_sha": rows[0]["canonical_base_sha"] if rows else canonical_sha(cfg),
        "assignment_count": len(rows), "assignment_counts_by_owner": dict(sorted(by_owner.items())),
        "member_counts_by_owner": dict(sorted(members_by_owner.items())),
        "assignment_counts_by_bucket": dict(sorted(by_bucket.items())),
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
