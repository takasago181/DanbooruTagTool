#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v14.csv')
OUT = Path('docs/issue118/clothing_accessory_review_v27')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace('_', ' ').split())


def main() -> int:
    general = read_csv(GENERAL)
    side = read_csv(SIDECAR)
    g = {norm(r['canonical']): r for r in general}

    rows = []
    for r in side:
        if r['review_status'] != 'UNCLASSIFIED' or r.get('is_special') == 'YES':
            continue
        key = r['identity_key']
        gr = g.get(key)
        if gr is None:
            continue
        path = (gr.get('primary_path') or '').strip()
        if path != 'CLOTHING/ACCESSORY':
            continue
        parts = set(key.lower().replace('-', '_').split('_'))
        risk = {'sex','sexual','penis','pussy','vagina','anus','anal','clit','nipple','breast','panty','panties','bra','underwear','fetish','bdsm','bondage','condom','dildo','vibrator','gag','rope','leash','handcuff','handcuffs'}
        if parts & risk:
            continue
        rows.append({'identity_key': key, 'candidate_state': 'FULL_REVIEW_CLOTHING_ACCESSORY_V27', 'human_intent': '', 'review_note': ''})

    rows.sort(key=lambda r: r['identity_key'])
    if len(rows) != 178:
        raise SystemExit(f'expected 178 General-only CLOTHING/ACCESSORY review rows, got {len(rows)}')

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'full_review_candidate_v27.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['identity_key','candidate_state','human_intent','review_note'], lineterminator='\n')
        w.writeheader(); w.writerows(rows)
    summary = {
        'issue': 118,
        'mode': 'CLOTHING_ACCESSORY_FULL_REVIEW_V27',
        'candidate_rows': len(rows),
        'selection_rules_use': 'DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY',
        'auto_promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
        'catalog_mutated': 'NO',
        'user_db_mutated': 'NO',
        'next_gate': 'full manual review of all 178 rows'
    }
    (OUT / 'summary_v27.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
