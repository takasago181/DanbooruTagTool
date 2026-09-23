#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

COUNT=31_003

FIELDS=[
    "review_seq","identity_key","manual_seen","semantic_summary_ja","discovery_mode",
    "route_1_id","route_1_strength","route_1_reason_ja",
    "route_2_id","route_2_strength","route_2_reason_ja",
    "route_3_id","route_3_strength","route_3_reason_ja",
    "local_refinement_ids","body_site_ids","theme_ids",
    "route_vocabulary_gap","route_vocabulary_gap_note",
    "review_depth","evidence_urls","uncertainty_note"
]

def write_neutral(path: Path):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["review_seq","identity_key","source_surfaces"],lineterminator="\n")
        w.writeheader()
        for i in range(1,COUNT+1):
            ident=f"synthetic_identity_{i:05d}"
            w.writerow({"review_seq":i,"identity_key":ident,"source_surfaces":json.dumps([ident])})

def base_row(seq: int, ident: str):
    return {
        "review_seq":str(seq),"identity_key":ident,"manual_seen":"YES",
        "semantic_summary_ja":"synthetic semantic fixture","discovery_mode":"BROWSE_WORTHY",
        "route_1_id":"ACTION_CONTACT","route_1_strength":"CORE","route_1_reason_ja":"synthetic route fixture",
        "route_2_id":"","route_2_strength":"","route_2_reason_ja":"",
        "route_3_id":"","route_3_strength":"","route_3_reason_ja":"",
        "local_refinement_ids":"[]","body_site_ids":"[]","theme_ids":"[]",
        "route_vocabulary_gap":"NO","route_vocabulary_gap_note":"",
        "review_depth":"CHECKED","evidence_urls":"[]","uncertainty_note":""
    }

def write_ledger(path: Path, rows, fields=FIELDS):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow(row)

def sha256_file(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def neutral_order_sha(path: Path):
    with path.open("r",encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    payload="".join(r["identity_key"]+"\n" for r in rows).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def run(validator: Path, neutral: Path, ledger: Path, contract: Path | None = None, *extra):
    cmd=[sys.executable,str(validator),"--input",str(neutral),"--ledger",str(ledger)]
    if contract is not None:
        cmd += ["--contract-manifest",str(contract)]
    cmd += list(extra)
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8")

def expect(result, code: int, label: str):
    if result.returncode != code:
        print(f"{label}: expected exit {code}, got {result.returncode}")
        print(result.stdout)
        raise SystemExit(1)

def main():
    root=Path(__file__).resolve().parents[2]
    validator=root/"scripts/issue132/validate_luna_pass_a.py"
    with tempfile.TemporaryDirectory(prefix="issue132-validator-") as td:
        temp=Path(td)
        neutral=temp/"neutral.csv"
        ledger=temp/"ledger.csv"
        write_neutral(neutral)
        neutral_manifest=temp/"neutral.manifest.json"
        neutral_manifest.write_text(json.dumps({
            "schema_version":"issue132-luna-neutral-v2",
            "authority":"synthetic",
            "authority_sha256":"synthetic",
            "identity_count":COUNT,
            "identity_order_sha256":neutral_order_sha(neutral),
            "output_sha256":sha256_file(neutral)
        },indent=2)+"\n",encoding="utf-8")
        contract=temp/"contract.json"
        builder=root/"scripts/issue132/build_pass_a_contract_manifest.py"
        built=subprocess.run(
            [sys.executable,str(builder),"--neutral",str(neutral),
             "--neutral-manifest",str(neutral_manifest),"--out",str(contract)],
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8")
        expect(built,0,"contract-build")

        # Empty exact-header ledger is a valid resumable starting state.
        write_ledger(ledger,[])
        expect(run(validator,neutral,ledger,contract),0,"empty-ledger")

        # Valid continuous prefix with distinct semantic modes.
        row1=base_row(1,"synthetic_identity_00001")
        row2=base_row(2,"synthetic_identity_00002")
        row2.update({
            "discovery_mode":"SEARCH_ORIENTED",
            "route_1_id":"","route_1_strength":"","route_1_reason_ja":"",
        })
        write_ledger(ledger,[row1,row2])
        valid=run(validator,neutral,ledger)
        expect(valid,0,"valid-prefix")
        if '"reviewed_count": 2' not in valid.stdout:
            print(valid.stdout); raise SystemExit("valid-prefix summary mismatch")

        # Completion is a separate explicit gate.
        expect(run(validator,neutral,ledger,contract,"--require-complete"),1,"incomplete-completion-gate")

        # Invalid route must fail.
        bad=base_row(1,"synthetic_identity_00001")
        bad["route_1_id"]="INVENTED_ROUTE"
        write_ledger(ledger,[bad])
        expect(run(validator,neutral,ledger,contract),1,"invented-route")

        # Valid local refinement requires its selected parent route.
        local_ok=base_row(1,"synthetic_identity_00001")
        local_ok["local_refinement_ids"]=json.dumps(["ACTION_CONTACT/INTIMATE"])
        write_ledger(ledger,[local_ok])
        expect(run(validator,neutral,ledger),0,"valid-local-refinement")

        # Local refinement with the wrong parent route must fail.
        local_bad=base_row(1,"synthetic_identity_00001")
        local_bad["route_1_id"]="BODY_SITE"
        local_bad["local_refinement_ids"]=json.dumps(["ACTION_CONTACT/INTIMATE"])
        write_ledger(ledger,[local_bad])
        expect(run(validator,neutral,ledger),1,"local-parent-mismatch")

        # Skipping review_seq 1 must fail exact-prefix validation.
        skipped=base_row(2,"synthetic_identity_00002")
        write_ledger(ledger,[skipped])
        expect(run(validator,neutral,ledger),1,"skipped-prefix")

        # RESEARCHED must cite evidence actually used.
        researched=base_row(1,"synthetic_identity_00001")
        researched["review_depth"]="RESEARCHED"
        write_ledger(ledger,[researched])
        expect(run(validator,neutral,ledger),1,"researched-without-evidence")

        # Frozen contract drift must fail before semantic continuation.
        tampered=temp/"contract-tampered.json"
        cm=json.loads(contract.read_text(encoding="utf-8"))
        first_key=next(iter(cm["contract_files_sha256"]))
        cm["contract_files_sha256"][first_key]="0"*64
        tampered.write_text(json.dumps(cm,indent=2)+"\n",encoding="utf-8")
        write_ledger(ledger,[base_row(1,"synthetic_identity_00001")])
        expect(run(validator,neutral,ledger,tampered),1,"contract-drift")

        # Invalid header must fail even with zero data rows.
        write_ledger(ledger,[],fields=FIELDS[:-1])
        expect(run(validator,neutral,ledger),1,"header-mismatch")

    print("PASS Issue132 Luna Pass A validator contract smoke")

if __name__=="__main__":
    main()
