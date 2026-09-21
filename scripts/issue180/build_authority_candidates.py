#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "artifacts/issue180-diverse-pilot/PILOT_250.csv"
OUT = ROOT / "artifacts/issue180-diverse-pilot/PILOT_250_AUTHORITY_CANDIDATES.csv"
SUMMARY = ROOT / "artifacts/issue180-diverse-pilot/authority_candidate_summary.json"

# Explicitly reviewed qualifier -> stable product-root mappings only.
APPROVED_QUALIFIER_ROOTS = {
    "pokemon": "pokemon",
    "vocaloid": "vocaloid",
    "fate": "fate_(series)",
    "umamusume": "umamusume",
    "blue_archive": "blue_archive",
    "honkai:_star_rail": "honkai:_star_rail",
    "honkai_star_rail": "honkai:_star_rail",
    "arknights": "arknights",
    "kancolle": "kantai_collection",
    "kantai_collection": "kantai_collection",
    "touhou": "touhou",
    "hololive": "hololive",
    "wuthering_waves": "wuthering_waves",
}

FINAL_QUALIFIER = re.compile(r"_\(([^()]+)\)$")

def main() -> int:
    with PILOT.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 250:
        raise SystemExit(f"expected 250 pilot rows, got {len(rows)}")

    out = []
    counts: dict[str, int] = {}
    for row in rows:
        tag = row["canonical_tag"]
        match = FINAL_QUALIFIER.search(tag)
        qualifier = match.group(1).lower() if match else ""
        root = APPROVED_QUALIFIER_ROOTS.get(qualifier, "")
        if root:
            state = "AUTO_CONFIRM_CANDIDATE"
            authority = "QUALIFIER_COPYRIGHT"
            reason = "final qualifier has an explicitly approved qualifier-to-root mapping"
        elif qualifier:
            state = "NEEDS_AUTHORITY_REVIEW"
            authority = "QUALIFIER_ALIAS_UNVERIFIED"
            reason = "final qualifier exists but has no approved root mapping"
        else:
            state = "NEEDS_AUTHORITY_REVIEW"
            authority = "NO_ACCEPTED_HOME_AUTHORITY"
            reason = "no accepted authority is mechanically provable from the canonical tag"

        counts[state] = counts.get(state, 0) + 1
        out.append({
            **row,
            "authority_candidate_state": state,
            "candidate_home_copyright": root,
            "candidate_authority_type": authority,
            "candidate_reason": reason,
            "sampled_ecosystem_is_authority": "false",
            "old_relation_is_authority": "false",
        })

    fields = list(rows[0].keys()) + [
        "authority_candidate_state", "candidate_home_copyright",
        "candidate_authority_type", "candidate_reason",
        "sampled_ecosystem_is_authority", "old_relation_is_authority",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(out)

    summary = {
        "pilot_rows": len(rows),
        "state_counts": counts,
        "mechanical_scope": "approved final qualifiers only",
        "curated_list_auto_inference": False,
        "legacy_relation_used_as_authority": False,
        "sampled_ecosystem_used_as_authority": False,
        "production_modified": False,
        "accepted_source_modified": False,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
