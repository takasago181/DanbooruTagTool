#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path('docs/issue118/research_sidecar_v34.csv')
CORRECTION = Path('docs/issue118/mixed_five_cluster_review_v59/review_correction_v59a.json')
CORRECTION_BLOB = '4d4f431d000f3ae53e63d0cfc836fe0113817da5'
OUT = Path('docs/issue118/research_sidecar_v35.csv')
SUMMARY = Path('docs/issue118/research_sidecar_summary_v35.json')


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def main() -> int:
    if git_blob_sha(CORRECTION) != CORRECTION_BLOB:
        raise SystemExit('V59A fixed correction blob SHA drift')

    base = read_csv(BASE)
    correction = json.loads(CORRECTION.read_text(encoding='utf-8'))
    if len(base) != 31752:
        raise SystemExit(f'base drift {len(base)}')
    if correction.get('review_verdicts_generated_by_materializer') != 'NO':
        raise SystemExit('V59A provenance drift: generated verdicts')
    if correction.get('review_artifacts_are_external_inputs') != 'YES':
        raise SystemExit('V59A provenance drift: external input flag')

    index = {r['identity_key']: dict(r) for r in base}
    expected_keys = {'futanari','full-package_futanari','male_futanari'}
    rows_correction = correction.get('corrections') or []
    if {x['identity_key'] for x in rows_correction} != expected_keys:
        raise SystemExit('V59A correction key drift')

    for item in rows_correction:
        key = item['identity_key']
        target = index.get(key)
        if target is None:
            raise SystemExit(f'missing correction target: {key}')
        if target['review_status'] != 'HUMAN_REVIEWED':
            raise SystemExit(f'correction target not human-reviewed: {key}')
        if target['sexual_intent'] != item['from']:
            raise SystemExit(f'correction source mismatch for {key}: {target["sexual_intent"]}')
        if item['to'] != 'SEXUAL':
            raise SystemExit(f'unexpected correction target class: {key}')
        target['sexual_intent'] = 'SEXUAL'
        target['rule_id'] = 'HUMAN_SEXUAL_V59A_CORRECTION'
        target['evidence'] = 'manual correction of V59 futanari intent classification'

    rows = [index[r['identity_key']] for r in base]
    status = Counter(r['review_status'] for r in rows)
    classes = Counter(r['sexual_intent'] or 'NULL' for r in rows)

    expected_status = {'AUTO_HIGH_CONF': 22371, 'HUMAN_REVIEWED': 3873, 'UNCLASSIFIED': 5508}
    expected_classes = {'CONTEXTUAL': 1070, 'NON_SEXUAL': 23559, 'NULL': 5508, 'SEXUAL': 1615}
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
        'mode': 'RESEARCH_SIDECAR_V35_V59A_CORRECTION',
        'identity_rows': len(rows),
        'source_base': str(BASE),
        'correction_count': 3,
        'corrected_keys': sorted(expected_keys),
        'review_status_counts': dict(sorted(status.items())),
        'sexual_intent_counts': dict(sorted(classes.items())),
        'remaining_unclassified': status['UNCLASSIFIED'],
        'correction_source': str(CORRECTION),
        'correction_git_blob_sha': CORRECTION_BLOB,
        'correction_sha256': sha256(CORRECTION),
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
