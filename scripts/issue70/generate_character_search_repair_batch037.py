#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 037.

Resolve remaining ACCEPTED_AI Character rows where the Japanese display is directly
supported by non-candidate source evidence and the only actionable defect is that
that confirmed display term is missing from search_ja. Display is never changed.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,re,shutil,subprocess,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch037'; OUT=AUDIT/'character_source_supported_search_repair_batch037.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
CRITICAL={'DISAMBIGUATOR_NOT_VISIBLE','DUPLICATE_DISPLAY_WITHIN_CATEGORY','VARIANT_DISPLAY_MISSING_BASE_IDENTITY','RAW_TAG_SYNTAX_IN_DISPLAY','UNBALANCED_BRACKETS','NO_SOURCE_JA_EVIDENCE_OVERLAP'}
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def done():
    s=set()
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name or 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():s.add(r['row_id'].strip())
    return s
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def source_support(r,display):
    nd=norm(display)
    for f in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'):
        for t in terms(r.get(f) or ''):
            if JA.search(t) and norm(t)==nd:return f,t
    return None
def main():
    audited=done(); out=[]
    for r in census():
        if r.get('row_id') in audited or r.get('category_name')!='Character' or r.get('translation_status')!='ACCEPTED_AI':continue
        flags={x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
        if 'DISPLAY_MISSING_FROM_SEARCH' not in flags or flags & CRITICAL:continue
        display=(r.get('display_ja') or '').strip(); search=(r.get('search_ja') or '').strip()
        if not display or not JA.search(display):continue
        support=source_support(r,display)
        if not support:continue
        cur_terms=terms(search)
        if norm(display) in {norm(x) for x in cur_terms}:continue
        proposed=' | '.join([display]+cur_terms)
        out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':display,'search_ja':search,'risk_flags':r.get('risk_flags') or '',
          'source_support_field':support[0],'source_support_term':support[1],
          'audit_verdict':'FIX_SEARCH','proposed_display_ja':'','proposed_search_ja':proposed,
          'reason_code':'SOURCE_SUPPORTED_DISPLAY_MISSING_FROM_SEARCH','confidence':'HIGH',
          'evidence_refs':f'{support[0]} exact display match; DISPLAY_MISSING_FROM_SEARCH',
          'audit_note':'display_jaは非candidateのsource根拠と直接一致。表示は維持し、検索から欠けているdisplay_jaのみsearch_jaへ追加。',
          'approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','risk_flags','source_support_field','source_support_term','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'fix_search':len(out),'production_modified':False})
if __name__=='__main__':main()
