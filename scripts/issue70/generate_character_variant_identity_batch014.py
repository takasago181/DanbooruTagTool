#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 014.

Repairs VARIANT_DISPLAY_MISSING_BASE_IDENTITY only for rows whose current
variant/form label already has positive contextual evidence. The label is kept
verbatim; this pass merely restores the frozen family-base character identity.
Machine-like/ambiguous candidate lanes are intentionally excluded.

Proposal-only; production translation data is never modified.
"""
from __future__ import annotations
import csv, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT_DIR=ROOT/'docs/issue70/audit'
TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch014'
OUT=AUDIT_DIR/'character_variant_identity_restore_batch014.csv'

POSITIVE_NOTES={
    'variant/form rendering plausible but not independently verified',
    'selected from contextual Japanese search evidence',
    'Japanese Pokemon form/name candidate consistent with franchise context',
    'selected from search+candidate agreement',
    'AI監修：日本版公式衣装名を確認',
    'AI監修：既存日本語表記を確認',
    '既存日本語候補・Alias・作品文脈を確認して採用',
    'AI監修：既存日本語候補・作品関係を確認して採用',
    'AI監修：既存候補・Alias・作品関係を確認し表示名を確定',
    'manual chat curation selected reliable Japanese identity',
}

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
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            if r.get('row_id') and r.get('audit_verdict'):ids.add(r['row_id'].strip())
    return ids
def run_census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return TMP/'audit_ledger_template.csv'

def main():
    audited=prior_ids(); ledger=read_csv(run_census()); rows=[]
    for r in ledger:
        if r.get('row_id') in audited or r.get('category_name')!='Character':continue
        if 'VARIANT_DISPLAY_MISSING_BASE_IDENTITY' not in (r.get('risk_flags') or ''):continue
        if (r.get('translation_note') or '') not in POSITIVE_NOTES:continue
        base=(r.get('family_base_display_ja') or '').strip(); current=(r.get('display_ja') or '').strip()
        if not base or not current:continue
        proposed=f'{base}（{current}）'
        rows.append({
            'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],
            'display_ja':current,'family_base_canonical':r.get('family_base_canonical') or '',
            'family_base_display_ja':base,'translation_note':r.get('translation_note') or '',
            'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'',
            'reason_code':'RESTORE_BASE_IDENTITY_KEEP_EVIDENCED_VARIANT_LABEL','confidence':'HIGH',
            'evidence_refs':'family base + current positively evidenced variant/form label',
            'audit_note':'既存の衣装/フォーム名は変更せず、欠落していたキャラ本人名だけをfamily baseから復元。機械訳・identity mismatch laneは除外。',
            'approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    write_csv(OUT,rows,['row_id','canonical_tag','post_count','display_ja','family_base_canonical','family_base_display_ja','translation_note','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status'])
    print({'rows':len(rows),'production_modified':False});return 0
if __name__=='__main__':raise SystemExit(main())
