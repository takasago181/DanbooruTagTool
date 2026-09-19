#!/usr/bin/env python3
"""Generate Issue #70 Copyright audit batch 017.

Closes ACCEPTED_AI Copyright rows that already carry a positive semantic
re-curation/official-title note and whose remaining v3 flags are only source
string-overlap bookkeeping. Structural, collision, disambiguation and ASCII
fallback risks are excluded.

Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT_DIR=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch017'; OUT=AUDIT_DIR/'copyright_curated_keep_batch017.csv'
GOOD_NOTES={
 'established/common Japanese title or official rendering',
 'manual chat curation selected high-confidence Japanese copyright title',
 'single clean Japanese copyright search title',
 'semantic re-curation: title/name judged usable; official/common rendering preferred over literal candidate',
 'semantic re-curation: title/name judged usable; official/common rendering or identity-safe original preferred over literal candidate',
}
HARMLESS={'NO_SOURCE_JA_EVIDENCE_OVERLAP','JA_DISPLAY_NOT_EXACT_SOURCE_EVIDENCE','DISPLAY_MISSING_FROM_SEARCH'}
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows,fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def prior_ids():
    ids=set()
    for p in AUDIT_DIR.glob('*.csv'):
        if p.name==OUT.name:continue
        try:rows=read_csv(p)
        except Exception:continue
        for r in rows:
            if r.get('row_id') and r.get('audit_verdict'):ids.add(r['row_id'].strip())
    return ids
def run_census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return TMP/'audit_ledger_template.csv'
def flagset(s):return {x.strip() for x in (s or '').split('|') if x.strip()}
def main():
    audited=prior_ids();rows=[]
    for r in read_csv(run_census()):
        if r.get('row_id') in audited or r.get('category_name')!='Copyright' or r.get('translation_status')!='ACCEPTED_AI':continue
        if (r.get('translation_note') or '') not in GOOD_NOTES:continue
        if not flagset(r.get('risk_flags')).issubset(HARMLESS):continue
        rows.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],'display_ja':r['display_ja'],'search_ja':r.get('search_ja') or '','translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '','audit_verdict':'KEEP','proposed_display_ja':'','proposed_search_ja':'','reason_code':'CURATED_COPYRIGHT_TITLE_NO_SEMANTIC_RISK','confidence':'HIGH','evidence_refs':'prior semantic re-curation + v3 risk classification','audit_note':'残存flagはsource文字列の完全一致差のみ。構造/衝突/曖昧性リスクがないため監修済み表示を維持。','approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    write_csv(OUT,rows,['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status'])
    print({'rows':len(rows),'production_modified':False});return 0
if __name__=='__main__':raise SystemExit(main())
