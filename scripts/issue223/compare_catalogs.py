"""Read-only whole-catalog comparison, including all non-Character categories."""
import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from itertools import zip_longest
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--baseline', type=Path, required=True)
parser.add_argument('--candidate', type=Path, required=True)
parser.add_argument('--report', type=Path, required=True)
args = parser.parse_args()
counts = Counter()
groups = Counter()
home_hash = hashlib.sha256()
rows = 0
with sqlite3.connect(args.baseline.resolve().as_uri()+'?mode=ro', uri=True) as before, sqlite3.connect(args.candidate.resolve().as_uri()+'?mode=ro', uri=True) as after:
    for old, new in zip_longest(before.execute('select id,payload from entries order by ordinal'), after.execute('select id,payload from entries order by ordinal')):
        assert old and new and old[0] == new[0]
        a, b = json.loads(old[1]), json.loads(new[1])
        group = b.pop('BrowseGroup', None)
        assert a == b, old[0]
        rows += 1
        counts[b['EffectiveCategory']] += 1
        if b['EffectiveCategory'] == 'Character':
            counts[b['BrowseHomeSource']] += 1
            home_hash.update(json.dumps([b['Canonical'], b['FormalHomeCopyright'], b['ReviewedBrowseHome'], b['BrowseHomeSource']], ensure_ascii=False, separators=(',', ':')).encode())
        if group:
            assert b['EffectiveCategory'] == 'Character' and b['EffectiveBrowseHome'] == group['HomeCopyright']
            groups[group['HomeCopyright']] += 1
assert counts['Character'] == 35278 and counts['Copyright'] == 7616
assert counts['FORMAL_HOME'] == 25533 and counts['REVIEWED_BROWSE_FALLBACK'] == 7409 and counts['UNRESOLVED'] == 2336
def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()
result = dict(verdict='PASS', total=rows, counts=dict(counts), grouped_by_home=dict(groups),
              grouped=sum(groups.values()), non_group_field_changes=0, identity_order_changes=0,
              home_authority_sha256=home_hash.hexdigest(), baseline_catalog_sha256=sha(args.baseline), candidate_catalog_sha256=sha(args.candidate))
args.report.write_bytes((json.dumps(result, indent=2)+'\n').encode())
print(json.dumps(result))
