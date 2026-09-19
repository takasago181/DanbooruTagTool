#!/usr/bin/env python3
"""Resolve remaining ACCEPTED_AI Character rows with blank translation_note.

Blank-note Accepted rows have no explicit semantic curation trail. Apply a
conservative evidence-first policy:
- trusted family base => base identity + canonical variant; preserve only strong
  source-backed Japanese search terms;
- no trusted family base, strong Japanese evidence differs => low-impact canonical
  display + strong source-backed search, high-impact external check;
- no strong Japanese evidence => low-impact canonical display and remove unsupported
  Japanese search terms, high-impact external check;
- readable non-Japanese originals are kept unless canonical context is missing.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/'docs/issue70/audit'
DIAG=AUDIT/'character_accepted_remaining_batch056_diagnostic.json'; OUT=AUDIT/'character_accepted_blank_batch057.csv'
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
def readable(v):return (v or '').replace('_',' ').strip()
def strong_values(r):
    vals=[]
    for part in (r.get('strong_ja_terms') or '').split(' | '):
        if ':' in part:
            _,v=part.split(':',1)
            if JA.search(v):vals.append(v.strip())
    return uniq(vals)
def nonja_search(v):return uniq([x for x in terms(v) if not JA.search(x)])
def effective_base(base_tag,by_tag,amap):
    if not base_tag or base_tag not in by_tag:return None,None
    bs,br=by_tag[base_tag];disp=(br.get('display_ja') or '').strip();decision=amap.get(bs['row_id'])
    if decision and (decision.get('audit_verdict') or '').strip() in RESOLVED:
        vv=(decision.get('audit_verdict') or '').strip()
        if vv in {'FIX_DISPLAY','FIX_BOTH'} and (decision.get('proposed_display_ja') or '').strip():disp=decision['proposed_display_ja'].strip()
        return (disp or None),'AUDIT_'+vv
    if (br.get('translation_status') or '').strip()=='ACCEPTED_AI' and JA.search(disp) and source_supports(disp,bs):return disp,'DIRECT_SOURCE_SUPPORT'
    return None,None
def outrow(r,verdict,pdisp='',psearch='',reason='',conf='HIGH',evidence='',note=''):
    return {'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '','display_ja':r.get('display_ja') or '','search_ja':r.get('search_ja') or '','audit_verdict':verdict,'proposed_display_ja':pdisp,'proposed_search_ja':psearch,'reason_code':reason,'confidence':conf,'evidence_refs':evidence,'audit_note':note,'approval_status':'PROPOSED'}
def main():
    d=json.loads(DIAG.read_text(encoding='utf-8'));amap=audit_map();done=set(amap)
    src=read(SOURCE);res=read(RESULTS);src_by={r['row_id']:r for r in src};res_by={r['row_id']:r for r in res};by_tag={}
    for rid,s in src_by.items():
        cat=(s.get('category_name') or s.get('category') or '').strip()
        if cat in {'Character','4'}:by_tag[s['canonical_tag']]=(s,res_by.get(rid,{}))
    out=[]
    for r in d['rows']:
        if r['row_id'] in done or (r.get('translation_note') or '').strip():continue
        bucket=r['diagnostic_bucket'];posts=int(r.get('post_count') or 0);strong=strong_values(r);base_tag=(r.get('family_base_canonical') or '').strip();base,basis=effective_base(base_tag,by_tag,amap);vt=variants(r['canonical_tag'],base_tag) if base_tag else []
        if base and vt:
            pdisp=f"{base}（{' / '.join(vt)}）"; ps=' | '.join(uniq(nonja_search(r.get('search_ja') or '')+strong))
            if strong:
                out.append(outrow(r,'FIX_BOTH',pdisp,ps,'BLANK_ACCEPTED_TRUSTED_BASE_WITH_SOURCE_SEARCH','HIGH',f'{basis}; canonical variant + strong Japanese source evidence','注記なしAccepted。表示は検証済み本体名＋canonical variantへ統一し、強い日本語証拠だけ検索に保持。'))
            else:
                out.append(outrow(r,'FIX_BOTH',pdisp,ps,'BLANK_ACCEPTED_TRUSTED_BASE_NO_JA_EVIDENCE','HIGH',f'{basis}; canonical variant; no strong Japanese evidence','注記なしAcceptedかつvariant日本語の強い証拠なし。検証済み本体名＋canonical variantへ戻し、未裏付け日本語検索語を除去。'))
            continue
        if bucket=='NON_JA_NO_FAMILY':
            flags={x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()};ctx=parens(r['canonical_tag']);cur=(r.get('display_ja') or '').strip()
            if 'DISAMBIGUATOR_NOT_VISIBLE' in flags and ctx:
                out.append(outrow(r,'FIX_DISPLAY',f"{cur}（{' / '.join(x.replace('_',' ') for x in ctx)}）",'','BLANK_ACCEPTED_LATIN_ADD_CONTEXT','HIGH','identity-safe original display + canonical context','英字固有名は保持し、欠けている識別文脈だけcanonicalから追加。'))
            else:out.append(outrow(r,'KEEP','','','BLANK_ACCEPTED_IDENTITY_SAFE_LATIN','HIGH','identity-safe original/Latin display; no proven semantic defect','日本語を推測せず原語表示としてKEEP。'))
            continue
        if posts>=500:
            out.append(outrow(r,'NEEDS_EXTERNAL_CHECK','','','BLANK_ACCEPTED_HIGH_IMPACT_EVIDENCE_GAP','MEDIUM','blank semantic note and unresolved Japanese evidence; post_count >= 500','高影響かつ注記なし。既存日本語を破棄する前に外部確認。'))
            continue
        pdisp=readable(r['canonical_tag'])
        if strong:
            ps=' | '.join(uniq(nonja_search(r.get('search_ja') or '')+strong))
            out.append(outrow(r,'FIX_BOTH',pdisp,ps,'BLANK_ACCEPTED_CANONICAL_WITH_SOURCE_JA_SEARCH','HIGH','current Japanese display unsupported; strong Japanese evidence exists only as alternate source term','表示はcanonicalへ戻し、保存済みの強い日本語証拠のみ検索語として残す。'))
        else:
            ps=' | '.join(nonja_search(r.get('search_ja') or ''))
            out.append(outrow(r,'FIX_BOTH',pdisp,ps,'BLANK_ACCEPTED_UNSUPPORTED_JA_TO_CANONICAL','HIGH','no strong Japanese evidence; blank semantic note','注記も強い日本語証拠もないため、低影響行はcanonical表示へ戻し未裏付け日本語検索語も除去。'))
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'verdicts':dict(Counter(r['audit_verdict'] for r in out)),'production_modified':False})
if __name__=='__main__':main()
