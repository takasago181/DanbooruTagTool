#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

BASE=Path('docs/issue118/research_sidecar_v1.csv')
LEX=Path('docs/issue118/lexeme_expansion_v3/all_matches_v1.csv')
GEN=Path('docs/issue118/general_subpath_candidates_v1/candidate_rows.csv')
OUT=Path('docs/issue118/research_sidecar_v2.csv')
SUMMARY=Path('docs/issue118/research_sidecar_summary_v2.json')


def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def write_csv(path,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def main():
    rows=read_csv(BASE)
    if len(rows)!=31752:raise SystemExit(f'base drift {len(rows)}')
    index={r['identity_key']:r for r in rows}
    lex={r['identity_key'] for r in read_csv(LEX)}
    gen={r['identity_key'] for r in read_csv(GEN)}
    if lex & gen: raise SystemExit('sexual/nonsexual expansion conflict')
    promoted=Counter()
    for key in sorted(lex):
        r=index[key]
        if r['review_status']!='UNCLASSIFIED':raise SystemExit(f'lexeme target already classified {key}')
        r['sexual_intent']='SEXUAL';r['review_status']='AUTO_HIGH_CONF';r['rule_id']='AUTO_SEXUAL_EXPLICIT_LEXEMES_V3';r['evidence']='FULL_MATCH_REVIEW_50_50'
        promoted['SEXUAL']+=1
    for key in sorted(gen):
        r=index[key]
        if r['review_status']!='UNCLASSIFIED':raise SystemExit(f'general target already classified {key}')
        r['sexual_intent']='NON_SEXUAL';r['review_status']='AUTO_HIGH_CONF';r['rule_id']='AUTO_NONSEX_VALIDATED_GENERAL_SUBPATHS_V3';r['evidence']='PILOT_PURE+FRESH_HOLDOUT_30_30'
        promoted['NON_SEXUAL']+=1
    out=[index[k] for k in sorted(index)]
    write_csv(OUT,out)
    status=Counter(r['review_status'] for r in out)
    classes=Counter(r['sexual_intent'] or 'NULL' for r in out)
    summary={'issue':118,'mode':'RESEARCH_SIDECAR_V2_EFFICIENCY_EXPANDED','identity_rows':len(out),
             'new_promotions':dict(promoted),'new_promotions_total':sum(promoted.values()),
             'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),
             'v3_rules':{
                 'AUTO_SEXUAL_EXPLICIT_LEXEMES_V3':'50/50 full candidate identities semantically checked',
                 'AUTO_NONSEX_VALIDATED_GENERAL_SUBPATHS_V3':'3 paths; pilot-pure and fresh holdout 30/30 NON_SEXUAL',
             },
             'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO'}
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
