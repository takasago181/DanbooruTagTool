#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v44.csv')
REVIEW = Path('docs/issue118/general_clothing_everyday_sexualized_review_v70/review_policy_v70.json')
CANDIDATE = Path('docs/issue118/general_clothing_everyday_sexualized_review_v70/full_review_candidate_v70.csv')
REVIEW_BLOB = 'b41e368a4dd981919e09323565e977625902925c'
CANDIDATE_BLOB = 'ec4300c0b8eddc95b7d0619e937b136be379caa5'
OUT = Path('docs/issue118/research_sidecar_v45.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v45.json')

def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_blob_sha(path: Path) -> str:
    data=path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def main()->int:
    if git_blob_sha(REVIEW)!=REVIEW_BLOB:
        raise SystemExit('V70 fixed review blob SHA drift')
    if git_blob_sha(CANDIDATE)!=CANDIDATE_BLOB:
        raise SystemExit('V70 fixed candidate blob SHA drift')
    base=read_csv(BASE)
    source=read_csv(CANDIDATE)
    review=json.loads(REVIEW.read_text(encoding='utf-8'))
    if len(base)!=31752:
        raise SystemExit(f'base drift {len(base)}')
    if len(source)!=100 or review.get('source_rows')!=100:
        raise SystemExit('V70 source count drift')
    if review.get('review_verdicts_generated_by_materializer')!='NO':
        raise SystemExit('V70 provenance drift: generated verdicts')
    if review.get('review_artifacts_are_external_inputs')!='YES':
        raise SystemExit('V70 provenance drift: external input flag')

    source_set={r['identity_key'] for r in source}
    groups={
        'SEXUAL':set(review.get('sexual') or []),
        'CONTEXTUAL':set(review.get('contextual') or []),
        'NON_SEXUAL':set(review.get('non_sexual') or []),
    }
    union=set()
    for intent,keys in groups.items():
        if not keys<=source_set:
            raise SystemExit(f'{intent} outside source')
        if union & keys:
            raise SystemExit('review groups overlap')
        union|=keys
    if union!=source_set:
        raise SystemExit(f'review does not cover fixed source: missing={sorted(source_set-union)}')
    if review.get('unclassified'):
        raise SystemExit('V70 has unexpected unclassified rows')
    expected_counts={intent:len(keys) for intent,keys in groups.items()}
    if expected_counts!=review['decision_counts']:
        raise SystemExit(f'review count drift {expected_counts}')

    index={r['identity_key']:dict(r) for r in base}
    promoted=Counter()
    for intent,keys in groups.items():
        for key in sorted(keys):
            target=index.get(key)
            if target is None or target['review_status']!='UNCLASSIFIED' or target['sexual_intent']:
                raise SystemExit(f'V70 not cleanly unclassified: {key}')
            target['sexual_intent']=intent
            target['review_status']='HUMAN_REVIEWED'
            target['rule_id']=f'HUMAN_{intent}_V70'
            target['evidence']='full semantic review of fixed V70 candidate set'
            promoted[intent]+=1

    rows=[index[r['identity_key']] for r in base]
    status=Counter(r['review_status'] for r in rows)
    classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':4755,'UNCLASSIFIED':4626}
    expected_classes={'CONTEXTUAL':1302,'NON_SEXUAL':24123,'NULL':4626,'SEXUAL':1701}
    if dict(sorted(status.items()))!=expected_status:
        raise SystemExit(f'status mismatch {dict(status)}')
    if dict(sorted(classes.items()))!=expected_classes:
        raise SystemExit(f'class mismatch {dict(classes)}')

    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys())
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n')
        w.writeheader(); w.writerows(rows)

    summary={
        'issue':118,
        'mode':'RESEARCH_SIDECAR_V45_V70_FULL_REVIEW',
        'identity_rows':len(rows),
        'source_base':str(BASE),
        'new_promotions':dict(sorted(promoted.items())),
        'new_total_promotions':sum(promoted.values()),
        'review_status_counts':dict(sorted(status.items())),
        'sexual_intent_counts':dict(sorted(classes.items())),
        'remaining_unclassified':status['UNCLASSIFIED'],
        'review_inputs':[{
            'label':'V70',
            'review_source':str(REVIEW),
            'review_git_blob_sha':REVIEW_BLOB,
            'review_sha256':sha256(REVIEW),
            'candidate_source':str(CANDIDATE),
            'candidate_git_blob_sha':CANDIDATE_BLOB,
            'source_rows':100,
        }],
        'review_verdicts_generated_by_materializer':'NO',
        'review_artifacts_are_external_inputs':'YES',
        'production_authority':'NO',
        'main_mutated':'NO',
        'issue117_code_mutated':'NO',
        'catalog_mutated':'NO',
        'user_db_mutated':'NO',
    }
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
