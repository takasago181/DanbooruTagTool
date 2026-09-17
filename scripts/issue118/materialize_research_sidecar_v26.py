#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v25.csv')
OUT=Path('docs/issue118/research_sidecar_v26.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v26.json')
INPUTS=[
    ('V40',Path('docs/issue118/overlap_clothing_exposure_intimate_review_v40/review_policy_v40.json'),Path('docs/issue118/overlap_clothing_exposure_intimate_review_v40/full_review_candidate_v40.csv'),66,{'SEXUAL':47,'CONTEXTUAL':19,'NON_SEXUAL':0,'UNCLASSIFIED':0}),
    ('V41',Path('docs/issue118/overlap_body_attribute_anatomy_review_v41/review_policy_v41.json'),Path('docs/issue118/overlap_body_attribute_anatomy_review_v41/full_review_candidate_v41.csv'),53,{'SEXUAL':3,'CONTEXTUAL':50,'NON_SEXUAL':0,'UNCLASSIFIED':0}),
]

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    base=read_csv(BASE)
    if len(base)!=31752:raise SystemExit(f'base sidecar drift: {len(base)}')
    index={r['identity_key']:dict(r) for r in base};promoted=Counter();review_inputs=[]
    seen=set()
    for label,review_path,source_path,count,expected in INPUTS:
        source=read_csv(source_path);review=json.loads(review_path.read_text(encoding='utf-8'))
        if len(source)!=count or review.get('source_rows')!=count or review.get('reviewed_rows')!=count:raise SystemExit(f'{label} source count drift')
        if review.get('decision_counts')!=expected:raise SystemExit(f'{label} decision count drift: {review.get("decision_counts")}')
        source_set={r['identity_key'] for r in source}
        groups={k:set(review.get(k) or []) for k in ('SEXUAL','CONTEXTUAL','NON_SEXUAL','UNCLASSIFIED')}
        if set().union(*groups.values())!=source_set or sum(len(v) for v in groups.values())!=len(source_set):raise SystemExit(f'{label} coverage/overlap drift')
        if seen & source_set:raise SystemExit(f'{label} overlaps prior review input')
        seen|=source_set
        for intent in ('NON_SEXUAL','CONTEXTUAL','SEXUAL'):
            for key in sorted(groups[intent]):
                target=index.get(key)
                if target is None or target['review_status']!='UNCLASSIFIED' or target['sexual_intent']:raise SystemExit(f'{label} key not cleanly UNCLASSIFIED in v25: {key}')
                target['sexual_intent']=intent;target['review_status']='HUMAN_REVIEWED';target['rule_id']=f'HUMAN_{intent}_{label}';target['evidence']=f'full human review from {label} fixed candidate set';promoted[intent]+=1
        review_inputs.append({'label':label,'review_source':str(review_path),'review_sha256':sha256(review_path),'source_rows':count})
    rows=[index[r['identity_key']] for r in base];status=Counter(r['review_status'] for r in rows);classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':3142,'UNCLASSIFIED':6239}
    expected_classes={'CONTEXTUAL':875,'NON_SEXUAL':23356,'NULL':6239,'SEXUAL':1282}
    if dict(sorted(status.items()))!=expected_status:raise SystemExit(f'status mismatch: {dict(status)}')
    if dict(sorted(classes.items()))!=expected_classes:raise SystemExit(f'class mismatch: {dict(classes)}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys());w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    summary={'issue':118,'mode':'RESEARCH_SIDECAR_V26_V40_V41_FULL_REVIEWS','identity_rows':len(rows),'source_base':str(BASE),'new_promotions':dict(sorted(promoted.items())),'new_total_promotions':sum(promoted.values()),'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),'remaining_unclassified':status['UNCLASSIFIED'],'review_inputs':review_inputs,'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
