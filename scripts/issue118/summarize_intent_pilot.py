#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('docs/issue118')
SAMPLE = ROOT / 'intent_pilot_sample_v1.csv'
REVIEWS = ROOT / 'reviews'
OUT = ROOT / 'intent_pilot_review_summary_v1.json'
LEDGER = ROOT / 'intent_pilot_review_ledger_v1.csv'
VALID = {'SEXUAL','NON_SEXUAL','CONTEXTUAL'}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main() -> int:
    sample = read_csv(SAMPLE)
    if len(sample) != 700:
        raise SystemExit(f'expected 700 sample rows, got {len(sample)}')
    sidx = {r['identity_key']: r for r in sample}
    if len(sidx) != 700:
        raise SystemExit('sample identity duplicate')

    review_rows = []
    for path in sorted(REVIEWS.glob('chunk_*_review_v1.csv')):
        review_rows.extend(read_csv(path))
    if len(review_rows) != 700:
        raise SystemExit(f'expected 700 review rows, got {len(review_rows)}')
    if len({r['identity_key'] for r in review_rows}) != 700:
        raise SystemExit('review identity duplicate')
    missing = set(sidx) - {r['identity_key'] for r in review_rows}
    extra = {r['identity_key'] for r in review_rows} - set(sidx)
    if missing or extra:
        raise SystemExit(f'review/sample mismatch missing={len(missing)} extra={len(extra)}')

    overall = Counter()
    by_stratum: dict[str, Counter] = defaultdict(Counter)
    by_membership: dict[str, Counter] = defaultdict(Counter)
    by_general_root: dict[str, Counter] = defaultdict(Counter)
    by_special_family: dict[str, Counter] = defaultdict(Counter)
    ledger = []

    for rr in review_rows:
        sr = sidx[rr['identity_key']]
        status = rr.get('pilot_review_status','').strip()
        cls = rr.get('reviewed_class','').strip()
        bucket = cls if status == 'REVIEWED' and cls in VALID else 'UNCLASSIFIED'
        overall[bucket] += 1
        stratum = sr['sample_stratum']
        by_stratum[stratum][bucket] += 1
        membership = ('OVERLAP' if sr['is_general']=='YES' and sr['is_special']=='YES'
                      else 'GENERAL_ONLY' if sr['is_general']=='YES'
                      else 'SPECIAL_ONLY' if sr['is_special']=='YES'
                      else 'NEITHER')
        by_membership[membership][bucket] += 1
        gp = sr.get('general_primary_path','').split('/')[0] if sr.get('general_primary_path','') else '(none)'
        by_general_root[gp][bucket] += 1
        sf = sr.get('generation_family','') or '(none)'
        by_special_family[sf][bucket] += 1
        ledger.append({
            'identity_key': rr['identity_key'],
            'sample_stratum': stratum,
            'membership': membership,
            'general_primary_path': sr.get('general_primary_path',''),
            'special_id': sr.get('special_id',''),
            'generation_family': sr.get('generation_family',''),
            'reviewed_class': cls,
            'pilot_review_status': status,
            'review_reason': rr.get('review_reason',''),
        })

    fields = list(ledger[0])
    with LEDGER.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader(); w.writerows(ledger)

    def norm(d):
        return {k: dict(sorted(v.items())) for k,v in sorted(d.items())}

    summary = {
        'issue': 118,
        'mode': 'REVIEWED_700_PILOT_SUMMARY_V1',
        'pilot_rows': 700,
        'reviewed_rows': sum(overall[c] for c in VALID),
        'unclassified_rows': overall['UNCLASSIFIED'],
        'overall_class_counts': dict(sorted(overall.items())),
        'by_stratum': norm(by_stratum),
        'by_membership': norm(by_membership),
        'by_general_root': norm(by_general_root),
        'by_special_family': norm(by_special_family),
        'interpretation_guard': 'This is a deliberately stratified pilot, not a prevalence estimate for the 31,752-identity union.',
        'production_mutated': 'NO',
        'issue117_code_mutated': 'NO',
    }
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary['overall_class_counts'], sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
