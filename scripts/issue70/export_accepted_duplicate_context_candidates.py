#!/usr/bin/env python3
"""Export safe-looking ACCEPTED_AI Character duplicate-display candidates.

Diagnostic only. No audit verdict is written. Candidates must have a Japanese
current display, a strong related-Copyright context, and no variant/raw/no-context
structural warning. The proposed contextual display is shown for human semantic
inspection before a bulk audit verdict is generated.
"""
from __future__ import annotations
import csv, json, re, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'
TMP=ROOT/'artifacts/issue70-semantic-audit-v3-accepted-duplicate-context'
OUT=AUDIT/'ACCEPTED_DUPLICATE_CONTEXT_CANDIDATES.json'
RUNTIME=ROOT/'docs/issue70/data/runtime/issue70_translation_results.csv'
JA_RE=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}


def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def audited_ids():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip():
                ids.add(r['row_id'].strip())
    return ids
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')
def preferred_copyright_displays():
    result={}
    for r in read_csv(RUNTIME):
        if r.get('category')=='3' and r.get('canonical_tag'):
            result[r['canonical_tag']] = (r.get('display_ja') or '').strip()
    for p in sorted(AUDIT.glob('*.csv')):
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            canonical=(r.get('canonical_tag') or '').strip(); proposed=(r.get('proposed_display_ja') or '').strip(); verdict=(r.get('audit_verdict') or '').strip()
            if canonical in result and proposed and verdict in {'FIX_DISPLAY','FIX_BOTH'}:
                result[canonical]=proposed
    return result
def flags(r):return {x.strip() for x in (r.get('risk_flags') or '').split('|') if x.strip()}
def coverage(r):
    try:return float(r.get('related_copyright_top1_coverage') or 0)
    except ValueError:return 0.0
def has_brackets(v):return any(ch in (v or '') for ch in '()（）[]【】')

def main():
    done=audited_ids(); cp=preferred_copyright_displays(); candidates=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Character' or r.get('translation_status')!='ACCEPTED_AI':continue
        fs=flags(r)
        if 'DUPLICATE_DISPLAY_WITHIN_CATEGORY' not in fs:continue
        if fs & {'VARIANT_DISPLAY_MISSING_BASE_IDENTITY','RAW_TAG_SYNTAX_IN_DISPLAY','CHARACTER_NO_COPYRIGHT_CONTEXT'}:continue
        display=(r.get('display_ja') or '').strip()
        if not display or not JA_RE.search(display) or has_brackets(display):continue
        related=(r.get('related_copyright_top1') or '').strip()
        if not related or related=='original' or coverage(r)<0.80:continue
        context=(cp.get(related) or '').strip()
        if not context or context==display:continue
        candidates.append({
            'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':int(r.get('post_count') or 0),
            'display_ja':display,'search_ja':r.get('search_ja') or '',
            'translation_note':r.get('translation_note') or '', 'risk_flags':r.get('risk_flags') or '',
            'related_copyright_top1':related,'related_copyright_top1_coverage':r.get('related_copyright_top1_coverage') or '',
            'copyright_display_context':context,'proposed_display_ja':f'{display}（{context}）',
            'existing_candidate_ja':r.get('existing_candidate_ja') or '',
            'existing_display_ja':r.get('existing_display_ja') or '',
        })
    candidates.sort(key=lambda r:(-r['post_count'],r['row_id']))
    OUT.write_text(json.dumps({'format_version':1,'issue':70,'production_modified':False,'population':len(candidates),'samples':candidates[:60]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print({'population':len(candidates),'samples':min(60,len(candidates)),'production_modified':False})
    return 0
if __name__=='__main__':raise SystemExit(main())
