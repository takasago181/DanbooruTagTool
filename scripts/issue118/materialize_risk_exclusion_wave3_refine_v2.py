#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v2.csv')
PILOT = Path('docs/issue118/reviews')
HOLDOUT_REVIEWS = Path('docs/issue118/holdout/reviews')
BASE = Path('docs/issue118/risk_exclusion_wave3')
RISK = BASE / 'risk_tokens_discovery_v1.txt'
DISCOVERY_SAMPLE = BASE / 'discovery_sample_v1.csv'
HOLDOUT_V1 = BASE / 'holdout_sample_v1.csv'
OUT_INV = BASE / 'refined_candidate_inventory_v2.csv'
OUT_AUDIT = BASE / 'existing_review_audit_v2.csv'
OUT_HOLDOUT = BASE / 'fresh_holdout_sample_v2.csv'
OUT_SUMMARY = BASE / 'refine_v2_summary.json'

TARGET = {'OBJECT_PROP/DAILY', 'CLOTHING/ACCESSORY', 'CLOTHING/COSTUME'}
VALID = {'SEXUAL', 'NON_SEXUAL', 'CONTEXTUAL'}
EXACT_EXCLUSIONS = {'shibarikini', 'frogtie', 'riding_crop'}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return '_'.join(v.strip().lower().replace('_', ' ').split())


def tokens(key: str) -> set[str]:
    return {x for x in re.split(r'[_()\-]+', key.lower()) if x}


def rank(key: str, lane: str) -> str:
    return hashlib.sha256(f'issue118-risk-wave3-refine-v2|{lane}|{key}'.encode()).hexdigest()


