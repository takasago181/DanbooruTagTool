#!/usr/bin/env python3
"""Bounded three-way residual Browse sorting; no formal authority writes."""
import csv
import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parents[2] / 'docs/issue216'
BASE = '96c70ad822ef1db319c1639aebff98c77978e68d'
GENERIC = {'', 'original', 'indie_virtual_youtuber', 'real_life', 'virtual_youtuber'}
NONWORK_ROOTS = GENERIC | {'cookie_(touhou)', 'indie_utaite', 'manatsu_no_yo_no_inmu',
    'minecraft_youtube', 'japanese_urban_legends', '2channel', 'niconico', 'twitch.tv',
    'pixiv', 'muppets', 'vedal_ai', 'vrchat', 'fromsoftware', 'namco', 'cygames', 'nintendo'}
AVATAR_ROOTS = {'vshojo', 'phase_connect', 'nijisanji', 'hololive', 'holostars', 'sana_channel',
    'kizuna_ai_inc.', 'vinesauce', '3am', 'voms', 'chromashift', 'nanashi_inc.', 'cloud9',
    'vspo!', 'densetsu.exe', 'v-dere', 'plivyou'}
NONWORK_SUBJECTS = set('''mishaguji santa_claus sakurai_masahiro vedal987 mii_(nintendo)
death_(entity) hasshaku-sama technoblade yagoo yajuu_senpai grim_reaper marichka
nessie_(respawn) naplings_(nimi_nightmare) kaniki_(sameko_saba)
'''.split())
CHOICES = {
    'monika_weisswind': 'shingeki_no_bahamut',
    'monika_weisswind_(magical_girl)': 'shingeki_no_bahamut',
    'king_(snk)': 'ryuuko_no_ken', 'sumeragi_aika': 'aika_(series)',
    'aida_rion': 'aika_(series)', 'aoki_kei': 'idolmaster_cinderella_girls',
    'nidoran_(male)': 'pokemon', 'nidoran_(female)': 'pokemon',
    'zundamon_(utau)': 'utau', 'hyper_roll_(marvel_vs._capcom)': 'mega_man_(classic)',
    'gekota_(character)': 'toaru_majutsu_no_index', 'pyonko_(toaru)': 'toaru_majutsu_no_index',
    'beliora_vike': 'zenless_zone_zero', 'roxy_ifrita_pryce': 'zenless_zone_zero',
    'hades_izanami': 'blazblue', 'he_mingshuo': 'false_memory', 'protagonist_halo': 'false_memory',
    'izumi_shirogane': 'under_night_in-birth', 'izumida_kyoka': 'hachigatsu_no_cinderella_nine',
    'kondo_saki': 'hachigatsu_no_cinderella_nine', 'kosaka_tsubaki': 'hachigatsu_no_cinderella_nine',
    'lin_lihua': 'hachigatsu_no_cinderella_nine', 'nikaido_reika': 'akatsuki_no_goei',
    'princess_lady_serenity': 'bishoujo_senshi_sailor_moon',
    'qiang_lei_(kingdom)': 'kingdom_(manga)', 'shantak-kun_(nyaruko-san)': 'haiyore!_nyaruko-san',
    'simon_jackson': 'cytus_ii', 't._hawk': 'street_fighter',
    'takamiya_subaru': 'choukou_(alicesoft)', 'gyoro_(so2)': 'star_ocean',
    'ururun_(so2)': 'star_ocean', 'hob_&_nob': 'wild_arms',
    'chainsaw_man_(character)': 'chainsaw_man', 'cure_arcana': 'precure', 'eclipse_shadow': 'precure',
    'petra_parker_(otrebot)': 'marvel', "marche_lorraine's_puppet": 'umamusume',
    'shadow_giant': 'fate_(series)', 'angelica_ainsworth': 'fate/kaleid_liner_prisma_illya',
    'ort_(type-moon)': 'fate_(series)',
    'yuzuki_yukari_(onn)': 'vocaloid', 'yuzuki_yukari_(lin)': 'vocaloid',
    'yuzuki_yukari_(vocaloid6)': 'vocaloid', 'hanakuma_chifuyu_(sv)': 'synthesizer_v',
    'gogeta_(xeno)': 'dragon_ball', 'super_sailor_chibi_moon_(stars)': 'bishoujo_senshi_sailor_moon',
    'lady_labrynth_of_the_silver_castle_(alternate_art)': 'yu-gi-oh!',
    'kaito_(rei_no_sakura_sousetsu)_(vocaloid)': 'vocaloid', 'gelgoog_(gquuuuuux)': 'gundam',
    'megatron_(idw)': 'transformers', 'vrtra_(final_fantasy)': 'final_fantasy_xiv',
    'nagase_minato': 'akane-iro_ni_somaru_saka', 'kuma-tan': 'kumatanchi',
    'squidward_tentacles': 'spongebob_squarepants_(series)',
}
# Clearly recognizable empty/short-page named forms, reviewed as a shared family.
# These are provisional Browse judgments, not validated VARIANT_OF additions.
CLEAR_SHORT_FORMS = set('''nobeta_(witch_skin) hoshino_ruri_(captain)
ayase_momo_(gyaru_combat_style) indou_hikaru_(human) ernesto_de_la_cruz_(alive)
psylocke_(blood_kariudo) charlotte_wiltshire_(q84) marceline_abadeer_(what_was_missing)
rouge_the_bat_(riders) amity_blight_(timeskip) luz_noceda_(timeskip)
kusanagi_motoko_(1995) kusanagi_motoko_(2026) isoi_reiji_(rei-kun)
'''.split())


