#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v71.csv')
REVIEW=Path('docs/issue118/remaining_small_clusters_review_v105/review_policy_v105.json')
CANDIDATE=Path('docs/issue118/remaining_small_clusters_review_v105/full_review_candidate_v105.csv')
REVIEW_BLOB='33340345385af4b174985893e9f3cf5dad0735b1'
CANDIDATE_BLOB='b0a351189906297fa552638481ad6fe9823e555e'
OUT=Path('docs/issue118/research_sidecar_v72.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v72.json')

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git_blob_sha(path):
    data=path.read_bytes(); return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def main():
    if git_blob_sha(REVIEW)!=REVIEW_BLOB: raise SystemExit('V105 fixed review blob SHA drift')
    if git_blob_sha(CANDIDATE)!=CANDIDATE_BLOB: raise SystemExit('V105 fixed candidate blob SHA drift')
    base=read_csv(BASE); source=read_csv(CANDIDATE); review=json.loads(REVIEW.read_text(encoding='utf-8'))
    if len(base)!=31752 or len(source)!=43 or review.get('source_rows')!=43: raise SystemExit('V105 source/base drift')
    if review.get('review_verdicts_generated_by_materializer')!='NO' or review.get('review_artifacts_are_external_inputs')!='YES': raise SystemExit('V105 provenance drift')
    source_set={r['identity_key'] for r in source}
    groups={'SEXUAL':set(review.get('sexual') or []),'CONTEXTUAL':set(review.get('contextual') or []),'NON_SEXUAL':set(review.get('non_sexual') or [])}
    union=set()
    for intent,keys in groups.items():
        if not keys<=source_set or union & keys: raise SystemExit(f'V105 group drift {intent}')
        union|=keys
    if union!=source_set or review.get('unclassified'): raise SystemExit('V105 coverage drift')
    if {k:len(v) for k,v in groups.items()}!=review['decision_counts']: raise SystemExit('V105 decision count drift')
    index={r['identity_key']:dict(r) for r in base}; promoted=Counter()
    for intent,keys in groups.items():
        for key in sorted(keys):
            t=index.get(key)
            if t is None or t['review_status']!='UNCLASSIFIED' or t['sexual_intent']: raise SystemExit(f'V105 target drift {key}')
            t['sexual_intent']=intent; t['review_status']='HUMAN_REVIEWED'; t['rule_id']=f'HUMAN_{intent}_V105'; t['evidence']='full semantic review of fixed V105 candidate set'; promoted[intent]+=1
    rows=[index[r['identity_key']] for r in base]
    status=Counter(r['review_status'] for r in rows); classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':7140,'UNCLASSIFIED':2241}
    expected_classes={'CONTEXTUAL':1908,'NON_SEXUAL':25595,'NULL':2241,'SEXUAL':2008}
    if dict(sorted(status.items()))!=expected_status: raise SystemExit(f'status mismatch {dict(status)}')
    if dict(sorted(classes.items()))!=expected_classes: raise SystemExit(f'class mismatch {dict(classes)}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys()); w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rows)
    summary={'issue':118,'mode':'RESEARCH_SIDECAR_V72_V105_FULL_REVIEW','identity_rows':len(rows),'source_base':str(BASE),
      'new_promotions':dict(sorted(promoted.items())),'new_total_promotions':sum(promoted.values()),
      'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),
      'remaining_unclassified':status['UNCLASSIFIED'],
      'review_inputs':[{'label':'V105','review_source':str(REVIEW),'review_git_blob_sha':REVIEW_BLOB,'review_sha256':sha256(REVIEW),'candidate_source':str(CANDIDATE),'candidate_git_blob_sha':CANDIDATE_BLOB,'source_rows':43}],
      'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES',
      'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
