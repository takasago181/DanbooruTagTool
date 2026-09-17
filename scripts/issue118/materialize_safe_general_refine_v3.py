#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, re
from pathlib import Path

SIDECAR=Path('docs/issue118/research_sidecar_v1.csv')
GENERAL=Path('docs/issue64/production_candidate/effective_sidecar.csv')
V2_INV=Path('docs/issue118/safe_general_candidates_v2/candidate_inventory_v2.csv')
V2_SAMPLE=Path('docs/issue118/safe_general_candidates_v2/validation_sample_v2.csv')
OUT=Path('docs/issue118/safe_general_refine_v3')
TARGET={'OBJECT_PROP/DAILY','PERSON_COUNT'}
NEW_RISK={'cage','stripper'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def toks(k):return set(x for x in re.split(r'[_()\-]+',k.lower()) if x)
def rank(k):return hashlib.sha256(f'issue118-safe-general-v3|{k}'.encode()).hexdigest()
def main():
    side=read_csv(SIDECAR); general=read_csv(GENERAL); inv=read_csv(V2_INV); old=read_csv(V2_SAMPLE)
    old_keys={r['identity_key'] for r in old}
    filtered=[]
    for r in inv:
        if r['general_path'] not in TARGET:continue
        if toks(r['identity_key']) & NEW_RISK:continue
        filtered.append(r)
    by={p:sorted([r for r in filtered if r['general_path']==p],key=lambda r:rank(r['identity_key'])) for p in TARGET}
    sample=[]
    for p in sorted(TARGET):
        fresh=[r for r in by[p] if r['identity_key'] not in old_keys][:12]
        if len(fresh)!=12:raise SystemExit(f'need 12 fresh rows for {p}, got {len(fresh)}')
        for r in fresh:
            sample.append({'identity_key':r['identity_key'],'general_path':p,'candidate_class':'NON_SEXUAL','phase':'FRESH_HOLDOUT_V3'})
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'validation_sample_v3.csv').open('w',encoding='utf-8',newline='') as f:
        fields=['identity_key','general_path','candidate_class','phase'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(sample)
    summary={
      'issue':118,'mode':'SAFE_GENERAL_REFINEMENT_V3',
      'new_risk_tokens':sorted(NEW_RISK),
      'target_paths':sorted(TARGET),
      'refined_candidate_counts':{p:len(by[p]) for p in sorted(TARGET)},
      'refined_candidate_rows':sum(len(v) for v in by.values()),
      'fresh_validation_rows':len(sample),
      'v2_sample_overlap':len({r['identity_key'] for r in sample}&old_keys),
      'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO'
    }
    (OUT/'summary_v3.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
