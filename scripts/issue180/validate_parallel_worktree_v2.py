#!/usr/bin/env python3
"""Issue #180 v2 branch/write-scope and authority-batch guard."""
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import ROOT
from build_parallel_campaigns_v2 import owner_slot

CONFIG=ROOT/"docs/issue180/parallel/PARALLEL_EXECUTION_V2.json"

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
        raise SystemExit(f"missing {remote}; fetch canonical before guard")
    base=run("merge-base","HEAD",remote)
    return {x for x in run("diff","--name-only",base+"..HEAD").splitlines() if x}

def require_latest_canonical_ancestor(canonical: str) -> None:
    remote=f"origin/{canonical}"
    p=subprocess.run(["git","merge-base","--is-ancestor",remote,"HEAD"],cwd=ROOT,text=True,capture_output=True)
    if p.returncode:
        raise SystemExit("QA Worktree must contain latest canonical before integration")

RELATION_CONTRACTS={
    ("Character","DIRECT_HOME","Copyright"),
    ("Family","FAMILY_HOME","Copyright"),
    ("Character","MEMBER_OF","Family"),
    ("Character","VARIANT_OF","Character"),
}

def validate_batch(data: dict, slot: int, path: Path, slots: int) -> None:
    required={"schema_version","proposal_id","campaign_key","campaign_fingerprint","worker_slot","batch_type","source_url","source_claim",
              "authority_type","evidence_basis","relations","terminal_reviews","notes"}
    missing=required-set(data)
    if missing:
        raise SystemExit(f"{path}: missing {sorted(missing)}")
    if data["schema_version"]!=2:
        raise SystemExit(f"{path}: schema_version must be 2")
    if int(data["worker_slot"])!=slot:
        raise SystemExit(f"{path}: worker_slot mismatch")
    key=str(data["campaign_key"]).strip()
    if not key or owner_slot(key,slots)!=slot:
        raise SystemExit(f"{path}: campaign_key is owned by another Forward lane")
    cfp=str(data["campaign_fingerprint"]).strip().lower()
    if len(cfp)!=64 or any(ch not in "0123456789abcdef" for ch in cfp):
        raise SystemExit(f"{path}: campaign_fingerprint must be sha256 hex")
    if not isinstance(data["relations"],list) or not isinstance(data["terminal_reviews"],list):
        raise SystemExit(f"{path}: relations/terminal_reviews must be arrays")
    btype=data["batch_type"]
    if btype=="AUTHORITY_BATCH":
        if not str(data["source_url"]).startswith(("https://","http://")):
            raise SystemExit(f"{path}: AUTHORITY_BATCH requires checked http(s) source")
        if len(str(data["source_claim"]).strip())<35:
            raise SystemExit(f"{path}: source_claim too short")
        if not str(data["authority_type"]).strip() or not str(data["evidence_basis"]).strip():
            raise SystemExit(f"{path}: authority_type/evidence_basis required")
        if not data["relations"] or data["terminal_reviews"]:
            raise SystemExit(f"{path}: AUTHORITY_BATCH requires relations and no terminal_reviews")
        for rel in data["relations"]:
            req={"subject_type","subject_key","relation_type","object_type","object_key"}
            if req-set(rel):
                raise SystemExit(f"{path}: relation missing {sorted(req-set(rel))}")
            actual=(rel["subject_type"],rel["relation_type"],rel["object_type"])
            if actual not in RELATION_CONTRACTS:
                raise SystemExit(f"{path}: invalid relation contract {actual}")
            if not str(rel["subject_key"]).strip() or not str(rel["object_key"]).strip():
                raise SystemExit(f"{path}: blank relation subject/object")
    elif btype=="TERMINAL_BATCH":
        if data["relations"] or not data["terminal_reviews"]:
            raise SystemExit(f"{path}: TERMINAL_BATCH requires terminal_reviews and no relations")
        for review in data["terminal_reviews"]:
            req={"unit_id","member_ids_sha256","terminal_status","authority_source","review_provenance"}
            if req-set(review):
                raise SystemExit(f"{path}: terminal review missing {sorted(req-set(review))}")
            if review["terminal_status"] not in {"PARTIALLY_RESOLVED","NO_SAFE_EVIDENCE"}:
                raise SystemExit(f"{path}: Forward may not propose terminal status {review['terminal_status']}")
            if not str(review["unit_id"]).startswith("ru3-") or len(str(review["member_ids_sha256"]))!=64:
                raise SystemExit(f"{path}: terminal review requires exact unit/fingerprint")
            if len(str(review["review_provenance"]).strip())<20:
                raise SystemExit(f"{path}: terminal review provenance too short")
    elif btype=="RESEARCH_OUTCOME":
        routes=data.get("checked_routes")
        scope=str(data.get("outcome_scope","")).strip()
        if scope not in {"PARTIAL","EXHAUSTIVE"}:
            raise SystemExit(f"{path}: RESEARCH_OUTCOME requires outcome_scope PARTIAL or EXHAUSTIVE")
        if data["relations"] or data["terminal_reviews"] or len(str(data["notes"]).strip())<20:
            raise SystemExit(f"{path}: RESEARCH_OUTCOME requires concrete notes and no relations/reviews")
        if not isinstance(routes,list) or not routes or len(routes)>5:
            raise SystemExit(f"{path}: RESEARCH_OUTCOME requires 1..5 checked_routes")
        for route in routes:
            req={"route_type","url_or_query","result"}
            if not isinstance(route,dict) or req-set(route) or not all(str(route[k]).strip() for k in req):
                raise SystemExit(f"{path}: invalid checked_routes entry")
    elif btype=="TECHNICAL_ESCALATION":
        if data["relations"] or data["terminal_reviews"] or len(str(data["notes"]).strip())<20:
            raise SystemExit(f"{path}: TECHNICAL_ESCALATION requires concrete notes only")
    else:
        raise SystemExit(f"{path}: invalid batch_type {btype}")

