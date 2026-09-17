#!/usr/bin/env python3
"""Export remaining Issue #70 Character ACCEPTED_AI rows for semantic diagnosis.

Diagnostic only. Does not modify production Issue #70 data or assign audit verdicts.
"""
from __future__ import annotations
import csv,json,shutil,subprocess,sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'
TMP=ROOT/'artifacts/issue70-semantic-audit-v3-batch029-diagnostic'
OUT=AUDIT/'character_remaining_accepted_batch029_diagnostic.csv'
SUMMARY=AUDIT/'character_remaining_accepted_batch029_summary.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def done_ids():
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

def main():
    done=done_ids(); rows=[]
    for r in census():
        if r.get('row_id') in done:continue
        if r.get('category_name')!='Character' or r.get('translation_status')!='ACCEPTED_AI':continue
        rows.append({k:r.get(k) or '' for k in [
            'row_id','canonical_tag','post_count','display_ja','search_ja','translation_note','risk_flags','audit_bucket','impact_tier',
            'source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja',
            'related_copyright_top1','related_copyright_top1_coverage','family_base_canonical','family_base_display_ja']})
    rows.sort(key=lambda r:(-int(r['post_count'] or 0),r['row_id']))
    fields=list(rows[0].keys()) if rows else ['row_id']
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    sig=Counter((r['translation_note'] or '<blank>',r['risk_flags'] or '<none>',r['audit_bucket'] or '<none>') for r in rows)
    groups=[]
    for (note,flags,bucket),count in sig.most_common():
        samples=[r for r in rows if (r['translation_note'] or '<blank>')==note and (r['risk_flags'] or '<none>')==flags and (r['audit_bucket'] or '<none>')==bucket][:8]
        groups.append({'translation_note':note,'risk_flags':flags,'audit_bucket':bucket,'count':count,'samples':samples})
    data={'format_version':1,'issue':70,'production_modified':False,'population':len(rows),'groups':groups}
    SUMMARY.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'population':len(rows),'group_count':len(groups),'production_modified':False},ensure_ascii=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
