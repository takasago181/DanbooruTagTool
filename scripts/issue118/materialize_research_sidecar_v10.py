#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v9.csv')
CANDIDATE = Path('docs/issue118/special_only_explicit_v21_1/explicit_sexual_candidate_v21_1.csv')
REVIEW = Path('docs/issue118/special_only_explicit_v21_1/review_policy_v21_1.json')
OUT = Path('docs/issue118/research_sidecar_v10.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v10.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = read_csv(BASE)
    candidate = read_csv(CANDIDATE)
    review = json.loads(REVIEW.read_text(encoding='utf-8'))

    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(candidate) != 151:
        raise SystemExit(f'expected 151 v21.1 candidate rows, got {len(candidate)}')
    if review.get('candidate_rows') != 151:
        raise SystemExit('v21.1 review candidate_rows drift')
    if review.get('reviewed_sexual_rows') != 103:
        raise SystemExit('v21.1 reviewed_sexual_rows drift')
    if review.get('reviewed_contextual_rows') != 37:
        raise SystemExit('v21.1 reviewed_contextual_rows drift')
    if review.get('keep_unclassified_rows') != 11:
        raise SystemExit('v21.1 keep_unclassified_rows drift')
    if review.get('reviewed_promotions') != 140:
        raise SystemExit('v21.1 reviewed_promotions drift')

    candidate_keys = [r['identity_key'] for r in candidate]
    candidate_set = set(candidate_keys)
    if len(candidate_keys) != 151 or len(candidate_set) != 151:
        raise SystemExit('duplicate identity_key in v21.1 candidate')

    contextual = review.get('contextual') or []
    keep_unclassified = review.get('keep_unclassified') or []
    contextual_set = set(contextual)
    keep_set = set(keep_unclassified)
    if len(contextual) != 37 or len(contextual_set) != 37:
        raise SystemExit('v21.1 contextual list count/uniqueness drift')
    if len(keep_unclassified) != 11 or len(keep_set) != 11:
        raise SystemExit('v21.1 keep_unclassified list count/uniqueness drift')
    if contextual_set & keep_set:
        raise SystemExit('v21.1 contextual and keep_unclassified overlap')
    if not contextual_set <= candidate_set or not keep_set <= candidate_set:
        raise SystemExit('v21.1 review policy references key outside candidate set')

    sexual_set = candidate_set - contextual_set - keep_set
    if len(sexual_set) != 103:
        raise SystemExit(f'v21.1 derived sexual set drift: {len(sexual_set)}')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    sexual_promoted = 0
    contextual_promoted = 0
    for key in sorted(sexual_set | contextual_set):
        target = index.get(key)
        if target is None:
            raise SystemExit(f'v21.1 reviewed key missing from sidecar: {key}')
        if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
            raise SystemExit(
                f'v21.1 reviewed key not cleanly UNCLASSIFIED in v9: {key} '
                f"status={target['review_status']} class={target['sexual_intent']}"
            )
        if key in contextual_set:
            target['sexual_intent'] = 'CONTEXTUAL'
            target['rule_id'] = 'HUMAN_CONTEXTUAL_SPECIAL_EXPLICIT_V21_1'
            target['evidence'] = 'full manual review of 151 Special-only v21.1 candidates; anatomy/exposure/dual-use concept retained in both intent views'
            contextual_promoted += 1
        else:
            target['sexual_intent'] = 'SEXUAL'
            target['rule_id'] = 'HUMAN_SEXUAL_SPECIAL_EXPLICIT_V21_1'
            target['evidence'] = 'full manual review of 151 Special-only v21.1 candidates; explicit sexual act/fetish/device/content concept'
            sexual_promoted += 1
        target['review_status'] = 'HUMAN_REVIEWED'

    for key in sorted(keep_set):
        target = index.get(key)
        if target is None:
            raise SystemExit(f'v21.1 keep-unclassified key missing from sidecar: {key}')
        if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
            raise SystemExit(f'v21.1 keep-unclassified key is no longer cleanly UNCLASSIFIED: {key}')

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 22371,
        'HUMAN_REVIEWED': 1402,
        'UNCLASSIFIED': 7979,
    }
    expected_classes = {
        'CONTEXTUAL': 238,
        'NON_SEXUAL': 22750,
        'NULL': 7979,
        'SEXUAL': 785,
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
        'mode': 'RESEARCH_SIDECAR_V10_SPECIAL_V21_1_FULL_REVIEW',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_special_v21_1_human_sexual_promotions': sexual_promoted,
        'new_special_v21_1_human_contextual_promotions': contextual_promoted,
        'new_special_v21_1_total_promotions': sexual_promoted + contextual_promoted,
        'v21_1_keep_unclassified': len(keep_set),
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'candidate_source': str(CANDIDATE),
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
