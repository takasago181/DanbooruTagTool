#!/usr/bin/env python3
"""Generate Issue #70 Copyright audit batch 020.

Closes REVIEW_REQUIRED Copyright rows only when prior semantic notes already
identify a reliable/established Japanese title and the current v3 risk state
contains no structural, collision, disambiguation, ASCII-fallback, or search
coverage defect. Proposal-only; production data is never modified.
"""
from __future__ import annotations

import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / 'docs/issue70/audit'
TMP = ROOT / 'artifacts/issue70-semantic-audit-v3-batch020'
OUT = AUDIT_DIR / 'copyright_curated_review_keep_batch020.csv'
JA_RE = re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
GOOD_NOTES = {
    'established/common Japanese title or official rendering',
    'manual chat curation selected high-confidence Japanese copyright title',
    'single clean Japanese copyright search title',
    'semantic re-curation: title/name judged usable; official/common rendering preferred over literal candidate',
    'semantic re-curation: title/name judged usable; official/common rendering or identity-safe original preferred over literal candidate',
}
ALLOWED_FLAGS = {
    'STATUS_REVIEW_REQUIRED',
    'JA_DISPLAY_NOT_EXACT_SOURCE_EVIDENCE',
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def prior_ids() -> set[str]:
    ids: set[str] = set()
    for path in AUDIT_DIR.glob('*.csv'):
        if path.name == OUT.name:
            continue
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for row in rows:
            row_id = (row.get('row_id') or '').strip()
            verdict = (row.get('audit_verdict') or '').strip()
            if row_id and verdict:
                ids.add(row_id)
    return ids


def run_census() -> list[dict[str, str]]:
    if TMP.exists():
        shutil.rmtree(TMP)
    subprocess.run([
        sys.executable,
        str(ROOT / 'scripts/issue70/audit_semantic_risk_v3.py'),
        '--out', str(TMP),
        '--sample-per-category', '300',
    ], cwd=ROOT, check=True)
    return read_csv(TMP / 'audit_ledger_template.csv')


def flagset(value: str) -> set[str]:
    return {x.strip() for x in (value or '').split('|') if x.strip()}


def main() -> int:
    audited = prior_ids()
    rows: list[dict[str, str]] = []
    for row in run_census():
        if row.get('row_id') in audited:
            continue
        if row.get('category_name') != 'Copyright':
            continue
        if row.get('translation_status') != 'REVIEW_REQUIRED':
            continue
        if (row.get('translation_note') or '') not in GOOD_NOTES:
            continue
        display = (row.get('display_ja') or '').strip()
        if not display or not JA_RE.search(display):
            continue
        flags = flagset(row.get('risk_flags') or '')
        if not flags.issubset(ALLOWED_FLAGS):
            continue
        rows.append({
            'row_id': row['row_id'],
            'canonical_tag': row['canonical_tag'],
            'post_count': row.get('post_count') or '',
            'display_ja': display,
            'search_ja': row.get('search_ja') or '',
            'translation_note': row.get('translation_note') or '',
            'risk_flags': row.get('risk_flags') or '',
            'audit_verdict': 'KEEP',
            'proposed_display_ja': '',
            'proposed_search_ja': '',
            'reason_code': 'CURATED_REVIEW_COPYRIGHT_TITLE_NO_BLOCKING_RISK',
            'confidence': 'HIGH',
            'evidence_refs': 'prior semantic re-curation note + v3 no-blocking-risk classification',
            'audit_note': '既に公式/一般日本語タイトルとして監修済みで、残存flagはREVIEW状態またはsource完全一致差のみ。構造・同名衝突・曖昧性・検索欠落がないため現表示を維持。',
            'approval_status': 'PROPOSED',
        })
    rows.sort(key=lambda r: (-int(r['post_count'] or 0), r['row_id']))
    fields = [
        'row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','risk_flags',
        'audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence',
        'evidence_refs','audit_note','approval_status'
    ]
    write_csv(OUT, rows, fields)
    print({'rows': len(rows), 'production_modified': False})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
