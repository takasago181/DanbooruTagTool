#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path('docs/issue118/safe_general_candidates_v2/candidate_inventory_v2.csv')
V4_EXCLUDED = Path('docs/issue118/safe_general_adversarial_v4/adversarial_exclusions_v4.csv')
PRIOR_SAMPLES = [
    Path('docs/issue118/safe_general_candidates_v2/validation_sample_v2.csv'),
    Path('docs/issue118/safe_general_refine_v3/validation_sample_v3.csv'),
    Path('docs/issue118/safe_general_adversarial_v4/risk_discovery_sample_v4.csv'),
    Path('docs/issue118/safe_general_adversarial_v4/clean_holdout_sample_v4.csv'),
]
OUT = Path('docs/issue118/safe_general_refined_v5')

TOKEN_RULES = {
    'STRIPPER_RISK': {'stripper'},
    'CONTRACEPTION_SEX_RELATED': {'condom', 'condoms', 'contraceptive', 'contraception'},
    'SEXUAL_MEDIA_OR_ROLE': {
        'porn', 'pornstar', 'prostitute', 'prostitution', 'courtesan', 'oiran',
        'dominatrix', 'brothel', 'sexworker', 'sexworkers',
    },
}

SEXUALIZED_COSTUME_PHRASES = {
    'playboy_bunny', 'bunny_girl', 'bunny_suit', 'slingshot_swimsuit', 'virgin_killer',
}
NARROW_INTIMATE_PHRASES = {
    'garter_belt', 'garter_strap', 'legwear_garter', 'neck_garter', 'thigh_garter',
    'chest_harness', 'body_harness',
}
CLOTHING_CONTEXT_TOKENS = {'choker', 'corset'}
O_RING_GARMENT_TOKENS = {
    'garter', 'harness', 'leotard', 'bottom', 'dress', 'legwear', 'thigh', 'strap',
    'belly', 'necktie', 'swimsuit', 'top',
}

KNOWN_MUST_EXCLUDE = {
    'stripper', 'stripper_pole', 'pornstar', 'multiple_condoms', 'okamoto_condoms',
    'too_many_condoms', 'playboy_bunny', 'o-ring_slingshot_swimsuit', 'head_cage',
}
KNOWN_MUST_REINTRODUCE = {
    'cage', 'rectangular_cage', 'suspended_cage', 'bug_cage', 'holding_cage',
    'sleeve_garter', 'star_o-ring',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace(' ', '_').split('_'))


def tokens(key: str) -> set[str]:
    return {x for x in re.split(r'[_()\-]+', key.lower()) if x}


def rank(seed: str, key: str) -> str:
    return hashlib.sha256(f'{seed}|{key}'.encode()).hexdigest()


