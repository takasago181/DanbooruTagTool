#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v3.csv')
V9_REVIEW = Path('docs/issue118/bulk_candidate_adversarial_v9/redteam_review_decisions_v9.json')
V10_BOUNDARY_REVIEW = Path('docs/issue118/relationship_boundary_refinement_v10/relationship_boundary_review_decisions_v10.json')
V10_HOLDOUT_REVIEW = Path('docs/issue118/relationship_boundary_refinement_v10/fresh_holdout_review_v10.json')
V10_CLEAN = Path('docs/issue118/relationship_boundary_refinement_v10/clean_candidate_inventory_v10.csv')
OUT = Path('docs/issue118/research_sidecar_v4.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v4.json')

EXPECTED_V9_REVIEW_INVENTORY_BLOB = '27b6c0851ba6a91fd9ab18e9d03c697c370e1761'
EXPECTED_V10_BOUNDARY_INVENTORY_BLOB = '9c6c38470bac1f67a99ffc51c9348c77e3cd51d2'
EXPECTED_V10_HOLDOUT_INVENTORY_BLOB = 'bd1c235a6c830ac91d83c52935891113eed0e9fd'


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def require_unclassified(index: dict[str, dict[str, str]], key: str, source: str) -> dict[str, str]:
    row = index.get(key)
    if row is None:
        raise SystemExit(f'{source}: identity missing from base sidecar: {key}')
    if row['review_status'] != 'UNCLASSIFIED' or row['sexual_intent']:
        raise SystemExit(
            f'{source}: identity is not cleanly UNCLASSIFIED in v3: {key} '
            f"status={row['review_status']} class={row['sexual_intent']}"
        )
    return row


def apply_human_decision(row: dict[str, str], intent: str, source: str, reason: str) -> None:
    if intent not in {'SEXUAL', 'NON_SEXUAL', 'CONTEXTUAL'}:
        raise SystemExit(f'{source}: invalid reviewed intent {intent}')
    row['sexual_intent'] = intent
    row['review_status'] = 'HUMAN_REVIEWED'
    row['rule_id'] = source
    row['evidence'] = reason


def main() -> int:
    base = read_csv(BASE)
    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    v9 = read_json(V9_REVIEW)
    if v9['inventory_blob_sha'] != EXPECTED_V9_REVIEW_INVENTORY_BLOB:
        raise SystemExit('v9 review inventory provenance drift')
    if v9['reviewed_rows'] != 132:
        raise SystemExit('v9 reviewed row count drift')

    v9_contextual = set(v9['contextual'])
    v9_sexual = set(v9['sexual'])
    v9_keep = set(v9['keep_unclassified'])
    special_v9 = v9_contextual | v9_sexual | v9_keep
    if len(special_v9) != 14:
        raise SystemExit(f'v9 special decision set drift: {len(special_v9)}')

    # The v9 artifact declares all remaining reviewed rows NON_SEXUAL.
    # Recover the exact reviewed inventory from the source CSV so the materializer
    # never invents row membership or review verdicts.
    v9_inventory = read_csv(Path(v9['inventory']))
    if len(v9_inventory) != 132:
        raise SystemExit(f'v9 inventory row drift: {len(v9_inventory)}')
    v9_keys = {r['identity_key'] for r in v9_inventory}
    if len(v9_keys) != 132 or not special_v9 <= v9_keys:
        raise SystemExit('v9 inventory key/provenance mismatch')

    applied_v9 = Counter()
    for key in sorted(v9_keys):
        row = require_unclassified(index, key, 'V9_REDTEAM_HUMAN_REVIEW')
        if key in v9_keep:
            applied_v9['KEEP_UNCLASSIFIED'] += 1
            continue
        if key in v9_contextual:
            intent = 'CONTEXTUAL'
        elif key in v9_sexual:
            intent = 'SEXUAL'
        else:
            intent = 'NON_SEXUAL'
        apply_human_decision(
            row,
            intent,
            'HUMAN_REVIEW_V9_REDTEAM',
            'independent v9 red-team semantic review; source inventory fixed by blob SHA',
        )
        applied_v9[intent] += 1

    boundary = read_json(V10_BOUNDARY_REVIEW)
    if boundary['inventory_blob_sha'] != EXPECTED_V10_BOUNDARY_INVENTORY_BLOB:
        raise SystemExit('v10 boundary review inventory provenance drift')
    decisions = boundary['decisions']
    if boundary['reviewed_rows'] != 3 or len(decisions) != 3:
        raise SystemExit('v10 boundary reviewed row count drift')

    applied_boundary = Counter()
    for key, d in sorted(decisions.items()):
        row = require_unclassified(index, key, 'V10_RELATIONSHIP_HUMAN_REVIEW')
        intent = d['sexual_intent']
        apply_human_decision(
            row,
            intent,
            'HUMAN_REVIEW_V10_RELATIONSHIP_BOUNDARY',
            d['reason'],
        )
        applied_boundary[intent] += 1

    holdout = read_json(V10_HOLDOUT_REVIEW)
    if holdout['inventory_blob_sha'] != EXPECTED_V10_HOLDOUT_INVENTORY_BLOB:
        raise SystemExit('v10 holdout review inventory provenance drift')
    if holdout['reviewed_rows'] != 120:
        raise SystemExit('v10 holdout reviewed row count drift')
    if holdout['gate_result'] != 'PASS_FOR_RESEARCH_PROMOTION':
        raise SystemExit(f"v10 holdout gate is not PASS: {holdout['gate_result']}")
    if holdout['decision_counts'] != {
        'NON_SEXUAL': 120,
        'CONTEXTUAL': 0,
        'SEXUAL': 0,
        'KEEP_UNCLASSIFIED': 0,
    }:
        raise SystemExit(f"unexpected v10 holdout decisions: {holdout['decision_counts']}")

    clean = read_csv(V10_CLEAN)
    if len(clean) != 1708:
        raise SystemExit(f'v10 clean candidate drift: {len(clean)}')
    clean_keys = [r['identity_key'] for r in clean]
    if len(set(clean_keys)) != len(clean_keys):
        raise SystemExit('duplicate identity_key in v10 clean candidates')

    promoted = 0
    for candidate in clean:
        key = candidate['identity_key']
        row = require_unclassified(index, key, 'AUTO_NONSEX_V10_CLEAN')
        row['sexual_intent'] = 'NON_SEXUAL'
        row['review_status'] = 'AUTO_HIGH_CONF'
        row['rule_id'] = 'AUTO_NONSEX_CLUSTER_V10'
        row['evidence'] = (
            'v8 conservative cluster triage; v9 adversarial scan; '
            'v9 counterexample-driven relationship refinement; '
            'independent v10 fresh holdout 120/120 NON_SEXUAL; '
            'no materializer-generated review verdicts'
        )
        promoted += 1

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 16656,
        'HUMAN_REVIEWED': 1056,
        'UNCLASSIFIED': 14040,
    }
    expected_classes = {
        'CONTEXTUAL': 201,
        'NON_SEXUAL': 16925,
        'NULL': 14040,
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
        'mode': 'RESEARCH_SIDECAR_V4_REVIEW_GATED',
        'identity_rows': len(rows),
        'source_base': 'research_sidecar_v3.csv',
        'v9_human_review_applied': dict(sorted(applied_v9.items())),
        'v10_relationship_human_review_applied': dict(sorted(applied_boundary.items())),
        'new_v10_clean_auto_promotions': promoted,
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'v10_holdout_gate': holdout['gate_result'],
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
