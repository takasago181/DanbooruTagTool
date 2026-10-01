"""Explicit build-time projection; never run at app startup. Master remains ignored."""
import argparse
import csv
import hashlib
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER_SHA = "135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071"


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def project(master):
    assert hashlib.sha256(master.read_bytes()).hexdigest() == MASTER_SHA
    formal = {r["canonical_tag"]: r["home_copyright"] for r in read(master)
              if r["final_state"] == "HOME_CONFIRMED"}
    docs = ROOT / "docs/issue216"
    for row in read(docs / "AUTHORITY_COVERAGE_DECISIONS_V1.csv"):
        if row["research_state"] == "HOME_CONFIRMED":
            assert row["canonical_character"] not in formal
            formal[row["canonical_character"]] = row["home_copyright"]
    reviewed = {r["character"]: r["reviewed_browse_home"]
                for r in read(docs / "REVIEWED_BROWSE_HOME_FINAL_V1.csv")
                if r["review_state"] == "REVIEWED_BROWSE_HOME"}
    catalog = read(ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay_2d_final.csv")
    characters = {r["canonical_tag"] for r in catalog if r["category_name"] == "Character"}
    roots = {r["canonical_tag"] for r in catalog if r["category_name"] == "Copyright"}
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["character", "formal_home", "reviewed_home"])
    for character in sorted(characters):
        home = formal.get(character, "")
        fallback = reviewed.get(character, "") if not home else ""
        # An unavailable formal root must never be replaced by a fallback.
        if home and home not in roots or fallback and fallback not in roots:
            continue
        if home or fallback:
            writer.writerow([character, home, fallback])
    return output.getvalue().encode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = project(args.master)
    target = ROOT / "docs/issue216/BROWSE_HOME_RUNTIME_V1.csv"
    if args.check:
        assert target.read_bytes() == payload, "Runtime HOME projection drift"
    else:
        target.write_bytes(payload)
    print(hashlib.sha256(payload).hexdigest())
