#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v2.csv')
OUT = Path('docs/issue118/risk_exclusion_wave3')

TARGET_PATHS = {
    'OBJECT_PROP/DAILY',
    'CLOTHING/ACCESSORY',
    'CLOTHING/COSTUME',
}

# Frozen before discovery review.  These are conservative boundary exclusions,
# not SEXUAL classifications.  A hit means only: do not bulk-auto-classify this
# identity as NON_SEXUAL under the wave3 predicate.
RISK_TOKENS = {
    'ageplay', 'ahegao', 'anal', 'anilingus', 'anus', 'areola', 'areolae',
    'arousal', 'aroused', 'ass', 'bdsm', 'birth', 'blindfold', 'blowjob',
    'bondage', 'bottomless', 'bound', 'bra', 'breast', 'breastfeeding',
    'breasts', 'bukkake', 'buttjob', 'cage', 'clamp', 'clamps', 'cleavage',
    'clitoris', 'collar', 'condom', 'cowgirl', 'creampie', 'crotch',
    'crotchless', 'cum', 'cumshot', 'cunnilingus', 'dildo', 'downblouse',
    'ecstasy', 'ejaculation', 'erect', 'erection', 'fellatio', 'femdom',
    'fertilisation', 'fertilization', 'fetish', 'fingering', 'fleshlight',
    'footjob', 'fuck', 'fucking', 'futa', 'gag', 'gagged', 'genital',
    'groping', 'handcuff', 'handcuffs', 'handjob', 'impregnation', 'incest',
    'insemination', 'insertion', 'irrumatio', 'lactation', 'leash',
    'lingerie', 'maebari', 'masturbation', 'naked', 'netorare', 'nipple',
    'nipples', 'nude', 'onahole', 'oppai', 'orgasm', 'paizuri', 'panties',
    'pasties', 'peeing', 'penetration', 'penis', 'pregnancy', 'pregnant',
    'prostitution', 'pubic', 'pussy', 'rape', 'restraint', 'restraints',
    'rope', 'scrotum', 'sex', 'shackle', 'slapping', 'slave', 'spanking',
    'straitjacket', 'stripper', 'striptease', 'tentacle', 'testicle',
    'testicles', 'threesome', 'topless', 'torture', 'underboob', 'underwear',
    'upskirt', 'vagina', 'vaginal', 'vibrator', 'vulva', 'whip', 'zoophilia',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return '_'.join(v.strip().lower().replace('_', ' ').split())


def tokens(key: str) -> set[str]:
    return {x for x in re.split(r'[_()\-]+', key.lower()) if x}


def rank(key: str, lane: str) -> str:
    return hashlib.sha256(f'issue118-risk-wave3|{lane}|{key}'.encode()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    general = {norm(r['canonical']): r for r in read_csv(GENERAL)}
    sidecar = read_csv(SIDECAR)
    if len(sidecar) != 31752:
        raise SystemExit(f'sidecar drift: {len(sidecar)}')

    candidates: list[dict[str, str]] = []
    excluded = Counter()
    by_path: dict[str, list[dict[str, str]]] = defaultdict(list)

    for s in sidecar:
        if s['review_status'] != 'UNCLASSIFIED':
            continue
        if s['is_general'] != 'YES' or s['is_special'] != 'NO':
            continue
        key = s['identity_key']
        g = general.get(key)
        if not g:
            continue
        path = (g.get('primary_path') or '').strip()
        if path not in TARGET_PATHS:
            continue
        hits = sorted(tokens(key) & RISK_TOKENS)
        if hits:
            excluded[path] += 1
            continue
        row = {
            'identity_key': key,
            'general_path': path,
            'general_status': g.get('classification_status', ''),
            'general_confidence': g.get('confidence', ''),
            'token_count': str(len(tokens(key))),
        }
        candidates.append(row)
        by_path[path].append(row)

    discovery: list[dict[str, str]] = []
    for path in sorted(TARGET_PATHS):
        rows = by_path[path]
        if len(rows) < 24:
            raise SystemExit(f'not enough candidates for {path}: {len(rows)}')

        chosen: dict[str, tuple[dict[str, str], str]] = {}
        # Six broad deterministic examples.
        for r in sorted(rows, key=lambda x: rank(x['identity_key'], 'random'))[:6]:
            chosen[r['identity_key']] = (r, 'HASH_RANDOM')

        # Six compound-name boundary examples.  Long/compound identities are a
        # cheap challenge set for latent semantics missed by exact risk tokens.
        remaining = [r for r in rows if r['identity_key'] not in chosen]
        remaining.sort(key=lambda x: (-int(x['token_count']), rank(x['identity_key'], 'compound')))
        for r in remaining[:6]:
            chosen[r['identity_key']] = (r, 'COMPOUND_CHALLENGE')

        if len(chosen) != 12:
            raise SystemExit(f'discovery sample drift for {path}: {len(chosen)}')
        for key, (r, lane) in sorted(chosen.items(), key=lambda kv: rank(kv[0], 'output')):
            discovery.append({
                **r,
                'candidate_rows_in_path': str(len(rows)),
                'sample_lane': lane,
                'candidate_class': 'NON_SEXUAL',
                'phase': 'DISCOVERY_WAVE3',
                'reviewed_class': '',
                'review_note': '',
            })

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUT / 'candidate_inventory_discovery_v1.csv',
        sorted(candidates, key=lambda r: (r['general_path'], r['identity_key'])),
        ['identity_key', 'general_path', 'general_status', 'general_confidence', 'token_count'],
    )
    write_csv(
        OUT / 'discovery_sample_v1.csv',
        discovery,
        [
            'identity_key', 'general_path', 'general_status', 'general_confidence',
            'token_count', 'candidate_rows_in_path', 'sample_lane', 'candidate_class',
            'phase', 'reviewed_class', 'review_note',
        ],
    )
    (OUT / 'risk_tokens_discovery_v1.txt').write_text(
        '\n'.join(sorted(RISK_TOKENS)) + '\n', encoding='utf-8'
    )

    summary = {
        'issue': 118,
        'mode': 'RISK_EXCLUSION_WAVE3_DISCOVERY',
        'source_sidecar': 'research_sidecar_v2.csv (efficiency checkpoint)',
        'target_paths': sorted(TARGET_PATHS),
        'risk_token_count': len(RISK_TOKENS),
        'candidate_rows_total': len(candidates),
        'candidate_rows_by_path': {p: len(by_path[p]) for p in sorted(TARGET_PATHS)},
        'risk_excluded_by_path': {p: excluded[p] for p in sorted(TARGET_PATHS)},
        'discovery_rows': len(discovery),
        'holdout_generated': 'NO',
        'promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
    }
    (OUT / 'summary_discovery_v1.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
