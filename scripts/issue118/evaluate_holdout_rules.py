#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path('docs/issue118/holdout')
REVIEWS = ROOT / 'reviews'
OUT = ROOT / 'rule_holdout_evaluation_v1.json'


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main() -> int:
    rows = []
    for p in sorted(REVIEWS.glob('chunk_*_review_v1.csv')):
        rows.extend(read_csv(p))
    if len(rows) != 240:
        raise SystemExit(f'expected 240 reviewed holdout rows, got {len(rows)}')

    by_rule = {}
    for rule in sorted({r['candidate_rule'] for r in rows}):
        rr = [r for r in rows if r['candidate_rule'] == rule]
        target = rr[0]['candidate_class']
        counts = Counter(r['reviewed_class'] for r in rr)
        misses = [r['identity_key'] for r in rr if r['reviewed_class'] != target]
        by_rule[rule] = {
            'target': target,
            'matched': len(rr),
            'reviewed_class_counts': dict(sorted(counts.items())),
            'target_precision': (len(rr)-len(misses))/len(rr),
            'non_target_count': len(misses),
            'non_target_examples': misses,
        }

    # Conservative v2: remove the two General roots that produced semantic
    # contextual counterexamples in independent holdout.
    sample = read_csv(ROOT / 'rule_holdout_sample_v1.csv')
    review = {r['identity_key']: r['reviewed_class'] for r in rows}
    safe_v2_roots = {
        'COMPOSITION_CAMERA','HAIR_FACE','LIGHT_TIME_WEATHER',
        'LIVING_NATURE','PLACE_BACKGROUND','TEXT_SYMBOL'
    }
    v2 = [r for r in sample if r['candidate_rule']=='AUTO_NONSEX_SAFE_GENERAL_ROOTS_ANYCONF_V1'
          and r['general_primary_path'].split('/')[0] in safe_v2_roots]
    v2_counts = Counter(review[r['identity_key']] for r in v2)
    v2_misses = [r['identity_key'] for r in v2 if review[r['identity_key']] != 'NON_SEXUAL']

    obj = {
        'issue': 118,
        'mode': 'INDEPENDENT_RULE_HOLDOUT_EVALUATION_V1',
        'holdout_rows': len(rows),
        'by_candidate_rule': by_rule,
        'refined_nonsexual_v2': {
            'rule': 'AUTO_NONSEX_SAFE_GENERAL_ROOTS_V2',
            'roots': sorted(safe_v2_roots),
            'matched': len(v2),
            'reviewed_class_counts': dict(sorted(v2_counts.items())),
            'target_precision': (len(v2)-len(v2_misses))/len(v2) if v2 else None,
            'non_target_count': len(v2_misses),
            'non_target_examples': v2_misses,
            'removed_roots_after_holdout_counterexamples': ['COLOR_APPEARANCE','GAZE_ORIENTATION'],
        },
        'production_classification_written': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
    }
    OUT.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(obj['refined_nonsexual_v2'], sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
