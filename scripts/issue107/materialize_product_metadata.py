#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

LABELS = {
'presenting_own_armpit':'自分の腋を見せる','breast_curtains':'胸カーテン','condom_in_mouth':'口にコンドーム','perky_breasts':'張りのある胸','sweaty_armpits':'汗ばんだ腋','veiny_breasts':'血管の浮いた胸','breasts_on_glass':'ガラスに押し付けた胸','armpit_focus':'腋フォーカス','face_to_breasts':'顔を胸に当てる','sweaty_breasts':'汗ばんだ胸','pointless_condom':'無意味なコンドーム','single_breast_curtain':'片胸カーテン','viewer_holding_leash':'視点人物がリードを持つ','breasts_on_head':'頭に胸を乗せる','stained_panties':'汚れたパンツ','pointy_breasts':'尖った胸',"hand_in_another's_panties":'他人のパンツに手を入れる','futa_without_balls':'睾丸なしふたなり','light_areolae':'薄い色の乳輪','straitjacket':'拘束衣','speckled_areolae':'斑点のある乳輪','handsfree_breast_squeeze':'手を使わない胸の圧迫','covering_one_breast':'片胸を隠す','breast_milk_in_container':'容器に母乳','pov_breasts':'一人称視点の胸','male_with_breasts':'胸のある男性',"poking_another's_breast":'他人の胸をつつく','viewer_on_leash':'視点人物がリードにつながれている','dark_areolae':'濃い色の乳輪','breast_zipper':'胸ジッパー','breast_pillow':'胸まくら','extended_downblouse':'深い胸元覗き','buttjob_over_clothes':'服越しの尻コキ','sweaty_feet':'汗ばんだ足','rope_around_neck':'首にロープ','condom_thigh_strap':'太もものコンドームストラップ','rope_marks':'縄痕','upright_restraints':'直立拘束','male_underwear_aside':'男性下着ずらし','wet_male_underwear':'濡れた男性下着','asymmetrical_breasts':'左右非対称の胸','used_condom_in_clothes':'服の中の使用済みコンドーム','condom_wrapper_in_clothes':'服の中のコンドーム包装','breast_drop':'胸ポロリ','extreme_gaping':'極端に開いた肛門','groping_motion':'揉むジェスチャー','extra_breasts':'余分な乳房','electrostimulation':'電気刺激','breast_size_difference':'胸のサイズ差','saliva_on_breasts':'胸に唾液','saliva_swap':'唾液交換','smelly_armpits':'臭い腋','smelling_armpit':'腋の匂いを嗅ぐ','powerful_breasts':'強力な胸','broken_condom':'破れたコンドーム','sabotaged_condom':'細工されたコンドーム','breast_on_breast':'胸同士を重ねる','cooperative_buttjob':'複数人で尻コキ',"covering_another's_breasts":'他人の胸を隠す','mole_on_areola':'乳輪のほくろ','shared_handcuffs':'二人で同じ手錠','tickling_breasts':'胸をくすぐる','shackle_piercing':'シャックルピアス','intestine_clothing':'腸でできた衣服',"feet_on_another's_face":'他人の顔に足を乗せる','breast_massage':'胸マッサージ','extended_upskirt':'奥まで見えるアップスカート','buttjob_under_clothes':'服の下で尻コキ','condom_pull':'コンドームを引っ張る',"unzipping_another's_clothes":'他人の服のファスナーを下ろす','standing_restraints':'立ち姿で拘束','slapping_breasts':'胸を叩く','offering_leash':'リードを差し出す','drinking_from_condom':'コンドームから飲む','kissing_breast':'胸にキス','uterus_pose':'子宮ポーズ','single_breast':'片方だけの胸','cospussy':'コスプッシー','areola_measuring':'乳輪を測る','cunt_punt':'女性器を蹴る','breast_reduction':'乳房縮小','female_fertilization':'女性の受精','open-chest_straitjacket':'胸が開いた拘束衣',"foot_on_another's_breast":'他人の胸に足を乗せる','condom_on_ass':'尻の上にコンドーム','lube_on_breasts':'胸に潤滑剤','breast_size_switch':'胸サイズ入れ替え','breast_pull':'胸を引っ張る','putting_on_condom':'コンドームを装着する','face_in_armpit':'顔を腋にうずめる','slapping_with_breasts':'胸で叩く','weighing_breasts':'胸の重さを量る','artificial_insemination':'人工授精','compressed_breasts':'圧迫された胸','shibarikini':'縛りビキニ','breasts_on_thighs':'太ももの上に胸','condom_in_ass':'尻にコンドーム','condom_on_tongue':'舌の上にコンドーム','breast_punch':'胸を殴る','fluid_on_breasts':'胸に液体','breast_implants':'豊胸インプラント','breast_crush':'胸を押し潰す','breast_shake':'胸を揺らす','implied_egg_laying':'産卵を示唆','tied_breast':'乳房縛り'
}

