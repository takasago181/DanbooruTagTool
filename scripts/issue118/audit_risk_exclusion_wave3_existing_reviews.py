#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
PILOT = Path('docs/issue118/reviews')
HOLDOUT = Path('docs/issue118/holdout/reviews')
RISK = Path('docs/issue118/risk_exclusion_wave3/risk_tokens_discovery_v1.txt')
OUT = Path('docs/issue118/risk_exclusion_wave3')
TARGET = {'OBJECT_PROP/DAILY', 'CLOTHING/ACCESSORY', 'CLOTHING/COSTUME'}
VALID = {'SEXUAL', 'NON_SEXUAL', 'CONTEXTUAL'}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return '_'.join(v.strip().lower().replace('_', ' ').split())


def tokens(key: str) -> set[str]:
    return {x for x in re.split(r'[_()\-]+', key.lower()) if x}


def load_reviews():
    out = []
    for cohort, directory, pattern in [
        ('PILOT', PILOT, 'chunk_???_review_v1.csv'),
        ('HOLDOUT', HOLDOUT, 'chunk_*_review_v1.csv'),
    ]:
        for p in sorted(directory.glob(pattern)):
            for r in read_csv(p):
                status = (r.get('pilot_review_status') or r.get('review_status') or '').strip()
                cls = (r.get('reviewed_class') or '').strip()
                if status == 'REVIEWED' and cls in VALID:
                    out.append((norm(r['identity_key']), cls, cohort, p.name))
    return out


def main() -> int:
    general = {norm(r['canonical']): r for r in read_csv(GENERAL)}
    risk = {x.strip() for x in RISK.read_text(encoding='utf-8').splitlines() if x.strip()}
    reviews = load_reviews()

    counts = defaultdict(lambda: defaultdict(Counter))
    evidence = []
    excluded = Counter()

    for key, cls, cohort, source in reviews:
        g = general.get(key)
        if not g:
            continue
        path = (g.get('primary_path') or '').strip()
        if path not in TARGET:
            continue
        hits = sorted(tokens(key) & risk)
        if hits:
            excluded[path] += 1
            continue
        counts[path][cohort][cls] += 1
        evidence.append({
            'identity_key': key,
            'general_path': path,
            'cohort': cohort,
            'reviewed_class': cls,
            'source_file': source,
        })

    rows = []
    safe_paths = []
    contradiction_rows = []
    for path in sorted(TARGET):
        p = counts[path]['PILOT']
        h = counts[path]['HOLDOUT']
        total = p + h
        contradictions = total['SEXUAL'] + total['CONTEXTUAL']
        support = sum(total.values())
        if support >= 3 and contradictions == 0 and total['NON_SEXUAL'] == support:
            safe_paths.append(path)
        rows.append({
            'general_path': path,
            'pilot_nonsexual': str(p['NON_SEXUAL']),
            'pilot_sexual': str(p['SEXUAL']),
            'pilot_contextual': str(p['CONTEXTUAL']),
            'holdout_nonsexual': str(h['NON_SEXUAL']),
            'holdout_sexual': str(h['SEXUAL']),
            'holdout_contextual': str(h['CONTEXTUAL']),
            'exact_predicate_support': str(support),
            'contradictions': str(contradictions),
            'risk_excluded_review_rows': str(excluded[path]),
            'safe_for_next_gate': 'YES' if path in safe_paths else 'NO',
        })

    for r in evidence:
        if r['reviewed_class'] in {'SEXUAL', 'CONTEXTUAL'}:
            contradiction_rows.append(r)

    OUT.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with (OUT / 'existing_review_audit_v1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader(); w.writerows(rows)
    contradiction_fields = ['identity_key', 'general_path', 'cohort', 'reviewed_class', 'source_file']
    with (OUT / 'existing_review_contradictions_v1.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=contradiction_fields, lineterminator='\n')
        w.writeheader(); w.writerows(contradiction_rows)

    summary = {
        'issue': 118,
        'mode': 'RISK_EXCLUSION_WAVE3_EXISTING_REVIEW_AUDIT',
        'loaded_review_rows': len(reviews),
        'frozen_risk_token_count': len(risk),
        'target_paths': sorted(TARGET),
        'safe_paths': safe_paths,
        'safe_path_count': len(safe_paths),
        'contradiction_rows': len(contradiction_rows),
        'promotion_performed': 'NO',
        'production_authority': 'NO',
        'main_mutated': 'NO',
        'issue117_code_mutated': 'NO',
    }
    (OUT / 'existing_review_audit_summary_v1.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
