#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v22.csv')
REVIEW = Path('docs/issue118/special_none_review_v37/review_policy_v37.json')
SOURCE = Path('docs/issue118/special_none_review_v37/full_review_candidate_v37.csv')
OUT = Path('docs/issue118/research_sidecar_v23.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v23.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = read_csv(BASE)
    source = read_csv(SOURCE)
    review = json.loads(REVIEW.read_text(encoding='utf-8'))
    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(source) != 257 or review.get('source_rows') != 257:
        raise SystemExit('v37 source count drift')
    expected_counts = {'SEXUAL':69,'CONTEXTUAL':105,'NON_SEXUAL':66,'UNCLASSIFIED':17}
    if review.get('decision_counts') != expected_counts:
        raise SystemExit(f'v37 decision count drift: {review.get("decision_counts")}')

    source_set = {r['identity_key'] for r in source}
    sexual = set(review.get('sexual') or [])
    nonsexual = set(review.get('non_sexual') or [])
    unclassified = set(review.get('unclassified') or [])
    if len(sexual) != 69 or len(nonsexual) != 66 or len(unclassified) != 17:
        raise SystemExit('v37 explicit list count drift')
    if (sexual | nonsexual | unclassified) - source_set:
        raise SystemExit('v37 review lists include unknown key')
    if (sexual & nonsexual) or (sexual & unclassified) or (nonsexual & unclassified):
        raise SystemExit('v37 review list overlap')
    contextual = source_set - sexual - nonsexual - unclassified
    if len(contextual) != 105:
        raise SystemExit(f'v37 contextual derivation drift: {len(contextual)}')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')
    promoted = Counter()
    for intent, group in [('SEXUAL',sexual),('CONTEXTUAL',contextual),('NON_SEXUAL',nonsexual)]:
        for key in sorted(group):
            target = index.get(key)
            if target is None:
                raise SystemExit(f'v37 key missing from sidecar: {key}')
            if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
                raise SystemExit(f'v37 key not cleanly UNCLASSIFIED in v22: {key}')
            target['sexual_intent'] = intent
            target['review_status'] = 'HUMAN_REVIEWED'
            target['rule_id'] = f'HUMAN_{intent}_SPECIAL_NONE_V37'
            target['evidence'] = 'full human review of fixed 257-row Special-only family-none lex-NONE source; ambiguous 17 rows retained UNCLASSIFIED'
            promoted[intent] += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status = {'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':2882,'UNCLASSIFIED':6499}
    expected_classes = {'CONTEXTUAL':757,'NON_SEXUAL':23288,'NULL':6499,'SEXUAL':1208}
    if dict(sorted(status.items())) != expected_status:
        raise SystemExit(f'status mismatch: {dict(status)}')
    if dict(sorted(classes.items())) != expected_classes:
        raise SystemExit(f'class mismatch: {dict(classes)}')

    with OUT.open('w', encoding='utf-8', newline='') as f:
        fields = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader(); w.writerows(rows)

    summary = {
        'issue':118,
        'mode':'RESEARCH_SIDECAR_V23_SPECIAL_NONE_FULL_REVIEW',
        'identity_rows':len(rows),
        'source_base':str(BASE),
        'new_promotions':dict(sorted(promoted.items())),
        'new_total_promotions':sum(promoted.values()),
        'kept_unclassified':len(unclassified),
        'review_status_counts':dict(sorted(status.items())),
        'sexual_intent_counts':dict(sorted(classes.items())),
        'remaining_unclassified':status['UNCLASSIFIED'],
        'review_source':str(REVIEW),
        'review_sha256':sha256(REVIEW),
        'review_verdicts_generated_by_materializer':'NO',
        'review_artifacts_are_external_inputs':'YES',
        'production_authority':'NO',
        'main_mutated':'NO',
        'issue117_code_mutated':'NO',
        'catalog_mutated':'NO',
        'user_db_mutated':'NO'
    }
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True)); return 0


if __name__=='__main__':
    raise SystemExit(main())
