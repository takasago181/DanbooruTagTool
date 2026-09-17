#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from pathlib import Path
BASE=Path('docs/issue118/research_sidecar_v28.csv')
INPUTS=[
('V50',Path('docs/issue118/overlap_restraint_action_review_v50/review_policy_v50.json'),Path('docs/issue118/overlap_restraint_action_review_v50/full_review_candidate_v50.csv'),38),
('V51',Path('docs/issue118/special_restraint_fetish_review_v51/review_policy_v51.json'),Path('docs/issue118/special_restraint_fetish_review_v51/full_review_candidate_v51.csv'),35),
]
OUT=Path('docs/issue118/research_sidecar_v29.csv');SUMMARY=Path('docs/issue118/research_sidecar_summary_v29.json')
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha256(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def groups(review,source_set):
    counts=review['decision_counts'];g={'SEXUAL':set(review.get('sexual') or []),'CONTEXTUAL':set(review.get('contextual') or []),'NON_SEXUAL':set(review.get('non_sexual') or [])};union=set()
    for intent,s in g.items():
        if not s<=source_set:raise SystemExit(f'{intent} outside source')
        if union&s:raise SystemExit('review groups overlap')
        union|=s
    missing=source_set-union;deficits={i:int(counts[i])-len(g[i]) for i in g}
    if any(v<0 for v in deficits.values()):raise SystemExit(f'negative deficit {deficits}')
    pos=[i for i,v in deficits.items() if v>0]
    if missing:
        if len(pos)!=1 or deficits[pos[0]]!=len(missing):raise SystemExit(f'cannot infer omitted group: missing={len(missing)} deficits={deficits}')
        g[pos[0]]|=missing
    elif pos:raise SystemExit(f'counts require missing rows: {deficits}')
    if {i:len(s) for i,s in g.items()}!=counts:raise SystemExit('review count drift')
    return g
def main():
    base=read_csv(BASE)
    if len(base)!=31752:raise SystemExit(f'base drift {len(base)}')
    index={r['identity_key']:dict(r) for r in base};promoted=Counter();seen=set();review_inputs=[]
    for label,rp,sp,n in INPUTS:
        source=read_csv(sp);review=json.loads(rp.read_text(encoding='utf-8'))
        if len(source)!=n or review.get('source_rows')!=n:raise SystemExit(f'{label} source count drift')
        source_set={r['identity_key'] for r in source}
        if seen&source_set:raise SystemExit('review input overlap')
        seen|=source_set;gg=groups(review,source_set)
        for intent,keys in gg.items():
            for key in sorted(keys):
                t=index.get(key)
                if t is None or t['review_status']!='UNCLASSIFIED' or t['sexual_intent']:raise SystemExit(f'{label} not cleanly unclassified: {key}')
                t['sexual_intent']=intent;t['review_status']='HUMAN_REVIEWED';t['rule_id']=f'HUMAN_{intent}_{label}';t['evidence']=f'full human review of fixed {label} candidate set';promoted[intent]+=1
        review_inputs.append({'label':label,'review_source':str(rp),'review_sha256':sha256(rp),'source_rows':n})
    rows=[index[r['identity_key']] for r in base];status=Counter(r['review_status'] for r in rows);classes=Counter(r['sexual_intent'] or 'NULL' for r in rows)
    es={'AUTO_HIGH_CONF':22371,'HUMAN_REVIEWED':3437,'UNCLASSIFIED':5944};ec={'CONTEXTUAL':952,'NON_SEXUAL':23411,'NULL':5944,'SEXUAL':1445}
    if dict(sorted(status.items()))!=es:raise SystemExit(f'status mismatch {dict(status)}')
    if dict(sorted(classes.items()))!=ec:raise SystemExit(f'class mismatch {dict(classes)}')
    with OUT.open('w',encoding='utf-8',newline='') as f:
        fields=list(rows[0].keys());w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    s={'issue':118,'mode':'RESEARCH_SIDECAR_V29_V50_V51_FULL_REVIEWS','identity_rows':len(rows),'source_base':str(BASE),'new_promotions':dict(sorted(promoted.items())),'new_total_promotions':sum(promoted.values()),'review_status_counts':dict(sorted(status.items())),'sexual_intent_counts':dict(sorted(classes.items())),'remaining_unclassified':status['UNCLASSIFIED'],'review_inputs':review_inputs,'review_verdicts_generated_by_materializer':'NO','review_artifacts_are_external_inputs':'YES','production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    SUMMARY.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(s,ensure_ascii=False,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
