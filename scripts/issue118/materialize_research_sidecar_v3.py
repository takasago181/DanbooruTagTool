#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v1.csv')
SAFE = Path('docs/issue118/safe_general_converged_v6/candidate_inventory_v6.csv')
OUT = Path('docs/issue118/research_sidecar_v3.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v3.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main() -> int:
    base = read_csv(BASE)
    safe = read_csv(SAFE)
    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(safe) != 10164:
        raise SystemExit(f'v6 safe candidate drift: {len(safe)}')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = 0
    for candidate in safe:
        key = candidate['identity_key']
        row = index.get(key)
        if row is None:
            raise SystemExit(f'v6 candidate missing from base sidecar: {key}')
        if row['review_status'] != 'UNCLASSIFIED' or row['sexual_intent']:
            raise SystemExit(
                f'v6 candidate is not cleanly UNCLASSIFIED in v1: {key} '
                f"status={row['review_status']} class={row['sexual_intent']}"
            )
        row['sexual_intent'] = 'NON_SEXUAL'
        row['review_status'] = 'AUTO_HIGH_CONF'
        row['rule_id'] = 'AUTO_NONSEX_SAFE_GENERAL_V6'
        row['evidence'] = (
            'safe_general_converged_v6; adversarial lexical exclusions; '
            'fresh v4 holdout 120/120 NON_SEXUAL; no materializer-generated review verdicts'
        )
        promoted += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 14948,
        'HUMAN_REVIEWED': 924,
        'UNCLASSIFIED': 15880,
    }
    expected_classes = {
        'CONTEXTUAL': 189,
        'NON_SEXUAL': 15099,
        'NULL': 15880,
        'SEXUAL': 584,
    }
    if dict(sorted(status.items())) != expected_status:
        raise SystemExit(f'status mismatch: {dict(status)}')
    if dict(sorted(classes.items())) != expected_classes:
        raise SystemExit(f'class mismatch: {dict(classes)}')

    with OUT.open('w', encoding='utf-8', newline='') as f:
        fields = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

    summary = {
        'issue': 118,
        'mode': 'RESEARCH_SIDECAR_V3_CORRECTED_PROVENANCE',
        'identity_rows': len(rows),
        'new_safe_general_auto_promotions_from_v1': promoted,
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'source_base': 'research_sidecar_v1.csv',
        'safe_candidate_source': 'safe_general_converged_v6/candidate_inventory_v6.csv',
        'inherits_materializer_generated_human_reviews_from_v2': 'NO',
        'new_human_review_rows_created': 0,
        'review_verdicts_generated_by_materializer': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
