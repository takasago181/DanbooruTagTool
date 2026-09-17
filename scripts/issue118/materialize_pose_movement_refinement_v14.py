#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v5.csv')
OUT = Path('docs/issue118/pose_movement_refinement_v14')

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

POSE_PATTERNS = [
    ('named_sex_position', re.compile(r'(?:^|[_\-/])(doggystyle|doggy[_-]?style|missionary|reverse[_-]?cowgirl|cowgirl[_-]?position|mating[_-]?press|prone[_-]?bone|piledriver|amazon[_-]?position)(?:$|[_\-/])')),
    ('spread_or_raised_legs', re.compile(r'(?:^|[_\-/])(spread[_-]?legs|legs[_-]?apart|knees[_-]?apart|legs?[_-]?up)(?:$|[_\-/])')),
    ('all_fours', re.compile(r'(?:^|[_\-/])(on[_-]?all[_-]?fours|all[_-]?fours|hands[_-]?and[_-]?knees)(?:$|[_\-/])')),
    ('bent_over', re.compile(r'(?:^|[_\-/])(bent[_-]?over|bending[_-]?over)(?:$|[_\-/])')),
    ('straddling', re.compile(r'(?:^|[_\-/])straddl(?:e|ing|ed)?(?:$|[_\-/])')),
    ('sexualized_dance_pose', re.compile(r'(?:^|[_\-/])(twerk|twerking|lap[_-]?dance|pole[_-]?dance|grinding)(?:$|[_\-/])')),
    ('sexualized_pose_label', re.compile(r'(?:^|[_\-/])(seductive[_-]?pose|sexy[_-]?pose|pinup[_-]?pose|jack[_-]?o[_-]?pose)(?:$|[_\-/])')),
    ('pelvic_hip_thrust', re.compile(r'(?:^|[_\-/])(pelvic[_-]?thrust|hip[_-]?thrust)(?:$|[_\-/])')),
]


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace('_', ' ').split())


def v13_flags(key: str) -> set[str]:
    k = key.lower()
    parts = {p for p in re.split(r'[_()\-/]+', k) if p}
    hit = {name for name, terms in LEX_GROUPS.items() if parts & terms}
    if re.search(r'(?:^|[_/\-])g[_\-]string(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])see[_\-]through(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])t[_\-]back(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])micro(?:dress|skirt|shorts|pants|top|shirt)(?:$|[_/\-])', k):
        hit.add('SEXUALIZED_CLOTHING')
    if re.search(r'(?:^|[_/\-])(?:top[/_-]bottom|bottom[/_-]top)[_/-]dynamic(?:$|[_/\-])', k):
        hit.add('RELATIONSHIP_ROLE')
    return hit


def pose_boundary_flags(key: str) -> list[str]:
    k = key.lower()
    return [name for name, pat in POSE_PATTERNS if pat.search(k)]


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v14-pose-fresh-holdout:' + key).encode('utf-8')).hexdigest()


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
        if gr is None or (gr.get('primary_path') or '').strip() != 'POSE_MOVEMENT':
            continue
        if v13_flags(key):
            continue
        source.append(key)

    source = sorted(set(source))
    if len(source) != 726:
        raise SystemExit(f'expected v13 POSE_MOVEMENT|NONE population 726, got {len(source)}')

    boundary = []
    clean = []
    reasons = Counter()
    for key in source:
        flags = pose_boundary_flags(key)
        item = {
            'identity_key': key,
            'boundary_flags': '|'.join(flags),
            'candidate_state': 'POSE_BOUNDARY' if flags else 'CLEAN_FOR_FRESH_HOLDOUT',
        }
        if flags:
            boundary.append(item)
            reasons.update(flags)
        else:
            clean.append(item)

    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for pose holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','boundary_flags','candidate_state']
    for name, rows in [('pose_boundary_v14.csv', boundary), ('pose_clean_v14.csv', clean)]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader(); w.writerows(rows)

    with (OUT / 'fresh_holdout_template_v14.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': r['candidate_state'], 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'POSE_MOVEMENT_REFINEMENT_V14',
        'source_cluster': 'GENERAL_ONLY|POSE_MOVEMENT|NONE',
        'source_rows': len(source),
        'boundary_rows': len(boundary),
        'clean_candidate_rows': len(clean),
        'fresh_holdout_template_rows': len(holdout),
        'boundary_reason_counts': dict(sorted(reasons.items())),
        'boundary_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review fixed 120-row pose holdout; refine only on observed counterexamples',
    }
    (OUT / 'summary_v14.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
