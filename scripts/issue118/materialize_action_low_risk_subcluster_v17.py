#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SRC = Path('docs/issue118/action_interaction_refinement_v16_10/ordinary_clean_v16_10.csv')
OUT = Path('docs/issue118/action_low_risk_subcluster_v17')

# Conservative ejector only. Matching rows remain UNCLASSIFIED; this is not a semantic classifier.
RELATION_OR_BODY_TOKENS = {
    'another','anothers','someone','someones','person','viewer','body','bodies','ass','butt','chest',
    'pectoral','pectorals','breast','breasts','thigh','thighs','leg','legs','foot','feet','toe','toes',
    'nape','neck','back','stomach','belly','navel','waist','hip','hips','crotch','bulge','lips','tongue',
    'mouth','armpit','armpits','shoulder','shoulders','arm','arms','hand','hands','finger','fingers',
    'wrist','wrists','face','cheek','cheeks','chin','head','hair',
}
INTIMATE_CONTEXT_TOKENS = {
    'kiss','kissing','hug','hugging','cuddle','cuddling','snuggle','snuggling','caress','caressing',
    'massage','massaging','lick','licking','bite','biting','touch','touching','fondle','fondling',
    'bed','sleeping','sleepover','date','dating','romance','romantic','strip','wedgie','twerk','twerking',
    'panty','panties','underwear','bra','buruma','bikini','swimsuit','pantyhose','thong','fetish','slut',
    'horny','lewd','erotic','ero','ecchi',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def tokens(key: str) -> set[str]:
    return {p for p in re.split(r'[^a-z0-9]+', key.lower()) if p}


def residual_flags(key: str) -> list[str]:
    t = tokens(key)
    flags = []
    if t & RELATION_OR_BODY_TOKENS:
        flags.append('relation_or_body_token')
    if t & INTIMATE_CONTEXT_TOKENS:
        flags.append('intimate_or_boundary_token')
    return flags


def holdout_rank(key: str) -> str:
    return hashlib.sha256(('issue118-v17-action-low-risk-holdout:' + key).encode('utf-8')).hexdigest()


def main() -> int:
    src = read_csv(SRC)
    if len(src) != 1509:
        raise SystemExit(f'expected v16.10 ordinary clean population 1509, got {len(src)}')

    low_risk, residual = [], []
    counts = Counter()
    for r in src:
        key = r['identity_key']
        hit = residual_flags(key)
        out = {
            'identity_key': key,
            'candidate_state': 'RESIDUAL_UNCLASSIFIED' if hit else 'LOW_RISK_CANDIDATE',
            'risk_flags': '|'.join(hit),
        }
        if hit:
            residual.append(out)
            counts.update(hit)
        else:
            low_risk.append(out)

    low_risk.sort(key=lambda r: r['identity_key'])
    residual.sort(key=lambda r: r['identity_key'])
    holdout = sorted(low_risk, key=lambda r: (holdout_rank(r['identity_key']), r['identity_key']))[:120]
    if len(holdout) != 120:
        raise SystemExit('not enough low-risk rows for v17 holdout')

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['identity_key','candidate_state','risk_flags']
    for name, rows in [('low_risk_candidate_v17.csv', low_risk), ('residual_unclassified_v17.csv', residual)]:
        with (OUT / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)

    with (OUT / 'fresh_holdout_template_v17.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n'); w.writeheader()
        for r in holdout:
            w.writerow({'identity_key': r['identity_key'], 'candidate_state': 'LOW_RISK_HOLDOUT_V17', 'human_intent': '', 'review_note': ''})

    summary = {
        'issue': 118,
        'mode': 'ACTION_LOW_RISK_SUBCLUSTER_V17',
        'source_rows_v16_10': len(src),
        'low_risk_candidate_rows': len(low_risk),
        'residual_unclassified_rows': len(residual),
        'residual_flag_counts': dict(sorted(counts.items())),
        'fresh_holdout_template_rows': len(holdout),
        'selection_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'holdout_verdicts_generated': 'NO',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'independently review fixed 120-row low-risk holdout; promote only low-risk candidate set if clean',
    }
    (OUT / 'summary_v17.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