def validate_forward(slot: int, prefix: str, cfg: dict) -> None:
    root=ROOT/prefix
    if not root.exists():
        return
    seen=set()
    for path in sorted(root.glob("*.json")):
        data=json.loads(path.read_text(encoding="utf-8"))
        batches=data if isinstance(data,list) else [data]
        for batch in batches:
            pid=str(batch.get("proposal_id",""))
            if not pid or pid in seen:
                raise SystemExit(f"{path}: duplicate/blank proposal_id {pid}")
            seen.add(pid)
            validate_batch(batch,slot,path,int(cfg["forward_slots"]))

def main() -> None:
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    br=branch_name()
    canonical=cfg["canonical_branch"]
    if br==canonical:
        print("Issue180 v2 guard PASS: canonical")
        return
    changed=changed_from_canonical(canonical)
    if br in cfg["forward_branches"]:
        slot=cfg["forward_branches"].index(br)
        prefix=f"{cfg['proposal_root']}/fwd-{slot}/"
        bad=sorted(p for p in changed if not p.startswith(prefix))
        if bad:
            raise SystemExit("Forward v2 write-scope violation:\n"+"\n".join("  "+p for p in bad))
        validate_forward(slot,prefix,cfg)
        print(f"Issue180 v2 guard PASS: Forward {slot}; latest-canonical ancestry intentionally not required")
        return
    if br==cfg["qa_branch"]:
        require_latest_canonical_ancestor(canonical)
        proposal_prefix=cfg["proposal_root"]+"/"
        bad=sorted(p for p in changed if p.startswith(proposal_prefix))
        if bad:
            raise SystemExit("QA must not edit Forward proposal-v2 files:\n"+"\n".join("  "+p for p in bad))
        print("Issue180 v2 guard PASS: QA contains latest canonical")
        return
    raise SystemExit(f"unrecognized Issue180 v2 branch: {br}")

if __name__=="__main__":
    main()
