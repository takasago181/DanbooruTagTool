#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 044.

For remaining low-impact REVIEW_REQUIRED Character rows with uncertain/raw-only
Japanese candidates, use an identity-safe canonical fallback instead of keeping
an unverified Japanese name. Stronger Japanese source evidence excludes a row.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,re,shutil,subprocess,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch044'
OUT=AUDIT/'character_uncertain_raw_fallback_batch044.csv'
NOTES={
 '要確認',
 'Latin-heavy candidate requires verification',
 'romanized handle plus generated qualifier',
 '日本語表示名・表記の確定に追加確認が必要',
 'multiple/conflicting Japanese candidates',
 'malformed or low-confidence Japanese evidence requires manual verification',
 '日本語公式表記の追加確認が必要',
 '日本語公式表記を追加確認',
 '日本語衣装名の追加確認が必要',
 '衣装呼称の公式表記を追加確認',
 '衣装名の日本語公式表記確認が必要',
 'AI監修：衣装名の公式表記を要確認',
 'AI監修：衣装名の公式対応を要確認',
 'AI監修：日本語公式表記の確証不足',
 'AI監修：作品内公式表記の確証不足',
 'AI監修：中国語候補のみで日本語公式表記を要確認',
 'AI監修：衣装区分の公式表記を要確認',
 '日本語衣装名との対応を追加確認',
 'AI監修：形態名の公式表記を要確認',
 '再臨別表記を追加確認',
}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
BLOCK_FLAGS={'RAW_TAG_SYNTAX_IN_DISPLAY','DISPLAY_MISSING_FROM_SEARCH'}

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
    return any(JA.search(r.get(f) or '') for f in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'))
def fallback(tag):return (tag or '').replace('_',' ').strip()

def main():
    done=done_ids(); out=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '') not in NOTES:continue
        if int(r.get('post_count') or 0)>=500:continue
        fs=flags(r.get('risk_flags') or '')
        if BLOCK_FLAGS & fs:continue
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
          'reason_code':'REJECT_UNVERIFIED_UNCERTAIN_JA_USE_CANONICAL_FALLBACK','confidence':'HIGH',
          'evidence_refs':'raw Japanese candidate only; no Japanese existing display/search/verified/source alias evidence',
          'audit_note':'要確認/低信頼の日本語候補がraw candidate以外で裏付けられない低使用数行。誤った日本語identityを残さずcanonical由来fallbackへ戻す。',
          'approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','existing_candidate_ja','translation_note','risk_flags','related_copyright_top1','related_copyright_top1_coverage','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'fix_display':len(out),'production_modified':False})
if __name__=='__main__':main()
