#!/usr/bin/env python3
"""Bounded human pattern review of Browse overlay; never writes formal authority."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'docs/issue216'
BASE = '2c23f513bab43d04f87a020daf39ef8a79b251bc'

# Human light-review judgments of recognizable subjects, retained wiki context,
# origin versus guest roles, and brand choices. These are Browse preferences.
CHOICES = {
    'yorick_(shiori_novella)': 'hololive',
    'phosphophyllite_(ll)': 'houseki_no_kuni',
    'touhoku_itako': 'voiceroid', 'jessica_albert': 'dragon_quest',
    'yuri_sakazaki': 'ryuuko_no_ken', 'xp-tan': 'os-tan',
    '95-tan': 'os-tan', '98-tan': 'os-tan', 'haman_karn': 'gundam',
    'koharu_rikka': 'cevio', 'kafu_(cevio)': 'cevio', 'sekai_(cevio)': 'cevio',
    'natsuki_karin': 'cevio', 'hanakuma_chifuyu': 'cevio',
    'symphony_miku': 'vocaloid', 'gramophone_miku': 'vocaloid',
    'bokukawauso': 'kantai_collection', 'kson': 'vshojo',
    'silvervale': 'vshojo', 'vei_(vtuber)': 'vshojo', 'henya_the_genius': 'vshojo',
    "riliane_lucifen_d'autriche": 'evillious_nendaiki',
    'allen_avadonia': 'evillious_nendaiki', 'sion_eltnam_atlasia': 'tsukihime',
    'amaterasu_(ookami)': 'ookami_(game)', 'noelle_holiday_(dark_world)': 'deltarune',
    'ribbon_(kirby)': 'kirby_(series)', 'void_shiki': 'kara_no_kyoukai',
    'blaidd_the_half-wolf': 'elden_ring', 'quattro_bajeena': 'gundam',
    'tenma_maemi': 'phase_connect', 'pauline_(nintendo)': 'mario_(series)',
    'snuffy_(vtuber)': '3am', 'sasori_(naruto)': 'naruto_(series)',
    'kagura_mea': 'paryi_project', 'mutsu-no-kami_yoshiyuki': 'touken_ranbu',
    'evangeline_a.k._mcdowell': 'mahou_sensei_negima!',
    'cheese-kun': 'pizza_hut', 'aozaki_touko': 'kara_no_kyoukai',
    'kaneko_lumi': 'phase_connect', 'banken_(inui_toko)': 'nijisanji',
    'gm_(mobile_suit)': 'gundam', 'chain_chomp': 'mario_(series)',
    'symphony_meiko': 'vocaloid', 'symphony_kaito': 'vocaloid',
}
# Exact named-base families reviewed together. No generic name-shape inheritance.
# Agency-only associations and indie avatars are intentionally not in this set.
FAMILIES = set('''miyu_edelfelt chloe_von_einzbern utsumi_erice momoe_nagisa
sessyoin_kiara raising_heart bardiche_(nanoha) emiya_kiritsugu
purple_heart_(neptunia) black_heart_(neptunia) blanc_(neptunia) vert_(neptunia)
noire_(neptunia) yae_sakura seele_vollerei murata_himeko kallen_kaslana
rita_rossweisse sirin fu_hua li_sushang senadina susannah_manatt
thelema_nutriscu liliya_olenyeva phosphophyllite wakaba_mutsumi misumi_uika
yahata_umiri yuutenji_nyamu illyasviel_von_einzbern prisma_illya
irisviel_von_einzbern waver_velvet hatsune_miku racing_miku symphony_meiko
symphony_kaito symphony_rin symphony_miku gramophone_miku
sagimiya_ryou mikami_nagisa
'''.split())
WORK_FAMILY_PREFIXES = ('love_live!', 'idolmaster', 'final_fantasy', 'lyrical_nanoha',
                        'neptune_', 'honkai_', 'kamen_rider')
NOTES_TOP500 = {
    'shigure_ui_(vtuber)': 'Independent avatar; no specific Copyright brand in frozen root catalog.',
    'sameko_saba': 'Independent avatar; designer and fanbase links do not establish an agency HOME.',
    'kemomimi-chan_(naga_u)': 'Own page explicitly identifies Naga U original character.',
    'dokibird': 'Independent avatar; do not transfer another persona agency to this identity.',
    'sendai_hakurei_no_miko': 'Catch-all for multiple fan-original predecessors, explicitly distinct from canon character.',
    'nimi_nightmare': 'Independent avatar; prior name and fanbase are not a specific Copyright root.',
    'yuuki_sakuna': 'Independent avatar; do not infer an agency from another persona.',
    'shigure_ui_(1st_costume)_(vtuber)': 'Explicit costume identity, but independent base has no specific catalog root.',
    'shylily': 'Independent avatar; collab and location joke are not a Copyright HOME.',
    'yorick_(shiori_novella)': 'Own page identifies Shiori Novella companion mascot; owner is Hololive EN Advent.',
}


def read(name):
    with (D / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (D / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main():
    names = ['PROVISIONAL_BROWSE_HOME_AUDIT_V1.csv', 'PROVISIONAL_BROWSE_HOME_INPUTS_V1.csv',
             'PROVISIONAL_BROWSE_HOME_AUDIT_HINTS_V1.csv', 'BROWSE_FINAL_REVIEW_CONTEXT_V1.csv',
             'BROWSE_FINAL_LIGHT_REVIEW_INPUTS_V1.json', 'COPYRIGHT_ROOTS_V1.csv',
             'AUTHORITY_COVERAGE_DECISIONS_V1.csv', 'AUTHORITY_SOURCE_MEMBERS_V1.csv',
             'COPYRIGHT_AUTHORITY_REGISTRY_V1.csv']
    hashes = {n: hashlib.sha256((D / n).read_bytes()).hexdigest() for n in names}
    protected = {
        'AUTHORITY_COVERAGE_DECISIONS_V1.csv': 'bee5915ac987a42885eb7688a39bd79128e7ac4a168ed5d8ed6a8cab9e7aae2a',
        'AUTHORITY_SOURCE_MEMBERS_V1.csv': 'a5c8d43ac36b0662f5406ecb7d5b4f65f67257b2ee7a3cd7d8abd52115f1214d',
        'COPYRIGHT_AUTHORITY_REGISTRY_V1.csv': '9dd947aca04e73733105fb34870ca4bb63a37c36a16e949f5d0339f6a7e84c71',
    }
    assert all(hashes[n] == expected for n, expected in protected.items()), 'Formal authority baseline changed'
    old = read(names[0])
    inputs = {r['character']: r for r in read(names[1])}
    hints = {r['character']: r for r in read(names[2])}
    ctx = {r['character']: r for r in read(names[3])}
    roots = {r['copyright_canonical'] for r in read('COPYRIGHT_ROOTS_V1.csv')}
    priorhomes = {r['character']: r['audited_browse_home'] for r in old if r['audited_browse_home']}
    # Review exactly the explicit Characters section of published creator works.
    scopes = {'kyatapi_land', 'otaku-kun_to_gyaru_no_koi', 'zenbu_kimi_no_sei',
              'nichijou_kamoshirenai', 'ordo_mediare_sisters_(ironlily)'}
    members = {}
    light = json.loads((D / names[4]).read_text(encoding='utf-8'))
    for page in light['pages']:
        if page['title'] not in scopes:
            continue
        body = page['body'].replace('\r', '')
        section = re.search(r'^h([1-6])\.\s*Characters\s*$([\s\S]*)', body, re.M | re.I)
        if not section:
            continue
        # Nested cast subheadings belong to Characters; sibling See also does not.
        cast = re.split(r'^h[1-' + section.group(1) + r']\. ', section.group(2), maxsplit=1, flags=re.M)[0]
        for target in re.findall(r'\[\[([^]|]+)(?:\|[^]]*)?\]\]', cast):
            exact = target.lower().replace(' ', '_')
            if exact in inputs:
                members.setdefault(exact, set()).add(page['title'])
    rows = []
    for r in sorted(old, key=lambda x: int(x['rank'])):
        t = r['character']; i = inputs[t]; h = hints[t]; c = ctx[t]
        previous = r['audited_browse_home']; home = previous
        pattern = 'PRIOR_PATTERN_REVIEW_RETAINED' if home else r['audit_rule']
        note = 'Prior Browse group judgment retained.' if home else 'Reviewed residual pattern; no sufficiently clear single Browse destination.'
        intro = c['wiki_intro']
        # Actual performer descriptions, not mentions of voice providers of fictional characters.
        performer = (t == 'mafia_kajita' or t == 'pekomama' or
                     bool(re.match(r'Voice of\b', intro, re.I)) or t == 'taisa_(cookie)')
        if t == 'bao_the_whale':
            home = ''; pattern = 'INDEPENDENT_AVATAR_NOT_RELATED_ANIME'
            note = 'Own page identifies independent live streamer avatar; Kakkou no Iinazuke is not this subject origin or membership.'
        elif performer:
            home = ''; pattern = 'REAL_PERSON_OR_PERFORMER_AVATAR_AMBIGUITY'
            note = 'Subject describes actual performer/person or their fan representation; keep work membership unresolved.'
        elif t in CHOICES:
            home = CHOICES[t]; pattern = 'LIGHT_SUBJECT_ORIGIN_BRAND_REVIEW'
            note = 'Human Browse preference from recognizable identity and saved wiki context; guest/event destination excluded; historical agency context is not a current-affiliation claim.'
        elif not home and len(members.get(t, set())) == 1:
            home = next(iter(members[t])); pattern = 'EXPLICIT_CREATOR_WORK_CHARACTER_SECTION'
            note = 'Exact linked member of named creator work; author qualifier does not make this a standalone OC.'
        elif not home and not h['artist_qualifiers'] and h['subject_is_actor'] != 'yes' and h['own_wiki_fan_original'] != 'yes':
            base = i['variant_base']; bh = h['variant_base_home'] or priorhomes.get(base, '')
            # Named entertainment families, plus explicitly described costumes/forms
            # with the same candidate context. Retain OC, fan transform and guest ambiguity.
            family = base in FAMILIES or bh.startswith(WORK_FAMILY_PREFIXES)
            explicit = h['explicit_costume_identity'] == 'yes' or h['clear_costume_name'] == 'yes'
            candidates = set(i['candidate_roots'].split(' | '))
            if bh in roots and base and 'original' not in candidates and (family or (explicit and bh in candidates)):
                home = 'honkai_(series)' if bh.startswith('honkai_') else bh
                if base.startswith(('symphony_', 'racing_miku')):
                    home = 'vocaloid'
                pattern = 'REVIEWED_NAMED_COSTUME_FORM_FAMILY'
                note = f'Browse-only named form/costume family review; base={base}; saved base context={bh}; variant authority remains unchanged.'
        if t in NOTES_TOP500:
            note = NOTES_TOP500[t]
            pattern = 'TOP500_INDIVIDUAL_LIGHT_CHECK'
        if t == 'cottontail_(vtuber)':
            pattern = 'INDEPENDENT_AVATAR_NO_SPECIFIC_ROOT'
            note = 'Page explicitly describes voice actor VTuber avatar; avatar is distinct from performer, but no specific Browse root is established.'
        assert not home or home in roots, (t, home)
        action = 'KEEP' if home == previous else 'ADD' if home and not previous else 'REMOVE' if previous and not home else 'CHANGE'
        rows.append(dict(character=t, previous_audited_home=previous, reviewed_browse_home=home,
                         review_state='REVIEWED_BROWSE_HOME' if home else 'REVIEWED_UNRESOLVED',
                         action=action, confidence=r['confidence'] if action == 'KEEP' and home else 'MEDIUM' if home else 'LOW',
                         review_pattern=pattern, review_note=note, source_url=c['source_url'],
                         rank=r['rank'], post_count=r['post_count'], current_formal_state=r['current_formal_state'],
                         formal_authority_eligible='NO'))
    assert len(rows) == len({r['character'] for r in rows}) == 10102
    write('REVIEWED_BROWSE_HOME_V1.csv', rows)
    write('BROWSE_FINAL_TOP500_CHECKS_V1.csv', [r for r in rows if r['character'] in NOTES_TOP500])
    originally_open = {r['character'] for r in old if not r['audited_browse_home'] and int(r['rank']) <= 2000}
    write('BROWSE_FINAL_TOP2000_CHECKS_V1.csv', [r for r in rows if r['character'] in originally_open])
    groups = Counter((r['review_state'], r['reviewed_browse_home'], r['review_pattern'], r['action']) for r in rows)
    write('BROWSE_FINAL_REVIEW_GROUPS_V1.csv', [dict(review_state=k[0], reviewed_browse_home=k[1], review_pattern=k[2], action=k[3], count=v) for k, v in sorted(groups.items())])
    summary = dict(base_commit=BASE, inspected=len(rows), reviewed_browse_home=sum(bool(r['reviewed_browse_home']) for r in rows),
                   unresolved=sum(not r['reviewed_browse_home'] for r in rows),
                   actions=dict(Counter(r['action'] for r in rows)),
                   Top500_unresolved=sum(not r['reviewed_browse_home'] and int(r['rank']) <= 500 for r in rows),
                   Top2000_unresolved=sum(not r['reviewed_browse_home'] and int(r['rank']) <= 2000 for r in rows),
                   residual_patterns=dict(Counter(r['review_pattern'] for r in rows if not r['reviewed_browse_home'])),
                   immutable_input_hashes=hashes, formal_authority_eligible=False,
                   note='Final bounded Browse audit disposition, not strict authority certification. Unresolved remains a valid reviewed outcome. Prior overlay and formal ledgers are immutable.')
    (D / 'BROWSE_FINAL_REVIEW_CHECKPOINT_V1.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
