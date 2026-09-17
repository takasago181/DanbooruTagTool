#!/usr/bin/env python3
"""Generate Issue #70 audit batch 026.

Close remaining REVIEW_REQUIRED Character/Copyright rows when the current display
is already the identity-safe readable form of the canonical Danbooru tag.
This is a deliberate fallback policy: an untranslated canonical identity is
preferable to an unverified Japanese name/title. No translation is invented.

Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch026'; OUT=AUDIT/'identity_safe_canonical_fallback_keep_batch026.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def audited_ids():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name:continue
        try:rows=read_csv(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():ids.add(r['row_id'].strip())
    return ids
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')
def fallback(tag):return (tag or '').replace('_',' ').strip()
def main():
    done=audited_ids();rows=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name') not in {'Character','Copyright'}:continue
        if r.get('translation_status')!='REVIEW_REQUIRED':continue
        display=(r.get('display_ja') or '').strip(); expected=fallback(r.get('canonical_tag') or '')
        if not expected or display!=expected:continue
        rows.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'category_name':r['category_name'],'post_count':r.get('post_count') or '','display_ja':display,'search_ja':r.get('search_ja') or '','translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '','audit_verdict':'KEEP','proposed_display_ja':'','proposed_search_ja':'','reason_code':'IDENTITY_SAFE_CANONICAL_FALLBACK_ALREADY_APPLIED','confidence':'HIGH','evidence_refs':'display equals readable canonical Danbooru tag exactly','audit_note':'日本語表記を推測せず、canonical tag由来のidentity-safe fallbackが既に適用済み。未検証の日本語名/作品名を再採用するより正確性を優先して現表示を維持。','approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(r['category_name'],-int(r['post_count'] or 0),r['row_id']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['row_id','canonical_tag','category_name','post_count','display_ja','search_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    from collections import Counter
    c=Counter(r['category_name'] for r in rows)
    print({'rows':len(rows),'by_category':dict(c),'production_modified':False});return 0
if __name__=='__main__':raise SystemExit(main())
