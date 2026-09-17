#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v26.csv')
V43_REVIEW=Path('docs/issue118/overlap_action_anatomy_review_v43/review_policy_v43.json')
V43_SOURCE=Path('docs/issue118/overlap_action_anatomy_review_v43/full_review_candidate_v43.csv')
V44_REVIEW=Path('docs/issue118/action_object_use_review_v44/review_policy_v44.json')
V44_SOURCE=Path('docs/issue118/action_object_use_review_v44/full_review_candidate_v44.csv')
OUT=Path('docs/issue118/research_sidecar_v27.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v27.json')

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    base=read_csv(BASE); v43s=read_csv(V43_SOURCE); v44s=read_csv(V44_SOURCE)
    v43=json.loads(V43_REVIEW.read_text(encoding='utf-8')); v44=json.loads(V44_REVIEW.read_text(encoding='utf-8'))
    if len(base)!=31752:raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(v43s)!=53 or v43.get('source_rows')!=53:raise SystemExit('v43 source count drift')
    if len(v44s)!=49 or v44.get('source_rows')!=49:raise SystemExit('v44 source count drift')
    if v43.get('decision_counts')!={'SEXUAL':53,'CONTEXTUAL':0,'NON_SEXUAL':0}:raise SystemExit(f'v43 decision count drift: {v43.get("decision_counts")}')
    if v44.get('decision_counts')!={'SEXUAL':1,'CONTEXTUAL':6,'NON_SEXUAL':42}:raise SystemExit(f'v44 decision count drift: {v44.get("decision_counts")}')
    v43set={r['identity_key'] for r in v43s}; v44set={r['identity_key'] for r in v44s}
    if v43set & v44set:raise SystemExit('v43/v44 overlap')
    v44sexual=set(v44.get('sexual') or []); v44context=set(v44.get('contextual') or [])
    if not v44sexual<=v44set or not v44context<=v44set or v44sexual&v44context:raise SystemExit('v44 policy membership drift')
    v44non=v44set-v44sexual-v44context
    if len(v44non)!=42:raise SystemExit(f'v44 nonsexual derivation drift: {len(v44non)}')
    index={r['identity_key']:dict(r) for r in base}; promoted=Counter()
    groups=[('SEXUAL',v43set),('SEXUAL',v44sexual),('CONTEXTUAL',v44context),('NON_SEXUAL',v44non)]
    for intent,group in groups:
        for key in sorted(group):
            target=index.get(key)
            if target is None or target['review_status']!='UNCLASSIFIED' or target['sexual_intent']:raise SystemExit(f'key not cleanly UNCLASSIFIED in v26: {key}')
            target['sexual_intent']=intent;target['review_status']='HUMAN_REVIEWED';target['rule_id']=f'HUMAN_{intent}_V43_V44';target['evidence']='full human review of fixed v43/v44 candidate set';promoted[intent]+=1
    rows=[index[r['identity_key']] for r in base];status=Counter(r['review_status'] for r in rows);classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':3244,'UNCLASSIFIED':6137}
    expected_classes={'CONTEXTUAL':881,'NON_SEXUAL':23398,'NULL':6137,'SEXUAL':1336}
    if dict(sorted(status.items()))!=expected_status:raise SystemExit(f'status mismatch: {dict(status)}')
    if dict(sorted(classes.items()))!=expected_classes:raise SystemExit(f'class mismatch: {dict(classes)}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys());w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    summary={'issue':118,'mode':'RESEARCH_SIDECAR_V27_V43_V44_FULL_REVIEWS','identity_rows':len(rows),'source_base':str(BASE),'new_promotions':dict(sorted(promoted.items())),'new_total_promotions':sum(promoted.values()),'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),'remaining_unclassified':status['UNCLASSIFIED'],'review_inputs':[{'label':'V43','review_source':str(V43_REVIEW),'review_sha256':sha256(V43_REVIEW),'source_rows':53},{'label':'V44','review_source':str(V44_REVIEW),'review_sha256':sha256(V44_REVIEW),'source_rows':49}],'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,sort_keys=True));return 0

if __name__=='__main__':raise SystemExit(main())
