#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path

EXPECTED_BASE = 2983
EXPECTED_NEW = 105
FIRST_NEW_ID = 2984
LAST_NEW_ID = 3088


def norm(value: str) -> str:
    return ' '.join(unicodedata.normalize('NFKC', value).strip().lower().replace('_', ' ').split())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidates', required=True)
    ap.add_argument('--profile', required=True)
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()

    candidate_path = Path(args.candidates)
    profile_path = Path(args.profile)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = read_csv(candidate_path)
    profile = read_csv(profile_path)

    if len(candidates) != EXPECTED_NEW:
        raise ValueError(f'Issue #104 candidate count must be {EXPECTED_NEW}, got {len(candidates)}')
    if len(profile) != EXPECTED_BASE:
        raise ValueError(f'accepted Special profile must be {EXPECTED_BASE}, got {len(profile)}')

    ids = [int(r['SpecialID']) for r in profile]
    if ids != list(range(1, EXPECTED_BASE + 1)):
        raise ValueError('accepted Special profile IDs are not contiguous 1..2983')

    if any(r.get('product_fit_decision') != 'SPECIAL_CANDIDATE' for r in candidates):
        raise ValueError('candidate source contains a non-SPECIAL_CANDIDATE row')

    tags = [r['canonical_tag'] for r in candidates]
    if len(set(tags)) != EXPECTED_NEW:
        raise ValueError('Issue #104 candidate canonical tags are not unique')
    normalized_tags = [norm(t) for t in tags]
    if len(set(normalized_tags)) != EXPECTED_NEW:
        raise ValueError('Issue #104 candidate tags collide after underscore/space normalization')

    existing = {norm(r['Tag']): r for r in profile}
    overlaps = sorted(tag for tag in tags if norm(tag) in existing)
    if overlaps:
        raise ValueError(f'Issue #104 candidates overlap current accepted Special: {overlaps}')

    rows: list[dict[str, object]] = []
    for offset, row in enumerate(candidates):
        sid = FIRST_NEW_ID + offset
        count = int(row['post_count'])
        rows.append({
            'proposed_special_id': sid,
            'canonical_tag': row['canonical_tag'],
            'canonical_aliases': row.get('aliases', ''),
            'frozen_post_count_2026_09_02': count,
            'proposed_layer': 'Core' if count >= 1000 else 'Extended',
            'adult_domains': row.get('canonical_adult_domains', ''),
            'review_source': row.get('review_source', ''),
            'source_issue104_merge': '0e165d02c4715fedbd28b49525276294d0cd8ee3',
            'metadata_status': 'PENDING_PRODUCT_METADATA',
        })

    proposed_ids = [int(r['proposed_special_id']) for r in rows]
    if proposed_ids != list(range(FIRST_NEW_ID, LAST_NEW_ID + 1)):
        raise ValueError('proposed IDs are not exactly 2984..3088')

    fields = list(rows[0].keys())
    proposal = out_dir / 'promotion_preflight_v1.csv'
    with proposal.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    layer_counts = Counter(str(r['proposed_layer']) for r in rows)
    summary = {
        'mode': 'ISSUE107_PROMOTION_PREFLIGHT_V1',
        'base_special_count': EXPECTED_BASE,
        'candidate_count': EXPECTED_NEW,
        'proposed_special_count': EXPECTED_BASE + EXPECTED_NEW,
        'id_range': f'{FIRST_NEW_ID}..{LAST_NEW_ID}',
        'layer_counts': dict(sorted(layer_counts.items())),
        'candidate_source_sha256': sha256(candidate_path),
        'base_profile_sha256': sha256(profile_path),
        'proposal_sha256': sha256(proposal),
        'normalized_overlap_count': len(overlaps),
        'source_set_exact': 'YES',
        'existing_ids_stable': 'YES',
        'production_mutation': 'NO',
        'issue70_mutated': 'NO',
        'userdata_mutated': 'NO',
        'content_filter_used': 'NO',
    }
    (out_dir / 'promotion_preflight_summary_v1.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