SEARCH_EXTRA = {
'presenting_own_armpit':['腋見せ','脇見せ','自分の脇を見せる'],'breast_curtains':['乳房カーテン'],'condom_in_mouth':['口内コンドーム'],'perky_breasts':['上向きの胸','張った胸'],'sweaty_armpits':['汗ばんだ脇','脇汗'],'veiny_breasts':['胸の血管'],'armpit_focus':['脇フォーカス','腋アップ'],'pointless_condom':['役に立たないコンドーム'],'stained_panties':['汚れパンツ','染み付きパンツ'],'pointy_breasts':['尖った乳房'],'futa_without_balls':['タマなしふたなり','睾丸のないふたなり'],'straitjacket':['ストレートジャケット'],'breast_milk_in_container':['容器の母乳','搾乳容器'],'male_with_breasts':['男性の胸','乳房のある男性'],'breast_zipper':['乳房ジッパー'],'extended_downblouse':['胸元を深く覗く','ダウンブラウス'],'buttjob_over_clothes':['着衣尻コキ'],'sweaty_feet':['足汗'],'rope_around_neck':['首縄'],'rope_marks':['縄の跡','縛り跡'],'upright_restraints':['立位拘束'],'male_underwear_aside':['男性下着をずらす'],'wet_male_underwear':['濡れた男物下着'],'breast_drop':['胸がこぼれる','乳房がこぼれる'],'extreme_gaping':['極端な肛門開き','大きく開いた肛門'],'groping_motion':['揉む手つき','胸を揉むジェスチャー'],'extra_breasts':['複数乳房','多乳房'],'electrostimulation':['電気責め'],'saliva_swap':['唾交換'],'smelly_armpits':['臭い脇'],'smelling_armpit':['脇の匂いを嗅ぐ'],'broken_condom':['破損コンドーム'],'sabotaged_condom':['穴を開けたコンドーム'],'shared_handcuffs':['共有手錠'],'shackle_piercing':['枷ピアス'],'intestine_clothing':['腸の服','内臓衣装'],"feet_on_another's_face":['顔に足','他人の顔を踏む'],'extended_upskirt':['深いアップスカート'],'offering_leash':['リードを渡す'],'uterus_pose':['子宮ポーズ構図'],'cospussy':['コスプレ女性器'],'cunt_punt':['股間を蹴る','女性器キック'],'breast_reduction':['胸が縮む','乳房を小さくする'],'female_fertilization':['女性受精'],'open-chest_straitjacket':['胸開き拘束衣'],'condom_on_ass':['お尻にコンドーム'],'breast_size_switch':['胸サイズ交換'],'putting_on_condom':['コンドーム装着'],'face_in_armpit':['顔を脇にうずめる'],'artificial_insemination':['人工受精'],'shibarikini':['縄ビキニ','緊縛ビキニ'],'condom_in_ass':['お尻にコンドーム','尻の間のコンドーム'],'implied_egg_laying':['産卵示唆','産卵を暗示'],'tied_breast':['胸縛り','乳房拘束']
}

