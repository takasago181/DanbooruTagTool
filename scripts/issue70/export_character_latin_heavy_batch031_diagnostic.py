#!/usr/bin/env python3
"""Export remaining REVIEW_REQUIRED Character rows with Latin-heavy candidates.
Diagnostic only; no audit verdicts and no production changes.
"""
from __future__ import annotations
import csv,json,re,shutil,subprocess,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch031'; OUT=AUDIT/'character_latin_heavy_batch031_diagnostic.csv'; SUMMARY=AUDIT/'character_latin_heavy_batch031_summary.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
JA=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def done():
    s=set()
    for p in AUDIT.glob('*.csv'):
        if p in {OUT} or 'diagnostic' in p.name:continue
        try: rows=read(p)
        except Exception: continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID:s.add((r.get('row_id') or '').strip())
    return s
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def main():
    audited=done(); rows=[]
    for r in census():
        if r.get('row_id') in audited:continue
        if r.get('category_name')!='Character' or r.get('translation_status')!='REVIEW_REQUIRED':continue
        if r.get('translation_note')!='Latin-heavy candidate requires verification':continue
        o={k:r.get(k) or '' for k in ['row_id','canonical_tag','post_count','display_ja','search_ja','translation_status','translation_note','risk_flags','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja','related_copyright_top1','related_copyright_top1_coverage','family_base_canonical','family_base_display_ja']}
        stronger=any(JA.search(o[x] or '') for x in ['source_aliases','verified_aliases','existing_display_ja','existing_search_ja'])
        o['has_stronger_ja_evidence']='true' if stronger else 'false'; rows.append(o)
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    assert len(rows)==380, len(rows)
    fields=list(rows[0].keys())
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    sig=Counter((r['risk_flags'] or '<none>',r['has_stronger_ja_evidence']) for r in rows)
    summary={'format_version':1,'issue':70,'production_modified':False,'population':len(rows),'signatures':[{'risk_flags':a,'has_stronger_ja_evidence':b,'count':n,'samples':[r for r in rows if (r['risk_flags'] or '<none>')==a and r['has_stronger_ja_evidence']==b][:10]} for (a,b),n in sig.most_common()]}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'rows':len(rows),'signatures':len(sig),'production_modified':False},ensure_ascii=False))
if __name__=='__main__':main()
