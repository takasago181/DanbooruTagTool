#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR=Path('docs/issue118/research_sidecar_v1.csv')
PILOT=Path('docs/issue118/reviews')
HOLDOUT=Path('docs/issue118/holdout/reviews')
OUT=Path('docs/issue118/general_subpath_candidates_v1')
VALID={'SEXUAL','NON_SEXUAL','CONTEXTUAL'}


def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def norm(v): return '_'.join(v.strip().lower().replace('_',' ').split())

def load_reviews():
    out=[]
    for cohort,directory,pattern in [('PILOT',PILOT,'chunk_???_review_v1.csv'),('HOLDOUT',HOLDOUT,'chunk_*_review_v1.csv')]:
        for p in sorted(directory.glob(pattern)):
            for r in read_csv(p):
                st=(r.get('pilot_review_status') or r.get('review_status') or '').strip()
                cls=(r.get('reviewed_class') or '').strip()
                if st=='REVIEWED' and cls in VALID: out.append((norm(r['identity_key']),cls,cohort))
    return out


def main():
    g={norm(r['canonical']):r for r in read_csv(GENERAL)}
    side={r['identity_key']:r for r in read_csv(SIDECAR)}
    ev=defaultdict(lambda:{'PILOT':Counter(),'HOLDOUT':Counter()})
    for key,cls,cohort in load_reviews():
        gr=g.get(key)
        if not gr: continue
        path=gr.get('primary_path','').strip()
        if path: ev[path][cohort][cls]+=1

    accepted=[]
    for path,by in ev.items():
        p=by['PILOT']; h=by['HOLDOUT']; total=p+h
        if sum(p.values())<4 or sum(h.values())<4: continue
        if set(k for k,v in total.items() if v)!={'NON_SEXUAL'}: continue
        accepted.append({'primary_path':path,'pilot_support':sum(p.values()),'holdout_support':sum(h.values()),'total_support':sum(total.values())})
    accepted.sort(key=lambda r:(-r['total_support'],r['primary_path']))

    candidates=[]
    bypath=defaultdict(list)
    allowed={r['primary_path'] for r in accepted}
    for key,sr in side.items():
        if sr['review_status']!='UNCLASSIFIED' or sr['is_general']!='YES' or sr['is_special']!='NO': continue
        gr=g.get(key)
        path=(gr or {}).get('primary_path','').strip()
        if path in allowed:
            row={'identity_key':key,'primary_path':path,'general_status':gr.get('classification_status',''),'general_confidence':gr.get('confidence','')}
            candidates.append(row); bypath[path].append(row)

    validation=[]
    for path in sorted(bypath):
        rows=sorted(bypath[path],key=lambda r:r['identity_key'])
        # up to 10 spread samples: first 5 + last 5.
        sample=rows if len(rows)<=10 else rows[:5]+rows[-5:]
        for r in sample:
            validation.append({**r,'path_candidate_rows':str(len(rows)),'reviewed_class':'','review_status_check':'','review_note':''})

    OUT.mkdir(parents=True,exist_ok=True)
    def write(path,rows):
        if not rows:path.write_text('',encoding='utf-8');return
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    write(OUT/'accepted_training_paths.csv',accepted)
    write(OUT/'candidate_rows.csv',candidates)
    write(OUT/'validation_sample_v1.csv',validation)
    summary={'issue':118,'mode':'GENERAL_SUBPATH_CANDIDATE_V1','accepted_training_paths':len(accepted),
             'candidate_rows':len(candidates),'validation_rows':len(validation),
             'candidate_rows_by_path':{k:len(v) for k,v in sorted(bypath.items())},
             'safety':'candidate only; no production or sidecar promotion until new validation review',
             'production_promotion_performed':'NO'}
    (OUT/'summary_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
