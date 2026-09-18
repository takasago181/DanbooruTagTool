#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v32.csv')
REVIEW = Path('docs/issue118/action_five_cluster_review_v58/review_policy_v58.json')
CANDIDATE = Path('docs/issue118/action_five_cluster_review_v58/full_review_candidate_v58.csv')
REVIEW_BLOB = '3556f8832e5c40cb52dfe0025faa452c16f183dd'
CANDIDATE_BLOB = '2c066aeaf1cc8a304dee89f221eede6f8a6874b9'
OUT = Path('docs/issue118/research_sidecar_v33.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v33.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def main() -> int:
    if git_blob_sha(REVIEW) != REVIEW_BLOB:
        raise SystemExit('V58 fixed review blob SHA drift')
    if git_blob_sha(CANDIDATE) != CANDIDATE_BLOB:
        raise SystemExit('V58 fixed candidate blob SHA drift')

    base = read_csv(BASE)
    source = read_csv(CANDIDATE)
    review = json.loads(REVIEW.read_text(encoding='utf-8'))
    if len(base) != 31752:
        raise SystemExit(f'base drift {len(base)}')
    if len(source) != 95 or review.get('source_rows') != 95:
        raise SystemExit('V58 source count drift')
    if review.get('review_verdicts_generated_by_materializer') != 'NO':
        raise SystemExit('V58 provenance drift: generated verdicts')
    if review.get('review_artifacts_are_external_inputs') != 'YES':
        raise SystemExit('V58 provenance drift: external input flag')

    source_set = {r['identity_key'] for r in source}
    groups = {
        'SEXUAL': set(review.get('sexual') or []),
        'CONTEXTUAL': set(review.get('contextual') or []),
        'NON_SEXUAL': set(review.get('non_sexual') or []),
    }
    union = set()
    for intent, keys in groups.items():
        if not keys <= source_set:
            raise SystemExit(f'{intent} outside source')
        if union & keys:
            raise SystemExit('review groups overlap')
        union |= keys
    if union != source_set:
        raise SystemExit(f'review does not cover fixed source: missing={sorted(source_set-union)}')
    expected_counts = {intent: len(keys) for intent, keys in groups.items()}
    if expected_counts != review['decision_counts']:
        raise SystemExit(f'review count drift {expected_counts}')
    if review.get('unclassified'):
        raise SystemExit('V58 has unexpected unclassified rows')

    index = {r['identity_key']: dict(r) for r in base}
    promoted = Counter()
    for intent, keys in groups.items():
        for key in sorted(keys):
            target = index.get(key)
            if target is None or target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
                raise SystemExit(f'V58 not cleanly unclassified: {key}')
            target['sexual_intent'] = intent
            target['review_status'] = 'HUMAN_REVIEWED'
            target['rule_id'] = f'HUMAN_{intent}_V58'
            target['evidence'] = 'full semantic review of fixed V58 candidate set'
            promoted[intent] += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status = {'AUTO_HIGH_CONF': 22371, 'HUMAN_REVIEWED': 3782, 'UNCLASSIFIED': 5599}
    expected_classes = {'CONTEXTUAL': 1025, 'NON_SEXUAL': 23528, 'NULL': 5599, 'SEXUAL': 1600}
    if dict(sorted(status.items())) != expected_status:
        raise SystemExit(f'status mismatch {dict(status)}')
    if dict(sorted(classes.items())) != expected_classes:
        raise SystemExit(f'class mismatch {dict(classes)}')

    with OUT.open('w', encoding='utf-8', newline='') as f:
        fields = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

    summary = {
        'issue': 118,
        'mode': 'RESEARCH_SIDECAR_V33_V58_FULL_REVIEW',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_promotions': dict(sorted(promoted.items())),
        'new_total_promotions': sum(promoted.values()),
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'review_inputs': [{
            'label': 'V58',
            'review_source': str(REVIEW),
            'review_git_blob_sha': REVIEW_BLOB,
            'review_sha256': sha256(REVIEW),
            'candidate_source': str(CANDIDATE),
            'candidate_git_blob_sha': CANDIDATE_BLOB,
            'source_rows': 95,
        }],
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