BODY_BREAST = {t for t in LABELS if 'breast' in t or 'areola' in t}
BODY_BUTTOCK = {'buttjob_over_clothes','buttjob_under_clothes','cooperative_buttjob','extreme_gaping','condom_on_ass','condom_in_ass'}
BODY_MOUTH = {'condom_in_mouth','condom_on_tongue','drinking_from_condom','saliva_swap'}
BODY_FEMALE = {'cospussy','cunt_punt','female_fertilization'}
BODY_MALE = {'pointless_condom','broken_condom','sabotaged_condom','condom_pull','putting_on_condom'}

THEME_BDSM = {'viewer_holding_leash','viewer_on_leash','straitjacket','breast_zipper','rope_around_neck','rope_marks','upright_restraints','electrostimulation','shared_handcuffs','shackle_piercing','standing_restraints','offering_leash','open-chest_straitjacket','shibarikini','tied_breast'}
THEME_REPRO = {'breast_milk_in_container','uterus_pose','female_fertilization','artificial_insemination','implied_egg_laying'}
THEME_R18G = {'intestine_clothing','cunt_punt','breast_punch','breast_crush'}

K_BODY = {'perky_breasts','sweaty_armpits','veiny_breasts','sweaty_breasts','pointy_breasts','futa_without_balls','light_areolae','speckled_areolae','male_with_breasts','dark_areolae','sweaty_feet','rope_marks','asymmetrical_breasts','extreme_gaping','extra_breasts','breast_size_difference','smelly_armpits','powerful_breasts','mole_on_areola','single_breast','cospussy','breast_reduction','compressed_breasts','breast_implants'}
K_CLOTHING = {'breast_curtains','stained_panties','covering_one_breast','extended_downblouse','male_underwear_aside','wet_male_underwear','used_condom_in_clothes','condom_wrapper_in_clothes','breast_drop','intestine_clothing','extended_upskirt',"unzipping_another's_clothes"}
K_POSE = {'presenting_own_armpit','armpit_focus','viewer_holding_leash','pov_breasts','viewer_on_leash','upright_restraints','standing_restraints','uterus_pose'}
K_TOOL = {'condom_in_mouth','pointless_condom','straitjacket','breast_zipper','rope_around_neck','condom_thigh_strap','electrostimulation','broken_condom','sabotaged_condom','shared_handcuffs','shackle_piercing','open-chest_straitjacket','condom_on_ass','shibarikini','condom_in_ass','condom_on_tongue'}
K_FLUID = {'breast_milk_in_container','saliva_on_breasts','saliva_swap','lube_on_breasts','fluid_on_breasts'}
K_NONHUMAN = {'implied_egg_laying'}
K_ACTION = set(LABELS) - K_BODY - K_CLOTHING - K_POSE - K_TOOL - K_FLUID - K_NONHUMAN

