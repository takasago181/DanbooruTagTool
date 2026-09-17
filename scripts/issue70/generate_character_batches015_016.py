#!/usr/bin/env python3
"""Generate Issue #70 Character audit batches 015-016.

015: KEEP previously curated/confirmed Character names when no semantic risk
remains (DISPLAY_MISSING_FROM_SEARCH alone is harmless under RuntimeCatalogIndex).
016: for the same curated name population, resolve only remaining short-name
collision/disambiguation by appending the related Copyright display.

Proposal-only; production data is never modified.
"""
from __future__ import annotations
import csv, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT_DIR=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batches015-016'
OUT15=AUDIT_DIR/'character_curated_keep_batch015.csv'; OUT16=AUDIT_DIR/'character_curated_context_batch016.csv'
RUNTIME=ROOT/'docs/issue70/data/runtime/issue70_translation_results.csv'
POSITIVE_NOTES={
 'AI監修：既存日本語候補・作品関係を確認して採用','AI監修：既存候補・Alias・作品関係を確認し表示名を確定',
 '既存日本語候補・Alias・作品文脈を確認して採用','selected from contextual Japanese search evidence','確定',
 '既存日本語候補・作品文脈を確認','AI監修：既存日本語表記を確認','manual chat curation selected reliable Japanese identity',
 'AI監修：日本版公式名を確認','AI監修：Alias・既存日本語候補・作品関係を確認して採用',
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
        if p.name in {OUT15.name,OUT16.name}:continue
        try: rows=read_csv(p)
        except Exception:continue
        for r in rows:
            if r.get('row_id') and r.get('audit_verdict'):ids.add(r['row_id'].strip())
    return ids
def run_census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return TMP/'audit_ledger_template.csv'
def flags(r):return {x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
def brackets(s):return any(c in (s or '') for c in '()（）[]【】')
def copyright_map():
    out={}
    for r in read_csv(RUNTIME):
        if r.get('category')=='3' and r.get('canonical_tag'):out[r['canonical_tag']]=(r.get('display_ja') or '').strip()
    for p in sorted(AUDIT_DIR.glob('*.csv')):
        if p.name in {OUT15.name,OUT16.name}:continue
        try: rows=read_csv(p)
        except Exception:continue
        for r in rows:
            c=(r.get('canonical_tag') or '').strip(); d=(r.get('proposed_display_ja') or '').strip(); v=(r.get('audit_verdict') or '').strip()
            if c in out and d and v in {'FIX_DISPLAY','FIX_BOTH'}:out[c]=d
    return out

def main():
    audited=prior_ids(); ledger=read_csv(run_census()); cp=copyright_map(); b15=[]; b16=[]; used=set()
    for r in ledger:
        if r.get('row_id') in audited or r.get('category_name')!='Character' or (r.get('translation_note') or '') not in POSITIVE_NOTES:continue
        fs=flags(r)
        if fs.issubset({'DISPLAY_MISSING_FROM_SEARCH'}):
            b15.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],'display_ja':r['display_ja'],'search_ja':r.get('search_ja') or '','translation_note':r.get('translation_note') or '','audit_verdict':'KEEP','proposed_display_ja':'','proposed_search_ja':'','reason_code':'CURATED_CHARACTER_NAME_NO_SEMANTIC_RISK','confidence':'HIGH','evidence_refs':'prior curation note + frozen source/context','audit_note':'既存監修済み日本語名を再確認。search_jaがdisplayを重複しないこと自体はruntime仕様上問題なし。','approval_status':'PROPOSED'});used.add(r['row_id']);continue
        if 'VARIANT_DISPLAY_MISSING_BASE_IDENTITY' in fs:continue
        if not ({'DUPLICATE_DISPLAY_WITHIN_CATEGORY','DISAMBIGUATOR_NOT_VISIBLE'} & fs):continue
        display=(r.get('display_ja') or '').strip(); related=(r.get('related_copyright_top1') or '').strip(); context=(cp.get(related) or '').strip()
        if not display or brackets(display) or not context:continue
        b16.append({'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r['post_count'],'display_ja':display,'related_copyright_top1':related,'copyright_display_context':context,'translation_note':r.get('translation_note') or '','audit_verdict':'FIX_DISPLAY','proposed_display_ja':f'{display}（{context}）','proposed_search_ja':'','reason_code':'CURATED_NAME_ADD_COPYRIGHT_DISAMBIGUATION','confidence':'HIGH','evidence_refs':'prior curation + related Copyright context','audit_note':'監修済みのキャラ名自体は維持し、同名衝突/不可視disambiguatorのみ作品名で解消。','approval_status':'PROPOSED'});used.add(r['row_id'])
    b15.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']));b16.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    write_csv(OUT15,b15,['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status'])
    write_csv(OUT16,b16,['row_id','canonical_tag','post_count','display_ja','related_copyright_top1','copyright_display_context','translation_note','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status'])
    print({'batch015':len(b15),'batch016':len(b16),'production_modified':False});return 0
if __name__=='__main__':raise SystemExit(main())
