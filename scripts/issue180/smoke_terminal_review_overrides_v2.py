#!/usr/bin/env python3
"""Integration smoke for terminal-review overrides in Issue #180 v2."""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

R=Path(__file__).resolve().parents[2]
D=R/"artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2"
LEDGER=D/"APPLIED_AUTHORITY_LEDGER_V2.csv"
MASTER=D/"CHARACTER_HOME_MASTER_V2.csv"
SHARD=R/"docs/issue180/autonomous/decisions/__SMOKE_terminal_override_v2.csv"
VALIDATOR=R/"scripts/issue180/validate_authority_decisions_v2.py"
COMPILER=R/"scripts/issue180/compile_character_home_v2.py"
FIELDS=[
 "scope","key","home_copyright","base_character","authority_type","evidence_url",
 "evidence_claim","validation_state","officiality_state","notes",
]


def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def write(rows):
    with SHARD.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def run(path):
    subprocess.run([sys.executable,str(path)],cwd=R,check=True)


def master_row(tag):
    rows={r["canonical_tag"]:r for r in read(MASTER)}
    if tag not in rows:
        raise SystemExit(f"smoke Character missing from master: {tag}")
    return rows[tag]


def restore():
    SHARD.unlink(missing_ok=True)
    run(VALIDATOR)
    run(COMPILER)


def main():
    if SHARD.exists():
        raise SystemExit(f"unexpected stale smoke shard: {SHARD}")

    applied=read(LEDGER)
    candidate=next(
        (
            r for r in applied
            if r.get("authority_scope")=="FAMILY_QUALIFIER"
            and r.get("family")
            and r.get("canonical_tag")
            and r.get("home_copyright")
        ),
        None,
    )
    if not candidate:
        raise SystemExit("no FAMILY_QUALIFIER-confirmed row available for terminal override smoke")

    tag=candidate["canonical_tag"]
    family=candidate["family"]
    baseline_home=candidate["home_copyright"]
    before=master_row(tag)
    if before.get("final_state")!="HOME_CONFIRMED" or before.get("home_copyright")!=baseline_home:
        raise SystemExit(f"unexpected baseline for {tag}: {before}")

    try:
        write([{
            "scope":"FAMILY_QUALIFIER",
            "key":family,
            "home_copyright":"",
            "base_character":"",
            "authority_type":"",
            "evidence_url":"https://example.com/issue180-family-terminal-override-smoke",
            "evidence_claim":"Synthetic external smoke evidence exercises a reviewed family-level terminal hold.",
            "validation_state":"NEEDS_HIGHER_REASONING",
            "officiality_state":"",
            "notes":"Integration smoke intentionally defers this family to prove an existing inherited HOME is suppressed.",
        }])
        run(VALIDATOR)
        run(COMPILER)
        family_after=master_row(tag)
        if family_after.get("final_state")!="HOME_UNRESOLVED" or family_after.get("home_copyright"):
            raise SystemExit(
                f"terminal family review failed to suppress inherited HOME for {tag}: {family_after}"
            )
        print(f"family terminal override: PASS {tag} family={family}")

        restore()
        restored=master_row(tag)
        if restored.get("final_state")!="HOME_CONFIRMED" or restored.get("home_copyright")!=baseline_home:
            raise SystemExit(f"baseline restore failed after family smoke for {tag}: {restored}")

        write([{
            "scope":"BLOCK_CHARACTER",
            "key":tag,
            "home_copyright":"",
            "base_character":"",
            "authority_type":"",
            "evidence_url":"https://example.com/issue180-character-terminal-override-smoke",
            "evidence_claim":"Synthetic external smoke evidence exercises a reviewed Character-level HOME hold.",
            "validation_state":"NEEDS_HIGHER_REASONING",
            "officiality_state":"",
            "notes":"Integration smoke intentionally blocks this Character to prove all HOME inheritance paths are suppressed.",
        }])
        run(VALIDATOR)
        run(COMPILER)
        block_after=master_row(tag)
        if block_after.get("final_state")!="HOME_UNRESOLVED" or block_after.get("home_copyright"):
            raise SystemExit(
                f"terminal Character review failed to suppress HOME for {tag}: {block_after}"
            )
        print(f"character terminal override: PASS {tag}")
    finally:
        restore()

    restored=master_row(tag)
    if restored.get("final_state")!="HOME_CONFIRMED" or restored.get("home_copyright")!=baseline_home:
        raise SystemExit(f"final baseline restore failed for {tag}: {restored}")

    print("Issue #180 terminal-review override integration smoke: PASS")


if __name__=="__main__":
    main()
