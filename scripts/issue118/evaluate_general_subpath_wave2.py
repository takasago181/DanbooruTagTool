#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR=Path('docs/issue118/research_sidecar_v2.csv')
PILOT=Path('docs/issue118/reviews'); HOLDOUT=Path('docs/issue118/holdout/reviews')
OUT=Path('docs/issue118/general_subpath_wave2')
VALID={'SEXUAL','NON_SEXUAL','CONTEXTUAL'}
ALREADY={'CLOTHING/UNIFORM','OBJECT_PROP/VEHICLE','PERSON_COUNT'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return '_'.join(v.strip().lower().replace('_',' ').split())
def reviews():
    out=[]
    for cohort,d,pat in [('PILOT',PILOT,'chunk_???_review_v1.csv'),('HOLDOUT',HOLDOUT,'chunk_*_review_v1.csv')]:
        for p in sorted(d.glob(pat)):
            for r in read_csv(p):
                st=(r.get('pilot_review_status') or r.get('review_status') or '').strip(); cl=(r.get('reviewed_class') or '').strip()
                if st=='REVIEWED' and cl in VALID:out.append((norm(r['identity_key']),cl,cohort))
    return out

def main():
    g={norm(r['canonical']):r for r in read_csv(GENERAL)}; side={r['identity_key']:r for r in read_csv(SIDECAR)}
    ev=defaultdict(lambda:{'PILOT':Counter(),'HOLDOUT':Counter()})
    for key,cl,co in reviews():
        gr=g.get(key); path=(gr or {}).get('primary_path','').strip()
        if path:ev[path][co][cl]+=1
    un_by=defaultdict(list)
    for key,sr in side.items():
        if sr['review_status']!='UNCLASSIFIED' or sr['is_general']!='YES' or sr['is_special']!='NO':continue
        gr=g.get(key); path=(gr or {}).get('primary_path','').strip()
        if path and path not in ALREADY:un_by[path].append({'identity_key':key,'primary_path':path,'general_status':gr.get('classification_status',''),'general_confidence':gr.get('confidence','')})
    paths=[]; validation=[]
    for path,rows in un_by.items():
        if len(rows)<100:continue
        p=ev[path]['PILOT']; h=ev[path]['HOLDOUT']; total=p+h
        # At least two historical NON_SEXUAL examples; zero known SEXUAL/CONTEXTUAL counterexamples.
        if total['NON_SEXUAL']<2 or total['SEXUAL'] or total['CONTEXTUAL']:continue
        rows=sorted(rows,key=lambda r:r['identity_key'])
        n=len(rows); idxs=sorted(set([0,1,2,3,n//5,2*n//5,n//2,3*n//5,4*n//5,max(0,n-3),max(0,n-2),n-1]))
        sample=[rows[i] for i in idxs]
        paths.append({'primary_path':path,'candidate_rows':n,'historical_nonsexual_support':total['NON_SEXUAL'],'fresh_holdout_rows':len(sample)})
        for r in sample:validation.append({**r,'path_candidate_rows':str(n),'historical_nonsexual_support':str(total['NON_SEXUAL']),'reviewed_class':'','review_status_check':'','review_note':''})
    paths.sort(key=lambda r:(-r['candidate_rows'],r['primary_path']))
    # only top 8 paths this wave to bound human review
    allowed={r['primary_path'] for r in paths[:8]}; paths=[r for r in paths if r['primary_path'] in allowed]; validation=[r for r in validation if r['primary_path'] in allowed]
    OUT.mkdir(parents=True,exist_ok=True)
    def write(p,rows):
        if not rows:p.write_text('',encoding='utf-8');return
        with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    write(OUT/'candidate_paths.csv',paths);write(OUT/'validation_sample.csv',validation)
    s={'issue':118,'mode':'GENERAL_SUBPATH_WAVE2_HIGH_LEVERAGE','candidate_paths':len(paths),'candidate_rows_total':sum(r['candidate_rows'] for r in paths),'validation_rows':len(validation),'paths':paths,'production_promotion_performed':'NO'}
    (OUT/'summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
