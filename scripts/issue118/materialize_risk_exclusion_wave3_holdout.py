#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

BASE = Path('docs/issue118/risk_exclusion_wave3')
INVENTORY = BASE / 'candidate_inventory_discovery_v1.csv'
DISCOVERY = BASE / 'discovery_sample_v1.csv'
DISCOVERY_REVIEW = BASE / 'discovery_review_v1.csv'
DISCOVERY_RESULT = BASE / 'discovery_result_v1.json'
RISK = BASE / 'risk_tokens_discovery_v1.txt'
OUT_SAMPLE = BASE / 'holdout_sample_v1.csv'
OUT_SUMMARY = BASE / 'summary_holdout_v1.json'
TARGET_PATHS = {'OBJECT_PROP/DAILY', 'CLOTHING/ACCESSORY', 'CLOTHING/COSTUME'}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def rank(key: str, lane: str) -> str:
    return hashlib.sha256(f'issue118-risk-wave3-holdout|{lane}|{key}'.encode()).hexdigest()


def main() -> int:
    inventory = read_csv(INVENTORY)
    discovery = read_csv(DISCOVERY)
    review = read_csv(DISCOVERY_REVIEW)
    result = json.loads(DISCOVERY_RESULT.read_text(encoding='utf-8'))
    frozen_risk = [x.strip() for x in RISK.read_text(encoding='utf-8').splitlines() if x.strip()]

    if len(discovery) != 36 or len(review) != 36:
        raise SystemExit('discovery evidence drift')
    if {r['identity_key'] for r in discovery} != {r['identity_key'] for r in review}:
        raise SystemExit('discovery/review identity mismatch')
    if any(r['review_status'] != 'REVIEWED' or r['reviewed_class'] != 'NON_SEXUAL' for r in review):
        raise SystemExit('discovery gate not pure NON_SEXUAL')
    if result.get('decision') != 'FREEZE_RULE_AND_GENERATE_FRESH_HOLDOUT':
        raise SystemExit('discovery decision not frozen for holdout')
    if result.get('risk_rule_changed_after_discovery') != 'NO':
        raise SystemExit('risk rule changed after discovery')

    seen = {r['identity_key'] for r in discovery}
    by_path: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in inventory:
        if r['identity_key'] in seen:
            continue
        if r['general_path'] in TARGET_PATHS:
            by_path[r['general_path']].append(r)

    holdout: list[dict[str, str]] = []
    for path in sorted(TARGET_PATHS):
        rows = by_path[path]
        if len(rows) < 24:
            raise SystemExit(f'not enough fresh candidates for {path}: {len(rows)}')

        chosen: dict[str, tuple[dict[str, str], str]] = {}
        for r in sorted(rows, key=lambda x: rank(x['identity_key'], 'random'))[:6]:
            chosen[r['identity_key']] = (r, 'HASH_RANDOM')

        remaining = [r for r in rows if r['identity_key'] not in chosen]
        remaining.sort(key=lambda x: (-int(x['token_count']), rank(x['identity_key'], 'compound')))
        for r in remaining[:6]:
            chosen[r['identity_key']] = (r, 'COMPOUND_CHALLENGE')

        if len(chosen) != 12:
            raise SystemExit(f'holdout sample drift for {path}: {len(chosen)}')
        for key, (r, lane) in sorted(chosen.items(), key=lambda kv: rank(kv[0], 'output')):
            holdout.append({
                **r,
                'candidate_rows_in_path': str(len(rows)),
                'sample_lane': lane,
                'candidate_class': 'NON_SEXUAL',
                'phase': 'FRESH_HOLDOUT_WAVE3',
                'reviewed_class': '',
                'review_note': '',
            })

    overlap = {r['identity_key'] for r in holdout} & seen
    if overlap:
        raise SystemExit(f'discovery/holdout overlap: {sorted(overlap)}')

    fields = [
        'identity_key', 'general_path', 'general_status', 'general_confidence',
        'token_count', 'candidate_rows_in_path', 'sample_lane', 'candidate_class',
        'phase', 'reviewed_class', 'review_note',
    ]
    with OUT_SAMPLE.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(holdout)

    summary = {
        'issue': 118,
        'mode': 'RISK_EXCLUSION_WAVE3_FRESH_HOLDOUT',
        'target_paths': sorted(TARGET_PATHS),
        'frozen_risk_token_count': len(frozen_risk),
        'discovery_review_rows': len(review),
        'discovery_nonsexual_rows': sum(r['reviewed_class'] == 'NON_SEXUAL' for r in review),
        'holdout_rows': len(holdout),
        'discovery_holdout_overlap': len(overlap),
        'rule_frozen_before_holdout': 'YES',
        'promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
    }
    OUT_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
