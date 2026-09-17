#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/safe_general_candidates_v2/candidate_inventory_v2.csv')
V4_EXCLUDED = Path('docs/issue118/safe_general_adversarial_v4/adversarial_exclusions_v4.csv')
V5_CLEAN = Path('docs/issue118/safe_general_refined_v5/candidate_inventory_v5.csv')
OUT = Path('docs/issue118/safe_general_converged_v6')

TOKEN_RULES = {
    'STRIPPER_RISK': {'stripper'},
    'CONTRACEPTION_SEX_RELATED': {'condom', 'condoms', 'contraceptive', 'contraception'},
    'SEXUAL_MEDIA_OR_ROLE': {
        'porn', 'pornstar', 'prostitute', 'prostitution', 'courtesan', 'oiran',
        'dominatrix', 'brothel', 'sexworker', 'sexworkers',
    },
    'REDTEAM_LOW_FREQUENCY_RISK': {'gravure', 'speculum', 'bodystocking', 'bustier'},
}

SEXUALIZED_COSTUME_PHRASES = {
    'playboy_bunny', 'bunny_girl', 'bunny_suit', 'slingshot_swimsuit', 'virgin_killer',
}
NARROW_INTIMATE_PHRASES = {
    'garter_belt', 'garter_strap', 'legwear_garter', 'neck_garter', 'thigh_garter',
    'chest_harness', 'body_harness',
}
CLOTHING_CONTEXT_TOKENS = {'choker', 'corset'}
SAFE_LOCATION_GARTER_TOKENS = {'arm', 'ankle', 'tail', 'sleeve'}
O_RING_GARMENT_TOKENS = {
    'garter', 'harness', 'leotard', 'bottom', 'dress', 'legwear', 'thigh', 'strap',
    'belly', 'necktie', 'swimsuit', 'top', 'belt', 'suspenders',
}

REVIEWED_SAFE_REINTRODUCTIONS = {
    # v4 discovery semantic review
    'cage', 'rectangular_cage', 'suspended_cage', 'bug_cage', 'holding_cage',
    'sleeve_garter', 'star_o-ring',
    # fresh v5 reintroduced holdout semantic review
    'arm_garter', 'heart_o-ring', 'rabbit_o-ring', 'black_arm_garter',
    'tail_garter', 'ankle_garter', 'cat_o-ring',
}

V5_CONTEXTUAL_COUNTEREXAMPLES = {
    'black_garter', 'blue_garter', 'o-ring_suspenders', 'o-ring_belt',
}
REDTEAM_DISCOVERIES = {
    'gravure_swimsuit_(idolmaster)', 'speculum', 'laddered_bodystocking', 'divine_bustier_(dq)',
}
KNOWN_MUST_EXCLUDE = {
    'head_cage', 'multiple_condoms', 'o-ring_slingshot_swimsuit', 'okamoto_condoms',
    'playboy_bunny', 'pornstar', 'stripper', 'stripper_pole', 'too_many_condoms',
} | V5_CONTEXTUAL_COUNTEREXAMPLES | REDTEAM_DISCOVERIES


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace(' ', '_').split('_'))


def tokens(key: str) -> set[str]:
    return {x for x in re.split(r'[_()\-]+', key.lower()) if x}


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

    if path.startswith('CLOTHING/') and 'garter' in tok and not (tok & SAFE_LOCATION_GARTER_TOKENS):
        hits.add('GENERIC_GARTER_CONTEXTUAL_RISK')

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
    v5_clean = {r['identity_key'] for r in read_csv(V5_CLEAN)}
    if len(base) != 10258:
        raise SystemExit(f'input drift: expected 10258, got {len(base)}')

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
    if missing_exclude:
        raise SystemExit(f'known semantic risk leaked into v6 clean set: {missing_exclude}')

    reintroduced_from_v4 = clean_keys & v4_excluded
    if reintroduced_from_v4 != REVIEWED_SAFE_REINTRODUCTIONS:
        raise SystemExit(
            'v6 reintroduced cohort must equal the fully reviewed safe set; '
            f'extra={sorted(reintroduced_from_v4-REVIEWED_SAFE_REINTRODUCTIONS)} '
            f'missing={sorted(REVIEWED_SAFE_REINTRODUCTIONS-reintroduced_from_v4)}'
        )

    newly_excluded_vs_v5 = excluded_keys & v5_clean
    expected_new = V5_CONTEXTUAL_COUNTEREXAMPLES | REDTEAM_DISCOVERIES
    if not expected_new <= newly_excluded_vs_v5:
        raise SystemExit(f'expected v6 new exclusions missing: {sorted(expected_new-newly_excluded_vs_v5)}')

    OUT.mkdir(parents=True, exist_ok=True)
    inv_fields = ['identity_key', 'general_path', 'confidence', 'risk_tokens', 'candidate_class']
    write_csv(OUT / 'candidate_inventory_v6.csv', clean, inv_fields)
    write_csv(OUT / 'adversarial_exclusions_v6.csv', excluded, inv_fields + ['risk_families'])

    base_idx = {r['identity_key']: r for r in base}
    reintro_rows = [base_idx[k] for k in sorted(reintroduced_from_v4)]
    write_csv(OUT / 'reviewed_safe_reintroduced_v6.csv', reintro_rows, inv_fields)

    new_excl_rows = []
    excluded_idx = {r['identity_key']: r for r in excluded}
    for k in sorted(newly_excluded_vs_v5):
        new_excl_rows.append(excluded_idx[k])
    write_csv(OUT / 'new_exclusions_vs_v5.csv', new_excl_rows, inv_fields + ['risk_families'])

    summary = {
        'issue': 118,
        'mode': 'SAFE_GENERAL_CONVERGED_V6',
        'input_candidate_rows': len(base),
        'excluded_rows_v6': len(excluded),
        'clean_candidate_rows_v6': len(clean),
        'risk_family_counts': dict(sorted(family_counts.items())),
        'v4_excluded_rows': len(v4_excluded),
        'reviewed_safe_reintroduced_rows': len(reintroduced_from_v4),
        'reviewed_safe_reintroduced_keys': sorted(reintroduced_from_v4),
        'newly_excluded_vs_v5_rows': len(newly_excluded_vs_v5),
        'v5_contextual_counterexamples_removed': sorted(V5_CONTEXTUAL_COUNTEREXAMPLES),
        'redteam_discoveries_removed': sorted(REDTEAM_DISCOVERIES),
        'new_unreviewed_reintroductions': 0,
        'review_verdicts_generated_by_materializer': 'NO',
        'promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
    }
    (OUT / 'summary_v6.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
