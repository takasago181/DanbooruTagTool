#!/usr/bin/env python3
"""One bounded artist-qualified Browse pass, independent of formal authority."""
import csv
import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parents[2] / 'docs/issue216'
BASE = '8789c41b8e1b4b96bc770a908f0dffd3dc865910'

# Human group review of exact subjects against cached/bulk own-page descriptions.
# Published creator works are distinguished from derivative fan identities below.
WORK = {
    'igarashi_kyou_(eroe)': 'seitenkango._shinyuu_to',
    'hasumi_souji_(eroe)': 'seitenkango._shinyuu_to',
    'kuroi_kuroneko_(katsumata_hiroki)': 'kamoku_dakedo_mechakucha_nori_no_ii_kuroneko-chan',
    'arung_samudra_(cessa)': 'ombok_diving_and_delivery_services',
    'itoya_(studionice2011)': 'working_girls_weekly',
    'haimiya_mio_(kamiyama_sumu)': 'haimiya-senpai_wa_kowakute_kawaii',
    'kuchisake-onna_(ishiyumi)': 'mechanical_buddy_universe',
    'lirin_(bae.c)': 'tsumi_no_hahen_(debris)',
}
DERIVATIVE = {
    'puru-see_(hoshizuki_(seigetsu))': 'touhou',
    'kuraishi_ringo_(glassy0302)': 'pokemon', 'inu_sakuya_(nejikirio)': 'touhou',
    'smol_mari_(blue_archive)_(horuhara)': 'blue_archive',
    'robin_(batrobin_k)': 'dc_comics', 'bunny-san_(naga_u)': 'sekaiju_no_meikyuu',
    'yorra_villeneuve_(nyantcha)': 'pokemon', 'gyaru_bulbasaur_(shin_no_tenpii)': 'pokemon',
    'hisamura_natsuki_(munmu-san)': 'kantai_collection', 'they_(kiman)': 'among_us',
    'hata-tan_(rui_(hershe))': 'touhou',
    'giant_otter_(kemono_friends)_(kuro_(kurojill))': 'kemono_friends',
    'female_sensei_(blue_archive)_(senta_(ysk_0218))': 'blue_archive',
    'female_sensei_(blue_archive)_(vivo_(vivo_sun_0222))': 'blue_archive',
    'sakura_miku_(rella)': 'vocaloid', 'panda_meiling_(seki_(red_shine))': 'touhou',
    'kazami_youka_(yokochou)': 'touhou', 'taida_(lazyartlazy12)': 'fate_(series)',
    'shirohashi_akari_(toji_(y2toj2))': 'umamusume', 'archerko_(himura_kiseki)': 'fate_(series)',
    'dovakini-chan_(nisetanaka)': 'the_elder_scrolls', 'chibi_miku_(mayo_riyo)': 'vocaloid',
    'glorpi_miku_(dyarikku)': 'vocaloid', 'makhia_(kasugai_(de-tteiu))': 'pokemon',
    'maria_(kasugai_(de-tteiu))': 'pokemon', 'eve_(kasugai_(de-tteiu))': 'pokemon',
    'gyaru_slowpoke_(shin_no_tenpii)': 'pokemon', 'proto_miku_(cheri_zao)': 'vocaloid',
    "awp_(girls'_frontline)_(nekoya_(liu))": "girls'_frontline",
    'shimamura_youmu_(unadare)': 'touhou', 'geronimo_(rokkotsu)': 'fate_(series)',
    'donut_(zoza)': 'splatoon_(series)', 'pudding_(zoza)': 'splatoon_(series)',
    'arihara_yuuna_(hanauna)': 'dragon_quest', 'majiko_(emurin)': 'ragnarok_online',
    'catchouli_(hazuki_ruu)': 'touhou', 'arcee_(prime)': 'transformers',
    'piano_(srnhuyuno)': 'mega_man_(classic)', 'renz_(rirene_rn)': 'final_fantasy',
    'xiaoling_(kyouno)': 'touhou', 'mouse_marisa_(yuasan)': 'touhou',
    'inukai_iroha_(dog)_(@est@)': 'precure', 'nekoyashiki_mayu_(cat)_(@est@)': 'precure',
    'kasane_neko_(haru57928031)': 'utau', 'biriri_(spacezin)': 'pokemon',
    'iris_(ryou@ryou)': 'phantasy_star',
    'uss_lexington_(cv-16)_(y.ssanoha)': 'warship_girls_r',
}
AMBIGUOUS = {
    'old_man_(guin_guin)': 'OC changes between Kancolle and Arknights story contexts; no single stable origin.',
    'little_blue_(guin_guin)': 'Admiral stand-in also independent artist signature/self-insert; no exclusive work identity.',
    'british_admiral_(y.ssanoha)': 'Shared Azur Lane and Warship Girls R comic identity; neither silently preferred.',
    'melusoy_(ebora)': 'Resemblance to Melusine alone does not establish a derived Character identity.',
    'baphomet_(grizz)': 'Game-inspired independent creation; association alone is insufficient in this pass.',
    'merc-san_(k0ng)': 'Loosely based on game faction; no clear borrowed Character identity.',
    'bandit-chan_(k0ng)': 'Loosely based on game faction; no clear borrowed Character identity.',
    'ghost_girl_(shikisokuzeku76)': 'OC based on another character; insufficient stable work scope in available description.',
}


