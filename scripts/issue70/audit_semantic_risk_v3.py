#!/usr/bin/env python3
"""Issue #70 semantic risk census v3.

Refines v2 false positives found during live semantic audit. In particular,
existing_rejected_ja can contain Latin/official spellings that were rejected
only as *Japanese* candidates; matching those spellings is not itself a
semantic defect. This wrapper removes those false conflict flags while keeping
all v2 runtime/family rules. Production data remains read-only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.issue70 import audit_semantic_risk as base
from scripts.issue70 import audit_semantic_risk_v2 as v2


def _remove_flag(record: dict[str, Any], flag: str, weight: int) -> None:
    flags = record.get("risk_flags") or []
    if flag in flags:
        flags.remove(flag)
        record["risk_score"] = max(0, int(record.get("risk_score") or 0) - weight)


def score_row(record: dict[str, Any]) -> None:
    v2.score_row(record)

    rejected_terms = base.evidence_terms(record, rejected=True)
    rejected_nonlatin = base.uniq_norm([x for x in rejected_terms if base.contains_ja(x)])
    display_norm = base.norm(record.get("display_ja", ""))
    search_norm = base.uniq_norm(base.split_pipe(record.get("search_ja", "")))

    # A Latin value in existing_rejected_ja means "not a Japanese candidate",
    # not "this official/Latin spelling is forbidden". Keep the conflict flag
    # only when the current value actually matches a CJK-bearing rejected term.
    if display_norm not in rejected_nonlatin:
        _remove_flag(record, "DISPLAY_MATCHES_REJECTED_JA", 4)
    if not (search_norm & rejected_nonlatin):
        _remove_flag(record, "SEARCH_CONTAINS_REJECTED_JA", 4)

    # accepted_evidence mixes existing_search_ja with raw candidate pools that
    # may contain Chinese-only forms. Do not let a raw candidate alone create a
    # strong Japanese-overlap warning. existing_display/search are the trusted
    # Japanese-facing evidence for this check; kana-bearing raw candidates are
    # still useful supporting evidence.
    trusted_terms: list[str] = []
    for field in ("existing_display_ja", "existing_search_ja"):
        trusted_terms.extend(base.split_pipe(record.get(field, "")))
    for term in base.split_pipe(record.get("existing_candidate_ja", "")):
        if any("\u3040" <= ch <= "\u30ff" for ch in term):
            trusted_terms.append(term)
    trusted_norm = base.uniq_norm([x for x in trusted_terms if base.contains_ja(x)])
    current_norm = {display_norm} | search_norm
    if "NO_SOURCE_JA_EVIDENCE_OVERLAP" in (record.get("risk_flags") or []):
        if not trusted_norm or current_norm & trusted_norm:
            _remove_flag(record, "NO_SOURCE_JA_EVIDENCE_OVERLAP", 2)


def rewrite_summary(out: Path) -> None:
    path = out / "risk_summary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["format_version"] = 3
    data["mode"] = "read_only_semantic_risk_census_v3_conflict_refined"
    data["selection_policy"]["v2_disposition"] = (
        "superseded for final triage: live audit showed that existing_rejected_ja also contains "
        "Latin/official spellings rejected only as Japanese candidates, and raw candidate pools "
        "can contain Chinese-only forms. v3 keeps only evidence conflicts supported by Japanese-facing evidence."
    )
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def output_path_from_argv() -> Path:
    if "--out" in sys.argv:
        i = sys.argv.index("--out")
        if i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return base.DEFAULT_OUT


def main() -> int:
    for field in ("family_base_canonical", "family_base_display_ja"):
        if field not in base.OUTPUT_FIELDS:
            base.OUTPUT_FIELDS.append(field)
        if field not in base.LEDGER_FIELDS:
            base.LEDGER_FIELDS.append(field)
    base.score_row = score_row
    base.add_duplicate_display_flags = v2.add_duplicate_display_flags
    base.is_accepted_risk = v2.is_accepted_risk
    rc = base.main()
    rewrite_summary(output_path_from_argv())
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
