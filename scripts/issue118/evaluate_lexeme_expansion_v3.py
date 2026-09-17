#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

SIDECAR=Path('docs/issue118/research_sidecar_v1.csv')
OUT=Path('docs/issue118/lexeme_expansion_v3')

LEXEMES={
    'footjob': re.compile(r'(^|_)footjob($|_)'),
    'glansjob': re.compile(r'(^|_)glansjob($|_)'),
    'hairjob': re.compile(r'(^|_)hairjob($|_)'),
    'backjob': re.compile(r'(^|_)backjob($|_)'),
    'pecfuck': re.compile(r'(^|_)pecfuck($|_)'),
    'buttsex': re.compile(r'(^|_)buttsex($|_)'),
    'frottage': re.compile(r'(^|_)frottage($|_)'),
    'rape': re.compile(r'(^|_)(rape|raped|raping)($|_)'),
}


def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))


def main():
    rows=read_csv(SIDECAR)
    un=[r for r in rows if r['review_status']=='UNCLASSIFIED']
    by=defaultdict(list)
    for r in un:
        key=r['identity_key']
        for name,rx in LEXEMES.items():
            if rx.search(key): by[name].append(r)
    review=[]; summary={}
    for name in LEXEMES:
        vals=sorted(by[name],key=lambda r:r['identity_key'])
        sample=vals if len(vals)<=12 else vals[:6]+vals[-6:]
        summary[name]={'matches':len(vals),'sample_rows':len(sample)}
        for r in sample:
            review.append({'lexeme':name,'match_count':str(len(vals)),**r,'reviewed_class':'','review_status_check':'','review_note':''})
    OUT.mkdir(parents=True,exist_ok=True)
    if review:
        with (OUT/'validation_sample_v1.csv').open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(review[0]),lineterminator='\n');w.writeheader();w.writerows(review)
    result={'issue':118,'mode':'SEXUAL_LEXEME_EXPANSION_V3_CANDIDATE','source_unclassified':len(un),
            'lexemes':summary,'unique_candidate_identities':len({r['identity_key'] for vals in by.values() for r in vals}),
            'validation_rows':len(review),'production_promotion_performed':'NO'}
    (OUT/'summary_v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
