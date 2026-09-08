import json
from pathlib import Path

from translation_quarantine.r3.r3_issue41_normalize_evidence import normalize


def test_normalize_69_approved_plus_31_review(tmp_path: Path):
    r3 = tmp_path / "translation_quarantine" / "r3"
    r3.mkdir(parents=True)
    approved_ordinals = list(range(1, 70))
    chunks = [approved_ordinals[index::8] for index in range(8)]
    for index, ordinals in enumerate(chunks, 1):
        rows = []
        for ordinal in ordinals:
            rows.append(
                {
                    "canonical": f"c{ordinal}",
                    "pilot_ordinal": ordinal,
                    "frozen": True,
                    "issue41_batch": f"{index:02d}",
                    "scope_basis": "TRANSPARENT_CANONICAL_COMPOSITION",
                    "semantic_scope": f"scope {ordinal}",
                    "display_candidate": f"表示{ordinal}",
                    "search_candidate": f"検索{ordinal}",
                    "term_class": "EXACT_SYNONYM",
                    "search_equivalence": "VERIFIED_EXACT",
                    "semantic_source": "fixture",
                }
            )
        (r3 / f"issue41_input_batch{index:02d}.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )

    reviews = []
    for ordinal in range(70, 101):
        reviews.append(
            {
                "canonical": f"c{ordinal}",
                "pilot_ordinal": ordinal,
                "frozen": True,
                "issue41_batch": "09",
                "decision_state": "REVIEW",
                "scope_basis": "INSUFFICIENT_FOR_APPROVAL",
                "review_reason": "NO_SCOPE",
                "note": "review",
            }
        )
    (r3 / "issue41_unresolved_review_batch09.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in reviews),
        encoding="utf-8",
    )

    summary = normalize(tmp_path)
    assert summary["approved_input_rows"] == 69
    assert summary["explicit_review_rows"] == 31
    assert summary["evidence_rows"] == 169
    evidence = [
        json.loads(line)
        for line in (r3 / "issue41_frozen_evidence_manifest.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert sum(row["evidence_role"] == "SEMANTIC_SCOPE" for row in evidence) == 69
    assert sum(row["evidence_role"] == "WORDING_CANDIDATE" for row in evidence) == 69
    assert sum(row["evidence_role"] == "IDENTITY_ONLY" for row in evidence) == 31
    wording = next(
        row for row in evidence if row["evidence_role"] == "WORDING_CANDIDATE"
    )
    assert wording["search_equivalence_proof"] == "VERIFIED_EXACT"
