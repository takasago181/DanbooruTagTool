#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 047.

For remaining ACCEPTED_AI Character rows marked as a single Japanese candidate,
when the current display is supported only by the raw candidate and a Japanese
family/base identity is available, replace the unverified localized variant label
with family base identity + canonical Danbooru variant qualifier(s).

This is the Accepted counterpart of batch028. Proposal-only; production data is
never modified.
"""
from __future__ import annotations
import csv,re,shutil,subprocess,sys,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch047'
OUT=AUDIT/'character_accepted_variant_identity_batch047.csv'
NOTE='single Japanese candidate with no conflicting evidence'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]'); PAREN=re.compile(r'_\(([^()]*)\)')

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def audited():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name or 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():ids.add(r['row_id'].strip())
    return ids
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def has_stronger_ja(r):
    return any(JA.search(r.get(f) or '') for f in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'))
def parens(tag):return [x.strip() for x in PAREN.findall(tag or '') if x.strip()]
def variant_tokens(canonical,base):
    c=parens(canonical); b=Counter(parens(base)); out=[]
    for x in c:
        if b[x]:b[x]-=1
        else:out.append(x.replace('_',' ').strip())
    return [x for x in out if x]
def main():
    done=audited(); out=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='ACCEPTED_AI' or (r.get('translation_note') or '')!=NOTE:continue
        current=(r.get('display_ja') or '').strip(); base=(r.get('family_base_display_ja') or '').strip(); base_tag=(r.get('family_base_canonical') or '').strip()
        if not current or not base or not base_tag or not JA.search(base):continue
        if has_stronger_ja(r):continue
        raw={norm(x) for x in terms(r.get('existing_candidate_ja') or '')}
        if norm(current) not in raw:continue
        toks=variant_tokens(r.get('canonical_tag') or '',base_tag)
        if not toks:continue
        qualifier=' / '.join(toks); proposed=f'{base}（{qualifier}）'
        if norm(proposed)==norm(current):continue
        out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':current,'family_base_canonical':base_tag,'family_base_display_ja':base,
          'canonical_variant_qualifier':qualifier,'existing_candidate_ja':r.get('existing_candidate_ja') or '',
          'risk_flags':r.get('risk_flags') or '','audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'',
          'reason_code':'ACCEPTED_BASE_IDENTITY_PLUS_CANONICAL_VARIANT_FALLBACK','confidence':'HIGH',
          'evidence_refs':'family_base_display_ja + canonical qualifier diff; current Japanese variant raw candidate only',
          'audit_note':'Accepted判定済みでもvariant側の日本語はraw candidateのみ。基準キャラ日本語名を保持し、未検証の衣装/形態訳はDanbooru canonical識別子へ戻してidentityを失わない。','approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','family_base_canonical','family_base_display_ja','canonical_variant_qualifier','existing_candidate_ja','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'fix_display':len(out),'production_modified':False})
if __name__=='__main__':main()
