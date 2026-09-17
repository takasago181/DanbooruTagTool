#!/usr/bin/env python3
"""Summarize second-stage external resolution progress for Issue #70.

Primary semantic audit decisions remain immutable. Rows initially marked
NEEDS_EXTERNAL_CHECK are resolved in docs/issue70/audit/external_resolutions/*.csv.
This avoids turning a legitimate second-stage resolution into a primary-ledger
conflict while preserving a full audit trail.
"""
from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'docs/issue70/audit'
EXT=AUDIT/'external_resolutions'
OUT=AUDIT/'EXTERNAL_PROGRESS_LIVE.json'
PRIMARY_VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH','NEEDS_EXTERNAL_CHECK','NEEDS_USER_DECISION'}
FINAL_VALID={'KEEP','FIX_DISPLAY','FIX_SEARCH','FIX_BOTH'}

def read_csv(p:Path):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def main():
    external_ids={}
    for p in sorted(AUDIT.glob('*.csv')):
        if p.parent==EXT: continue
        try: rows=read_csv(p)
        except Exception: continue
        for r in rows:
            rid=(r.get('row_id') or '').strip(); v=(r.get('audit_verdict') or '').strip()
            if rid and v=='NEEDS_EXTERNAL_CHECK':
                external_ids[rid]={'category':(r.get('category') or r.get('category_name') or '').strip(),
                                   'canonical_tag':(r.get('canonical_tag') or '').strip(),
                                   'source_file':p.name}
    resolved={}; conflicts=[]
    if EXT.exists():
        for p in sorted(EXT.glob('*.csv')):
            for r in read_csv(p):
                rid=(r.get('row_id') or '').strip(); v=(r.get('external_verdict') or '').strip()
                if rid not in external_ids or v not in FINAL_VALID: continue
                d=((r.get('proposed_display_ja') or '').strip(),(r.get('proposed_search_ja') or '').strip())
                entry={'external_verdict':v,'proposed_display_ja':d[0],'proposed_search_ja':d[1],
                       'source_file':p.name,'canonical_tag':external_ids[rid]['canonical_tag'],
                       'category':external_ids[rid]['category']}
                if rid in resolved and (resolved[rid]['external_verdict'],resolved[rid]['proposed_display_ja'],resolved[rid]['proposed_search_ja']) != (v,d[0],d[1]):
                    conflicts.append({'row_id':rid,'first':resolved[rid],'second':entry})
                resolved[rid]=entry
    remaining=set(external_ids)-set(resolved)
    by_verdict=Counter(v['external_verdict'] for v in resolved.values())
    by_category_resolved=Counter(v['category'] or '<unknown>' for v in resolved.values())
    by_category_remaining=Counter((external_ids[r]['category'] or '<unknown>') for r in remaining)
    result={
      'format_version':1,'issue':70,'production_modified':False,
      'initial_external_rows':len(external_ids),'resolved_external_rows':len(resolved),
      'remaining_external_rows':len(remaining),'conflicted_external_rows':len(conflicts),
      'resolved_verdict_counts':dict(sorted(by_verdict.items())),
      'resolved_by_category':dict(sorted(by_category_resolved.items())),
      'remaining_by_category':dict(sorted(by_category_remaining.items())),
      'conflicts':conflicts,
      'next_step':'continue official-source verification in impact order; do not mutate production until external queue reaches closure or an explicit stop rule is accepted'
    }
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not conflicts else 2
if __name__=='__main__':raise SystemExit(main())
