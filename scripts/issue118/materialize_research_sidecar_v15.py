#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v14.csv')
CANDIDATE_REVIEW = Path('docs/issue118/object_prop_low_risk_v26/review_policy_v26.json')
BOUNDARY_REVIEW = Path('docs/issue118/object_prop_low_risk_v26/boundary_review_policy_v26.json')
OUT = Path('docs/issue118/research_sidecar_v15.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v15.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = read_csv(BASE)
    candidate_review = json.loads(CANDIDATE_REVIEW.read_text(encoding='utf-8'))
    boundary_review = json.loads(BOUNDARY_REVIEW.read_text(encoding='utf-8'))

    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if candidate_review.get('source_rows') != 141:
        raise SystemExit('v26 candidate review row drift')
    if candidate_review.get('decision_counts') != {'NON_SEXUAL': 131, 'CONTEXTUAL': 4, 'SEXUAL': 4, 'UNCLASSIFIED': 2}:
        raise SystemExit('v26 candidate review decision drift')
    if boundary_review.get('source_rows') != 20:
        raise SystemExit('v26 boundary review row drift')
    if boundary_review.get('decision_counts') != {'NON_SEXUAL': 12, 'CONTEXTUAL': 4, 'SEXUAL': 4}:
        raise SystemExit('v26 boundary review decision drift')

    groups = {
        'NON_SEXUAL': [],
        'CONTEXTUAL': [],
        'SEXUAL': [],
    }
    candidate_set = set()
    all_candidate_source = read_csv(Path(candidate_review['source']))
    if len(all_candidate_source) != 141:
        raise SystemExit('v26 candidate source row drift')
    all_candidate_keys = [r['identity_key'] for r in all_candidate_source]
    if len(all_candidate_keys) != len(set(all_candidate_keys)):
        raise SystemExit('duplicate identity in v26 candidate source')
    candidate_set = set(all_candidate_keys)
    c_context = set(candidate_review.get('contextual') or [])
    c_sexual = set(candidate_review.get('sexual') or [])
    c_keep = set(candidate_review.get('keep_unclassified') or [])
    if len(c_context) != 4 or len(c_sexual) != 4 or len(c_keep) != 2:
        raise SystemExit('v26 candidate exception count drift')
    c_non = candidate_set - c_context - c_sexual - c_keep
    if len(c_non) != 131:
        raise SystemExit(f'v26 candidate derived NON_SEXUAL drift: {len(c_non)}')
    groups['NON_SEXUAL'].extend(sorted(c_non))
    groups['CONTEXTUAL'].extend(sorted(c_context))
    groups['SEXUAL'].extend(sorted(c_sexual))

    for intent, field in [('NON_SEXUAL', 'non_sexual'), ('CONTEXTUAL', 'contextual'), ('SEXUAL', 'sexual')]:
        vals = boundary_review.get(field) or []
        groups[intent].extend(vals)

    keep = sorted(c_keep)
    promoted_keys = [k for vals in groups.values() for k in vals]
    if len(promoted_keys) != 159 or len(set(promoted_keys)) != 159:
        raise SystemExit('v26 total promotion count/uniqueness drift')
    if set(promoted_keys) & set(keep):
        raise SystemExit('v26 promoted/keep overlap')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = Counter()
    for intent, keys in groups.items():
        for key in keys:
            target = index.get(key)
            if target is None:
                raise SystemExit(f'v26 reviewed key missing from sidecar: {key}')
            if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
                raise SystemExit(f'v26 reviewed key not cleanly UNCLASSIFIED in v14: {key}')
            target['sexual_intent'] = intent
            target['review_status'] = 'HUMAN_REVIEWED'
            target['rule_id'] = f'HUMAN_{intent}_OBJECT_PROP_V26'
            target['evidence'] = 'full human review of all 161 General-only OBJECT_PROP identities; candidate and boundary policies are fixed external review artifacts'
            promoted[intent] += 1

    for key in keep:
        target = index.get(key)
        if target is None:
            raise SystemExit(f'v26 keep-unclassified key missing from sidecar: {key}')
        if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
            raise SystemExit(f'v26 keep-unclassified key no longer cleanly UNCLASSIFIED: {key}')

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {'AUTO_HIGH_CONF': 22371, 'HUMAN_REVIEWED': 1735, 'UNCLASSIFIED': 7646}
    expected_classes = {'CONTEXTUAL': 252, 'NON_SEXUAL': 22990, 'NULL': 7646, 'SEXUAL': 864}
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
        'mode': 'RESEARCH_SIDECAR_V15_OBJECT_PROP_FULL_REVIEW',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_promotions': dict(sorted(promoted.items())),
        'new_total_promotions': sum(promoted.values()),
        'kept_unclassified': len(keep),
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'candidate_review_source': str(CANDIDATE_REVIEW),
        'candidate_review_sha256': sha256(CANDIDATE_REVIEW),
        'boundary_review_source': str(BOUNDARY_REVIEW),
        'boundary_review_sha256': sha256(BOUNDARY_REVIEW),
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
