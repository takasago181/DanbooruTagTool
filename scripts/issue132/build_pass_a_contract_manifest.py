#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_FILES = [
    "docs/issue132/CURRENT_RECOMMENDED_DIRECTION.md",
    "docs/issue132/FULL_SEMANTIC_REVIEW_PROTOCOL.md",
    "docs/issue132/LUNA_NEUTRAL_INPUT_CONTRACT.md",
    "docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md",
    "docs/issue132/LUNA_PASS_A_LEDGER_CONTRACT.md",
    "docs/issue132/LUNA_PARALLEL_AUTOMATION_PROTOCOL.md",
    "scripts/issue132/build_luna_neutral_input.py",
    "scripts/issue132/build_pass_a_contract_manifest.py",
    "scripts/issue132/check_review_vocabulary_against_code.py",
    "scripts/issue132/validate_luna_lane.py",
    "scripts/issue132/validate_luna_pass_a.py",
    "src/DanbooruTagTool.Core/UnifiedBrowse.cs",
    "src/DanbooruTagTool.Core/SpecialBrowseV2.cs",
    "docs/issue64/production_candidate/general_taxonomy.json",
]

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_validator():
    path=ROOT/"scripts/issue132/validate_luna_pass_a.py"
    spec=importlib.util.spec_from_file_location("issue132_validator_contract", path)
    if spec is None or spec.loader is None:
        raise SystemExit("unable to load validator module")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git","rev-parse","HEAD"], cwd=ROOT, text=True, encoding="utf-8"
        ).strip()
    except Exception:
        return ""

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--neutral", required=True, help="luna_neutral_review_input_v2.csv")
    ap.add_argument("--neutral-manifest", required=True)
    ap.add_argument("--out", required=True)
    args=ap.parse_args()

    neutral=Path(args.neutral)
    neutral_manifest_path=Path(args.neutral_manifest)
    out=Path(args.out)

    neutral_manifest=json.loads(neutral_manifest_path.read_text(encoding="utf-8"))
    if neutral_manifest.get("identity_count") != 31_003:
        raise SystemExit("neutral manifest identity count mismatch")
    if sha256_file(neutral) != neutral_manifest.get("output_sha256"):
        raise SystemExit("neutral CSV SHA does not match neutral manifest")

    v=load_validator()
    files={}
    for rel in CONTRACT_FILES:
        p=ROOT/rel
        if not p.is_file():
            raise SystemExit(f"missing contract file: {rel}")
        files[rel]=sha256_file(p)

    manifest={
        "schema_version":"issue132-pass-a-contract-v1",
        "created_from_commit":git_head(),
        "population":31_003,
        "execution_model":"continuous_exact_prefix",
        "neutral":{
            "schema_version":neutral_manifest.get("schema_version"),
            "authority":neutral_manifest.get("authority"),
            "authority_sha256":neutral_manifest.get("authority_sha256"),
            "identity_count":neutral_manifest.get("identity_count"),
            "identity_order_sha256":neutral_manifest.get("identity_order_sha256"),
            "output_sha256":neutral_manifest.get("output_sha256"),
        },
        "contract_files_sha256":files,
        "ledger_fields":list(v.FIELDS),
        "route_ids":sorted(v.ROUTES),
        "local_refinement_parent":dict(sorted(v.LOCAL_PARENT.items())),
        "body_site_ids":sorted(v.BODY),
        "theme_ids":sorted(v.THEMES),
        "allowed_discovery_modes":sorted(v.MODES),
        "allowed_route_strengths":sorted(v.STRENGTHS),
        "allowed_review_depths":sorted(v.DEPTHS),
        "rule":"If any frozen contract hash/vocabulary changes during Pass A, do not silently continue the ledger. Reconcile the contract change first."
    }

    out.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(manifest,ensure_ascii=False,indent=2)+"\n"
    out.write_text(text,encoding="utf-8")
    print(text,end="")

if __name__=="__main__":
    main()
