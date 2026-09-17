#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 043.

Conservative extension of batch023 for low-impact REVIEW_REQUIRED Character
parenthetical/variant rows. If the current Japanese display is supported only by
the raw candidate field and no stronger Japanese source evidence exists, prefer
an identity-safe human-readable canonical fallback over an unverified localized
variant/name.

Proposal-only; production Issue #70 data is never modified.
"""
from __future__ import annotations
import csv,re,shutil,subprocess,sys,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch043'
OUT=AUDIT/'character_unverified_variant_fallback_batch043.csv'
NOTES={
 'parenthetical candidate does not map cleanly to a copyright disambiguator',
 'variant/form rendering plausible but not independently verified',
}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
ALLOWED_FLAGS={'STATUS_REVIEW_REQUIRED','DISAMBIGUATOR_NOT_VISIBLE','VARIANT_DISPLAY_MISSING_BASE_IDENTITY','DUPLICATE_DISPLAY_WITHIN_CATEGORY','CHARACTER_NO_COPYRIGHT_CONTEXT'}

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
def flags(v):return {x.strip() for x in (v or '').split('|') if x.strip()}
def has_stronger_ja(r):
    for f in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'):
        if JA.search(r.get(f) or ''):return True
    return False
def fallback(tag):return (tag or '').replace('_',' ').strip()

def main():
    done=done_ids(); out=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '') not in NOTES:continue
        if int(r.get('post_count') or 0)>=500:continue
        fs=flags(r.get('risk_flags') or '')
        if not fs or 'STATUS_REVIEW_REQUIRED' not in fs or not fs.issubset(ALLOWED_FLAGS):continue
        current=(r.get('display_ja') or '').strip()
        if not current or not JA.search(current) or has_stronger_ja(r):continue
        raw={norm(x) for x in terms(r.get('existing_candidate_ja') or '')}
        if not raw or norm(current) not in raw:continue
        proposed=fallback(r.get('canonical_tag') or '')
        if not proposed or norm(proposed)==norm(current):continue
        out.append({
          'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':current,'existing_candidate_ja':r.get('existing_candidate_ja') or '',
          'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
          'related_copyright_top1':r.get('related_copyright_top1') or '',
          'related_copyright_top1_coverage':r.get('related_copyright_top1_coverage') or '',
          'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'',
          'reason_code':'REJECT_UNVERIFIED_VARIANT_JA_USE_CANONICAL_FALLBACK','confidence':'HIGH',
          'evidence_refs':'raw Japanese candidate only; no Japanese existing display/search/verified/source alias evidence',
          'audit_note':'variant/括弧付き日本語候補がraw candidate以外で裏付けられない低使用数行。誤った日本語identity/variant訳を残さずcanonical由来fallbackへ戻す。',
          'approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','existing_candidate_ja','translation_note','risk_flags','related_copyright_top1','related_copyright_top1_coverage','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'fix_display':len(out),'production_modified':False})
if __name__=='__main__':main()
