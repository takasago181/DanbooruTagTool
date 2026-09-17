#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v1.csv')
V2_INV=Path('docs/issue118/safe_general_candidates_v2/candidate_inventory_v2.csv')
V2_SAMPLE=Path('docs/issue118/safe_general_candidates_v2/validation_sample_v2.csv')
V3_SAMPLE=Path('docs/issue118/safe_general_refine_v3/validation_sample_v3.csv')
OUT=Path('docs/issue118/research_sidecar_v2.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v2.json')
V2_REVIEW=Path('docs/issue118/safe_general_candidates_v2/validation_review_v2.csv')
V3_REVIEW=Path('docs/issue118/safe_general_refine_v3/validation_review_v3.csv')
REFINED_PATHS={'OBJECT_PROP/DAILY','PERSON_COUNT'}
NEW_RISK={'cage','stripper'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def toks(k):return set(x for x in re.split(r'[_()\-]+',k.lower()) if x)
def write_review(path, rows, exceptions):
    out=[]
    for r in rows:
        key=r['identity_key'];cls=exceptions.get(key,'NON_SEXUAL')
        reason='manual semantic validation accepted NON_SEXUAL candidate'
        if key=='stripper':reason='erotic/sexualized performer role; concept itself is sexual-context discovery'
        elif key=='head_cage':reason='restraint-device concept has substantial ordinary/restraint and sexual/BDSM discovery use'
        out.append({'identity_key':key,'reviewed_class':cls,'review_status':'REVIEWED','review_reason':reason})
    with path.open('w',encoding='utf-8',newline='') as f:
        fields=['identity_key','reviewed_class','review_status','review_reason'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(out)
    return out

def main():
    base=read_csv(BASE); inv=read_csv(V2_INV); v2=read_csv(V2_SAMPLE); v3=read_csv(V3_SAMPLE)
    if len(base)!=31752 or len(inv)!=10258 or len(v2)!=120 or len(v3)!=24:raise SystemExit('input drift')
    exceptions={'stripper':'SEXUAL','head_cage':'CONTEXTUAL'}
    v2r=write_review(V2_REVIEW,v2,exceptions);v3r=write_review(V3_REVIEW,v3,{})
    manual={r['identity_key']:r['reviewed_class'] for r in v2r+v3r}
    if len(manual)!=144:raise SystemExit('manual validation identity overlap')
    safe=set()
    for r in inv:
        key=r['identity_key'];path=r['general_path']
        if path in REFINED_PATHS and toks(key)&NEW_RISK:continue
        safe.add(key)
    if len(safe)!=10252:raise SystemExit(f'expected 10252 safe candidates, got {len(safe)}')
    index={r['identity_key']:dict(r) for r in base}
    for key,cls in manual.items():
        row=index[key]
        if row['review_status']!='UNCLASSIFIED':raise SystemExit(f'manual row not unclassified in v1: {key}')
        row['sexual_intent']=cls;row['review_status']='HUMAN_REVIEWED';row['rule_id']='';row['evidence']='SAFE_GENERAL_VALIDATION_V2_V3'
    for key in safe:
        row=index[key]
        if row['review_status']=='HUMAN_REVIEWED':continue
        if row['review_status']!='UNCLASSIFIED':raise SystemExit(f'auto row not unclassified in v1: {key}')
        row['sexual_intent']='NON_SEXUAL';row['review_status']='AUTO_HIGH_CONF';row['rule_id']='AUTO_NONSEX_LEARNED_RISK_EXCLUSION_V3';row['evidence']='924_REVIEW_EVIDENCE+V2_118_120+V3_24_24; risk exclusions cage/stripper'
    rows=[index[r['identity_key']] for r in base]
    status=Counter(r['review_status'] for r in rows);classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0]);w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    summary={
      'issue':118,'mode':'RESEARCH_SIDECAR_V2', 'identity_rows':len(rows),
      'new_safe_general_candidates':len(safe), 'new_manual_validation_rows':len(manual),
      'review_status_counts':dict(sorted(status.items())), 'sexual_intent_counts':dict(sorted(classes.items())),
      'remaining_unclassified':status['UNCLASSIFIED'],
      'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'
    }
    expected_status={'AUTO_HIGH_CONF':14894,'HUMAN_REVIEWED':1068,'UNCLASSIFIED':15790}
    expected_classes={'CONTEXTUAL':190,'NON_SEXUAL':15187,'NULL':15790,'SEXUAL':585}
    if dict(sorted(status.items()))!=expected_status:raise SystemExit(f'status mismatch {status}')
    if dict(sorted(classes.items()))!=expected_classes:raise SystemExit(f'class mismatch {classes}')
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
