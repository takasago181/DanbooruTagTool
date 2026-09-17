#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v13.csv')
REVIEW = Path('docs/issue118/misc_general_review_v25/review_policy_v25.json')
OUT = Path('docs/issue118/research_sidecar_v14.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v14.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = read_csv(BASE)
    review = json.loads(REVIEW.read_text(encoding='utf-8'))

    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if review.get('reviewed_rows') != 10:
        raise SystemExit('v25 review row count drift')
    expected_decisions = {'NON_SEXUAL': 5, 'CONTEXTUAL': 4, 'UNCLASSIFIED': 1}
    if review.get('decision_counts') != expected_decisions:
        raise SystemExit(f'v25 decision drift: {review.get("decision_counts")}')

    groups = {
        'NON_SEXUAL': review.get('non_sexual') or [],
        'CONTEXTUAL': review.get('contextual') or [],
    }
    keep = review.get('keep_unclassified') or []
    all_keys = [k for vals in groups.values() for k in vals] + keep
    if len(all_keys) != 10 or len(set(all_keys)) != 10:
        raise SystemExit('v25 review keys count/uniqueness drift')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = Counter()
    for intent, keys in groups.items():
        for key in keys:
            target = index.get(key)
            if target is None:
                raise SystemExit(f'v25 reviewed key missing from sidecar: {key}')
            if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
                raise SystemExit(f'v25 reviewed key not cleanly UNCLASSIFIED in v13: {key}')
            target['sexual_intent'] = intent
            target['review_status'] = 'HUMAN_REVIEWED'
            target['rule_id'] = f'HUMAN_{intent}_MISC_GENERAL_V25'
            target['evidence'] = 'full human review of all v25 candidate and risk-ejected identities; fixed review policy'
            promoted[intent] += 1

    for key in keep:
        target = index.get(key)
        if target is None:
            raise SystemExit(f'v25 keep-unclassified key missing from sidecar: {key}')
        if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
            raise SystemExit(f'v25 keep-unclassified key is no longer cleanly UNCLASSIFIED: {key}')

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 22371,
        'HUMAN_REVIEWED': 1576,
        'UNCLASSIFIED': 7805,
    }
    expected_classes = {
        'CONTEXTUAL': 244,
        'NON_SEXUAL': 22847,
        'NULL': 7805,
        'SEXUAL': 856,
    }
    if dict(sorted(status.items())) != expected_status:
        raise SystemExit(f'status mismatch: {dict(status)}')
    if dict(sorted(classes.items())) != expected_classes:
        raise SystemExit(f'class mismatch: {dict(classes)}')

    with OUT.open('w', encoding='utf-8', newline='') as f:
        fields = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader(); w.writerows(rows)

    summary = {
        'issue': 118,
        'mode': 'RESEARCH_SIDECAR_V14_MISC_GENERAL_V25_FULL_REVIEW',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_promotions': dict(sorted(promoted.items())),
        'new_total_promotions': sum(promoted.values()),
        'kept_unclassified': len(keep),
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'review_source': str(REVIEW),
        'review_sha256': sha256(REVIEW),
        'review_verdicts_generated_by_materializer': 'NO',
        'review_artifacts_are_external_inputs': 'YES',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
