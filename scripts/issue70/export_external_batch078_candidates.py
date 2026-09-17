#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'docs/issue70/audit'
OUT = AUDIT / 'EXTERNAL_QUEUE_BATCH078_CANDIDATES.csv'
VALID = {'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}

def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def main():
    base: dict[str, dict[str, str]] = {}
    overlays: dict[str, dict[str, str]] = {}
    for path in sorted(AUDIT.glob('*.csv')):
        if path.name == OUT.name:
            continue
        is_overlay = path.name.startswith('external_resolution_')
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for r in rows:
            rid = (r.get('row_id') or '').strip()
            verdict = (r.get('audit_verdict') or '').strip()
            if not rid or verdict not in VALID:
                continue
            item = {
                'row_id': rid,
                'canonical_tag': (r.get('canonical_tag') or '').strip(),
                'category': (r.get('category') or '').strip(),
                'post_count': (r.get('post_count') or '0').strip(),
                'display_ja': (r.get('display_ja') or '').strip(),
                'search_ja': (r.get('search_ja') or '').strip(),
                'translation_note': (r.get('translation_note') or '').strip(),
                'audit_verdict': verdict,
                'source_file': path.name,
                'reason_code': (r.get('reason_code') or '').strip(),
            }
            if is_overlay:
                overlays[rid] = item
            elif rid not in base:
                base[rid] = item
    unresolved = []
    for rid, b in base.items():
        eff = overlays.get(rid, b)
        if eff['audit_verdict'] != 'NEEDS_EXTERNAL_CHECK':
            continue
        unresolved.append({
            'row_id': b['row_id'],
            'canonical_tag': b['canonical_tag'],
            'category': b['category'],
            'post_count': b['post_count'],
            'display_ja': b['display_ja'],
            'search_ja': b['search_ja'],
            'translation_note': b['translation_note'],
            'reason_code': b['reason_code'],
            'source_file': b['source_file'],
            'effective_source_file': eff['source_file'],
        })
    unresolved.sort(key=lambda r: (-int(r.get('post_count') or 0), r['row_id']))
    fields = ['row_id','canonical_tag','category','post_count','display_ja','search_ja','translation_note','reason_code','source_file','effective_source_file']
    with OUT.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(unresolved[:400])
    print({'unresolved_external': len(unresolved), 'candidate_rows': min(400, len(unresolved)), 'production_modified': False})

if __name__ == '__main__':
    main()
