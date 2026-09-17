#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 036.

For remaining REVIEW_REQUIRED parenthetical/variant rows, derive an exact shorter
Character base tag. Reuse the base only when it has a trustworthy Japanese name:
- the base row is already resolved by this semantic audit, or
- its Japanese display is directly supported by non-candidate source evidence.

The current variant row must still satisfy the batch028 safety rule: its display is
only the raw Japanese candidate and has no stronger Japanese source evidence.
Then propose trusted base display + canonical Danbooru qualifier(s).
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,itertools,re,shutil,subprocess,sys,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch036'
OUT=AUDIT/'character_derived_base_variant_batch036.csv'
SOURCE=ROOT/'docs/issue70/data/source/issue70_translation_source_with_relations.csv'
RESULTS=ROOT/'docs/issue70/data/runtime/issue70_translation_results.csv'
NOTES={'parenthetical candidate does not map cleanly to a copyright disambiguator','variant/form rendering plausible but not independently verified'}
RESOLVED={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH'}
VALID=RESOLVED|{'NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]'); GROUP=re.compile(r'_\(([^()]*)\)')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def audit_map():
    out={}
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            rid=(r.get('row_id') or '').strip(); v=(r.get('audit_verdict') or '').strip()
            if rid and v in VALID:out[rid]=r
    return out
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def split_tag(tag):
    m=list(GROUP.finditer(tag or '')); stem=(tag[:m[0].start()] if m else tag).rstrip('_')
    return stem,[x.group(1) for x in m]
def rebuild(stem,groups):return stem+''.join(f'_({g})' for g in groups)
def source_supports(display,s):
    nd=norm(display)
    for f in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'):
        for t in terms(s.get(f) or ''):
            if JA.search(t) and norm(t)==nd:return True
    return False
def has_stronger_current_ja(r):
    return any(JA.search(r.get(f) or '') for f in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'))
def parens(tag):return [x.strip() for x in GROUP.findall(tag or '') if x.strip()]
def variant_tokens(canonical,base):
    c=parens(canonical); b=Counter(parens(base)); out=[]
    for x in c:
        if b[x]:b[x]-=1
        else:out.append(x.replace('_',' ').strip())
    return [x for x in out if x]
def main():
    src=read(SOURCE); res=read(RESULTS); amap=audit_map(); audited=set(amap)
    src_by_id={r['row_id']:r for r in src}; res_by_id={r['row_id']:r for r in res}; char_by_tag={}
    for rid,s in src_by_id.items():
        cat=(s.get('category_name') or s.get('category') or '').strip()
        if cat in {'Character','4'}:char_by_tag[s['canonical_tag']]=(s,res_by_id.get(rid,{}))
    out=[]
    for r in census():
        if r.get('row_id') in audited or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '') not in NOTES:continue
        if (r.get('family_base_display_ja') or '').strip():continue
        current=(r.get('display_ja') or '').strip(); raw={norm(x) for x in terms(r.get('existing_candidate_ja') or '')}
        if not current or norm(current) not in raw or has_stronger_current_ja(r):continue
        stem,gs=split_tag(r['canonical_tag']); candidates=[]
        for keep_n in range(len(gs)-1,-1,-1):
            for idxs in itertools.combinations(range(len(gs)),keep_n):
                tag=rebuild(stem,[gs[i] for i in idxs]); hit=char_by_tag.get(tag)
                if not hit:continue
                bs,br=hit; bdisp=(br.get('display_ja') or '').strip(); status=(br.get('translation_status') or '').strip()
                if status=='ACCEPTED_AI' and JA.search(bdisp):candidates.append((bs,br,bdisp,tag))
            if candidates:break
        if len(candidates)!=1:continue
        bs,br,bdisp,btag=candidates[0]; decision=amap.get(bs['row_id']); effective=bdisp; basis=''
        if decision and (decision.get('audit_verdict') or '').strip() in RESOLVED:
            v=(decision.get('audit_verdict') or '').strip(); basis='AUDIT_'+v
            if v in {'FIX_DISPLAY','FIX_BOTH'} and (decision.get('proposed_display_ja') or '').strip():effective=decision['proposed_display_ja'].strip()
        elif source_supports(bdisp,bs):basis='DIRECT_SOURCE_SUPPORT'
        else:continue
        toks=variant_tokens(r['canonical_tag'],btag)
        if not toks:continue
        qualifier=' / '.join(toks); proposed=f'{effective}（{qualifier}）'
        if norm(proposed)==norm(current):continue
        out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':current,'base_row_id':bs['row_id'],'base_canonical_tag':btag,'base_effective_display_ja':effective,
          'base_trust_basis':basis,'canonical_variant_qualifier':qualifier,'existing_candidate_ja':r.get('existing_candidate_ja') or '',
          'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
          'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'',
          'reason_code':'DERIVED_TRUSTED_BASE_PLUS_CANONICAL_VARIANT_FALLBACK','confidence':'HIGH',
          'evidence_refs':'exact shorter Character canonical + trusted base Japanese identity + canonical qualifier diff; current row raw candidate only',
          'audit_note':'family_base欠落をexact canonical逆引きで復元。親日本語名をaudit/sourceで再検証し、未検証variant訳は親名＋Danbooru canonical識別子へ戻す。','approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','base_row_id','base_canonical_tag','base_effective_display_ja','base_trust_basis','canonical_variant_qualifier','existing_candidate_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'fix_display':len(out),'production_modified':False})
if __name__=='__main__':main()
