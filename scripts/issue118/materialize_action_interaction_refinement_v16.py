#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v6.csv')
OUT = Path('docs/issue118/action_interaction_refinement_v16')

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

SEXUAL_BOUNDARY_PATTERNS = [
    re.compile(r'(?:^|[_\-/])accidental[_-]?pervert(?:$|[_\-/])'),
    re.compile(r'(?:^|[_\-/])(?:molest|molesting|molestation|grope|groping|fondle|fondling|hump|humping|dry[_-]?hump|dry[_-]?humping)(?:$|[_\-/])'),
    re.compile(r'(?:^|[_\-/])(?:butt|ass)[_-]?(?:grab|grabbing|touch|touching|lick|licking|bite|biting|squeeze|squeezing)(?:$|[_\-/])'),
]

INTIMATE_GENERAL_PATTERNS = [
    re.compile(r'(?:^|[_\-/])(?:kiss|kissing|hug|hugging|cuddle|cuddling|snuggle|snuggling|nuzzle|nuzzling|embrace|embracing)(?:$|[_\-/])'),
    re.compile(r'(?:^|[_\-/])(?:holding[_-]?hands|hand[_-]?holding|sleeping[_-]?together|dating|date)(?:$|[_\-/])'),
]

VIOLENCE_PATTERNS = [
    re.compile(r'(?:^|[_\-/])(?:abuse|abusing|abduction|abducting|assault|attacking|attack|bully|bullying|choke|choking|strangle|strangling|slap|slapping|punch|punching|kick|kicking|fight|fighting|torture|torturing|kidnap|kidnapping|murder|murdering|execution|executing|hit|hitting)(?:$|[_\-/])'),
]

BODY_BOUNDARY_PATTERN = re.compile(
    r'(?:^|[_\-/])(?:foot|feet|thigh|thighs|butt|ass|hip|hips|waist|neck|armpit|armpits|belly|navel)[_-]?(?:grab|grabbing|touch|touching|lick|licking|bite|biting|rub|rubbing|squeeze|squeezing|kiss|kissing)(?:$|[_\-/])'
)


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace('_', ' ').split())


def v15_flags(key: str) -> set[str]:
    k = key.lower()
    parts = {p for p in re.split(r'[_()\-/]+', k) if p}
    hit = {name for name, terms in LEX_GROUPS.items() if parts & terms}
    if re.search(r'(?:^|[_/\-])g[_\-]string(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])see[_\-]through(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])t[_\-]back(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])micro(?:dress|skirt|shorts|pants|top|shirt)(?:$|[_/\-])', k):
        hit.add('SEXUALIZED_CLOTHING')
    if re.search(r'(?:^|[_/\-])(?:top[/_-]bottom|bottom[/_-]top)[_/-]dynamic(?:$|[_/\-])', k):
        hit.add('RELATIONSHIP_ROLE')
    return hit


def bucket(key: str) -> tuple[str, str]:
    k = key.lower()
    if any(p.search(k) for p in SEXUAL_BOUNDARY_PATTERNS) or BODY_BOUNDARY_PATTERN.search(k):
        return 'SEXUAL_BOUNDARY', 'sexual_or_fetish_contact_cue'
    if any(p.search(k) for p in INTIMATE_GENERAL_PATTERNS):
        return 'INTIMATE_GENERAL', 'affection_or_romance_contact'
    if any(p.search(k) for p in VIOLENCE_PATTERNS):
        return 'VIOLENCE_NONSEX_AXIS', 'violence_or_coercion_contact'
    return 'ORDINARY_INTERACTION', 'no_boundary_cue'


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v16-action-ordinary-holdout:' + key).encode('utf-8')).hexdigest()


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
        if gr is None or (gr.get('primary_path') or '').strip() != 'ACTION_CONTACT/INTERACTION':
            continue
        if v15_flags(key):
            continue
        source.append(key)

    source = sorted(set(source))
    if len(source) != 1852:
        raise SystemExit(f'expected v15 ACTION_CONTACT/INTERACTION|NONE population 1852, got {len(source)}')

    groups = {k: [] for k in ['SEXUAL_BOUNDARY','INTIMATE_GENERAL','VIOLENCE_NONSEX_AXIS','ORDINARY_INTERACTION']}
    reason_counts = Counter()
    for key in source:
        b, reason = bucket(key)
        groups[b].append({'identity_key': key, 'bucket': b, 'reason': reason})
        reason_counts[b] += 1

    ordinary = groups['ORDINARY_INTERACTION']
    holdout = sorted(ordinary, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough ordinary interaction rows for holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','bucket','reason']
    names = {
        'SEXUAL_BOUNDARY': 'sexual_boundary_v16.csv',
        'INTIMATE_GENERAL': 'intimate_general_v16.csv',
        'VIOLENCE_NONSEX_AXIS': 'violence_nonsex_axis_v16.csv',
        'ORDINARY_INTERACTION': 'ordinary_interaction_v16.csv',
    }
    for b, filename in names.items():
        with (OUT / filename).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader(); w.writerows(sorted(groups[b], key=lambda r: r['identity_key']))

    with (OUT / 'ordinary_fresh_holdout_template_v16.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': 'ORDINARY_INTERACTION_HOLDOUT', 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'ACTION_INTERACTION_REFINEMENT_V16',
        'source_cluster': 'GENERAL_ONLY|ACTION_CONTACT/INTERACTION|NONE',
        'source_rows': len(source),
        'bucket_counts': dict(sorted(reason_counts.items())),
        'ordinary_fresh_holdout_rows': len(holdout),
        'bucket_rules_use': 'TRIAGE_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'review ordinary holdout; keep intimate/violence/sexual-boundary buckets separate until independently validated',
    }
    (OUT / 'summary_v16.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
