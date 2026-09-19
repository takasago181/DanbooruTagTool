#!/usr/bin/env python3
"""Generate Issue #70 Character audit batch 027.

For remaining ACCEPTED_AI Character rows with duplicate Japanese displays, add
Copyright context only when that context actually makes the label unique across
the full Character baseline. This avoids noisy context that still fails to
resolve same-work/same-franchise duplicates.

Proposal-only; production Issue #70 data is never modified.
"""
from __future__ import annotations

import csv
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'
TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch027'
OUT=AUDIT/'character_unique_copyright_context_batch027.csv'
RUNTIME=ROOT/'docs/issue70/data/runtime/issue70_translation_results.csv'
SOURCE=ROOT/'docs/issue70/data/source/issue70_translation_source_with_relations.csv'
JA_RE=re.compile(r'[\u3040-\u30ff\u3400-\u9fff々〆ヶ]')
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}


def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def audited_ids():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        if p.name==OUT.name:continue
        try:rows=read_csv(p)
        except Exception:continue
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
            result[r['canonical_tag']]=(r.get('display_ja') or '').strip()
    for p in sorted(AUDIT.glob('*.csv')):
        if p.name==OUT.name:continue
        try:rows=read_csv(p)
        except Exception:continue
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

def full_character_groups():
    source_by_id={r['row_id']:r for r in read_csv(SOURCE) if r.get('row_id')}
    groups=defaultdict(list); all_displays=set()
    for r in read_csv(RUNTIME):
        rid=(r.get('row_id') or '').strip(); src=source_by_id.get(rid)
        if not src or src.get('category_name')!='Character':continue
        display=(r.get('display_ja') or '').strip()
        if not display:continue
        all_displays.add(display)
        groups[display].append({
            'row_id':rid,
            'canonical_tag':r.get('canonical_tag') or '',
            'related_copyright_top1':(src.get('related_copyright_top1') or '').strip(),
        })
    return groups,all_displays

def main():
    done=audited_ids(); cp=preferred_copyright_displays(); groups,all_displays=full_character_groups(); rows=[]
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
        siblings=groups.get(display,[])
        if len(siblings)<2:continue
        # Context must distinguish this row from every other baseline row with the same display.
        if any(s['row_id']!=r['row_id'] and s['related_copyright_top1']==related for s in siblings):continue
        proposed=f'{display}（{context}）'
        if proposed in all_displays:continue
        rows.append({
            'row_id':r['row_id'],'canonical_tag':r['canonical_tag'],'post_count':r.get('post_count') or '',
            'display_ja':display,'search_ja':r.get('search_ja') or '',
            'translation_note':r.get('translation_note') or '','risk_flags':r.get('risk_flags') or '',
            'related_copyright_top1':related,'related_copyright_top1_coverage':r.get('related_copyright_top1_coverage') or '',
            'copyright_display_context':context,'duplicate_group_size':str(len(siblings)),
            'audit_verdict':'FIX_DISPLAY','proposed_display_ja':proposed,'proposed_search_ja':'',
            'reason_code':'ADD_UNIQUE_COPYRIGHT_CONTEXT_TO_ACCEPTED_DUPLICATE_CHARACTER','confidence':'HIGH',
            'evidence_refs':'full-baseline duplicate group + unique related_copyright_top1 + coverage >=0.80',
            'audit_note':'日本語名自体はACCEPTED_AIを維持。同名Characterが存在するが、この行の作品関係は同名群内で一意なので作品名を表示へ付与して識別性だけを改善。',
            'approval_status':'PROPOSED'})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','risk_flags','related_copyright_top1','related_copyright_top1_coverage','copyright_display_context','duplicate_group_size','audit_verdict','proposed_display_ja','proposed_search_ja','reason_code','confidence','evidence_refs','audit_note','approval_status']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print({'rows':len(rows),'fix_display':len(rows),'production_modified':False})
    return 0
if __name__=='__main__':raise SystemExit(main())
