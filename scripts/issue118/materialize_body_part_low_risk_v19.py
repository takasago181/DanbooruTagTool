#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v7.csv')
OUT = Path('docs/issue118/body_part_low_risk_v19')

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

RISK_PATTERNS = {
    'sexualized_body_site': re.compile(r'(?:^|_)(?:ass|butt|butts|buttocks|booty|bulge|boob|boobs|tit|tits|bust|cameltoe)(?:_|$)'),
    'intimate_or_fetish_body_site': re.compile(r'(?:^|_)(?:armpit|armpits|navel|belly|stomach|hip|hips|thigh|thighs|groin|pelvis|waist|foot|feet|sole|soles|toe|toes|tongue|lip|lips|mouth|chest|pectoral|pectorals)(?:_|$)'),
    'sexualized_shape_or_emphasis': re.compile(r'(?:^|_)(?:thicc|thick|curvy|voluptuous|hourglass|seductive|sexy)(?:_|$)'),
    'intimate_mark_or_secretion': re.compile(r'(?:^|_)(?:tanline|tanlines|sweaty|sweat|saliva|drool)(?:_|$)'),
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
    return '+'.join(sorted(hit)) if hit else 'NONE'


def stable_rank(key: str) -> str:
    return hashlib.sha256(('issue118-body-v19-holdout|' + key).encode('utf-8')).hexdigest()


def main() -> int:
    general = read_csv(GENERAL)
    side = read_csv(SIDECAR)
    g = {norm(r['canonical']): r for r in general}

    source = []
    for r in side:
        if r['review_status'] != 'UNCLASSIFIED':
            continue
        if r.get('is_special') == 'YES':
            continue
        key = r['identity_key']
        gr = g.get(key)
        if gr is None:
            continue
        if (gr.get('primary_path') or '').strip() != 'BODY_PART':
            continue
        if lex_flags(key) != 'NONE':
            continue
        source.append(key)

    source = sorted(set(source))
    if len(source) != 1697:
        raise SystemExit(f'expected 1697 GENERAL_ONLY BODY_PART/NONE source rows, got {len(source)}')

    low_risk = []
    residual = []
    flag_counts = Counter()
    for key in source:
        hits = [name for name, pattern in RISK_PATTERNS.items() if pattern.search(key.lower())]
        if hits:
            residual.append({'identity_key': key, 'state': 'BODY_BOUNDARY_UNCLASSIFIED', 'risk_flags': '+'.join(hits)})
            for hit in hits:
                flag_counts[hit] += 1
        else:
            low_risk.append({'identity_key': key, 'state': 'LOW_RISK_BODY_CANDIDATE_V19'})

    holdout_keys = sorted((r['identity_key'] for r in low_risk), key=stable_rank)[:120]
    holdout = [
        {'identity_key': key, 'candidate_state': 'LOW_RISK_BODY_HOLDOUT_V19', 'human_intent': '', 'review_note': ''}
        for key in holdout_keys
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'low_risk_body_candidate_v19.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state'], lineterminator='\n')
        w.writeheader(); w.writerows(low_risk)
    with (OUT / 'body_boundary_residual_v19.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','state','risk_flags'], lineterminator='\n')
        w.writeheader(); w.writerows(residual)
    with (OUT / 'fresh_holdout_template_v19.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader(); w.writerows(holdout)

    summary = {
        'issue': 118,
        'mode': 'BODY_PART_LOW_RISK_SUBCLUSTER_V19',
        'source_cluster': 'GENERAL_ONLY|BODY_PART|NONE',
        'source_rows': len(source),
        'low_risk_candidate_rows': len(low_risk),
        'boundary_residual_rows': len(residual),
        'boundary_flag_counts': dict(sorted(flag_counts.items())),
        'fresh_holdout_template_rows': len(holdout),
        'selection_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review fixed 120-row low-risk body holdout; promote only if clean',
    }
    (OUT / 'summary_v19.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
