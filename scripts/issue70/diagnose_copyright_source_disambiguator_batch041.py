#!/usr/bin/env python3
"""Diagnose source-backed Japanese disambiguators for remaining Issue #70 Copyright rows.

Find remaining ACCEPTED_AI Copyright rows with duplicate/disambiguator risk where
existing_search_ja contains a Japanese alternative distinct from display_ja that
looks like a browse disambiguator (parenthetical, 初代/無印/シリーズ, or numeric
edition marker). Check whether that alternative would be unique among current
Copyright displays and all candidates found here. Diagnostic only.
"""
from __future__ import annotations
import csv,json,re,shutil,subprocess,sys,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch041'; OUT=AUDIT/'copyright_source_disambiguator_batch041_diagnostic.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
CURATED={
'established/common Japanese title or official rendering',
'manual chat curation selected high-confidence Japanese copyright title',
'semantic re-curation: title/name judged usable; official/common rendering preferred over literal candidate',
'semantic re-curation: title/name judged usable; official/common rendering or identity-safe original preferred over literal candidate',
'single clean Japanese copyright search title',
}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
MARK=re.compile(r'[（(].+[）)]|初代|無印|シリーズ|第\s*[0-9０-９一二三四五六七八九十]+|[0-9０-９]+(?:作|版|期|章|部|代)')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def done():
    s=set()
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            rid=(r.get('row_id') or '').strip();v=(r.get('audit_verdict') or '').strip()
            if rid and v in VALID:s.add(rid)
    return s
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def main():
    audited=done(); allrows=census(); current_displays=Counter()
    for r in allrows:
        if r.get('category_name')=='Copyright':current_displays[norm(r.get('display_ja') or '')]+=1
    candidates=[]
    for r in allrows:
        if r.get('row_id') in audited or r.get('category_name')!='Copyright' or r.get('translation_status')!='ACCEPTED_AI':continue
        if (r.get('translation_note') or '').strip() not in CURATED:continue
        flags={x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
        if not ({'DUPLICATE_DISPLAY_WITHIN_CATEGORY','DISAMBIGUATOR_NOT_VISIBLE'} & flags):continue
        display=(r.get('display_ja') or '').strip(); nd=norm(display)
        for term in terms(r.get('existing_search_ja') or ''):
            nt=norm(term)
            if not term or nt==nd or not JA.search(term) or not MARK.search(term):continue
            # Must visibly preserve the current title stem unless the source term has explicit edition wording.
            preserve=(nd and nd in nt) or bool(re.search(r'初代|無印|シリーズ|第\s*[0-9０-９一二三四五六七八九十]+|[0-9０-９]+(?:作|版|期|章|部|代)',term))
            if not preserve:continue
            candidates.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
              'display_ja':display,'search_ja':r.get('search_ja') or '','existing_search_ja':r.get('existing_search_ja') or '',
              'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
              'candidate_display_ja':term,'candidate_norm':nt})
    cand_counts=Counter(x['candidate_norm'] for x in candidates)
    byrow={}
    for x in candidates:
        x['unique_candidate']='true' if cand_counts[x['candidate_norm']]==1 and current_displays[x['candidate_norm']]==0 else 'false'
        byrow.setdefault(x['row_id'],[]).append(x)
    safe=[]; ambiguous=[]
    for rid,xs in byrow.items():
        u=[x for x in xs if x['unique_candidate']=='true']
        if len(u)==1:safe.append(u[0])
        else:ambiguous.extend(xs)
    safe.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    ambiguous.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id'],r['candidate_display_ja']))
    data={'format_version':1,'issue':70,'production_modified':False,'candidate_rows':len(byrow),'safe_unique_rows':len(safe),'ambiguous_candidate_terms':len(ambiguous),'safe_samples':safe[:40],'ambiguous_samples':ambiguous[:40]}
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:data[k] for k in ['candidate_rows','safe_unique_rows','ambiguous_candidate_terms','production_modified']},ensure_ascii=False))
if __name__=='__main__':main()
