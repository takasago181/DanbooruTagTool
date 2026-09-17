#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL = Path('data/generation/special2788_generation_profile.csv')
PILOT_REVIEWS = Path('docs/issue118/reviews')
HOLDOUT_REVIEWS = Path('docs/issue118/holdout/reviews')
SIDECAR = Path('docs/issue118/research_sidecar_v1.csv')
OUT_DIR = Path('docs/issue118/cluster_rules_v1')
VALID = {'SEXUAL','NON_SEXUAL','CONTEXTUAL'}

LEX_GROUPS = {
    'EXPLICIT_SEX': {'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm','masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia'},
    'ANATOMY_SEXUALIZED': {'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples','breast','breasts','areola','areolae'},
    'RESTRAINT': {'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps'},
    'REPRO': {'pregnant','pregnancy','lactation','breastfeeding','birth','insemination','fertilization','fertilisation'},
    'INJURY': {'blood','wound','gore','amputee','amputation','castration','corpse','injury'},
    'EXPOSURE': {'nude','naked','topless','bottomless','panties','underwear','bra','cleavage','underboob','upskirt','downblouse'},
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return '_'.join(v.strip().lower().replace('_',' ').split())


def root(v: str) -> str:
    v=(v or '').strip()
    return v.split('/',1)[0] if v else ''


def membership(gr, sr):
    if gr is not None and sr is not None:
        return 'OVERLAP'
    if gr is not None:
        return 'GENERAL_ONLY'
    return 'SPECIAL_ONLY'


def lex_flags(key: str):
    parts=set(p for p in key.replace('(','_').replace(')','_').replace('-','_').split('_') if p)
    return tuple(sorted(name for name,tokens in LEX_GROUPS.items() if parts & tokens))


def load_labels(directory: Path, status_field: str):
    out={}
    for p in sorted(directory.glob('chunk_*_review_v1.csv')):
        for r in read_csv(p):
            key=norm(r['identity_key'])
            status=(r.get(status_field) or r.get('pilot_review_status') or r.get('review_status') or '').strip()
            cls=(r.get('reviewed_class') or '').strip()
            if status == 'REVIEWED' and cls in VALID:
                if key in out:
                    raise SystemExit(f'duplicate review: {key}')
                out[key]=cls
    return out


def signatures(key, gr, sr):
    mem=membership(gr,sr)
    rt=root((gr or {}).get('primary_path',''))
    full=((gr or {}).get('primary_path','') or '').strip()
    fam=((sr or {}).get('GenerationFamily','') or '').strip()
    flags=lex_flags(key)
    sig=[]
    def add(name, value):
        if value:
            sig.append((name,value))
    add('MEMBERSHIP',mem)
    add('GENERAL_ROOT',rt)
    add('GENERAL_PATH',full)
    add('SPECIAL_FAMILY',fam)
    if rt: add('MEMBERSHIP+GENERAL_ROOT',f'{mem}|{rt}')
    if fam: add('MEMBERSHIP+SPECIAL_FAMILY',f'{mem}|{fam}')
    if rt and fam: add('GENERAL_ROOT+SPECIAL_FAMILY',f'{rt}|{fam}')
    if rt and fam: add('MEMBERSHIP+ROOT+FAMILY',f'{mem}|{rt}|{fam}')
    for fl in flags:
        add('LEX',fl)
        if rt: add('GENERAL_ROOT+LEX',f'{rt}|{fl}')
        if fam: add('SPECIAL_FAMILY+LEX',f'{fam}|{fl}')
        add('MEMBERSHIP+LEX',f'{mem}|{fl}')
    if not flags:
        add('NO_RISK_LEX','YES')
        if rt: add('GENERAL_ROOT+NO_RISK_LEX',rt)
        if fam: add('SPECIAL_FAMILY+NO_RISK_LEX',fam)
        add('MEMBERSHIP+NO_RISK_LEX',mem)
    return sig


def eval_rules(labels, g, s):
    buckets=defaultdict(list)
    for key,cls in labels.items():
        for sig in signatures(key,g.get(key),s.get(key)):
            buckets[sig].append((key,cls))
    stats={}
    for sig,rows in buckets.items():
        c=Counter(cls for _,cls in rows)
        target,count=c.most_common(1)[0]
        stats[sig]={
            'matched':len(rows),
            'target':target,
            'precision':count/len(rows),
            'class_counts':dict(sorted(c.items())),
            'examples':[k for k,_ in rows[:8]],
        }
    return stats


def matches(sig, key, gr, sr):
    return sig in signatures(key,gr,sr)


def main():
    general=read_csv(GENERAL); special=read_csv(SPECIAL); sidecar=read_csv(SIDECAR)
    if len(general)!=30629 or len(special)!=3059 or len(sidecar)!=31752:
        raise SystemExit('input drift')
    g={norm(r['canonical']):r for r in general}
    s={norm(r['Tag']):r for r in special}
    pilot=load_labels(PILOT_REVIEWS,'pilot_review_status')
    holdout=load_labels(HOLDOUT_REVIEWS,'review_status')
    if len(pilot)!=684 or len(holdout)!=240:
        raise SystemExit(f'label drift pilot={len(pilot)} holdout={len(holdout)}')
    train=eval_rules(pilot,g,s); test=eval_rules(holdout,g,s)
    unknown=[r['identity_key'] for r in sidecar if r['review_status']=='UNCLASSIFIED']

    candidates=[]
    for sig,tr in train.items():
        te=test.get(sig)
        if not te:
            continue
        if tr['matched'] < 5 or te['matched'] < 3:
            continue
        if tr['precision'] != 1.0 or te['precision'] != 1.0:
            continue
        if tr['target'] != te['target']:
            continue
        coverage=[k for k in unknown if matches(sig,k,g.get(k),s.get(k))]
        if not coverage:
            continue
        candidates.append({
            'signature_type':sig[0], 'signature_value':sig[1], 'target_class':tr['target'],
            'pilot_support':tr['matched'], 'holdout_support':te['matched'],
            'pilot_precision':1.0, 'holdout_precision':1.0,
            'unclassified_coverage':len(coverage), 'coverage_examples':coverage[:12],
        })

    candidates.sort(key=lambda r:(-r['unclassified_coverage'],-r['holdout_support'],-r['pilot_support'],r['signature_type'],r['signature_value']))

    # Greedy conflict-free pack: add broadest validated rules first, but never let two selected rules
    # assign different classes to the same currently-unclassified identity.
    assigned={}; selected=[]
    for r in candidates:
        sig=(r['signature_type'],r['signature_value']); target=r['target_class']
        matched=[k for k in unknown if matches(sig,k,g.get(k),s.get(k))]
        if any(k in assigned and assigned[k]!=target for k in matched):
            continue
        new=[k for k in matched if k not in assigned]
        if len(new) < 5:
            continue
        for k in new: assigned[k]=target
        rr=dict(r); rr['new_coverage']=len(new); selected.append(rr)

    OUT_DIR.mkdir(parents=True,exist_ok=True)
    with (OUT_DIR/'validated_candidates_v1.csv').open('w',encoding='utf-8',newline='') as f:
        fields=['signature_type','signature_value','target_class','pilot_support','holdout_support','pilot_precision','holdout_precision','unclassified_coverage','coverage_examples']
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader()
        for r in candidates:
            x=dict(r); x['coverage_examples']=';'.join(x['coverage_examples']); w.writerow(x)
    with (OUT_DIR/'selected_conflict_free_v1.csv').open('w',encoding='utf-8',newline='') as f:
        fields=['signature_type','signature_value','target_class','pilot_support','holdout_support','unclassified_coverage','new_coverage']
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n'); w.writeheader(); w.writerows([{k:r[k] for k in fields} for r in selected])

    summary={
        'issue':118,
        'mode':'VALIDATED_CLUSTER_RULE_DISCOVERY_V1',
        'pilot_reviewed':len(pilot),'independent_holdout_reviewed':len(holdout),'source_unclassified':len(unknown),
        'candidate_rules_100pct_both':len(candidates),'selected_conflict_free_rules':len(selected),
        'selected_new_coverage':len(assigned),'remaining_after_selected':len(unknown)-len(assigned),
        'selected_class_counts':dict(sorted(Counter(assigned.values()).items())),
        'top_candidates':candidates[:20],
        'guard':'Candidate rules require 100% precision on pilot and independent holdout with minimum support; still research-only.',
        'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO'
    }
    (OUT_DIR/'summary_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['candidate_rules_100pct_both','selected_conflict_free_rules','selected_new_coverage','remaining_after_selected','selected_class_counts']},sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
