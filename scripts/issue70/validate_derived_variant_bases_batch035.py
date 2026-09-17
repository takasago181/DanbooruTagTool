#!/usr/bin/env python3
"""Validate the 153 derived Character base candidates from batch034.

A derived base is trusted for bulk reuse only when either:
1) its own Issue70 audit row is already resolved as KEEP/FIX_DISPLAY/FIX_SEARCH/FIX_BOTH, or
2) its current Japanese display is directly supported by non-candidate source evidence
   (existing display/search or verified/source aliases).

Diagnostic only. No audit verdict or production data is modified.
"""
from __future__ import annotations
import csv,itertools,json,re,shutil,subprocess,sys,unicodedata
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch035'
OUT=AUDIT/'character_derived_variant_base_validation_batch035.json'
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
            verdict=(r.get('audit_verdict') or '').strip(); rid=(r.get('row_id') or '').strip()
            if rid and verdict in VALID: out[rid]=r
    return out
def done_ids(amap):return set(amap)
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
            if JA.search(t) and norm(t)==nd:return True,f,t
    return False,'',''
def main():
    src=read(SOURCE); res=read(RESULTS); amap=audit_map(); audited=done_ids(amap)
    src_by_id={r['row_id']:r for r in src}; res_by_id={r['row_id']:r for r in res}
    char_by_tag={}
    for rid,s in src_by_id.items():
        cat=(s.get('category_name') or s.get('category') or '').strip()
        if cat in {'Character','4'}:char_by_tag[s['canonical_tag']]=(s,res_by_id.get(rid,{}))
    groups=defaultdict(list); population=0
    for r in census():
        if r.get('row_id') in audited or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '') not in NOTES:continue
        if (r.get('family_base_display_ja') or '').strip():continue
        stem,gs=split_tag(r['canonical_tag']); candidates=[]
        for keep_n in range(len(gs)-1,-1,-1):
            for idxs in itertools.combinations(range(len(gs)),keep_n):
                tag=rebuild(stem,[gs[i] for i in idxs]); hit=char_by_tag.get(tag)
                if not hit:continue
                s,b=hit; disp=(b.get('display_ja') or '').strip(); status=(b.get('translation_status') or '').strip()
                if status=='ACCEPTED_AI' and JA.search(disp): candidates.append((s,b,disp,tag))
            if candidates:break
        if len(candidates)!=1:continue
        population+=1; bs,br,bdisp,btag=candidates[0]; brid=bs['row_id']; decision=amap.get(brid)
        effective=bdisp; audit_basis=''
        if decision and (decision.get('audit_verdict') or '').strip() in RESOLVED:
            v=(decision.get('audit_verdict') or '').strip()
            if v in {'FIX_DISPLAY','FIX_BOTH'} and (decision.get('proposed_display_ja') or '').strip():effective=decision['proposed_display_ja'].strip()
            group='AUDITED_RESOLVED_BASE'; audit_basis=v
        else:
            ok,field,term=source_supports(bdisp,bs)
            group='SOURCE_SUPPORTED_BASE' if ok else 'UNSUPPORTED_ACCEPTED_BASE'
            audit_basis=(field+':'+term) if ok else ''
        item={k:r.get(k) or '' for k in ['row_id','canonical_tag','post_count','display_ja','translation_note','risk_flags','existing_candidate_ja','related_copyright_top1','related_copyright_top1_coverage']}
        item.update({'base_row_id':brid,'base_canonical_tag':btag,'base_current_display_ja':bdisp,'base_effective_display_ja':effective,'base_translation_note':br.get('translation_note') or '','base_audit_or_source_basis':audit_basis,
          'base_source_aliases':bs.get('source_aliases') or '','base_verified_aliases':bs.get('verified_aliases') or '','base_existing_display_ja':bs.get('existing_display_ja') or '','base_existing_search_ja':bs.get('existing_search_ja') or '','base_existing_candidate_ja':bs.get('existing_candidate_ja') or ''})
        groups[group].append(item)
    assert population==153,population
    data={'format_version':1,'issue':70,'production_modified':False,'population':population,'groups':[]}
    for reason,rows in sorted(groups.items(),key=lambda kv:(-len(kv[1]),kv[0])):
        rows.sort(key=lambda x:(-int(x['post_count'] or 0),x['row_id']))
        data['groups'].append({'reason':reason,'count':len(rows),'samples':rows[:30]})
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'population':population,'groups':[(g['reason'],g['count']) for g in data['groups']],'production_modified':False},ensure_ascii=False))
if __name__=='__main__':main()
