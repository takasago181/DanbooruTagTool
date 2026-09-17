#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v13.csv')
OUT = Path('docs/issue118/object_prop_low_risk_v26')

RISK = re.compile(
    r'(?:^|_)(?:ass|butt|boob|breast|nipple|panty|panties|bra|underwear|lingerie|condom|dildo|vibrator|onahole|'
    r'sex|sexual|erotic|porn|fetish|bdsm|chastity|gag|bondage|rope|leash|speculum|penis|cock|dick|pussy|vagina|'
    r'anal|anus|clit|crotch|genital|semen|cum|masturbat|aphrodisiac|clothes[-_]?dissolving)(?:_|$)'
)


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace('_', ' ').split())


def stable_rank(key: str) -> str:
    return hashlib.sha256(('issue118-object-v26-holdout|' + key).encode('utf-8')).hexdigest()


def main() -> int:
    general = read_csv(GENERAL)
    side = read_csv(SIDECAR)
    g = {norm(r['canonical']): r for r in general}

    selected = []
    residual = []
    path_counts = Counter()
    for r in side:
        if r['review_status'] != 'UNCLASSIFIED' or r.get('is_special') == 'YES':
            continue
        key = r['identity_key']
        gr = g.get(key)
        if gr is None:
            continue
        path = (gr.get('primary_path') or '').strip()
        if not (path == 'OBJECT_PROP' or path.startswith('OBJECT_PROP/')):
            continue
        if RISK.search(key.lower()):
            residual.append({'identity_key': key, 'general_path': path, 'state': 'OBJECT_PROP_BOUNDARY_UNCLASSIFIED_V26'})
        else:
            selected.append({'identity_key': key, 'general_path': path, 'state': 'OBJECT_PROP_LOW_RISK_CANDIDATE_V26'})
            path_counts[path] += 1

    selected.sort(key=lambda r: (r['general_path'], r['identity_key']))
    residual.sort(key=lambda r: (r['general_path'], r['identity_key']))
    total = len(selected) + len(residual)
    if total != 161:
        raise SystemExit(f'expected 161 remaining General-only OBJECT_PROP rows, got {total}')

    holdout_n = min(120, len(selected))
    holdout_keys = sorted((r['identity_key'] for r in selected), key=stable_rank)[:holdout_n]
    holdout = [
        {'identity_key': key, 'candidate_state': 'OBJECT_PROP_LOW_RISK_HOLDOUT_V26', 'human_intent': '', 'review_note': ''}
        for key in holdout_keys
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'low_risk_candidate_v26.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','general_path','state'], lineterminator='\n')
        w.writeheader(); w.writerows(selected)
    with (OUT / 'boundary_residual_v26.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','general_path','state'], lineterminator='\n')
        w.writeheader(); w.writerows(residual)
    with (OUT / 'fresh_holdout_template_v26.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader(); w.writerows(holdout)

    summary = {
        'issue': 118,
        'mode': 'OBJECT_PROP_LOW_RISK_V26',
        'source_rows': total,
        'low_risk_candidate_rows': len(selected),
        'boundary_residual_rows': len(residual),
        'candidate_path_counts': dict(sorted(path_counts.items())),
        'fresh_holdout_template_rows': len(holdout),
        'risk_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review fixed holdout; if clean, promote only low-risk object-prop candidate set'
    }
    (OUT / 'summary_v26.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
