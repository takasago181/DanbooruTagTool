#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 045.

Close remaining ACCEPTED_AI Character rows only when the current Japanese display
is directly supported by preserved Japanese source evidence (existing display or
search). This treats source-overlap heuristics as stale without assuming every
Accepted row is correct.

Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,shutil,subprocess,sys,unicodedata,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch045'
OUT=AUDIT/'character_accepted_source_supported_keep_batch045.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def done_ids():
    out=set()
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name or 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():out.add(r['row_id'].strip())
    return out
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def matching_evidence(r,display):
    nd=norm(display); hits=[]
    for f in ('existing_display_ja','existing_search_ja'):
        for t in terms(r.get(f) or ''):
            if JA.search(t) and norm(t)==nd:hits.append(f+':'+t)
    return hits

def main():
    done=done_ids(); out=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='ACCEPTED_AI':continue
        display=(r.get('display_ja') or '').strip()
        if not display or not JA.search(display):continue
        hits=matching_evidence(r,display)
        if not hits:continue
        out.append({
          'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':display,'search_ja':r.get('search_ja') or '',
          'existing_display_ja':r.get('existing_display_ja') or '',
          'existing_search_ja':r.get('existing_search_ja') or '',
          'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
          'audit_verdict':'KEEP','proposed_display_ja':'','proposed_search_ja':'',
          'reason_code':'ACCEPTED_DISPLAY_DIRECTLY_SUPPORTED_BY_PRESERVED_JA_SOURCE','confidence':'HIGH',
          'evidence_refs':' | '.join(hits),
          'audit_note':'現在表示が保存済みの日本語display/search証拠と正規化後に完全一致。残るriskはsource-overlap等の機械ヒューリスティックとしてKEEP。',
          'approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','existing_display_ja','existing_search_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'keep':len(out),'production_modified':False})
if __name__=='__main__':main()
