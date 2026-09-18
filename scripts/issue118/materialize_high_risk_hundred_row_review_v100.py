#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL = Path('data/generation/special2788_generation_profile.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v68.csv')
OUT = Path('docs/issue118/high_risk_hundred_row_review_v100')

TARGETS = {
    "GENERAL_ONLY|(none)|RELATIONSHIP_ROLE": 3,
    "GENERAL_ONLY|(none)|RESTRAINT_FETISH": 3,
    "GENERAL_ONLY|(none)|SEXUALIZED_CLOTHING": 3,
    "GENERAL_ONLY|ACTION_CONTACT/INTERACTION|RESTRAINT_FETISH": 3,
    "GENERAL_ONLY|ACTION_CONTACT/INTIMATE|EXPOSURE_INTIMATE": 3,
    "GENERAL_ONLY|ACTION_CONTACT/OBJECT_USE|EXPOSURE_INTIMATE": 3,
    "GENERAL_ONLY|CLOTHING/ACCESSORY|EXPOSURE_INTIMATE": 3,
    "GENERAL_ONLY|CLOTHING_STATE_EXPOSURE|RESTRAINT_FETISH": 3,
    "OVERLAP|ACTION_CONTACT|CONTEXT_MODIFIER|ANATOMY": 3,
    "OVERLAP|ACTION_CONTACT|CONTEXT_MODIFIER|RESTRAINT_FETISH": 3,
    "OVERLAP|ACTION_CONTACT|FLUID_STATE_ACTION|ANATOMY": 3,
    "OVERLAP|ACTION_CONTACT|IMPLEMENT_OBJECT|NONE": 3,
    "OVERLAP|ACTION_CONTACT|INSERTION_STRUCTURED|ANATOMY": 3,
    "OVERLAP|ACTION_CONTACT|MULTI_ACTOR_INTERACTION|ANATOMY": 3,
    "OVERLAP|ACTION_CONTACT|POSE_COMPOSITION|ANATOMY": 3,
    "OVERLAP|ACTION_CONTACT|REACTION_STATE|NONE": 3,
    "OVERLAP|ACTION_CONTACT|SELF_ACTION|ANATOMY": 3,
    "OVERLAP|BODY_PART|NONHUMAN_INTERACTION|ANATOMY": 3,
    "OVERLAP|CLOTHING_STATE_EXPOSURE|BODY_ATTRIBUTE|EXPOSURE_INTIMATE": 3,
    "OVERLAP|CLOTHING|NONHUMAN_INTERACTION|NONE": 3,
    "OVERLAP|CLOTHING|RESTRAINT_ACTION|NONE": 3,
    "OVERLAP|OBJECT_PROP|(none)|ANATOMY": 3,
    "OVERLAP|OBJECT_PROP|(none)|EXPLICIT_SEX": 3,
    "OVERLAP|OBJECT_PROP|NONHUMAN_INTERACTION|NONE": 3,
    "OVERLAP|POSE_MOVEMENT|RESTRAINT_ACTION|NONE": 3,
    "OVERLAP|STYLE_QUALITY_META|DAMAGE_STATE_ACTION|NONE": 3,
    "OVERLAP|STYLE_QUALITY_META|RELATION_ROLE_CONTEXT|NONE": 3,
    "SPECIAL_ONLY|(none)|(none)|RELATIONSHIP_ROLE": 3,
    "GENERAL_ONLY|(none)|ANATOMY": 2,
    "GENERAL_ONLY|(none)|EXPOSURE_INTIMATE": 2,
    "GENERAL_ONLY|ACTION_CONTACT/INTERACTION|EXPLICIT_SEX": 2,
    "GENERAL_ONLY|ACTION_CONTACT/INTIMATE|ADULT_ROLE_DEVICE": 2,
    "GENERAL_ONLY|ACTION_CONTACT/INTIMATE|ANATOMY": 2,
    "GENERAL_ONLY|ACTION_CONTACT/INTIMATE|EXPLICIT_SEX": 2,
    "GENERAL_ONLY|ACTION_CONTACT/INTIMATE|RELATIONSHIP_ROLE": 2,
    "GENERAL_ONLY|ACTION_CONTACT/OBJECT_USE|ANATOMY": 2,
}

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


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return '_'.join(v.strip().lower().replace('_', ' ').split())


def root(path: str) -> str:
    path = (path or '').strip()
    return path.split('/', 1)[0] if path else '(none)'


def flags(key: str) -> str:
    k = key.lower()
    parts = {p for p in re.split(r'[_()\-/]+', k) if p}
    hit = {name for name, terms in LEX_GROUPS.items() if parts & terms}
    if re.search(r'(?:^|[_/\-])g[_\-]string(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])see[_\-]through(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])t[_\-]back(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])micro(?:dress|skirt|shorts|pants|top|shirt)(?:$|[_/\-])', k):
        hit.add('SEXUALIZED_CLOTHING')
    if re.search(r'(?:^|[_/\-])(?:top[/_-]bottom|bottom[/_-]top)[_/-]dynamic(?:$|[_/\-])', k):
        hit.add('RELATIONSHIP_ROLE')
    return '+'.join(sorted(hit)) if hit else 'NONE'


def main() -> int:
    general = read_csv(GENERAL)
    special = read_csv(SPECIAL)
    side = read_csv(SIDECAR)
    g = {norm(r['canonical']): r for r in general}
    s = {norm(r['Tag']): r for r in special}

    rows = []
    counts = Counter()

    for r in side:
        if r['review_status'] != 'UNCLASSIFIED':
            continue
        key = r['identity_key']
        gr = g.get(key)
        sr = s.get(key)
        if gr is not None and r.get('is_special') == 'YES':
            membership = 'OVERLAP'
        elif gr is not None:
            membership = 'GENERAL_ONLY'
        else:
            membership = 'SPECIAL_ONLY'

        path = ((gr or {}).get('primary_path') or '').strip() or '(none)'
        rt = root(path if path != '(none)' else '')
        fam = ((sr or {}).get('GenerationFamily') or '').strip() or '(none)'
        fl = flags(key)

        if membership == 'GENERAL_ONLY':
            cluster_key = '|'.join([membership, path, fl])
        else:
            cluster_key = '|'.join([membership, rt, fam, fl])

        if cluster_key not in TARGETS:
            continue

        counts[cluster_key] += 1
        rows.append({
            'identity_key': key,
            'candidate_cluster': cluster_key,
            'candidate_state': 'FULL_REVIEW_HIGH_RISK_HUNDRED_ROW_V100',
            'human_intent': '',
            'review_note': '',
        })

    expected = dict(TARGETS)
    if dict(counts) != expected:
        raise SystemExit(f'cluster count drift: expected {expected}, got {dict(counts)}')
    if len(rows) != 100:
        raise SystemExit(f'expected 100 rows, got {len(rows)}')

    rows.sort(key=lambda r: (r['candidate_cluster'], r['identity_key']))
    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','candidate_cluster','candidate_state','human_intent','review_note']
    with (OUT / 'full_review_candidate_v100.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

    summary = {
        'issue': 118,
        'mode': 'HIGH_RISK_HUNDRED_ROW_FULL_REVIEW_V100',
        'source_sidecar': 'research_sidecar_v68.csv',
        'candidate_rows': len(rows),
        'cluster_counts': dict(sorted(counts.items())),
        'selection_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'auto_promotion_performed': 'NO',
        'review_verdicts_generated_by_materializer': 'NO',
        'review_artifacts_are_external_inputs': 'YES',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'full manual review of all 100 rows',
    }
    (OUT / 'summary_v100.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
