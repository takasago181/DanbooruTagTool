#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v51.csv')
OUT = Path('docs/issue118/general_action_interaction_none_review_v78')
EXPECTED_CLUSTER_ROWS = 495
BATCH_ROWS = 100

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
    general=read_csv(GENERAL)
    side=read_csv(SIDECAR)
    g={norm(r['canonical']):r for r in general}
    cluster=[]
    for r in side:
        if r['review_status']!='UNCLASSIFIED' or r.get('is_special')=='YES':
            continue
        key=r['identity_key']
        gr=g.get(key)
        if gr is None:
            continue
        if (gr.get('primary_path') or '').strip()!='ACTION_CONTACT/INTERACTION':
            continue
        if flags(key)!='NONE':
            continue
        cluster.append(key)

    cluster=sorted(cluster)
    if len(cluster)!=EXPECTED_CLUSTER_ROWS:
        raise SystemExit(f'expected {EXPECTED_CLUSTER_ROWS} cluster rows, got {len(cluster)}')

    chosen=cluster[:BATCH_ROWS]
    rows=[{
        'identity_key':key,
        'candidate_cluster':'GENERAL_ONLY|ACTION_CONTACT/INTERACTION|NONE',
        'candidate_state':'FULL_REVIEW_GENERAL_ACTION_INTERACTION_NONE_V78_BATCH4',
        'human_intent':'',
        'review_note':'',
    } for key in chosen]

    OUT.mkdir(parents=True,exist_ok=True)
    fields=['identity_key','candidate_cluster','candidate_state','human_intent','review_note']
    with (OUT/'full_review_candidate_v78.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n')
        w.writeheader(); w.writerows(rows)

    summary={
        'issue':118,
        'mode':'GENERAL_ACTION_INTERACTION_NONE_FULL_REVIEW_V78_BATCH4',
        'source_sidecar':'research_sidecar_v51.csv',
        'source_cluster':'GENERAL_ONLY|ACTION_CONTACT/INTERACTION|NONE',
        'source_cluster_rows':len(cluster),
        'candidate_rows':len(rows),
        'batch_selection':'alphabetically first 100 identities from the remaining fixed General-only Action/Interaction cluster after V77; selection only, not classification authority',
        'first_identity':chosen[0],
        'last_identity':chosen[-1],
        'selection_rules_use':'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'auto_promotion_performed':'NO',
        'review_verdicts_generated_by_materializer':'NO',
        'review_artifacts_are_external_inputs':'YES',
        'production_authority':'NO',
        'main_mutated':'NO',
        'issue117_code_mutated':'NO',
        'catalog_mutated':'NO',
        'user_db_mutated':'NO',
        'next_gate':'full manual review of all 100 rows',
    }
    (OUT/'summary_v78.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
