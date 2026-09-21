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

    summary = {
        "pilot_character_rows": len(result),
        "ecosystems": {k: {"home": v["home"], "characters": len(v["characters"])} for k, v in PILOT.items()},
        "production_modified": False,
        "accepted_source_modified": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\n--- source_rows.csv ---")
    print((OUT / "source_rows.csv").read_text(encoding="utf-8-sig"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