def risk_families(row: dict[str, str]) -> list[str]:
    key = norm(row['identity_key'])
    tok = tokens(key)
    path = row['general_path']
    hits: set[str] = set()

    for family, terms in TOKEN_RULES.items():
        if tok & terms:
            hits.add(family)

    if key == 'head_cage' or key.startswith('head_cage_'):
        hits.add('TARGETED_RESTRAINT_RISK')

    if any(p in key for p in SEXUALIZED_COSTUME_PHRASES):
        hits.add('SEXUALIZED_COSTUME')

    if any(p in key for p in NARROW_INTIMATE_PHRASES):
        hits.add('NARROW_INTIMATE_WEAR')

    if path.startswith('CLOTHING/') and tok & CLOTHING_CONTEXT_TOKENS:
        hits.add('CLOTHING_CONTEXTUAL_RISK')

    if path.startswith('CLOTHING/') and 'o-ring' in key and tok & O_RING_GARMENT_TOKENS:
        hits.add('O_RING_GARMENT_RISK')

    return sorted(hits)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    base = read_csv(BASE)
    v4_excluded = {r['identity_key'] for r in read_csv(V4_EXCLUDED)}
    prior_keys: set[str] = set()
    for path in PRIOR_SAMPLES:
        prior_keys |= {r['identity_key'] for r in read_csv(path)}

    clean: list[dict[str, str]] = []
    excluded: list[dict[str, str]] = []
    family_counts = Counter()
    for row in base:
        fam = risk_families(row)
        if fam:
            out = dict(row)
            out['risk_families'] = '|'.join(fam)
            excluded.append(out)
            for f in fam:
                family_counts[f] += 1
        else:
            clean.append(dict(row))

    clean_keys = {r['identity_key'] for r in clean}
    excluded_keys = {r['identity_key'] for r in excluded}
    missing_exclude = sorted(KNOWN_MUST_EXCLUDE - excluded_keys)
    missing_reintro = sorted(KNOWN_MUST_REINTRODUCE - clean_keys)
    if missing_exclude:
        raise SystemExit(f'known risk leaked into clean v5: {missing_exclude}')
    if missing_reintro:
        raise SystemExit(f'known v4 over-exclusion not reintroduced in v5: {missing_reintro}')

    reintroduced = [r for r in clean if r['identity_key'] in v4_excluded]
    reintroduced.sort(key=lambda r: (r['general_path'], r['identity_key']))

    # Fresh validation targets only rows newly reintroduced by the refined predicate.
    # Anything used in v2/v3/v4 discovery/holdout is excluded from this sample.
    by_path: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in reintroduced:
        if row['identity_key'] not in prior_keys:
            by_path[row['general_path']].append(row)
    validation: list[dict[str, str]] = []
    for path in sorted(by_path):
        items = sorted(by_path[path], key=lambda r: rank(f'issue118-v5-reintroduced-{path}', r['identity_key']))
        for row in items[:12]:
            validation.append({
                'identity_key': row['identity_key'],
                'general_path': row['general_path'],
                'candidate_class': 'NON_SEXUAL',
                'phase': 'FRESH_REINTRODUCED_HOLDOUT_V5',
            })

    validation_keys = {r['identity_key'] for r in validation}
    if validation_keys & prior_keys:
        raise SystemExit('v5 validation overlaps earlier samples')

    OUT.mkdir(parents=True, exist_ok=True)
    inv_fields = ['identity_key', 'general_path', 'confidence', 'risk_tokens', 'candidate_class']
    write_csv(OUT / 'candidate_inventory_v5.csv', clean, inv_fields)
    write_csv(
        OUT / 'adversarial_exclusions_v5.csv',
        excluded,
        inv_fields + ['risk_families'],
    )
    write_csv(OUT / 'reintroduced_from_v4.csv', reintroduced, inv_fields)
    write_csv(
        OUT / 'reintroduced_holdout_sample_v5.csv',
        validation,
        ['identity_key', 'general_path', 'candidate_class', 'phase'],
    )

    summary = {
        'issue': 118,
        'mode': 'SAFE_GENERAL_REFINED_V5',
        'input_candidate_rows': len(base),
        'excluded_rows_v5': len(excluded),
        'clean_candidate_rows_v5': len(clean),
        'risk_family_counts': dict(sorted(family_counts.items())),
        'v4_excluded_rows': len(v4_excluded),
        'reintroduced_from_v4_rows': len(reintroduced),
        'reintroduced_path_counts': dict(sorted(Counter(r['general_path'] for r in reintroduced).items())),
        'fresh_reintroduced_holdout_rows': len(validation),
        'fresh_reintroduced_holdout_paths': len({r['general_path'] for r in validation}),
        'prior_sample_overlap': len(validation_keys & prior_keys),
        'known_must_exclude': sorted(KNOWN_MUST_EXCLUDE),
        'known_must_reintroduce': sorted(KNOWN_MUST_REINTRODUCE),
        'review_verdicts_generated_by_materializer': 'NO',
        'promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
    }
    (OUT / 'summary_v5.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
