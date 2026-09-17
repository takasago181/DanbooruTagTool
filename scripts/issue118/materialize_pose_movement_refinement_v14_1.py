#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path('docs/issue118/pose_movement_refinement_v14/pose_clean_v14.csv')
OUT = Path('docs/issue118/pose_movement_refinement_v14_1')

PATTERNS = [
    ('bulge_emphasis', re.compile(r'(?:^|[_\-/])(?:object[_-]?on[_-]?bulge|bulge[_-]?presentation)(?:$|[_\-/])')),
    ('tanline_presentation', re.compile(r'(?:^|[_\-/])presenting[_-]?tanlines(?:$|[_\-/])')),
    ('hips_in_air', re.compile(r'(?:^|[_\-/])hips[_-]?in[_-]?air(?:$|[_\-/])')),
    ('explicit_ass_pose_label', re.compile(r'(?:^|[_\-/])huge[_-]?ass[_-]?lying[_-]?on[_-]?couch[_-]?pose(?:$|[_\-/])')),
    ('arched_back_boundary', re.compile(r'(?:^|[_\-/])arched[_-]?back(?:$|[_\-/])')),
    ('pole_dancing', re.compile(r'(?:^|[_\-/])pole[_-]?danc(?:e|ing|ed)(?:$|[_\-/])')),
]

REQUIRED = {
    'object_on_bulge',
    'presenting_tanlines',
    'hips_in_air',
    'huge_ass_lying_on_couch_pose_(meme)',
    'arched_back',
    'pole_dancing',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def flags(key: str) -> list[str]:
    k = key.lower()
    return [name for name, pat in PATTERNS if pat.search(k)]


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v14.1-pose-fresh-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 717:
        raise SystemExit(f'expected v14 clean population 717, got {len(src)}')

    boundary = []
    clean = []
    for r in src:
        key = r['identity_key']
        hit = flags(key)
        out = {
            'identity_key': key,
            'boundary_flags': '|'.join(hit),
            'candidate_state': 'POSE_BOUNDARY' if hit else 'CLEAN_FOR_FRESH_HOLDOUT_V14_1',
        }
        (boundary if hit else clean).append(out)

    captured = {r['identity_key'] for r in boundary}
    missing = sorted(REQUIRED - captured)
    if missing:
        raise SystemExit(f'v14.1 failed to capture required counterexamples: {missing}')

    boundary.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v14.1 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','boundary_flags','candidate_state']
    for name, rows in [('pose_boundary_v14_1.csv', boundary), ('pose_clean_v14_1.csv', clean)]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader(); w.writerows(rows)

    with (OUT / 'fresh_holdout_template_v14_1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': r['candidate_state'], 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'POSE_MOVEMENT_REFINEMENT_V14_1_COUNTEREXAMPLE_SPLIT',
        'source_clean_rows_v14': len(src),
        'new_boundary_rows': len(boundary),
        'clean_candidate_rows_v14_1': len(clean),
        'fresh_holdout_template_rows': len(holdout),
        'required_counterexamples_captured': sorted(REQUIRED),
        'pole_dancing_pattern_morphology_fixed': 'YES',
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
    (OUT / 'summary_v14_1.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
