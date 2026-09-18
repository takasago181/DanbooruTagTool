#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL=Path('data/generation/special2788_generation_profile.csv')
SIDECAR=Path('docs/issue118/research_sidecar_v69.csv')
OUT=Path('docs/issue118/remaining_small_clusters_review_v102')
BATCH_ROWS=100
EXPECTED_ELIGIBLE=242
RETAINED={'knee_boobs','powerful_ass','cock-tail','mushikan','licking_tip'}

LEX_GROUPS={
 'EXPLICIT_SEX':{'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm','masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia','rape','cunnilingus','anilingus','fingering','footjob','creampie','bukkake','fleshlight','onahole','fuck','fucking'},
 'ANATOMY':{'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples','breast','breasts','areola','areolae','pubic','crotch','genital'},
 'RESTRAINT_FETISH':{'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps','collar','fetish','bdsm','spanking','whip'},
 'REPRO':{'pregnant','pregnancy','lactation','breastfeeding','birth','insemination','fertilization','fertilisation','impregnation'},
 'INJURY':{'blood','wound','gore','amputee','amputation','castration','corpse','injury','snuff'},
 'EXPOSURE_INTIMATE':{'nude','naked','topless','bottomless','panty','panties','underwear','bra','cleavage','underboob','upskirt','downblouse','lingerie','crotchless','pasties','maebari'},
 'ADULT_ROLE_DEVICE':{'condom','condoms','porn','pornstar','stripper','prostitute','courtesan','oiran','speculum','bodystocking','bustier','gravure'},
 'RELATIONSHIP_ROLE':{'brocon','siscon','lolicon','shotacon','incest','virgin','virginity','seme','uke','femdom','maledom','ageplay','cuckold','cuckquean','netorare','netori','ntr'},
 'SEXUALIZED_CLOTHING':{'bikini','swimsuit','swimwear','thong','garter','garters','gstring','fishnet','fishnets','corset','harness','latex','leotard','bodysuit','bunnysuit','playboy','fetishwear','bodycon','slingshot','highleg','lowleg','sheer','transparent','frontless','backless','assless','sideless','tankini','monokini','trikini','microdress','dongtan'},
}

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return '_'.join(v.strip().lower().replace('_',' ').split())
def root(path):
    path=(path or '').strip(); return path.split('/',1)[0] if path else '(none)'
def flags(key):
    k=key.lower(); parts={p for p in re.split(r'[_()\-/]+',k) if p}
    hit={name for name,terms in LEX_GROUPS.items() if parts & terms}
    if re.search(r'(?:^|[_/\-])g[_\-]string(?:$|[_/\-])',k) or re.search(r'(?:^|[_/\-])see[_\-]through(?:$|[_/\-])',k) or re.search(r'(?:^|[_/\-])t[_\-]back(?:$|[_/\-])',k) or re.search(r'(?:^|[_/\-])micro(?:dress|skirt|shorts|pants|top|shirt)(?:$|[_/\-])',k):
        hit.add('SEXUALIZED_CLOTHING')
    if re.search(r'(?:^|[_/\-])(?:top[/_-]bottom|bottom[/_-]top)[_/-]dynamic(?:$|[_/\-])',k):
        hit.add('RELATIONSHIP_ROLE')
    return '+'.join(sorted(hit)) if hit else 'NONE'

def main():
    general=read_csv(GENERAL); special=read_csv(SPECIAL); side=read_csv(SIDECAR)
    g={norm(r['canonical']):r for r in general}; s={norm(r['Tag']):r for r in special}
    eligible=[]
    giant=0
    for r in side:
        if r['review_status']!='UNCLASSIFIED':continue
        key=r['identity_key']; gr=g.get(key); sr=s.get(key)
        if gr is not None and r.get('is_special')=='YES':membership='OVERLAP'
        elif gr is not None:membership='GENERAL_ONLY'
        else:membership='SPECIAL_ONLY'
        path=((gr or {}).get('primary_path') or '').strip() or '(none)'
        rt=root(path if path!='(none)' else '')
        fam=((sr or {}).get('GenerationFamily') or '').strip() or '(none)'
        fl=flags(key)
        ck='|'.join([membership,path,fl]) if membership=='GENERAL_ONLY' else '|'.join([membership,rt,fam,fl])
        if ck=='GENERAL_ONLY|(none)|NONE':
            giant+=1; continue
        if key in RETAINED:
            continue
        eligible.append((ck,key))
    eligible.sort()
    if giant!=2237: raise SystemExit(f'giant cluster drift {giant}')
    if len(eligible)!=EXPECTED_ELIGIBLE: raise SystemExit(f'expected {EXPECTED_ELIGIBLE} eligible small-cluster rows, got {len(eligible)}')
    chosen=eligible[:BATCH_ROWS]
    rows=[{'identity_key':key,'candidate_cluster':ck,'candidate_state':'FULL_REVIEW_REMAINING_SMALL_CLUSTERS_V102_BATCH1','human_intent':'','review_note':''} for ck,key in chosen]
    OUT.mkdir(parents=True,exist_ok=True)
    fields=['identity_key','candidate_cluster','candidate_state','human_intent','review_note']
    with (OUT/'full_review_candidate_v102.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
    summary={'issue':118,'mode':'REMAINING_SMALL_CLUSTERS_FULL_REVIEW_V102_BATCH1','source_sidecar':'research_sidecar_v69.csv',
      'giant_cluster_excluded':'GENERAL_ONLY|(none)|NONE','giant_cluster_rows':giant,'retained_exclusions':sorted(RETAINED),
      'eligible_small_cluster_rows':len(eligible),'candidate_rows':len(rows),
      'batch_selection':'first 100 rows sorted by cluster_key then identity_key from all remaining non-giant clusters after excluding prior intentional UNCLASSIFIED rows; selection only, not classification authority',
      'selection_rules_use':'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY','auto_promotion_performed':'NO',
      'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES',
      'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO',
      'next_gate':'full manual review of all 100 rows'}
    (OUT/'summary_v102.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True)); return 0
if __name__=='__main__':raise SystemExit(main())
