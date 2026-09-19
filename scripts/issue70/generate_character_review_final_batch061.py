#!/usr/bin/env python3
"""Resolve every remaining REVIEW_REQUIRED Character row from batch060.

Evidence-first final Character policy:
- exact strong Japanese evidence with no identity defect => KEEP;
- trusted family base => base identity + canonical variant, preserving only strong
  source-backed Japanese search evidence;
- no trusted family base => low-impact (<500) readable canonical display, retaining
  only strong Japanese source terms; high-impact => external check;
- identity-safe original/Latin fallback is allowed when no Japanese display is used;
- exact strong labels with identity risk retain the label in search and gain canonical
  identity context in display.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];AUDIT=ROOT/'docs/issue70/audit';DIAG=AUDIT/'character_review_remaining_batch060_diagnostic.json';OUT=AUDIT/'character_review_final_batch061.csv'
SOURCE=ROOT/'docs/issue70/data/source/issue70_translation_source_with_relations.csv';RESULTS=ROOT/'docs/issue70/data/runtime/issue70_translation_results.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'};RESOLVED={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]');PAREN=re.compile(r'_\(([^()]*)\)')
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
def nonja(v):return uniq([x for x in terms(v) if not JA.search(x)])
def effective_base(base_tag,by_tag,amap):
    if not base_tag or base_tag not in by_tag:return None,None
    bs,br=by_tag[base_tag];disp=(br.get('display_ja') or '').strip();dec=amap.get(bs['row_id'])
    if dec and (dec.get('audit_verdict') or '').strip() in RESOLVED:
        vv=(dec.get('audit_verdict') or '').strip()
        if vv in {'FIX_DISPLAY','FIX_BOTH'} and (dec.get('proposed_display_ja') or '').strip():disp=dec['proposed_display_ja'].strip()
        return (disp or None),'AUDIT_'+vv
    if (br.get('translation_status') or '').strip()=='ACCEPTED_AI' and JA.search(disp) and source_supports(disp,bs):return disp,'DIRECT_SOURCE_SUPPORT'
    return None,None
def outrow(r,v,pd='',ps='',reason='',conf='HIGH',evidence='',note=''):
    return {'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '','display_ja':r.get('display_ja') or '','search_ja':r.get('search_ja') or '','translation_note':r.get('translation_note') or '','audit_verdict':v,'proposed_display_ja':pd,'proposed_search_ja':ps,'reason_code':reason,'confidence':conf,'evidence_refs':evidence,'audit_note':note,'approval_status':'PROPOSED'}
def main():
    d=json.loads(DIAG.read_text(encoding='utf-8'));amap=audit_map();done=set(amap);src=read(SOURCE);res=read(RESULTS);sb={r['row_id']:r for r in src};rb={r['row_id']:r for r in res};by_tag={}
    for rid,s in sb.items():
        cat=(s.get('category_name') or s.get('category') or '').strip()
        if cat in {'Character','4'}:by_tag[s['canonical_tag']]=(s,rb.get(rid,{}))
    out=[]
    for r in d['rows']:
        if r['row_id'] in done:continue
        bucket=r['diagnostic_bucket'];posts=int(r.get('post_count') or 0);cur=(r.get('display_ja') or '').strip();search=(r.get('search_ja') or '').strip();flags={x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()};strong=strong_values(r);base_tag=(r.get('family_base_canonical') or '').strip();base,basis=effective_base(base_tag,by_tag,amap);vt=variants(r['canonical_tag'],base_tag) if base_tag else []
        if bucket=='EXACT_STRONG_SAFE':
            out.append(outrow(r,'KEEP','','','REVIEW_EXACT_STRONG_JA_SAFE','HIGH','current display exactly matches strong preserved Japanese evidence','ReviewRequiredだったが強い日本語証拠と完全一致し具体的identity欠陥もないためKEEP。'));continue
        if bucket=='EXACT_STRONG_IDENTITY_RISK':
            if base and vt:
                pd=f"{base}（{' / '.join(vt)}）";ps=' | '.join(uniq(nonja(search)+[cur]+strong))
                out.append(outrow(r,'FIX_BOTH',pd,ps,'REVIEW_STRONG_LABEL_RESTORE_BASE_IDENTITY','HIGH',f'{basis}; exact strong Japanese label + canonical variant','強い日本語ラベルは検索に保持し、表示を検証済み本体名＋canonical variantへしてidentity欠落を解消。'));continue
            ctx=parens(r['canonical_tag'])
            if ctx:
                pd=f"{cur}（{' / '.join(x.replace('_',' ') for x in ctx)}）"
                out.append(outrow(r,'FIX_DISPLAY',pd,'','REVIEW_STRONG_LABEL_ADD_CANONICAL_CONTEXT','HIGH','exact strong Japanese display + canonical disambiguator','強い日本語表示は維持し、欠けている識別文脈のみcanonicalから付与。'));continue
            out.append(outrow(r,'NEEDS_EXTERNAL_CHECK','','','REVIEW_STRONG_LABEL_IDENTITY_RISK_NO_SAFE_CONTEXT','MEDIUM','exact strong Japanese evidence but identity collision has no safe canonical qualifier','日本語自体は強く支持されるが同名識別を安全に付けられないため外部確認。'));continue
        if base and vt and bucket in {'STRONG_DIFFERS_WITH_FAMILY','NO_STRONG_JA_WITH_FAMILY','NON_JA_WITH_FAMILY'}:
            pd=f"{base}（{' / '.join(vt)}）";ps=' | '.join(uniq(nonja(search)+strong))
            if bucket=='STRONG_DIFFERS_WITH_FAMILY':reason='REVIEW_TRUSTED_BASE_WITH_SOURCE_JA_SEARCH';ev=f'{basis}; canonical variant + strong Japanese source evidence';note='表示は検証済み本体名＋canonical variantへ。強い日本語証拠だけ検索に維持。'
            elif bucket=='NO_STRONG_JA_WITH_FAMILY':reason='REVIEW_TRUSTED_BASE_NO_STRONG_JA';ev=f'{basis}; canonical variant; no strong Japanese evidence';note='未検証の日本語variant表示を検証済み本体名＋canonical variantへ戻し、裏付けのない日本語検索語を除去。'
            else:reason='REVIEW_NON_JA_VARIANT_TO_TRUSTED_BASE';ev=f'{basis}; canonical variant';note='非日本語variant表示を検証済み本体名＋canonical variantへ統一。'
            out.append(outrow(r,'FIX_BOTH',pd,ps,reason,'HIGH',ev,note));continue
        if bucket=='NON_JA_NO_FAMILY':
            ctx=parens(r['canonical_tag']);raw=norm(cur)==norm(r['canonical_tag']) or '_(' in cur
            if raw:
                out.append(outrow(r,'FIX_DISPLAY',readable(r['canonical_tag']),'','REVIEW_NORMALIZE_RAW_CANONICAL','HIGH','raw canonical syntax','意味を変えずraw tag構文だけ読みやすく整形。'));continue
            if 'DISAMBIGUATOR_NOT_VISIBLE' in flags and ctx and not any(ch in cur for ch in '（('):
                out.append(outrow(r,'FIX_DISPLAY',f"{cur}（{' / '.join(x.replace('_',' ') for x in ctx)}）",'','REVIEW_LATIN_ADD_CANONICAL_CONTEXT','HIGH','identity-safe original/Latin display + canonical qualifier','原語表示を維持し識別文脈のみcanonicalから付与。'));continue
            out.append(outrow(r,'KEEP','','','REVIEW_IDENTITY_SAFE_ORIGINAL_LATIN','HIGH','identity-safe original/Latin display; no proven semantic defect','日本語を推測せず原語表示としてKEEP。'));continue
        if posts>=500:
            out.append(outrow(r,'NEEDS_EXTERNAL_CHECK','','','REVIEW_HIGH_IMPACT_UNRESOLVED_EVIDENCE','MEDIUM','no trusted family-base resolution; post_count >= 500','高影響かつ日本語表示の確証不足。破棄・断定せず外部確認。'));continue
        pd=readable(r['canonical_tag'])
        if strong:
            ps=' | '.join(uniq(nonja(search)+strong));out.append(outrow(r,'FIX_BOTH',pd,ps,'REVIEW_CANONICAL_WITH_SOURCE_JA_SEARCH','HIGH','no trusted base; strong Japanese evidence available as search terms','表示はcanonicalへ戻し、強い日本語証拠のみ検索語として保持。'))
        else:
            ps=' | '.join(nonja(search));out.append(outrow(r,'FIX_BOTH',pd,ps,'REVIEW_UNSUPPORTED_JA_TO_CANONICAL','HIGH','no trusted base and no strong Japanese evidence','低影響かつ確証不足の日本語を断定せずcanonical表示へ戻し、未裏付け日本語検索語を除去。'))
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'verdicts':dict(Counter(r['audit_verdict'] for r in out)),'production_modified':False})
if __name__=='__main__':main()
