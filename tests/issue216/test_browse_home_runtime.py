import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/issue216"


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def test_runtime_projection_is_frozen_exact_and_not_authority_mutation():
    manifest = json.loads((DOCS / "BROWSE_HOME_RUNTIME_MANIFEST_V1.json").read_text())
    for name, expected in manifest.items():
        if name.endswith(".csv"):
            assert hashlib.sha256((DOCS / name).read_bytes()).hexdigest() == expected
    rows = read(DOCS / "BROWSE_HOME_RUNTIME_V1.csv")
    assert rows == sorted(rows, key=lambda r: r["character"])
    assert len({r["character"] for r in rows}) == len(rows) == 32942
    catalog = read(ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay_2d_final.csv")
    characters = {r["canonical_tag"] for r in catalog if r["category_name"] == "Character"}
    roots = {r["canonical_tag"] for r in catalog if r["category_name"] == "Copyright"}
    reviewed = {r["character"]: r for r in read(DOCS / "REVIEWED_BROWSE_HOME_FINAL_V1.csv")}
    decisions = {r["canonical_character"]: r for r in read(DOCS / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")}
    for row in rows:
        character = row["character"]
        assert character in characters
        assert bool(row["formal_home"]) != bool(row["reviewed_home"])
        assert (row["formal_home"] or row["reviewed_home"]) in roots
        if row["reviewed_home"]:
            assert reviewed[character]["review_state"] == "REVIEWED_BROWSE_HOME"
            assert reviewed[character]["reviewed_browse_home"] == row["reviewed_home"]
            assert reviewed[character]["formal_authority_eligible"] == "NO"
            assert decisions[character]["research_state"] != "HOME_CONFIRMED"
        elif character in decisions:
            assert decisions[character]["research_state"] == "HOME_CONFIRMED"
            assert decisions[character]["home_copyright"] == row["formal_home"]
    assert sum(bool(r["formal_home"]) for r in rows) == 25533
    assert sum(bool(r["reviewed_home"]) for r in rows) == 7409
