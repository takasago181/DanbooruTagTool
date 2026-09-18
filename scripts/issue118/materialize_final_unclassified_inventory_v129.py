#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path

SRC=Path('docs/issue118/research_sidecar_v95.csv')
OUTDIR=Path('docs/issue118/final_unclassified_inventory_v129')
OUT=OUTDIR/'remaining_unclassified_v129.csv'
SUMMARY=OUTDIR/'summary_v129.json'

def main():
    with SRC.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=31752:
        raise SystemExit(f'expected 31752 sidecar rows, got {len(rows)}')
    rem=[dict(r) for r in rows if r.get('review_status')=='UNCLASSIFIED']
    if len(rem)!=6:
        raise SystemExit(f'expected 6 remaining unclassified rows, got {len(rem)}')
    OUTDIR.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0].keys())
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows(rem)
    s={
      'issue':118,
      'mode':'FINAL_UNCLASSIFIED_INVENTORY_V129',
      'source_sidecar':'docs/issue118/research_sidecar_v95.csv',
      'identity_rows':len(rows),
      'remaining_unclassified':len(rem),
      'identity_keys':[r['identity_key'] for r in rem],
      'review_verdicts_generated_by_materializer':'NO',
      'review_artifacts_are_external_inputs':'YES',
      'production_authority':'NO',
      'main_mutated':'NO',
      'issue117_code_mutated':'NO',
      'catalog_mutated':'NO',
      'user_db_mutated':'NO',
      'next_gate':'manual semantic review of only the six remaining unresolved identities'
    }
    SUMMARY.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(s,ensure_ascii=False,sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
