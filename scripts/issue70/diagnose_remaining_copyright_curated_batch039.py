#!/usr/bin/env python3
"""Diagnose remaining Issue #70 Copyright rows with explicit curated/established notes.
Diagnostic only; no verdicts or production changes.
"""
from __future__ import annotations
import csv,json,shutil,subprocess,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch039'; OUT=AUDIT/'copyright_remaining_curated_batch039_diagnostic.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
NOTES={
'established/common Japanese title or official rendering',
'manual chat curation selected high-confidence Japanese copyright title',
'semantic re-curation: title/name judged usable; official/common rendering preferred over literal candidate',
'semantic re-curation: title/name judged usable; official/common rendering or identity-safe original preferred over literal candidate',
'single clean Japanese copyright search title',
}
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def done():
    out=set()
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():out.add(r['row_id'].strip())
    return out
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def fs(v):
    xs=sorted(x.strip() for x in (v or '').split('|') if x.strip()); return '|'.join(xs) if xs else '<none>'
def main():
    audited=done(); groups=defaultdict(list); total=0
    for r in census():
        if r.get('row_id') in audited or r.get('category_name')!='Copyright':continue
        note=(r.get('translation_note') or '').strip()
        if note not in NOTES:continue
        total+=1
        o={k:r.get(k) or '' for k in ['row_id','canonical_tag','post_count','impact_tier','display_ja','search_ja','translation_status','translation_note','risk_flags','audit_bucket','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja']}
        groups[(note,fs(o['risk_flags']),o['translation_status'])].append(o)
    data={'format_version':1,'issue':70,'production_modified':False,'population':total,'groups':[]}
    for (note,flags,status),rows in sorted(groups.items(),key=lambda kv:(-len(kv[1]),kv[0])):
        rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
        data['groups'].append({'translation_note':note,'risk_flags':flags,'translation_status':status,'count':len(rows),'samples':rows[:20]})
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'population':total,'groups':[(g['translation_note'],g['risk_flags'],g['translation_status'],g['count']) for g in data['groups']], 'production_modified':False},ensure_ascii=False))
if __name__=='__main__':main()
