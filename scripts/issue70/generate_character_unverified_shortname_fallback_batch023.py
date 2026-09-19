#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 023.

For low-impact REVIEW_REQUIRED short kana/kanji Character rows, reject a
Japanese display when its only Japanese-facing support is the raw candidate
field. Preserve accuracy by proposing a human-readable canonical/Latin fallback
instead of guessing the Japanese identity. Rows with any stronger Japanese
source evidence or any additional v3 risk flag are excluded.

Proposal-only; production data is never modified.
"""
from __future__ import annotations

import csv
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT_DIR=ROOT/'docs/issue70/audit'
TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch023'
OUT=AUDIT_DIR/'character_unverified_shortname_fallback_batch023.csv'
NOTES={
 'short kana-only candidate is too ambiguous without contextual search evidence',
 'short kanji-only candidate is too ambiguous without contextual search evidence',
}
JA_RE=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')


def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows,fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
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
    return read_csv(TMP/'audit_ledger_template.csv')
def norm(v):
    return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def split(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def has_stronger_ja(r):
    # Raw existing_candidate_ja is deliberately NOT trusted here: this is the
    # field that produced the ambiguous short candidate. Existing display/search
    # and verified/source aliases are stronger preserved evidence.
    for field in ('existing_display_ja','existing_search_ja','verified_aliases','source_aliases'):
        if JA_RE.search(r.get(field) or ''):return True
    return False
def candidate_terms(r):return {norm(x) for x in split(r.get('existing_candidate_ja') or '')}
def flagset(r):return {x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
def fallback(canonical):
    # Identity-safe readable fallback; do not invent capitalization/readings.
    return (canonical or '').replace('_',' ').strip()

def main():
    audited=prior_ids();rows=[]
    for r in run_census():
        if r.get('row_id') in audited or r.get('category_name')!='Character':continue
        if r.get('translation_status')!='REVIEW_REQUIRED' or (r.get('translation_note') or '') not in NOTES:continue
        if flagset(r)!={'STATUS_REVIEW_REQUIRED'}:continue
        posts=int(r.get('post_count') or 0)
        if posts>=500:continue
        display=(r.get('display_ja') or '').strip()
        if not display or not JA_RE.search(display):continue
        if has_stronger_ja(r):continue
        if norm(display) not in candidate_terms(r):continue
        proposed=fallback(r.get('canonical_tag') or '')
        if not proposed or norm(proposed)==norm(display):continue
        rows.append({
          'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':display,'existing_candidate_ja':r.get('existing_candidate_ja') or '',
          'related_copyright_top1':r.get('related_copyright_top1') or '',
          'related_copyright_top1_coverage':r.get('related_copyright_top1_coverage') or '',
          'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
          'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'',
          'reason_code':'REJECT_UNVERIFIED_SHORT_JA_CANDIDATE_USE_CANONICAL_FALLBACK','confidence':'HIGH',
          'evidence_refs':'raw candidate only; no Japanese existing display/search/verified/source alias evidence',
          'audit_note':'短い日本語候補はraw candidate以外の裏付けがなく、実サンプルでidentity誤りを確認。低使用数行は誤った日本語名を残すよりcanonical由来の安全なLatin fallbackへ戻す。',
          'approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','existing_candidate_ja','related_copyright_top1','related_copyright_top1_coverage','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    write_csv(OUT,rows,fields)
    print({'rows':len(rows),'fix_display':len(rows),'production_modified':False});return 0
if __name__=='__main__':raise SystemExit(main())
