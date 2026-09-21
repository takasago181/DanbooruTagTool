#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
OUT = ROOT / "artifacts/issue180-single-home-pilot"

PILOT = {
    "pokemon": {
        "home": "pokemon",
        "characters": ["dawn_(pokemon)", "pikachu", "lapras"],
    },
    "vocaloid": {
        "home": "vocaloid",
        "characters": ["hatsune_miku", "kaito_(vocaloid)"],
    },
    "kantai_collection": {
        "home": "kantai_collection",
        "characters": ["ikazuchi_(kancolle)", "inazuma_(kancolle)", "shimakaze_(kancolle)"],
    },
    "bocchi_the_rock": {
        "home": "bocchi_the_rock!",
        "characters": ["gotoh_hitori"],
    },
    "hololive": {
        "home": "hololive",
        "characters": ["shirakami_fubuki", "irys_(hololive)", "gawr_gura"],
    },
}


# Evidence types allowed to prove a production HOME relation in this pilot.
# Co-occurrence, generic wiki-body links, and catalog fallback guesses are
# deliberately excluded even when they point to a plausible single candidate.
ACCEPTED_HOME_EVIDENCE = {
    "CURATED_COPYRIGHT_LIST",
    "QUALIFIER_COPYRIGHT",
    "CHARACTER_IMPLICATION_INHERITANCE",
}

# Pilot-only authority evidence.  Each tuple is:
#   (candidate_home, evidence_type, provenance)
# Multiple accepted candidates are a conflict -> HOME_UNRESOLVED.
HOME_EVIDENCE = {
    "dawn_(pokemon)": [
        ("pokemon", "QUALIFIER_COPYRIGHT", "canonical qualifier"),
        ("pokemon", "CURATED_COPYRIGHT_LIST", "official Pokemon character page"),
    ],
    "pikachu": [
        ("pokemon", "CURATED_COPYRIGHT_LIST", "official Pokemon Pokedex"),
    ],
    "lapras": [
        ("pokemon", "CURATED_COPYRIGHT_LIST", "official Pokemon site"),
    ],
    "hatsune_miku": [
        ("vocaloid", "CATALOG_ROOT_FALLBACK", "Piapro/Crypton character; current catalog root guess"),
    ],
    "kaito_(vocaloid)": [
        ("vocaloid", "QUALIFIER_COPYRIGHT", "canonical qualifier"),
        ("vocaloid", "CURATED_COPYRIGHT_LIST", "official Piapro Characters page"),
    ],
    "ikazuchi_(kancolle)": [
        ("kantai_collection", "QUALIFIER_COPYRIGHT", "canonical qualifier"),
    ],
    "inazuma_(kancolle)": [
        ("kantai_collection", "QUALIFIER_COPYRIGHT", "canonical qualifier"),
    ],
    "shimakaze_(kancolle)": [
        ("kantai_collection", "QUALIFIER_COPYRIGHT", "canonical qualifier"),
        ("kantai_collection", "CURATED_COPYRIGHT_LIST", "official DMM Kantai Collection page"),
    ],
    "gotoh_hitori": [
        ("bocchi_the_rock!", "CURATED_COPYRIGHT_LIST", "official Bocchi the Rock! character page"),
    ],
    "shirakami_fubuki": [
        ("hololive", "CURATED_COPYRIGHT_LIST", "official hololive talent roster"),
    ],
    "irys_(hololive)": [
        ("hololive", "QUALIFIER_COPYRIGHT", "canonical qualifier"),
        ("hololive", "CURATED_COPYRIGHT_LIST", "official hololive talent profile"),
    ],
    "gawr_gura": [
        ("hololive", "CURATED_COPYRIGHT_LIST", "official hololive talent/alumni profile"),
    ],
}

