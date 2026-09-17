#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path('docs/issue118/clothing_refinement_v12_3/clothing_clean_v12_3.csv')
OUT = Path('docs/issue118/clothing_refinement_v12_4')

# Discovery-only boundary family learned from v12.3 holdout counterexamples.
# Matching only removes rows from bulk NON_SEXUAL candidacy.
BOUNDARY_PATTERNS = {
    't_back_family': re.compile(r'(?:^|[_/\-])t[_/\-]?back(?:$|[_/\-])', re.I),
    'kini_family': re.compile(r'(?:^|[_/\-])(?:tankini|monokini|trikini)(?:$|[_/\-])', re.I),
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def boundary_flags(key: str) -> list[str]:
    return [name for name, pat in BOUNDARY_PATTERNS.items() if pat.search(key)]


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v12.4-clothing-fresh-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 2687:
        raise SystemExit(f'expected v12.3 clean population 2687, got {len(src)}')

    boundary = []
    clean = []
    for r in src:
        key = r['identity_key']
        flags = boundary_flags(key)
        out = {
            'identity_key': key,
            'boundary_flags': '|'.join(flags),
            'candidate_state': 'CLOTHING_BOUNDARY' if flags else 'CLEAN_FOR_FRESH_HOLDOUT_V12_4',
        }
        (boundary if flags else clean).append(out)

    captured = {r['identity_key'] for r in boundary}
    required = {'t-back', 'tankini'}
    missing = sorted(required - captured)
    if missing:
        raise SystemExit(f'v12.4 failed to capture required counterexamples: {missing}')

    boundary.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v12.4 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','boundary_flags','candidate_state']
    for name, rows in [
        ('clothing_boundary_v12_4.csv', boundary),
        ('clothing_clean_v12_4.csv', clean),
    ]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader()
            w.writerows(rows)

    holdout_fields = ['identity_key','candidate_state','human_intent','review_note']
    with (OUT / 'fresh_holdout_template_v12_4.csv').open('w', encoding='utf-8', newline='') as f:
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
        'mode': 'CLOTHING_REFINEMENT_V12_4_SWIMWEAR_BOUNDARY',
        'source_clean_rows_v12_3': len(src),
        'new_boundary_rows': len(boundary),
        'clean_candidate_rows_v12_4': len(clean),
        'fresh_holdout_template_rows': len(holdout),
        'required_counterexamples_captured': sorted(required),
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
    (OUT / 'summary_v12_4.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
