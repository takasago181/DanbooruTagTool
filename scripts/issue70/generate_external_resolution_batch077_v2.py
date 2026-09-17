from __future__ import annotations

import csv

from generate_external_resolution_batch077 import CANDIDATES, FIELDS, ITEMS, OUT, QUEUE


def main() -> None:
    with QUEUE.open(encoding="utf-8-sig", newline="") as f:
        queue = list(csv.DictReader(f))
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = list(csv.DictReader(f))

    by_tag = {r["canonical_tag"]: r for r in queue}
    effective_unresolved = {r["canonical_tag"] for r in candidates}
    missing_from_effective = sorted(set(ITEMS) - effective_unresolved)
    assert not missing_from_effective, f"batch077 targets not effective unresolved anymore: {missing_from_effective}"
    missing_from_queue = sorted(set(ITEMS) - set(by_tag))
    assert not missing_from_queue, f"batch077 targets absent from root queue: {missing_from_queue}"

    rows = []
    for tag, spec in ITEMS.items():
        verdict, display, search, url, note = spec
        q = by_tag[tag]
        assert q["category"] == "Copyright", (tag, q["category"])
        assert verdict in {"KEEP", "FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH"}, (tag, verdict)
        pd = display if verdict in {"FIX_DISPLAY", "FIX_BOTH"} else ""
        ps = search if verdict in {"FIX_SEARCH", "FIX_BOTH"} else ""
        if verdict in {"FIX_DISPLAY", "FIX_BOTH"}:
            assert pd and pd != q["display_ja"], (tag, q["display_ja"], pd)
        if verdict in {"FIX_SEARCH", "FIX_BOTH"}:
            assert ps and ps != q["search_ja"], (tag, q["search_ja"], ps)
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
            "reason_code": "OFFICIAL_OR_FIRST_PARTY_TITLE_CONFIRMED_BATCH077",
            "confidence": "HIGH",
            "evidence_refs": url,
            "audit_note": note,
            "approval_status": "PROPOSED",
        })

    assert len(rows) == 80
    assert len({r["row_id"] for r in rows}) == 80
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print({"rows": len(rows), "output": str(OUT), "production_modified": False})


if __name__ == "__main__":
    main()
