#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL=Path('data/generation/special2788_generation_profile.csv')
SIDECAR=Path('docs/issue118/research_sidecar_v26.csv')
OUT=Path('docs/issue118/overlap_action_anatomy_review_v43')

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
def root(path):
    path=(path or '').strip(); return path.split('/',1)[0] if path else '(none)'
def flags(key):
    k=key.lower(); parts={p for p in re.split(r'[_()\-/]+',k) if p}; hit={n for n,t in LEX_GROUPS.items() if parts&t}
    return '+'.join(sorted(hit)) if hit else 'NONE'

def main():
    general=read_csv(GENERAL); special=read_csv(SPECIAL); side=read_csv(SIDECAR)
    g={norm(r['canonical']):r for r in general}; s={norm(r['Tag']):r for r in special}; rows=[]
    for r in side:
        if r['review_status']!='UNCLASSIFIED' or r.get('is_special')!='YES':continue
        key=r['identity_key']; gr=g.get(key); sr=s.get(key)
        if gr is None or sr is None:continue
        if root(gr.get('primary_path') or '')!='ACTION_CONTACT':continue
        if (sr.get('GenerationFamily') or '').strip()!='ACTION_INTERACTION':continue
        if flags(key)!='ANATOMY':continue
        rows.append({'identity_key':key,'candidate_state':'FULL_REVIEW_OVERLAP_ACTION_ANATOMY_V43','human_intent':'','review_note':''})
    rows.sort(key=lambda r:r['identity_key'])
    if len(rows)!=53:raise SystemExit(f'expected 53 rows, got {len(rows)}')
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'full_review_candidate_v43.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['identity_key','candidate_state','human_intent','review_note'],lineterminator='\n');w.writeheader();w.writerows(rows)
    summary={'issue':118,'mode':'OVERLAP_ACTION_ANATOMY_FULL_REVIEW_V43','candidate_rows':53,'selection_rules_use':'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY','auto_promotion_performed':'NO','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO','next_gate':'full manual review of all 53 rows'}
    (OUT/'summary_v43.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(summary,ensure_ascii=False,sort_keys=True)); return 0

if __name__=='__main__':raise SystemExit(main())
