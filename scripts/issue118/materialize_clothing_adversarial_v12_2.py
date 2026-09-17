#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path('docs/issue118/clothing_everyday_refinement_v12_1/clothing_clean_v12_1.csv')
OUT = Path('docs/issue118/clothing_adversarial_v12_2')

# Human-selected semantic-risk subset of the learned v9 vocabulary plus a few
# obvious sexualized-clothing descriptors. These are discovery/exclusion hints
# only. Generic high-lift tokens such as meme/face/one/through/skirt are excluded.
RISK_TOKENS = {
    'sex','sexual','sexy','erotic','erotica','ecchi','hentai','nsfw','r18','fetish','fetishwear',
    'seductive','revealing','skimpy','risque','provocative','slut','slutty','dominatrix',
    'cum','dildo','threesome','penetration','vibrator','handjob','masturbation','fellatio','paizuri',
    'condom','ejaculation','orgasm','anal','blowjob','buttjob','naked','panties','penis','nipple','nipples',
    'pussy','vagina','vulva','clitoris','crotch','breast','breasts','gag','blindfold','handcuffs','bondage',
    'restraints','leash','rope','bra','underwear','thighhighs','latex','pasties','pregnant','groping','irrumatio',
    'vaginal','futa','peeing','nursing','wet','implied','imminent','forced','licking','milking','tentacle',
}

RISK_STEMS = {
    'crotchless','assless','bottomless','topless','underboob','sideboob','downblouse','upskirt',
    'porn','stripper','prostitut','onahole','fleshlight','bukkake','creampie','cunniling','aniling',
    'masturb','ejaculat','orgasm','impregn','lactat','bondage','fetish','dominatrix','slingshot',
    'microbikini','micro_bikini','micro-bikini','gstring','g-string','see_through','see-through',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def tokens(key: str) -> set[str]:
    return {p for p in re.split(r'[^a-z0-9]+', key.lower()) if p}


def redteam_flags(key: str) -> list[str]:
    t = tokens(key)
    flags = []
    hits = sorted(t & RISK_TOKENS)
    if hits:
        flags.append('risk_token:' + ','.join(hits))
    k = key.lower()
    stems = sorted(stem for stem in RISK_STEMS if stem in k)
    if stems:
        flags.append('risk_stem:' + ','.join(stems))
    return flags


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v12.2-clothing-fresh-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 2704:
        raise SystemExit(f'expected v12.1 clean population 2704, got {len(src)}')

    flagged = []
    clean = []
    for r in src:
        key = r['identity_key']
        flags = redteam_flags(key)
        out = {
            'identity_key': key,
            'redteam_flags': '|'.join(flags),
            'candidate_state': 'REDTEAM_REVIEW' if flags else 'CLEAN_FOR_FRESH_HOLDOUT_V12_2',
        }
        if flags:
            flagged.append(out)
        else:
            clean.append(out)

    flagged.sort(key=lambda r: r['identity_key'])
    clean.sort(key=lambda r: r['identity_key'])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough clean rows for v12.2 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','redteam_flags','candidate_state']
    for name, rows in [
        ('redteam_review_v12_2.csv', flagged),
        ('clothing_clean_v12_2.csv', clean),
    ]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            w.writeheader()
            w.writerows(rows)

    holdout_fields = ['identity_key','candidate_state','human_intent','review_note']
    with (OUT / 'fresh_holdout_template_v12_2.csv').open('w', encoding='utf-8', newline='') as f:
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
        'mode': 'CLOTHING_ADVERSARIAL_V12_2',
        'source_clean_rows_v12_1': len(src),
        'redteam_review_rows': len(flagged),
        'clean_candidate_rows_v12_2': len(clean),
        'fresh_holdout_template_rows': len(holdout),
        'risk_vocabulary_basis': 'human-selected semantic-risk subset of learned v9 tokens plus explicit sexualized-clothing descriptors',
        'risk_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'semantic_authority': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review redteam rows and new fixed 120-row holdout; freeze both review artifacts before any research-sidecar promotion',
    }
    (OUT / 'summary_v12_2.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
