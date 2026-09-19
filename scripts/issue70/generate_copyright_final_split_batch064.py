#!/usr/bin/env python3
"""Resolve the final remaining Accepted Copyright audit rows conservatively.

KEEP only rows whose current display exactly matches preserved Japanese evidence
and that have no collision/disambiguation/raw-syntax defect. Everything else is
explicitly routed to NEEDS_EXTERNAL_CHECK. Proposal-only; production data is not
modified.
"""
from __future__ import annotations
import csv, shutil, subprocess, sys, unicodedata
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-copyright-batch064'
OUT=AUDIT/'copyright_final_internal_external_split_batch064.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
BLOCKING={'DUPLICATE_DISPLAY_WITHIN_CATEGORY','DISAMBIGUATOR_NOT_VISIBLE','RAW_TAG_SYNTAX_IN_DISPLAY'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def done_ids():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name or 'diagnostic' in p.name:continue
        try:rows=read_csv(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():ids.add(r['row_id'].strip())
    return ids
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')
def flags(r):return {x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
def exact_preserved(r):
    nd=norm(r.get('display_ja') or '')
    vals=[]
    for f in ('existing_display_ja','existing_search_ja','existing_candidate_ja'):vals += terms(r.get(f) or '')
    return bool(nd) and any(norm(x)==nd for x in vals)
def main():
    done=done_ids(); rows=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Copyright' or r.get('translation_status')!='ACCEPTED_AI':continue
        fs=flags(r); exact=exact_preserved(r)
        keep=exact and not (fs & BLOCKING)
        verdict='KEEP' if keep else 'NEEDS_EXTERNAL_CHECK'
        reason='EXACT_PRESERVED_JA_NO_IDENTITY_DEFECT' if keep else 'FINAL_COPYRIGHT_REQUIRES_EXTERNAL_SEMANTIC_CHECK'
        confidence='HIGH' if keep else 'MEDIUM'
        evidence='display exact in preserved Japanese evidence; no duplicate/disambiguation/raw-syntax flag' if keep else 'remaining Accepted Copyright has collision/disambiguation or insufficient exact preserved Japanese evidence'
        note='保存済み日本語証拠と現表示が完全一致し、表示衝突・区別不足・raw構文の警告もないためKEEP。' if keep else '内部証拠だけでは作品系列・媒体・版・同名作品の区別を安全に確定できないため、推測修正せず外部確認へ送る。'
        rows.append({
          'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':r.get('display_ja') or '','search_ja':r.get('search_ja') or '',
          'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
          'audit_verdict':verdict,'proposed_display_ja':'','proposed_search_ja':'',
          'reason_code':reason,'confidence':confidence,'evidence_refs':evidence,
          'audit_note':note,'approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(0 if r['audit_verdict']=='KEEP' else 1,-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    from collections import Counter
    print({'rows':len(rows),'verdicts':dict(Counter(r['audit_verdict'] for r in rows)),'production_modified':False})
if __name__=='__main__':main()
