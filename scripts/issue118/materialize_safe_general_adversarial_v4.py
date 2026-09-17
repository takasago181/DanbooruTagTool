#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path('docs/issue118/safe_general_candidates_v2/candidate_inventory_v2.csv')
V2_SAMPLE = Path('docs/issue118/safe_general_candidates_v2/validation_sample_v2.csv')
V3_SAMPLE = Path('docs/issue118/safe_general_refine_v3/validation_sample_v3.csv')
OUT = Path('docs/issue118/safe_general_adversarial_v4')

# IMPORTANT: these rules only REMOVE rows from AUTO_NON_SEXUAL eligibility.
# They never classify a row as SEXUAL/CONTEXTUAL by themselves.
TOKEN_RULES = {
    'PREVIOUS_V3_RISK': {'cage', 'stripper'},
    'CONTRACEPTION_SEX_RELATED': {'condom', 'condoms', 'contraceptive', 'contraception'},
    'SEXUAL_MEDIA_OR_ROLE': {
        'porn', 'pornstar', 'stripper', 'prostitute', 'prostitution', 'courtesan',
        'oiran', 'dominatrix', 'brothel', 'sexworker', 'sexworkers',
    },
}

PHRASE_RULES = {
    'SEXUALIZED_COSTUME': {
        'playboy_bunny', 'bunny_girl', 'bunny_suit', 'slingshot_swimsuit',
        'virgin_killer',
    },
    'FETISH_CODED_WEAR': {
        'o-ring_', '_o-ring', 'garter_belt', 'garter_strap', 'chest_harness',
        'body_harness', 'o-ring_harness', 'neck_garter', 'thigh_garter',
        'legwear_garter',
    },
}

# Broad fashion words are ambiguous. Restrict them to clothing paths and use them
# only as conservative auto-exclusion signals, never as semantic labels.
CLOTHING_CONTEXT_TOKENS = {'garter', 'harness', 'choker', 'corset'}

KNOWN_LEAKS = {
    'stripper',
    'pornstar',
    'multiple_condoms',
    'okamoto_condoms',
    'too_many_condoms',
    'playboy_bunny',
    'o-ring_slingshot_swimsuit',
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

    for family, phrases in PHRASE_RULES.items():
        if any(p in key for p in phrases):
            hits.add(family)

    if path.startswith('CLOTHING/') and tok & CLOTHING_CONTEXT_TOKENS:
        hits.add('CLOTHING_CONTEXTUAL_RISK')

    return sorted(hits)


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    base = read_csv(BASE)
    old_keys = {r['identity_key'] for r in read_csv(V2_SAMPLE)} | {r['identity_key'] for r in read_csv(V3_SAMPLE)}
    if len(base) != 10258:
        raise SystemExit(f'input drift: expected 10258 v2 candidates, got {len(base)}')

    excluded: list[dict[str, str]] = []
    clean: list[dict[str, str]] = []
    family_counts = Counter()
    path_excluded = Counter()

    for row in base:
        families = risk_families(row)
        if families:
            out = dict(row)
            out['risk_families'] = '|'.join(families)
            excluded.append(out)
            path_excluded[row['general_path']] += 1
            for family in families:
                family_counts[family] += 1
        else:
            clean.append(dict(row))

    clean_keys = {r['identity_key'] for r in clean}
    missing_known = sorted(k for k in KNOWN_LEAKS if k not in {r['identity_key'] for r in base})
    still_clean_known = sorted(k for k in KNOWN_LEAKS if k in clean_keys)
    if missing_known:
        raise SystemExit(f'known leak examples missing from input inventory: {missing_known}')
    if still_clean_known:
        raise SystemExit(f'known leak examples survived v4 exclusion: {still_clean_known}')

    OUT.mkdir(parents=True, exist_ok=True)
    inv_fields = ['identity_key', 'general_path', 'confidence', 'risk_tokens', 'candidate_class']
    write_csv(OUT / 'candidate_inventory_v4.csv', clean, inv_fields)

    excluded_fields = inv_fields + ['risk_families']
    write_csv(OUT / 'adversarial_exclusions_v4.csv', excluded, excluded_fields)

    # DISCOVERY is sampled from excluded risk families. It is NOT a validation holdout.
    discovery: list[dict[str, str]] = []
    seen_discovery: set[str] = set()
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in excluded:
        for family in row['risk_families'].split('|'):
            by_family[family].append(row)
    for family in sorted(by_family):
        items = sorted(by_family[family], key=lambda r: rank(f'issue118-v4-risk-{family}', r['identity_key']))
        chosen = 0
        for row in items:
            if row['identity_key'] in seen_discovery:
                continue
            discovery.append({
                'identity_key': row['identity_key'],
                'general_path': row['general_path'],
                'risk_family': family,
                'phase': 'DISCOVERY_V4',
            })
            seen_discovery.add(row['identity_key'])
            chosen += 1
            if chosen == 12:
                break
    write_csv(
        OUT / 'risk_discovery_sample_v4.csv',
        discovery,
        ['identity_key', 'general_path', 'risk_family', 'phase'],
    )

    # HOLDOUT is sampled only from the cleaned pool and excludes every v2/v3 sample.
    # No review verdict is written by this script.
    holdout: list[dict[str, str]] = []
    clean_by_path: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clean:
        clean_by_path[row['general_path']].append(row)
    for path in sorted(clean_by_path):
        fresh = [r for r in clean_by_path[path] if r['identity_key'] not in old_keys]
        fresh.sort(key=lambda r: rank(f'issue118-v4-clean-holdout-{path}', r['identity_key']))
        for row in fresh[:12]:
            holdout.append({
                'identity_key': row['identity_key'],
                'general_path': row['general_path'],
                'candidate_class': 'NON_SEXUAL',
                'phase': 'FRESH_HOLDOUT_V4',
            })
    holdout_keys = {r['identity_key'] for r in holdout}
    if holdout_keys & old_keys:
        raise SystemExit('fresh holdout overlaps v2/v3 validation samples')
    write_csv(
        OUT / 'clean_holdout_sample_v4.csv',
        holdout,
        ['identity_key', 'general_path', 'candidate_class', 'phase'],
    )

    summary = {
        'issue': 118,
        'mode': 'SAFE_GENERAL_ADVERSARIAL_V4',
        'input_candidate_rows': len(base),
        'adversarial_excluded_rows': len(excluded),
        'clean_candidate_rows': len(clean),
        'risk_family_counts': dict(sorted(family_counts.items())),
        'excluded_path_counts': dict(sorted(path_excluded.items())),
        'risk_discovery_rows': len(discovery),
        'clean_holdout_rows': len(holdout),
        'clean_holdout_paths': len({r['general_path'] for r in holdout}),
        'prior_validation_overlap': len(holdout_keys & old_keys),
        'known_leaks_removed': sorted(KNOWN_LEAKS),
        'review_verdicts_generated_by_materializer': 'NO',
        'promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
    }
    (OUT / 'summary_v4.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
