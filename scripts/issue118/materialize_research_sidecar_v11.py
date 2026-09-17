#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v10.csv')
REVIEW = Path('docs/issue118/special_only_explicit_v21_2/review_decisions_v21_2.json')
OUT = Path('docs/issue118/research_sidecar_v11.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v11.json')


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
    if review.get('reviewed_rows') != 70 or review.get('decision_counts') != {'SEXUAL': 70}:
        raise SystemExit(f'v21.2 review drift: {review.get("decision_counts")}')

    review_keys = review.get('reviewed_identity_keys') or []
    if len(review_keys) != 70 or len(set(review_keys)) != 70:
        raise SystemExit('v21.2 reviewed_identity_keys count/uniqueness drift')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = 0
    for key in review_keys:
        target = index.get(key)
        if target is None:
            raise SystemExit(f'v21.2 reviewed key missing from sidecar: {key}')
        if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
            raise SystemExit(
                f'v21.2 reviewed key not cleanly UNCLASSIFIED in v10: {key} '
                f"status={target['review_status']} class={target['sexual_intent']}"
            )
        target['sexual_intent'] = 'SEXUAL'
        target['review_status'] = 'HUMAN_REVIEWED'
        target['rule_id'] = 'HUMAN_SEXUAL_SPECIAL_EXPLICIT_V21_2'
        target['evidence'] = 'full manual concept review of 70 explicit sexual Special-only residual identities; fixed review artifact'
        promoted += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 22371,
        'HUMAN_REVIEWED': 1472,
        'UNCLASSIFIED': 7909,
    }
    expected_classes = {
        'CONTEXTUAL': 238,
        'NON_SEXUAL': 22750,
        'NULL': 7909,
        'SEXUAL': 855,
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
        'mode': 'RESEARCH_SIDECAR_V11_SPECIAL_V21_2_FULL_REVIEW',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_special_v21_2_human_sexual_promotions': promoted,
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
