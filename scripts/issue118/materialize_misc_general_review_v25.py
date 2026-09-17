#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v12.csv')
OUT = Path('docs/issue118/misc_general_review_v25')

TARGET_ROOTS = {
    'STYLE_QUALITY_META',
    'COLOR_APPEARANCE',
    'COMPOSITION_CAMERA',
    'PLACE_BACKGROUND',
    'GAZE_ORIENTATION',
    'LIVING_NATURE',
    'TEXT_SYMBOL',
    'HAIR_FACE',
    'EXPRESSION_EMOTION',
}

LEX_GROUPS = {
    'EXPLICIT_SEX': {'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm','masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia','rape','cunnilingus','anilingus','fingering','footjob','creampie','bukkake','fleshlight','onahole','fuck','fucking'},
    'ANATOMY': {'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples','breast','breasts','areola','areolae','pubic','crotch','genital'},
    'RESTRAINT_FETISH': {'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps','collar','fetish','bdsm','spanking','whip'},
    'REPRO': {'pregnant','pregnancy','lactation','breastfeeding','birth','insemination','fertilization','fertilisation','impregnation'},
    'EXPOSURE_INTIMATE': {'nude','naked','topless','bottomless','panty','panties','underwear','bra','cleavage','underboob','upskirt','downblouse','lingerie','crotchless','pasties','maebari'},
    'ADULT_ROLE_DEVICE': {'condom','condoms','porn','pornstar','stripper','prostitute','speculum','bodystocking','bustier','gravure'},
    'RELATIONSHIP_ROLE': {'brocon','siscon','lolicon','shotacon','incest','virgin','virginity','seme','uke','femdom','maledom','ageplay','cuckold','cuckquean','netorare','netori','ntr'},
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace('_', ' ').split())


def root(path: str) -> str:
    return path.split('/', 1)[0] if path else ''


def risk_flag(key: str) -> bool:
    parts = {p for p in re.split(r'[_()\-/]+', key.lower()) if p}
    return any(parts & terms for terms in LEX_GROUPS.values())


def main() -> int:
    general = read_csv(GENERAL)
    side = read_csv(SIDECAR)
    g = {norm(r['canonical']): r for r in general}

    selected = []
    excluded = []
    root_counts = Counter()
    for r in side:
        if r['review_status'] != 'UNCLASSIFIED' or r.get('is_special') == 'YES':
            continue
        key = r['identity_key']
        gr = g.get(key)
        if gr is None:
            continue
        path = (gr.get('primary_path') or '').strip()
        rt = root(path)
        if rt not in TARGET_ROOTS:
            continue
        if risk_flag(key):
            excluded.append({'identity_key': key, 'general_root': rt, 'state': 'RISK_EJECTED_V25'})
            continue
        selected.append({'identity_key': key, 'general_root': rt, 'state': 'FULL_REVIEW_CANDIDATE_V25'})
        root_counts[rt] += 1

    selected.sort(key=lambda r: (r['general_root'], r['identity_key']))
    excluded.sort(key=lambda r: (r['general_root'], r['identity_key']))

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'full_review_candidate_v25.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','general_root','state'], lineterminator='\n')
        w.writeheader(); w.writerows(selected)
    with (OUT / 'risk_ejected_v25.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','general_root','state'], lineterminator='\n')
        w.writeheader(); w.writerows(excluded)

    summary = {
        'issue': 118,
        'mode': 'MISC_GENERAL_FULL_REVIEW_CANDIDATES_V25',
        'target_roots': sorted(TARGET_ROOTS),
        'candidate_rows': len(selected),
        'risk_ejected_rows': len(excluded),
        'candidate_root_counts': dict(sorted(root_counts.items())),
        'selection_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'full manual review of every candidate row; do not bulk promote from root membership alone'
    }
    (OUT / 'summary_v25.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
