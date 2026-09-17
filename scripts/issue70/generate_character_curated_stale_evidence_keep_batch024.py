#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 024.

Close ACCEPTED_AI Character rows that were explicitly curated earlier and whose
remaining v3 warnings are only stale-source bookkeeping: current Japanese
rendering differs from frozen source evidence and/or has no exact source overlap,
optionally with display-search redundancy. Structural/identity warnings are not
allowed. Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT_DIR=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch024'
OUT=AUDIT_DIR/'character_curated_stale_evidence_keep_batch024.csv'
JA_RE=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
POSITIVE_NOTES={
 'AI監修：既存日本語候補・作品関係を確認して採用',
 'AI監修：既存候補・Alias・作品関係を確認し表示名を確定',
 '既存日本語候補・Alias・作品文脈を確認して採用',
 'selected from contextual Japanese search evidence','確定',
 '既存日本語候補・作品文脈を確認','既存日本語候補と作品文脈を確認',
 'AI監修：既存日本語表記を確認','manual chat curation selected reliable Japanese identity',
 'AI監修：日本版公式名を確認','公式日本語名を採用','既存日本語候補を確認',
 '既存日本語候補とAliasを確認','AI監修：既存日本語候補を確認',
 'AI監修：Alias・既存日本語候補・作品関係を確認して採用',
}
ALLOWED={'JA_DISPLAY_NOT_EXACT_SOURCE_EVIDENCE','NO_SOURCE_JA_EVIDENCE_OVERLAP','DISPLAY_MISSING_FROM_SEARCH'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows,fields):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def audited_ids():
    out=set()
    for p in AUDIT_DIR.glob('*.csv'):
        if p.name==OUT.name:continue
        try:rows=read_csv(p)
        except Exception:continue
        for r in rows:
            if r.get('row_id') and r.get('audit_verdict'):out.add(r['row_id'].strip())
    return out
def run_census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')
def flags(r):return {x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
def main():
    done=audited_ids();rows=[]
    for r in run_census():
        if r.get('row_id') in done or r.get('category_name')!='Character' or r.get('translation_status')!='ACCEPTED_AI':continue
        note=(r.get('translation_note') or '').strip()
        if note not in POSITIVE_NOTES:continue
        fs=flags(r)
        if not fs or not fs.issubset(ALLOWED) or 'NO_SOURCE_JA_EVIDENCE_OVERLAP' not in fs:continue
        display=(r.get('display_ja') or '').strip()
        if not display or not JA_RE.search(display):continue
        rows.append({
          'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
          'display_ja':display,'search_ja':r.get('search_ja') or '','translation_note':note,'risk_flags':r.get('risk_flags') or '',
          'audit_verdict':'KEEP','proposed_display_ja':'','proposed_search_ja':'',
          'reason_code':'CURATED_CHARACTER_STALE_SOURCE_EVIDENCE_ONLY','confidence':'HIGH',
          'evidence_refs':'explicit prior semantic/official-name curation note; no structural identity warnings',
          'audit_note':'表示名は既に文脈・Alias・公式名等を用いて監修済み。残存flagは凍結sourceとの文字列不一致/非重複のみで、同名衝突・variant欠落・disambiguator欠落などのidentity警告がないため現表示を維持。',
          'approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','risk_flags','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    write_csv(OUT,rows,fields);print({'rows':len(rows),'keep':len(rows),'production_modified':False});return 0
if __name__=='__main__':raise SystemExit(main())
