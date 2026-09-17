#!/usr/bin/env python3
"""Resolve all remaining Character '要確認' rows from batch054.

Conservative policies:
- EXACT_STRONG_WITH_IDENTITY_FLAG: preserve the source-backed Japanese label in
  search; make display identity-safe using a trusted family base when available,
  otherwise append canonical disambiguation context.
- STRONG_JA_EXISTS_BUT_DISPLAY_DIFFERS: if a trusted family base exists, use
  base + canonical variant and preserve strong Japanese evidence in search.
  Without a trusted base, high-impact rows go to external check; lower-impact
  rows use readable canonical display while retaining only strong source-backed
  Japanese search terms.
- NON_JA_DISPLAY: identity-safe Latin/original rendering is acceptable. Fix only
  raw canonical syntax or a missing canonical disambiguator; otherwise KEEP.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/'docs/issue70/audit'
DIAG=AUDIT/'character_youkakunin_final_batch054_diagnostic.json'; OUT=AUDIT/'character_youkakunin_final_batch055.csv'
SOURCE=ROOT/'docs/issue70/data/source/issue70_translation_source_with_relations.csv'; RESULTS=ROOT/'docs/issue70/data/runtime/issue70_translation_results.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}; RESOLVED={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]'); PAREN=re.compile(r'_\(([^()]*)\)')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def uniq(xs):
    out=[]; seen=set()
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
def stem(tag):
    m=PAREN.search(tag or '')
    return ((tag[:m.start()] if m else tag) or '').rstrip('_')
def variants(canonical,base):
    c=parens(canonical);b=Counter(parens(base));out=[]
    for x in c:
        if b[x]:b[x]-=1
        else:out.append(x.replace('_',' ').strip())
    return [x for x in out if x]
def readable(v):return (v or '').replace('_',' ').strip()
def strong_ja_values(r):
    vals=[]
    raw=(r.get('strong_ja_terms') or '')
    for part in raw.split(' | '):
        if ':' in part:
            _,v=part.split(':',1)
            if JA.search(v):vals.append(v.strip())
    return uniq(vals)
def effective_base(base_tag,by_tag,amap):
    if not base_tag or base_tag not in by_tag:return None,None
    bs,br=by_tag[base_tag];disp=(br.get('display_ja') or '').strip();decision=amap.get(bs['row_id'])
    if decision and (decision.get('audit_verdict') or '').strip() in RESOLVED:
        v=(decision.get('audit_verdict') or '').strip()
        if v in {'FIX_DISPLAY','FIX_BOTH'} and (decision.get('proposed_display_ja') or '').strip():disp=decision['proposed_display_ja'].strip()
        return (disp or None),'AUDIT_'+v
    if (br.get('translation_status') or '').strip()=='ACCEPTED_AI' and JA.search(disp) and source_supports(disp,bs):return disp,'DIRECT_SOURCE_SUPPORT'
    return None,None
def rowout(r,verdict,pdisp='',psearch='',reason='',confidence='HIGH',evidence='',note=''):
    return {'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '','display_ja':r.get('display_ja') or '','search_ja':r.get('search_ja') or '','audit_verdict':verdict,'proposed_display_ja':pdisp,'proposed_search_ja':psearch,'reason_code':reason,'confidence':confidence,'evidence_refs':evidence,'audit_note':note,'approval_status':'PROPOSED'}
def main():
    d=json.loads(DIAG.read_text(encoding='utf-8'));amap=audit_map();done=set(amap)
    src=read(SOURCE);res=read(RESULTS);src_by_id={r['row_id']:r for r in src};res_by_id={r['row_id']:r for r in res};by_tag={}
    for rid,s in src_by_id.items():
        cat=(s.get('category_name') or s.get('category') or '').strip()
        if cat in {'Character','4'}:by_tag[s['canonical_tag']]=(s,res_by_id.get(rid,{}))
    out=[]
    for r in d['rows']:
        if r['row_id'] in done:continue
        bucket=r['diagnostic_bucket']; flags={x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}; current=(r.get('display_ja') or '').strip(); search=(r.get('search_ja') or '').strip(); posts=int(r.get('post_count') or 0)
        base_tag=(r.get('family_base_canonical') or '').strip();base,basis=effective_base(base_tag,by_tag,amap);vt=variants(r['canonical_tag'],base_tag) if base_tag else []
        strong=strong_ja_values(r)
        if bucket=='EXACT_STRONG_WITH_IDENTITY_FLAG':
            if base and vt:
                proposed=f"{base}（{' / '.join(vt)}）"
                psearch=' | '.join(uniq(terms(search)+[current]+strong))
                out.append(rowout(r,'FIX_BOTH',proposed,psearch,'SOURCE_LABEL_PRESERVED_WITH_TRUSTED_BASE_IDENTITY','HIGH',f'{basis}; exact strong Japanese label; canonical variant diff','強い日本語ラベルは検索に保持し、表示は検証済み本体名＋canonical識別子で誰のvariantか明示。'))
            else:
                ctx=parens(r['canonical_tag'])
                proposed=current if not ctx else f"{current}（{' / '.join(x.replace('_',' ') for x in ctx)}）"
                out.append(rowout(r,'FIX_DISPLAY',proposed,'','SOURCE_LABEL_PLUS_CANONICAL_DISAMBIGUATION','HIGH','current display exactly matches strong Japanese evidence + canonical qualifier','強い日本語表示は保持し、同名/識別子欠落だけcanonical文脈を付与して解消。'))
            continue
        if bucket=='STRONG_JA_EXISTS_BUT_DISPLAY_DIFFERS':
            if base and vt:
                proposed=f"{base}（{' / '.join(vt)}）";psearch=' | '.join(uniq(terms(search)+[current]+strong))
                out.append(rowout(r,'FIX_BOTH',proposed,psearch,'TRUSTED_BASE_CANONICAL_VARIANT_WITH_SOURCE_SEARCH','HIGH',f'{basis}; strong preserved Japanese search evidence','現表示を断定せず検証済み本体名＋canonical variantへ。保存済み日本語証拠は検索語として維持。'))
            elif posts>=500:
                out.append(rowout(r,'NEEDS_EXTERNAL_CHECK','','','HIGH_IMPACT_DISPLAY_CONFLICTS_WITH_STRONG_JA_EVIDENCE','MEDIUM','current display differs from preserved strong Japanese evidence; post_count >= 500','高影響かつ現表示と強い日本語証拠が不一致。どちらを表示正本にするか外部確認。'))
            else:
                pdisp=readable(r['canonical_tag']);psearch=' | '.join(uniq(strong))
                out.append(rowout(r,'FIX_BOTH',pdisp,psearch,'CANONICAL_DISPLAY_WITH_SOURCE_BACKED_JA_SEARCH','HIGH','display conflicts with source-backed Japanese terms; low-impact','表示はidentity-safeなcanonicalへ戻し、強い日本語証拠だけを検索語として残す。'))
            continue
        if bucket=='NON_JA_DISPLAY':
            raw_exact=norm(current)==norm(r['canonical_tag']) or '_(' in current
            ctx=parens(r['canonical_tag'])
            if raw_exact:
                out.append(rowout(r,'FIX_DISPLAY',readable(r['canonical_tag']),'','NORMALIZE_RAW_CANONICAL_DISPLAY','HIGH','current display is raw canonical syntax','意味は変えずraw tag構文だけ読みやすいcanonical表示へ整形。'))
            elif 'DISAMBIGUATOR_NOT_VISIBLE' in flags and ctx:
                proposed=f"{current}（{' / '.join(x.replace('_',' ') for x in ctx)}）"
                out.append(rowout(r,'FIX_DISPLAY',proposed,'','LATIN_IDENTITY_PLUS_CANONICAL_DISAMBIGUATION','HIGH','identity-safe Latin/original display + canonical qualifier','英字固有名は保持し、欠けているcanonical識別子だけ表示へ追加。'))
            else:
                out.append(rowout(r,'KEEP','','','IDENTITY_SAFE_ORIGINAL_LATIN_FALLBACK','HIGH','human-readable original/Latin display; no proven semantic defect','日本語根拠がなくても英字固有名/既存原語表示としてidentity-safe。推測翻訳せずKEEP。'))
            continue
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'verdicts':dict(Counter(r['audit_verdict'] for r in out)),'production_modified':False})
if __name__=='__main__':main()
