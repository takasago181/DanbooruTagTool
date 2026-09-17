#!/usr/bin/env python3
from __future__ import annotations
import csv,json,re
from pathlib import Path
GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR=Path('docs/issue118/research_sidecar_v29.csv')
OUT=Path('docs/issue118/everyday_restraint_flag_review_v52')
TERMS={'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps','collar','fetish','bdsm','spanking','whip'}
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return '_'.join(v.strip().lower().replace('_',' ').split())
def main():
    general=read_csv(GENERAL);side=read_csv(SIDECAR);g={norm(r['canonical']):r for r in general};rows=[]
    for r in side:
        if r['review_status']!='UNCLASSIFIED' or r.get('is_special')=='YES':continue
        key=r['identity_key'];gr=g.get(key)
        if gr is None or (gr.get('primary_path') or '').strip()!='CLOTHING/EVERYDAY':continue
        parts={p for p in re.split(r'[_()\-/]+',key.lower()) if p}
        if not (parts & TERMS):continue
        # exclude rows carrying other known sexual-risk vocabulary; this review is specifically the restraint-only flagged Everyday cluster
        other={'sex','penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','nipple','nipples','breast','breasts','pubic','crotch','nude','naked','panty','panties','underwear','bra','lingerie','bikini','swimsuit','thong','garter','latex','harness'}
        if parts & other:continue
        rows.append({'identity_key':key,'candidate_state':'FULL_REVIEW_EVERYDAY_RESTRAINT_FLAG_V52','human_intent':'','review_note':''})
    rows.sort(key=lambda r:r['identity_key'])
    if len(rows)!=34:raise SystemExit(f'expected 34 rows, got {len(rows)}')
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'full_review_candidate_v52.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['identity_key','candidate_state','human_intent','review_note'],lineterminator='\n');w.writeheader();w.writerows(rows)
    s={'issue':118,'mode':'EVERYDAY_RESTRAINT_FLAG_FULL_REVIEW_V52','candidate_rows':34,'selection_rules_use':'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY','auto_promotion_performed':'NO','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO','next_gate':'full manual review of all 34 rows'}
    (OUT/'summary_v52.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
