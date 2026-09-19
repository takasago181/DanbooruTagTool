#!/usr/bin/env python3
"""Resolve the safe remainder of Character '要確認' batch050.

Policies:
- RAW_ONLY_NO_FAMILY_BASE: unsupported Japanese raw candidate. Low-impact (<500)
  => canonical fallback; high-impact => external check.
- NON_JA_DISPLAY with trusted Japanese family base and canonical variant diff
  => base Japanese identity + canonical qualifier.
Other buckets are left for focused semantic handling.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/'docs/issue70/audit'
DIAG=AUDIT/'character_youkakunin_batch050_diagnostic.json'; OUT=AUDIT/'character_youkakunin_remaining_batch053.csv'
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
        if r['row_id'] in done:continue
        bucket=r['diagnostic_bucket']; posts=int(r.get('post_count') or 0)
        if bucket=='RAW_ONLY_NO_FAMILY_BASE':
            if posts<500:
                out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],'display_ja':r['display_ja'],'audit_verdict':'FIX_DISPLAY','proposed_display_ja':fallback(r['canonical_tag']),'proposed_search_ja':'','reason_code':'RAW_ONLY_NO_BASE_TO_CANONICAL_FALLBACK','confidence':'HIGH','evidence_refs':'raw Japanese candidate only; no trusted family base','audit_note':'raw候補しか裏付けのない日本語を断定せず、低影響行はcanonical由来表示へ戻す。','approval_status':'PROPOSED'})
            else:
                out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],'display_ja':r['display_ja'],'audit_verdict':'NEEDS_EXTERNAL_CHECK','proposed_display_ja':'','proposed_search_ja':'','reason_code':'HIGH_IMPACT_RAW_ONLY_NO_BASE_EXTERNAL_CHECK','confidence':'MEDIUM','evidence_refs':'raw Japanese candidate only; no trusted family base; post_count >= 500','audit_note':'高影響かつ日本語根拠がraw候補のみ。canonical fallbackで日本語名を捨てる前に外部確認する。','approval_status':'PROPOSED'})
            continue
        if bucket!='NON_JA_DISPLAY':continue
        base_tag=(r.get('family_base_canonical') or '').strip()
        if not base_tag or base_tag not in by_tag:continue
        toks=variants(r['canonical_tag'],base_tag)
        if not toks:continue
        bs,br=by_tag[base_tag]; bdisp=(br.get('display_ja') or '').strip(); decision=amap.get(bs['row_id']); effective=bdisp; trusted=False; basis=''
        if decision and (decision.get('audit_verdict') or '').strip() in RESOLVED:
            v=(decision.get('audit_verdict') or '').strip(); trusted=True; basis='AUDIT_'+v
            if v in {'FIX_DISPLAY','FIX_BOTH'} and (decision.get('proposed_display_ja') or '').strip():effective=decision['proposed_display_ja'].strip()
        elif (br.get('translation_status') or '').strip()=='ACCEPTED_AI' and JA.search(bdisp) and source_supports(bdisp,bs):
            trusted=True; basis='DIRECT_SOURCE_SUPPORT'
        if not trusted or not effective:continue
        proposed=f"{effective}（{' / '.join(toks)}）"
        if norm(proposed)==norm(r['display_ja']):continue
        out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],'display_ja':r['display_ja'],'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'','reason_code':'NON_JA_VARIANT_TO_TRUSTED_BASE_PLUS_CANONICAL','confidence':'HIGH','evidence_refs':f'{basis}; exact family base + canonical qualifier diff','audit_note':'raw/canonical風の非日本語表示を、検証済み基準キャラ日本語名＋canonical variant識別子へ直す。','approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'verdicts':dict(Counter(r['audit_verdict'] for r in out)),'production_modified':False})
if __name__=='__main__':main()
