#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v5.csv')
CLEAN = Path('docs/issue118/pose_movement_refinement_v14_2/pose_clean_v14_2.csv')
HOLDOUT_GATE = Path('docs/issue118/pose_movement_refinement_v14_2/holdout_gate_v14_2.json')
OUT = Path('docs/issue118/research_sidecar_v6.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v6.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = read_csv(BASE)
    clean = read_csv(CLEAN)
    gate = json.loads(HOLDOUT_GATE.read_text(encoding='utf-8'))

    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(clean) != 706:
        raise SystemExit(f'expected v14.2 pose clean population 706, got {len(clean)}')
    if gate.get('gate') != 'PASS_FOR_RESEARCH_PROMOTION':
        raise SystemExit(f'v14.2 holdout gate is not PASS: {gate.get("gate")}')
    if gate.get('reviewed_rows') != 120:
        raise SystemExit('v14.2 holdout row count drift')
    if gate.get('decision_counts') != {'NON_SEXUAL': 120, 'CONTEXTUAL': 0, 'SEXUAL': 0}:
        raise SystemExit(f'v14.2 decision count drift: {gate.get("decision_counts")}')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = 0
    seen = set()
    for candidate in clean:
        key = candidate['identity_key']
        if key in seen:
            raise SystemExit(f'duplicate v14.2 clean identity: {key}')
        seen.add(key)
        row = index.get(key)
        if row is None:
            raise SystemExit(f'v14.2 clean key missing from sidecar: {key}')
        if row['review_status'] != 'UNCLASSIFIED' or row['sexual_intent']:
            raise SystemExit(
                f'v14.2 clean key is not cleanly UNCLASSIFIED in v5: {key} '
                f"status={row['review_status']} class={row['sexual_intent']}"
            )
        row['sexual_intent'] = 'NON_SEXUAL'
        row['review_status'] = 'AUTO_HIGH_CONF'
        row['rule_id'] = 'AUTO_NONSEX_POSE_V14_2'
        row['evidence'] = (
            'pose v14.2 final clean set; iterative sexual/fetish pose boundary refinement; '
            'fresh v14.2 holdout 120/120 NON_SEXUAL'
        )
        promoted += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 19962,
        'HUMAN_REVIEWED': 1062,
        'UNCLASSIFIED': 10728,
    }
    expected_classes = {
        'CONTEXTUAL': 201,
        'NON_SEXUAL': 20237,
        'NULL': 10728,
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
        'mode': 'RESEARCH_SIDECAR_V6_POSE_REVIEW_GATED',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_pose_auto_promotions': promoted,
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'pose_clean_source': str(CLEAN),
        'pose_holdout_gate_source': str(HOLDOUT_GATE),
        'pose_holdout_gate_sha256': sha256(HOLDOUT_GATE),
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
