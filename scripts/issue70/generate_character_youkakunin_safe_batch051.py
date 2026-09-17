#!/usr/bin/env python3
"""Resolve the mechanically safe subset of Character '要確認' diagnostic batch050.
- EXACT_STRONG_NO_IDENTITY_FLAG => KEEP
- RAW_ONLY_WITH_FAMILY_BASE => FIX_DISPLAY using base identity + canonical qualifier
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; AUDIT=ROOT/'docs/issue70/audit'
INP=AUDIT/'character_youkakunin_batch050_diagnostic.json'; OUT=AUDIT/'character_youkakunin_safe_batch051.csv'
PAREN=re.compile(r'_\(([^()]*)\)')
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def parens(tag):return [x.strip() for x in PAREN.findall(tag or '') if x.strip()]
def variants(canonical,base):
    c=parens(canonical); b=Counter(parens(base)); out=[]
    for x in c:
        if b[x]:b[x]-=1
        else:out.append(x.replace('_',' ').strip())
    return [x for x in out if x]
def main():
    d=json.loads(INP.read_text(encoding='utf-8')); out=[]
    for r in d['rows']:
        b=r['diagnostic_bucket']
        if b=='EXACT_STRONG_NO_IDENTITY_FLAG':
            out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],'display_ja':r['display_ja'],'audit_verdict':'KEEP','proposed_display_ja':'','proposed_search_ja':'','reason_code':'EXACT_STRONG_JA_EVIDENCE_NO_IDENTITY_DEFECT','confidence':'HIGH','evidence_refs':r.get('strong_exact_terms') or 'exact strong Japanese evidence','audit_note':'現表示が保存済みの強い日本語証拠と完全一致し、重複・識別子欠落・variant identity欠落等の警告もないためKEEP。','approval_status':'PROPOSED'})
        elif b=='RAW_ONLY_WITH_FAMILY_BASE':
            base=(r.get('family_base_display_ja') or '').strip(); base_tag=(r.get('family_base_canonical') or '').strip(); toks=variants(r['canonical_tag'],base_tag)
            if not base or not base_tag or not toks:continue
            proposed=f"{base}（{' / '.join(toks)}）"
            if norm(proposed)==norm(r['display_ja']):continue
            out.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],'display_ja':r['display_ja'],'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'','reason_code':'YOUKAKUNIN_BASE_IDENTITY_PLUS_CANONICAL_VARIANT','confidence':'HIGH','evidence_refs':'family_base_display_ja + canonical qualifier; current display raw candidate only','audit_note':'raw候補しかないvariant日本語を断定せず、基準キャラ日本語名＋Danbooru canonical識別子へ戻してidentityを保持。','approval_status':'PROPOSED'})
    out.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    print({'rows':len(out),'keep':sum(r['audit_verdict']=='KEEP' for r in out),'fix_display':sum(r['audit_verdict']=='FIX_DISPLAY' for r in out),'production_modified':False})
if __name__=='__main__':main()
