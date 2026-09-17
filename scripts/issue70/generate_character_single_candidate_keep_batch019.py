#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 019.

Closes remaining Character rows whose translation note says there is exactly
one Japanese candidate with no conflicting evidence, provided the current
Japanese display is present in preserved evidence, the related Copyright link
is strong, and no identity/disambiguation/structural risk remains.

Proposal-only; production translation data is never modified.
"""
from __future__ import annotations

import csv
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT_DIR=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch019'
OUT=AUDIT_DIR/'character_single_candidate_keep_batch019.csv'
NOTE='single Japanese candidate with no conflicting evidence'
JA_RE=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
DANGEROUS={
 'DISAMBIGUATOR_NOT_VISIBLE','DUPLICATE_DISPLAY_WITHIN_CATEGORY',
 'VARIANT_DISPLAY_MISSING_BASE_IDENTITY','VARIANT_DISPLAY_LOST_QUALIFIER',
 'RAW_TAG_SYNTAX_IN_DISPLAY','UNBALANCED_BRACKETS','UNICODE_REPLACEMENT_CHAR',
 'CHARACTER_NO_COPYRIGHT_CONTEXT','ASCII_ONLY_DISPLAY_NON_ARTIST',
}
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows,fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def prior_ids():
    ids=set()
    for p in AUDIT_DIR.glob('*.csv'):
        if p.name==OUT.name:continue
        try:rows=read_csv(p)
        except Exception:continue
        for r in rows:
            if r.get('row_id') and r.get('audit_verdict'):ids.add(r['row_id'].strip())
    return ids
def run_census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')
def norm(v):
    return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(row):
    out=[]
    for field in ('existing_display_ja','existing_search_ja','existing_candidate_ja'):
        out.extend(x.strip() for x in (row.get(field) or '').split('|') if x.strip())
    return {norm(x) for x in out if x}
def flagset(row):return {x.strip() for x in (row.get('risk_flags') or '').split('|') if x.strip()}
def coverage(row):
    try:return float(row.get('related_copyright_top1_coverage') or 0)
    except ValueError:return 0.0
def main():
    audited=prior_ids();rows=[]
    for r in run_census():
        if r.get('row_id') in audited or r.get('category_name')!='Character':continue
        if (r.get('translation_note') or '')!=NOTE:continue
        display=(r.get('display_ja') or '').strip()
        if not display or not JA_RE.search(display):continue
        if flagset(r)&DANGEROUS:continue
        if norm(display) not in terms(r):continue
        if not (r.get('related_copyright_top1') or '').strip() or coverage(r)<0.80:continue
        rows.append({
          'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],
          'display_ja':display,'search_ja':r.get('search_ja') or '',
          'related_copyright_top1':r.get('related_copyright_top1') or '',
          'related_copyright_top1_coverage':r.get('related_copyright_top1_coverage') or '',
          'audit_verdict':'KEEP','proposed_display_ja':'','proposed_search_ja':'',
          'reason_code':'SINGLE_JA_CANDIDATE_STRONG_CONTEXT_NO_CONFLICT','confidence':'HIGH',
          'evidence_refs':'exact preserved Japanese candidate/display/search evidence + strong related Copyright coverage',
          'audit_note':'単一日本語候補・source完全一致・強い作品関係を満たし、衝突/variant欠落/構造異常がないため現表示を維持。',
          'approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    write_csv(OUT,rows,['row_id','canonical_tag','post_count','display_ja','search_ja','related_copyright_top1','related_copyright_top1_coverage','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status'])
    print({'rows':len(rows),'production_modified':False});return 0
if __name__=='__main__':raise SystemExit(main())
