#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL = Path('data/generation/special2788_generation_profile.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v8.csv')
OUT = Path('docs/issue118/special_only_explicit_v21')

LEX_GROUPS = {
    'EXPLICIT_SEX': {'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm','masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia','rape','cunnilingus','anilingus','fingering','footjob','creampie','bukkake','fleshlight','onahole','fuck','fucking'},
    'ANATOMY': {'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples','breast','breasts','areola','areolae','pubic','crotch','genital'},
    'RESTRAINT_FETISH': {'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps','collar','fetish','bdsm','spanking','whip'},
    'REPRO': {'pregnant','pregnancy','lactation','breastfeeding','birth','insemination','fertilization','fertilisation','impregnation'},
    'INJURY': {'blood','wound','gore','amputee','amputation','castration','corpse','injury','snuff'},
    'EXPOSURE_INTIMATE': {'nude','naked','topless','bottomless','panty','panties','underwear','bra','cleavage','underboob','upskirt','downblouse','lingerie','crotchless','pasties','maebari'},
    'ADULT_ROLE_DEVICE': {'condom','condoms','porn','pornstar','stripper','prostitute','courtesan','oiran','speculum','bodystocking','bustier','gravure'},
    'RELATIONSHIP_ROLE': {'brocon','siscon','lolicon','shotacon','incest','virgin','virginity','seme','uke','femdom','maledom','ageplay','cuckold','cuckquean','netorare','netori','ntr'},
    'SEXUALIZED_CLOTHING': {'bikini','swimsuit','swimwear','thong','garter','garters','gstring','fishnet','fishnets','corset','harness','latex','leotard','bodysuit','bunnysuit','playboy','fetishwear','bodycon','slingshot','highleg','lowleg','sheer','transparent','frontless','backless','assless','sideless','tankini','monokini','trikini','microdress','dongtan'},
}

EXPLICIT_PATTERNS = {
    'adult_content_or_toy': re.compile(r'(?:^|_)(?:18\+|r18|r_18|adult|adultbaby|adult_baby)(?:_|$)|(?:^|_)adult_toys?(?:_|$)'),
    'sexual_compound_or_state': re.compile(r'(?:^|_)(?:aftersex|sexed|sexual|sexually|intercourse|coitus|copulation|frottage|tribadism|scissoring|humping|dry_humping|orgasmic|arousal|aroused|horny|lewd|erotic|hentai|masturbatory)(?:_|$)'),
    'sexual_assault_variant': re.compile(r'(?:^|_)(?:raped|raping|rapeplay|molest|molested|molestation|sexual_assault)(?:_|$)'),
    'genital_slang': re.compile(r'(?:^|_)(?:cock|cocks|dick|dicks|phallus|balls|boob|boobs|boobies|titty|titties|tits)(?:_|$)'),
    'sexual_fluid_variant': re.compile(r'(?:^|_)(?:semen|sperm|sperma|ejaculate|ejaculating|ejaculated|precum|pre_cum)(?:_|$)'),
    'explicit_group_sex': re.compile(r'(?:^|_)(?:3p|4p|5p|6p|gangbang|gang_bang|orgy)(?:_|$)'),
    'explicit_act_variant': re.compile(r'(?:^|_)(?:after_oral|after_frottage|after_urethral|oral_creampie|urethral|vaginal|facesitting|facefucking|face_fucking|gokkun|nakadashi|voyeurism|exhibitionism)(?:_|$)'),
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace('_', ' ').split())


def lex_flags(key: str) -> str:
    k = key.lower()
    parts = {p for p in re.split(r'[_()\-/]+', k) if p}
    hit = {name for name, terms in LEX_GROUPS.items() if parts & terms}
    if re.search(r'(?:^|[_/\-])g[_\-]string(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])see[_\-]through(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])t[_\-]back(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])micro(?:dress|skirt|shorts|pants|top|shirt)(?:$|[_/\-])', k):
        hit.add('SEXUALIZED_CLOTHING')
    if re.search(r'(?:^|[_/\-])(?:top[/_-]bottom|bottom[/_-]top)[_/-]dynamic(?:$|[_/\-])', k):
        hit.add('RELATIONSHIP_ROLE')
    return '+'.join(sorted(hit)) if hit else 'NONE'


def stable_rank(key: str) -> str:
    return hashlib.sha256(('issue118-special-explicit-v21|' + key).encode('utf-8')).hexdigest()


def main() -> int:
    general = read_csv(GENERAL)
    special = read_csv(SPECIAL)
    side = read_csv(SIDECAR)
    gkeys = {norm(r['canonical']) for r in general}
    smap = {norm(r['Tag']): r for r in special}

    source = []
    for r in side:
        if r['review_status'] != 'UNCLASSIFIED':
            continue
        key = r['identity_key']
        if key in gkeys:
            continue
        if r.get('is_special') != 'YES':
            continue
        sr = smap.get(key)
        if sr is None:
            continue
        if (sr.get('GenerationFamily') or '').strip():
            continue
        if lex_flags(key) != 'NONE':
            continue
        source.append(key)

    source = sorted(set(source))
    if len(source) != 563:
        raise SystemExit(f'expected 563 SPECIAL_ONLY/(none)/NONE source rows, got {len(source)}')

    explicit = []
    residual = []
    counts = Counter()
    for key in source:
        hits = [name for name, pattern in EXPLICIT_PATTERNS.items() if pattern.search(key.lower())]
        if hits:
            explicit.append({'identity_key': key, 'state': 'EXPLICIT_SEXUAL_CANDIDATE_V21', 'evidence_flags': '+'.join(hits)})
            for hit in hits:
                counts[hit] += 1
        else:
            residual.append({'identity_key': key, 'state': 'SPECIAL_ONLY_RESIDUAL_UNCLASSIFIED_V21'})

    if len(explicit) < 120:
        holdout_keys = sorted((r['identity_key'] for r in explicit), key=stable_rank)
    else:
        holdout_keys = sorted((r['identity_key'] for r in explicit), key=stable_rank)[:120]
    holdout = [
        {'identity_key': key, 'candidate_state': 'EXPLICIT_SEXUAL_HOLDOUT_V21', 'human_intent': '', 'review_note': ''}
        for key in holdout_keys
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'explicit_sexual_candidate_v21.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state','evidence_flags'], lineterminator='\n')
        w.writeheader(); w.writerows(explicit)
    with (OUT / 'residual_unclassified_v21.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state'], lineterminator='\n')
        w.writeheader(); w.writerows(residual)
    with (OUT / 'fresh_holdout_template_v21.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader(); w.writerows(holdout)

    summary = {
        'issue': 118,
        'mode': 'SPECIAL_ONLY_EXPLICIT_SEXUAL_DISCOVERY_V21',
        'source_cluster': 'SPECIAL_ONLY|(none)|(none)|NONE',
        'source_rows': len(source),
        'explicit_candidate_rows': len(explicit),
        'residual_unclassified_rows': len(residual),
        'evidence_flag_counts': dict(sorted(counts.items())),
        'fresh_holdout_template_rows': len(holdout),
        'selection_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review explicit-sexual holdout; promote only concept-level explicit candidates if clean',
    }
    (OUT / 'summary_v21.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
