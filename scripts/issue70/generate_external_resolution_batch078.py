from __future__ import annotations

import csv
from pathlib import Path

QUEUE = Path("docs/issue70/audit/EXTERNAL_QUEUE_LIVE.csv")
CANDIDATES = Path("docs/issue70/audit/EXTERNAL_QUEUE_BATCH078_COPYRIGHT_CANDIDATES.csv")
SHORTLISTS = [
    Path("docs/issue70/audit/BATCH078_VERIFIED_SHORTLIST_A.csv"),
    Path("docs/issue70/audit/BATCH078_VERIFIED_SHORTLIST_B.csv"),
    Path("docs/issue70/audit/BATCH078_VERIFIED_SHORTLIST_C.csv"),
]
OUT = Path("docs/issue70/audit/external_resolution_copyright_official_batch078.csv")

FIELDS = [
    "row_id","canonical_tag","post_count","display_ja","search_ja",
    "prior_audit_verdict","audit_verdict","proposed_display_ja","proposed_search_ja",
    "reason_code","confidence","evidence_refs","audit_note","approval_status"
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    queue = read_csv(QUEUE)
    candidates = read_csv(CANDIDATES)

    shortlist_rows: list[dict[str, str]] = []
    for path in SHORTLISTS:
        rows = read_csv(path)
        assert rows, f"empty shortlist: {path}"
        shortlist_rows.extend(rows)

    tags = [r["canonical_tag"] for r in shortlist_rows]
    assert len(tags) == 80, f"expected 80 shortlist rows, got {len(tags)}"
    assert len(set(tags)) == 80, "duplicate canonical_tag across batch078 shortlists"
    assert all(r["status"] == "VERIFIED_SHORTLIST" for r in shortlist_rows)
    assert all((r["evidence_ref"] or "").startswith("http") for r in shortlist_rows)

    by_tag = {r["canonical_tag"]: r for r in queue}
    effective_unresolved = {r["canonical_tag"] for r in candidates}

    missing_effective = sorted(set(tags) - effective_unresolved)
    assert not missing_effective, f"batch078 targets not effective unresolved: {missing_effective}"
    missing_queue = sorted(set(tags) - set(by_tag))
    assert not missing_queue, f"batch078 targets absent from root queue: {missing_queue}"

    rows: list[dict[str, str]] = []
    for s in shortlist_rows:
        tag = s["canonical_tag"]
        q = by_tag[tag]
        verdict = s["provisional_verdict"]
        display = s["proposed_display_ja"]
        search = s["proposed_search_ja"]

        assert q["category"] == "Copyright", (tag, q["category"])
        assert verdict in {"KEEP", "FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH"}, (tag, verdict)

        pd = display if verdict in {"FIX_DISPLAY", "FIX_BOTH"} else ""
        ps = search if verdict in {"FIX_SEARCH", "FIX_BOTH"} else ""

        if verdict in {"FIX_DISPLAY", "FIX_BOTH"}:
            assert pd and pd != q["display_ja"], (tag, q["display_ja"], pd)
        else:
            assert not display, (tag, display)

        if verdict in {"FIX_SEARCH", "FIX_BOTH"}:
            assert ps and ps != q["search_ja"], (tag, q["search_ja"], ps)
        else:
            assert not search, (tag, search)

        rows.append({
            "row_id": q["row_id"],
            "canonical_tag": tag,
            "post_count": q["post_count"],
            "display_ja": q["display_ja"],
            "search_ja": q["search_ja"],
            "prior_audit_verdict": "NEEDS_EXTERNAL_CHECK",
            "audit_verdict": verdict,
            "proposed_display_ja": pd,
            "proposed_search_ja": ps,
            "reason_code": "OFFICIAL_OR_FIRST_PARTY_TITLE_CONFIRMED_BATCH078",
            "confidence": "HIGH",
            "evidence_refs": s["evidence_ref"],
            "audit_note": s["audit_note"],
            "approval_status": "PROPOSED",
        })

    assert len(rows) == 80
    assert len({r["row_id"] for r in rows}) == 80

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    verdict_counts = {
        v: sum(r["audit_verdict"] == v for r in rows)
        for v in sorted({r["audit_verdict"] for r in rows})
    }
    print({
        "rows": len(rows),
        "verdicts": verdict_counts,
        "output": str(OUT),
        "production_modified": False,
    })


if __name__ == "__main__":
    main()
