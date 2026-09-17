#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v11.csv')
REVIEWED_SOURCE = Path('docs/issue118/pathless_structural_safe_v24/fresh_holdout_template_v24.csv')
REVIEW_GATE = Path('docs/issue118/pathless_structural_safe_v24/review_gate_v24.json')
OUT = Path('docs/issue118/research_sidecar_v12.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v12.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f'blob {len(data)}\0'.encode('utf-8')
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    base = read_csv(BASE)
    reviewed = read_csv(REVIEWED_SOURCE)
    gate = json.loads(REVIEW_GATE.read_text(encoding='utf-8'))

    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(reviewed) != 83:
        raise SystemExit(f'expected 83 reviewed v24 rows, got {len(reviewed)}')
    if gate.get('reviewed_rows') != 83 or gate.get('decision_counts') != {'NON_SEXUAL': 83}:
        raise SystemExit('v24 review gate count drift')
    if gate.get('decision') != 'PASS_FOR_RESEARCH_PROMOTION':
        raise SystemExit('v24 review gate not PASS')
    expected_blob = gate.get('reviewed_source_git_blob_sha1')
    actual_blob = git_blob_sha1(REVIEWED_SOURCE)
    if actual_blob != expected_blob:
        raise SystemExit(f'v24 reviewed source blob drift: expected={expected_blob} actual={actual_blob}')

    keys = [r['identity_key'] for r in reviewed]
    if len(keys) != len(set(keys)):
        raise SystemExit('duplicate identity_key in v24 reviewed source')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted = 0
    for key in keys:
        target = index.get(key)
        if target is None:
            raise SystemExit(f'v24 reviewed key missing from sidecar: {key}')
        if target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
            raise SystemExit(
                f'v24 reviewed key not cleanly UNCLASSIFIED in v11: {key} '
                f"status={target['review_status']} class={target['sexual_intent']}"
            )
        target['sexual_intent'] = 'NON_SEXUAL'
        target['review_status'] = 'HUMAN_REVIEWED'
        target['rule_id'] = 'HUMAN_NONSEXUAL_PATHLESS_STRUCTURAL_V24'
        target['evidence'] = 'full human review of all 83 fixed structural-safe pathless identities; reviewed source pinned by Git blob SHA-1'
        promoted += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 22371,
        'HUMAN_REVIEWED': 1555,
        'UNCLASSIFIED': 7826,
    }
    expected_classes = {
        'CONTEXTUAL': 238,
        'NON_SEXUAL': 22833,
        'NULL': 7826,
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
        'mode': 'RESEARCH_SIDECAR_V12_PATHLESS_STRUCTURAL_FULL_REVIEW',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_pathless_structural_human_nonsexual_promotions': promoted,
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'reviewed_source': str(REVIEWED_SOURCE),
        'reviewed_source_git_blob_sha1': actual_blob,
        'review_gate_source': str(REVIEW_GATE),
        'review_gate_sha256': sha256(REVIEW_GATE),
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