def read(name):
    with (D / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (D / name).open('w', encoding='utf-8', newline='') as f:
        out = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        out.writeheader(); out.writerows(rows)


def main():
    old = read('REVIEWED_BROWSE_HOME_V1.csv')
    subjects = [r for r in old if r['review_pattern'] == 'ARTIST_QUALIFIED_ORIGINAL_OR_DERIVATIVE_IDENTITY']
    assert len(subjects) == 1092 and all(not r['reviewed_browse_home'] for r in subjects)
    inputs = {r['character']: r for r in read('PROVISIONAL_BROWSE_HOME_INPUTS_V1.csv')}
    roots = {r['copyright_canonical'] for r in read('COPYRIGHT_ROOTS_V1.csv')}
    source = json.loads(gzip.decompress((D / 'BROWSE_ARTIST_REVIEW_WIKI_INPUTS_V1.json.gz').read_bytes()))
    assert set(source['subjects']) == {r['character'] for r in subjects}
    pages = {r['title']: r for r in source['cached_pages']}
    for batch in source['bulk_requests']:
        assert all(r['title'] in batch['requested_tags'] for r in batch['pages'])
        pages.update({r['title']: r for r in batch['pages']})
    reviewed = []
    for row in subjects:
        t = row['character']; page = pages.get(t, {})
        body = page.get('body', '').replace('\r', '')
        intro = body.split('\n\n')[0]
        home = ''; category = 'AMBIGUOUS'; pattern = 'NO_CLEAR_ORIGIN_IN_AVAILABLE_CONTEXT'
        reason = 'Author qualifier or candidate alone does not distinguish standalone OC from fan derivative.'
        # Check avatar/persona applicability before either OC or derivative classification.
        if re.search(r'virtual.?YouTuber|virtual.?youtuber|\bVTuber\b|performer|self.portrait|artist.?self.insert|artist avatar|fictional persona', intro, re.I):
            category = 'ORIGINAL_INDEPENDENT'; pattern = 'AVATAR_PERSONA_SEPARATE_FROM_WORK_CAST'
            reason = 'Explicit artist/persona/VTuber context; no fictional work HOME assigned in this pass.'
        elif t in WORK or t in DERIVATIVE:
            home = (WORK | DERIVATIVE)[t]
            category = 'DERIVATIVE_OR_WORK_SCOPED'
            pattern = 'EXPLICIT_AUTHORED_WORK' if t in WORK else 'REVIEWED_FAN_IDENTITY_OR_IN_UNIVERSE_DESIGN'
            reason = 'Named authored work membership.' if t in WORK else 'Reviewed borrowed Character design or explicit in-universe fan identity; use origin IP rather than artist/guest context.'
        elif t in AMBIGUOUS:
            reason = AMBIGUOUS[t]; pattern = 'LOOSE_INSPIRATION_OR_MULTIPLE_CONTEXTS'
        elif inputs[t]['qualifier_root'] and inputs[t]['qualifier_root'] in roots:
            home = inputs[t]['qualifier_root']; category = 'DERIVATIVE_OR_WORK_SCOPED'
            pattern = 'EXPLICIT_NESTED_WORK_QUALIFIER'
            reason = 'Exact canonical work qualifier inside artist-qualified identity; Browse-only fan-work routing.'
        elif re.search(r'\boriginal\b|\bOC\b|character (?:created|designed|by|belonging)|mascot character|recurring characters|own character', intro, re.I):
            category = 'ORIGINAL_INDEPENDENT'; pattern = 'OWN_WIKI_CREATOR_ORIGINAL_DESCRIPTION'
            reason = 'Own-page creator/original description; no explicit borrowed identity or single work scope established.'
        if home:
            assert home in roots, (t, home)
        reviewed.append(dict(character=t, classification=category, browse_home=home, pattern=pattern,
                             reason=reason, wiki_id=page.get('id', ''),
                             source_url=f"https://danbooru.donmai.us/wiki_pages/{page['id']}" if page else '',
                             evidence_excerpt=' '.join(intro.split())[:900],
                             qualifier_root=inputs[t]['qualifier_root'], rank=row['rank'],
                             formal_authority_eligible='NO'))
    bytag = {r['character']: r for r in reviewed}
    updated = []
    for row in old:
        r = dict(row); review = bytag.get(r['character'])
        if review:
            home = review['browse_home']
            r.update(previous_audited_home=row['reviewed_browse_home'], reviewed_browse_home=home,
                     review_state='REVIEWED_BROWSE_HOME' if home else 'REVIEWED_UNRESOLVED',
                     action='ADD' if home else 'KEEP', confidence='MEDIUM' if home else 'LOW',
                     review_pattern=review['pattern'], review_note=review['reason'], source_url=review['source_url'])
        updated.append(r)
    assert len(updated) == len({r['character'] for r in updated}) == 10102
    write('BROWSE_ARTIST_QUALIFIER_REVIEW_V1.csv', reviewed)
    write('REVIEWED_BROWSE_HOME_V2.csv', updated)
    patterns = Counter((r['classification'], r['pattern'], r['browse_home']) for r in reviewed)
    write('BROWSE_ARTIST_QUALIFIER_GROUPS_V1.csv', [dict(classification=k[0], pattern=k[1], browse_home=k[2], count=v) for k, v in sorted(patterns.items())])
    summary = dict(base_commit=BASE, inspected=1092, classification_counts=dict(Counter(r['classification'] for r in reviewed)),
                   fan_derivative_assignments=sum(bool(r['browse_home']) and r['pattern'] != 'EXPLICIT_AUTHORED_WORK' for r in reviewed),
                   authored_work_assignments=sum(r['pattern'] == 'EXPLICIT_AUTHORED_WORK' for r in reviewed),
                   reviewed_browse_home=sum(bool(r['reviewed_browse_home']) for r in updated),
                   unresolved=sum(not r['reviewed_browse_home'] for r in updated),
                   Top2000_reduction=sum(bool(r['browse_home']) and int(r['rank']) <= 2000 for r in reviewed),
                   Top2000_unresolved=sum(not r['reviewed_browse_home'] and int(r['rank']) <= 2000 for r in updated),
                   Top500_unresolved=sum(not r['reviewed_browse_home'] and int(r['rank']) <= 500 for r in updated),
                   wiki_pages_reused=len(source['cached_pages']), bulk_request_count=len(source['bulk_requests']),
                   exact_own_pages=len(pages), nonempty_own_pages=sum(bool(r['body']) for r in pages.values()),
                   input_sha256={n: hashlib.sha256((D / n).read_bytes()).hexdigest() for n in ['REVIEWED_BROWSE_HOME_V1.csv', 'BROWSE_ARTIST_REVIEW_WIKI_INPUTS_V1.json.gz', 'PROVISIONAL_BROWSE_HOME_INPUTS_V1.csv', 'COPYRIGHT_ROOTS_V1.csv']},
                   formal_authority_eligible=False)
    (D / 'BROWSE_ARTIST_QUALIFIER_CHECKPOINT_V1.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