def read_rows():
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def main() -> int:
    rows = read_rows()
    by_tag = {r["canonical_tag"]: r for r in rows}
    OUT.mkdir(parents=True, exist_ok=True)

    result = []
    missing = []
    for ecosystem, spec in PILOT.items():
        home_tag = spec["home"]
        home = by_tag.get(home_tag)
        if not home:
            missing.append(home_tag)
            continue
        if home.get("category_name") != "Copyright":
            raise SystemExit(f"home tag is not Copyright: {home_tag} -> {home.get('category_name')}")
        for tag in spec["characters"]:
            row = by_tag.get(tag)
            if not row:
                missing.append(tag)
                continue
            if row.get("category_name") != "Character":
                raise SystemExit(f"pilot character is not Character: {tag} -> {row.get('category_name')}")
            result.append({
                "ecosystem": ecosystem,
                "row_id": row.get("row_id", ""),
                "canonical_tag": tag,
                "display_ja": row.get("display_ja", ""),
                "search_ja": row.get("search_ja", ""),
                "aliases": row.get("aliases", ""),
                "post_count": row.get("post_count", ""),
                "old_related_copyright": row.get("related_copyright", ""),
                "proposed_home_copyright": home_tag,
                "home_row_id": home.get("row_id", ""),
                "home_display_ja": home.get("display_ja", ""),
            })

    if missing:
        raise SystemExit("missing pilot tags: " + ", ".join(missing))

    fields = list(result[0].keys())
    with (OUT / "source_rows.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(result)

    # Resolve HOME strictly from accepted authority evidence.
    decisions = []
    for row in result:
        tag = row["canonical_tag"]
        evidence = HOME_EVIDENCE.get(tag, [])
        accepted = [item for item in evidence if item[1] in ACCEPTED_HOME_EVIDENCE]
        accepted_homes = sorted({item[0] for item in accepted})

        if len(accepted_homes) == 1:
            state = "HOME_CONFIRMED"
            home = accepted_homes[0]
        else:
            state = "HOME_UNRESOLVED"
            home = ""

        if len(accepted_homes) > 1:
            conflict = "MULTIPLE_ACCEPTED_HOME_CANDIDATES"
        elif not accepted:
            conflict = "NO_ACCEPTED_HOME_AUTHORITY"
        else:
            conflict = ""

        decisions.append({
            "row_id": row["row_id"],
            "canonical_tag": tag,
            "state": state,
            "home_copyright": home,
            "accepted_home_count": len(accepted_homes),
            "accepted_evidence": " | ".join(
                f"{candidate}::{etype}::{provenance}"
                for candidate, etype, provenance in accepted
            ),
            "rejected_or_supporting_evidence": " | ".join(
                f"{candidate}::{etype}::{provenance}"
                for candidate, etype, provenance in evidence
                if etype not in ACCEPTED_HOME_EVIDENCE
            ),
            "conflict_reason": conflict,
            "old_related_copyright": row["old_related_copyright"],
        })

    # Cardinality invariant: no Character may resolve to more than one HOME.
    invalid = [d for d in decisions if d["accepted_home_count"] > 1]
    if invalid:
        raise SystemExit(
            "HOME cardinality violation: "
            + ", ".join(d["canonical_tag"] for d in invalid)
        )

    decision_fields = list(decisions[0].keys())
    with (OUT / "authority_decisions.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=decision_fields, lineterminator="\n")
        w.writeheader()
        w.writerows(decisions)

    confirmed = sum(d["state"] == "HOME_CONFIRMED" for d in decisions)
    unresolved = sum(d["state"] == "HOME_UNRESOLVED" for d in decisions)

    summary = {
        "pilot_character_rows": len(result),
        "home_confirmed": confirmed,
        "home_unresolved": unresolved,
        "home_cardinality_violations": len(invalid),
        "ecosystems": {k: {"home": v["home"], "characters": len(v["characters"])} for k, v in PILOT.items()},
        "production_modified": False,
        "accepted_source_modified": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\n--- source_rows.csv ---")
    print((OUT / "source_rows.csv").read_text(encoding="utf-8-sig"))
    print("\n--- authority_decisions.csv ---")
    print((OUT / "authority_decisions.csv").read_text(encoding="utf-8-sig"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
