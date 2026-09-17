#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL=Path('data/generation/special2788_generation_profile.csv')
SIDECAR=Path('docs/issue118/research_sidecar_v1.csv')
OUT=Path('docs/issue118/special_cluster_review_v1')

LEX_GROUPS={
 'EXPLICIT_SEX':{'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm','masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia'},
 'ANATOMY':{'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples','breast','breasts','areola','areolae'},
 'RESTRAINT':{'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps'},
 'REPRO':{'pregnant','pregnancy','lactation','breastfeeding','birth','insemination','fertilization','fertilisation'},
 'INJURY':{'blood','wound','gore','amputee','amputation','castration','corpse','injury'},
 'EXPOSURE':{'nude','naked','topless','bottomless','panties','underwear','bra','cleavage','underboob','upskirt','downblouse'},
}

def read_csv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def norm(v):return '_'.join(v.strip().lower().replace('_',' ').split())

def root(v):
 v=(v or '').strip();return v.split('/',1)[0] if v else '(none)'

def flags(key):
 parts=set(p for p in key.replace('(','_').replace(')','_').replace('-','_').split('_') if p)
 hit=sorted(n for n,t in LEX_GROUPS.items() if parts&t)
 return '+'.join(hit) if hit else 'NONE'

def rank(seed,key):return hashlib.sha256(f'{seed}|{key}'.encode()).hexdigest()

def main():
 general=read_csv(GENERAL);special=read_csv(SPECIAL);side=read_csv(SIDECAR)
 g={norm(r['canonical']):r for r in general};s={norm(r['Tag']):r for r in special}
 rows=[];clusters=defaultdict(list)
 for r in side:
  if r['review_status']!='UNCLASSIFIED' or r['is_special']!='YES':continue
  k=r['identity_key'];gr=g.get(k);sr=s.get(k)
  mem='OVERLAP' if gr is not None else 'SPECIAL_ONLY'
  fam=(sr or {}).get('GenerationFamily','').strip() or '(none)'
  role=(sr or {}).get('GenerationRole','').strip() or '(none)'
  rt=root((gr or {}).get('primary_path',''))
  fl=flags(k)
  ck='|'.join([mem,rt,fam,fl])
  item={'identity_key':k,'membership':mem,'general_root':rt,'generation_family':fam,'generation_role':role,'lex_flags':fl,'cluster_key':ck}
  rows.append(item);clusters[ck].append(item)
 if len(rows)!=2322: raise SystemExit(f'expected 2322 unclassified Special/overlap rows, got {len(rows)}')
 inv=[]
 for ck,items in clusters.items():
  a=items[0]
  inv.append({'cluster_key':ck,'rows':len(items),'membership':a['membership'],'general_root':a['general_root'],'generation_family':a['generation_family'],'lex_flags':a['lex_flags'],'examples':';'.join(x['identity_key'] for x in sorted(items,key=lambda x:rank(ck,x['identity_key']))[:10])})
 inv.sort(key=lambda x:(-x['rows'],x['cluster_key']))
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/'cluster_inventory_v1.csv').open('w',encoding='utf-8',newline='') as f:
  fields=list(inv[0]);w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(inv)
 # Review only representative rows. Large clusters get 6 discovery + 6 holdout; medium 4+4; small clusters are deferred.
 sample=[];covered=0
 for c in inv:
  n=int(c['rows'])
  if n<8:continue
  per=6 if n>=20 else 4
  items=sorted(clusters[c['cluster_key']],key=lambda x:rank('issue118-cluster-sample-v1',x['identity_key']))
  take=min(per*2,len(items));chosen=items[:take]
  if len(sample)+take>240:continue
  for i,x in enumerate(chosen):
   y=dict(x);y['phase']='DISCOVERY' if i<min(per,len(chosen)) else 'HOLDOUT';y['cluster_size']=str(n);sample.append(y)
  covered+=n
 with (OUT/'cluster_review_sample_v1.csv').open('w',encoding='utf-8',newline='') as f:
  fields=['identity_key','membership','general_root','generation_family','generation_role','lex_flags','cluster_key','cluster_size','phase']
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(sample)
 for old in OUT.glob('review_chunk_*.csv'):old.unlink()
 for i in range(0,len(sample),60):
  with (OUT/f'review_chunk_{i//60+1:03d}.csv').open('w',encoding='utf-8',newline='') as f:
   fields=['identity_key','membership','general_root','generation_family','generation_role','lex_flags','cluster_key','cluster_size','phase']
   w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(sample[i:i+60])
 summary={'issue':118,'mode':'UNCLASSIFIED_SPECIAL_CLUSTER_REVIEW_V1','source_rows':len(rows),'cluster_count':len(inv),'clusters_ge_8':sum(1 for x in inv if int(x['rows'])>=8),'top20_rows':sum(int(x['rows']) for x in inv[:20]),'sample_rows':len(sample),'sampled_cluster_population':covered,'sampled_cluster_count':len(set(x['cluster_key'] for x in sample)),'review_chunks':(len(sample)+59)//60,'top_clusters':inv[:20],'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO'}
 (OUT/'summary_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:summary[k] for k in ['source_rows','cluster_count','clusters_ge_8','sample_rows','sampled_cluster_population','sampled_cluster_count']},sort_keys=True))
 return 0
if __name__=='__main__':raise SystemExit(main())
