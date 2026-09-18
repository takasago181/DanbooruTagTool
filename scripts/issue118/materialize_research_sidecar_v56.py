#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v55.csv')
CORRECTION=Path('docs/issue118/general_action_interaction_none_review_v81/review_correction_v81a.json')
CORRECTION_BLOB='75a636345aed8ba5a0171da96ad592d68ec8d688'
OUT=Path('docs/issue118/research_sidecar_v56.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v56.json')

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_blob_sha(path):
    data=path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def main():
    if git_blob_sha(CORRECTION)!=CORRECTION_BLOB:
        raise SystemExit('V81A fixed correction blob SHA drift')
    base=read_csv(BASE)
    correction=json.loads(CORRECTION.read_text(encoding='utf-8'))
    if len(base)!=31752:
        raise SystemExit(f'base drift {len(base)}')
    if correction.get('review_verdicts_generated_by_materializer')!='NO':
        raise SystemExit('V81A provenance drift')
    if correction.get('review_artifacts_are_external_inputs')!='YES':
        raise SystemExit('V81A external input flag drift')
    items=correction.get('corrections') or []
    if len(items)!=1 or items[0].get('identity_key')!='sensory_deprivation':
        raise SystemExit('V81A correction set drift')

    index={r['identity_key']:dict(r) for r in base}
    item=items[0]
    target=index.get(item['identity_key'])
    if target is None:
        raise SystemExit('missing sensory_deprivation')
    if target['review_status']!='HUMAN_REVIEWED':
        raise SystemExit('sensory_deprivation not HUMAN_REVIEWED')
    if target['sexual_intent']!=item['from'] or item['from']!='CONTEXTUAL' or item['to']!='SEXUAL':
        raise SystemExit('V81A source/target class drift')

    target['sexual_intent']='SEXUAL'
    target['rule_id']='HUMAN_SEXUAL_V81A_CORRECTION'
    target['evidence']='manual correction of V81 sensory_deprivation intent classification'

    rows=[index[r['identity_key']] for r in base]
    status=Counter(r['review_status'] for r in rows)
    classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':5680,'UNCLASSIFIED':3701}
    expected_classes={'CONTEXTUAL':1510,'NON_SEXUAL':24832,'NULL':3701,'SEXUAL':1709}
    if dict(sorted(status.items()))!=expected_status:
        raise SystemExit(f'status mismatch {dict(status)}')
    if dict(sorted(classes.items()))!=expected_classes:
        raise SystemExit(f'class mismatch {dict(classes)}')

    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys())
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

    summary={
        'issue':118,
        'mode':'RESEARCH_SIDECAR_V56_V81A_CORRECTION',
        'identity_rows':len(rows),
        'source_base':str(BASE),
        'correction_count':1,
        'corrected_keys':['sensory_deprivation'],
        'review_status_counts':dict(sorted(status.items())),
        'sexual_intent_counts':dict(sorted(classes.items())),
        'remaining_unclassified':status['UNCLASSIFIED'],
        'correction_source':str(CORRECTION),
        'correction_git_blob_sha':CORRECTION_BLOB,
        'correction_sha256':sha256(CORRECTION),
        'review_verdicts_generated_by_materializer':'NO',
        'review_artifacts_are_external_inputs':'YES',
        'production_authority':'NO',
        'main_mutated':'NO',
        'issue117_code_mutated':'NO',
        'catalog_mutated':'NO',
        'user_db_mutated':'NO'
    }
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
