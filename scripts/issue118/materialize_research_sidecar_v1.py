#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL = Path('data/generation/special2788_generation_profile.csv')
ISSUE104 = Path('docs/issue104/product_fit_review_v1.csv')
PILOT_REVIEWS = Path('docs/issue118/reviews')
HOLDOUT_REVIEWS = Path('docs/issue118/holdout/reviews')
OUT = Path('docs/issue118/research_sidecar_v1.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v1.json')
SCHEMA = Path('docs/issue118/RESEARCH_SIDECAR_CONTRACT_v1.md')

SAFE_ROOTS_V2 = {
    'COMPOSITION_CAMERA','HAIR_FACE','LIGHT_TIME_WEATHER',
    'LIVING_NATURE','PLACE_BACKGROUND','TEXT_SYMBOL'
}
SEXUAL_V2 = [
    re.compile(r'(^|_)(handjob|blowjob|fellatio|paizuri|irrumatio|cum|cumshot|ejaculation|orgasm|masturbation|vibrator|dildo|buttjob|threesome|zoophilia|prostitution|penetration)($|_)'),
    re.compile(r'(^|_)sex($|_)'),
]
VALID_CLASSES = {'SEXUAL','NON_SEXUAL','CONTEXTUAL'}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return '_'.join(v.strip().lower().replace('_',' ').split())


def root(row: dict[str,str] | None) -> str:
    p=(row or {}).get('primary_path','').strip()
    return p.split('/',1)[0] if p else ''


def load_human_reviews() -> dict[str, tuple[str|None,str,str]]:
    result: dict[str, tuple[str|None,str,str]] = {}
    for source, directory, pattern in [
        ('PILOT_700', PILOT_REVIEWS, 'chunk_???_review_v1.csv'),
        ('HOLDOUT_240', HOLDOUT_REVIEWS, 'chunk_*_review_v1.csv'),
    ]:
        for path in sorted(directory.glob(pattern)):
            for r in read_csv(path):
                key=norm(r['identity_key'])
                status=(r.get('pilot_review_status') or r.get('review_status') or '').strip()
                cls=(r.get('reviewed_class') or '').strip()
                value=cls if status == 'REVIEWED' and cls in VALID_CLASSES else None
                if key in result:
                    raise SystemExit(f'duplicate human review identity: {key}')
                result[key]=(value, source, path.name)
    return result


def main() -> int:
    general=read_csv(GENERAL); special=read_csv(SPECIAL); issue104=read_csv(ISSUE104)
    if len(general)!=30629 or len(special)!=3059:
        raise SystemExit(f'input drift general={len(general)} special={len(special)}')
    g={norm(r['canonical']):r for r in general}; s={norm(r['Tag']):r for r in special}
    if len(g)!=30629 or len(s)!=3059: raise SystemExit('normalized source collision')
    risk={norm(r['canonical_tag']) for r in issue104}
    human=load_human_reviews()
    if len(human)!=940: raise SystemExit(f'expected 940 disjoint human-reviewed identities, got {len(human)}')

    union=sorted(set(g)|set(s))
    if len(union)!=31752: raise SystemExit(f'union drift {len(union)}')
    missing_review=set(human)-set(union)
    if missing_review: raise SystemExit(f'human review identities missing from current union: {len(missing_review)}')

    rows=[]; status_counts=Counter(); class_counts=Counter(); rule_counts=Counter()
    for key in union:
        gr=g.get(key); sr=s.get(key)
        semantic=None; review_status='UNCLASSIFIED'; evidence=''; rule_id=''
        if key in human:
            semantic, source, file_name=human[key]
            if semantic is not None:
                review_status='HUMAN_REVIEWED'
                evidence=f'{source}:{file_name}'
            else:
                review_status='UNCLASSIFIED'
                evidence=f'{source}:{file_name}:UNRESOLVED'
        else:
            nonsex = gr is not None and sr is None and key not in risk and root(gr) in SAFE_ROOTS_V2
            sexual = sr is not None and any(p.search(key) for p in SEXUAL_V2)
            if nonsex and sexual: raise SystemExit(f'auto rule conflict: {key}')
            if nonsex:
                semantic='NON_SEXUAL'; review_status='AUTO_HIGH_CONF'; rule_id='AUTO_NONSEX_SAFE_GENERAL_ROOTS_V2'; evidence='PILOT_61_61+HOLDOUT_120_120'
            elif sexual:
                semantic='SEXUAL'; review_status='AUTO_HIGH_CONF'; rule_id='AUTO_SEXUAL_EXPLICIT_SPECIAL_LEXEMES_V2'; evidence='PILOT_23_23+HOLDOUT_80_80'
        status_counts[review_status]+=1
        class_counts[semantic or 'NULL']+=1
        if rule_id: rule_counts[rule_id]+=1
        rows.append({
            'identity_key':key,
            'is_general':'YES' if gr is not None else 'NO',
            'is_special':'YES' if sr is not None else 'NO',
            'sexual_intent':semantic or '',
            'review_status':review_status,
            'rule_id':rule_id,
            'evidence':evidence,
        })

    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0]); w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)

    summary={
        'issue':118,
        'mode':'RESEARCH_SIDECAR_V1',
        'identity_rows':len(rows),
        'general_rows':len(g),
        'special_rows':len(s),
        'overlap_rows':len(set(g)&set(s)),
        'human_review_evidence_rows':len(human),
        'review_status_counts':dict(sorted(status_counts.items())),
        'sexual_intent_counts':dict(sorted(class_counts.items())),
        'auto_rule_counts':dict(sorted(rule_counts.items())),
        'precedence':['HUMAN_REVIEWED','AUTO_HIGH_CONF','UNCLASSIFIED'],
        'unknown_representation':'sexual_intent empty + review_status UNCLASSIFIED',
        'production_authority':'NO',
        'main_mutated':'NO',
        'issue117_code_mutated':'NO',
        'catalog_mutated':'NO',
        'user_db_mutated':'NO',
    }
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    SCHEMA.write_text('''# Issue #118 research sidecar contract v1\n\nResearch evidence only. This file is not production authority.\n\n## Identity\n\nExactly one row per normalized unified Tag identity. Current expected population: 31,752.\n\n## Fields\n\n- `identity_key`: normalized identity key.\n- `is_general`: current General membership.\n- `is_special`: current Special membership.\n- `sexual_intent`: `SEXUAL`, `NON_SEXUAL`, `CONTEXTUAL`, or empty when unclassified.\n- `review_status`: `HUMAN_REVIEWED`, `AUTO_HIGH_CONF`, or `UNCLASSIFIED`.\n- `rule_id`: populated only for automatic candidate evidence.\n- `evidence`: review/rule provenance.\n\n## Semantics\n\n`CONTEXTUAL` is a semantic verdict: the concept itself has substantial natural sexual and non-sexual use. It is not uncertainty.\n\nEmpty `sexual_intent` + `UNCLASSIFIED` is epistemic uncertainty and MUST NOT silently map to `NON_SEXUAL`.\n\n## Precedence\n\nHuman-reviewed evidence overrides automatic candidate rules. Automatic rules may classify only rows not already human-reviewed. Everything else stays explicitly unclassified.\n\n## Runtime boundary\n\nThis research sidecar is not a runtime dependency and is not yet wired into Issue #117. A later accepted production sidecar may be baked into compact catalog metadata at build time.\n''',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