def load_reviews():
    out = []
    for cohort, directory, pattern in [
        ('PILOT', PILOT, 'chunk_???_review_v1.csv'),
        ('HOLDOUT', HOLDOUT_REVIEWS, 'chunk_*_review_v1.csv'),
    ]:
        for p in sorted(directory.glob(pattern)):
            for r in read_csv(p):
                status = (r.get('pilot_review_status') or r.get('review_status') or '').strip()
                cls = (r.get('reviewed_class') or '').strip()
                if status == 'REVIEWED' and cls in VALID:
                    out.append((norm(r['identity_key']), cls, cohort))
    return out


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def main() -> int:
    general = {norm(r['canonical']): r for r in read_csv(GENERAL)}
    sidecar = read_csv(SIDECAR)
    if len(sidecar) != 31752:
        raise SystemExit(f'sidecar drift: {len(sidecar)}')
    risk = {x.strip() for x in RISK.read_text(encoding='utf-8').splitlines() if x.strip()}

    candidates = []
    by_path: dict[str, list[dict[str, str]]] = defaultdict(list)
    risk_excluded = Counter()
    exact_excluded = Counter()
    for s in sidecar:
        if s['review_status'] != 'UNCLASSIFIED' or s['is_general'] != 'YES' or s['is_special'] != 'NO':
            continue
        key = s['identity_key']
        g = general.get(key)
        if not g:
            continue
        path = (g.get('primary_path') or '').strip()
        if path not in TARGET:
            continue
        if key in EXACT_EXCLUSIONS:
            exact_excluded[path] += 1
            continue
        if tokens(key) & risk:
            risk_excluded[path] += 1
            continue
        row = {
            'identity_key': key,
            'general_path': path,
            'general_status': g.get('classification_status', ''),
            'general_confidence': g.get('confidence', ''),
            'token_count': str(len(tokens(key))),
        }
        candidates.append(row); by_path[path].append(row)

    review_counts = defaultdict(Counter)
    review_excluded = Counter()
    for key, cls, cohort in load_reviews():
        g = general.get(key)
        if not g:
            continue
        path = (g.get('primary_path') or '').strip()
        if path not in TARGET:
            continue
        if key in EXACT_EXCLUSIONS or tokens(key) & risk:
            review_excluded[path] += 1
            continue
        review_counts[path][cls] += 1

    audit_rows = []
    for path in sorted(TARGET):
        c = review_counts[path]
        support = sum(c.values())
        contradictions = c['SEXUAL'] + c['CONTEXTUAL']
        audit_rows.append({
            'general_path': path,
            'nonsexual': str(c['NON_SEXUAL']),
            'sexual': str(c['SEXUAL']),
            'contextual': str(c['CONTEXTUAL']),
            'support': str(support),
            'contradictions': str(contradictions),
            'excluded_review_rows': str(review_excluded[path]),
            'safe_for_fresh_holdout': 'YES' if support >= 3 and contradictions == 0 else 'NO',
        })

    if any(r['safe_for_fresh_holdout'] != 'YES' for r in audit_rows):
        raise SystemExit(f'refined exact predicate still has contradictions: {audit_rows}')

    seen = {r['identity_key'] for r in read_csv(DISCOVERY_SAMPLE)} | {r['identity_key'] for r in read_csv(HOLDOUT_V1)}
    fresh_holdout = []
    for path in sorted(TARGET):
        rows = [r for r in by_path[path] if r['identity_key'] not in seen]
        if len(rows) < 24:
            raise SystemExit(f'not enough fresh refined rows for {path}: {len(rows)}')
        chosen: dict[str, tuple[dict[str, str], str]] = {}
        for r in sorted(rows, key=lambda x: rank(x['identity_key'], 'random'))[:6]:
            chosen[r['identity_key']] = (r, 'HASH_RANDOM')
        remaining = [r for r in rows if r['identity_key'] not in chosen]
        remaining.sort(key=lambda x: (-int(x['token_count']), rank(x['identity_key'], 'compound')))
        for r in remaining[:6]:
            chosen[r['identity_key']] = (r, 'COMPOUND_CHALLENGE')
        for key, (r, lane) in sorted(chosen.items(), key=lambda kv: rank(kv[0], 'output')):
            fresh_holdout.append({
                **r,
                'candidate_rows_in_path': str(len(by_path[path])),
                'sample_lane': lane,
                'candidate_class': 'NON_SEXUAL',
                'phase': 'FRESH_HOLDOUT_WAVE3_V2',
                'reviewed_class': '',
                'review_note': '',
            })

    overlap = {r['identity_key'] for r in fresh_holdout} & seen
    if overlap:
        raise SystemExit(f'prior-sample overlap: {sorted(overlap)}')

    inv_fields = ['identity_key', 'general_path', 'general_status', 'general_confidence', 'token_count']
    write_csv(OUT_INV, sorted(candidates, key=lambda r: (r['general_path'], r['identity_key'])), inv_fields)
    write_csv(OUT_AUDIT, audit_rows, list(audit_rows[0]))
    holdout_fields = inv_fields + ['candidate_rows_in_path', 'sample_lane', 'candidate_class', 'phase', 'reviewed_class', 'review_note']
    write_csv(OUT_HOLDOUT, fresh_holdout, holdout_fields)

    summary = {
        'issue': 118,
        'mode': 'RISK_EXCLUSION_WAVE3_REFINE_V2',
        'exact_exclusions': sorted(EXACT_EXCLUSIONS),
        'frozen_risk_token_count': len(risk),
        'candidate_rows_total': len(candidates),
        'candidate_rows_by_path': {p: len(by_path[p]) for p in sorted(TARGET)},
        'risk_excluded_by_path': {p: risk_excluded[p] for p in sorted(TARGET)},
        'exact_excluded_by_path': {p: exact_excluded[p] for p in sorted(TARGET)},
        'existing_review_safe_paths': [r['general_path'] for r in audit_rows if r['safe_for_fresh_holdout'] == 'YES'],
        'fresh_holdout_rows': len(fresh_holdout),
        'prior_sample_overlap': len(overlap),
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
