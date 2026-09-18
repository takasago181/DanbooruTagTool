#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path
BASE=Path('docs/issue118/research_sidecar_v90.csv')
REVIEW=Path('docs/issue118/general_none_none_review_v124/review_policy_v124.json')
CANDIDATE=Path('docs/issue118/general_none_none_review_v124/full_review_candidate_v124.csv')
REVIEW_BLOB='0549e4a60a1ee947723f11403addf9977f7b521f'
CANDIDATE_BLOB='9d93bf52ffdad19a7cdeebefc283c840aed3b719'
OUT=Path('docs/issue118/research_sidecar_v91.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v91.json')
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha256(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git_blob_sha(p):
    d=p.read_bytes(); return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def main():
    if git_blob_sha(REVIEW)!=REVIEW_BLOB: raise SystemExit('V124 fixed review blob SHA drift')
    if git_blob_sha(CANDIDATE)!=CANDIDATE_BLOB: raise SystemExit('V124 fixed candidate blob SHA drift')
    base=read_csv(BASE); src=read_csv(CANDIDATE); review=json.loads(REVIEW.read_text(encoding='utf-8'))
    if len(base)!=31752 or len(src)!=100 or review.get('source_rows')!=100: raise SystemExit('V124 source/base drift')
    if review.get('review_verdicts_generated_by_materializer')!='NO' or review.get('review_artifacts_are_external_inputs')!='YES': raise SystemExit('V124 provenance drift')
    source={r['identity_key'] for r in src}
    groups={'SEXUAL':set(review.get('sexual') or []),'CONTEXTUAL':set(review.get('contextual') or []),'NON_SEXUAL':set(review.get('non_sexual') or [])}
    union=set()
    for intent,keys in groups.items():
        if not keys<=source or union&keys: raise SystemExit(f'V124 group drift {intent}')
        union|=keys
    if union!=source or review.get('unclassified'): raise SystemExit('V124 coverage drift')
    if {k:len(v) for k,v in groups.items()}!=review['decision_counts']: raise SystemExit('V124 decision count drift')
    idx={r['identity_key']:dict(r) for r in base}; promoted=Counter()
    for intent,keys in groups.items():
        for key in sorted(keys):
            t=idx.get(key)
            if t is None or t['review_status']!='UNCLASSIFIED' or t['sexual_intent']: raise SystemExit(f'V124 target drift {key}')
            t['sexual_intent']=intent; t['review_status']='HUMAN_REVIEWED'; t['rule_id']=f'HUMAN_{intent}_V124'; t['evidence']='full semantic review of fixed V124 candidate set'; promoted[intent]+=1
    rows=[idx[r['identity_key']] for r in base]; status=Counter(r['review_status'] for r in rows); classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    es={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':9038,'UNCLASSIFIED':343}; ec={'CONTEXTUAL':1948,'NON_SEXUAL':27429,'NULL':343,'SEXUAL':2032}
    if dict(sorted(status.items()))!=es: raise SystemExit(f'status mismatch {dict(status)}')
    if dict(sorted(classes.items()))!=ec: raise SystemExit(f'class mismatch {dict(classes)}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0]); w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
    s={'issue':118,'mode':'RESEARCH_SIDECAR_V91_V124_FULL_REVIEW','identity_rows':len(rows),'source_base':str(BASE),'new_promotions':dict(sorted(promoted.items())),'new_total_promotions':sum(promoted.values()),'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),'remaining_unclassified':status['UNCLASSIFIED'],'review_inputs':[{'label':'V124','review_source':str(REVIEW),'review_git_blob_sha':REVIEW_BLOB,'review_sha256':sha256(REVIEW),'candidate_source':str(CANDIDATE),'candidate_git_blob_sha':CANDIDATE_BLOB,'source_rows':100}],'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    SUMMARY.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(s,ensure_ascii=False,sort_keys=True))
if __name__=='__main__':raise SystemExit(main())
