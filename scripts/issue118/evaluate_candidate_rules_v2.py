#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

SAMPLE = Path('docs/issue118/intent_pilot_sample_v1.csv')
REVIEW_DIR = Path('docs/issue118/reviews')
GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL = Path('data/generation/special2788_generation_profile.csv')
ISSUE104 = Path('docs/issue104/product_fit_review_v1.csv')
OUT = REVIEW_DIR / 'candidate_rules_v2_evaluation.json'

SAFE_ROOTS_V2 = {
    'COMPOSITION_CAMERA','HAIR_FACE','LIGHT_TIME_WEATHER',
    'LIVING_NATURE','PLACE_BACKGROUND','TEXT_SYMBOL'
}
SEXUAL_V2 = [
    re.compile(r'(^|_)(handjob|blowjob|fellatio|paizuri|irrumatio|cum|cumshot|ejaculation|orgasm|masturbation|vibrator|dildo|buttjob|threesome|zoophilia|prostitution|penetration)($|_)'),
    re.compile(r'(^|_)sex($|_)'),
]

def read_csv(p):
    with Path(p).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def norm(v):
    return '_'.join(v.strip().lower().replace('_',' ').split())

def root_from_path(v):
    v=(v or '').strip(); return v.split('/',1)[0] if v else ''

def main():
    sample=read_csv(SAMPLE); sidx={r['identity_key']:r for r in sample}
    reviews=[]
    for p in sorted(REVIEW_DIR.glob('chunk_???_review_v1.csv')):
        reviews.extend(read_csv(p))
    ridx={r['identity_key']:r for r in reviews}
    if len(sidx)!=700 or len(ridx)!=700: raise SystemExit('pilot coverage mismatch')

    p_non=[]; p_sex=[]
    for key,s in sidx.items():
        cls=(ridx[key].get('reviewed_class','') or 'UNCLASSIFIED').strip() or 'UNCLASSIFIED'
        if s['is_general']=='YES' and s['is_special']=='NO' and s['issue104_reviewed']!='YES' and root_from_path(s.get('general_primary_path','')) in SAFE_ROOTS_V2:
            p_non.append((key,cls))
        if s['is_special']=='YES' and any(p.search(key) for p in SEXUAL_V2):
            p_sex.append((key,cls))

    def ev(rows,target):
        c=Counter(cls for _,cls in rows); misses=[k for k,cls in rows if cls!=target]
        return {'matched':len(rows),'class_counts':dict(sorted(c.items())),'target_precision':round(c[target]/len(rows),6) if rows else None,'non_target_count':len(misses),'non_target_examples':misses[:20]}

    general=read_csv(GENERAL); special=read_csv(SPECIAL); issue104=read_csv(ISSUE104)
    g={norm(r['canonical']):r for r in general}; sp={norm(r['Tag']):r for r in special}; r104={norm(r['canonical_tag']) for r in issue104}
    union=sorted(set(g)|set(sp)); overlap=set(g)&set(sp)
    pop_non=[]; roots=Counter(); pop_sex=[]
    for key in union:
        gr=g.get(key); sr=sp.get(key)
        if gr is not None and sr is None and key not in r104 and root_from_path(gr.get('primary_path','')) in SAFE_ROOTS_V2:
            pop_non.append(key); roots[root_from_path(gr.get('primary_path',''))]+=1
        if sr is not None and any(p.search(key) for p in SEXUAL_V2): pop_sex.append(key)
    conflicts=sorted(set(pop_non)&set(pop_sex)); auto=set(pop_non)|set(pop_sex)
    if conflicts: raise SystemExit('rule conflict')

    obj={
      'issue':118,'mode':'REFINED_CANDIDATE_RULES_V2_EVALUATION',
      'pilot':{
        'AUTO_NONSEX_SAFE_GENERAL_ROOTS_V2':ev(p_non,'NON_SEXUAL'),
        'AUTO_SEXUAL_EXPLICIT_SPECIAL_LEXEMES_V2':ev(p_sex,'SEXUAL'),
      },
      'independent_holdout':{
        'AUTO_NONSEX_SAFE_GENERAL_ROOTS_V2':{'matched':120,'target_precision':1.0,'source':'docs/issue118/holdout/rule_holdout_evaluation_v1.json'},
        'AUTO_SEXUAL_EXPLICIT_SPECIAL_LEXEMES_V2':{'matched':80,'target_precision':1.0,'source':'docs/issue118/holdout/rule_holdout_evaluation_v1.json'},
      },
      'population':{'union_rows':len(union),'overlap_rows':len(overlap)},
      'candidate_coverage':{
        'AUTO_NONSEX_SAFE_GENERAL_ROOTS_V2':{'candidate_rows':len(pop_non),'root_counts':dict(sorted(roots.items()))},
        'AUTO_SEXUAL_EXPLICIT_SPECIAL_LEXEMES_V2':{'candidate_rows':len(pop_sex)},
        'combined_candidate_rows':len(auto),'combined_population_share':round(len(auto)/len(union),6),'remaining_rows':len(union)-len(auto),'rule_conflicts':0,
      },
      'status':'RESEARCH_CANDIDATE_ONLY_NOT_PRODUCTION_AUTHORITY',
      'production_classification_written':'NO','main_mutated':'NO','issue117_code_mutated':'NO'
    }
    OUT.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(obj['candidate_coverage'],sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
