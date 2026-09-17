#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from collections import defaultdict
from pathlib import Path
GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR=Path('docs/issue118/research_sidecar_v1.csv')
OUT=Path('docs/issue118/general_cluster_review_v1')
LEX_GROUPS={
 'EXPLICIT_SEX':{'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm','masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia','rape','cunnilingus','anilingus','fingering','footjob','creampie','bukkake'},
 'ANATOMY':{'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples','breast','breasts','areola','areolae','pubic'},
 'RESTRAINT':{'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps','bound'},
 'REPRO':{'pregnant','pregnancy','lactation','breastfeeding','birth','insemination','fertilization','fertilisation','impregnation'},
 'INJURY':{'blood','wound','gore','amputee','amputation','castration','corpse','injury','torture'},
 'EXPOSURE':{'nude','naked','topless','bottomless','panties','underwear','bra','cleavage','underboob','upskirt','downblouse','crotchless'},
}
def read_csv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return '_'.join(v.strip().lower().replace('_',' ').split())
def flags(key):
 parts=set(p for p in key.replace('(','_').replace(')','_').replace('-','_').split('_') if p)
 hit=sorted(n for n,t in LEX_GROUPS.items() if parts&t)
 return '+'.join(hit) if hit else 'NONE'
def rank(seed,key):return hashlib.sha256(f'{seed}|{key}'.encode()).hexdigest()
def main():
 general=read_csv(GENERAL);side=read_csv(SIDECAR);g={norm(r['canonical']):r for r in general}
 rows=[];clusters=defaultdict(list)
 for r in side:
  if r['review_status']!='UNCLASSIFIED' or r['is_general']!='YES' or r['is_special']=='YES':continue
  k=r['identity_key'];gr=g[k];path=(gr.get('primary_path') or '').strip() or '(none)';fl=flags(k);ck=f'{path}|{fl}'
  item={'identity_key':k,'general_path':path,'general_confidence':(gr.get('confidence') or '').strip(),'lex_flags':fl,'cluster_key':ck}
  rows.append(item);clusters[ck].append(item)
 if len(rows)!=23717:raise SystemExit(f'expected 23717 General-only unclassified rows, got {len(rows)}')
 inv=[]
 for ck,items in clusters.items():
  a=items[0];inv.append({'cluster_key':ck,'rows':len(items),'general_path':a['general_path'],'lex_flags':a['lex_flags'],'examples':';'.join(x['identity_key'] for x in sorted(items,key=lambda x:rank(ck,x['identity_key']))[:10])})
 inv.sort(key=lambda x:(-x['rows'],x['cluster_key']))
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/'cluster_inventory_v1.csv').open('w',encoding='utf-8',newline='') as f:
  fields=list(inv[0]);w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(inv)
 sample=[];covered=0
 for c in inv:
  n=int(c['rows'])
  if n<20:continue
  per=6
  items=sorted(clusters[c['cluster_key']],key=lambda x:rank('issue118-general-cluster-v1',x['identity_key']))
  chosen=items[:12]
  if len(sample)+len(chosen)>240:continue
  for i,x in enumerate(chosen):
   y=dict(x);y['phase']='DISCOVERY' if i<per else 'HOLDOUT';y['cluster_size']=str(n);sample.append(y)
  covered+=n
 with (OUT/'cluster_review_sample_v1.csv').open('w',encoding='utf-8',newline='') as f:
  fields=['identity_key','general_path','general_confidence','lex_flags','cluster_key','cluster_size','phase'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(sample)
 for old in OUT.glob('review_chunk_*.csv'):old.unlink()
 for i in range(0,len(sample),60):
  with (OUT/f'review_chunk_{i//60+1:03d}.csv').open('w',encoding='utf-8',newline='') as f:
   fields=['identity_key','general_path','general_confidence','lex_flags','cluster_key','cluster_size','phase'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(sample[i:i+60])
 summary={'issue':118,'mode':'UNCLASSIFIED_GENERAL_CLUSTER_REVIEW_V1','source_rows':len(rows),'cluster_count':len(inv),'clusters_ge_20':sum(1 for x in inv if int(x['rows'])>=20),'top20_rows':sum(int(x['rows']) for x in inv[:20]),'sample_rows':len(sample),'sampled_cluster_population':covered,'sampled_cluster_count':len(set(x['cluster_key'] for x in sample)),'review_chunks':(len(sample)+59)//60,'top_clusters':inv[:20],'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO'}
 (OUT/'summary_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:summary[k] for k in ['source_rows','cluster_count','clusters_ge_20','sample_rows','sampled_cluster_population','sampled_cluster_count']},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
