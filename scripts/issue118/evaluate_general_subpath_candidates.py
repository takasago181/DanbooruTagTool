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
SAFE_ROOTS={'COMPOSITION_CAMERA','HAIR_FACE','LIGHT_TIME_WEATHER','LIVING_NATURE','PLACE_BACKGROUND','TEXT_SYMBOL'}


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
        p=by['PILOT']; h=by['HOLDOUT']
        ps=sum(p.values()); hs=sum(h.values())
        if ps<4: continue
        if set(k for k,v in p.items() if v)!={'NON_SEXUAL'}: continue
        # Existing holdout may be sparse, but any contradiction vetoes the path.
        if any(h.get(c,0) for c in ('SEXUAL','CONTEXTUAL')): continue
        root=path.split('/',1)[0]
        # Already-covered safe roots do not add useful coverage.
        if root in SAFE_ROOTS: continue
        accepted.append({'primary_path':path,'pilot_support':ps,'holdout_support':hs,'training_nonsexual_support':ps+hs})
    accepted.sort(key=lambda r:(-r['training_nonsexual_support'],r['primary_path']))

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
        # Fresh holdout: 10 deterministic spread examples from previously unclassified rows.
        if len(rows)<=10:
            sample=rows
        else:
            idxs=sorted({0,1,2,3,4,len(rows)//2,max(0,len(rows)-4),max(0,len(rows)-3),max(0,len(rows)-2),len(rows)-1})
            sample=[rows[i] for i in idxs]
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
    summary={'issue':118,'mode':'GENERAL_SUBPATH_CANDIDATE_V2_FRESH_HOLDOUT','accepted_training_paths':len(accepted),
             'candidate_rows':len(candidates),'validation_rows':len(validation),
             'candidate_rows_by_path':{k:len(v) for k,v in sorted(bypath.items())},
             'safety':'pilot-pure candidate only; any prior contradiction vetoes; fresh unclassified holdout required before promotion',
             'production_promotion_performed':'NO'}
    (OUT/'summary_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
