#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v7.csv')
CANDIDATE = Path('docs/issue118/body_part_refinement_v19_2/low_risk_body_candidate_v19_2.csv')
HOLDOUT_GATE = Path('docs/issue118/body_part_refinement_v19_2/holdout_gate_v19_2.json')
OUT = Path('docs/issue118/research_sidecar_v8.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v8.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = read_csv(BASE)
    candidate = read_csv(CANDIDATE)
    gate = json.loads(HOLDOUT_GATE.read_text(encoding='utf-8'))

    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(candidate) != 1456:
        raise SystemExit(f'expected BODY_PART candidate population 1456, got {len(candidate)}')
    if gate.get('result') != 'PASS_FOR_RESEARCH_PROMOTION':
        raise SystemExit(f'BODY_PART holdout gate is not PASS: {gate.get("result")}')
    if gate.get('holdout_rows') != 120 or gate.get('decision_counts') != {'NON_SEXUAL': 120}:
        raise SystemExit(f'BODY_PART holdout gate drift: {gate}')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = 0
    seen = set()
    for row in candidate:
        key = row['identity_key']
        if key in seen:
            raise SystemExit(f'duplicate BODY_PART candidate identity: {key}')
        seen.add(key)
        target = index.get(key)
        if target is None:
            raise SystemExit(f'BODY_PART candidate missing from sidecar: {key}')
        if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
            raise SystemExit(
                f'BODY_PART candidate not cleanly UNCLASSIFIED in v7: {key} '
                f"status={target['review_status']} class={target['sexual_intent']}"
            )
        target['sexual_intent'] = 'NON_SEXUAL'
        target['review_status'] = 'AUTO_HIGH_CONF'
        target['rule_id'] = 'AUTO_NONSEX_BODY_PART_V19_2'
        target['evidence'] = (
            'BODY_PART v19.2 low-risk identity set; conservative boundary ejection; '
            'fresh salted holdout 120/120 NON_SEXUAL'
        )
        promoted += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 22371,
        'HUMAN_REVIEWED': 1166,
        'UNCLASSIFIED': 8215,
    }
    expected_classes = {
        'CONTEXTUAL': 201,
        'NON_SEXUAL': 22750,
        'NULL': 8215,
        'SEXUAL': 586,
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
        'mode': 'RESEARCH_SIDECAR_V8_BODY_PART_REVIEW_GATED',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_body_part_auto_promotions': promoted,
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'body_part_candidate_source': str(CANDIDATE),
        'body_part_holdout_gate_source': str(HOLDOUT_GATE),
        'body_part_holdout_gate_sha256': sha256(HOLDOUT_GATE),
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
