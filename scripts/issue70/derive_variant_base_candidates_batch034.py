#!/usr/bin/env python3
"""Derive exact existing Character base tags for remaining Issue #70 variant rows.

For each remaining parenthetical/variant Character row lacking family_base fields,
enumerate proper subsets of canonical parenthetical groups and retain only exact
canonical Character tags that exist in the 92,739-row source. Rank the longest
existing shorter form whose current Japanese display is ACCEPTED_AI and contains
Japanese. Diagnostic only: no verdicts and no production changes.
"""
from __future__ import annotations
import csv,itertools,json,re,shutil,subprocess,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch034'
OUT=AUDIT/'character_derived_variant_base_batch034_diagnostic.json'
SOURCE=ROOT/'docs/issue70/data/source/issue70_translation_source_with_relations.csv'
RESULTS=ROOT/'docs/issue70/data/runtime/issue70_translation_results.csv'
NOTES={'parenthetical candidate does not map cleanly to a copyright disambiguator','variant/form rendering plausible but not independently verified'}
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]'); GROUP=re.compile(r'_\(([^()]*)\)')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def done():
    s=set()
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():s.add(r['row_id'].strip())
    return s
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def split_tag(tag):
    m=list(GROUP.finditer(tag or ''))
    stem=(tag[:m[0].start()] if m else tag).rstrip('_')
    return stem,[x.group(1) for x in m]
def rebuild(stem,groups):return stem+''.join(f'_({g})' for g in groups)
def main():
    src=read(SOURCE); res=read(RESULTS)
    src_by_id={r['row_id']:r for r in src}; res_by_id={r['row_id']:r for r in res}
    char_by_tag={}
    for rid,s in src_by_id.items():
        cat=(s.get('category_name') or s.get('category') or '').strip()
        if cat not in {'Character','4'}:continue
        char_by_tag[s['canonical_tag']]=(s,res_by_id.get(rid,{}))
    audited=done(); groups=defaultdict(list); population=0
    for r in census():
        if r.get('row_id') in audited or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '') not in NOTES:continue
        if (r.get('family_base_display_ja') or '').strip():continue
        population+=1; stem,gs=split_tag(r['canonical_tag']); candidates=[]
        # enumerate non-empty proper subsets in original order; longest first
        for keep_n in range(len(gs)-1,-1,-1):
            for idxs in itertools.combinations(range(len(gs)),keep_n):
                tag=rebuild(stem,[gs[i] for i in idxs])
                hit=char_by_tag.get(tag)
                if not hit:continue
                s,b=hit; disp=(b.get('display_ja') or '').strip(); status=(b.get('translation_status') or '').strip()
                candidates.append({'canonical_tag':tag,'display_ja':disp,'translation_status':status,'row_id':s.get('row_id') or '', 'kept_groups':keep_n,'has_ja':bool(JA.search(disp))})
            if candidates:break
        safe=[c for c in candidates if c['translation_status']=='ACCEPTED_AI' and c['has_ja']]
        reason='SAFE_ACCEPTED_JA_BASE' if len(safe)==1 else ('AMBIGUOUS_SAFE_BASE' if len(safe)>1 else 'NO_SAFE_ACCEPTED_JA_BASE')
        chosen=safe[0] if len(safe)==1 else None
        o={k:r.get(k) or '' for k in ['row_id','canonical_tag','post_count','display_ja','translation_note','risk_flags','related_copyright_top1','related_copyright_top1_coverage','existing_candidate_ja']}
        o['reason']=reason;o['chosen_base']=chosen;o['existing_shorter_candidates']=candidates[:8]
        groups[reason].append(o)
    assert population==1195,population
    data={'format_version':1,'issue':70,'production_modified':False,'population':population,'groups':[]}
    for reason,rows in sorted(groups.items(),key=lambda kv:(-len(kv[1]),kv[0])):
        rows.sort(key=lambda x:(-int(x['post_count'] or 0),x['row_id']))
        data['groups'].append({'reason':reason,'count':len(rows),'samples':rows[:20]})
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'population':population,'groups':[(g['reason'],g['count']) for g in data['groups']],'production_modified':False},ensure_ascii=False))
if __name__=='__main__':main()
