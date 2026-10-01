#!/usr/bin/env python3
"""Fast pattern audit of a provisional overlay, never formal HOME authority."""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'docs/issue216'
BASE = 'd9ab6d0739b8e4ff6293a25c2a21c9eb4aad19d5'
REAL_PERSONS = set('''tsukine_kona nirei_nozomi sakurai_hina kan_kanna nonaka_kokona
kurusu_rin kusunoki_tomori saitou_shuka sasaki_kotoko hayama_fuka inami_anju
mimori_suzuko aida_rikako uchida_aya kitou_akari miyake_miu nanjou_yoshino
akamine_ten kusuda_aina tokui_sora kobayashi_aika nitta_emi maeda_kaori
uesaka_sumire ogura_yui iwami_manaka fairouz_ai inoue_kikuko inoue_marina
yanning sawashiro_miyuki taketatsu_ayana hikasa_youko toyosaki_aki minase_inori
taneda_risa hanazawa_kana hirano_aya gotou_yuuko cristina_valenzuela
okada_mei youmiya_hina hayashi_coco aoki_hina takao_kanon touyama_nao
kayano_ai ozawa_ari iguchi_yuka uchida_shuu steven_seagal suzaki_aya
uchida_maaya fukuen_misato kurosawa_tomoyo hayami_saori amamiya_sora
itou_miku takahashi_rie minase_inori hanae_natsuki nakamura_yuuichi
toyama_nao sugita_tomokazu miyano_mamoru fukuyama_jun uchiyama_kouki
ishikawa_kaito kamiya_hiroshi miyata_kouki ono_daisuke ono_kenshou
satou_satomi oogame_asuka taketatsu_ayana tamura_yukari mizuki_nana
erling_haaland
ikezoe_ken'ichi kouchi_tadashi zun iwata_satoru nasu_kinoko fujita_saki
shimoda_asami asakawa_yuu nakajima_megumi ishikawa_yui sakura_ayane
'''.split())
REAL_CONTEXT_ROOTS = set('''formula_one gachimuchi manatsu_no_yo_no_inmu
indie_utaite minecraft_youtube twice_(group) strawberry_prince urashimasakatasen perfume_(band)
daft_punk le_sserafim queen_(band) akb48 national_basketball_association
'''.split())
GENERIC_ROOTS = {'indie_virtual_youtuber', 'virtual_youtuber', 'vtuber', 'original',
                 'real_life', 'character', 'nurse', 'fairy_tale_character', 'alter_ego'}
CONTEXT_ROOTS = {'5pb.', 'nitroplus', 'cygames', 'disney', 'sega', 'nintendo',
                 'microsoft', 'niconico', '2channel', '4chan'}
NON_WORK_ROOTS = {'greek_mythology', 'egyptian_mythology', 'japanese_mythology',
                  'the_bible', 'book_of_genesis', 'japanese_urban_legends'}
RISKY_IDENTITIES = {'unsinkable_sam', 'meto_(cat)', 'victory_(dog)', 'uchicchii',
                    'bishamonten', 'loch_ness_monster', 'okiku_(banchou_sarayashiki)',
                    'tiger_mask_(character)', 'kawashiro_mitori', 'steam_delivery_girl'}
# Alias namespace collisions and author-qualified published-work characters were
# explicitly separated from creator OCs in the group review.
ARTIST_QUALIFIER_EXCEPTIONS = {'gridman_(ssss)', 'fox_wife_(batta_(kanzume_quality))',
                             "devil's_hand_(ishiyumi)"}
CORRECTIONS = {'family_computer_robot': 'nintendo', 'english_miku': 'vocaloid'}
# Quick high-value recognition of origin/brand context among guest/related hints.
# These are human provisional judgments, not an authority table.
ADDITIONS = {
    'chando_(ado)': 'ado_(utaite)', 'brazilian_miku': 'vocaloid',
    'racing_miku': 'vocaloid', 'hello_kitty_(character)': 'sanrio',
    'zentreya': 'vshojo', 'ushiromiya_jessica': 'umineko_no_naku_koro_ni',
    'shokudaikiri_mitsutada': 'touken_ranbu', 'ookurikara': 'touken_ranbu',
    'captain_falcon': 'f-zero', 'piranha_plant': 'mario_(series)',
    'hachune_miku': 'vocaloid', 'super_sonic': 'sonic_(series)',
    'cinnamiku': 'vocaloid', 'blanc_(neptunia)': 'neptune_(series)',
    'satou_lilly': 'katawa_shoujo', 'kuriboh': 'yu-gi-oh!',
    'ezio_auditore_da_firenze': "assassin's_creed_(series)",
    'blonney': 'reverse:1999', 'dokuro-kun_(houshou_marine)': 'hololive',
    'upao_(amane_kanata)': 'hololive', 'pina_korata': 'idolmaster',
    'wii_fit_trainer_(female)': 'wii_fit',
}
BROWSE_ONLY_BLOCK_EXCEPTIONS = {'rx-78-2_gundam': 'gundam', 'p-head_producer': 'idolmaster'}


