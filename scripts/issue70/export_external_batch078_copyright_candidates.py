#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'docs/issue70/audit'
CANDIDATES = AUDIT / 'EXTERNAL_QUEUE_BATCH078_CANDIDATES.csv'
ROOT_QUEUE = AUDIT / 'EXTERNAL_QUEUE_LIVE.csv'
OUT = AUDIT / 'EXTERNAL_QUEUE_BATCH078_COPYRIGHT_CANDIDATES.csv'

def read(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def main():
    candidates = read(CANDIDATES)
    root = {r['row_id']: r for r in read(ROOT_QUEUE)}
    rows = []
    for c in candidates:
        r = root.get(c['row_id'])
        if not r or r.get('category') != 'Copyright':
            continue
        rows.append({
            'row_id': c['row_id'],
            'canonical_tag': c['canonical_tag'],
            'post_count': c['post_count'],
            'display_ja': c['display_ja'],
            'search_ja': c['search_ja'],
            'translation_note': c['translation_note'],
            'reason_code': c['reason_code'],
            'source_file': c['source_file'],
        })
    fields = ['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','reason_code','source_file']
    with OUT.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print({'effective_candidate_input': len(candidates), 'copyright_candidates': len(rows), 'production_modified': False})

if __name__ == '__main__':
    main()
