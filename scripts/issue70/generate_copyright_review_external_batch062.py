#!/usr/bin/env python3
"""Classify all remaining Copyright REVIEW_REQUIRED rows as NEEDS_EXTERNAL_CHECK.

These rows are already explicitly marked by the translation pass as requiring
manual verification, unresolved title identity, or insufficient Japanese source
evidence. Final semantic audit must not invent a Japanese title. Proposal-only;
production Issue #70 data is never modified.
"""
from __future__ import annotations
import csv, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'
TMP=ROOT/'artifacts/issue70-copyright-batch062'
OUT=AUDIT/'copyright_review_external_batch062.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}

def read_csv(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def done_ids():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name or 'diagnostic' in p.name:
            continue
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():
                ids.add(r['row_id'].strip())
    return ids

def census():
    if TMP.exists(): shutil.rmtree(TMP)
    subprocess.run([sys.executable, str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'), '--out', str(TMP), '--sample-per-category', '300'], cwd=ROOT, check=True)
    return read_csv(TMP/'audit_ledger_template.csv')

def main():
    done=done_ids(); out=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Copyright':
            continue
        if r.get('translation_status')!='REVIEW_REQUIRED':
            continue
        note=(r.get('translation_note') or '').strip()
        out.append({
            'row_id':r['row_id'], 'canonical_tag':r['canonical_tag'], 'post_count':r.get('post_count') or '',
            'display_ja':r.get('display_ja') or '', 'search_ja':r.get('search_ja') or '',
            'translation_note':note, 'risk_flags':r.get('risk_flags') or '',
            'audit_verdict':'NEEDS_EXTERNAL_CHECK', 'proposed_display_ja':'', 'proposed_search_ja':'',
            'reason_code':'COPYRIGHT_REVIEW_REQUIRES_EXTERNAL_TITLE_VERIFICATION', 'confidence':'HIGH',
            'evidence_refs':'translation_status=REVIEW_REQUIRED; translation_note explicitly requires manual/external verification or reports insufficient/ambiguous title evidence',
            'audit_note':'Copyrightタイトルを一意に確定できる根拠が不足しているため、推測修正せず外部確認対象として確定。',
            'approval_status':'PROPOSED'
        })
    out.sort(key=lambda r:(-int(r['post_count'] or 0), r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w', encoding='utf-8-sig', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)
    print({'rows':len(out),'needs_external_check':len(out),'production_modified':False})
    return 0

if __name__=='__main__': raise SystemExit(main())
