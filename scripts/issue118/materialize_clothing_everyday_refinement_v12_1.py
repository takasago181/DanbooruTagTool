#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v4.csv')
OUT = Path('docs/issue118/clothing_everyday_refinement_v12_1')

V11_RISK_TERMS = {
    'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm',
    'masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia','rape',
    'cunnilingus','anilingus','fingering','footjob','creampie','bukkake','fleshlight','onahole','fuck','fucking',
    'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples',
    'breast','breasts','areola','areolae','pubic','crotch','genital','gag','gagged','handcuff','handcuffs',
    'leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps','collar','fetish',
    'bdsm','spanking','whip','pregnant','pregnancy','lactation','breastfeeding','birth','insemination',
    'fertilization','fertilisation','impregnation','blood','wound','gore','amputee','amputation','castration',
    'corpse','injury','snuff','nude','naked','topless','bottomless','panties','underwear','bra','cleavage',
    'underboob','upskirt','downblouse','lingerie','crotchless','pasties','maebari','condom','condoms','porn',
    'pornstar','stripper','prostitute','courtesan','oiran','speculum','bodystocking','bustier','gravure','brocon',
    'siscon','lolicon','shotacon','incest','virgin','virginity','seme','uke','femdom','maledom','ageplay',
    'cuckold','cuckquean','netorare','netori','ntr',
}

BOUNDARY_TOKENS = {
    'bikini','swimsuit','swimwear','thong','garter','garters','gstring','fishnet','fishnets','corset','corsets',
    'harness','harnesses','latex','rubber','leather','leotard','leotards','babydoll','stocking','stockings',
    'thighhigh','thighhighs','pantyhose','bodysuit','bodysuits','bunnysuit','bunny','playboy','fetishwear',
    'bodycon','sideboob','boob','boobs','pastie','pasties','maebari','loincloth','fundoshi','micro','slingshot',
    'highleg','lowleg','seethrough','sheer','transparent','frontless','backless','assless','crotchless','keyhole',
    'cutout','strapless','bralette','bandeau','negligee','nightgown',
}

# Explicit separator-aware patterns close the v12 tokenizer gap. Matches are
# exclusion/discovery only and never assign a semantic class.
BOUNDARY_PATTERNS = [
    ('g_string', re.compile(r'(?:^|[_/\-])g[_\-]?string(?:$|[_/\-])')),
    ('see_through', re.compile(r'(?:^|[_/\-])see[_\-]through(?:$|[_/\-])')),
    ('cut_out', re.compile(r'(?:^|[_/\-])cut[_\-]out(?:$|[_/\-])')),
    ('high_leg', re.compile(r'(?:^|[_/\-])high[_\-]leg(?:$|[_/\-])')),
    ('low_leg', re.compile(r'(?:^|[_/\-])low[_\-]leg(?:$|[_/\-])')),
    ('tube_top', re.compile(r'(?:^|[_/\-])tube[_\-]top(?:$|[_/\-])')),
    ('thigh_high', re.compile(r'(?:^|[_/\-])thigh[_\-]highs?(?:$|[_/\-])')),
    ('body_suit', re.compile(r'(?:^|[_/\-])body[_\-]suit(?:$|[_/\-])')),
    ('bunny_suit', re.compile(r'(?:^|[_/\-])bunny[_\-]suit(?:$|[_/\-])')),
    ('baby_doll', re.compile(r'(?:^|[_/\-])baby[_\-]doll(?:$|[_/\-])')),
    ('night_gown', re.compile(r'(?:^|[_/\-])night[_\-]gown(?:$|[_/\-])')),
    ('swim_suit', re.compile(r'(?:^|[_/\-])swim[_\-]?suit(?:$|[_/\-])')),
    ('virgin_killer', re.compile(r'(?:^|[_/\-])virgin[_\-]killer(?:$|[_/\-])')),
    ('intimate_compound', re.compile(r'(?:^|[_/\-])(micro|slingshot|string)[_\-/]?(bikini|swimsuit)(?:$|[_/\-])')),
    ('exposure_compound', re.compile(r'(?:^|[_/\-])(side|under|upper|lower)[_\-/]?(boob|breast|ass)(?:$|[_/\-])')),
    ('garter_compound', re.compile(r'(?:^|[_/\-])garter(?:$|[_/\-])')),
    ('fetish_material', re.compile(r'(?:^|[_/\-])(latex|rubber)[_\-/](suit|dress|outfit|clothes|clothing)(?:$|[_/\-])')),
]


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace('_', ' ').split())


