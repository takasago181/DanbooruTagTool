#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v4.csv')
CLEAN = Path('docs/issue118/clothing_refinement_v12_7/clothing_clean_v12_7.csv')
HOLDOUT_GATE = Path('docs/issue118/clothing_refinement_v12_7/holdout_gate_v12_7.json')
REDTEAM_REVIEW = Path('docs/issue118/clothing_adversarial_v12_2/redteam_review_decisions_v12_2.json')
OUT = Path('docs/issue118/research_sidecar_v5.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v5.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    base = read_csv(BASE)
    clean = read_csv(CLEAN)
    gate = json.loads(HOLDOUT_GATE.read_text(encoding='utf-8'))
    redteam = json.loads(REDTEAM_REVIEW.read_text(encoding='utf-8'))

    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(clean) != 2600:
        raise SystemExit(f'expected v12.7 clean population 2600, got {len(clean)}')
    if gate.get('result') != 'PASS_FOR_RESEARCH_PROMOTION':
        raise SystemExit(f'v12.7 holdout gate is not PASS: {gate.get("result")}')
    if gate.get('holdout_rows') != 120:
        raise SystemExit('v12.7 holdout row count drift')
    if redteam.get('decision_counts') != {'NON_SEXUAL': 6, 'KEEP_UNCLASSIFIED': 4}:
        raise SystemExit(f'v12.2 redteam decision drift: {redteam.get("decision_counts")}')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    human_promoted = 0
    for key, decision in redteam['decisions'].items():
        row = index.get(key)
        if row is None:
            raise SystemExit(f'v12.2 reviewed key missing from sidecar: {key}')
        if decision == 'KEEP_UNCLASSIFIED':
            continue
        if decision != 'NON_SEXUAL':
            raise SystemExit(f'unexpected v12.2 decision: {key}={decision}')
        if row['review_status'] != 'UNCLASSIFIED' or row['sexual_intent']:
            raise SystemExit(
                f'v12.2 reviewed key is not cleanly UNCLASSIFIED in v4: {key} '
                f"status={row['review_status']} class={row['sexual_intent']}"
            )
        row['sexual_intent'] = 'NON_SEXUAL'
        row['review_status'] = 'HUMAN_REVIEWED'
        row['rule_id'] = 'HUMAN_NONSEX_CLOTHING_REDTEAM_V12_2'
        row['evidence'] = 'independent clothing redteam review v12.2; fixed review artifact'
        human_promoted += 1

    auto_promoted = 0
    clean_keys = set()
    for candidate in clean:
        key = candidate['identity_key']
        if key in clean_keys:
            raise SystemExit(f'duplicate v12.7 clean identity: {key}')
        clean_keys.add(key)
        row = index.get(key)
        if row is None:
            raise SystemExit(f'v12.7 clean key missing from sidecar: {key}')
        if row['review_status'] != 'UNCLASSIFIED' or row['sexual_intent']:
            raise SystemExit(
                f'v12.7 clean key is not cleanly UNCLASSIFIED in v4: {key} '
                f"status={row['review_status']} class={row['sexual_intent']}"
            )
        row['sexual_intent'] = 'NON_SEXUAL'
        row['review_status'] = 'AUTO_HIGH_CONF'
        row['rule_id'] = 'AUTO_NONSEX_CLOTHING_V12_7'
        row['evidence'] = (
            'clothing v12.7 final clean set; iterative adversarial boundary refinement; '
            'fresh v12.7 holdout 120/120 NON_SEXUAL'
        )
        auto_promoted += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 19256,
        'HUMAN_REVIEWED': 1062,
        'UNCLASSIFIED': 11434,
    }
    expected_classes = {
        'CONTEXTUAL': 201,
        'NON_SEXUAL': 19531,
        'NULL': 11434,
        'SEXUAL': 586,
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
        'mode': 'RESEARCH_SIDECAR_V5_CLOTHING_REVIEW_GATED',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_clothing_auto_promotions': auto_promoted,
        'new_clothing_human_promotions': human_promoted,
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'clothing_clean_source': str(CLEAN),
        'clothing_holdout_gate_source': str(HOLDOUT_GATE),
        'clothing_holdout_gate_sha256': sha256(HOLDOUT_GATE),
        'clothing_redteam_review_source': str(REDTEAM_REVIEW),
        'clothing_redteam_review_sha256': sha256(REDTEAM_REVIEW),
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
