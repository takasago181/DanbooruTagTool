#!/usr/bin/env python3
"""Diagnose all currently remaining Issue #70 Character ACCEPTED_AI audit rows.

Groups live remaining rows by exact translation_note x risk_flags signature and
exports representative samples with source evidence. Diagnostic only: no audit
verdicts and no production changes.
"""
from __future__ import annotations
import csv,json,shutil,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-batch038'; OUT=AUDIT/'character_remaining_accepted_batch038_diagnostic.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}

def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def done():
    s=set()
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name:continue
        try:rows=read(p)
        except Exception:continue
        for r in rows:
            rid=(r.get('row_id') or '').strip(); v=(r.get('audit_verdict') or '').strip()
            if rid and v in VALID:s.add(rid)
    return s
def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read(TMP/'audit_ledger_template.csv')
def sig(flags):
    xs=sorted(x.strip() for x in (flags or '').split('|') if x.strip())
    return '|'.join(xs) if xs else '<none>'
def main():
    audited=done(); groups=defaultdict(list); rows=[]
    for r in census():
        if r.get('row_id') in audited:continue
        if r.get('category_name')!='Character' or r.get('translation_status')!='ACCEPTED_AI':continue
        o={k:r.get(k) or '' for k in ['row_id','canonical_tag','post_count','impact_tier','display_ja','search_ja','translation_note','risk_flags','audit_bucket','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja','related_copyright_top1','related_copyright_top1_coverage','family_base_canonical','family_base_display_ja']}
        rows.append(o); groups[((o['translation_note'] or '<blank>'),sig(o['risk_flags']))].append(o)
    data={'format_version':1,'issue':70,'production_modified':False,'population':len(rows),'groups':[]}
    for (note,flags),xs in sorted(groups.items(),key=lambda kv:(-len(kv[1]),kv[0])):
        xs.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
        data['groups'].append({'translation_note':note,'risk_flags':flags,'count':len(xs),'samples':xs[:15]})
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'population':len(rows),'group_count':len(data['groups']),'top_groups':[(g['translation_note'],g['risk_flags'],g['count']) for g in data['groups'][:15]],'production_modified':False},ensure_ascii=False))
if __name__=='__main__':main()
