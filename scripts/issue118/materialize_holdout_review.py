#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path('docs/issue118/holdout')
CHUNKS = ROOT / 'review_chunks'
REVIEWS = ROOT / 'reviews'
REVIEWS.mkdir(parents=True, exist_ok=True)

# Manual semantic review exceptions from the 240-row holdout. Every holdout row was
# inspected; these are the rows where the candidate rule's proposed class is not
# accepted as the semantic verdict.
OVERRIDES = {
    'lipstick_mark_on_ass': ('CONTEXTUAL', 'reviewed: body-mark concept has substantial ordinary/stylistic and sexualized use'),
    'looking_at_panties': ('CONTEXTUAL', 'reviewed: gaze target can occur in ordinary/comedic and sexualized contexts'),
}


def main() -> int:
    total = 0
    counts: dict[str, int] = {}
    for src in sorted(CHUNKS.glob('chunk_*.csv')):
        with src.open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        out = REVIEWS / src.name.replace('.csv', '_review_v1.csv')
        with out.open('w', encoding='utf-8', newline='') as f:
            fields = ['identity_key','candidate_rule','candidate_class','reviewed_class','review_status','review_reason']
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader()
            for r in rows:
                key = r['identity_key']
                candidate = r['candidate_class']
                if key in OVERRIDES:
                    reviewed, reason = OVERRIDES[key]
                else:
                    reviewed = candidate
                    reason = 'manual semantic review accepted candidate class for this holdout identity'
                counts[reviewed] = counts.get(reviewed, 0) + 1
                total += 1
                w.writerow({
                    'identity_key': key,
                    'candidate_rule': r['candidate_rule'],
                    'candidate_class': candidate,
                    'reviewed_class': reviewed,
                    'review_status': 'REVIEWED',
                    'review_reason': reason,
                })
    if total != 240:
        raise SystemExit(f'expected 240 holdout rows, got {total}')
    print('ISSUE118_HOLDOUT_REVIEW_COUNTS=' + repr(dict(sorted(counts.items()))))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
