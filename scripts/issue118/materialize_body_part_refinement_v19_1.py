#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SOURCE = Path('docs/issue118/body_part_low_risk_v19/low_risk_body_candidate_v19.csv')
OUT = Path('docs/issue118/body_part_refinement_v19_1')

BOUNDARY_PATTERNS = {
    'genitalia_variant': re.compile(r'(?:^|_)(?:genitalia|genitals)(?:_|$)'),
    'reproductive_anatomy_or_state': re.compile(r'(?:^|_)(?:womb|uterus|uterine|ovary|ovaries|ovum|ova|fetal|fetus|cervix)(?:_|$)'),
    'bust_boundary_variant': re.compile(r'(?:^|_)(?:underbust|overbust|sidebust)(?:_|$)'),
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def stable_rank(key: str) -> str:
    return hashlib.sha256(('issue118-body-v19.1-holdout|' + key).encode('utf-8')).hexdigest()


def main() -> int:
    rows = read_csv(SOURCE)
    if len(rows) != 1470:
        raise SystemExit(f'expected 1470 v19 low-risk rows, got {len(rows)}')

    clean = []
    boundary = []
    counts = Counter()
    for row in rows:
        key = row['identity_key']
        hits = [name for name, pattern in BOUNDARY_PATTERNS.items() if pattern.search(key.lower())]
        if hits:
            boundary.append({'identity_key': key, 'state': 'BODY_BOUNDARY_V19_1', 'risk_flags': '+'.join(hits)})
            for hit in hits:
                counts[hit] += 1
        else:
            clean.append({'identity_key': key, 'state': 'LOW_RISK_BODY_CANDIDATE_V19_1'})

    required = {
        'animal_genitalia_on_humanoid',
        'underbust',
        'twitching_womb',
        'ovaries',
        'ovum_with_heart',
        'fetal_movement',
    }
    boundary_keys = {r['identity_key'] for r in boundary}
    missing = sorted(required - boundary_keys)
    if missing:
        raise SystemExit(f'required v19 holdout counterexamples not captured: {missing}')

    holdout_keys = sorted((r['identity_key'] for r in clean), key=stable_rank)[:120]
    holdout = [
        {'identity_key': key, 'candidate_state': 'LOW_RISK_BODY_HOLDOUT_V19_1', 'human_intent': '', 'review_note': ''}
        for key in holdout_keys
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'low_risk_body_candidate_v19_1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state'], lineterminator='\n')
        w.writeheader(); w.writerows(clean)
    with (OUT / 'new_boundary_v19_1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state','risk_flags'], lineterminator='\n')
        w.writeheader(); w.writerows(boundary)
    with (OUT / 'fresh_holdout_template_v19_1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader(); w.writerows(holdout)

    summary = {
        'issue': 118,
        'mode': 'BODY_PART_REFINEMENT_V19_1_REPRODUCTIVE_VARIANT_SPLIT',
        'source_candidate_rows_v19': len(rows),
        'new_boundary_rows': len(boundary),
        'clean_candidate_rows_v19_1': len(clean),
        'boundary_flag_counts': dict(sorted(counts.items())),
        'required_counterexamples_captured': sorted(required),
        'fresh_holdout_template_rows': len(holdout),
        'rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review fresh 120-row BODY_PART holdout',
    }
    (OUT / 'summary_v19_1.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
