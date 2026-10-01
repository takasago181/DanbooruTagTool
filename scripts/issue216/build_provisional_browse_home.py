#!/usr/bin/env python3
"""Rebuild a research-only, unreviewed Browse overlay; never writes HOME ledgers."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'docs/issue216'
FIELDS = ['character', 'provisional_home', 'confidence', 'reason', 'evidence_hint',
          'review_state', 'rank', 'post_count', 'current_state']
# These are Browse preferences, not authority normalization rules.
PREFER = {
    'nikki': 'nikki_(series)', 'neptunia': 'neptune_(series)',
    'naruto': 'naruto_(series)', 'mega_man': 'mega_man_(series)',
    'nanoha': 'lyrical_nanoha', 'utdr': 'utdr_(toby_fox)',
    'tsukuyomi': 'cho_kaguya-hime!',
}
GENERIC = {'original', 'real_life', 'character', 'vtuber', 'virtual_youtuber',
           'indie_virtual_youtuber', 'nurse', 'fairy_tale_character', 'alter_ego'}
# A small explicit human-readable recognition pass over the highest-frequency rows.
RECOGNIZED = {
    'tachibana_kanade': 'angel_beats!', 'nakamura_yuri': 'angel_beats!',
    'phosphophyllite': 'houseki_no_kuni', 'ranni_the_witch': 'elden_ring',
    'malenia_blade_of_miquella': 'elden_ring', 'kurapika': 'hunter_x_hunter',
    'gon_freecss': 'hunter_x_hunter', 'ushiromiya_ange': 'umineko_no_naku_koro_ni',
    'ushiromiya_maria': 'umineko_no_naku_koro_ni', 'ogata_hyakunosuke': 'golden_kamuy',
    'sugimoto_saichi': 'golden_kamuy', 'uzaki_hana': 'uzaki-chan_wa_asobitai!',
    'uzaki_tsuki': 'uzaki-chan_wa_asobitai!', 'arle_nadja': 'puyopuyo',
    'roxas': 'kingdom_hearts', 'purah': 'the_legend_of_zelda',
    'toon_link': 'the_legend_of_zelda', 'tanya_degurechaff': 'youjo_senki',
    'yamamura_sadako': 'the_ring', 'rotom_phone': 'pokemon',
    'rx-78-2_gundam': 'gundam', 'zaku_ii': 'gundam',
    'mochizuki_honami': 'project_sekai', 'haro': 'gundam',
    'nikki_(nikki)': 'nikki_(series)', 'momo_(nikki)': 'nikki_(series)',
    'shiomi_kotone': 'persona', 'noelle_holiday': 'utdr_(toby_fox)',
    'neptune_(neptunia)': 'neptune_(series)', 'nepgear': 'neptune_(series)',
    'vita_(nanoha)': 'lyrical_nanoha', 'gogeta': 'dragon_ball',
    'nugget_(project_moon)': 'project_moon', 'tron_bonne_(mega_man)': 'mega_man_(series)',
    'psylocke': 'marvel',
}
RECOGNIZED_MEDIUM = {
    'yuzuki_yukari': 'voiceroid', 'touhoku_kiritan': 'voiceroid',
    'tsurumaki_maki': 'voiceroid', 'gumi': 'vocaloid',
    'akita_neru': 'vocaloid', 'yowane_haku': 'vocaloid',
    'isekaijoucho': 'kamitsubaki_studio',
    'neuro-sama': 'vedal_ai', 'reines_el-melloi_archisorte': 'fate_(series)',
    'sion_eltnam_(type-moon)': 'tsukihime',
}


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def classify(r, valid_roots):
    tag = r['character']
    roots = set(filter(None, r['candidate_roots'].split(' | '))) & valid_roots
    roots = {PREFER.get(x, x) if PREFER.get(x, x) in valid_roots else x for x in roots}
    intro = set(filter(None, r['wiki_intro_roots'].split(' | '))) & roots
    qualifier = r['qualifier_root']
    hint = ('candidate=' + r['candidate_roots'] + '; qualifier=' + qualifier
            + '; wiki=' + r['wiki_hint'] + '; variant_base=' + r['variant_base'])
    state = r['current_state']
    home, confidence, reason = '', 'LOW', 'Insufficient recognizable Browse signal'
    if r['artist_qualified'] == 'yes' or 'real_life' in roots:
        reason = 'OC/artist-qualified/real-person class retained for later identity and applicability review'
    elif state in {'IDENTITY_BLOCKED', 'EVIDENCE_CONFLICT'}:
        reason = 'Existing identity/conflict finding retained; no provisional override'
    elif r['variant_base'] and r['variant_validated'] != 'yes':
        reason = 'Candidate-only variant identity retained unresolved'
    elif tag in RECOGNIZED_MEDIUM and RECOGNIZED_MEDIUM[tag] in roots:
        home, confidence, reason = RECOGNIZED_MEDIUM[tag], 'MEDIUM', 'Fast recognizable ecosystem/origin preference; related brands or guest contexts require audit'
    elif 'original' in roots:
        reason = 'Original/derivative identity not resolved by fast pass'
    else:
        usable = roots - GENERIC
        if tag in RECOGNIZED and RECOGNIZED[tag] in usable:
            home, confidence, reason = RECOGNIZED[tag], 'HIGH', 'Recognized work membership in fast high-frequency review, consistent with frozen candidate'
        elif qualifier in usable and len(usable) == 1:
            home, confidence, reason = next(iter(usable)), 'HIGH', 'Exact work qualifier agrees with a unique frozen Browse candidate; provisional inference only'
        elif len(intro - GENERIC) == 1 and len(usable) == 1 and r['wiki_membership_phrase'] == 'yes':
            home, confidence, reason = next(iter(usable)), 'HIGH', 'Own cached wiki introductory membership phrase agrees with unique candidate; not validated authority'
        elif len(usable) == 1:
            home, confidence, reason = next(iter(usable)), 'MEDIUM', 'Single plausible work/ecosystem candidate; identity and Browse scope pending audit'
        elif len(usable) > 1:
            # Related title/franchise contexts are allowed only in this provisional overlay.
            families = [x for x in usable if x in {'fate_(series)', 'idolmaster', 'love_live!',
                        'final_fantasy', 'gundam', 'precure', 'science_adventure'}
                        and all(x in y or (x == 'fate_(series)' and y.startswith('fate/'))
                                or (x == 'idolmaster' and y.startswith('idolmaster'))
                                or (x == 'love_live!' and y.startswith('love_live'))
                                or (x == 'science_adventure' and y in {'steins;gate', 'chaos;head', 'chaos;child', 'robotics;notes'})
                                for y in usable if y != x)]
            if len(families) == 1:
                home, confidence, reason = families[0], 'MEDIUM', 'Related franchise/subseries candidates; provisional franchise Browse preference'
            else:
                reason = 'Multiple work candidates without a natural unique Browse preference'
    return dict(character=tag, provisional_home=home, confidence=confidence, reason=reason,
                evidence_hint=hint, review_state='PENDING_AUDIT' if home else 'PROVISIONAL_UNRESOLVED',
                rank=r['rank'], post_count=r['post_count'], current_state=state)


def main():
    frozen = read(D / 'PROVISIONAL_BROWSE_HOME_INPUTS_V1.csv')
    formal = read(D / 'AUTHORITY_COVERAGE_DECISIONS_V1.csv')
    roots = {r['copyright_canonical'] for r in read(D / 'COPYRIGHT_ROOTS_V1.csv')}
    assert {r['character'] for r in frozen} == {r['canonical_character'] for r in formal if not r['home_copyright']}
    rows = [classify(r, roots) for r in sorted(frozen, key=lambda r: (int(r['rank']), r['character']))]
    assert len(rows) == len({r['character'] for r in rows})
    assert all(not r['provisional_home'] or r['provisional_home'] in roots for r in rows)
    target = D / 'PROVISIONAL_BROWSE_HOME_V1.csv'
    with target.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator='\n'); w.writeheader(); w.writerows(rows)
    counts = Counter(r['confidence'] for r in rows)
    checkpoint = dict(inspected=len(rows), provisional_HIGH=counts['HIGH'], provisional_MEDIUM=counts['MEDIUM'],
                      provisional_unresolved=counts['LOW'],
                      Top500_remaining_provisional_unresolved=sum(not r['provisional_home'] and int(r['rank']) <= 500 for r in rows),
                      Top2000_remaining_provisional_unresolved=sum(not r['provisional_home'] and int(r['rank']) <= 2000 for r in rows))
    (D / 'PROVISIONAL_BROWSE_HOME_CHECKPOINT_V1.json').write_text(json.dumps(checkpoint, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(checkpoint))


if __name__ == '__main__':
    main()
