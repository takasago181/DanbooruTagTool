#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path('docs/issue118/action_interaction_refinement_v16_2/ordinary_clean_v16_2.csv')
OUT = Path('docs/issue118/action_interaction_refinement_v16_3')

BODY_TOKENS = {
    'ass','butt','chest','pectoral','pectorals','tongue','ear','ears','navel','womb','uterus',
    'tail','tails','armpit','armpits','thigh','thighs','foot','feet','finger','fingers',
}
CONTACT_TOKENS = {
    'support','grab','grabbing','touch','touching','squeeze','squeezing','tickle','tickling',
    'bite','biting','massage','massaging','stimulation','stimulating','suck','sucking','lick',
    'licking','rub','rubbing','press','pressing','hold','holding','hand','hands','head',
}
EXACT_BOUNDARY = {'giving_wedgie'}

REQUIRED = {
    'ass_support',
    'giving_wedgie',
    "hands_on_another's_chest",
    'finger_sucking',
    'tickling_ass',
    "biting_another's_tongue",
    'pectoral_squeeze',
    'womb_massage',
    'tail_stimulation',
    'tickling_navel',
    'biting_ear',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def tokens(key: str) -> set[str]:
    return {p for p in re.split(r'[^a-z0-9]+', key.lower()) if p}


def boundary_reason(key: str) -> str:
    if key.lower() in EXACT_BOUNDARY:
        return 'explicit_underwear_contact'
    t = tokens(key)
    if t & BODY_TOKENS and t & CONTACT_TOKENS:
        return 'body_site_x_contact_risk'
    return ''


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v16.3-action-ordinary-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 1715:
        raise SystemExit(f'expected v16.2 ordinary clean population 1715, got {len(src)}')

    boundary = []
    clean = []
    for r in src:
        key = r['identity_key']
        reason = boundary_reason(key)
        out = {
            'identity_key': key,
            'candidate_state': 'BOUNDARY_REVIEW' if reason else 'ORDINARY_CLEAN',
            'reason': reason or 'no_body_contact_risk',
        }
        (boundary if reason else clean).append(out)

    captured = {r['identity_key'] for r in boundary}
    missing = sorted(REQUIRED - captured)
    if missing:
        raise SystemExit(f'v16.3 failed required counterexamples: {missing}')

    boundary.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v16.3 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','candidate_state','reason']
    for name, rows in [('boundary_review_v16_3.csv', boundary), ('ordinary_clean_v16_3.csv', clean)]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader(); w.writerows(rows)

    with (OUT / 'ordinary_fresh_holdout_template_v16_3.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': 'ORDINARY_CLEAN_HOLDOUT_V16_3', 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'ACTION_INTERACTION_REFINEMENT_V16_3_BODY_CONTACT_REDTEAM',
        'source_ordinary_rows_v16_2': len(src),
        'body_contact_boundary_rows': len(boundary),
        'ordinary_clean_rows_v16_3': len(clean),
        'fresh_holdout_template_rows': len(holdout),
        'required_counterexamples_captured': sorted(REQUIRED),
        'risk_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review new fixed 120-row holdout before any research-sidecar promotion',
    }
    (OUT / 'summary_v16_3.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