G_BODY_ATTRIBUTE = {'perky_breasts','veiny_breasts','pointy_breasts','futa_without_balls','light_areolae','speckled_areolae','male_with_breasts','dark_areolae','asymmetrical_breasts','extra_breasts','breast_size_difference','mole_on_areola','single_breast','cospussy','breast_implants'}
G_BODY_STATE = K_BODY - G_BODY_ATTRIBUTE
G_CLOTHING = K_CLOTHING - {'intestine_clothing'}
G_FLUID = K_FLUID
G_RESTRAINT_IMPLEMENT = {'straitjacket','breast_zipper','rope_around_neck','shared_handcuffs','shackle_piercing','open-chest_straitjacket','shibarikini','tied_breast'}
G_RESTRAINT_ACTION = {'viewer_holding_leash','viewer_on_leash','upright_restraints','standing_restraints','offering_leash','electrostimulation'}
G_IMPLEMENT = {'pointless_condom','condom_thigh_strap','broken_condom','sabotaged_condom'}
G_POSE = {'presenting_own_armpit','armpit_focus','pov_breasts','uterus_pose'}
G_CONTEXT = {'implied_egg_laying'}
G_DAMAGE = {'intestine_clothing','cunt_punt','breast_punch','breast_crush'}
G_DIRECT_COMPOSITE = {'condom_in_mouth','breasts_on_glass','face_to_breasts','breasts_on_head','condom_on_ass','condom_in_ass','condom_on_tongue',"foot_on_another's_breast",'breasts_on_thighs',"feet_on_another's_face"}
G_ACTION = set(LABELS) - G_BODY_ATTRIBUTE - G_BODY_STATE - G_CLOTHING - G_FLUID - G_RESTRAINT_IMPLEMENT - G_RESTRAINT_ACTION - G_IMPLEMENT - G_POSE - G_CONTEXT - G_DAMAGE - G_DIRECT_COMPOSITE


def read_csv(path: Path):
    with path.open('r', encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))

def hash_file(path: Path): return hashlib.sha256(path.read_bytes()).hexdigest()

def browse_kind(tag: str) -> str:
    groups=[('BODY_STATE',K_BODY),('CLOTHING_EXPOSURE',K_CLOTHING),('POSE_SCENE',K_POSE),('TOOL_OBJECT',K_TOOL),('FLUID_EXCRETION',K_FLUID),('NONHUMAN_TRANSFORMATION',K_NONHUMAN),('ACTION_CONTACT',K_ACTION)]
    hits=[k for k,s in groups if tag in s]
    if len(hits)!=1: raise ValueError(f'browse kind partition error {tag}: {hits}')
    return hits[0]

def body_sites(tag: str) -> str:
    vals=[]
    for name,group in [('BREAST_NIPPLE',BODY_BREAST),('BUTTOCK_ANAL',BODY_BUTTOCK),('MOUTH_ORAL',BODY_MOUTH),('FEMALE_GENITAL',BODY_FEMALE),('MALE_GENITAL',BODY_MALE)]:
        if tag in group: vals.append(name)
    return '|'.join(vals)

def themes(tag: str) -> str:
    vals=[]
    for name,group in [('BDSM_RESTRAINT',THEME_BDSM),('REPRO_PREGNANCY_LACTATION',THEME_REPRO),('INJURY_R18G',THEME_R18G)]:
        if tag in group: vals.append(name)
    return '|'.join(vals)

