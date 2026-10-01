"""Reproduce display-only groups from frozen HOME and reviewed exact rosters.

No network, co-occurrence, fuzzy name mapping, or production writes.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import tarfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/issue223'
HOME = 'docs/issue216/BROWSE_HOME_RUNTIME_V1.csv'
OVERLAY = 'docs/issue70/data/runtime/issue70_catalog_overlay_2d_final.csv'
SNAPSHOT = 'docs/issue216/DANBOORU_RETAINED_CURATED_REVIEW_INPUTS_2026-10-01.tar.gz'

# Work-scoped reviewed rosters only. Returning/guest/event-only rosters excluded.
ROSTERS = {
 'fate_(series)': {
  'fate/stay_night': ('Fate/stay night', ['BATCH_FATE_STAY_NIGHT_REALTA_NUA_DIRECTORY', 'BATCH_FATE_STAY_NIGHT_HF3_EXACT_CHARACTER']),
  'fate/zero': ('Fate/Zero', ['BATCH_FATE_ZERO_DIRECTORY']),
  'fate/extra': ('Fate/EXTRA', ['BATCH_FATE_EXTRA_LAST_ENCORE_DIRECTORY']),
  'fate/apocrypha': ('Fate/Apocrypha', ['BATCH_FATE_APOCRYPHA_DIRECTORY', 'BATCH_FATE_APOCRYPHA_JEANNE_EXACT_CONTEXTUAL_IDENTITY']),
  'fate/strange_fake': ('Fate/strange Fake', ['BATCH_FATE_STRANGE_FAKE_DIRECTORY']),
  'fate/grand_order': ('Fate/Grand Order', ['BATCH_FGO_BENI_ENMA_OFFICIAL_SERVANT_TIMELINE']),
 },
 'gundam': {
  'gundam_seed': ('ガンダムSEED / SEED DESTINY', ['BATCH_GUNDAM_SEED_OFFICIAL_CHARACTER_DIRECTORY', 'BATCH_GUNDAM_SEED_DESTINY_DIRECTORY', 'BATCH_GUNDAM_SEED_AISHA_EXACT_CONTEXTUAL_IDENTITY']),
  'gundam_00': ('ガンダム00', ['gundam_00_curated_roster']),
  'gundam_suisei_no_majo': ('ガンダム 水星の魔女', ['BATCH_GUNDAM_WITCH_FROM_MERCURY_MAIN_CAST']),
  'mobile_suit_gundam': ('機動戦士ガンダム', ['mobile_suit_gundam_curated_roster']),
  'g_gundam': ('機動武闘伝Gガンダム', ['g_gundam_curated_character_profiles']),
  'gundam_build_fighters': ('ガンダムビルドファイターズ', ['gundam_build_fighters_first_party_roster']),
  'gundam_08th_ms_team': ('ガンダム 第08MS小隊', ['BATCH_GUNDAM_08TH_MS_TEAM_EXACT_ROSTER']),
  'gundam_gquuuuuux': ('ガンダムGQuuuuuuX', ['BATCH_GUNDAM_GQUUUUUUX_MECHA_EXACT_NEW_UNITS']),
 },
 'final_fantasy': {
  'final_fantasy_vii': ('FINAL FANTASY VII', []),
  'final_fantasy_viii': ('FINAL FANTASY VIII', ['BATCH_FINAL_FANTASY_VIII_CHARACTER_PAGE']),
  'final_fantasy_ix': ('FINAL FANTASY IX', ['final_fantasy_ix_roster']),
  'final_fantasy_xiii': ('FINAL FANTASY XIII', ['BATCH_FINAL_FANTASY_XIII_PORTAL']),
  'final_fantasy_xiv': ('FINAL FANTASY XIV', ['BATCH_FINAL_FANTASY_XIV_ENDWALKER']),
  'final_fantasy_xvi': ('FINAL FANTASY XVI', ['BATCH_FINAL_FANTASY_XVI_DIRECTORY']),
 },
 'precure': {},
 'fire_emblem': {},
}


def read(relative):
    return list(csv.DictReader((ROOT / relative).open(encoding='utf-8-sig', newline='')))


def csv_bytes(fields, rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def build():
    inputs = {HOME, OVERLAY}
    population = read(OVERLAY)
    characters = {r['canonical_tag']: r for r in population if r['category_name'] == 'Character'}
    roots = {r['canonical_tag']: r for r in population if r['category_name'] == 'Copyright'}
    home_rows = read(HOME)
    homes = {r['character']: r['formal_home'] or r['reviewed_home'] for r in home_rows}
    census = Counter(homes.values())
    assert len(characters) == 35278 and len(roots) == 7616
    assert Counter('FORMAL_HOME' if r['formal_home'] else 'REVIEWED_BROWSE_FALLBACK' for r in home_rows) == {'FORMAL_HOME': 25533, 'REVIEWED_BROWSE_FALLBACK': 7409}
    definitions = {h: dict(groups) for h, groups in ROSTERS.items()}
    # Exact canonical work qualifiers; broad franchise/variant qualifiers excluded.
    for title in roots:
        home = ('fire_emblem' if title.startswith('fire_emblem') and title != 'fire_emblem'
                else 'precure' if 'precure' in title and title != 'precure' else None)
        if home:
            definitions[home][title] = (roots[title]['display_ja'], [])
    candidates = defaultdict(lambda: defaultdict(list))

    def offer(character, home, group, kind, ref):
        if homes.get(character) == home:
            candidates[character][(home, group)].append((kind, ref))

    for character, home in homes.items():
        for qualifier in re.findall(r'\(([^()]*)\)', character):
            if qualifier in definitions.get(home, {}):
                offer(character, home, qualifier, 'EXACT_WORK_QUALIFIER', OVERLAY + '#' + character)

    files = sorted((ROOT / 'docs/issue180/evidence').glob('*.csv')) + sorted((ROOT / 'docs/issue216').glob('BATCH*.csv'))
    for path in files:
        explicit = [(h, g) for h, gs in definitions.items() for g, (_, prefixes) in gs.items() if any(path.name.startswith(p + '_') for p in prefixes)]
        generic = path.name in {'final_fantasy_work_roster_v1.csv', 'precure_first_party_series_rosters_v1.csv', 'precure_residual_first_party_rosters_v1.csv'}
        if not explicit and not generic:
            continue
        relative = path.relative_to(ROOT).as_posix()
        inputs.add(relative)
        for row in read(relative):
            character = row.get('canonical_character', row.get('canonical_tag', ''))
            for h, g in explicit:
                offer(character, h, g, 'REVIEWED_EXACT_ROSTER', relative + '#' + character)
            if generic:
                g = row['home_copyright']
                for h, gs in definitions.items():
                    if g in gs:
                        offer(character, h, g, 'REVIEWED_EXACT_ROSTER', relative + '#' + character)

    # Reviewed section contract: literal canonical links in roster list/table
    # rows, never prose, See also, staff, collaboration, guest or event sections.
    # These snapshots were retained by #216; no wiki downloads at build/startup.
    inputs.add(SNAPSHOT)
    pages = {}
    with tarfile.open(ROOT / SNAPSHOT) as archive:
        for member in archive:
            if member.name.endswith('.json') and 'manifest' not in member.name:
                page = json.load(archive.extractfile(member))
                pages[page['title']] = page
    normalize = lambda s: s.strip().lower().replace(' ', '_')
    section_rules = {
        'list_of_fate_series_characters': ('fate_(series)', 4, {
            'fsn': 'fate/stay_night', 'fha': 'fate/hollow_ataraxia', 'zero': 'fate/zero',
            'extra': 'fate/extra', 'strange-fake': 'fate/strange_fake', 'prototype': 'fate/prototype',
            'apocrypha': 'fate/apocrypha', 'fgo': 'fate/grand_order',
            'requiem': 'fate/requiem', 'samurai-remnant': 'fate/samurai_remnant'}),
        'list_of_fire_emblem_characters': ('fire_emblem', 4, {}),
        'list_of_final_fantasy_characters': ('final_fantasy', 6, {
            'ff'+str(i): 'final_fantasy_'+roman for i, roman in enumerate(
                ['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii','xiii','xiv','xv','xvi'], 1)}),
        'list_of_jojo_no_kimyou_na_bouken_characters': ('jojo_no_kimyou_na_bouken', 4, {}),
        'list_of_project_moon_characters': ('project_moon', 3, {}),
    }
    for page_name, (home, level, anchors) in section_rules.items():
        page = pages[page_name]
        definitions.setdefault(home, {})
        group = None
        blocked = False
        for line in page['body'].replace('\\r\\n', '\n').splitlines():
            heading = re.match(r'h([1-6])(?:#([^.]+))?\.\s*(.*)', line)
            if heading:
                depth, anchor, label = heading.groups()
                depth = int(depth)
                if depth <= level:
                    group = anchors.get(anchor)
                    if not anchors:
                        links = re.findall(r'\[\[([^]|]+)', label)
                        if len(links) == 1:
                            title = normalize(links[0])
                            if title in roots and (home != 'fire_emblem' or title.startswith('fire_emblem')):
                                group = title
                    if group not in roots:
                        group = None
                    if group:
                        definitions[home].setdefault(group, (roots[group]['display_ja'], []))
                blocked = bool(re.search(r'collaboration|crossover|guest|event|See also|External links', label, re.I))
            if not group or blocked or not re.match(r'\s*(?:\*+|\|)', line):
                continue
            for link in re.findall(r'\[\[([^]|]+)', line):
                character = normalize(link)
                if character in characters:
                    offer(character, home, group, 'REVIEWED_CACHED_ROSTER_SECTION',
                          SNAPSHOT + '#' + page_name + '/' + group + '/' + character)

    # Additional research is frozen separately; reproduction is offline.
    uc_titles = {'mobile_suit_gundam', 'zeta_gundam', 'gundam_zz', 'gundam_0080', 'gundam_0083', 'gundam_unicorn'}
    definitions['gundam']['uc'] = ('宇宙世紀（UC）', [])
    for path in sorted((OUT/'snapshots').glob('*.json')):
        relative = path.relative_to(ROOT).as_posix()
        inputs.add(relative)
        page = json.loads(path.read_text(encoding='utf-8'))
        group = None
        active = False
        for line in page['body'].splitlines():
            heading = re.match(r'h([1-6])\.\s*(.*)', line)
            if heading:
                depth, label = heading.groups()
                if page['title'] == 'list_of_pokemon':
                    match = re.fullmatch(r'Generation (I|II|III|IV|V|VI|VII|VIII|IX)', label.strip())
                    if depth == '5':
                        group = 'generation_' + str(['I','II','III','IV','V','VI','VII','VIII','IX'].index(match[1])+1) if match else None
                        if group:
                            definitions.setdefault('pokemon', {})[group] = ('ポケモン種族・第'+group[-1]+'世代', [])
                    # Only numbered base species rows; regional/mega/named individuals unclassified.
                    active = depth == '5' and group is not None
                elif depth == '4':
                    active = bool(re.fullmatch(r'Characters|Mecha|Mobile Suits|\[\[Mobile Suit\]\]s|Related characters|Related mecha', label.strip(), re.I))
                    group = 'uc' if page['title'] in uc_titles else page['title']
            if not active or group is None:
                continue
            if page['title'] == 'list_of_pokemon':
                if not re.match(r'^\* \d{4}\. ', line):
                    continue
                home = 'pokemon'
            else:
                if not re.match(r'^\*+', line):
                    continue
                home = 'gundam'
            for link in re.findall(r'\[\[([^]|]+)', line):
                character = normalize(link)
                if character in characters:
                    offer(character, home, group, 'REVIEWED_FROZEN_ROSTER_SECTION', relative+'#'+character)

    # UC work rosters join one local display group, never modify HOME.
    for c, gs in list(candidates.items()):
        for key in list(gs):
            if key[0] == 'gundam' and key[1] in uc_titles:
                candidates[c][('gundam', 'uc')].extend(gs.pop(key))

    # Only uniquely evidenced exact identities; no automatic costume inheritance.
    unique = {c: next(iter(gs)) for c, gs in candidates.items() if len(gs) == 1}
    counts = Counter(unique.values())
    useful = {key for key, count in counts.items() if count >= 3}
    selected = {h for h, n in census.items() if n >= 100
                and sum(1 for hh, _ in useful if hh == h) >= 2
                and sum(n for (hh, g), n in counts.items() if hh == h and (hh, g) in useful) >= 20}
    groups = []
    visible = {key for key, count in counts.items() if count > 0 and key[0] in selected}
    for h in sorted(selected):
        for order, g in enumerate(sorted(g for hh, g in visible if hh == h), 1):
            assert h in roots, (h, g)
            groups.append(dict(home_copyright=h, group_id=g, group_label_ja=definitions[h][g][0], sort_order=order))
    members = []
    for c, (h, g) in sorted(unique.items()):
        if (h, g) not in visible:
            continue
        kind, ref = sorted(candidates[c][(h, g)])[0]
        members.append(dict(home_copyright=h, group_id=g, character_canonical=c, evidence_kind=kind, evidence_ref=ref, review_status='REVIEWED'))
    grouped = {m['character_canonical'] for m in members}
    holds = [dict(home_copyright=homes[c], character_canonical=c, candidate_groups=' | '.join(sorted(g for h, g in gs)), reason='COMPETING_WORK_EVIDENCE')
             for c, gs in sorted(candidates.items()) if len(gs) > 1]
    ranking = [dict(rank=i, home_copyright=h, label_ja=roots[h]['display_ja'], character_count=n,
                    selected=str(h in selected).lower(), grouped=sum(m['home_copyright'] == h for m in members),
                    unclassified=n-sum(m['home_copyright'] == h for m in members))
               for i, (h, n) in enumerate(sorted(((h, census[h]) for h in roots), key=lambda p: (-p[1], p[0])), 1)]
    outputs = {
        'HOME_CENSUS_V1.csv': csv_bytes(list(ranking[0]), ranking),
        'BROWSE_GROUPS_V1.csv': csv_bytes(['home_copyright', 'group_id', 'group_label_ja', 'sort_order'], groups),
        'BROWSE_GROUP_MEMBERS_V1.csv': csv_bytes(['home_copyright', 'group_id', 'character_canonical', 'evidence_kind', 'evidence_ref', 'review_status'], members),
        'HOLD_V1.csv': csv_bytes(['home_copyright', 'character_canonical', 'candidate_groups', 'reason'], holds),
    }
    manifest = dict(schema='issue223-browse-groups-v1', baseline_main='84a4ac467cc534d44f322d02989f23d12933974f',
                    selection='HOME >=100; >=2 evidence groups of >=3 exact members; >=20 grouped; conservative work rosters only',
                    character_count=len(characters), copyright_count=len(roots), formal=25533, fallback=7409, unresolved=2336,
                    home_count=len(census), selected_home_count=len(selected), group_count=len(groups), grouped_characters=len(grouped),
                    selected_home_unclassified=sum(census[h] for h in selected)-len(grouped), hold_count=len(holds),
                    inputs={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(inputs)},
                    assets={n: hashlib.sha256(b).hexdigest() for n,b in outputs.items()})
    outputs['MANIFEST_V1.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode()
    return outputs, manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs, manifest = build()
    if args.check:
        for name, content in outputs.items():
            assert (OUT/name).read_bytes() == content, name
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (OUT/name).write_bytes(content)
    print(json.dumps({k:v for k,v in manifest.items() if k not in {'inputs','assets'}}, ensure_ascii=False))
