#!/usr/bin/env python3
"""Freeze every HOME_UNRESOLVED row from the immutable Issue #180 authority master."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE_COMMIT = "9c0db59c0f1dc56402c955e718a37d9de1849d7e"
BASELINE_MASTER_SHA256 = "135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071"
BASELINE_POPULATION = 35_890
EXPECTED_UNRESOLVED = 13_983
FIELDS = ["cohort_id", "canonical_character", "baseline_state", "baseline_home"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build(master_path: Path) -> tuple[list[dict[str, str]], dict[str, object]]:
    master_sha = digest(master_path)
    if master_sha != BASELINE_MASTER_SHA256:
        raise SystemExit(f"frozen #180 master SHA mismatch: expected {BASELINE_MASTER_SHA256}, got {master_sha}")
    with master_path.open(encoding="utf-8-sig", newline="") as stream:
        master = list(csv.DictReader(stream))
    if len(master) != BASELINE_POPULATION:
        raise SystemExit(f"frozen #180 master population mismatch: expected {BASELINE_POPULATION}, got {len(master)}")
    confirmed = [row for row in master if row["final_state"] == "HOME_CONFIRMED"]
    if len(confirmed) != 21_907 or any(not row["home_copyright"] for row in confirmed):
        raise SystemExit("frozen #180 HOME_CONFIRMED count/cardinality does not match the issue baseline")
    if any(row["final_state"] not in {"HOME_CONFIRMED", "HOME_UNRESOLVED"} for row in master):
        raise SystemExit("frozen #180 master contains an unexpected terminal state")
    unresolved = [row for row in master if row["final_state"] == "HOME_UNRESOLVED"]
    if len(unresolved) != EXPECTED_UNRESOLVED:
        raise SystemExit(f"frozen #180 unresolved count mismatch: expected {EXPECTED_UNRESOLVED}, got {len(unresolved)}")
    if len({row["canonical_tag"] for row in unresolved}) != EXPECTED_UNRESOLVED:
        raise SystemExit("frozen unresolved master contains duplicate Character identities")
    unresolved.sort(key=lambda row: row["canonical_tag"])
    cohort = [{
        "cohort_id": row["canonical_tag"],
        "canonical_character": row["canonical_tag"],
        "baseline_state": "HOME_UNRESOLVED",
        "baseline_home": "",
    } for row in unresolved]
    manifest = {
        "schema_version": "issue216-authority-coverage-cohort-v1",
        "baseline_issue": 180,
        "baseline_commit": BASELINE_COMMIT,
        "baseline_master_sha256": master_sha,
        "baseline_character_population": BASELINE_POPULATION,
        "baseline_home_unresolved": EXPECTED_UNRESOLVED,
        "cohort_sha256": hashlib.sha256(
            ("\n".join(row["canonical_character"] for row in cohort) + "\n").encode("utf-8")
        ).hexdigest(),
        "cohort_order": "canonical Character ascending; deterministic identity order only",
        "scope": "Only Characters HOME_UNRESOLVED in the frozen Issue #180 master; original master is immutable.",
    }
    return cohort, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, required=True, help="frozen #180 character_home_master_v3.csv")
    parser.add_argument("--cohort", type=Path, default=ROOT / "docs/issue216/AUTHORITY_COVERAGE_COHORT_V1.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "docs/issue216/AUTHORITY_COVERAGE_COHORT_V1.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cohort, manifest = build(args.master)
    if args.check:
        with args.cohort.open(encoding="utf-8-sig", newline="") as stream:
            actual_cohort = list(csv.DictReader(stream))
        actual_manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if actual_cohort != cohort or actual_manifest != manifest:
            raise SystemExit("frozen full unresolved cohort differs from deterministic reconstruction")
        print("full unresolved cohort reproducibility: PASS (13,983 rows)")
        return
    if args.cohort.exists() or args.manifest.exists():
        raise SystemExit("refusing to overwrite frozen coverage cohort/manifest")
    args.cohort.parent.mkdir(parents=True, exist_ok=True)
    with args.cohort.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(cohort)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"frozen unresolved cohort: {len(cohort)}; master sha256={manifest['baseline_master_sha256']}")


if __name__ == "__main__":
    main()
