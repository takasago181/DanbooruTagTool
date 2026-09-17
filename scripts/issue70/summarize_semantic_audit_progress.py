#!/usr/bin/env python3
"""Summarize Issue #70 semantic audit progress exactly.

Runs the current v3 census, scans all proposal CSVs under docs/issue70/audit,
deduplicates by row_id, and reports remaining rows plus any conflicting audit
verdict/proposal combinations. It also emits the remaining translation-note,
risk-flag, status and impact distributions so the next audit batches can be
selected from live evidence rather than guessed.

This script is read-only with respect to the production Issue #70 data.
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "docs/issue70/audit"
TMP = ROOT / "artifacts/issue70-semantic-audit-v3-progress"
OUT = AUDIT_DIR / "PROGRESS_LIVE.json"
CATEGORIES = ("Character", "Copyright", "Artist")
VALID_VERDICTS = {
    "KEEP", "FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH",
    "NEEDS_EXTERNAL_CHECK", "NEEDS_USER_DECISION",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def run_census() -> list[dict[str, str]]:
    if TMP.exists():
        shutil.rmtree(TMP)
    subprocess.run([
        sys.executable,
        str(ROOT / "scripts/issue70/audit_semantic_risk_v3.py"),
        "--out", str(TMP),
        "--sample-per-category", "300",
    ], cwd=ROOT, check=True)
    return read_csv(TMP / "audit_ledger_template.csv")


def normalized_decision(row: dict[str, str]) -> tuple[str, str, str]:
    return (
        (row.get("audit_verdict") or "").strip(),
        (row.get("proposed_display_ja") or "").strip(),
        (row.get("proposed_search_ja") or "").strip(),
    )


def top_counter(counter: Counter[str], limit: int = 30) -> list[dict[str, object]]:
    return [{"value": key, "count": count} for key, count in counter.most_common(limit)]


def remaining_patterns(rows: list[dict[str, str]]) -> dict[str, object]:
    by_category: dict[str, object] = {}
    for category in CATEGORIES:
        subset = [row for row in rows if row["category_name"] == category]
        notes = Counter((row.get("translation_note") or "").strip() or "<blank>" for row in subset)
        statuses = Counter((row.get("translation_status") or "").strip() for row in subset)
        impacts = Counter((row.get("impact_tier") or "").strip() for row in subset)
        buckets = Counter((row.get("audit_bucket") or "").strip() for row in subset)
        flags: Counter[str] = Counter()
        for row in subset:
            for flag in (row.get("risk_flags") or "").split("|"):
                flag = flag.strip()
                if flag:
                    flags[flag] += 1
        by_category[category] = {
            "rows": len(subset),
            "status_counts": dict(sorted(statuses.items())),
            "impact_counts": dict(sorted(impacts.items())),
            "audit_bucket_counts": dict(sorted(buckets.items())),
            "top_translation_notes": top_counter(notes),
            "risk_flag_counts": dict(flags.most_common()),
        }
    return by_category


def main() -> int:
    ledger = run_census()
    ledger_by_id = {row["row_id"]: row for row in ledger}
    if len(ledger_by_id) != len(ledger):
        raise SystemExit("v3 ledger row_id is not unique")

    observations: dict[str, list[dict[str, str]]] = defaultdict(list)
    ignored_nonledger = Counter()
    source_files = []
    for path in sorted(AUDIT_DIR.glob("*.csv")):
        rows = read_csv(path)
        used = 0
        for row in rows:
            row_id = (row.get("row_id") or "").strip()
            verdict = (row.get("audit_verdict") or "").strip()
            if not row_id or verdict not in VALID_VERDICTS:
                continue
            if row_id not in ledger_by_id:
                ignored_nonledger[path.name] += 1
                continue
            observations[row_id].append({
                "source_file": path.name,
                "audit_verdict": verdict,
                "proposed_display_ja": (row.get("proposed_display_ja") or "").strip(),
                "proposed_search_ja": (row.get("proposed_search_ja") or "").strip(),
                "reason_code": (row.get("reason_code") or "").strip(),
                "confidence": (row.get("confidence") or "").strip(),
            })
            used += 1
        if used:
            source_files.append({"file": path.name, "ledger_rows": used})

    resolved: dict[str, dict[str, str]] = {}
    conflicts = []
    duplicate_same_decision = 0
    for row_id, entries in observations.items():
        decisions = {
            (e["audit_verdict"], e["proposed_display_ja"], e["proposed_search_ja"])
            for e in entries
        }
        if len(decisions) == 1:
            resolved[row_id] = entries[-1]
            if len(entries) > 1:
                duplicate_same_decision += 1
        else:
            conflicts.append({
                "row_id": row_id,
                "canonical_tag": ledger_by_id[row_id]["canonical_tag"],
                "category": ledger_by_id[row_id]["category_name"],
                "entries": entries,
            })

    # Conflicted rows are considered audited-but-not-resolved. They stay out of
    # remaining-to-audit but remain a separate blocking queue.
    audited_ids = set(observations)
    remaining = [row for row in ledger if row["row_id"] not in audited_ids]

    verdict_counts = Counter(e["audit_verdict"] for e in resolved.values())
    category_audited = Counter(ledger_by_id[rid]["category_name"] for rid in audited_ids)
    category_remaining = Counter(row["category_name"] for row in remaining)
    unresolved_external = [rid for rid, e in resolved.items() if e["audit_verdict"] == "NEEDS_EXTERNAL_CHECK"]
    unresolved_user = [rid for rid, e in resolved.items() if e["audit_verdict"] == "NEEDS_USER_DECISION"]

    result = {
        "format_version": 2,
        "issue": 70,
        "production_modified": False,
        "initial_ledger_rows": len(ledger),
        "audited_unique_rows": len(audited_ids),
        "resolved_unique_rows": len(resolved),
        "conflicted_unique_rows": len(conflicts),
        "remaining_unaudited_rows": len(remaining),
        "duplicate_same_decision_rows": duplicate_same_decision,
        "verdict_counts_resolved": dict(sorted(verdict_counts.items())),
        "audited_by_category": {k: category_audited.get(k, 0) for k in CATEGORIES},
        "remaining_by_category": {k: category_remaining.get(k, 0) for k in CATEGORIES},
        "unresolved_external_check_rows": len(unresolved_external),
        "unresolved_user_decision_rows": len(unresolved_user),
        "remaining_patterns": remaining_patterns(remaining),
        "source_files": source_files,
        "ignored_nonledger_rows_by_file": dict(ignored_nonledger),
        "conflicts": conflicts,
        "next_step": "continue highest-volume safe pattern batches, then resolve external/user queues before production correction",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
