"""Audited ID-only product eligibility. Source identities and raw search stay intact."""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
from types import MappingProxyType


MANIFEST_PATH = Path('docs/audit/SPECIAL2788_PRODUCT_FIT_VERDICT_MANIFEST_20260912.json')
CSV_PATH = Path('data/special2788/product_fit_verdicts.csv')
MANIFEST_SHA256 = '187372bef6937028b16986b76a841719a3710e0ca21b7b885b9230556066a12d'
COUNTS = MappingProxyType({'KEEP': 1618, 'KEEP_REFERENCE_ONLY': 1133,
                          'OUT_OF_SCOPE_PRODUCT': 12, 'REVIEW': 25})
FIELDS = ('special_id', 'product_fit_verdict')
_ELIGIBILITY = {
    'browse': frozenset({'KEEP'}),
    'recommendation': frozenset({'KEEP'}),
    'search': frozenset({'KEEP', 'KEEP_REFERENCE_ONLY', 'REVIEW'}),
    'selection': frozenset({'KEEP', 'KEEP_REFERENCE_ONLY', 'REVIEW'}),
    'statistics': frozenset({'KEEP', 'KEEP_REFERENCE_ONLY'}),
    'support': frozenset({'KEEP', 'KEEP_REFERENCE_ONLY'}),
    'inspect': frozenset(COUNTS),
}
LABELS_JA = MappingProxyType({'KEEP': '', 'KEEP_REFERENCE_ONLY': '参照用',
                            'OUT_OF_SCOPE_PRODUCT': '通常候補の対象外', 'REVIEW': '要確認'})


def validate_verdicts(verdicts):
    if set(verdicts) != {str(i) for i in range(1, 2789)}:
        raise ValueError('Product-fit IDs must be unique and contiguous 1..2788')
    if Counter(verdicts.values()) != dict(COUNTS):
        raise ValueError('Product-fit verdict counts must match the audited 1618/1133/12/25')


def expand_manifest(manifest):
    """Expand explicit ranges without applying precedence to hide overlaps."""
    if (manifest.get('schema_version') != 1 or manifest.get('status') != 'COMPLETE'
            or manifest.get('total_entries') != 2788 or manifest.get('default_verdict') != 'KEEP'
            or manifest.get('expected_counts') != dict(COUNTS)):
        raise ValueError('Unexpected product-fit manifest contract')
    sets = manifest.get('verdict_sets', {})
    if set(sets) != set(COUNTS) - {'KEEP'}:
        raise ValueError('Unexpected explicit verdict sets')
    contract = manifest.get('expansion_contract', {})
    if (contract.get('id_domain') != '1..2788 inclusive'
            or contract.get('precedence') != ['REVIEW', 'OUT_OF_SCOPE_PRODUCT',
                                               'KEEP_REFERENCE_ONLY', 'KEEP']
            or contract.get('overlap_allowed') is not False or contract.get('missing_id_allowed') is not False
            or contract.get('generated_csv_columns') != list(FIELDS)
            or contract.get('generated_csv_path') != CSV_PATH.as_posix()):
        raise ValueError('Unexpected expansion contract')
    verdicts = {str(i): 'KEEP' for i in range(1, 2789)}
    assigned = set()
    for verdict, ranges in sets.items():
        if not isinstance(ranges, str):
            raise ValueError('Verdict set must be comma-separated ID ranges')
        for token in ranges.split(','):
            if not re.fullmatch(r'[1-9][0-9]*(?:-[1-9][0-9]*)?', token):
                raise ValueError('Invalid verdict ID range')
            bounds = token.split('-')
            low, high = int(bounds[0]), int(bounds[-1])
            if not 1 <= low <= high <= 2788:
                raise ValueError('Verdict ID range outside 1..2788')
            for number in range(low, high + 1):
                sid = str(number)
                if sid in assigned:
                    raise ValueError('Overlapping or repeated verdict ID')
                assigned.add(sid)
                verdicts[sid] = verdict
    validate_verdicts(verdicts)
    return verdicts


def load_authority(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise ValueError('Audited product-fit manifest hash mismatch')
    return expand_manifest(json.loads(raw))


def csv_bytes(verdicts):
    validate_verdicts(verdicts)
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(FIELDS)
    writer.writerows((str(i), verdicts[str(i)]) for i in range(1, 2789))
    return stream.getvalue().encode('utf-8')


class ProductFitPolicy:
    """Small immutable sidecar; no term-based inference or canonical mutation.

    Direct construction supports explicit in-memory fixtures. Production loading
    always requires the pinned complete authority and the materialized CSV.
    """
    def __init__(self, verdicts, special):
        if set(verdicts) != set(special) or not set(verdicts.values()) <= set(COUNTS):
            raise ValueError('Product-fit sidecar must cover exactly the supplied Special IDs')
        self.verdicts = MappingProxyType(dict(verdicts))
        by_canonical = {}
        for sid, tag in special.items():
            for canonical in tag.canonical_candidates:
                by_canonical.setdefault(canonical, []).append(sid)
        self._canonical_ids = MappingProxyType({c: tuple(ids) for c, ids in by_canonical.items()})

    @classmethod
    def load(cls, root: Path, special):
        expected = load_authority(root / MANIFEST_PATH)
        with (root / CSV_PATH).open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != list(FIELDS):
                raise ValueError('Unexpected product-fit CSV columns')
            actual = {}
            for row in reader:
                sid = row['special_id']
                if set(row) != set(FIELDS) or sid in actual:
                    raise ValueError('Duplicate ID or malformed product-fit CSV row')
                actual[sid] = row['product_fit_verdict']
        validate_verdicts(actual)
        if actual != expected:
            raise ValueError('Product-fit CSV differs from audited ID verdicts')
        return cls(actual, special)

    def verdict(self, special_id: str) -> str:
        return self.verdicts[special_id]

    def allows(self, special_id: str, surface: str) -> bool:
        return self.verdict(special_id) in _ELIGIBILITY[surface]

    def canonical_allows(self, canonical: str, surface: str) -> bool:
        allowed = _ELIGIBILITY[surface]  # invalid surfaces never silently pass
        ids = self._canonical_ids.get(canonical, ())
        # A retained KEEP identity takes precedence over reference/ambiguous
        # aliases pointing at it. Unrelated All-Danbooru assets are unchanged.
        return not ids or any(self.verdict(sid) in allowed for sid in ids)

    def label(self, special_id: str) -> str:
        return LABELS_JA[self.verdict(special_id)]
