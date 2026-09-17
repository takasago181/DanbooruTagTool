#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v2.csv')
BASE_SUMMARY = Path('docs/issue118/research_sidecar_summary_v2.json')
WAVE = Path('docs/issue118/risk_exclusion_wave3')
INVENTORY = WAVE / 'refined_candidate_inventory_v2.csv'
AUDIT = WAVE / 'existing_review_audit_v2.csv'
DISCOVERY_REVIEW = WAVE / 'discovery_review_v1.csv'
HOLDOUT_V1_REVIEW = WAVE / 'holdout_review_v1.csv'
HOLDOUT_V2_REVIEW = WAVE / 'fresh_holdout_review_v2.csv'
HOLDOUT_V2_RESULT = WAVE / 'fresh_holdout_result_v2.json'
REFINE_SUMMARY = WAVE / 'refine_v2_summary.json'
OUT = Path('docs/issue118/research_sidecar_v3.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v3.json')

RULE_ID = 'AUTO_NONSEX_RISK_EXCLUSION_WAVE3_V2'
MANUAL_EVIDENCE = 'RISK_EXCLUSION_WAVE3_MANUAL_REVIEW'
AUTO_EVIDENCE = (
    'EXISTING_EXACT_PREDICATE_68_68_NONSEXUAL+'
    'DISCOVERY_36_36+'
    'FRESH_HOLDOUT_V1_36_36+'
    'FRESH_HOLDOUT_V2_36_36; '
    'risk=118_tokens; exact_exclusions=frogtie,riding_crop,shibarikini'
)


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def require_review(path: Path, expected: int) -> list[dict[str, str]]:
    rows = read_csv(path)
    if len(rows) != expected:
        raise SystemExit(f'{path}: expected {expected} review rows, got {len(rows)}')
    bad = [r for r in rows if r['review_status'] != 'REVIEWED' or r['reviewed_class'] != 'NON_SEXUAL']
    if bad:
        raise SystemExit(f'{path}: non-NON_SEXUAL review rows present: {bad[:3]}')
    return rows


def main() -> int:
    base = read_csv(BASE)
    base_summary = read_json(BASE_SUMMARY)
    inventory = read_csv(INVENTORY)
    audit = read_csv(AUDIT)
    refine = read_json(REFINE_SUMMARY)
    final_result = read_json(HOLDOUT_V2_RESULT)

    if len(base) != 31752:
        raise SystemExit(f'base row drift: {len(base)}')
    if base_summary.get('mode') != 'RESEARCH_SIDECAR_V2_EFFICIENCY_EXPANDED':
        raise SystemExit(f'unexpected base checkpoint: {base_summary.get("mode")}')
    if len(inventory) != 5845 or refine.get('candidate_rows_total') != 5845:
        raise SystemExit('wave3 inventory drift')
    if len(audit) != 3 or any(r['contradictions'] != '0' or r['safe_for_fresh_holdout'] != 'YES' for r in audit):
        raise SystemExit('existing-review exact-predicate gate failed')
    if sum(int(r['support']) for r in audit) != 68:
        raise SystemExit('existing-review support drift')
    if final_result.get('decision') != 'ELIGIBLE_FOR_RESEARCH_SIDECAR_V3':
        raise SystemExit('final holdout gate not approved for research sidecar v3')
    if final_result.get('rule_changed_after_holdout') != 'NO':
        raise SystemExit('rule changed after final holdout')
    if refine.get('prior_sample_overlap') != 0:
        raise SystemExit('fresh holdout overlap detected')

    manual_rows = (
        require_review(DISCOVERY_REVIEW, 36)
        + require_review(HOLDOUT_V1_REVIEW, 36)
        + require_review(HOLDOUT_V2_REVIEW, 36)
    )
    manual_keys = {r['identity_key'] for r in manual_rows}
    if len(manual_keys) != 108:
        raise SystemExit(f'manual wave3 identity overlap: expected 108, got {len(manual_keys)}')

    candidate_keys = {r['identity_key'] for r in inventory}
    if len(candidate_keys) != 5845:
        raise SystemExit('duplicate candidate identities in wave3 inventory')
    if not manual_keys <= candidate_keys:
        raise SystemExit(f'manual identities missing from inventory: {sorted(manual_keys - candidate_keys)[:5]}')

    index = {r['identity_key']: dict(r) for r in base}
    if len(index) != 31752:
        raise SystemExit('duplicate base identities')

    not_unclassified = [k for k in candidate_keys if index[k]['review_status'] != 'UNCLASSIFIED']
    if not_unclassified:
        raise SystemExit(f'wave3 candidate already classified in base: {not_unclassified[:5]}')

    for key in sorted(manual_keys):
        r = index[key]
        r['sexual_intent'] = 'NON_SEXUAL'
        r['review_status'] = 'HUMAN_REVIEWED'
        r['rule_id'] = ''
        r['evidence'] = MANUAL_EVIDENCE

    auto_keys = candidate_keys - manual_keys
    for key in sorted(auto_keys):
        r = index[key]
        r['sexual_intent'] = 'NON_SEXUAL'
        r['review_status'] = 'AUTO_HIGH_CONF'
        r['rule_id'] = RULE_ID
        r['evidence'] = AUTO_EVIDENCE

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {
        'AUTO_HIGH_CONF': 12417,
        'HUMAN_REVIEWED': 1032,
        'UNCLASSIFIED': 18303,
    }
    expected_classes = {
        'CONTEXTUAL': 189,
        'NON_SEXUAL': 12626,
        'NULL': 18303,
        'SEXUAL': 634,
    }
    if dict(sorted(status.items())) != expected_status:
        raise SystemExit(f'status mismatch: {dict(status)}')
    if dict(sorted(classes.items())) != expected_classes:
        raise SystemExit(f'class mismatch: {dict(classes)}')

    with OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)

    summary = {
        'issue': 118,
        'mode': 'RESEARCH_SIDECAR_V3_RISK_EXCLUSION_WAVE3',
        'identity_rows': len(rows),
        'base_checkpoint': 'RESEARCH_SIDECAR_V2_EFFICIENCY_EXPANDED',
        'new_wave3_candidates': len(candidate_keys),
        'new_wave3_human_reviewed': len(manual_keys),
        'new_wave3_auto_high_conf': len(auto_keys),
        'validation': {
            'existing_exact_predicate_nonsexual': 68,
            'existing_exact_predicate_contradictions': 0,
            'discovery_nonsexual': 36,
            'first_holdout_nonsexual': 36,
            'final_fresh_holdout_nonsexual': 36,
            'final_holdout_prior_sample_overlap': 0,
        },
        'rule': {
            'rule_id': RULE_ID,
            'risk_token_count': 118,
            'exact_exclusions': ['frogtie', 'riding_crop', 'shibarikini'],
            'paths': ['CLOTHING/ACCESSORY', 'CLOTHING/COSTUME', 'OBJECT_PROP/DAILY'],
        },
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
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
