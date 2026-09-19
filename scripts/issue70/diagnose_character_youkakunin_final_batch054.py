#!/usr/bin/env python3
"""Dump all remaining Character rows from batch050 '要確認' diagnostic after batches 051-053.
Diagnostic only; production data is never modified.
"""
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/'docs/issue70/audit'
INP=AUDIT/'character_youkakunin_batch050_diagnostic.json'; OUT=AUDIT/'character_youkakunin_final_batch054_diagnostic.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def done():
    s=set()
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():s.add(r['row_id'].strip())
    return s
def main():
    d=json.loads(INP.read_text(encoding='utf-8')); audited=done(); rows=[r for r in d['rows'] if r['row_id'] not in audited]
    rows.sort(key=lambda r:(r.get('diagnostic_bucket',''),-int(r.get('post_count') or 0),r['row_id']))
    counts=Counter(r.get('diagnostic_bucket','') for r in rows); sig=Counter((r.get('diagnostic_bucket',''),r.get('risk_flags','')) for r in rows)
    data={'format_version':1,'issue':70,'production_modified':False,'population':len(rows),'bucket_counts':dict(counts),'signatures':[{'bucket':b,'risk_flags':f,'count':c} for (b,f),c in sig.most_common()],'rows':rows}
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'population':len(rows),'bucket_counts':dict(counts),'production_modified':False})
if __name__=='__main__':main()