def read(name):
    with (D / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (D / name).open('w', encoding='utf-8', newline='') as f:
        out = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        out.writeheader(); out.writerows(rows)


def main():
    old = read('REVIEWED_BROWSE_HOME_V2.csv')
    subjects = [r for r in old if r['review_pattern'] == 'NO_OBVIOUS_ADDITIONAL_CLASSIFICATION']
    assert len(subjects) == 1278 and all(not r['reviewed_browse_home'] for r in subjects)
    inputs = {r['character']: r for r in read('PROVISIONAL_BROWSE_HOME_INPUTS_V1.csv')}
    hints = {r['character']: r for r in read('PROVISIONAL_BROWSE_HOME_AUDIT_HINTS_V1.csv')}
    homes = {r['character']: r['reviewed_browse_home'] for r in old if r['reviewed_browse_home']}
    roots = {r['copyright_canonical'] for r in read('COPYRIGHT_ROOTS_V1.csv')}
    source = json.loads(gzip.decompress((D / 'BROWSE_RESIDUAL_REVIEW_WIKI_INPUTS_V1.json.gz').read_bytes()))
    assert set(source['subjects']) == {r['character'] for r in subjects}
    pages = {r['title']: r for r in source['cached_pages']}
    for batch in source['bulk_requests']:
        assert all(r['title'] in batch['requested_tags'] for r in batch['pages'])
        pages.update({r['title']: r for r in batch['pages']})
    reviewed = []
    for row in subjects:
        t = row['character']; i = inputs[t]; h = hints[t]; p = pages.get(t, {})
        body = p.get('body', '').replace('\r', ''); intro = body.split('\n\n')[0]
        links = {x.lower().replace(' ', '_') for x in re.findall(r'\[\[([^]|]+)(?:\|[^]]*)?\]\]', intro)}
        candidates = set(i['candidate_roots'].split(' | '))
        base = i['variant_base']; bh = homes.get(base, '') or h['variant_base_home']
        category = 'OTHER_AMBIGUOUS'; pattern = 'INSUFFICIENT_SUBJECT_CONTEXT'; home = ''
        reason = 'No clear unique origin in the bounded available context.'
        avatar = (candidates & AVATAR_ROOTS or bh in AVATAR_ROOTS or re.search(r'virtual.?youtuber|\bVTuber\b|self.insert|streamer|artist avatar|self.portrait', intro, re.I) or '(vtuber)' in t)
        oc = re.search(r'\bOC\b|original character|\[\[original(?:\|[^]]+)?\]\].{0,120}character|commissioner insert|character (?:created|belonging).*\[\[', intro, re.I)
        person = re.search(r'^.{0,45}(?:game designer|CEO|musician|voice actor|voice actress|software developer)|^Voice of\b', intro, re.I)
        concept = re.search(r'\[\[meme\]\]|legendary figure|any recognizable personification|gods in .*folktales', intro, re.I)
        if avatar or oc or person or concept or t in NONWORK_SUBJECTS or candidates == {'real_life'}:
            category = 'AVATAR_CONCEPT_NONWORK'; pattern = 'AVATAR_OC_PERSON_OR_CONCEPT'
            reason = 'Avatar/person/creator OC/general concept context; keep unresolved rather than use an associated work.'
        elif t in CHOICES or base and bh in roots and bh not in AVATAR_ROOTS | NONWORK_ROOTS or candidates - AVATAR_ROOTS - NONWORK_ROOTS or re.search(r'character (?:from|in)|playable character', intro, re.I):
            category = 'WORK_CHARACTER_LIKE'; pattern = 'WORK_ROUTE_REVIEW_NO_CLEAR_HOME'
            reason = 'Work route is plausible; candidate alone is not enough to assign Browse HOME.'
            if t in CHOICES:
                home = CHOICES[t]; pattern = 'REVIEWED_EXPLICIT_ORIGIN_OR_NAMED_CHARACTER'
            elif re.search(r'voicebank|vocal database|VOCALOID', intro, re.I) and links & {'a.i._voice', 'cevio', 'vocaloid', 'synthesizer_v', 'voicepeak', 'gynoid_talk'}:
                engines = links & {'a.i._voice', 'cevio', 'vocaloid', 'synthesizer_v', 'voicepeak', 'gynoid_talk'}
                if len(engines) == 1:
                    home = next(iter(engines)); pattern = 'EXPLICIT_NAMED_VOICEBANK_ECOSYSTEM'
            elif base and bh in roots and bh not in AVATAR_ROOTS | NONWORK_ROOTS and (base in links or t in CLEAR_SHORT_FORMS):
                home = bh; pattern = 'NAMED_FORM_OR_COSTUME_BASE_CONTEXT'
                if base.startswith(('symphony_', 'racing_miku', 'gramophone_miku')):
                    home = 'vocaloid'
                reason = f'Named base={base}; saved Browse context={bh}; guest/event destinations are excluded.'
            elif re.search(r'character (?:from|in)|playable character|\]\].{0,8}character\b', intro, re.I):
                worklinks = links & roots - NONWORK_ROOTS - AVATAR_ROOTS
                if len(worklinks) == 1 and not re.search(r'collab|guest|cosplay|original character', intro, re.I):
                    home = next(iter(worklinks)); pattern = 'EXPLICIT_UNIQUE_WORK_DESCRIPTION'
            if home and pattern != 'NAMED_FORM_OR_COSTUME_BASE_CONTEXT':
                reason = 'Light group review establishes recognizable origin/brand context, not guest, collab or event HOME.'
        if home:
            assert home in roots, (t, home)
            assert category == 'WORK_CHARACTER_LIKE'
        reviewed.append(dict(character=t, classification=category, browse_home=home, review_pattern=pattern,
            reason=reason, evidence_excerpt=' '.join(intro.split())[:850], source_url=f"https://danbooru.donmai.us/wiki_pages/{p['id']}" if p else '',
            base_character=base, base_browse_context=bh, rank=row['rank'], formal_authority_eligible='NO'))
    bytag = {r['character']: r for r in reviewed}; updated = []
    for row in old:
        r = dict(row); v = bytag.get(r['character'])
        if v:
            home = v['browse_home']
            r.update(previous_audited_home=row['reviewed_browse_home'], reviewed_browse_home=home,
                review_state='REVIEWED_BROWSE_HOME' if home else 'REVIEWED_UNRESOLVED', action='ADD' if home else 'KEEP',
                confidence='MEDIUM' if home else 'LOW', review_pattern=v['review_pattern'], review_note=v['reason'], source_url=v['source_url'])
        updated.append(r)
    assert len(updated) == len({r['character'] for r in updated}) == 10102
    write('BROWSE_RESIDUAL_THREE_WAY_REVIEW_V1.csv', reviewed)
    write('REVIEWED_BROWSE_HOME_V3.csv', updated)
    groups = Counter((r['classification'], r['review_pattern'], r['browse_home']) for r in reviewed)
    write('BROWSE_RESIDUAL_REVIEW_GROUPS_V1.csv', [dict(classification=k[0], pattern=k[1], browse_home=k[2], count=v) for k, v in sorted(groups.items())])
    summary = dict(base_commit=BASE, inspected=1278, classification_counts=dict(Counter(r['classification'] for r in reviewed)),
        browse_home_additions=sum(bool(r['browse_home']) for r in reviewed),
        reviewed_browse_home=sum(bool(r['reviewed_browse_home']) for r in updated), unresolved=sum(not r['reviewed_browse_home'] for r in updated),
        Top2000_reduction=sum(bool(r['browse_home']) and int(r['rank']) <= 2000 for r in reviewed),
        Top2000_unresolved=sum(not r['reviewed_browse_home'] and int(r['rank']) <= 2000 for r in updated),
        Top500_unresolved=sum(not r['reviewed_browse_home'] and int(r['rank']) <= 500 for r in updated),
        wiki_pages_reused=len(source['cached_pages']), bulk_request_count=len(source['bulk_requests']), exact_own_pages=len(pages),
        input_sha256={n: hashlib.sha256((D / n).read_bytes()).hexdigest() for n in ['REVIEWED_BROWSE_HOME_V2.csv', 'BROWSE_RESIDUAL_REVIEW_WIKI_INPUTS_V1.json.gz', 'PROVISIONAL_BROWSE_HOME_INPUTS_V1.csv', 'PROVISIONAL_BROWSE_HOME_AUDIT_HINTS_V1.csv', 'COPYRIGHT_ROOTS_V1.csv']},
        formal_authority_eligible=False)
    (D / 'BROWSE_RESIDUAL_REVIEW_CHECKPOINT_V1.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
