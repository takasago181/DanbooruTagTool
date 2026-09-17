#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SRC = Path('docs/issue118/action_interaction_refinement_v16_8/ordinary_clean_v16_8.csv')
OUT = Path('docs/issue118/action_interaction_refinement_v16_9')

SEXUALIZED_LANGUAGE = {
    'slut','horny','lewd','ecchi','erotic','ero','fetish','pervert','perverted','sexy','aphrodisiac',
}
RESTRAINT_WORDS = {
    'chain','chains','chained','bound','bondage','rope','ropes','tied','handcuff','handcuffs','gag','gagged','collar','leash','shackle','shackles',
}

PATTERNS = [
    ('ear_intimate_contact', re.compile(r'(?:^|[_\-/])(?:blowing|whispering|licking|kissing|biting)[_-]?(?:in[_-]?)?(?:another(?:s)?[_-]?)?ear(?:s)?(?:$|[_\-/])')),
    ('foot_toe_fetish_contact', re.compile(r'(?:^|[_\-/])(?:finger|fingers|hand|hands|mouth|tongue|face)[_-]?(?:in|between|on|to)[_-]?(?:another(?:s)?[_-]?)?(?:foot|feet|toe|toes)(?:$|[_\-/])')),
    ('hands_on_neck', re.compile(r"(?:^|[_\-/])hands?[_-]?on[_-]?(?:another's|anothers|someone's|someones)[_-]?neck(?:$|[_\-/])")),
    ('intimate_clothing_manipulation', re.compile(r'(?:^|[_\-/])(?:lift|lifting|pull|pulling|tug|tugging|grab|grabbing|adjusting)[_-]?(?:panty|panties|underwear|bra|bikini|swimsuit|buruma|skirt|shorts|towel)(?:$|[_\-/])')),
    ('body_display_ass_bulge', re.compile(r'(?:^|[_\-/])(?:ass|butt|bulge)[_-]?(?:display|show|showing|present|presenting|press|pressed|lift|lifting|grab|grabbing|touch|touching)(?:$|[_\-/])')),
]

REQUIRED = {
    'fingers_between_toes',
    'whispering_in_ear',
    'blowing_in_ear',
    "hands_on_another's_neck",
    'hand_chains',
    'cover_them_up_slut_(meme)',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def tokens(key: str) -> set[str]:
    return {p for p in re.split(r'[^a-z0-9]+', key.lower()) if p}


def risk_flags(key: str) -> list[str]:
    k = key.lower()
    t = tokens(k)
    flags = []
    if t & SEXUALIZED_LANGUAGE:
        flags.append('sexualized_language')
    if t & RESTRAINT_WORDS:
        flags.append('restraint_context')
    flags.extend(name for name, pat in PATTERNS if pat.search(k))
    return sorted(set(flags))


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v16.9-action-ordinary-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 1583:
        raise SystemExit(f'expected v16.8 ordinary clean population 1583, got {len(src)}')

    boundary, clean = [], []
    reason_counts = Counter()
    for r in src:
        key = r['identity_key']
        hit = risk_flags(key)
        out = {
            'identity_key': key,
            'candidate_state': 'BOUNDARY_REVIEW' if hit else 'ORDINARY_CLEAN',
            'risk_flags': '|'.join(hit),
        }
        if hit:
            boundary.append(out)
            reason_counts.update(hit)
        else:
            clean.append(out)

    captured = {r['identity_key'] for r in boundary}
    missing = sorted(REQUIRED - captured)
    if missing:
        raise SystemExit(f'v16.9 failed required counterexamples: {missing}')

    boundary.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v16.9 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','candidate_state','risk_flags']
    for name, rows in [('boundary_review_v16_9.csv', boundary), ('ordinary_clean_v16_9.csv', clean)]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)

    with (OUT / 'ordinary_fresh_holdout_template_v16_9.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n'); w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': 'ORDINARY_CLEAN_HOLDOUT_V16_9', 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'ACTION_INTERACTION_REFINEMENT_V16_9_FINAL_ADVERSARIAL_SWEEP',
        'source_ordinary_rows_v16_8': len(src),
        'adversarial_boundary_rows': len(boundary),
        'ordinary_clean_rows_v16_9': len(clean),
        'risk_flag_counts': dict(sorted(reason_counts.items())),
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
        'next_gate': 'independently review fresh 120-row holdout; promote only if no sexual-intent counterexample remains',
    }
    (OUT / 'summary_v16_9.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
