from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEARCH = ROOT / "artifacts/issue179-search-cleanup/SEARCH_CLEANUP_CANDIDATES_V1.csv"
DISPLAY = ROOT / "artifacts/issue179-display-cleanup/DISPLAY_CLEANUP_CANDIDATES_V1.csv"
OUT = ROOT / "artifacts/issue179-corrections"
LEDGER = OUT / "CORRECTION_LEDGER_V1.csv"
HOLDS = OUT / "CORRECTION_HOLDS_V1.csv"
SUMMARY = OUT / "summary.json"

LEDGER_FIELDS = [
    "row_id", "canonical_tag", "category", "field",
    "old_value", "proposed_value", "reason_code",
    "evidence_provenance", "first_review", "second_review", "final_status",
]
HOLD_FIELDS = [
    "row_id", "canonical_tag", "category", "field",
    "old_value", "proposed_value", "reason_code", "hold_reason",
]

def read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

EXPLICIT_REVIEWED_FIXES = [
    {
        "row_id": "I70-010624",
        "canonical_tag": "super_sailor_venus",
        "category": "Character",
        "field": "display_ja",
        "old_value": "スーパーセーラーヴィーナス（セーラームーン）",
        "proposed_value": "スーパーセーラーヴィーナス",
        "reason_code": "OFFICIAL_NAME_AND_COLLISION_REPAIR",
        "evidence_provenance": "OFFICIAL:https://sailormoon-official.com/stage/information/_-shining_theater_260714.php",
    },
    {
        "row_id": "I70-012005",
        "canonical_tag": "super_sailor_jupiter",
        "category": "Character",
        "field": "display_ja",
        "old_value": "スーパーセーラーヴィーナス（セーラームーン）",
        "proposed_value": "スーパーセーラージュピター",
        "reason_code": "WRONG_CHARACTER_NAME_COLLISION_REPAIR",
        "evidence_provenance": "OFFICIAL:https://sailormoon-official.com/stage/information/_-shining_theater_260714.php",
    },
    {
        "row_id": "I70-012005",
        "canonical_tag": "super_sailor_jupiter",
        "category": "Character",
        "field": "search_ja",
        "old_value": "スーパーセーラーヴィーナス",
        "proposed_value": "スーパーセーラージュピター",
        "reason_code": "WRONG_CHARACTER_SEARCH_NAME_REPAIR",
        "evidence_provenance": "OFFICIAL:https://sailormoon-official.com/stage/information/_-shining_theater_260714.php",
    },
]

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    accepted: list[dict[str, str]] = []
    holds: list[dict[str, str]] = []

    search_rows = read(SEARCH)
    for r in search_rows:
        if r["review_state"] != "SECOND_REVIEW_ACCEPTED":
            continue
        accepted.append({
            "row_id": r["row_id"],
            "canonical_tag": r["canonical_tag"],
            "category": r["category"],
            "field": "search_ja",
            "old_value": r["old_search_ja"],
            "proposed_value": r["proposed_search_ja"],
            "reason_code": r["reason"],
            "evidence_provenance": "retained B001/B002 review + curated exact/safe-pattern second review",
            "first_review": "PASS",
            "second_review": "PASS",
            "final_status": "ACCEPTED_AUDIT_OVERLAY",
        })

    display_rows = read(DISPLAY)
    for r in display_rows:
        if r["review_state"] == "SECOND_REVIEW_ACCEPTED":
            accepted.append({
                "row_id": r["row_id"],
                "canonical_tag": r["canonical_tag"],
                "category": r["category"],
                "field": "display_ja",
                "old_value": r["old_display_ja"],
                "proposed_value": r["proposed_display_ja"],
                "reason_code": r["reason"],
                "evidence_provenance": "existing search surface + collision-safe conservative second review",
                "first_review": "PASS",
                "second_review": "PASS",
                "final_status": "ACCEPTED_AUDIT_OVERLAY",
            })
        else:
            if r["row_id"] not in {"I70-010624", "I70-012005"}:
                holds.append({
                    "row_id": r["row_id"],
                    "canonical_tag": r["canonical_tag"],
                    "category": r["category"],
                    "field": "display_ja",
                    "old_value": r["old_display_ja"],
                    "proposed_value": r["proposed_display_ja"],
                    "reason_code": r["reason"],
                    "hold_reason": r.get("review_note", "") or r["review_state"],
                })

    for r in EXPLICIT_REVIEWED_FIXES:
        accepted.append({
            **r,
            "first_review": "PASS",
            "second_review": "PASS",
            "final_status": "ACCEPTED_AUDIT_OVERLAY",
        })

    # Deterministic and no duplicate row+field corrections.
    accepted.sort(key=lambda r: (r["row_id"], r["field"]))
    holds.sort(key=lambda r: (r["row_id"], r["field"]))
    keys = [(r["row_id"], r["field"]) for r in accepted]
    if len(keys) != len(set(keys)):
        raise SystemExit("duplicate accepted row+field correction")

    # Frozen current audit counts. Fail if candidate logic drifts silently.
    search_count = sum(r["field"] == "search_ja" for r in accepted)
    display_count = sum(r["field"] == "display_ja" for r in accepted)
    if search_count != 967:
        raise SystemExit(f"expected 967 accepted search rows, got {search_count}")
    if display_count != 214:
        raise SystemExit(f"expected 214 accepted display rows, got {display_count}")
    if len(holds) != 19:
        raise SystemExit(f"expected 19 display holds, got {len(holds)}")

    with LEDGER.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(accepted)
    with HOLDS.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HOLD_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(holds)

    summary = {
        "accepted_field_changes": len(accepted),
        "accepted_search_rows": search_count,
        "accepted_display_rows": display_count,
        "display_holds": len(holds),
        "source_data_mutated": False,
        "production_modified": False,
        "home_authority_modified": False,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
