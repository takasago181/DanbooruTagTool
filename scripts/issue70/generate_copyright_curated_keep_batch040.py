#!/usr/bin/env python3
"""Generate Issue #70 Copyright audit batch 040.

KEEP remaining ACCEPTED_AI Copyright rows that were explicitly curated/established
and whose remaining flags are only evidence/orthography heuristics, not identity or
browse-disambiguation defects. Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch040'; OUT=AUDIT/'copyright_curated_safe_keep_batch040.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
NOTES={
'established/common Japanese title or official rendering',
'manual chat curation selected high-confidence Japanese copyright title',
'semantic re-curation: title/name judged usable; official/common rendering preferred over literal candidate',
'semantic re-curation: title/name judged usable; official/common rendering or identity-safe original preferred over literal candidate',
'single clean Japanese copyright search title',
}
BLOCK={'DUPLICATE_DISPLAY_WITHIN_CATEGORY','DISAMBIGUATOR_NOT_VISIBLE','RAW_TAG_SYNTAX_IN_DISPLAY','UNBALANCED_BRACKETS','DISPLAY_UNUSUALLY_LONG'}
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
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
def main():
    audited=done(); out=[]
    for r in census():
        if r.get('row_id') in audited or r.get('category_name')!='Copyright' or r.get('translation_status')!='ACCEPTED_AI':continue
        if (r.get('translation_note') or '').strip() not in NOTES:continue
        flags={x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
        if flags & BLOCK:continue
        out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':r.get('display_ja') or '','search_ja':r.get('search_ja') or '',
          'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
          'audit_verdict':'KEEP','proposed_display_ja':'','proposed_search_ja':'',
          'reason_code':'CURATED_COPYRIGHT_NO_IDENTITY_OR_DISAMBIGUATION_DEFECT','confidence':'HIGH',
          'evidence_refs':'explicit curated/established translation_note; no duplicate/disambiguator/raw-syntax flags',
          'audit_note':'既に意味監修済みのCopyright。残る警告はsource一致/ASCII等の機械ヒューリスティックのみで、identity・区別表示の問題はないためKEEP。',
          'approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'keep':len(out),'production_modified':False})
if __name__=='__main__':main()
