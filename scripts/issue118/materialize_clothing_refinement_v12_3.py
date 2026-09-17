#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path('docs/issue118/clothing_adversarial_v12_2/clothing_clean_v12_2.csv')
OUT = Path('docs/issue118/clothing_refinement_v12_3')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def tokens(key: str) -> set[str]:
    return {p for p in re.split(r'[^a-z0-9]+', key.lower()) if p}


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v12.3-clothing-fresh-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 2694:
        raise SystemExit(f'expected v12.2 clean population 2694, got {len(src)}')

    boundary = []
    clean = []
    for r in src:
        key = r['identity_key']
        hit = 'panty' in tokens(key)
        out = {
            'identity_key': key,
            'boundary_reason': 'singular_panty_token' if hit else '',
            'candidate_state': 'CLOTHING_BOUNDARY' if hit else 'CLEAN_FOR_FRESH_HOLDOUT_V12_3',
        }
        (boundary if hit else clean).append(out)

    if 'panty_straps' not in {r['identity_key'] for r in boundary}:
        raise SystemExit('v12.3 failed to capture panty_straps counterexample')

    boundary.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v12.3 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','boundary_reason','candidate_state']
    for name, rows in [
        ('panty_boundary_v12_3.csv', boundary),
        ('clothing_clean_v12_3.csv', clean),
    ]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader()
            w.writerows(rows)

    holdout_fields = ['identity_key','candidate_state','human_intent','review_note']
    with (OUT / 'fresh_holdout_template_v12_3.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=holdout_fields, lineterminator='\n')
        w.writeheader()
        for r in holdout:
            w.writerow({
                'identity_key': r['identity_key'],
                'candidate_state': r['candidate_state'],
                'human_intent': '',
                'review_note': '',
            })

    summary = {
        'issue': 118,
        'mode': 'CLOTHING_REFINEMENT_V12_3_PANTY_BOUNDARY',
        'source_clean_rows_v12_2': len(src),
        'new_boundary_rows': len(boundary),
        'clean_candidate_rows_v12_3': len(clean),
        'fresh_holdout_template_rows': len(holdout),
        'required_counterexample_captured': 'panty_straps',
        'boundary_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review new fixed 120-row holdout before any research-sidecar promotion',
    }
    (OUT / 'summary_v12_3.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
