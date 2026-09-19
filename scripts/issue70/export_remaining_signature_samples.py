#!/usr/bin/env python3
"""Export compact representative samples from the largest remaining Issue70 signatures.

Diagnostic only. No audit verdicts are produced and production data is untouched.
"""
from __future__ import annotations
import csv, json, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT_DIR=ROOT/'docs/issue70/audit'
TMP=ROOT/'artifacts/issue70-semantic-audit-v3-signature-samples'
OUT=AUDIT_DIR/'REMAINING_SIGNATURE_SAMPLES.json'
TARGETS=[
 ('Character','short kana-only candidate is too ambiguous without contextual search evidence','STATUS_REVIEW_REQUIRED',10),
 ('Character','short kanji-only candidate is too ambiguous without contextual search evidence','STATUS_REVIEW_REQUIRED',10),
 ('Character','parenthetical candidate does not map cleanly to a copyright disambiguator','STATUS_REVIEW_REQUIRED',10),
 ('Character','variant/form rendering plausible but not independently verified','DISAMBIGUATOR_NOT_VISIBLE|STATUS_REVIEW_REQUIRED',10),
 ('Character','single Japanese candidate with no conflicting evidence','DISPLAY_MISSING_FROM_SEARCH|DUPLICATE_DISPLAY_WITHIN_CATEGORY|JA_DISPLAY_NOT_EXACT_SOURCE_EVIDENCE',10),
 ('Copyright','Japanese rendering requires manual verification or source evidence is insufficient','STATUS_REVIEW_REQUIRED',10),
 ('Copyright','copyright title not uniquely resolved; manual verification required','STATUS_REVIEW_REQUIRED',10),
]
VALID_VERDICTS={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def run_census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')
def audited_ids():
    ids=set()
    for p in AUDIT_DIR.glob('*.csv'):
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID_VERDICTS and (r.get('row_id') or '').strip():ids.add(r['row_id'].strip())
    return ids
def sig(r):
    return '|'.join(sorted(x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip())) or '<none>'
def compact(r):
    keys=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_status','translation_note','risk_flags','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja','related_copyright_top1','related_copyright_top1_coverage','family_base_canonical','family_base_display_ja']
    return {k:(r.get(k) or '') for k in keys}
def main():
    audited=audited_ids(); ledger=[r for r in run_census() if r.get('row_id') not in audited]
    groups=[]
    for category,note,signature,limit in TARGETS:
        rows=[r for r in ledger if r.get('category_name')==category and (r.get('translation_note') or '')==note and sig(r)==signature]
        rows.sort(key=lambda r:(-int(r.get('post_count') or 0),r['row_id']))
        groups.append({'category':category,'translation_note':note,'risk_flags':signature,'population':len(rows),'samples':[compact(r) for r in rows[:limit]]})
    OUT.write_text(json.dumps({'format_version':1,'issue':70,'production_modified':False,'groups':groups},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'groups':[{**{k:g[k] for k in ('category','translation_note','risk_flags','population')},'samples':len(g['samples'])} for g in groups]},ensure_ascii=False,indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
