#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path('docs/issue118/action_interaction_refinement_v16_4/ordinary_clean_v16_4.csv')
OUT = Path('docs/issue118/action_interaction_refinement_v16_5')

BOUNDARY_PATTERNS = [
    ('strip_game', re.compile(r'(?:^|[_\-/])strip[_-]?(?:mahjong|poker|game)(?:$|[_\-/])')),
    ('clothing_lift_or_tug', re.compile(r'(?:^|[_\-/])(?:babydoll[_-]?lift|towel[_-]?tug)(?:$|[_\-/])')),
    ('mating_context', re.compile(r'(?:^|[_\-/])mating[_-]?season(?:$|[_\-/])')),
    ('ambiguous_licking_tip', re.compile(r'(?:^|[_\-/])licking[_-]?tip(?:$|[_\-/])')),
    ('riding_person', re.compile(r'(?:^|[_\-/])riding[_-]?person(?:$|[_\-/])')),
]

INTIMATE_PATTERNS = [
    ('hand_on_intimate_body_site', re.compile(r"(?:^|[_\-/])hands?[_-]?on[_-]?(?:another's|anothers|someone's|someones)[_-]?(?:hip|hips|waist|stomach)(?:$|[_\-/])")),
]

REQUIRED_BOUNDARY = {
    'strip_mahjong',
    'babydoll_lift',
    'towel_tug',
    'mating_season',
    'licking_tip',
    'riding_person',
}
REQUIRED_INTIMATE = {
    "hand_on_another's_hip",
    "hand_on_another's_waist",
    "hand_on_another's_stomach",
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def classify(key: str) -> tuple[str, str]:
    k = key.lower()
    for name, pat in BOUNDARY_PATTERNS:
        if pat.search(k):
            return 'BOUNDARY_REVIEW', name
    for name, pat in INTIMATE_PATTERNS:
        if pat.search(k):
            return 'MOVE_TO_INTIMATE_GENERAL', name
    return 'ORDINARY_CLEAN', 'no_new_boundary_cue'


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v16.5-action-ordinary-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 1624:
        raise SystemExit(f'expected v16.4 ordinary clean population 1624, got {len(src)}')

    boundary = []
    intimate = []
    clean = []
    for r in src:
        key = r['identity_key']
        state, reason = classify(key)
        out = {'identity_key': key, 'candidate_state': state, 'reason': reason}
        if state == 'BOUNDARY_REVIEW':
            boundary.append(out)
        elif state == 'MOVE_TO_INTIMATE_GENERAL':
            intimate.append(out)
        else:
            clean.append(out)

    bkeys = {r['identity_key'] for r in boundary}
    ikeys = {r['identity_key'] for r in intimate}
    missing_b = sorted(REQUIRED_BOUNDARY - bkeys)
    missing_i = sorted(REQUIRED_INTIMATE - ikeys)
    if missing_b or missing_i:
        raise SystemExit(f'v16.5 failed required capture boundary={missing_b} intimate={missing_i}')

    boundary.sort(key=lambda r: r['identity_key'])
    intimate.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v16.5 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','candidate_state','reason']
    for name, rows in [
        ('boundary_review_v16_5.csv', boundary),
        ('moved_intimate_v16_5.csv', intimate),
        ('ordinary_clean_v16_5.csv', clean),
    ]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader(); w.writerows(rows)

    with (OUT / 'ordinary_fresh_holdout_template_v16_5.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': 'ORDINARY_CLEAN_HOLDOUT_V16_5', 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'ACTION_INTERACTION_REFINEMENT_V16_5_FINAL_FAMILY_SPLIT',
        'source_ordinary_rows_v16_4': len(src),
        'new_boundary_rows': len(boundary),
        'moved_intimate_rows': len(intimate),
        'ordinary_clean_rows_v16_5': len(clean),
        'fresh_holdout_template_rows': len(holdout),
        'required_boundary_counterexamples_captured': sorted(REQUIRED_BOUNDARY),
        'required_intimate_moves_captured': sorted(REQUIRED_INTIMATE),
        'rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review new fixed 120-row ordinary holdout before any research-sidecar promotion',
    }
    (OUT / 'summary_v16_5.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