def generation(tag: str):
    groups=[
        (G_BODY_ATTRIBUTE,('BODY_ATTRIBUTE','body_target_or_attribute','DIRECT','GFR_BODY_ATTRIBUTE')),
        (G_BODY_STATE,('BODY_STATE','body_state','DIRECT','GFR_BODY_STATE')),
        (G_CLOTHING,('CLOTHING_EXPOSURE','visual_state','DIRECT','GFR_CLOTHING_EXPOSURE')),
        (G_FLUID,('FLUID_STATE_ACTION','effect_or_action','DIRECT','GFR_FLUID_STATE_ACTION')),
        (G_RESTRAINT_IMPLEMENT,('RESTRAINT_IMPLEMENT','restraint_implement','DIRECT','GFR_RESTRAINT_IMPLEMENT')),
        (G_RESTRAINT_ACTION,('RESTRAINT_ACTION','restraint_action','STRUCTURED','GFR_RESTRAINT_ACTION')),
        (G_IMPLEMENT,('IMPLEMENT_OBJECT','implement','DIRECT','GFR_IMPLEMENT_OBJECT')),
        (G_POSE,('POSE_COMPOSITION','pose_camera','STRUCTURED','GFR_POSE_COMPOSITION')),
        (G_CONTEXT,('CONTEXT_MODIFIER','temporal_or_implied_context','SUPPORT','GFR_CONTEXT_MODIFIER')),
        (G_DAMAGE,('DAMAGE_STATE_ACTION','state_or_action','STRUCTURED','GFR_DAMAGE_STATE_ACTION')),
        (G_DIRECT_COMPOSITE,('DIRECT_COMPOSITE','spatial_relation','STRUCTURED','GFR_DIRECT_COMPOSITE')),
        (G_ACTION,('ACTION_INTERACTION','action','STRUCTURED','GFR_ACTION_INTERACTION')),
    ]
    hits=[meta for group,meta in groups if tag in group]
    if len(hits)!=1: raise ValueError(f'generation partition error {tag}: {hits}')
    return hits[0]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--preflight',required=True); ap.add_argument('--out-dir',required=True); args=ap.parse_args()
    source=read_csv(Path(args.preflight)); tags=[r['canonical_tag'] for r in source]
    if len(source)!=105 or len(set(tags))!=105: raise ValueError('expected 105 unique preflight rows')
    if set(tags)!=set(LABELS):
        raise ValueError(f'Japanese metadata set mismatch missing={sorted(set(tags)-set(LABELS))} extra={sorted(set(LABELS)-set(tags))}')
    browse_groups=[K_BODY,K_CLOTHING,K_POSE,K_TOOL,K_FLUID,K_NONHUMAN,K_ACTION]
    if set().union(*browse_groups)!=set(tags) or sum(len(g) for g in browse_groups)!=105: raise ValueError('browse partition does not form an exact disjoint source partition')
    gen_groups=[G_BODY_ATTRIBUTE,G_BODY_STATE,G_CLOTHING,G_FLUID,G_RESTRAINT_IMPLEMENT,G_RESTRAINT_ACTION,G_IMPLEMENT,G_POSE,G_CONTEXT,G_DAMAGE,G_DIRECT_COMPOSITE,G_ACTION]
    if set().union(*gen_groups)!=set(tags) or sum(len(g) for g in gen_groups)!=105: raise ValueError('generation partition does not form an exact disjoint source partition')

    out=[]
    for r in source:
        tag=r['canonical_tag']; fam,role,mode,rule=generation(tag)
        ja=[]
        for value in [LABELS[tag],*SEARCH_EXTRA.get(tag,[])]:
            if value and value not in ja: ja.append(value)
        row=dict(r); row.update({
            'display_ja':LABELS[tag], 'search_ja':'|'.join(ja),
            'kind_id':browse_kind(tag), 'body_site_ids':body_sites(tag), 'theme_ids':themes(tag),
            'generation_family':fam, 'generation_role':role, 'prompt_use_mode':mode, 'family_rule_id':rule,
            'metadata_status':'HUMAN_BOUNDED_RESOLVED'
        }); out.append(row)
    fields=list(out[0].keys()); root=Path(args.out_dir); root.mkdir(parents=True,exist_ok=True)
    path=root/'promotion_metadata_v1.csv'
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
    summary={
        'rows':len(out), 'ids':[int(out[0]['proposed_special_id']),int(out[-1]['proposed_special_id'])],
        'kind_counts':dict(sorted(Counter(r['kind_id'] for r in out).items())),
        'body_facet_counts':dict(sorted(Counter(v for r in out for v in r['body_site_ids'].split('|') if v).items())),
        'theme_counts':dict(sorted(Counter(v for r in out for v in r['theme_ids'].split('|') if v).items())),
        'generation_family_counts':dict(sorted(Counter(r['generation_family'] for r in out).items())),
        'source_sha256':hash_file(Path(args.preflight)), 'metadata_sha256':hash_file(path),
        'unresolved_rows':0, 'hidden_prompt_insertion':'NO','content_filter_used':'NO','production_mutation':'NO','issue70_mutated':'NO','userdata_mutated':'NO'
    }
    (root/'promotion_metadata_summary_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
