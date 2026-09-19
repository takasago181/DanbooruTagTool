#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 028.

For REVIEW_REQUIRED parenthetical/variant rows whose Japanese variant label is
supported only by the raw candidate, preserve the verified family/base Japanese
identity and replace the unverified localized qualifier with the canonical
Danbooru variant qualifier(s). This gives an identity-safe mixed Japanese/Latin
fallback without inventing a translation.

Proposal-only; production Issue #70 data is never modified.
"""
from __future__ import annotations
import csv,re,shutil,subprocess,sys,unicodedata
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch028'
OUT=AUDIT/'character_canonical_variant_fallback_batch028.csv'
NOTES={
 'parenthetical candidate does not map cleanly to a copyright disambiguator',
 'variant/form rendering plausible but not independently verified',
}
JA_RE=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
PAREN_RE=re.compile(r'_\(([^()]*)\)')
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def done_ids():
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
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def split(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def has_stronger_ja(r):
    # raw existing_candidate_ja is explicitly the unverified lane and is not
    # accepted as evidence. Any Japanese in these fields blocks fallback.
    for field in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'):
        if JA_RE.search(r.get(field) or ''):return True
    return False
def candidate_terms(r):return {norm(x) for x in split(r.get('existing_candidate_ja') or '')}
def parenthetical_tokens(tag):return [x.strip() for x in PAREN_RE.findall(tag or '') if x.strip()]
def variant_tokens(canonical,base):
    c=parenthetical_tokens(canonical); b=Counter(parenthetical_tokens(base)); out=[]
    for tok in c:
        if b[tok]:b[tok]-=1
        else:out.append(tok)
    return out
def readable_token(tok):return tok.replace('_',' ').strip()
def main():
    done=done_ids();rows=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '') not in NOTES:continue
        base=(r.get('family_base_display_ja') or '').strip(); base_canonical=(r.get('family_base_canonical') or '').strip()
        if not base or not base_canonical or not JA_RE.search(base):continue
        if has_stronger_ja(r):continue
        current=(r.get('display_ja') or '').strip()
        if not current or norm(current) not in candidate_terms(r):continue
        toks=variant_tokens(r.get('canonical_tag') or '',base_canonical)
        toks=[readable_token(x) for x in toks if readable_token(x)]
        if not toks:continue
        qualifier=' / '.join(toks)
        proposed=f'{base}（{qualifier}）'
        if norm(proposed)==norm(current):continue
        rows.append({
          'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':current,'family_base_canonical':base_canonical,'family_base_display_ja':base,
          'canonical_variant_qualifier':qualifier,'existing_candidate_ja':r.get('existing_candidate_ja') or '',
          'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
          'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'',
          'reason_code':'BASE_IDENTITY_PLUS_CANONICAL_VARIANT_FALLBACK','confidence':'HIGH',
          'evidence_refs':'family_base_display_ja + canonical qualifier diff; raw Japanese candidate only',
          'audit_note':'基準キャラの日本語名は確定済みだがvariant日本語名はraw candidate以外の裏付けがない。未検証訳を残さず、基準名＋Danbooru canonical variant識別子へ戻してidentityと区別を両立。',
          'approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['row_id','canonical_tag','post_count','display_ja','family_base_canonical','family_base_display_ja','canonical_variant_qualifier','existing_candidate_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print({'rows':len(rows),'fix_display':len(rows),'production_modified':False})
    return 0
if __name__=='__main__':raise SystemExit(main())
