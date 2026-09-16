#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, unicodedata
from pathlib import Path

def norm(v: object) -> str:
    s = '' if v is None else str(v)
    s = unicodedata.normalize('NFKC', s).strip().casefold().replace('_', ' ')
    return ' '.join(s.split())

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--omissions', required=True)
    ap.add_argument('--special-profile', required=True)
    ap.add_argument('--summary', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    with Path(args.special_profile).open(encoding='utf-8-sig', newline='') as f:
        special = list(csv.DictReader(f))
    all_surfaces = {norm(r['Tag']) for r in special if norm(r['Tag'])}

    with Path(args.omissions).open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    kept = [r for r in rows if norm(r['canonical_tag']) not in all_surfaces]
    removed = [r for r in rows if norm(r['canonical_tag']) in all_surfaces]

    out = Path(args.out)
    with out.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [
            'canonical_tag','post_count','aliases','adult_review_priority','adult_review_hits',
            'coverage_status','human_review_status','notes'])
        w.writeheader(); w.writerows(kept)

    summary_path = Path(args.summary)
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    summary['pre_strict_omission_count'] = summary['product_complete_omission_count']
    summary['special_all_surface_count'] = len(all_surfaces)
    summary['removed_exact_special_surface_count'] = len(removed)
    summary['removed_exact_special_surfaces'] = [r['canonical_tag'] for r in removed]
    summary['product_complete_omission_count'] = len(kept)
    summary['adult_priority_count'] = sum(r['adult_review_priority'] == 'HIGH' for r in kept)
    summary['top_20_omissions'] = [
        {'tag': r['canonical_tag'], 'post_count': int(r['post_count']), 'priority': r['adult_review_priority']}
        for r in kept[:20]
    ]
    summary['special_surface_semantics_included_in_absence_test'] = 'YES'
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'kept': len(kept), 'removed_special_surfaces': len(removed), 'removed': [r['canonical_tag'] for r in removed]}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
