#!/usr/bin/env python3
"""Export all remaining Character ACCEPTED_CLEAN_SAMPLE audit-ledger rows.
Diagnostic only; production and audit verdicts are not modified.
"""
from __future__ import annotations
import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'
SRC=AUDIT/'character_remaining_accepted_batch029_diagnostic.csv'
OUT=AUDIT/'character_remaining_clean_sample_batch030_diagnostic.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def done_ids():
    out=set()
    for p in AUDIT.glob('*.csv'):
        if p in {SRC,OUT} or 'diagnostic' in p.name: continue
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip(): out.add(r['row_id'].strip())
    return out

def main():
    done=done_ids()
    rows=[r for r in read_csv(SRC) if r.get('audit_bucket')=='ACCEPTED_CLEAN_SAMPLE' and r.get('row_id') not in done]
    rows.sort(key=lambda r:(-int(r.get('post_count') or 0),r.get('row_id') or ''))
    assert len(rows)==68, len(rows)
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print({'rows':len(rows),'production_modified':False})
if __name__=='__main__': main()
