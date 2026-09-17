#!/usr/bin/env python3
"""Dump remaining Issue #70 Character rows whose note is 'single Japanese candidate with no conflicting evidence'.
Diagnostic only; production data is never modified.
"""
from __future__ import annotations
import csv, json, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'
TMP=ROOT/'artifacts/issue70-batch046'
OUT=AUDIT/'character_single_candidate_batch046_diagnostic.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
NOTE='single Japanese candidate with no conflicting evidence'

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def audited_ids():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name:continue
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():
                ids.add(r['row_id'].strip())
    return ids

def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')

def main():
    done=audited_ids(); rows=[]
    keep_fields=['row_id','canonical_tag','post_count','impact_tier','display_ja','search_ja','translation_status','translation_note','risk_flags','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja','related_copyright_top1','related_copyright_top1_coverage','family_base_canonical','family_base_display_ja']
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Character':continue
        if (r.get('translation_note') or '')!=NOTE:continue
        rows.append({k:r.get(k,'') for k in keep_fields})
    rows.sort(key=lambda r:(-int(r.get('post_count') or 0),r['row_id']))
    OUT.write_text(json.dumps({'format_version':1,'issue':70,'production_modified':False,'population':len(rows),'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'population':len(rows),'production_modified':False})
if __name__=='__main__':main()
