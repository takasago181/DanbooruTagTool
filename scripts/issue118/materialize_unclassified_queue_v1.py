#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

SIDECAR = Path('docs/issue118/research_sidecar_v1.csv')
GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL = Path('data/generation/special2788_generation_profile.csv')
ISSUE104 = Path('docs/issue104/product_fit_review_v1.csv')
OUT_DIR = Path('docs/issue118/coverage_queue_v1')
QUEUE_SIZE = 1000
SEED = 'issue118-coverage-queue-v1'
RISK_ROOTS = {
    'ACTION_CONTACT','BODY_PART','CLOTHING_STATE_EXPOSURE','OBJECT_PROP',
    'CLOTHING','POSE_MOVEMENT','EXPRESSION_EMOTION','COLOR_APPEARANCE',
    'GAZE_ORIENTATION','STYLE_QUALITY_META'
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return '_'.join(v.strip().lower().replace('_',' ').split())


def stable_rank(key: str) -> str:
    return hashlib.sha256(f'{SEED}|{key}'.encode()).hexdigest()


def main() -> int:
    sidecar = read_csv(SIDECAR)
    general = read_csv(GENERAL)
    special = read_csv(SPECIAL)
    issue104 = read_csv(ISSUE104)
    if len(sidecar) != 31752 or len(general) != 30629 or len(special) != 3059:
        raise SystemExit('input population drift')

    g = {norm(r['canonical']): r for r in general}
    s = {norm(r['Tag']): r for r in special}
    risk = {norm(r['canonical_tag']) for r in issue104}

    candidates = []
    band_counts = Counter()
    for r in sidecar:
        if r['review_status'] != 'UNCLASSIFIED':
            continue
        key = r['identity_key']
        gr = g.get(key)
        sr = s.get(key)
        primary = (gr or {}).get('primary_path','').strip()
        root = primary.split('/',1)[0] if primary else ''
        evidence = r.get('evidence','')
        if evidence.endswith(':UNRESOLVED'):
            band = 'P0_PREVIOUSLY_REVIEWED_UNRESOLVED'
        elif sr is not None:
            band = 'P1_SPECIAL_OR_OVERLAP'
        elif key in risk:
            band = 'P2_ISSUE104_RISK'
        elif root in RISK_ROOTS:
            band = 'P3_GENERAL_RISK_ROOT'
        else:
            band = 'P4_REMAINDER'
        band_counts[band] += 1
        candidates.append({
            'identity_key': key,
            'priority_band': band,
            'is_general': 'YES' if gr is not None else 'NO',
            'is_special': 'YES' if sr is not None else 'NO',
            'general_primary_path': primary,
            'general_status': (gr or {}).get('status',''),
            'general_confidence': (gr or {}).get('confidence',''),
            'special_id': (sr or {}).get('SpecialID',''),
            'generation_family': (sr or {}).get('GenerationFamily',''),
            'generation_role': (sr or {}).get('GenerationRole',''),
            'issue104_risk': 'YES' if key in risk else 'NO',
            'prior_evidence': evidence,
            'sample_rank': stable_rank(key),
            'reviewed_class': '',
            'review_status': '',
            'review_reason': '',
        })

    order = {
        'P0_PREVIOUSLY_REVIEWED_UNRESOLVED':0,
        'P1_SPECIAL_OR_OVERLAP':1,
        'P2_ISSUE104_RISK':2,
        'P3_GENERAL_RISK_ROOT':3,
        'P4_REMAINDER':4,
    }
    candidates.sort(key=lambda r: (order[r['priority_band']], r['sample_rank']))
    queue = candidates[:QUEUE_SIZE]
    if len(queue) != QUEUE_SIZE:
        raise SystemExit(f'queue too small: {len(queue)}')

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / 'unclassified_review_queue_1000_v1.csv'
    fields = list(queue[0])
    with out.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader(); w.writerows(queue)

    for old in OUT_DIR.glob('chunk_*.csv'):
        old.unlink()
    compact_fields = ['identity_key','priority_band','is_general','is_special','general_primary_path','special_id','generation_family','issue104_risk']
    for i in range(0, QUEUE_SIZE, 100):
        p = OUT_DIR / f'chunk_{i//100+1:03d}.csv'
        with p.open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=compact_fields, lineterminator='\n')
            w.writeheader()
            for row in queue[i:i+100]:
                w.writerow({k: row[k] for k in compact_fields})

    selected = Counter(r['priority_band'] for r in queue)
    summary = {
        'issue':118,
        'mode':'UNCLASSIFIED_COVERAGE_QUEUE_V1',
        'source_unclassified_rows':sum(band_counts.values()),
        'queue_rows':len(queue),
        'source_band_counts':dict(sorted(band_counts.items())),
        'selected_band_counts':dict(sorted(selected.items())),
        'queue_chunks':10,
        'production_authority':'NO',
        'main_mutated':'NO',
        'issue117_code_mutated':'NO',
    }
    (OUT_DIR/'summary_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