def read(name):
    with (D / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows, fields=None):
    with (D / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def main():
    old = read('PROVISIONAL_BROWSE_HOME_V1.csv')
    inputs = {r['character']: r for r in read('PROVISIONAL_BROWSE_HOME_INPUTS_V1.csv')}
    hints = {r['character']: r for r in read('PROVISIONAL_BROWSE_HOME_AUDIT_HINTS_V1.csv')}
    roots = {r['copyright_canonical'] for r in read('COPYRIGHT_ROOTS_V1.csv')}
    frozen_meta = json.loads((D/'PROVISIONAL_BROWSE_HOME_AUDIT_HINTS_V1.json').read_text(encoding='utf-8'))
    immutable_names = {'AUTHORITY_COVERAGE_DECISIONS_V1.csv', 'AUTHORITY_SOURCE_MEMBERS_V1.csv',
                       'COPYRIGHT_AUTHORITY_REGISTRY_V1.csv', 'PROVISIONAL_BROWSE_HOME_V1.csv',
                       'PROVISIONAL_BROWSE_HOME_INPUTS_V1.csv', 'DANBOORU_NORMALIZED_SEMANTIC_RELATIONS_V1.csv'}
    immutable_hashes = {}
    for source, expected in frozen_meta['input_hashes'].items():
        name = source.replace('\\', '/').rsplit('/', 1)[-1]
        if name in immutable_names:
            actual = hashlib.sha256((D/name).read_bytes()).hexdigest()
            assert actual == expected, name
            immutable_hashes[name] = actual
    assert set(immutable_hashes) == immutable_names
    assert hashlib.sha256((D/'PROVISIONAL_BROWSE_HOME_AUDIT_HINTS_V1.csv').read_bytes()).hexdigest() == frozen_meta['hints_sha256']
    assert len(old) == 10102 and Counter(r['confidence'] for r in old) == {'HIGH': 308, 'MEDIUM': 6703, 'LOW': 3091}
    parents = defaultdict(set)
    for r in read('DANBOORU_NORMALIZED_SEMANTIC_RELATIONS_V1.csv'):
        if r['status'] == 'active' and r['antecedent_category'] == r['consequent_category'] == '3':
            parents[r['antecedent_canonical']].add(r['consequent_canonical'])
    def ancestors(x):
        out, stack = set(), list(parents[x])
        while stack:
            v = stack.pop()
            if v not in out:
                out.add(v); stack.extend(parents[v] - out)
        return out
    def related_choice(candidates):
        usable = candidates - GENERIC_ROOTS
        if len(usable) > 1:
            usable -= CONTEXT_ROOTS
        choices = [x for x in usable if all(y == x or x in ancestors(y) for y in usable)]
        return choices[0] if len(choices) == 1 else ''

    results = []
    reviewed_bases = {}
    # Stable HIGH -> MEDIUM -> LOW order; original overlay is never rewritten.
    for r in sorted(old, key=lambda r: ({'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}[r['confidence']], int(r['rank']))):
        t, previous = r['character'], r['provisional_home']
        inp, h = inputs[t], hints[t]
        candidates = set(filter(None, inp['candidate_roots'].split(' | '))) & roots
        q = inp['qualifier_root']
        pattern = ('WORK_QUALIFIER' if q == previous and q else
                   'OWN_WIKI_CONTEXT' if inp['wiki_intro_roots'] else 'FROZEN_CANDIDATE')
        home, rule = previous, 'PLAUSIBLE_WORK_SCOPE_PATTERN'
        hazard = ''
        if (t in REAL_PERSONS or h['subject_is_actor'] == 'yes'
                or re.search(r'\((?:racehorse|voice_actor|voice_actress|real)\)', t)
                or previous in REAL_CONTEXT_ROOTS):
            hazard = 'REAL_PERSON_OR_PERFORMER_CONTEXT'
        elif h['artist_qualifiers'] and t not in ARTIST_QUALIFIER_EXCEPTIONS:
            hazard = 'ARTIST_QUALIFIED_ORIGINAL_OR_DERIVATIVE_IDENTITY'
        elif h['own_wiki_fan_original'] == 'yes' or t in RISKY_IDENTITIES:
            hazard = 'FAN_OR_NON_WORK_IDENTITY_NOT_SAFE_FOR_BULK_ACCEPTANCE'
        elif previous in NON_WORK_ROOTS or re.search(r'\((?:mythology|youtuber)\)', t):
            hazard = 'NON_WORK_OR_REAL_PERSON_APPLICABILITY'
        if hazard:
            home, rule, pattern = '', hazard, 'HAZARD_' + hazard
        elif previous:
            if t in CORRECTIONS:
                home, rule = CORRECTIONS[t], 'GUEST_CONTEXT_REPLACED_BY_NATURAL_BRAND'
            elif q and q in candidates and previous in ancestors(q):
                rule = 'QUALIFIER_TITLE_AND_FRANCHISE_CONTEXT_COMPATIBLE'
            elif r['confidence'] == 'HIGH':
                rule = 'HIGH_PATTERN_REVIEW_NO_CONTRADICTORY_SIGNAL'
            elif t in ARTIST_QUALIFIER_EXCEPTIONS:
                rule = 'KNOWN_WORK_SCOPE_NOT_ARTIST_OC_ALIAS_COLLISION'
        else:
            home, rule = '', 'NO_OBVIOUS_ADDITIONAL_CLASSIFICATION'
            if t in BROWSE_ONLY_BLOCK_EXCEPTIONS:
                home, rule = BROWSE_ONLY_BLOCK_EXCEPTIONS[t], 'RECOGNIZABLE_BROWSE_CONTEXT_FORMAL_IDENTITY_BLOCK_UNCHANGED'
            elif q == 'project_voltage' and q in candidates:
                home, rule = q, 'DEDICATED_COLLABORATION_SCOPE_NOT_ONE_PARENT_IP'
            elif t in ADDITIONS and ADDITIONS[t] in roots and inp['current_state'] not in {'IDENTITY_BLOCKED', 'EVIDENCE_CONFLICT'}:
                home, rule = ADDITIONS[t], 'HIGH_VALUE_ORIGIN_BRAND_RECOGNITION'
            elif inp['variant_base']:
                basehome = h['variant_base_home'] or reviewed_bases.get(inp['variant_base'], '')
                if (basehome in roots and (h['explicit_costume_identity'] == 'yes' or h['clear_costume_name'] == 'yes')
                        and 'original' not in candidates and basehome in candidates
                        and inp['current_state'] not in {'IDENTITY_BLOCKED', 'EVIDENCE_CONFLICT'}):
                    home, rule = basehome, 'CLEAR_COSTUME_FAMILY_BASE_BROWSE_CONTEXT'
            elif ('original' not in candidates and inp['artist_qualified'] != 'yes'
                    and inp['current_state'] not in {'IDENTITY_BLOCKED', 'EVIDENCE_CONFLICT'}):
                choice = related_choice(candidates)
                if choice and choice not in NON_WORK_ROOTS | REAL_CONTEXT_ROOTS:
                    home, rule = choice, 'RELATED_TITLE_FRANCHISE_PATTERN_COLLAPSED'
        assert not home or home in roots
        if home:
            reviewed_bases[t] = home
        verdict = ('ACCEPT' if previous and home == previous else 'CHANGE' if home else 'REJECT' if previous else 'UNRESOLVED')
        results.append(dict(character=t, previous_provisional_home=previous, audited_browse_home=home,
                            audit_verdict=verdict, audit_rule=rule, evidence_pattern=pattern,
                            previous_confidence=r['confidence'], confidence=r['confidence'] if verdict == 'ACCEPT' else 'MEDIUM' if home else 'LOW',
                            reason=r['reason'], evidence_hint=r['evidence_hint'], rank=r['rank'], post_count=r['post_count'],
                            current_formal_state=inp['current_state'], formal_authority_eligible='NO'))
    results.sort(key=lambda r: int(r['rank']))
    assert len({r['character'] for r in results}) == len(results) == 10102
    groups = defaultdict(list)
    for r in results:
        groups[(r['previous_provisional_home'], r['reason'], r['evidence_pattern'], r['audit_verdict'], r['audited_browse_home'], r['audit_rule'])].append(r)
    group_rows = [dict(previous_provisional_home=k[0], original_reason=k[1], evidence_pattern=k[2], verdict=k[3], audited_browse_home=k[4], audit_rule=k[5], count=len(v), samples=' | '.join(r['character'] for r in v[:3])) for k, v in sorted(groups.items())]
    write('PROVISIONAL_BROWSE_HOME_AUDIT_V1.csv', results)
    write('PROVISIONAL_BROWSE_HOME_AUDIT_GROUPS_V1.csv', group_rows)
    counts = Counter(r['audit_verdict'] for r in results)
    summary = dict(base_commit=BASE, inspected=len(results), original_assignments=7011,
                   ACCEPT=counts['ACCEPT'], CHANGE=counts['CHANGE'], REJECT=counts['REJECT'],
                   newly_classified_from_unresolved=sum(r['audit_verdict'] == 'CHANGE' and not r['previous_provisional_home'] for r in results),
                   changes_to_existing_assignments=sum(r['audit_verdict'] == 'CHANGE' and bool(r['previous_provisional_home']) for r in results),
                   still_unresolved=sum(not r['audited_browse_home'] for r in results),
                   Top500_unresolved=sum(not r['audited_browse_home'] and int(r['rank']) <= 500 for r in results),
                   Top2000_unresolved=sum(not r['audited_browse_home'] and int(r['rank']) <= 2000 for r in results),
                   rule_counts=dict(Counter(r['audit_rule'] for r in results)),
                   confidence_stage_verdicts={c: dict(Counter(r['audit_verdict'] for r in results if r['previous_confidence'] == c)) for c in ['HIGH', 'MEDIUM', 'LOW']},
                   audit_group_count=len(group_rows), immutable_input_hashes=immutable_hashes,
                   note='Pattern audit of a provisional Browse overlay, not formal HOME validation. CHANGE includes additions from previously unresolved rows.')
    (D/'PROVISIONAL_BROWSE_HOME_AUDIT_CHECKPOINT_V1.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
