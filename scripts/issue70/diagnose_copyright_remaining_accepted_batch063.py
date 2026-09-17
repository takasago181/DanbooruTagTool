#!/usr/bin/env python3
"""Diagnose the final remaining ACCEPTED_AI Copyright audit rows.

Groups rows by normalized display and records canonical/source evidence so the
last Accepted Copyright rows can be split into safe KEEP, source-backed
fix/disambiguation, and genuine external-check buckets. Read-only/proposal-only.
"""
from __future__ import annotations
import csv, json, shutil, subprocess, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'; TMP=ROOT/'artifacts/issue70-copyright-batch063'
OUT=AUDIT/'copyright_remaining_accepted_batch063_diagnostic.json'
VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(v):return ' '.join(unicodedata.normalize('NFKC',v or '').strip().lower().replace('_',' ').replace('・',' ').split())
def terms(v):return [x.strip() for x in (v or '').split('|') if x.strip()]
def done_ids():
    ids=set()
    for p in AUDIT.glob('*.csv'):
        if 'diagnostic' in p.name:continue
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            if (r.get('audit_verdict') or '').strip() in VALID and (r.get('row_id') or '').strip(): ids.add(r['row_id'].strip())
    return ids

def census():
    if TMP.exists():shutil.rmtree(TMP)
    subprocess.run([sys.executable,str(ROOT/'scripts/issue70/audit_semantic_risk_v3.py'),'--out',str(TMP),'--sample-per-category','300'],cwd=ROOT,check=True)
    return read_csv(TMP/'audit_ledger_template.csv')
def main():
    done=done_ids(); rows=[]
    for r in census():
        if r.get('row_id') in done or r.get('category_name')!='Copyright' or r.get('translation_status')!='ACCEPTED_AI':continue
        rows.append(r)
    by_display=defaultdict(list)
    for r in rows:by_display[norm(r.get('display_ja') or '')].append(r)
    recs=[]
    for r in sorted(rows,key=lambda x:(-int(x.get('post_count') or 0),x['row_id'])):
        group=by_display[norm(r.get('display_ja') or '')]
        source_ja=[]
        for f in ('existing_display_ja','existing_search_ja','existing_candidate_ja'):
            source_ja += terms(r.get(f) or '')
        recs.append({k:r.get(k) or '' for k in ['row_id','canonical_tag','post_count','impact_tier','display_ja','search_ja','translation_note','risk_flags','audit_bucket','source_aliases','verified_aliases','existing_display_ja','existing_search_ja','existing_candidate_ja','existing_rejected_ja']} | {
          'duplicate_group_size':len(group),
          'duplicate_group_tags':[x.get('canonical_tag') or '' for x in group],
          'source_ja_terms':source_ja,
          'display_exact_in_preserved_ja':any(norm(x)==norm(r.get('display_ja') or '') for x in source_ja),
        })
    payload={
      'format_version':1,'issue':70,'production_modified':False,'population':len(rows),
      'status_counts':dict(Counter(r.get('translation_status') or '<blank>' for r in rows)),
      'risk_flag_counts':dict(Counter(f.strip() for r in rows for f in (r.get('risk_flags') or '').split('|') if f.strip())),
      'translation_note_counts':dict(Counter(r.get('translation_note') or '<blank>' for r in rows)),
      'duplicate_rows':sum(1 for r in recs if r['duplicate_group_size']>1),
      'exact_preserved_ja_rows':sum(1 for r in recs if r['display_exact_in_preserved_ja']),
      'rows':recs,
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print({k:payload[k] for k in ['population','duplicate_rows','exact_preserved_ja_rows','production_modified']})
if __name__=='__main__':main()
