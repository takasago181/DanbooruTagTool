#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v24.csv')
REVIEW=Path('docs/issue118/overlap_clothing_exposure_review_v39/review_policy_v39.json')
SOURCE=Path('docs/issue118/overlap_clothing_exposure_review_v39/full_review_candidate_v39.csv')
OUT=Path('docs/issue118/research_sidecar_v25.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v25.json')

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    base=read_csv(BASE);source=read_csv(SOURCE);review=json.loads(REVIEW.read_text(encoding='utf-8'))
    if len(base)!=31752:raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(source)!=83 or review.get('source_rows')!=83 or review.get('reviewed_rows')!=83:raise SystemExit('v39 source count drift')
    expected={'SEXUAL':24,'CONTEXTUAL':48,'NON_SEXUAL':11,'UNCLASSIFIED':0}
    if review.get('decision_counts')!=expected:raise SystemExit(f'v39 decision count drift: {review.get("decision_counts")}')
    source_set={r['identity_key'] for r in source}
    groups={k:set(review.get(k) or []) for k in ('SEXUAL','CONTEXTUAL','NON_SEXUAL','UNCLASSIFIED')}
    if set().union(*groups.values())!=source_set or sum(len(v) for v in groups.values())!=len(source_set):raise SystemExit('v39 review coverage/overlap drift')
    index={r['identity_key']:dict(r) for r in base};promoted=Counter()
    for intent in ('NON_SEXUAL','CONTEXTUAL','SEXUAL'):
        for key in sorted(groups[intent]):
            target=index.get(key)
            if target is None or target['review_status']!='UNCLASSIFIED' or target['sexual_intent']:raise SystemExit(f'v39 key not cleanly UNCLASSIFIED in v24: {key}')
            target['sexual_intent']=intent;target['review_status']='HUMAN_REVIEWED';target['rule_id']=f'HUMAN_{intent}_OVERLAP_CLOTHING_EXPOSURE_V39';target['evidence']='full human review of fixed 83-row overlap clothing-exposure cluster';promoted[intent]+=1
    rows=[index[r['identity_key']] for r in base];status=Counter(r['review_status'] for r in rows);classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':3023,'UNCLASSIFIED':6358}
    expected_classes={'CONTEXTUAL':806,'NON_SEXUAL':23356,'NULL':6358,'SEXUAL':1232}
    if dict(sorted(status.items()))!=expected_status:raise SystemExit(f'status mismatch: {dict(status)}')
    if dict(sorted(classes.items()))!=expected_classes:raise SystemExit(f'class mismatch: {dict(classes)}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys());w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    summary={'issue':118,'mode':'RESEARCH_SIDECAR_V25_OVERLAP_CLOTHING_EXPOSURE_FULL_REVIEW','identity_rows':len(rows),'source_base':str(BASE),'new_promotions':dict(sorted(promoted.items())),'new_total_promotions':sum(promoted.values()),'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),'remaining_unclassified':status['UNCLASSIFIED'],'review_source':str(REVIEW),'review_sha256':sha256(REVIEW),'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
