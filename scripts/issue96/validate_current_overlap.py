#!/usr/bin/env python3
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

EXPECTED_ROWS = 195
EXPECTED_STATUS = "GENERAL_ONLY_GAP"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--proposal", required=True)
    p.add_argument("--inventory", required=True)
    p.add_argument("--scan-summary", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--summary", required=True)
    a = p.parse_args()

    with Path(a.proposal).open("r", encoding="utf-8-sig", newline="") as f:
        proposal = list(csv.DictReader(f))
    with Path(a.inventory).open("r", encoding="utf-8-sig", newline="") as f:
        inventory_rows = list(csv.DictReader(f))
    scan_summary = json.loads(Path(a.scan_summary).read_text(encoding="utf-8"))

    if len(proposal) != EXPECTED_ROWS:
        raise SystemExit(f"proposal row drift: {len(proposal)} != {EXPECTED_ROWS}")
    canonicals = [r["canonical_tag"] for r in proposal]
    if len(set(canonicals)) != EXPECTED_ROWS:
        raise SystemExit("duplicate canonical in proposal")

    inventory = {r["canonical"]: r for r in inventory_rows}
    if len(inventory) != len(inventory_rows):
        raise SystemExit("duplicate canonical in scanner inventory")

    problems = []
    status_counts = Counter()
    for row in proposal:
        tag = row["canonical_tag"]
        inv = inventory.get(tag)
        if inv is None:
            problems.append((tag, "MISSING_FROM_CURRENT_INVENTORY"))
            continue
        status = inv["identity_status"]
        status_counts[status] += 1
        if status != EXPECTED_STATUS:
            problems.append((tag, f"IDENTITY_STATUS={status}; evidence={inv.get('identity_evidence','')}"))
            continue
        if int(inv["post_count"]) != int(row["post_count"]):
            problems.append((tag, f"POST_COUNT_DRIFT={inv['post_count']} != {row['post_count']}"))
            continue

        row["duplicate_guard"] = "PASS_GENERAL_ONLY_GAP_CURRENT_SPECIAL_2788"
        row["validation_status"] = "IDENTITY_LAYER_TAXONOMY_DUPLICATE_READY"

    if problems:
        details = "\n".join(f"- {tag}: {why}" for tag, why in problems[:50])
        raise SystemExit(f"current Special overlap validation failed ({len(problems)} rows):\n{details}")

    if status_counts != Counter({EXPECTED_STATUS: EXPECTED_ROWS}):
        raise SystemExit(f"unexpected status distribution: {dict(status_counts)}")

    special_rows = scan_summary.get("special_rows")
    unresolved = scan_summary.get("special_profile_unresolved_identity_rows")
    identity_counts = scan_summary.get("identity_status_counts", {})
    if special_rows != 2788:
        raise SystemExit(f"current Special population drift: {special_rows} != 2788")
    if unresolved != 0:
        raise SystemExit(f"current Special unresolved identity rows: {unresolved}")
    if identity_counts.get("GENERAL_ONLY_GAP") != 29021:
        raise SystemExit(f"General-only population drift: {identity_counts}")

    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(proposal[0])
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(proposal)

    lines = [
        "# Issue #96 duplicate / identity validation summary v1",
        "",
        "Status: **195/195 CURRENT-SPECIAL CLOSURE PASS / JA PENDING / NO PRODUCTION MUTATION**",
        "",
        f"- proposal rows checked: **{len(proposal)}**",
        f"- `GENERAL_ONLY_GAP`: **{status_counts[EXPECTED_STATUS]}**",
        "- `PRESENT_EXACT`: **0**",
        "- `PRESENT_CANONICAL_TARGET`: **0**",
        "- missing from current inventory: **0**",
        "- post-count drift: **0**",
        f"- current Special rows: **{special_rows}**",
        f"- current Special unresolved identity rows: **{unresolved}**",
        f"- current full General-only gap population: **{identity_counts.get('GENERAL_ONLY_GAP')}**",
        "",
        "## Meaning",
        "",
        "The frozen 195 Issue #94 candidates were rechecked with the pinned Issue #94 canonical/alias-closure scanner against the current tracked Special 2,788 generation profile. Every candidate still resolves as a true General-only identity gap. No candidate became an exact Special identity or a canonical target through the current alias closure.",
        "",
        "This validates identity non-overlap only. It does not itself promote rows into production Special and does not certify Japanese metadata.",
        "",
        "`CONTENT_FILTER_USED=NO`  ",
        "`PRODUCTION_FILES_CHANGED=NO`  ",
        "`ISSUE70_MUTATED=NO`",
        "",
    ]
    Path(a.summary).write_text("\n".join(lines), encoding="utf-8")
    print(f"ISSUE96_DUPLICATE_VALIDATION_PASS rows={len(proposal)} status={EXPECTED_STATUS} collisions=0")


if __name__ == "__main__":
    main()
