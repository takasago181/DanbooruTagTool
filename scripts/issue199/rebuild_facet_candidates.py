#!/usr/bin/env python3
"""Rebuild the #199 frozen extraction and current-catalog eligibility report.

This is an offline audit/generation tool. The runtime does not read #132 Git
objects, the reconciliation ledger, or the catalog database to infer facets.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sqlite3
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

RESEARCH_COMMIT = "de450958eb598a2c7c3a34b112f139dfba617c6e"
LEDGER_PATH = "docs/issue132/product-reconciliation/product_reconciliation_ledger.csv"
SEMANTIC_PATH = "docs/issue132/final-audit/effective_semantic_ledger.jsonl"
EXPECTED_LEDGER_SHA256 = "02582ba54976b8b3b344ba09a4bb4aa3f86159db315506593f3a309a11f0cac6"
EXPECTED_SEMANTIC_SHA256 = "993bd537b77a6583f17db333d00d29f5132e88e10bf7934810958ed197d1398b"
BODY_IDS = {
    "BREAST_NIPPLE", "BUTTOCK_ANAL", "FEMALE_GENITAL", "MALE_GENITAL",
    "MOUTH_ORAL", "URETHRA",
}
THEME_IDS = {"BDSM_RESTRAINT", "INJURY_R18G", "REPRO_PREGNANCY_LACTATION"}

# Focused semantic QA exclusions. The row-level frozen evidence is retained in
# the disposition report; only these clear mismatches are withheld here.
SEMANTIC_HOLDS = {
    ("forked_hair", "BODY", "BREAST_NIPPLE"): "Surface names a hair form and the frozen row provides no breast-site evidence; unrelated body site.",
    ("perineum_peek", "BODY", "BREAST_NIPPLE"): "Perineum is a separate genital/anal region, not breast/nipple.",
    ("torn_bike_shorts", "BODY", "BREAST_NIPPLE"): "Clothing damage does not identify a breast/nipple site.",
    ("bruise_on_leg", "BODY", "BUTTOCK_ANAL"): "Leg is a different body site from buttock/anal.",
    ("covered_navel", "BODY", "FEMALE_GENITAL"): "Navel is not a female genital site.",
    ("large_pectorals", "BODY", "MALE_GENITAL"): "Pectorals are chest muscles, not male genital anatomy.",
    ("shark_fin", "BODY", "MOUTH_ORAL"): "The tag identifies a shark fin and does not indicate a mouth/oral site.",
    ("implied_cannibalism", "THEME", "BDSM_RESTRAINT"): "Cannibalism is a separate theme and does not indicate BDSM or restraint.",
    ("swaddled", "THEME", "REPRO_PREGNANCY_LACTATION"): "Swaddling alone describes wrapping an infant; it does not indicate reproduction, pregnancy, or lactation.",
}


def git_blob(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"], check=True, capture_output=True
    ).stdout


def normalize(value: str) -> str:
    return "_".join(value.strip().lower().replace("_", " ").split())


def write_csv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-db", required=True, type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--research-commit", default=RESEARCH_COMMIT)
    args = parser.parse_args()

    ledger_bytes = git_blob(args.research_commit, LEDGER_PATH)
    semantic_bytes = git_blob(args.research_commit, SEMANTIC_PATH)
    ledger_hash = hashlib.sha256(ledger_bytes).hexdigest()
    semantic_hash = hashlib.sha256(semantic_bytes).hexdigest()
    if ledger_hash != EXPECTED_LEDGER_SHA256 or semantic_hash != EXPECTED_SEMANTIC_SHA256:
        raise SystemExit("Frozen #132 provenance blob hash mismatch.")

    ledger = list(csv.DictReader(io.StringIO(ledger_bytes.decode("utf-8-sig"))))
    semantic = {
        row["identity_key"]: row
        for row in (json.loads(line) for line in semantic_bytes.decode("utf-8-sig").splitlines())
    }
    if len(ledger) != 31_003 or len(semantic) != 31_003:
        raise SystemExit("Frozen #132 ordinary-identity population mismatch.")

    frozen: list[dict[str, str]] = []
    for row in ledger:
        if row["membership"] != "GENERAL_ONLY":
            continue
        for axis, field in (("BODY", "missing_body_sites"), ("THEME", "missing_themes")):
            values = json.loads(row[field] or "[]")
            allowed = BODY_IDS if axis == "BODY" else THEME_IDS
            if any(value not in allowed for value in values):
                raise SystemExit(f"Unknown frozen #76 facet ID: {row['identity_key']} {axis} {values}")
            semantic_row = semantic.get(row["identity_key"])
            semantic_field = "body_facets" if axis == "BODY" else "theme_facets"
            if semantic_row is None or any(value not in semantic_row[semantic_field] for value in values):
                raise SystemExit(f"Frozen semantic evidence does not name candidate facet: {row['identity_key']} {axis}")
            if values and semantic_row["review_depth"] not in ("CHECKED", "RESEARCHED"):
                raise SystemExit(f"Frozen semantic review is not finalized: {row['identity_key']} {semantic_row['review_depth']}")
            for facet in values:
                frozen.append({"identity_key": row["identity_key"], "axis": axis, "facet_id": facet})

    frozen.sort(key=lambda row: (row["identity_key"], row["axis"], row["facet_id"]))
    identities = {row["identity_key"] for row in frozen}
    facet_counts = Counter((row["axis"], row["facet_id"]) for row in frozen)
    if (len(identities), len(frozen), facet_counts) != (
        359,
        370,
        Counter({
            ("BODY", "BREAST_NIPPLE"): 77,
            ("BODY", "BUTTOCK_ANAL"): 32,
            ("BODY", "FEMALE_GENITAL"): 11,
            ("BODY", "MALE_GENITAL"): 20,
            ("BODY", "MOUTH_ORAL"): 117,
            ("THEME", "BDSM_RESTRAINT"): 24,
            ("THEME", "INJURY_R18G"): 82,
            ("THEME", "REPRO_PREGNANCY_LACTATION"): 7,
        }),
    ):
        raise SystemExit("Frozen #132 extraction did not reproduce 359 identities / 370 assignments.")

    connection = sqlite3.connect(f"file:{args.catalog_db.resolve().as_posix()}?mode=ro", uri=True)
    entries = [json.loads(row[0]) for row in connection.execute("SELECT payload FROM entries")]
    catalog_groups: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        if entry["EffectiveCategory"] in ("General", "Special"):
            catalog_groups[normalize(entry.get("Canonical") or entry["English"])].append(entry)

    dispositions: list[dict[str, str]] = []
    accepted: list[dict[str, str]] = []
    reason_counts: Counter[str] = Counter()
    for candidate in frozen:
        key, axis, facet = candidate["identity_key"], candidate["axis"], candidate["facet_id"]
        group = catalog_groups.get(normalize(key), [])
        exact = [entry for entry in group if (entry.get("Canonical") or entry["English"]) == key]
        reason = ""
        if len(group) != len(exact) or not exact:
            reason = "LIVE_IDENTITY_NOT_EXACTLY_RESOLVED"
        elif any(entry["EffectiveCategory"] == "Special" for entry in group) or not any(
            entry["EffectiveCategory"] == "General" for entry in group
        ):
            reason = "LIVE_IDENTITY_NOT_GENERAL_ONLY"
        elif not any(
            entry["EffectiveCategory"] == "General"
            and entry["BrowseClassification"] == 1
            and entry["CanBrowse"]
            for entry in group
        ):
            reason = "LIVE_GENERAL_NOT_PROPOSED_AND_BROWSEABLE"
        else:
            prop = "BodySiteIds" if axis == "BODY" else "ThemeIds"
            if any(
                facet in ((entry.get("UnifiedBrowseFacets") or {}).get(prop) or [])
                or facet in (((entry.get("SpecialBrowseV2") or {}).get(prop)) or [])
                for entry in group
            ):
                reason = "FACET_ALREADY_PRESENT_IN_LIVE_PROJECTION"
        if not reason and (key, axis, facet) in SEMANTIC_HOLDS:
            reason = "FOCUSED_SEMANTIC_HOLD: " + SEMANTIC_HOLDS[(key, axis, facet)]
        if reason:
            reason_counts[reason.split(":", 1)[0]] += 1
        else:
            accepted.append(candidate)
        semantic_row = semantic[key]
        semantic_field = "body_facets" if axis == "BODY" else "theme_facets"
        dispositions.append({
            **candidate,
            "semantic_review_depth": semantic_row["review_depth"],
            "semantic_facets": json.dumps(semantic_row[semantic_field], ensure_ascii=False, separators=(",", ":")),
            "disposition": "SHIP" if not reason else "EXCLUDE",
            "reason": reason,
        })

    if len(accepted) != len(set((row["identity_key"], row["axis"], row["facet_id"]) for row in accepted)):
        raise SystemExit("Duplicate accepted identity/axis/facet assignment.")

    write_csv(args.repo_root / "docs/issue199/frozen_facet_extraction_v1.csv",
              ["identity_key", "axis", "facet_id"], frozen)
    write_csv(args.repo_root / "docs/issue199/candidate_disposition_v1.csv",
              ["identity_key", "axis", "facet_id", "semantic_review_depth", "semantic_facets", "disposition", "reason"], dispositions)
    write_csv(args.repo_root / "src/DanbooruTagTool.Data/UnifiedBrowseData/issue199_general_facets_v1.csv",
              ["identity_key", "axis", "facet_id"], accepted)
    summary = {
        "research_commit": args.research_commit,
        "ledger_sha256": ledger_hash,
        "semantic_ledger_sha256": semantic_hash,
        "live_baseline_catalog_sha256": hashlib.sha256(args.catalog_db.read_bytes()).hexdigest(),
        "frozen_identity_count": len(identities),
        "frozen_assignment_count": len(frozen),
        "live_eligible_identity_count_before_semantic_qa": len({
            (r["identity_key"]) for r in dispositions if r["reason"] == ""
            or r["reason"].startswith("FOCUSED_SEMANTIC_HOLD:")
        }),
        "shipped_identity_count": len({row["identity_key"] for row in accepted}),
        "shipped_assignment_count": len(accepted),
        "excluded_assignment_count": len(dispositions) - len(accepted),
        "exclusions_by_reason": dict(sorted(reason_counts.items())),
        "shipped_by_facet": {f"{axis}/{facet}": count for (axis, facet), count in sorted(Counter((r["axis"], r["facet_id"]) for r in accepted).items())},
    }
    (args.repo_root / "docs/issue199/candidate_summary_v1.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
