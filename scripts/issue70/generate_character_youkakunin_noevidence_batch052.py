#!/usr/bin/env python3
"""Resolve Character '要確認' rows with Japanese display but zero preserved Japanese evidence.
Policy:
1) trusted/audited family base + canonical variant => FIX_DISPLAY to base + canonical qualifier;
2) otherwise post_count < 500 => FIX_DISPLAY to readable canonical fallback;
3) otherwise => NEEDS_EXTERNAL_CHECK.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/'docs/issue70/audit'
DIAG=AUDIT/'character_youkakunin_batch050_diagnostic.json'; OUT=AUDIT/'character_youkakunin_noevidence_batch052.csv'
SOURCE=ROOT/'docs/issue70/data/source/issue70_translation_source_with_relations.csv'; RESULTS=ROOT/'docs/issue70/data/runtime/issue70_translation_results.csv'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}; RESOLVED={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]'); PAREN=re.compile(r'_\(([^()]*)\)')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def audit_map():
    out={}
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name or 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            rid=(r.get('row_id') or '').strip(); v=(r.get('audit_verdict') or '').strip()
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
    c=parens(canonical); b=Counter(parens(base)); out=[]
    for x in c:
        if b[x]:b[x]-=1
        else:out.append(x.replace('_',' ').strip())
    return [x for x in out if x]
def fallback(tag):return (tag or '').replace('_',' ').strip()
def main():
    diag=json.loads(DIAG.read_text(encoding='utf-8')); amap=audit_map(); done=set(amap)
    src=read(SOURCE); res=read(RESULTS); src_by_id={r['row_id']:r for r in src}; res_by_id={r['row_id']:r for r in res}; by_tag={}
    for rid,s in src_by_id.items():
        cat=(s.get('category_name') or s.get('category') or '').strip()
        if cat in {'Character','4'}:by_tag[s['canonical_tag']]=(s,res_by_id.get(rid,{}))
    out=[]
    for r in diag['rows']:
        if r['diagnostic_bucket']!='JA_DISPLAY_NO_JA_EVIDENCE' or r['row_id'] in done:continue
        current=r['display_ja']; proposed=''; reason=''; verdict=''; confidence='HIGH'; evidence=''; note=''
        base_tag=(r.get('family_base_canonical') or '').strip(); toks=variants(r['canonical_tag'],base_tag) if base_tag else []
        if base_tag and toks and base_tag in by_tag:
            bs,br=by_tag[base_tag]; bdisp=(br.get('display_ja') or '').strip(); decision=amap.get(bs['row_id']); effective=bdisp; trusted=False; basis=''
            if decision and (decision.get('audit_verdict') or '').strip() in RESOLVED:
                v=(decision.get('audit_verdict') or '').strip(); trusted=True; basis='AUDIT_'+v
                if v in {'FIX_DISPLAY','FIX_BOTH'} and (decision.get('proposed_display_ja') or '').strip():effective=decision['proposed_display_ja'].strip()
            elif (br.get('translation_status') or '').strip()=='ACCEPTED_AI' and JA.search(bdisp) and source_supports(bdisp,bs):
                trusted=True; basis='DIRECT_SOURCE_SUPPORT'
            if trusted and effective:
                proposed=f"{effective}（{' / '.join(toks)}）"; verdict='FIX_DISPLAY'; reason='TRUSTED_BASE_PLUS_CANONICAL_VARIANT_NO_JA_EVIDENCE'; evidence=f'{basis}; exact family base + canonical qualifier diff'; note='現日本語variantは保存証拠ゼロ。検証済み基準キャラ名＋Danbooru canonical識別子へ戻す。'
        if not verdict:
            posts=int(r.get('post_count') or 0)
            if posts<500:
                proposed=fallback(r['canonical_tag']); verdict='FIX_DISPLAY'; reason='UNSUPPORTED_JA_TO_CANONICAL_FALLBACK'; evidence='zero preserved Japanese evidence; REVIEW_REQUIRED'; note='日本語表示を裏付ける保存証拠がないため、低影響行はidentity-safeなcanonical fallbackへ戻す。'
            else:
                verdict='NEEDS_EXTERNAL_CHECK'; reason='HIGH_IMPACT_UNSUPPORTED_JA_REQUIRES_EXTERNAL_CHECK'; confidence='MEDIUM'; evidence='zero preserved Japanese evidence; post_count >= 500'; note='高影響タグのため日本語を断定も破棄もせず、外部ソースで正式表記を確認する。'
        out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '','display_ja':current,'audit_verdict':verdict,'proposed_display_ja':proposed if verdict=='FIX_DISPLAY' else '','proposed_search_ja':'','reason_code':reason,'confidence':confidence,'evidence_refs':evidence,'audit_note':note,'approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'verdicts':dict(Counter(r['audit_verdict'] for r in out)),'production_modified':False})
if __name__=='__main__':main()
