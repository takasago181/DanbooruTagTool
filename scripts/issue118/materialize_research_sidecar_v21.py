#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v20.csv')
REVIEW = Path('docs/issue118/exposure_clothing_review_v33/review_policy_v33.json')
SOURCE = Path('docs/issue118/exposure_clothing_review_v33/full_review_candidate_v33.csv')
OUT = Path('docs/issue118/research_sidecar_v21.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v21.json')


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
    if len(source) != 83 or review.get('source_rows') != 83:
        raise SystemExit('v33 source count drift')
    if review.get('decision_counts') != {'SEXUAL': 22, 'CONTEXTUAL': 44, 'NON_SEXUAL': 17}:
        raise SystemExit(f'v33 decision count drift: {review.get("decision_counts")}')

    source_set = {r['identity_key'] for r in source}
    groups = {
        'SEXUAL': set(review.get('sexual') or []),
        'CONTEXTUAL': set(review.get('contextual') or []),
        'NON_SEXUAL': set(review.get('non_sexual') or []),
    }
    union = set().union(*groups.values())
    if union != source_set or sum(len(v) for v in groups.values()) != len(source_set):
        raise SystemExit('v33 review coverage/overlap drift')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = Counter()
    for intent in ('NON_SEXUAL', 'CONTEXTUAL', 'SEXUAL'):
        for key in sorted(groups[intent]):
            target = index.get(key)
            if target is None:
                raise SystemExit(f'v33 key missing from sidecar: {key}')
            if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
                raise SystemExit(f'v33 key not cleanly UNCLASSIFIED in v20: {key}')
            target['sexual_intent'] = intent
            target['review_status'] = 'HUMAN_REVIEWED'
            target['rule_id'] = f'HUMAN_{intent}_EXPOSURE_CLOTHING_V33'
            target['evidence'] = 'full human review of all 83 General-only exposure/sexualized-clothing candidates; fixed review policy'
            promoted[intent] += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {'AUTO_HIGH_CONF': 22371, 'HUMAN_REVIEWED': 2396, 'UNCLASSIFIED': 6985}
    expected_classes = {'CONTEXTUAL': 421, 'NON_SEXUAL': 23222, 'NULL': 6985, 'SEXUAL': 1124}
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
        'mode': 'RESEARCH_SIDECAR_V21_EXPOSURE_CLOTHING_FULL_REVIEW',
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
