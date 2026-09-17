#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v6.csv')
LOW_RISK = Path('docs/issue118/action_low_risk_subcluster_v17/low_risk_candidate_v17.csv')
LOW_RISK_GATE = Path('docs/issue118/action_low_risk_subcluster_v17/holdout_gate_v17.json')
VIOLENCE = Path('docs/issue118/action_interaction_refinement_v16/violence_nonsex_axis_v16.csv')
VIOLENCE_REVIEW = Path('docs/issue118/action_interaction_refinement_v16/violence_review_decisions_v16.json')
INTIMATE = Path('docs/issue118/action_interaction_refinement_v16/intimate_general_v16.csv')
INTIMATE_REVIEW = Path('docs/issue118/action_interaction_refinement_v16/intimate_review_decisions_v16.json')
OUT = Path('docs/issue118/research_sidecar_v7.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v7.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def promote(row: dict[str, str], *, status: str, rule_id: str, evidence: str) -> None:
    if row['review_status'] != 'UNCLASSIFIED' or row['sexual_intent']:
        raise SystemExit(
            f"row is not cleanly UNCLASSIFIED before promotion: {row['identity_key']} "
            f"status={row['review_status']} class={row['sexual_intent']}"
        )
    row['sexual_intent'] = 'NON_SEXUAL'
    row['review_status'] = status
    row['rule_id'] = rule_id
    row['evidence'] = evidence


def main() -> int:
    base = read_csv(BASE)
    low_risk = read_csv(LOW_RISK)
    low_gate = json.loads(LOW_RISK_GATE.read_text(encoding='utf-8'))
    violence = read_csv(VIOLENCE)
    violence_review = json.loads(VIOLENCE_REVIEW.read_text(encoding='utf-8'))
    intimate = read_csv(INTIMATE)
    intimate_review = json.loads(INTIMATE_REVIEW.read_text(encoding='utf-8'))

    if len(base) != 31752:
        raise SystemExit(f'base sidecar drift: {len(base)}')
    if len(low_risk) != 953:
        raise SystemExit(f'expected v17 low-risk population 953, got {len(low_risk)}')
    if low_gate.get('gate') != 'PASS_FOR_RESEARCH_PROMOTION':
        raise SystemExit(f'v17 holdout gate is not PASS: {low_gate.get("gate")}')
    if low_gate.get('decision_counts') != {'NON_SEXUAL': 120, 'CONTEXTUAL': 0, 'SEXUAL': 0}:
        raise SystemExit(f'v17 gate count drift: {low_gate.get("decision_counts")}')

    if len(violence) != 41 or violence_review.get('reviewed_rows') != 41:
        raise SystemExit('violence review/source count drift')
    if violence_review.get('decision_counts') != {'NON_SEXUAL': 41}:
        raise SystemExit(f'violence review drift: {violence_review.get("decision_counts")}')
    if violence_review.get('review_verdicts_generated_by_materializer') != 'NO':
        raise SystemExit('violence review provenance drift')

    if len(intimate) != 71 or intimate_review.get('reviewed_rows') != 71:
        raise SystemExit('intimate review/source count drift')
    if intimate_review.get('decision_counts') != {'NON_SEXUAL': 63, 'KEEP_UNCLASSIFIED': 8}:
        raise SystemExit(f'intimate review drift: {intimate_review.get("decision_counts")}')
    if intimate_review.get('review_verdicts_generated_by_materializer') != 'NO':
        raise SystemExit('intimate review provenance drift')
    intimate_keep = set(intimate_review.get('keep_unclassified') or [])
    if len(intimate_keep) != 8:
        raise SystemExit('intimate keep-unclassified list drift')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != len(base):
        raise SystemExit('duplicate identity_key in base sidecar')

    promoted_keys: set[str] = set()
    auto = 0
    human_violence = 0
    human_intimate = 0

    for candidate in low_risk:
        key = candidate['identity_key']
        if key in promoted_keys:
            raise SystemExit(f'duplicate promotion key: {key}')
        row = index.get(key)
        if row is None:
            raise SystemExit(f'low-risk key missing from sidecar: {key}')
        promote(
            row,
            status='AUTO_HIGH_CONF',
            rule_id='AUTO_NONSEX_ACTION_LOWRISK_V17',
            evidence='action v17 conservative low-risk subcluster; fresh independent holdout 120/120 NON_SEXUAL',
        )
        promoted_keys.add(key)
        auto += 1

    for candidate in violence:
        key = candidate['identity_key']
        if key in promoted_keys:
            raise SystemExit(f'violence overlaps prior promotion: {key}')
        row = index.get(key)
        if row is None:
            raise SystemExit(f'violence key missing from sidecar: {key}')
        promote(
            row,
            status='HUMAN_REVIEWED',
            rule_id='REVIEWED_NONSEX_ACTION_VIOLENCE_V16',
            evidence='independent v16 full review: violence/coercion severity is separate from sexual intent',
        )
        promoted_keys.add(key)
        human_violence += 1

    intimate_source_keys = {r['identity_key'] for r in intimate}
    if not intimate_keep <= intimate_source_keys:
        raise SystemExit(f'intimate keep list contains non-source keys: {sorted(intimate_keep - intimate_source_keys)}')
    for candidate in intimate:
        key = candidate['identity_key']
        if key in intimate_keep:
            continue
        if key in promoted_keys:
            raise SystemExit(f'intimate overlaps prior promotion: {key}')
        row = index.get(key)
        if row is None:
            raise SystemExit(f'intimate key missing from sidecar: {key}')
        promote(
            row,
            status='HUMAN_REVIEWED',
            rule_id='REVIEWED_NONSEX_ACTION_INTIMATE_V16',
            evidence='independent v16 full review: ordinary affection/romance concept; fetish-ambiguous body-site variants kept UNCLASSIFIED',
        )
        promoted_keys.add(key)
        human_intimate += 1

    if auto != 953 or human_violence != 41 or human_intimate != 63:
        raise SystemExit(f'promotion counts drift auto={auto} violence={human_violence} intimate={human_intimate}')

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 20915,
        'HUMAN_REVIEWED': 1166,
        'UNCLASSIFIED': 9671,
    }
    expected_classes = {
        'CONTEXTUAL': 201,
        'NON_SEXUAL': 21294,
        'NULL': 9671,
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
        'mode': 'RESEARCH_SIDECAR_V7_ACTION_REVIEW_GATED',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_action_auto_promotions': auto,
        'new_action_human_violence_promotions': human_violence,
        'new_action_human_intimate_promotions': human_intimate,
        'new_action_total_promotions': len(promoted_keys),
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'low_risk_source': str(LOW_RISK),
        'low_risk_gate_source': str(LOW_RISK_GATE),
        'low_risk_gate_sha256': sha256(LOW_RISK_GATE),
        'violence_review_source': str(VIOLENCE_REVIEW),
        'violence_review_sha256': sha256(VIOLENCE_REVIEW),
        'intimate_review_source': str(INTIMATE_REVIEW),
        'intimate_review_sha256': sha256(INTIMATE_REVIEW),
        'intimate_keep_unclassified': len(intimate_keep),
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
