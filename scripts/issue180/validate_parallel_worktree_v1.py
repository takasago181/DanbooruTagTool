#!/usr/bin/env python3
"""Branch/write-ownership guard for Issue #180 parallel Worktrees."""
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import OUT, ROOT, read_csv
from build_parallel_assignment_v1 import owner_slot

CONFIG = ROOT / "docs/issue180/parallel/PARALLEL_EXECUTION_V1.json"
ASSIGNMENTS = OUT / "parallel_assignments_v1.csv"
QA_LEDGER = ROOT / "docs/issue180/parallel/QA_REVIEW_LEDGER_V1.csv"

def run(*args: str, check: bool=True) -> str:
    p=subprocess.run(["git",*args],cwd=ROOT,text=True,capture_output=True)
    if check and p.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout.strip()

def branch_name() -> str:
    return os.environ.get("GITHUB_REF_NAME","").strip() or run("branch","--show-current")

def changed_from_canonical(canonical: str) -> set[str]:
    remote=f"origin/{canonical}"
    if not run("rev-parse","--verify",remote,check=False):
        raise SystemExit(f"missing {remote}; fetch canonical branch before guard")
    base=run("merge-base","HEAD",remote)
    return {x for x in run("diff","--name-only",base+"..HEAD").splitlines() if x}

def load_ingested_ids() -> set[str]:
    if not QA_LEDGER.exists():
        return set()
    return {r.get("proposal_id","") for r in read_csv(QA_LEDGER) if r.get("proposal_id")}

def validate_forward_proposals(slot: int, prefix: str, cfg: dict) -> None:
    if not ASSIGNMENTS.exists():
        raise SystemExit("parallel assignment manifest missing; run v3 then build_parallel_assignment_v1.py")
    assignments={r["assignment_id"]:r for r in read_csv(ASSIGNMENTS) if r["owner_role"]=="FORWARD" and r["owner_slot"]==str(slot)}
    ingested=load_ingested_ids()
    root=ROOT/prefix
    if not root.exists():
        return
    required={"proposal_id","assignment_id","epoch_id","canonical_base_sha","unit_id","source_member_ids_sha256",
              "assignment_member_ids_sha256","ownership_key","work_bucket","worker_slot","proposal_type",
              "source_url","source_claim","payload"}
    seen=set()
    for path in sorted(root.glob("*.json")):
        data=json.loads(path.read_text(encoding="utf-8"))
        proposals=data if isinstance(data,list) else [data]
        for p in proposals:
            missing=required-set(p)
            if missing: raise SystemExit(f"{path}: proposal missing {sorted(missing)}")
            pid=str(p["proposal_id"])
            if not pid or pid in seen: raise SystemExit(f"duplicate/blank proposal_id: {pid}")
            seen.add(pid)
            if pid in ingested:
                continue
            a=assignments.get(str(p["assignment_id"]))
            if not a: raise SystemExit(f"{path}: stale/unowned assignment {p['assignment_id']}")
            checks={
                "epoch_id":"epoch_id","canonical_base_sha":"canonical_base_sha","unit_id":"source_unit_id",
                "source_member_ids_sha256":"source_member_ids_sha256",
                "assignment_member_ids_sha256":"assignment_member_ids_sha256",
                "ownership_key":"ownership_key","work_bucket":"work_bucket",
            }
            for pk,ak in checks.items():
                if str(p[pk])!=a[ak]: raise SystemExit(f"{path}: {pk} does not match current assignment")
            if int(p["worker_slot"])!=slot or owner_slot(a["ownership_key"],int(cfg["forward_slots"]))!=slot:
                raise SystemExit(f"{path}: worker ownership mismatch")
            if p["proposal_type"] not in {"EVIDENCE_DIRECT_HOME","EVIDENCE_FAMILY_HOME","EVIDENCE_MEMBER_OF",
                                         "EVIDENCE_VARIANT_OF","TERMINAL_REVIEW","SUPERSESSION","TECHNICAL_ESCALATION"}:
                raise SystemExit(f"{path}: invalid proposal_type {p['proposal_type']}")
            if p["proposal_type"].startswith("EVIDENCE_"):
                if not str(p["source_url"]).startswith(("https://","http://")):
                    raise SystemExit(f"{path}: evidence proposal requires checked http(s) source")
                if len(str(p["source_claim"]).strip())<35:
                    raise SystemExit(f"{path}: evidence source_claim too short")

def main() -> None:
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    br=branch_name()
    canonical=cfg["canonical_branch"]
    if br==canonical:
        print("Issue180 parallel guard PASS: canonical branch; single-writer enforcement is role contract + QA ledger")
        return
    changed=changed_from_canonical(canonical)
    if br in cfg["forward_branches"]:
        slot=cfg["forward_branches"].index(br)
        prefix=f"{cfg['proposal_root']}/fwd-{slot}/"
        bad=sorted(p for p in changed if not p.startswith(prefix))
        if bad:
            raise SystemExit("forward Worktree write-scope violation:\n"+"\n".join("  "+p for p in bad))
        validate_forward_proposals(slot,prefix,cfg)
        print(f"Issue180 parallel guard PASS: forward slot={slot} changed={len(changed)}")
        return
    if br==cfg["qa_branch"]:
        proposal_prefix=cfg["proposal_root"]+"/"
        bad=sorted(p for p in changed if p.startswith(proposal_prefix))
        if bad:
            raise SystemExit("QA must not edit worker proposal branches/files:\n"+"\n".join("  "+p for p in bad))
        print(f"Issue180 parallel guard PASS: QA/integrator changed={len(changed)}")
        return
    raise SystemExit(f"unrecognized Issue180 parallel branch: {br}")

if __name__=="__main__":
    main()
