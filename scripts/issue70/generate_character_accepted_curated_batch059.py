#!/usr/bin/env python3
"""Resolve all remaining explicitly curated ACCEPTED_AI Character rows.

A nonblank semantic curation note is treated as evidence that the current display
was deliberately selected. Preserve it unless there is a concrete identity defect:
- variant lost base identity => trusted family base + canonical variant; keep curated
  label/search as search evidence;
- disambiguator missing and display has no visible parenthetical context => append
  canonical qualifier;
- otherwise KEEP.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/'docs/issue70/audit'
DIAG=AUDIT/'character_accepted_curated_batch058_diagnostic.json'; OUT=AUDIT/'character_accepted_curated_batch059.csv'
SOURCE=ROOT/'docs/issue70/data/source/issue70_translation_source_with_relations.csv'; RESULTS=ROOT/'docs/issue70/data/runtime/issue70_translation_results.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}; RESOLVED={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]'); PAREN=re.compile(r'_\(([^()]*)\)')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def uniq(xs):
    out=[];seen=set()
    for x in xs:
        x=(x or '').strip()
        if not x:continue
        n=norm(x)
        if n in seen:continue
        seen.add(n);out.append(x)
    return out
def audit_map():
    out={}
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name or 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            rid=(r.get('row_id') or '').strip();v=(r.get('audit_verdict') or '').strip()
            if rid and v in VALID:out[rid]=r
    return out
def source_supports(display,s):
    nd=norm(display)
    for f in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'):
        for t in terms(s.get(f) or ''):
            if JA.search(t) and norm(t)==nd:return True
    return False
def parens(tag):return [x.strip() for x in PAREN.findall(tag or '') if x.strip()]
def variants(canonical,base):
    c=parens(canonical);b=Counter(parens(base));out=[]
    for x in c:
        if b[x]:b[x]-=1
        else:out.append(x.replace('_',' ').strip())
    return [x for x in out if x]
def effective_base(base_tag,by_tag,amap):
    if not base_tag or base_tag not in by_tag:return None,None
    bs,br=by_tag[base_tag];disp=(br.get('display_ja') or '').strip();dec=amap.get(bs['row_id'])
    if dec and (dec.get('audit_verdict') or '').strip() in RESOLVED:
        v=(dec.get('audit_verdict') or '').strip()
        if v in {'FIX_DISPLAY','FIX_BOTH'} and (dec.get('proposed_display_ja') or '').strip():disp=dec['proposed_display_ja'].strip()
        return (disp or None),'AUDIT_'+v
    if (br.get('translation_status') or '').strip()=='ACCEPTED_AI' and JA.search(disp) and source_supports(disp,bs):return disp,'DIRECT_SOURCE_SUPPORT'
    return None,None
def outrow(r,v,pd='',ps='',reason='',evidence='',note=''):
    return {'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '','display_ja':r.get('display_ja') or '','search_ja':r.get('search_ja') or '','translation_note':r.get('translation_note') or '','audit_verdict':v,'proposed_display_ja':pd,'proposed_search_ja':ps,'reason_code':reason,'confidence':'HIGH','evidence_refs':evidence,'audit_note':note,'approval_status':'PROPOSED'}
def main():
    d=json.loads(DIAG.read_text(encoding='utf-8'));amap=audit_map();done=set(amap)
    src=read(SOURCE);res=read(RESULTS);sb={r['row_id']:r for r in src};rb={r['row_id']:r for r in res};by_tag={}
    for rid,s in sb.items():
        cat=(s.get('category_name') or s.get('category') or '').strip()
        if cat in {'Character','4'}:by_tag[s['canonical_tag']]=(s,rb.get(rid,{}))
    out=[]
    for r in d['rows']:
        if r['row_id'] in done:continue
        flags={x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()};cur=(r.get('display_ja') or '').strip();search=(r.get('search_ja') or '').strip();base_tag=(r.get('family_base_canonical') or '').strip();base,basis=effective_base(base_tag,by_tag,amap);vt=variants(r['canonical_tag'],base_tag) if base_tag else []
        if 'VARIANT_DISPLAY_MISSING_BASE_IDENTITY' in flags and base and vt and norm(base) not in norm(cur):
            pd=f"{base}（{' / '.join(vt)}）";ps=' | '.join(uniq(terms(search)+[cur]))
            out.append(outrow(r,'FIX_BOTH',pd,ps,'CURATED_VARIANT_RESTORE_BASE_IDENTITY',f'explicit curation note; {basis}; canonical variant diff','監修済みvariant名は検索に保持し、表示だけ検証済み本体名＋canonical識別子へしてidentity欠落を解消。'));continue
        ctx=parens(r['canonical_tag'])
        if 'DISAMBIGUATOR_NOT_VISIBLE' in flags and ctx and not any(ch in cur for ch in '（('):
            pd=f"{cur}（{' / '.join(x.replace('_',' ') for x in ctx)}）"
            out.append(outrow(r,'FIX_DISPLAY',pd,'','CURATED_ADD_CANONICAL_DISAMBIGUATION','explicit semantic curation note + canonical qualifier','監修済み表示は維持し、表示だけでは欠けている識別文脈をcanonicalから追記。'));continue
        out.append(outrow(r,'KEEP','','','CURATED_ACCEPTED_SEMANTIC_DECISION','explicit nonblank semantic curation note','既存の監修理由が明記され、追加の具体的identity欠陥がないため監修結果をKEEP。'))
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'verdicts':dict(Counter(r['audit_verdict'] for r in out)),'production_modified':False})
if __name__=='__main__':main()
