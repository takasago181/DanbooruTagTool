#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path('docs/issue118/action_interaction_refinement_v16_7/ordinary_clean_v16_7.csv')
OUT = Path('docs/issue118/action_interaction_refinement_v16_8')

PATTERNS = [
    ('sexualized_dance', re.compile(r'(?:^|[_\-/])twerking(?:$|[_\-/])')),
    ('intimate_body_site_contact', re.compile(r'(?:^|[_\-/])finger[_-]?in[_-]?navel(?:$|[_\-/])')),
    ('ass_contact_display', re.compile(r'(?:^|[_\-/])face[_-]?in[_-]?(?:ass|butt)(?:$|[_\-/])')),
    ('bulge_manipulation', re.compile(r'(?:^|[_\-/])bulge[_-]?(?:lift|press|grab|touch|squeeze)(?:$|[_\-/])')),
    ('adult_play_term', re.compile(r'(?:^|[_\-/])lotion[_-]?play(?:$|[_\-/])')),
    ('boundary_clothing_adjustment', re.compile(r'(?:^|[_\-/])adjusting[_-]?(?:buruma|panties|underwear|bra|thong|bikini|swimsuit)(?:$|[_\-/])')),
]

REQUIRED = {
    'twerking',
    'finger_in_navel',
    'face_in_ass',
    'bulge_lift',
    'bulge_press',
    'lotion_play',
    'adjusting_buruma',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def flags(key: str) -> list[str]:
    k = key.lower()
    return [name for name, pat in PATTERNS if pat.search(k)]


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v16.8-action-ordinary-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 1590:
        raise SystemExit(f'expected v16.7 ordinary clean population 1590, got {len(src)}')

    boundary, clean = [], []
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
        raise SystemExit(f'v16.8 failed required counterexamples: {missing}')

    boundary.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v16.8 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','candidate_state','reason']
    for name, rows in [('boundary_review_v16_8.csv', boundary), ('ordinary_clean_v16_8.csv', clean)]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)

    with (OUT / 'ordinary_fresh_holdout_template_v16_8.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n'); w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': 'ORDINARY_CLEAN_HOLDOUT_V16_8', 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'ACTION_INTERACTION_REFINEMENT_V16_8_BODY_DISPLAY_PLAY_SPLIT',
        'source_ordinary_rows_v16_7': len(src),
        'new_boundary_rows': len(boundary),
        'ordinary_clean_rows_v16_8': len(clean),
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
    (OUT / 'summary_v16_8.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
