#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL = Path('data/generation/special2788_generation_profile.csv')
QUEUE = Path('docs/issue118/coverage_queue_v1')
OUT = Path('docs/issue118/efficiency_clustering_v1')

BUCKETS = [
    ('SEX_ACT', re.compile(r'(sex|fuck|job|fellatio|blowjob|paizuri|masturb|penetrat|insert|orgasm|ejaculat|cum|threesome|foursome|frott|grope|groping|fondl|licking|suck|rape|prostitut)')),
    ('SEX_DEVICE', re.compile(r'(vibrator|dildo|condom|masturbator|tenga|sex_toy|sybian|onahole|plug)')),
    ('GENITAL', re.compile(r'(penis|dick|cock|pussy|vulva|vagina|clitoris|anus|anal|rectum|testicle|scrot|nipple|areola|breast|boob)')),
    ('REPRO', re.compile(r'(pregnan|birth|fertil|impreg|lactat|breast_milk|inseminat|uterus|cervix|ovum|egg_laying)')),
    ('RESTRAINT_BDSM', re.compile(r'(bondage|bdsm|gag|blindfold|handcuff|cuff|leash|shackle|restraint|rope|spank|whip|crop|sadism|masoch)')),
    ('EXPOSURE_CLOTHING', re.compile(r'(naked|nude|topless|bottomless|panties|underwear|bra|bikini|swimsuit|open_|cutout|aside|unbutton|unzipp|see_through|transparent|exposure)')),
    ('FLUID_EXCRETION', re.compile(r'(saliva|drool|urine|pee|peeing|piss|sweat|fluid|milk|semen|blood|vomit)')),
    ('INJURY_GORE', re.compile(r'(wound|injur|gore|blood|corpse|amput|castrat|torture|stomp|kick|punch|crush)')),
    ('BODY_APPEARANCE', re.compile(r'(large|small|huge|gigantic|dark|light|colored|hair|freckle|mole|scar|size|growth|flat|veiny|puffy|inverted)')),
    ('RELATION_ROLE', re.compile(r'(incest|yuri|yaoi|futa|shota|loli|onee|relation|couple|polyamory|harem)')),
]


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(v: str) -> str:
    return '_'.join(v.strip().lower().replace('_',' ').split())


def root(row):
    p=(row or {}).get('primary_path','').strip()
    return p.split('/',1)[0] if p else '(none)'


def bucket(key: str) -> str:
    for name, rx in BUCKETS:
        if rx.search(key): return name
    return 'OTHER'


def main() -> int:
    g={norm(r['canonical']):r for r in read_csv(GENERAL)}
    s={norm(r['Tag']):r for r in read_csv(SPECIAL)}
    queue=[]
    for p in sorted(QUEUE.glob('chunk_*.csv')): queue.extend(read_csv(p))
    if len(queue)!=1000: raise SystemExit(f'expected 1000, got {len(queue)}')

    groups=defaultdict(list)
    for r in queue:
        key=norm(r['identity_key']); gr=g.get(key); sr=s.get(key)
        fam=(sr or {}).get('GenerationFamily','').strip() or '(none)'
        rt=root(gr)
        b=bucket(key)
        membership='OVERLAP' if gr and sr else 'SPECIAL_ONLY' if sr else 'GENERAL_ONLY'
        # Keep P0 unresolved separate; otherwise cluster on semantic bucket + structural evidence.
        pri=r.get('priority_band','')
        cluster_key=(pri if pri.startswith('P0_') else 'P1+', membership, b, fam, rt)
        groups[cluster_key].append(r)

    cluster_rows=[]; reps=[]
    for idx,(ck,rows) in enumerate(sorted(groups.items(),key=lambda kv:(-len(kv[1]),kv[0])),1):
        pri,membership,b,fam,rt=ck
        rows=sorted(rows,key=lambda r:r['identity_key'])
        cid=f'C{idx:03d}'
        cluster_rows.append({
            'cluster_id':cid,'rows':str(len(rows)),'priority_scope':pri,'membership':membership,
            'semantic_bucket':b,'generation_family':fam,'general_root':rt,
            'representatives':';'.join(r['identity_key'] for r in rows[:3]),
        })
        # 1 rep for singleton, 2 for 2-4, 3 for >=5. Large clusters also take one tail example.
        take=1 if len(rows)==1 else 2 if len(rows)<=4 else 3
        selected=rows[:take]
        if len(rows)>=20:
            selected=selected+[rows[-1]]
        seen=set()
        for r in selected:
            if r['identity_key'] in seen: continue
            seen.add(r['identity_key'])
            reps.append({
                'cluster_id':cid,'cluster_rows':str(len(rows)),'semantic_bucket':b,
                'generation_family':fam,'general_root':rt,**r,
                'reviewed_class':'','review_status':'','review_note':''
            })

    OUT.mkdir(parents=True,exist_ok=True)
    def write(path, rows):
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n'); w.writeheader(); w.writerows(rows)
    write(OUT/'clusters_v1.csv',cluster_rows)
    write(OUT/'representative_review_v1.csv',reps)

    sizes=Counter()
    for r in cluster_rows:
        n=int(r['rows'])
        sizes['20+'] += n>=20
        sizes['10-19'] += 10<=n<20
        sizes['5-9'] += 5<=n<10
        sizes['2-4'] += 2<=n<5
        sizes['1'] += n==1
    summary={
        'issue':118,'mode':'SEMANTIC_QUEUE_CLUSTERING_V1','queue_rows':1000,
        'clusters':len(cluster_rows),'representative_review_rows':len(reps),
        'compression_ratio':round(len(reps)/1000,4),
        'cluster_size_bands':dict(sizes),
        'largest_clusters':cluster_rows[:15],
        'production_promotion_performed':'NO',
    }
    (OUT/'summary_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
