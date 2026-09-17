#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v23.csv')
REVIEW=Path('docs/issue118/body_injury_review_v38/review_policy_v38.json')
SOURCE=Path('docs/issue118/body_injury_review_v38/full_review_candidate_v38.csv')
OUT=Path('docs/issue118/research_sidecar_v24.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v24.json')

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    base=read_csv(BASE);source=read_csv(SOURCE);review=json.loads(REVIEW.read_text(encoding='utf-8'))
    if len(base)!=31752:raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(source)!=58 or review.get('source_rows')!=58:raise SystemExit('v38 source count drift')
    if review.get('decision_counts')!={'SEXUAL':0,'CONTEXTUAL':1,'NON_SEXUAL':57}:raise SystemExit(f'v38 decision count drift: {review.get("decision_counts")}')
    source_set={r['identity_key'] for r in source};contextual=set(review.get('contextual') or [])
    if contextual!={'menstrual_blood'} or not contextual<=source_set:raise SystemExit('v38 contextual drift')
    nonsexual=source_set-contextual
    if len(nonsexual)!=57:raise SystemExit(f'v38 nonsexual derivation drift: {len(nonsexual)}')
    index={r['identity_key']:dict(r) for r in base};promoted=Counter()
    for intent,group in [('NON_SEXUAL',nonsexual),('CONTEXTUAL',contextual)]:
        for key in sorted(group):
            target=index.get(key)
            if target is None or target['review_status']!='UNCLASSIFIED' or target['sexual_intent']:raise SystemExit(f'v38 key not cleanly UNCLASSIFIED in v23: {key}')
            target['sexual_intent']=intent;target['review_status']='HUMAN_REVIEWED';target['rule_id']=f'HUMAN_{intent}_BODY_INJURY_V38';target['evidence']='full human review of fixed 58-row General-only BODY_PART INJURY cluster';promoted[intent]+=1
    rows=[index[r['identity_key']] for r in base];status=Counter(r['review_status'] for r in rows);classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':2940,'UNCLASSIFIED':6441}
    expected_classes={'CONTEXTUAL':758,'NON_SEXUAL':23345,'NULL':6441,'SEXUAL':1208}
    if dict(sorted(status.items()))!=expected_status:raise SystemExit(f'status mismatch: {dict(status)}')
    if dict(sorted(classes.items()))!=expected_classes:raise SystemExit(f'class mismatch: {dict(classes)}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys());w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    summary={'issue':118,'mode':'RESEARCH_SIDECAR_V24_BODY_INJURY_FULL_REVIEW','identity_rows':len(rows),'source_base':str(BASE),'new_promotions':dict(sorted(promoted.items())),'new_total_promotions':sum(promoted.values()),'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),'remaining_unclassified':status['UNCLASSIFIED'],'review_source':str(REVIEW),'review_sha256':sha256(REVIEW),'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
