#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SRC = Path('docs/issue118/action_interaction_refinement_v16_9/ordinary_clean_v16_9.csv')
OUT = Path('docs/issue118/action_interaction_refinement_v16_10')

BODY_SITES = {
    'ass','butt','chest','pectoral','pectorals','breast','breasts','thigh','thighs','leg','legs',
    'foot','feet','toe','toes','nape','neck','back','stomach','belly','navel','waist','hip','hips',
    'crotch','bulge','lips','tongue','mouth','armpit','armpits',
}
CONTACT_OR_DISPLAY = {
    'poke','poking','lick','licking','kiss','kissing','massage','massaging','hold','holding','hand','hands',
    'finger','fingers','touch','touching','press','pressing','squeeze','squeezing','rub','rubbing','grab','grabbing',
    'pillow','kabedon','caress','caressing','stroke','stroking',
}
UNDERGARMENT = {'pantyhose','tights','stockings','panties','panty','underwear','bra','buruma','thong'}
INSIDE_MANIPULATION = {'in','inside','under','lift','lifting','pull','pulling','tug','tugging','grab','grabbing','adjusting'}
RELATIONSHIP_CUES = {'hetero','homosexual','homo','yuri','yaoi','incest','ntr','netorare','netori'}
FOOD_OR_SUBSTANCE = {'chocolate','cream','honey','syrup','lotion','oil','food'}

REQUIRED = {
    'chocolate_on_legs',
    'pectoral_pillow',
    'hand_in_own_pantyhose',
    'foot_kabedon',
    'poking_ass',
    "holding_another's_wrists",
    'hand_in_pantyhose',
    'licking_back',
    'implied_hetero',
    "hand_on_another's_nape",
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def tokens(key: str) -> set[str]:
    return {p for p in re.split(r'[^a-z0-9]+', key.lower()) if p}


def flags(key: str) -> list[str]:
    k = key.lower()
    t = tokens(k)
    out = []
    if t & BODY_SITES and t & CONTACT_OR_DISPLAY:
        out.append('body_site_x_contact_or_display')
    if t & UNDERGARMENT and t & INSIDE_MANIPULATION:
        out.append('undergarment_inside_or_manipulation')
    if t & RELATIONSHIP_CUES:
        out.append('relationship_sexual_context_cue')
    if t & FOOD_OR_SUBSTANCE and t & BODY_SITES:
        out.append('substance_on_body_site')
    if re.search(r"(?:^|[_\-/])holding[_-]?(?:another's|anothers|someone's|someones)[_-]?wrists?(?:$|[_\-/])", k):
        out.append('restraint_like_wrist_holding')
    if re.search(r'(?:^|[_\-/])foot[_-]?kabedon(?:$|[_\-/])', k):
        out.append('foot_kabedon_boundary')
    return sorted(set(out))


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v16.10-action-convergence-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 1570:
        raise SystemExit(f'expected v16.9 ordinary clean population 1570, got {len(src)}')

    boundary, clean = [], []
    counts = Counter()
    for r in src:
        key = r['identity_key']
        hit = flags(key)
        out = {
            'identity_key': key,
            'candidate_state': 'BOUNDARY_REVIEW' if hit else 'ORDINARY_CLEAN',
            'risk_flags': '|'.join(hit),
        }
        if hit:
            boundary.append(out)
            counts.update(hit)
        else:
            clean.append(out)

    captured = {r['identity_key'] for r in boundary}
    missing = sorted(REQUIRED - captured)
    if missing:
        raise SystemExit(f'v16.10 failed required counterexamples: {missing}')

    boundary.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v16.10 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','candidate_state','risk_flags']
    for name, rows in [('boundary_review_v16_10.csv', boundary), ('ordinary_clean_v16_10.csv', clean)]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)

    with (OUT / 'ordinary_fresh_holdout_template_v16_10.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n'); w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': 'ORDINARY_CLEAN_HOLDOUT_V16_10', 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'ACTION_INTERACTION_REFINEMENT_V16_10_CONVERGENCE_SWEEP',
        'source_ordinary_rows_v16_9': len(src),
        'conservative_boundary_rows': len(boundary),
        'ordinary_clean_rows_v16_10': len(clean),
        'risk_flag_counts': dict(sorted(counts.items())),
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
        'next_gate': 'review fresh holdout; if it still leaks sexual/contextual counterexamples, stop whole-cluster bulk promotion and split into narrower safe subclusters',
    }
    (OUT / 'summary_v16_10.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
