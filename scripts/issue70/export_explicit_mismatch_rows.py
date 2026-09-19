#!/usr/bin/env python3
"""Export remaining Character rows already marked as explicit identity mismatch.
Diagnostic only; no verdicts and no production mutation.
"""
from __future__ import annotations
import csv,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-semantic-audit-v3-explicit-mismatch'; OUT=AUDIT/'EXPLICIT_MISMATCH_ROWS.json'
NOTES={'identity mismatch or low-confidence mapping identified during chat review','fan-art/search tag is not character identity'}
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def audited_ids():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        try:rows=read_csv(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():ids.add(r['row_id'].strip())
    return ids
def run():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')
def main():
    done=audited_ids(); out=[]
    keys=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_status','translation_note','risk_flags','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja','related_copyright_top1','related_copyright_top1_coverage','family_base_canonical','family_base_display_ja']
    for r in run():
        if r.get('row_id') in done or r.get('category_name')!='Character' or (r.get('translation_note') or '') not in NOTES:continue
        out.append({k:(r.get(k) or '') for k in keys})
    out.sort(key=lambda r:(r['translation_note'],-int(r['post_count'] or 0),r['row_id']))
    OUT.write_text(json.dumps({'format_version':1,'issue':70,'production_modified':False,'rows':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'rows':len(out),'production_modified':False});return 0
if __name__=='__main__':raise SystemExit(main())
