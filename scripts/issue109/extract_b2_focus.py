from __future__ import annotations

import csv
from pathlib import Path

SRC = Path('docs/issue109/mechanical_triage_v1.csv')
OUT = Path('docs/issue109/b2_focus_801_1600.csv')

with SRC.open(encoding='utf-8-sig', newline='') as f:
    rows = [r for r in csv.DictReader(f) if 801 <= int(r['special_id']) <= 1600]

# Human focus: anything already review/candidate, product-scope warnings, reference-only,
# generic General taxonomy homes, or plain identity aliases that may be redundant.
plain_alias_terms = {
    'nipple','cock','dick','vagina','vulva','sperm','cocks','dicks','manko',
    'ass hole','asshole','butt hole','butthole','fondle','fondling','grope',
}
focus = []
for r in rows:
    reasons=[]
    if r['mechanical_triage'] != 'KEEP_SPECIAL': reasons.append('MECHANICAL_REVIEW')
    if r['product_fit_verdict'] in {'OUT_OF_SCOPE_PRODUCT','REVIEW','KEEP_REFERENCE_ONLY'}:
        reasons.append('PRODUCT_FIT_'+r['product_fit_verdict'])
    if r['general_primary_path'] in {
        'TEXT_SYMBOL/TEXT','TEXT_SYMBOL/SYMBOL','STYLE_QUALITY_META','OBJECT_PROP',
        'OBJECT_PROP/VEHICLE','OBJECT_PROP/DAILY','BODY_PART','CLOTHING_STATE_EXPOSURE'
    }:
        reasons.append('GENERAL_PATH_'+r['general_primary_path'])
    if r['tag'] in plain_alias_terms:
        reasons.append('PLAIN_ALIAS_IDENTITY')
    if reasons:
        x=dict(r)
        x['focus_reason']=';'.join(reasons)
        focus.append(x)

OUT.parent.mkdir(parents=True, exist_ok=True)
fields=list(rows[0].keys())+['focus_reason']
with OUT.open('w', encoding='utf-8-sig', newline='') as f:
    w=csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(focus)
print(f'B2_ROWS={len(rows)}')
print(f'B2_FOCUS_ROWS={len(focus)}')
