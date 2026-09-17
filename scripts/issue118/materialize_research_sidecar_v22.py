#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v21.csv')
REVIEWS = [
    ('V34', Path('docs/issue118/clothing_everyday_exposure_review_v34/review_policy_v34.json'), Path('docs/issue118/clothing_everyday_exposure_review_v34/full_review_candidate_v34.csv'), 180, 8, 172),
    ('V35', Path('docs/issue118/overlap_body_anatomy_review_v35/review_policy_v35.json'), Path('docs/issue118/overlap_body_anatomy_review_v35/full_review_candidate_v35.csv'), 66, 7, 59),
]
OUT = Path('docs/issue118/research_sidecar_v22.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v22.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = read_csv(BASE)
    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = Counter()
    review_meta = []
    all_review_keys = set()
    for label, review_path, source_path, expected_rows, expected_sexual, expected_contextual in REVIEWS:
        source = read_csv(source_path)
        review = json.loads(review_path.read_text(encoding='utf-8'))
        if len(source) != expected_rows or review.get('source_rows') != expected_rows:
            raise SystemExit(f'{label} source count drift')
        if review.get('decision_counts') != {'SEXUAL': expected_sexual, 'CONTEXTUAL': expected_contextual, 'NON_SEXUAL': 0}:
            raise SystemExit(f'{label} decision count drift: {review.get("decision_counts")}')
        source_set = {r['identity_key'] for r in source}
        sexual = set(review.get('sexual') or [])
        if len(sexual) != expected_sexual or not sexual <= source_set:
            raise SystemExit(f'{label} sexual list drift')
        contextual = source_set - sexual
        if len(contextual) != expected_contextual:
            raise SystemExit(f'{label} contextual derivation drift: {len(contextual)}')
        if all_review_keys & source_set:
            raise SystemExit(f'{label} overlaps previous review source')
        all_review_keys |= source_set
        for intent, group in [('SEXUAL', sexual), ('CONTEXTUAL', contextual)]:
            for key in sorted(group):
                target = index.get(key)
                if target is None:
                    raise SystemExit(f'{label} key missing from sidecar: {key}')
                if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
                    raise SystemExit(f'{label} key not cleanly UNCLASSIFIED in v21: {key}')
                target['sexual_intent'] = intent
                target['review_status'] = 'HUMAN_REVIEWED'
                target['rule_id'] = f'HUMAN_{intent}_{label}'
                target['evidence'] = f'full human review of fixed {expected_rows}-row research source {label}; external review policy'
                promoted[intent] += 1
        review_meta.append({'label': label, 'review_source': str(review_path), 'review_sha256': sha256(review_path), 'source_rows': expected_rows})

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status = {'AUTO_HIGH_CONF': 22371, 'HUMAN_REVIEWED': 2642, 'UNCLASSIFIED': 6739}
    expected_classes = {'CONTEXTUAL': 652, 'NON_SEXUAL': 23222, 'NULL': 6739, 'SEXUAL': 1139}
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
        'mode': 'RESEARCH_SIDECAR_V22_V34_V35_FULL_REVIEWS',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_promotions': dict(sorted(promoted.items())),
        'new_total_promotions': sum(promoted.values()),
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'review_inputs': review_meta,
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
