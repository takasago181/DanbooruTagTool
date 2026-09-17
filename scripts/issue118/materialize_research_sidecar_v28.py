#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v27.csv')
INPUTS=[
    ('V45',Path('docs/issue118/overlap_action_interaction_none_review_v45/review_policy_v45.json'),Path('docs/issue118/overlap_action_interaction_none_review_v45/full_review_candidate_v45.csv'),45),
    ('V46',Path('docs/issue118/clothing_exposure_intimate_general_review_v46/review_policy_v46.json'),Path('docs/issue118/clothing_exposure_intimate_general_review_v46/full_review_candidate_v46.csv'),38),
    ('V47',Path('docs/issue118/special_explicit_sex_review_v47/review_policy_v47.json'),Path('docs/issue118/special_explicit_sex_review_v47/full_review_candidate_v47.csv'),37),
]
OUT=Path('docs/issue118/research_sidecar_v28.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v28.json')

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def policy_groups(review, source_set):
    counts=review['decision_counts']
    sexual=set(review.get('sexual') or [])
    contextual=set(review.get('contextual') or [])
    nonsexual=set(review.get('non_sexual') or [])
    if counts['SEXUAL']==len(source_set) and not sexual and not contextual and not nonsexual:
        sexual=set(source_set)
    else:
        if not nonsexual:
            nonsexual=source_set-sexual-contextual
    if sexual&contextual or sexual&nonsexual or contextual&nonsexual:raise SystemExit('policy groups overlap')
    if sexual|contextual|nonsexual != source_set:raise SystemExit('policy groups do not cover source')
    if {'SEXUAL':len(sexual),'CONTEXTUAL':len(contextual),'NON_SEXUAL':len(nonsexual)}!=counts:raise SystemExit(f'policy count drift: {counts}')
    return sexual,contextual,nonsexual

def main():
    base=read_csv(BASE)
    if len(base)!=31752:raise SystemExit(f'base sidecar drift: {len(base)}')
    index={r['identity_key']:dict(r) for r in base};promoted=Counter();review_inputs=[];seen=set()
    for label,review_path,source_path,expected_rows in INPUTS:
        source=read_csv(source_path);review=json.loads(review_path.read_text(encoding='utf-8'))
        if len(source)!=expected_rows or review.get('source_rows')!=expected_rows:raise SystemExit(f'{label} source count drift')
        source_set={r['identity_key'] for r in source}
        if seen&source_set:raise SystemExit(f'{label} overlaps earlier review input')
        seen|=source_set
        sexual,contextual,nonsexual=policy_groups(review,source_set)
        for intent,group in [('SEXUAL',sexual),('CONTEXTUAL',contextual),('NON_SEXUAL',nonsexual)]:
            for key in sorted(group):
                target=index.get(key)
                if target is None or target['review_status']!='UNCLASSIFIED' or target['sexual_intent']:raise SystemExit(f'{label} key not cleanly UNCLASSIFIED in v27: {key}')
                target['sexual_intent']=intent;target['review_status']='HUMAN_REVIEWED';target['rule_id']=f'HUMAN_{intent}_{label}';target['evidence']=f'full human review of fixed {label} candidate set';promoted[intent]+=1
        review_inputs.append({'label':label,'review_source':str(review_path),'review_sha256':sha256(review_path),'source_rows':expected_rows})
    rows=[index[r['identity_key']] for r in base];status=Counter(r['review_status'] for r in rows);classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':3364,'UNCLASSIFIED':6017}
    expected_classes={'CONTEXTUAL':901,'NON_SEXUAL':23408,'NULL':6017,'SEXUAL':1426}
    if dict(sorted(status.items()))!=expected_status:raise SystemExit(f'status mismatch: {dict(status)}')
    if dict(sorted(classes.items()))!=expected_classes:raise SystemExit(f'class mismatch: {dict(classes)}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys());w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    summary={'issue':118,'mode':'RESEARCH_SIDECAR_V28_V45_V46_V47_FULL_REVIEWS','identity_rows':len(rows),'source_base':str(BASE),'new_promotions':dict(sorted(promoted.items())),'new_total_promotions':sum(promoted.values()),'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),'remaining_unclassified':status['UNCLASSIFIED'],'review_inputs':review_inputs,'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,sort_keys=True));return 0

if __name__=='__main__':raise SystemExit(main())
