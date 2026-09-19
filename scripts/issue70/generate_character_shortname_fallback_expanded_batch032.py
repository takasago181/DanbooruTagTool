#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 032.

Expand the proven batch023 short-name safety rule to the remaining REVIEW_REQUIRED
short kana/kanji rows that have extra *risk* flags but still no stronger Japanese
evidence. If a verified family/base Japanese identity exists, retain it and use
canonical variant qualifiers; otherwise use a readable canonical fallback.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,re,shutil,subprocess,sys,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch032'; OUT=AUDIT/'character_shortname_fallback_expanded_batch032.csv'
NOTES={'short kana-only candidate is too ambiguous without contextual search evidence','short kanji-only candidate is too ambiguous without contextual search evidence'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]'); PAREN=re.compile(r'_\(([^()]*)\)')
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def done():
    s=set()
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name or 'diagnostic' in p.name:continue
        try: rows=read(p)
        except Exception: continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID:s.add((r.get('row_id') or '').strip())
    return s
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def has_stronger_ja(r):
    return any(JA.search(r.get(f) or '') for f in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'))
def parens(tag):return [x.strip() for x in PAREN.findall(tag or '') if x.strip()]
def variant_tokens(canonical,base):
    c=parens(canonical); b=Counter(parens(base)); out=[]
    for x in c:
        if b[x]: b[x]-=1
        else: out.append(x.replace('_',' ').strip())
    return [x for x in out if x]
def proposal(r):
    base=(r.get('family_base_display_ja') or '').strip(); base_can=(r.get('family_base_canonical') or '').strip()
    if base and base_can and JA.search(base):
        toks=variant_tokens(r.get('canonical_tag') or '',base_can)
        if toks:return f"{base}（{' / '.join(toks)}）",'BASE_IDENTITY_PLUS_CANONICAL_VARIANT_FALLBACK'
    return (r.get('canonical_tag') or '').replace('_',' ').strip(),'CANONICAL_IDENTITY_FALLBACK'
def main():
    audited=done(); rows=[]
    for r in census():
        if r.get('row_id') in audited or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '') not in NOTES:continue
        if int(r.get('post_count') or 0)>=500:continue
        cur=(r.get('display_ja') or '').strip()
        if not cur or not JA.search(cur) or has_stronger_ja(r):continue
        cand={norm(x) for x in terms(r.get('existing_candidate_ja') or '')}
        if norm(cur) not in cand:continue
        proposed,mode=proposal(r)
        if not proposed or norm(proposed)==norm(cur):continue
        reason='REJECT_UNVERIFIED_SHORT_JA_CANDIDATE_'+mode
        rows.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':cur,'existing_candidate_ja':r.get('existing_candidate_ja') or '',
          'family_base_canonical':r.get('family_base_canonical') or '','family_base_display_ja':r.get('family_base_display_ja') or '',
          'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
          'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'','reason_code':reason,'confidence':'HIGH',
          'evidence_refs':'raw candidate only; no stronger Japanese existing/search/verified/source evidence',
          'audit_note':'短い日本語候補はraw candidate以外の裏付けがなく実サンプルでidentity誤りを確認済み。追加risk flagは根拠ではないため、確定base名＋canonical qualifier、なければcanonical由来表示へ戻す。','approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','existing_candidate_ja','family_base_canonical','family_base_display_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print({'rows':len(rows),'fix_display':len(rows),'production_modified':False})
if __name__=='__main__':main()
