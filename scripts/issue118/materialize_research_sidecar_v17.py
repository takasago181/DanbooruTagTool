#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v16.csv')
REVIEW = Path('docs/issue118/special_anatomy_review_v28/review_policy_v28.json')
SOURCE = Path('docs/issue118/special_anatomy_review_v28/full_review_candidate_v28.csv')
OUT = Path('docs/issue118/research_sidecar_v17.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v17.json')


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
    if len(source) != 170 or review.get('reviewed_rows') != 170:
        raise SystemExit('v28 source count drift')
    expected_verdict_counts = {'SEXUAL': 128, 'CONTEXTUAL': 42, 'NON_SEXUAL': 0, 'UNCLASSIFIED': 0}
    if review.get('verdict_counts') != expected_verdict_counts:
        raise SystemExit(f'v28 verdict count drift: {review.get("verdict_counts")}')

    source_keys = [r['identity_key'] for r in source]
    if len(source_keys) != len(set(source_keys)):
        raise SystemExit('duplicate identity in v28 source')
    source_set = set(source_keys)

    groups = {}
    for intent in ('SEXUAL', 'CONTEXTUAL', 'NON_SEXUAL', 'UNCLASSIFIED'):
        values = review.get(intent) or []
        if len(values) != len(set(values)):
            raise SystemExit(f'duplicate key in v28 {intent}')
        groups[intent] = set(values)

    decided_union = set().union(*groups.values())
    if decided_union != source_set:
        missing = sorted(source_set - decided_union)
        extra = sorted(decided_union - source_set)
        raise SystemExit(f'v28 review coverage drift missing={missing[:5]} extra={extra[:5]}')
    if sum(len(v) for v in groups.values()) != len(decided_union):
        raise SystemExit('v28 key appears in multiple verdict groups')
    if len(groups['SEXUAL']) != 128 or len(groups['CONTEXTUAL']) != 42:
        raise SystemExit('v28 reviewed group size drift')
    if groups['NON_SEXUAL'] or groups['UNCLASSIFIED']:
        raise SystemExit('v28 unexpected NON_SEXUAL/UNCLASSIFIED decisions')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = Counter()
    for intent in ('SEXUAL', 'CONTEXTUAL'):
        for key in sorted(groups[intent]):
            target = index.get(key)
            if target is None:
                raise SystemExit(f'v28 key missing from sidecar: {key}')
            if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
                raise SystemExit(f'v28 key not cleanly UNCLASSIFIED in v16: {key}')
            target['sexual_intent'] = intent
            target['review_status'] = 'HUMAN_REVIEWED'
            target['rule_id'] = f'HUMAN_{intent}_SPECIAL_ANATOMY_V28'
            target['evidence'] = 'full human review of all 170 Special-only anatomy candidates; breastfeeding/general-care anatomy remains CONTEXTUAL rather than NON_SEXUAL-only'
            promoted[intent] += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {'AUTO_HIGH_CONF': 22371, 'HUMAN_REVIEWED': 2083, 'UNCLASSIFIED': 7298}
    expected_classes = {'CONTEXTUAL': 331, 'NON_SEXUAL': 23131, 'NULL': 7298, 'SEXUAL': 992}
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
        'mode': 'RESEARCH_SIDECAR_V17_SPECIAL_ANATOMY_FULL_REVIEW',
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
