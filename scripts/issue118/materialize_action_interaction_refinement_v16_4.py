#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path('docs/issue118/action_interaction_refinement_v16_3/ordinary_clean_v16_3.csv')
OUT = Path('docs/issue118/action_interaction_refinement_v16_4')

PATTERNS = [
    ('sexualized_body_display', re.compile(r'(?:^|[_\-/])(?:ass[_-]?on[_-]?glass|bust[_-]?measuring)(?:$|[_\-/])')),
    ('bed_or_strip_context', re.compile(r'(?:^|[_\-/])(?:bed[_-]?invitation|strip[_-]?poker)(?:$|[_\-/])')),
    ('restraint_chain', re.compile(r'(?:^|[_\-/])(?:chained|chain)[_-]?(?:wrists?|ankles?|arms?|legs?)(?:$|[_\-/])')),
    ('intimate_licking', re.compile(r'(?:^|[_\-/])licking[_-]?(?:shoulder|neck|ear|ears|face|thigh|thighs|foot|feet)(?:$|[_\-/])')),
    ('between_legs_contact', re.compile(r"(?:^|[_\-/])(?:arm|arms|hand|hands|head|foot|feet)[_-]?between[_-]?(?:another's|anothers|someone's|someones)?[_-]?legs(?:$|[_\-/])")),
    ('foot_on_thigh', re.compile(r"(?:^|[_\-/])foot[_-]?on[_-]?(?:another's|anothers|someone's|someones)[_-]?thigh(?:$|[_\-/])")),
    ('finger_to_tongue', re.compile(r'(?:^|[_\-/])finger[_-]?to[_-]?tongue(?:$|[_\-/])')),
]

REQUIRED = {
    'ass_on_glass',
    'bust_measuring',
    'bed_invitation',
    'strip_poker',
    'licking_shoulder',
    "foot_on_another's_thigh",
    "arm_between_another's_legs",
    'chained_wrists',
    'finger_to_tongue',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def flags(key: str) -> list[str]:
    k = key.lower()
    return [name for name, pat in PATTERNS if pat.search(k)]


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v16.4-action-ordinary-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 1634:
        raise SystemExit(f'expected v16.3 ordinary clean population 1634, got {len(src)}')

    boundary = []
    clean = []
    for r in src:
        key = r['identity_key']
        hit = flags(key)
        out = {
            'identity_key': key,
            'candidate_state': 'BOUNDARY_REVIEW' if hit else 'ORDINARY_CLEAN',
            'reason': '|'.join(hit) if hit else 'no_new_boundary_cue',
        }
        (boundary if hit else clean).append(out)

    captured = {r['identity_key'] for r in boundary}
    missing = sorted(REQUIRED - captured)
    if missing:
        raise SystemExit(f'v16.4 failed required counterexamples: {missing}')

    boundary.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v16.4 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','candidate_state','reason']
    for name, rows in [('boundary_review_v16_4.csv', boundary), ('ordinary_clean_v16_4.csv', clean)]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader(); w.writerows(rows)

    with (OUT / 'ordinary_fresh_holdout_template_v16_4.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': 'ORDINARY_CLEAN_HOLDOUT_V16_4', 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'ACTION_INTERACTION_REFINEMENT_V16_4_CONTEXT_BOUNDARY',
        'source_ordinary_rows_v16_3': len(src),
        'new_boundary_rows': len(boundary),
        'ordinary_clean_rows_v16_4': len(clean),
        'fresh_holdout_template_rows': len(holdout),
        'required_counterexamples_captured': sorted(REQUIRED),
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
    (OUT / 'summary_v16_4.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