def tokens(key: str) -> set[str]:
    return {p for p in re.split(r'[^a-z0-9]+', key.lower()) if p}


def v11_none(key: str) -> bool:
    return not (tokens(key) & V11_RISK_TERMS)


def boundary_flags(key: str) -> list[str]:
    t = tokens(key)
    flags = []
    hits = sorted(t & BOUNDARY_TOKENS)
    if hits:
        flags.append('clothing_token:' + ','.join(hits))
    k = key.lower()
    for name, pat in BOUNDARY_PATTERNS:
        if pat.search(k):
            flags.append('clothing_pattern:' + name)
    return flags


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v12.1-clothing-fresh-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    general = read_csv(GENERAL)
    side = read_csv(SIDECAR)
    g = {norm(r['canonical']): r for r in general}

    source = []
    for r in side:
        if r['review_status'] != 'UNCLASSIFIED' or r['is_special'] == 'YES':
            continue
        key = r['identity_key']
        gr = g.get(key)
        if gr is None or (gr.get('primary_path') or '').strip() != 'CLOTHING/EVERYDAY':
            continue
        if not v11_none(key):
            continue
        source.append(key)

    source = sorted(set(source))
    if len(source) != 3298:
        raise SystemExit(f'expected v11 CLOTHING/EVERYDAY|NONE population 3298, got {len(source)}')

    boundary = []
    clean = []
    pattern_counts = Counter()
    for key in source:
        flags = boundary_flags(key)
        item = {
            'identity_key': key,
            'boundary_flags': '|'.join(flags),
            'candidate_state': 'CLOTHING_BOUNDARY' if flags else 'CLEAN_FOR_FRESH_HOLDOUT',
        }
        if flags:
            boundary.append(item)
            for flag in flags:
                if flag.startswith('clothing_pattern:'):
                    pattern_counts[flag.split(':', 1)[1]] += 1
        else:
            clean.append(item)

    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v12.1 holdout')

    # Regression checks for the separator-aware boundary handling when those
    # identities exist in the source population.
    by_key = {r['identity_key']: r for r in boundary}
    source_set = set(source)
    for probe in ['g-string', 'see-through_shirt', 'high-leg_swimsuit', 'tube_top']:
        if probe in source_set and probe not in by_key:
            raise SystemExit(f'v12.1 boundary regression: {probe}')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','boundary_flags','candidate_state']
    for name, rows in [
        ('clothing_boundary_v12_1.csv', boundary),
        ('clothing_clean_v12_1.csv', clean),
    ]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader()
            w.writerows(rows)

    holdout_fields = ['identity_key','candidate_state','human_intent','review_note']
    with (OUT / 'fresh_holdout_template_v12_1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=holdout_fields, lineterminator='\n')
        w.writeheader()
        for r in holdout:
            w.writerow({
                'identity_key': r['identity_key'],
                'candidate_state': r['candidate_state'],
                'human_intent': '',
                'review_note': '',
            })

    summary = {
        'issue': 118,
        'mode': 'CLOTHING_EVERYDAY_REFINEMENT_V12_1_SEPARATOR_AWARE',
        'source_cluster': 'GENERAL_ONLY|CLOTHING/EVERYDAY|NONE',
        'source_rows': len(source),
        'boundary_rows': len(boundary),
        'clean_candidate_rows': len(clean),
        'fresh_holdout_template_rows': len(holdout),
        'separator_pattern_counts': dict(sorted(pattern_counts.items())),
        'supersedes_for_promotion_gate': 'clothing_everyday_refinement_v12',
        'boundary_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'semantic_authority': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review fixed v12.1 120-row holdout; refine again on any counterexample before research promotion',
    }
    (OUT / 'summary_v12_1.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
