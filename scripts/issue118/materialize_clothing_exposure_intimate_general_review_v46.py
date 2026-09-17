#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR=Path('docs/issue118/research_sidecar_v27.csv')
OUT=Path('docs/issue118/clothing_exposure_intimate_general_review_v46')

LEX_GROUPS={
'EXPLICIT_SEX':{'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm','masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia','rape','cunnilingus','anilingus','fingering','footjob','creampie','bukkake','fleshlight','onahole','fuck','fucking'},
'ANATOMY':{'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples','breast','breasts','areola','areolae','pubic','crotch','genital'},
'RESTRAINT_FETISH':{'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps','collar','fetish','bdsm','spanking','whip'},
'REPRO':{'pregnant','pregnancy','lactation','breastfeeding','birth','insemination','fertilization','fertilisation','impregnation'},
'INJURY':{'blood','wound','gore','amputee','amputation','castration','corpse','injury','snuff'},
'EXPOSURE_INTIMATE':{'nude','naked','topless','bottomless','panty','panties','underwear','bra','cleavage','underboob','upskirt','downblouse','lingerie','crotchless','pasties','maebari'},
'ADULT_ROLE_DEVICE':{'condom','condoms','porn','pornstar','stripper','prostitute','courtesan','oiran','speculum','bodystocking','bustier','gravure'},
'RELATIONSHIP_ROLE':{'brocon','siscon','lolicon','shotacon','incest','virgin','virginity','seme','uke','femdom','maledom','ageplay','cuckold','cuckquean','netorare','netori','ntr'},
'SEXUALIZED_CLOTHING':{'bikini','swimsuit','swimwear','thong','garter','garters','gstring','fishnet','fishnets','corset','harness','latex','leotard','bodysuit','bunnysuit','playboy','fetishwear','bodycon','slingshot','highleg','lowleg','sheer','transparent','frontless','backless','assless','sideless','tankini','monokini','trikini','microdress','dongtan'}}

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return '_'.join(v.strip().lower().replace('_',' ').split())
def flags(key):
    parts={p for p in re.split(r'[_()\-/]+',key.lower()) if p};hit={n for n,t in LEX_GROUPS.items() if parts&t};return '+'.join(sorted(hit)) if hit else 'NONE'

def main():
    general=read_csv(GENERAL);side=read_csv(SIDECAR);g={norm(r['canonical']):r for r in general};rows=[]
    for r in side:
        if r['review_status']!='UNCLASSIFIED' or r.get('is_special')=='YES':continue
        key=r['identity_key'];gr=g.get(key)
        if gr is None:continue
        if (gr.get('primary_path') or '').strip()!='CLOTHING_STATE_EXPOSURE':continue
        if flags(key)!='EXPOSURE_INTIMATE':continue
        rows.append({'identity_key':key,'candidate_state':'FULL_REVIEW_CLOTHING_EXPOSURE_INTIMATE_GENERAL_V46','human_intent':'','review_note':''})
    rows.sort(key=lambda r:r['identity_key'])
    if len(rows)!=38:raise SystemExit(f'expected 38 rows, got {len(rows)}')
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'full_review_candidate_v46.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['identity_key','candidate_state','human_intent','review_note'],lineterminator='\n');w.writeheader();w.writerows(rows)
    summary={'issue':118,'mode':'CLOTHING_EXPOSURE_INTIMATE_GENERAL_FULL_REVIEW_V46','candidate_rows':38,'selection_rules_use':'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY','auto_promotion_performed':'NO','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO','next_gate':'full manual review of all 38 rows'}
    (OUT/'summary_v46.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,sort_keys=True));return 0

if __name__=='__main__':raise SystemExit(main())
