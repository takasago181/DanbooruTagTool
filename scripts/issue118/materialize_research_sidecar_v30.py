#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v29.csv')
INPUTS = [
    {
        'label': 'V52',
        'review': Path('docs/issue118/everyday_restraint_flag_review_v52/review_policy_v52.json'),
        'candidate': Path('docs/issue118/everyday_restraint_flag_review_v52/full_review_candidate_v52.csv'),
        'rows': 34,
        'review_blob': '5c454e0f7b86ff9785948fbf8fd01113e89bc28a',
        'candidate_blob': 'e5f0ff36fed6ad700a2994ec926752f9a336406d',
    },
    {
        'label': 'V54',
        'review': Path('docs/issue118/general_three_cluster_review_v54/review_policy_v54.json'),
        'candidate': Path('docs/issue118/general_three_cluster_review_v54/full_review_candidate_v54.csv'),
        'rows': 72,
        'review_blob': '0dd8de749730715d60d740044ca78e514958d319',
        'candidate_blob': '4f418f1220703cca42152b56587bb3f2e86fd5dd',
    },
]
OUT = Path('docs/issue118/research_sidecar_v30.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v30.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def groups(review: dict, source_set: set[str]):
    counts = review['decision_counts']
    g = {
        'SEXUAL': set(review.get('sexual') or []),
        'CONTEXTUAL': set(review.get('contextual') or []),
        'NON_SEXUAL': set(review.get('non_sexual') or []),
    }
    union = set()
    for intent, keys in g.items():
        if not keys <= source_set:
            raise SystemExit(f'{intent} outside source')
        if union & keys:
            raise SystemExit('review groups overlap')
        union |= keys
    missing = source_set - union
    deficits = {intent: int(counts[intent]) - len(g[intent]) for intent in g}
    if any(v < 0 for v in deficits.values()):
        raise SystemExit(f'negative deficit {deficits}')
    positive = [intent for intent, v in deficits.items() if v > 0]
    if missing:
        if len(positive) != 1 or deficits[positive[0]] != len(missing):
            raise SystemExit(f'cannot infer omitted group: missing={len(missing)} deficits={deficits}')
        g[positive[0]] |= missing
    elif positive:
        raise SystemExit(f'counts require missing rows: {deficits}')
    if {intent: len(keys) for intent, keys in g.items()} != counts:
        raise SystemExit('review count drift')
    return g


def main() -> int:
    base = read_csv(BASE)
    if len(base) != 31752:
        raise SystemExit(f'base drift {len(base)}')
    index = {r['identity_key']: dict(r) for r in base}
    promoted = Counter()
    seen = set()
    review_inputs = []

    for cfg in INPUTS:
        label = cfg['label']
        rp = cfg['review']
        cp = cfg['candidate']
        n = cfg['rows']
        if git_blob_sha(rp) != cfg['review_blob']:
            raise SystemExit(f'{label} fixed review blob SHA drift')
        if git_blob_sha(cp) != cfg['candidate_blob']:
            raise SystemExit(f'{label} fixed candidate blob SHA drift')
        source = read_csv(cp)
        review = json.loads(rp.read_text(encoding='utf-8'))
        if len(source) != n or review.get('source_rows') != n:
            raise SystemExit(f'{label} source count drift')
        if review.get('review_verdicts_generated_by_materializer') != 'NO':
            raise SystemExit(f'{label} provenance drift: generated verdicts')
        if review.get('review_artifacts_are_external_inputs') != 'YES':
            raise SystemExit(f'{label} provenance drift: external input flag')
        source_set = {r['identity_key'] for r in source}
        if seen & source_set:
            raise SystemExit('review input overlap')
        seen |= source_set
        gg = groups(review, source_set)
        for intent, keys in gg.items():
            for key in sorted(keys):
                target = index.get(key)
                if target is None or target['review_status'] != 'UNCLASSIFIED' or target['sexual_intent']:
                    raise SystemExit(f'{label} not cleanly unclassified: {key}')
                target['sexual_intent'] = intent
                target['review_status'] = 'HUMAN_REVIEWED'
                target['rule_id'] = f'HUMAN_{intent}_{label}'
                target['evidence'] = f'full semantic review of fixed {label} candidate set'
                promoted[intent] += 1
        review_inputs.append({
            'label': label,
            'review_source': str(rp),
            'review_git_blob_sha': cfg['review_blob'],
            'review_sha256': sha256(rp),
            'candidate_source': str(cp),
            'candidate_git_blob_sha': cfg['candidate_blob'],
            'source_rows': n,
        })

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)
    expected_status = {'AUTO_HIGH_CONF': 22371, 'HUMAN_REVIEWED': 3543, 'UNCLASSIFIED': 5838}
    expected_classes = {'CONTEXTUAL': 971, 'NON_SEXUAL': 23495, 'NULL': 5838, 'SEXUAL': 1448}
    if dict(sorted(status.items())) != expected_status:
        raise SystemExit(f'status mismatch {dict(status)}')
    if dict(sorted(classes.items())) != expected_classes:
        raise SystemExit(f'class mismatch {dict(classes)}')

    with OUT.open('w', encoding='utf-8', newline='') as f:
        fields = list(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

    summary = {
        'issue': 118,
        'mode': 'RESEARCH_SIDECAR_V30_V52_V54_FULL_REVIEWS',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'new_promotions': dict(sorted(promoted.items())),
        'new_total_promotions': sum(promoted.values()),
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'review_inputs': review_inputs,
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
