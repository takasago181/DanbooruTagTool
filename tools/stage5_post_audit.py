"""Read-only audit; writes only benchmarks/stage5_post_audit artifacts."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import random
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.normalization import normalize_lookup
from danbooru_tag_tool.runtime_index import RuntimeIndex
from tools.benchmark_runtime_index import rss_bytes

OUT = ROOT / 'benchmarks/stage5_post_audit'

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def table(name, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

def fingerprints():
    paths = list((ROOT / 'data/runtime_index').iterdir()) + list((ROOT / 'danbooru_tag_tool').glob('*.py'))
    paths += list((ROOT / 'data/source').iterdir()) + list((ROOT / 'data/special2788').iterdir())
    paths += [ROOT / 'data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv']
    result = {}
    for p in paths:
        if p.is_file():
            with p.open('rb') as f:
                result[str(p.relative_to(ROOT))] = hashlib.file_digest(f, 'sha256').hexdigest()
    return result

def mapping():
    before = fingerprints(); save('input_hashes_before.json', before)
    k = TagKnowledgeCore.load(ROOT); x = RuntimeIndex(ROOT / 'data/runtime_index')
    rows = []; groups = defaultdict(list)
    # Original verified keys distinguish pre-existing ambiguity from ambiguity
    # introduced by normalization merging multiple keys.
    verified = defaultdict(list)
    with (ROOT / 'data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv').open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            verified[normalize_lookup(row['NormalizedAlias'])].append(row)
    for i, tag in enumerate(x.tags):
        r = k.resolve_exact(tag); targets = r.canonical_candidates; target = ''
        if tag in k.canonical:
            target = tag; category = '1_exact_general' if k.canonical[tag].category == 0 else '7_exact_non_general'
        elif r.match_type == 'canonical':
            category = '5_normalization'; target = targets[0] if len(targets) == 1 else ''
        elif r.match_type == 'alias':
            if len(targets) == 1:
                target = targets[0]; category = '2_alias_general' if k.canonical[target].category == 0 else '3_alias_non_general'
            else:
                originals = verified[normalize_lookup(tag)]
                category = '4_ambiguous_alias' if any(int(v['TargetCount']) > 1 for v in originals) else '5_normalization'
        else:
            category = '6_runtime_only'
        if target: groups[target].append(tag)
        rows.append(dict(source_tag=tag, classification=category, target=target, candidates=json.dumps(targets),
                         resolution_type=r.match_type, runtime_global_count=int(x.runtime_global_counts[i])))
    table('all_source_tags.csv', rows)
    summary = {}
    total = int(x.runtime_global_counts.sum())
    assert total == 354571220 and len(rows) == 103198
    for category in ['1_exact_general','2_alias_general','3_alias_non_general','4_ambiguous_alias','5_normalization','6_runtime_only','7_exact_non_general']:
        subset = [r for r in rows if r['classification'] == category]
        mask = np.zeros(x.total_posts, dtype=bool)
        for r in subset: mask[x.postings(r['source_tag'])] = True
        occurrences = sum(r['runtime_global_count'] for r in subset)
        summary[category] = dict(unique_tags=len(subset), occurrences=occurrences, entry_percent=100*occurrences/total,
                                 posts=int(mask.sum()), top50=sorted(subset,key=lambda r:(-r['runtime_global_count'],r['source_tag']))[:50])
    duplicate_posts = np.zeros(x.total_posts, dtype=bool); impacts = []; merged = {}
    for target, sources in groups.items():
        raw = int(x.runtime_global_counts[x.tag_id(target)]) if target in x.tag_to_id else 0
        summed = sum(int(x.runtime_global_counts[x.tag_id(t)]) for t in sources)
        if len(sources) > 1:
            ids, counts = np.unique(np.concatenate([x.postings(t) for t in sources]), return_counts=True)
            dup = ids[counts > 1]; duplicate_posts[dup] = True
            union = len(ids)
            impacts.append(dict(canonical=target, category=k.canonical[target].category, source_tags=json.dumps(sources),
                                source_tag_count=len(sources), raw_canonical_count=raw, summed_source_counts=summed,
                                union_global_count=union, duplicate_posts=len(dup), duplicate_entries=summed-union,
                                added_posts=union-raw, example_post_ids=json.dumps(x.post_ids[dup[:10]].tolist())))
        else: union = summed
        merged[target] = union
    table('canonical_merges.csv', impacts)
    special = []
    for s in k.special.values():
        t = s.chosen_canonical
        if not t: continue
        raw = int(x.runtime_global_counts[x.tag_id(t)]) if t in x.tag_to_id else 0
        special.append(dict(special_id=s.special_id, term=s.term, japanese=s.japanese, canonical=t,
                            category=k.canonical[t].category, raw_global_count=raw, merged_global_count=merged.get(t,0),
                            added_posts=merged.get(t,0)-raw, source_tags=json.dumps(groups.get(t,[]))))
    table('special_impact.csv',special)
    save('mapping_summary.json',dict(total_tags=len(rows), total_entries=total, total_posts=x.total_posts, categories=summary,
         merge_groups=len(impacts), merge_source_tags=sum(r['source_tag_count'] for r in impacts),
         groups_with_same_post_duplicates=sum(r['duplicate_posts']>0 for r in impacts),
         posts_with_any_canonical_duplicate=int(duplicate_posts.sum()), duplicate_entries=sum(r['duplicate_entries'] for r in impacts),
         special_resolved_entries=len(special), special_unique_canonicals=len({r['canonical'] for r in special}),
         special_changed_entries=sum(r['added_posts']!=0 for r in special),
         special_changed_canonicals=len({r['canonical'] for r in special if r['added_posts']}),
         special_raw_missing=sum(r['raw_global_count']==0 for r in special),
         special_recovered=sum(r['raw_global_count']==0 and r['merged_global_count']>0 for r in special)))
    # Real Special provenance, one representative Special ID per canonical.
    eligible = {r['canonical']:r for r in special if r['category']==0 and r['raw_global_count']>0}
    cases = []
    for target in [1,100,10000,100001,500001,1000001]:
        options = [t for t in eligible if eligible[t]['raw_global_count']>=target] if target>100000 else list(eligible)
        if options:
            t=min(options,key=lambda t:(abs(eligible[t]['raw_global_count']-target),t))
            cases.append(dict(name=f'single_{target}',tags=[t],specials=[eligible[t]]))
    rng=random.Random(20260905)
    pool=sorted(eligible,key=lambda t:(-eligible[t]['raw_global_count'],t))[:100]
    for n in [2,3,5]:
        candidates=[]
        for _ in range(60):
            tags=sorted(rng.sample(pool,n)); base=x.intersect(tags).base_count
            candidates.append((base,tags))
        for target in [100,10000]:
            base,tags=min(candidates,key=lambda item:(abs(item[0]-target),item[1]))
            cases.append(dict(name=f'{n}_special_target_{target}',tags=tags,specials=[eligible[t] for t in tags]))
    save('workload_plan.json',cases)
    after=fingerprints(); save('input_hashes_after_mapping.json',after); assert before==after
    print(json.dumps({c:(v['unique_tags'],v['occurrences']) for c,v in summary.items()}),flush=True)

def measure(case_number):
    case=json.loads((OUT/'workload_plan.json').read_text(encoding='utf-8'))[case_number]
    x=RuntimeIndex(ROOT/'data/runtime_index'); case['open_rss_bytes']=rss_bytes()
    tags=case['tags']; base=x.intersect(tags); case['base_count']=base.base_count
    # One warm-up; 5 observations for expensive queries, 15 otherwise.
    x.aggregate(base,exclude=tags)
    repeats=5 if base.base_count>100000 else 15
    def timed(fn,n):
        samples=[]
        for _ in range(n):
            start=time.perf_counter(); result=fn(); elapsed=(time.perf_counter()-start)*1000
            samples.append(elapsed); del result
        return dict(samples_ms=samples,median_ms=float(np.median(samples)),p95_ms=float(np.percentile(samples,95)),repeats=n)
    case['and']=timed(lambda:x.intersect(tags),max(15,repeats))
    case['aggregation']=timed(lambda:x.aggregate(base,exclude=tags),repeats)
    case['rss_after_aggregation_bytes']=rss_bytes()
    case['total']=timed(lambda:x.aggregate(x.intersect(tags),exclude=tags),repeats)
    case['rss_after_total_bytes']=rss_bytes()
    save(f'workload_{case_number:02d}.json',case)
    print(case['name'],case['tags'],case['base_count'],case['aggregation']['median_ms'],flush=True)

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    parser=argparse.ArgumentParser(); parser.add_argument('mode'); parser.add_argument('--case',type=int); args=parser.parse_args()
    if args.mode=='mapping': mapping()
    elif args.mode=='measure': measure(args.case)
    elif args.mode=='workloads':
        for i in range(len(json.loads((OUT/'workload_plan.json').read_text(encoding='utf-8')))):
            subprocess.run([sys.executable,__file__,'measure','--case',str(i)],check=True)
        after=fingerprints(); save('input_hashes_final.json',after)
        assert after==json.loads((OUT/'input_hashes_before.json').read_text(encoding='utf-8'))
