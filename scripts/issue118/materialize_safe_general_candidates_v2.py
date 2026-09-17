#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR=Path('docs/issue118/research_sidecar_v1.csv')
PILOT=Path('docs/issue118/reviews')
HOLDOUT=Path('docs/issue118/holdout/reviews')
OUT=Path('docs/issue118/safe_general_candidates_v2')
MANUAL_RISK={
 'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm','masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia','rape','cunnilingus','anilingus','fingering','footjob','creampie','bukkake','onahole','fleshlight','fuck','fucking',
 'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples','breast','breasts','areola','areolae','pubic','crotch','ass','genital','erection','erect',
 'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps','bound','slave','bdsm','spanking','whip','collar','fetish','femdom','netorare','incest','ageplay',
 'nude','naked','topless','bottomless','panties','underwear','bra','cleavage','underboob','upskirt','downblouse','crotchless','lingerie','maebari','pasties','striptease',
 'pregnant','pregnancy','lactation','breastfeeding','birth','insemination','fertilization','fertilisation','impregnation','ahegao','ecstasy','arousal','aroused'
}
TARGET_PATHS={
 'CLOTHING/EVERYDAY','OBJECT_PROP/DAILY','CLOTHING/ACCESSORY','CLOTHING/COSTUME','OBJECT_PROP/WEAPON','STYLE_QUALITY_META','OBJECT_PROP/FOOD','ACTION_CONTACT/OBJECT_USE','PERSON_COUNT','CLOTHING/UNIFORM','OBJECT_PROP/VEHICLE','OBJECT_PROP'
}
def read_csv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return '_'.join(v.strip().lower().replace('_',' ').split())
def tokens(k):return [x for x in re.split(r'[_()\-]+',k.lower()) if x]
def rank(seed,key):return hashlib.sha256(f'{seed}|{key}'.encode()).hexdigest()
def load_reviews():
 out={}
 for d,statusf in [(PILOT,'pilot_review_status'),(HOLDOUT,'review_status')]:
  for p in sorted(d.glob('chunk_*_review_v1.csv')):
   for r in read_csv(p):
    st=(r.get(statusf) or r.get('review_status') or '').strip();cls=(r.get('reviewed_class') or '').strip();k=norm(r['identity_key'])
    if st=='REVIEWED' and cls in {'SEXUAL','NON_SEXUAL','CONTEXTUAL'}:out[k]=cls
 return out
def main():
 general=read_csv(GENERAL);side=read_csv(SIDECAR);reviews=load_reviews();g={norm(r['canonical']):r for r in general}
 tc=defaultdict(Counter)
 for k,cls in reviews.items():
  for t in set(tokens(k)):tc[t][cls]+=1
 learned=set()
 for t,c in tc.items():
  risk=c['SEXUAL']+c['CONTEXTUAL'];total=risk+c['NON_SEXUAL']
  if risk>=2 and total>=2 and risk/total>=0.80:learned.add(t)
 risk_tokens=MANUAL_RISK|learned
 candidates=[];by_path=Counter();excluded=Counter()
 for r in side:
  if r['review_status']!='UNCLASSIFIED' or r['is_general']!='YES' or r['is_special']=='YES':continue
  k=r['identity_key'];gr=g[k];path=(gr.get('primary_path') or '').strip()
  if path not in TARGET_PATHS:continue
  hits=sorted(set(tokens(k)) & risk_tokens)
  if hits:
   excluded[path]+=1;continue
  candidates.append({'identity_key':k,'general_path':path,'confidence':(gr.get('confidence') or '').strip(),'risk_tokens':'','candidate_class':'NON_SEXUAL'})
  by_path[path]+=1
 # Validate against all existing reviewed identities using the exact same predicate.
 eval_counts=defaultdict(Counter);eval_examples=defaultdict(list)
 for k,cls in reviews.items():
  gr=g.get(k)
  if not gr:continue
  # only General-only in current sources
  sr=next((x for x in side if x['identity_key']==k),None)
  if sr and sr['is_special']=='YES':continue
  path=(gr.get('primary_path') or '').strip()
  if path not in TARGET_PATHS or set(tokens(k)) & risk_tokens:continue
  eval_counts[path][cls]+=1
  if cls!='NON_SEXUAL' and len(eval_examples[path])<10:eval_examples[path].append(k)
 accepted_paths=[]
 for p,n in by_path.items():
  c=eval_counts[p];total=sum(c.values())
  if total>=3 and c['NON_SEXUAL']==total:accepted_paths.append(p)
 accepted_paths=sorted(accepted_paths)
 accepted=[r for r in candidates if r['general_path'] in accepted_paths]
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/'candidate_inventory_v2.csv').open('w',encoding='utf-8',newline='') as f:
  fields=['identity_key','general_path','confidence','risk_tokens','candidate_class'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(accepted)
 # Dedicated discovery/holdout sample from accepted paths, 6+6 per path capped at 240.
 sample=[]
 for p in sorted(accepted_paths,key=lambda x:(-sum(1 for r in accepted if r['general_path']==x),x)):
  items=sorted([r for r in accepted if r['general_path']==p],key=lambda r:rank('issue118-safe-general-v2',r['identity_key']))
  chosen=items[:12]
  if len(sample)+len(chosen)>240:continue
  for i,r in enumerate(chosen):
   x=dict(r);x['phase']='DISCOVERY' if i<6 else 'HOLDOUT';x['path_population']=str(by_path[p]);sample.append(x)
 with (OUT/'validation_sample_v2.csv').open('w',encoding='utf-8',newline='') as f:
  fields=['identity_key','general_path','confidence','candidate_class','path_population','phase'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(sample)
 for old in OUT.glob('validation_chunk_*.csv'):old.unlink()
 for i in range(0,len(sample),60):
  with (OUT/f'validation_chunk_{i//60+1:03d}.csv').open('w',encoding='utf-8',newline='') as f:
   fields=['identity_key','general_path','confidence','candidate_class','path_population','phase'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(sample[i:i+60])
 summary={'issue':118,'mode':'SAFE_GENERAL_CANDIDATES_V2','reviewed_evidence_rows':len(reviews),'learned_risk_token_count':len(learned),'total_risk_token_count':len(risk_tokens),'target_paths':sorted(TARGET_PATHS),'accepted_paths':accepted_paths,'accepted_candidate_rows':len(accepted),'accepted_path_counts':dict(sorted(Counter(r['general_path'] for r in accepted).items())),'validation_sample_rows':len(sample),'validation_chunks':(len(sample)+59)//60,'existing_review_validation':{p:{'counts':dict(sorted(eval_counts[p].items())),'non_target_examples':eval_examples[p]} for p in sorted(TARGET_PATHS)},'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO'}
 (OUT/'summary_v2.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (OUT/'risk_tokens_v2.txt').write_text('\n'.join(sorted(risk_tokens))+'\n',encoding='utf-8')
 print(json.dumps({'accepted_paths':accepted_paths,'accepted_candidate_rows':len(accepted),'validation_sample_rows':len(sample),'total_risk_token_count':len(risk_tokens)},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
