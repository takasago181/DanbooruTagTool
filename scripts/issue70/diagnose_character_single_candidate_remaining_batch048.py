#!/usr/bin/env python3
"""Dump remaining single-candidate Character rows after batch047. Diagnostic only."""
from __future__ import annotations
import csv,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch048'
OUT=AUDIT/'character_single_candidate_remaining_batch048_diagnostic.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
NOTE='single Japanese candidate with no conflicting evidence'
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
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def main():
    d=done(); fields=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_status','translation_note','risk_flags','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja','related_copyright_top1','related_copyright_top1_coverage','family_base_canonical','family_base_display_ja']; out=[]
    for r in census():
        if r.get('row_id') in d or r.get('category_name')!='Character' or (r.get('translation_note') or '')!=NOTE:continue
        out.append({k:r.get(k,'') for k in fields})
    out.sort(key=lambda r:(-int(r.get('post_count') or 0),r['row_id']))
    OUT.write_text(json.dumps({'format_version':1,'issue':70,'production_modified':False,'population':len(out),'rows':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'population':len(out),'production_modified':False})
if __name__=='__main__':main()
