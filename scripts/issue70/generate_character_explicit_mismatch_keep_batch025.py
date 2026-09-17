#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 025.

Closes rows whose prior semantic review already identified the Japanese candidate
as an identity mismatch or fan-art/search label, and whose current display has
already been conservatively restored to a readable canonical fallback.
Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch025'; OUT=AUDIT/'character_explicit_mismatch_keep_batch025.csv'
NOTES={'identity mismatch or low-confidence mapping identified during chat review','fan-art/search tag is not character identity'}
EXPECTED={'STATUS_REVIEW_REQUIRED','DISPLAY_CANONICAL_LIKE','ASCII_ONLY_DISPLAY_NON_ARTIST','NO_SOURCE_JA_EVIDENCE_OVERLAP'}
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows,fields):
    with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def done_ids():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name:continue
        try:rows=read_csv(p)
        except Exception:continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():ids.add(r['row_id'].strip())
    return ids
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')
def flags(r):return {x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
def fallback(tag):return (tag or '').replace('_',' ').strip()
def main():
    done=done_ids();rows=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Character' or (r.get('translation_note') or '') not in NOTES:continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or flags(r)!=EXPECTED:continue
        display=(r.get('display_ja') or '').strip()
        if display!=fallback(r.get('canonical_tag') or ''):continue
        rows.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '','display_ja':display,'existing_candidate_ja':r.get('existing_candidate_ja') or '','translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '','audit_verdict':'KEEP','proposed_display_ja':'','proposed_search_ja':'','reason_code':'EXPLICIT_BAD_JA_CANDIDATE_ALREADY_SAFE_CANONICAL_FALLBACK','confidence':'HIGH','evidence_refs':'prior explicit mismatch/search-tag review + exact readable canonical fallback','audit_note':'旧日本語候補は人物名ではない/identity誤対応と既に判定済み。現在表示はcanonical由来の安全なfallbackへ戻っており、誤った日本語を再採用せず現状維持。','approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['row_id','canonical_tag','post_count','display_ja','existing_candidate_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    write_csv(OUT,rows,fields);print({'rows':len(rows),'keep':len(rows),'production_modified':False});return 0
if __name__=='__main__':raise SystemExit(main())
