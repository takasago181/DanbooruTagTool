#!/usr/bin/env python3
"""Replay the frozen 145 individual light-review dispositions, Browse only."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parents[2] / 'docs/issue216'
BASE = 'e5b6361e52f95b372a8672d2b0fc47d07a433145'


def read(name):
    with (D / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    old = read('REVIEWED_BROWSE_HOME_V3.csv')
    reviews = read('BROWSE_TOP2000_FINAL_REVIEW_V1.csv')
    open_tags = {r['character'] for r in old if not r['reviewed_browse_home'] and int(r['rank']) <= 2000}
    bytag = {r['character']: r for r in reviews}
    assert len(open_tags) == len(reviews) == len(bytag) == 145
    assert open_tags == set(bytag)
    roots = {r['copyright_canonical'] for r in read('COPYRIGHT_ROOTS_V1.csv')}
    updated = []
    for row in old:
        r = dict(row); v = bytag.get(r['character'])
        if v:
            home = v['reviewed_browse_home']
            assert v['rank'] == row['rank'] and v['individual_review_note']
            assert v['formal_authority_eligible'] == 'NO'
            assert (home and v['final_action'] == 'ADD' and home in roots) or (not home and v['final_action'] == 'RETAIN_UNRESOLVED')
            r.update(previous_audited_home=row['reviewed_browse_home'], reviewed_browse_home=home,
                review_state='REVIEWED_BROWSE_HOME' if home else 'REVIEWED_UNRESOLVED',
                action='ADD' if home else 'KEEP', confidence='MEDIUM' if home else 'LOW',
                review_pattern='FINAL_HIGH_FREQUENCY_' + v['reason_category'],
                review_note=v['individual_review_note'], source_url=v['source_url'])
        updated.append(r)
    assert len(updated) == len({r['character'] for r in updated}) == 10102
    with (D / 'REVIEWED_BROWSE_HOME_FINAL_V1.csv').open('w', encoding='utf-8', newline='') as f:
        out = csv.DictWriter(f, fieldnames=list(updated[0]), lineterminator='\n')
        out.writeheader(); out.writerows(updated)
    names = ['REVIEWED_BROWSE_HOME_V3.csv', 'BROWSE_TOP2000_FINAL_REVIEW_V1.csv',
        'BROWSE_TOP2000_FINAL_CONTEXT_V1.json.gz', 'COPYRIGHT_ROOTS_V1.csv',
        'AUTHORITY_COVERAGE_DECISIONS_V1.csv', 'AUTHORITY_SOURCE_MEMBERS_V1.csv', 'COPYRIGHT_AUTHORITY_REGISTRY_V1.csv']
    summary = dict(base_commit=BASE, individually_light_reviewed=145,
        browse_home_additions=sum(bool(r['reviewed_browse_home']) for r in reviews),
        retained_unresolved=sum(not r['reviewed_browse_home'] for r in reviews),
        unresolved_reason_counts=dict(Counter(r['reason_category'] for r in reviews if not r['reviewed_browse_home'])),
        final_Top2000_unresolved=sum(not r['reviewed_browse_home'] and int(r['rank']) <= 2000 for r in updated),
        final_Top500_unresolved=sum(not r['reviewed_browse_home'] and int(r['rank']) <= 500 for r in updated),
        reviewed_browse_home=sum(bool(r['reviewed_browse_home']) for r in updated),
        whole_overlay_unresolved=sum(not r['reviewed_browse_home'] for r in updated),
        input_sha256={n: hashlib.sha256((D / n).read_bytes()).hexdigest() for n in names},
        formal_authority_eligible=False, high_frequency_audit_complete=True,
        note='Final bounded individual light review. Retained unresolved is a reviewed outcome; no further high-frequency hunting in this task.')
    (D / 'BROWSE_TOP2000_FINAL_CHECKPOINT_V1.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
