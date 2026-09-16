#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def norm_tag(value: str) -> str:
    return (value or "").strip().casefold().replace("_", " ")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--adult-priority", required=True)
    ap.add_argument("--top-uncovered", required=True)
    ap.add_argument("--issue94-candidates", required=True)
    ap.add_argument("--issue94-exclusions", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    adult = read_csv(Path(args.adult_priority))
    top = read_csv(Path(args.top_uncovered))
    old_candidates = read_csv(Path(args.issue94_candidates))
    old_exclusions = read_csv(Path(args.issue94_exclusions))

    cand_by = {norm_tag(r["canonical_tag"]): r for r in old_candidates}
    excl_by = {norm_tag(r["canonical_tag"]): r for r in old_exclusions}

    promoted_but_missing = []
    adult_rows = []
    for r in adult:
        n = norm_tag(r["canonical_tag"])
        out = dict(r)
        if n in cand_by:
            old = cand_by[n]
            out["issue94_crosswalk"] = "ERROR_ISSUE94_CANDIDATE_STILL_MISSING"
            out["issue94_final_status"] = old.get("final_status", "CANDIDATE")
            out["issue94_final_reason"] = old.get("final_reason", "")
            promoted_but_missing.append(r["canonical_tag"])
        elif n in excl_by:
            old = excl_by[n]
            out["issue94_crosswalk"] = "ISSUE94_REVIEWED_EXCLUDED"
            out["issue94_final_status"] = old.get("final_status", "")
            out["issue94_final_reason"] = old.get("final_reason", "")
        else:
            out["issue94_crosswalk"] = "NEW_TO_ADULT_FOCUSED_REVIEW"
            out["issue94_final_status"] = ""
            out["issue94_final_reason"] = "not present in Issue #94 final 324-row review candidate/exclusion outcome"
        adult_rows.append(out)

    top_rows = []
    for r in top:
        n = norm_tag(r["canonical_tag"])
        out = dict(r)
        if n in cand_by:
            old = cand_by[n]
            out["issue94_crosswalk"] = "ERROR_ISSUE94_CANDIDATE_STILL_MISSING"
            out["issue94_final_status"] = old.get("final_status", "CANDIDATE")
            out["issue94_final_reason"] = old.get("final_reason", "")
        elif n in excl_by:
            old = excl_by[n]
            out["issue94_crosswalk"] = "ISSUE94_REVIEWED_EXCLUDED"
            out["issue94_final_status"] = old.get("final_status", "")
            out["issue94_final_reason"] = old.get("final_reason", "")
        else:
            out["issue94_crosswalk"] = "NOT_IN_ISSUE94_FINAL_REVIEW"
            out["issue94_final_status"] = ""
            out["issue94_final_reason"] = ""
        top_rows.append(out)

    if promoted_but_missing:
        raise ValueError(f"Issue #94 promoted candidates unexpectedly still missing from Special: {promoted_but_missing[:20]}")

    base_fields = list(adult[0].keys()) if adult else []
    fields = base_fields + ["issue94_crosswalk", "issue94_final_status", "issue94_final_reason"]
    out_dir = Path(args.out_dir)
    write_csv(out_dir / "adult_priority_issue94_crosswalk_v1.csv", adult_rows, fields)
    write_csv(
        out_dir / "adult_priority_new_since_issue94_prescreen_v1.csv",
        [r for r in adult_rows if r["issue94_crosswalk"] == "NEW_TO_ADULT_FOCUSED_REVIEW"],
        fields,
    )

    top_fields = list(top[0].keys()) + ["issue94_crosswalk", "issue94_final_status", "issue94_final_reason"] if top else []
    write_csv(out_dir / "top_uncovered_issue94_crosswalk_v1.csv", top_rows, top_fields)

    counts = Counter(r["issue94_crosswalk"] for r in adult_rows)
    prior_status = Counter(r["issue94_final_status"] for r in adult_rows if r["issue94_final_status"])
    new_rows = [r for r in adult_rows if r["issue94_crosswalk"] == "NEW_TO_ADULT_FOCUSED_REVIEW"]
    new_rows.sort(key=lambda r: (-int(r["post_count"]), r["canonical_tag"]))

    summary = {
        "adult_priority_total": len(adult_rows),
        "crosswalk_counts": dict(sorted(counts.items())),
        "prior_issue94_status_counts": dict(sorted(prior_status.items())),
        "new_to_adult_focused_review_count": len(new_rows),
        "issue94_candidate_still_missing_count": len(promoted_but_missing),
        "top_new_to_adult_focused_review": [
            {
                "tag": r["canonical_tag"],
                "post_count": int(r["post_count"]),
                "domains": r.get("canonical_adult_domains", ""),
            }
            for r in new_rows[:150]
        ],
        "content_filter_used": "NO",
        "production_mutation": "NO",
        "issue70_mutated": "NO",
    }
    (out_dir / "issue94_crosswalk_summary_v1.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
