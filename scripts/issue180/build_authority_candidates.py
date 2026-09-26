#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "artifacts/issue180-diverse-pilot/PILOT_250.csv"
B002 = ROOT / "docs/issue180/reviews/I180-B002_HARD_CASE_FIRST_PASS.csv"
OUT = ROOT / "artifacts/issue180-diverse-pilot/PILOT_250_AUTHORITY_CANDIDATES.csv"
SUMMARY = ROOT / "artifacts/issue180-diverse-pilot/authority_candidate_summary.json"

# Baseline mappings already reviewed before B002.
BASE_QUALIFIER_ROOTS = {
    "pokemon": "pokemon", "vocaloid": "vocaloid", "fate": "fate_(series)",
    "umamusume": "umamusume", "blue_archive": "blue_archive",
    "honkai:_star_rail": "honkai:_star_rail", "honkai_star_rail": "honkai:_star_rail",
    "arknights": "arknights", "kancolle": "kantai_collection",
    "kantai_collection": "kantai_collection", "touhou": "touhou",
    "hololive": "hololive", "wuthering_waves": "wuthering_waves",
    "azur_lane": "azur_lane", "girls_und_panzer": "girls_und_panzer",
    "princess_connect!": "princess_connect!",
}
FINAL_QUALIFIER = re.compile(r"_\(([^()]+)\)$")

def load_reviewed_authority():
    exact = {}
    qualifier_pairs: dict[str, set[str]] = {}
    with B002.open("r", encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["home_state"] != "HOME_CONFIRMED":
                continue
            exact[r["canonical_tag"]] = r
            if r["authority_type"] == "QUALIFIER_COPYRIGHT":
                m = FINAL_QUALIFIER.search(r["canonical_tag"])
                if m:
                    qualifier_pairs.setdefault(m.group(1).lower(), set()).add(r["home_copyright"])
    roots = dict(BASE_QUALIFIER_ROOTS)
    conflicts = {}
    for q, homes in qualifier_pairs.items():
        if len(homes) == 1:
            home = next(iter(homes))
            if q in roots and roots[q] != home:
                conflicts[q] = sorted({roots[q], home})
            else:
                roots[q] = home
        else:
            conflicts[q] = sorted(homes)
    if conflicts:
        raise SystemExit("reviewed qualifier-root conflicts: " + json.dumps(conflicts, ensure_ascii=False))
    return exact, roots

def main() -> int:
    with PILOT.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 250:
        raise SystemExit(f"expected 250 pilot rows, got {len(rows)}")

    reviewed_exact, approved_roots = load_reviewed_authority()
    out = []
    counts: dict[str, int] = {}
    authority_counts: dict[str, int] = {}

    for row in rows:
        tag = row["canonical_tag"]
        reviewed = reviewed_exact.get(tag)
        match = FINAL_QUALIFIER.search(tag)
        qualifier = match.group(1).lower() if match else ""
        root = approved_roots.get(qualifier, "")

        if reviewed:
            state = "AUTO_CONFIRM_CANDIDATE"
            home = reviewed["home_copyright"]
            authority = reviewed["authority_type"]
            reason = "exact Character has a reviewed B002 HOME_CONFIRMED authority decision"
        elif root:
            state = "AUTO_CONFIRM_CANDIDATE"
            home = root
            authority = "QUALIFIER_COPYRIGHT"
            reason = "final qualifier has an explicitly reviewed qualifier-to-root mapping"
        elif qualifier:
            state = "NEEDS_AUTHORITY_REVIEW"
            home = ""
            authority = "QUALIFIER_ALIAS_UNVERIFIED"
            reason = "final qualifier exists but has no approved qualifier-to-root mapping"
        else:
            state = "NEEDS_AUTHORITY_REVIEW"
            home = ""
            authority = "NO_ACCEPTED_HOME_AUTHORITY"
            reason = "no accepted authority is mechanically provable from the canonical tag"

        counts[state] = counts.get(state, 0) + 1
        authority_counts[authority] = authority_counts.get(authority, 0) + 1
        out.append({
            **row,
            "authority_candidate_state": state,
            "candidate_home_copyright": home,
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
        "authority_counts": authority_counts,
        "reviewed_exact_authority_rows": len(reviewed_exact),
        "approved_qualifier_root_count": len(approved_roots),
        "reviewed_source": str(B002.relative_to(ROOT)),
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
