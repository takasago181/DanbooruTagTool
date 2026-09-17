#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v15.csv')
REVIEW = Path('docs/issue118/clothing_accessory_review_v27/review_policy_v27.json')
SOURCE = Path('docs/issue118/clothing_accessory_review_v27/full_review_candidate_v27.csv')
OUT = Path('docs/issue118/research_sidecar_v16.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v16.json')


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
    if len(source) != 178 or review.get('source_rows') != 178:
        raise SystemExit('v27 source count drift')
    if review.get('decision_counts') != {'NON_SEXUAL': 141, 'CONTEXTUAL': 37}:
        raise SystemExit('v27 decision count drift')

    keys = [r['identity_key'] for r in source]
    if len(keys) != len(set(keys)):
        raise SystemExit('duplicate identity in v27 source')
    source_set = set(keys)
    contextual = review.get('contextual') or []
    contextual_set = set(contextual)
    if len(contextual) != 37 or len(contextual_set) != 37 or not contextual_set <= source_set:
        raise SystemExit('v27 contextual list drift')
    nonsexual_set = source_set - contextual_set
    if len(nonsexual_set) != 141:
        raise SystemExit(f'v27 derived NON_SEXUAL drift: {len(nonsexual_set)}')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = Counter()
    for intent, group in [('NON_SEXUAL', nonsexual_set), ('CONTEXTUAL', contextual_set)]:
        for key in sorted(group):
            target = index.get(key)
            if target is None:
                raise SystemExit(f'v27 key missing from sidecar: {key}')
            if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
                raise SystemExit(f'v27 key not cleanly UNCLASSIFIED in v15: {key}')
            target['sexual_intent'] = intent
            target['review_status'] = 'HUMAN_REVIEWED'
            target['rule_id'] = f'HUMAN_{intent}_CLOTHING_ACCESSORY_V27'
            target['evidence'] = 'full human review of all 178 General-only CLOTHING/ACCESSORY candidates; fixed review policy'
            promoted[intent] += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {'AUTO_HIGH_CONF': 22371, 'HUMAN_REVIEWED': 1913, 'UNCLASSIFIED': 7468}
    expected_classes = {'CONTEXTUAL': 289, 'NON_SEXUAL': 23131, 'NULL': 7468, 'SEXUAL': 864}
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
        'mode': 'RESEARCH_SIDECAR_V16_CLOTHING_ACCESSORY_FULL_REVIEW',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_promotions': dict(sorted(promoted.items())),
        'new_total_promotions': sum(promoted.values()),
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
