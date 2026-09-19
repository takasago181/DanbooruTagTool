#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 022.

Resolve conservative REVIEW_REQUIRED short kana/kanji Character names only when
all identity evidence is strong: the current Japanese display exactly matches a
verified alias for the canonical tag, related-Copyright top1 coverage is >=0.80,
and the only v3 flag is STATUS_REVIEW_REQUIRED. No display correction is made.

Proposal-only; production data is never modified.
"""
from __future__ import annotations

import csv
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / 'docs/issue70/audit'
TMP = ROOT / 'artifacts/issue70-semantic-audit-v3-batch022'
OUT = AUDIT_DIR / 'character_verified_shortname_keep_batch022.csv'
NOTES = {
    'short kana-only candidate is too ambiguous without contextual search evidence',
    'short kanji-only candidate is too ambiguous without contextual search evidence',
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def prior_ids() -> set[str]:
    ids: set[str] = set()
    for path in AUDIT_DIR.glob('*.csv'):
        if path.name == OUT.name:
            continue
        try: rows = read_csv(path)
        except Exception: continue
        for row in rows:
            rid = (row.get('row_id') or '').strip()
            if rid and (row.get('audit_verdict') or '').strip():
                ids.add(rid)
    return ids


def run_census() -> list[dict[str, str]]:
    if TMP.exists(): shutil.rmtree(TMP)
    subprocess.run([
        sys.executable, str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),
        '--out', str(TMP), '--sample-per-category', '300'
    ], cwd=ROOT, check=True)
    return read_csv(TMP/'audit_ledger_template.csv')


def norm(value: str) -> str:
    value = unicodedata.normalize('NFKC', value or '').strip().lower()
    value = value.replace('・', ' ').replace('_', ' ')
    return ' '.join(value.split())


def verified_terms(row: dict[str, str]) -> set[str]:
    return {norm(x) for x in (row.get('verified_aliases') or '').split('|') if x.strip()}


def flags(row: dict[str, str]) -> set[str]:
    return {x.strip() for x in (row.get('risk_flags') or '').split('|') if x.strip()}


def coverage(row: dict[str, str]) -> float:
    try: return float(row.get('related_copyright_top1_coverage') or 0)
    except ValueError: return 0.0


def main() -> int:
    audited = prior_ids(); rows: list[dict[str, str]] = []
    for row in run_census():
        if row.get('row_id') in audited:
            continue
        if row.get('category_name') != 'Character' or row.get('translation_status') != 'REVIEW_REQUIRED':
            continue
        if (row.get('translation_note') or '') not in NOTES:
            continue
        if flags(row) != {'STATUS_REVIEW_REQUIRED'}:
            continue
        display = (row.get('display_ja') or '').strip()
        if not display or norm(display) not in verified_terms(row):
            continue
        related = (row.get('related_copyright_top1') or '').strip()
        if not related or coverage(row) < 0.80:
            continue
        rows.append({
            'row_id': row['row_id'],
            'canonical_tag': row['canonical_tag'],
            'post_count': row.get('post_count') or '',
            'display_ja': display,
            'search_ja': row.get('search_ja') or '',
            'verified_aliases': row.get('verified_aliases') or '',
            'related_copyright_top1': related,
            'related_copyright_top1_coverage': row.get('related_copyright_top1_coverage') or '',
            'translation_note': row.get('translation_note') or '',
            'risk_flags': row.get('risk_flags') or '',
            'audit_verdict': 'KEEP',
            'proposed_display_ja': '',
            'proposed_search_ja': '',
            'reason_code': 'VERIFIED_ALIAS_STRONG_COPYRIGHT_CONTEXT_SHORT_NAME',
            'confidence': 'HIGH',
            'evidence_refs': 'verified_aliases exact match + related_copyright_top1 coverage >= 0.80',
            'audit_note': '短名ゆえ旧処理では保守的REVIEWだったが、canonical tagの検証済みAliasに表示名が直接一致し、作品関係も強く、他のsemantic risk flagがないため現表示を維持。',
            'approval_status': 'PROPOSED',
        })
    rows.sort(key=lambda r: (-int(r['post_count'] or 0), r['row_id']))
    fields = [
        'row_id','canonical_tag','post_count','display_ja','search_ja','verified_aliases',
        'related_copyright_top1','related_copyright_top1_coverage','translation_note','risk_flags',
        'audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence',
        'evidence_refs','audit_note','approval_status'
    ]
    write_csv(OUT, rows, fields)
    print({'rows': len(rows), 'production_modified': False})
    return 0


if __name__ == '__main__': raise SystemExit(main())
