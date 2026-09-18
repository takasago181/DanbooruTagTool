#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v57.csv')
REVIEW=Path('docs/issue118/general_clothing_state_exposure_none_review_v84/review_policy_v84.json')
CANDIDATE=Path('docs/issue118/general_clothing_state_exposure_none_review_v84/full_review_candidate_v84.csv')
REVIEW_BLOB='9a66ece8a6090a6c65f8b8b9836473971cb1f5c8'
CANDIDATE_BLOB='0669da0b5a86c29d9f19ccedf5dfeb4971b1f64f'
OUT=Path('docs/issue118/research_sidecar_v58.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v58.json')

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def git_blob_sha(path):
    data=path.read_bytes(); return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def main():
    if git_blob_sha(REVIEW)!=REVIEW_BLOB: raise SystemExit('V84 fixed review blob SHA drift')
    if git_blob_sha(CANDIDATE)!=CANDIDATE_BLOB: raise SystemExit('V84 fixed candidate blob SHA drift')
    base=read_csv(BASE); source=read_csv(CANDIDATE); review=json.loads(REVIEW.read_text(encoding='utf-8'))
    if len(base)!=31752 or len(source)!=100 or review.get('source_rows')!=100: raise SystemExit('V84 source/base drift')
    if review.get('review_verdicts_generated_by_materializer')!='NO' or review.get('review_artifacts_are_external_inputs')!='YES': raise SystemExit('V84 provenance drift')
    source_set={r['identity_key'] for r in source}
    groups={'SEXUAL':set(review.get('sexual') or []),'CONTEXTUAL':set(review.get('contextual') or []),'NON_SEXUAL':set(review.get('non_sexual') or [])}
    union=set()
    for intent,keys in groups.items():
        if not keys<=source_set or union & keys: raise SystemExit(f'V84 group drift {intent}')
        union|=keys
    if union!=source_set or review.get('unclassified'): raise SystemExit('V84 coverage drift')
    expected_counts={k:len(v) for k,v in groups.items()}
    if expected_counts!=review['decision_counts']: raise SystemExit(f'V84 count drift {expected_counts}')
    index={r['identity_key']:dict(r) for r in base}; promoted=Counter()
    for intent,keys in groups.items():
        for key in sorted(keys):
            t=index.get(key)
            if t is None or t['review_status']!='UNCLASSIFIED' or t['sexual_intent']: raise SystemExit(f'V84 target drift {key}')
            t['sexual_intent']=intent; t['review_status']='HUMAN_REVIEWED'; t['rule_id']=f'HUMAN_{intent}_V84'; t['evidence']='full semantic review of fixed V84 candidate set'; promoted[intent]+=1
    rows=[index[r['identity_key']] for r in base]; status=Counter(r['review_status'] for r in rows); classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    if dict(sorted(status.items()))!={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':5875,'UNCLASSIFIED':3506}: raise SystemExit(f'status mismatch {dict(status)}')
    if dict(sorted(classes.items()))!={'CONTEXTUAL':1548,'NON_SEXUAL':24983,'NULL':3506,'SEXUAL':1715}: raise SystemExit(f'class mismatch {dict(classes)}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys()); w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
    summary={'issue':118,'mode':'RESEARCH_SIDECAR_V58_V84_FULL_REVIEW','identity_rows':len(rows),'source_base':str(BASE),'new_promotions':dict(sorted(promoted.items())),'new_total_promotions':sum(promoted.values()),'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),'remaining_unclassified':status['UNCLASSIFIED'],'review_inputs':[{'label':'V84','review_source':str(REVIEW),'review_git_blob_sha':REVIEW_BLOB,'review_sha256':sha256(REVIEW),'candidate_source':str(CANDIDATE),'candidate_git_blob_sha':CANDIDATE_BLOB,'source_rows':100}],'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(summary,ensure_ascii=False,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
