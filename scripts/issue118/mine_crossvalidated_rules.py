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
QUEUE = Path('docs/issue118/coverage_queue_v1')
OUT = Path('docs/issue118/efficiency_mining_v1')
VALID = {'SEXUAL','NON_SEXUAL','CONTEXTUAL'}
STOP = {
    'with','without','another','own','between','around','under','over','on','in','of','the',
    'female','male','viewer','one','two','three','four','self','from','and','or','to','a','an',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return '_'.join(v.strip().lower().replace('_',' ').split())


def root(row: dict[str,str] | None) -> str:
    p=(row or {}).get('primary_path','').strip()
    return p.split('/',1)[0] if p else ''


def tokens(key: str) -> set[str]:
    out=set()
    for t in key.replace('(','_').replace(')','_').replace('-','_').split('_'):
        t=t.strip().lower()
        if len(t) >= 4 and not t.isdigit() and t not in STOP:
            out.add(t)
    return out


def load_reviews():
    result=[]
    for cohort, directory, pattern in [
        ('PILOT', PILOT_REVIEWS, 'chunk_???_review_v1.csv'),
        ('HOLDOUT', HOLDOUT_REVIEWS, 'chunk_*_review_v1.csv'),
    ]:
        for path in sorted(directory.glob(pattern)):
            for r in read_csv(path):
                status=(r.get('pilot_review_status') or r.get('review_status') or '').strip()
                cls=(r.get('reviewed_class') or '').strip()
                if status == 'REVIEWED' and cls in VALID:
                    result.append((norm(r['identity_key']), cls, cohort))
    return result


def features(key: str, gr, sr):
    feats=set()
    rt=root(gr)
    fam=(sr or {}).get('GenerationFamily','').strip()
    membership=('OVERLAP' if gr and sr else 'GENERAL_ONLY' if gr else 'SPECIAL_ONLY')
    feats.add(f'MEMBERSHIP={membership}')
    if rt: feats.add(f'GROOT={rt}')
    if fam: feats.add(f'SFAM={fam}')
    ts=tokens(key)
    for t in ts:
        feats.add(f'TOK={t}')
        if rt: feats.add(f'TOK={t}|GROOT={rt}')
        if fam: feats.add(f'TOK={t}|SFAM={fam}')
    return feats


def main() -> int:
    general=read_csv(GENERAL); special=read_csv(SPECIAL)
    g={norm(r['canonical']):r for r in general}
    s={norm(r['Tag']):r for r in special}
    reviews=load_reviews()
    if len(reviews) != 924:
        raise SystemExit(f'expected 924 resolved human reviews, got {len(reviews)}')

    evidence=defaultdict(lambda: {'PILOT':Counter(), 'HOLDOUT':Counter()})
    for key, cls, cohort in reviews:
        for f in features(key, g.get(key), s.get(key)):
            evidence[f][cohort][cls] += 1

    accepted=[]
    for feat, byc in evidence.items():
        p=byc['PILOT']; h=byc['HOLDOUT']
        total=p+h
        classes=[c for c,n in total.items() if n]
        if len(classes) != 1:
            continue
        cls=classes[0]
        ps=sum(p.values()); hs=sum(h.values()); support=ps+hs
        if ps < 2 or hs < 2 or support < 6:
            continue
        # Broad taxonomy/family-only rules are too coarse for intent. Keep them only as diagnostics,
        # never as candidates. Candidate rules must contain a lexical token.
        if 'TOK=' not in feat:
            continue
        accepted.append({
            'feature':feat,'target_class':cls,'pilot_support':ps,'holdout_support':hs,
            'total_support':support,
        })
    accepted.sort(key=lambda r:(-int(r['total_support']), r['feature']))

    queue=[]
    for path in sorted(QUEUE.glob('chunk_*.csv')):
        queue.extend(read_csv(path))
    if len(queue) != 1000:
        raise SystemExit(f'expected queue 1000, got {len(queue)}')

    rules_by_feature={r['feature']:r for r in accepted}
    candidates=[]; unresolved=[]; conflicts=[]
    for q in queue:
        key=norm(q['identity_key'])
        hits=[rules_by_feature[f] for f in features(key,g.get(key),s.get(key)) if f in rules_by_feature]
        classes=sorted({r['target_class'] for r in hits})
        if len(classes) == 1:
            best=sorted(hits,key=lambda r:(-int(r['total_support']),r['feature']))[0]
            candidates.append({
                **q,
                'candidate_class':classes[0],
                'best_rule':best['feature'],
                'best_rule_support':best['total_support'],
                'matching_rule_count':str(len(hits)),
            })
        elif len(classes) > 1:
            conflicts.append({**q,'candidate_classes':';'.join(classes),'matching_rule_count':str(len(hits))})
        else:
            unresolved.append(q)

    # Compact validation sample: at most 120 identities, stratified by candidate class and best rule.
    groups=defaultdict(list)
    for r in candidates:
        groups[(r['candidate_class'],r['best_rule'])].append(r)
    validation=[]
    for keygrp, rows in sorted(groups.items(), key=lambda kv:(kv[0][0], kv[0][1])):
        rows=sorted(rows,key=lambda r:r['identity_key'])
        validation.extend(rows[:3])
    if len(validation) > 120:
        # Deterministic cap while preserving all three target classes when present.
        per=[]
        byclass=defaultdict(list)
        for r in validation: byclass[r['candidate_class']].append(r)
        while len(per)<120 and any(byclass.values()):
            for cls in ('SEXUAL','NON_SEXUAL','CONTEXTUAL'):
                if byclass[cls] and len(per)<120:
                    per.append(byclass[cls].pop(0))
        validation=per

    OUT.mkdir(parents=True,exist_ok=True)
    def write(path, rows):
        if not rows:
            path.write_text('',encoding='utf-8'); return
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n'); w.writeheader(); w.writerows(rows)
    write(OUT/'accepted_rule_candidates.csv',accepted)
    write(OUT/'queue_rule_candidates.csv',candidates)
    write(OUT/'queue_rule_conflicts.csv',conflicts)
    write(OUT/'validation_sample_v1.csv',validation)

    summary={
        'issue':118,
        'mode':'CROSS_VALIDATED_EFFICIENCY_MINING_V1',
        'resolved_human_reviews':len(reviews),
        'accepted_crossvalidated_rules':len(accepted),
        'coverage_queue_rows':len(queue),
        'candidate_rows':len(candidates),
        'conflict_rows':len(conflicts),
        'unresolved_rows':len(unresolved),
        'validation_sample_rows':len(validation),
        'candidate_class_counts':dict(sorted(Counter(r['candidate_class'] for r in candidates).items())),
        'safety_contract':{
            'requires_both_pilot_and_holdout_support':True,
            'minimum_support_total':6,
            'minimum_support_per_cohort':2,
            'training_purity_required':1.0,
            'taxonomy_or_family_only_rules_allowed':False,
            'production_promotion_performed':'NO',
        },
    }
    (OUT/'summary_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
