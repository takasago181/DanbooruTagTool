#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path('docs/issue118/action_interaction_refinement_v16_5/ordinary_clean_v16_5.csv')
OUT = Path('docs/issue118/action_interaction_refinement_v16_6')

BOUNDARY_PATTERNS = [
    ('straddling_family', re.compile(r'(?:^|[_\-/])(?:thigh[_-]?straddling|straddling[_-]?(?:thigh|waist|hips?|person))(?:$|[_\-/])')),
    ('licking_another_body', re.compile(r"(?:^|[_\-/])licking[_-]?(?:another's|anothers|someone's|someones)[_-]?(?:arm|arms|leg|legs|hand|hands|shoulder|shoulders|back|chest|stomach|neck|ear|ears|foot|feet|thigh|thighs)(?:$|[_\-/])")),
    ('foot_on_another_body', re.compile(r"(?:^|[_\-/])foot[_-]?on[_-]?(?:another's|anothers|someone's|someones)[_-]?(?:chest|back|stomach|shoulder|shoulders|thigh|thighs|hip|hips)(?:$|[_\-/])")),
    ('footwear_fetish_cue', re.compile(r'(?:^|[_\-/])(?:smelling|sniffing)[_-]?(?:shoe|shoes|sock|socks|footwear)(?:$|[_\-/])')),
]

INTIMATE_PATTERNS = [
    ('arms_around_neck', re.compile(r'(?:^|[_\-/])arms?[_-]?around[_-]?neck(?:$|[_\-/])')),
    ('shared_bed', re.compile(r'(?:^|[_\-/])shared[_-]?bed(?:$|[_\-/])')),
]

REQUIRED_BOUNDARY = {
    'thigh_straddling',
    "licking_another's_arm",
    "foot_on_another's_chest",
    'smelling_shoe',
}
REQUIRED_INTIMATE = {'arms_around_neck', 'shared_bed'}


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
    return hashlib.sha256(('issue118-v16.6-action-ordinary-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 1611:
        raise SystemExit(f'expected v16.5 ordinary clean population 1611, got {len(src)}')

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
        raise SystemExit(f'v16.6 failed required capture boundary={missing_b} intimate={missing_i}')

    boundary.sort(key=lambda r: r['identity_key'])
    intimate.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v16.6 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','candidate_state','reason']
    for name, rows in [
        ('boundary_review_v16_6.csv', boundary),
        ('moved_intimate_v16_6.csv', intimate),
        ('ordinary_clean_v16_6.csv', clean),
    ]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader(); w.writerows(rows)

    with (OUT / 'ordinary_fresh_holdout_template_v16_6.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': 'ORDINARY_CLEAN_HOLDOUT_V16_6', 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'ACTION_INTERACTION_REFINEMENT_V16_6_FETISH_INTIMATE_SPLIT',
        'source_ordinary_rows_v16_5': len(src),
        'new_boundary_rows': len(boundary),
        'moved_intimate_rows': len(intimate),
        'ordinary_clean_rows_v16_6': len(clean),
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
    (OUT / 'summary_v16_6.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
