#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

GENERAL = Path('docs/issue64/production_candidate/effective_sidecar.csv')
SPECIAL = Path('data/generation/special2788_generation_profile.csv')
SIDECAR = Path('docs/issue118/research_sidecar_v17.csv')
OUT = Path('docs/issue118/remaining_cluster_inventory_v29')

LEX_GROUPS = {
    'EXPLICIT_SEX': {'sex','handjob','blowjob','fellatio','paizuri','irrumatio','cum','cumshot','ejaculation','orgasm','masturbation','vibrator','dildo','buttjob','threesome','penetration','prostitution','zoophilia','rape','cunnilingus','anilingus','fingering','footjob','creampie','bukkake','fleshlight','onahole','fuck','fucking'},
    'ANATOMY': {'penis','pussy','vagina','vulva','anus','anal','clitoris','testicle','testicles','scrotum','nipple','nipples','breast','breasts','areola','areolae','pubic','crotch','genital'},
    'RESTRAINT_FETISH': {'gag','gagged','handcuff','handcuffs','leash','rope','shackle','restraint','restraints','bondage','blindfold','clamp','clamps','collar','fetish','bdsm','spanking','whip'},
    'REPRO': {'pregnant','pregnancy','lactation','breastfeeding','birth','insemination','fertilization','fertilisation','impregnation'},
    'INJURY': {'blood','wound','gore','amputee','amputation','castration','corpse','injury','snuff'},
    'EXPOSURE_INTIMATE': {'nude','naked','topless','bottomless','panty','panties','underwear','bra','cleavage','underboob','upskirt','downblouse','lingerie','crotchless','pasties','maebari'},
    'ADULT_ROLE_DEVICE': {'condom','condoms','porn','pornstar','stripper','prostitute','courtesan','oiran','speculum','bodystocking','bustier','gravure'},
    'RELATIONSHIP_ROLE': {'brocon','siscon','lolicon','shotacon','incest','virgin','virginity','seme','uke','femdom','maledom','ageplay','cuckold','cuckquean','netorare','netori','ntr'},
    'SEXUALIZED_CLOTHING': {'bikini','swimsuit','swimwear','thong','garter','garters','gstring','fishnet','fishnets','corset','harness','latex','leotard','bodysuit','bunnysuit','playboy','fetishwear','bodycon','slingshot','highleg','lowleg','sheer','transparent','frontless','backless','assless','sideless','tankini','monokini','trikini','microdress','dongtan'},
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def norm(value: str) -> str:
    return '_'.join(value.strip().lower().replace('_', ' ').split())


def root(path: str) -> str:
    path = (path or '').strip()
    return path.split('/', 1)[0] if path else '(none)'


def flags(key: str) -> str:
    k = key.lower()
    parts = {p for p in re.split(r'[_()\-/]+', k) if p}
    hit = {name for name, terms in LEX_GROUPS.items() if parts & terms}
    if re.search(r'(?:^|[_/\-])g[_\-]string(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])see[_\-]through(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])t[_\-]back(?:$|[_/\-])', k) or re.search(r'(?:^|[_/\-])micro(?:dress|skirt|shorts|pants|top|shirt)(?:$|[_/\-])', k):
        hit.add('SEXUALIZED_CLOTHING')
    if re.search(r'(?:^|[_/\-])(?:top[/_-]bottom|bottom[/_-]top)[_/-]dynamic(?:$|[_/\-])', k):
        hit.add('RELATIONSHIP_ROLE')
    return '+'.join(sorted(hit)) if hit else 'NONE'


def main() -> int:
    general = read_csv(GENERAL)
    special = read_csv(SPECIAL)
    side = read_csv(SIDECAR)
    g = {norm(r['canonical']): r for r in general}
    s = {norm(r['Tag']): r for r in special}

    clusters: dict[str, list[dict[str, str]]] = defaultdict(list)
    membership_counts = Counter(); root_counts = Counter(); path_counts = Counter(); family_counts = Counter(); lex_counts = Counter(); rows = []

    for r in side:
        if r['review_status'] != 'UNCLASSIFIED':
            continue
        key = r['identity_key']; gr = g.get(key); sr = s.get(key)
        if gr is not None and r['is_special'] == 'YES': membership = 'OVERLAP'
        elif gr is not None: membership = 'GENERAL_ONLY'
        else: membership = 'SPECIAL_ONLY'
        path = ((gr or {}).get('primary_path') or '').strip() or '(none)'
        rt = root(path if path != '(none)' else '')
        fam = ((sr or {}).get('GenerationFamily') or '').strip() or '(none)'
        role = ((sr or {}).get('GenerationRole') or '').strip() or '(none)'
        fl = flags(key)
        cluster_key = '|'.join([membership, path, fl]) if membership == 'GENERAL_ONLY' else '|'.join([membership, rt, fam, fl])
        item = {'identity_key': key,'membership': membership,'general_path': path,'general_root': rt,'generation_family': fam,'generation_role': role,'lex_flags': fl,'cluster_key': cluster_key}
        rows.append(item); clusters[cluster_key].append(item); membership_counts[membership] += 1; root_counts[rt] += 1; path_counts[path] += 1; family_counts[fam] += 1; lex_counts[fl] += 1

    if len(rows) != 7298:
        raise SystemExit(f'expected 7298 remaining UNCLASSIFIED rows, got {len(rows)}')

    inventory = []
    for ck, items in clusters.items():
        a = items[0]
        inventory.append({'cluster_key': ck,'rows': len(items),'membership': a['membership'],'general_path': a['general_path'],'general_root': a['general_root'],'generation_family': a['generation_family'],'lex_flags': a['lex_flags'],'examples': ';'.join(x['identity_key'] for x in sorted(items, key=lambda x: x['identity_key'])[:12])})
    inventory.sort(key=lambda x: (-int(x['rows']), x['cluster_key']))

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ['cluster_key','rows','membership','general_path','general_root','generation_family','lex_flags','examples']
    with (OUT / 'cluster_inventory_v29.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(inventory)

    summary = {'issue':118,'mode':'REMAINING_CLUSTER_INVENTORY_V29_FROM_SIDECAR_V17','source_sidecar':'research_sidecar_v17.csv','remaining_unclassified_rows':len(rows),'membership_counts':dict(sorted(membership_counts.items())),'cluster_count':len(inventory),'clusters_ge_20':sum(1 for x in inventory if int(x['rows']) >= 20),'clusters_ge_100':sum(1 for x in inventory if int(x['rows']) >= 100),'top10_cluster_rows':sum(int(x['rows']) for x in inventory[:10]),'top20_cluster_rows':sum(int(x['rows']) for x in inventory[:20]),'top30_cluster_rows':sum(int(x['rows']) for x in inventory[:30]),'top_general_roots':root_counts.most_common(20),'top_general_paths':path_counts.most_common(30),'top_generation_families':family_counts.most_common(20),'lex_flag_counts':dict(sorted(lex_counts.items())),'top_clusters':inventory[:40],'production_authority':'NO','main_mutated':'NO','issue117_code_mutated':'NO','catalog_mutated':'NO','user_db_mutated':'NO'}
    (OUT / 'summary_v29.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'remaining_unclassified_rows':len(rows),'membership_counts':dict(sorted(membership_counts.items())),'cluster_count':len(inventory),'top20_cluster_rows':summary['top20_cluster_rows']}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
