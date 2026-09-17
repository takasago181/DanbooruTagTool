#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SOURCE = Path('docs/issue118/pathless_low_risk_v23/low_risk_candidate_v23.csv')
OUT = Path('docs/issue118/pathless_structural_safe_v24')

PATTERNS = {
    'calendar_day': re.compile(r'(?:^|_)day$'),
    'anniversary': re.compile(r'(?:^|_)anniversary(?:_|$)'),
    'live_or_tour': re.compile(r'(?:^|_)(?:live_tour|tour)(?:_|$)'),
    'festival_or_fair': re.compile(r'(?:^|_)(?:festival|fair)(?:_|$)'),
    'campaign_or_convention': re.compile(r'(?:^|_)(?:campaign|convention)(?:_|$)'),
    'collaboration': re.compile(r'(?:^|_)(?:collab|collaboration)(?:_|$)'),
    'safe_disambiguator': re.compile(r'_\((?:brand|company|culture|sport)\)$'),
    'pure_year': re.compile(r'^(?:19|20)\d{2}$'),
    'dated_public_event': re.compile(r'^(?:19|20)\d{2}_.+(?:incident|earthquake|tsunami|cyberattack|assassination|disaster)(?:_|$)'),
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def stable_rank(key: str) -> str:
    return hashlib.sha256(('issue118-pathless-v24-holdout|' + key).encode('utf-8')).hexdigest()


def main() -> int:
    source = read_csv(SOURCE)
    if len(source) != 2318:
        raise SystemExit(f'expected 2318 v23 low-risk rows, got {len(source)}')

    selected = []
    residual = []
    counts = Counter()
    for row in source:
        key = row['identity_key']
        hits = [name for name, pattern in PATTERNS.items() if pattern.search(key.lower())]
        if hits:
            selected.append({'identity_key': key, 'state': 'PATHLESS_STRUCTURAL_SAFE_CANDIDATE_V24', 'structural_flags': '+'.join(hits)})
            for hit in hits:
                counts[hit] += 1
        else:
            residual.append({'identity_key': key, 'state': 'PATHLESS_RESIDUAL_UNCLASSIFIED_V24'})

    holdout_n = min(120, len(selected))
    holdout_keys = sorted((r['identity_key'] for r in selected), key=stable_rank)[:holdout_n]
    holdout = [
        {'identity_key': key, 'candidate_state': 'PATHLESS_STRUCTURAL_SAFE_HOLDOUT_V24', 'human_intent': '', 'review_note': ''}
        for key in holdout_keys
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'structural_safe_candidate_v24.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state','structural_flags'], lineterminator='\n')
        w.writeheader(); w.writerows(selected)
    with (OUT / 'residual_unclassified_v24.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state'], lineterminator='\n')
        w.writeheader(); w.writerows(residual)
    with (OUT / 'fresh_holdout_template_v24.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader(); w.writerows(holdout)

    summary = {
        'issue': 118,
        'mode': 'PATHLESS_STRUCTURAL_SAFE_V24',
        'source_rows_v23_low_risk': len(source),
        'structural_safe_candidate_rows': len(selected),
        'residual_unclassified_rows': len(residual),
        'structural_flag_counts': dict(sorted(counts.items())),
        'fresh_holdout_template_rows': len(holdout),
        'selection_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review fixed holdout; if clean, promote only structural-safe candidate set'
    }
    (OUT / 'summary_v24.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
