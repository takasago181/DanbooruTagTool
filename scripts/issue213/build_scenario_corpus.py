"""Build the immutable Issue #213 scenario ledger from checked-in intents."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(os.environ.get("DTT_ISSUE213_CATALOG", r"C:\Codex\DanbooruTagTool-App\Data\catalog.db"))
OUT = ROOT / "docs" / "issue213" / "scenarios.json"

# Each tuple is (target, Japanese intent, Japanese query, family, route, body, theme, deep).
# Queries are written as user intent; the canonical target is never copied into the query.
SEXUAL = [
    ("breast_sucking", "口を使って胸を愛撫する場面", "胸に口を寄せる", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "", False),
    ("paizuri", "胸の間で相手を刺激する構図", "胸の間に相手を挟む", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "", False),
    ("cooperative_paizuri", "二人で胸を使う行為をしている場面", "二人で胸を使った行為", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "", True),
    ("breast_sucking_through_clothes", "服越しに胸へ口を寄せている", "服の上から胸を愛撫", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "", True),
    ("breast_on_breast", "二人の胸が触れ合う場面", "胸同士を押し当てる", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "", True),
    ("nipple_stimulation", "乳首を重点的に刺激する場面", "乳首を刺激する", "breast", "BODY_SITE", "BREAST_NIPPLE", "", True),
    ("nipple_clamps", "乳首に器具を付けた拘束表現", "乳首に留め具を付ける", "breast", "TOOL_OBJECT", "BREAST_NIPPLE", "BDSM_RESTRAINT", True),
    ("nipple_chain", "乳首から鎖をつないだ衣装や拘束", "胸元の鎖で拘束", "breast", "TOOL_OBJECT", "BREAST_NIPPLE", "BDSM_RESTRAINT", True),
    ("breast_bondage", "胸を布や縄で縛った姿", "胸を縛っている", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "BDSM_RESTRAINT", True),
    ("nipple_tweak", "指で乳首をつまむ接触", "指で乳首をつまむ", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "", True),
    ("grabbing_another's_breast", "相手の胸を手でつかむ", "相手の胸を手でつかむ", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "", False),
    ("breast_focus", "人物の顔より胸を画面の主役にしたい", "胸を画面の中心に寄せる", "composition", "COMPOSITION_CAMERA", "BREAST_NIPPLE", "", False),
    ("fellatio", "口を使って相手を刺激する場面", "口で相手を愛撫する", "oral", "ACTION_CONTACT", "MOUTH_ORAL", "", False),
    ("cunnilingus", "女性器へ口を寄せる場面", "口で下半身を愛撫", "oral", "ACTION_CONTACT", "MOUTH_ORAL", "", False),
    ("anilingus", "尻側へ口を寄せる接触", "後ろ側に口を寄せる", "oral", "ACTION_CONTACT", "MOUTH_ORAL", "", True),
    ("irrumatio", "相手が主導して口を使わせる場面", "相手に口を使わせる", "oral", "ACTION_CONTACT", "MOUTH_ORAL", "", True),
    ("deepthroat", "口の奥まで含めた強い口の行為", "口の奥まで含めた行為", "oral", "ACTION_CONTACT", "MOUTH_ORAL", "", True),
    ("oral_sandwich", "複数人が口で同じ相手を挟む構図", "二人で相手を挟んで口を使う", "oral", "ACTION_CONTACT", "MOUTH_ORAL", "", True),
    ("oral_invitation", "口での行為を誘う仕草", "口での行為に誘う仕草", "oral", "ACTION_CONTACT", "MOUTH_ORAL", "", True),
    ("standing_cunnilingus", "立った姿勢で下半身へ口を寄せる", "立ったまま口で愛撫", "oral", "POSE_POSITION", "MOUTH_ORAL", "", True),
    ("cooperative_fellatio", "複数人で口を使う側を分担する", "複数人で口を使う行為", "oral", "ACTION_CONTACT", "MOUTH_ORAL", "", True),
    ("anal", "後ろ側を使う挿入行為", "後ろ側への挿入", "anal", "ACTION_CONTACT", "BUTTOCK_ANAL", "", False),
    ("anal_fingering", "指で肛門を刺激する", "指で後ろ側を刺激", "anal", "ACTION_CONTACT", "BUTTOCK_ANAL", "", True),
    ("anal_fisting", "手を使う強い肛門刺激", "手を使った後ろ側の刺激", "anal", "ACTION_CONTACT", "BUTTOCK_ANAL", "", True),
    ("spread_anus", "肛門を見せるように開いた構図", "後ろ側を開いて見せる", "anal", "BODY_SITE", "BUTTOCK_ANAL", "", True),
    ("presenting_own_anus", "本人が後ろ側を見せるポーズ", "自分の後ろ側を見せる", "anal", "POSE_POSITION", "BUTTOCK_ANAL", "", True),
    ("anal_object_insertion", "肛門に器具を挿入する場面", "後ろ側に器具を入れる", "anal", "ACTION_CONTACT", "BUTTOCK_ANAL", "", True),
    ("ass-to-mouth", "尻を口元へ近づける構図", "尻を相手の口元へ寄せる", "anal", "ACTION_CONTACT", "BUTTOCK_ANAL", "", True),
    ("anal_beads", "後ろ側に連なる珠状の器具を使う", "後ろ側に連なる器具", "anal", "TOOL_OBJECT", "BUTTOCK_ANAL", "", True),
    ("double_anal", "二つの挿入物を使う後ろ側の行為", "同時に二つ使う後ろ側の行為", "anal", "ACTION_CONTACT", "BUTTOCK_ANAL", "", True),
    ("vaginal", "女性器を使った挿入行為", "前側への挿入", "female_genital", "ACTION_CONTACT", "FEMALE_GENITAL", "", False),
    ("fingering", "指で女性器を刺激する", "指で下半身を刺激", "female_genital", "ACTION_CONTACT", "FEMALE_GENITAL", "", False),
    ("clitoral_stimulation", "クリトリスを重点的に刺激する", "特定の部位を指で刺激", "female_genital", "ACTION_CONTACT", "FEMALE_GENITAL", "", True),
    ("spread_pussy", "女性器を見せるように開いた構図", "下半身を開いて見せる", "female_genital", "BODY_SITE", "FEMALE_GENITAL", "", True),
    ("presenting_own_pussy", "本人が女性器を見せるポーズ", "自分の下半身を見せる", "female_genital", "POSE_POSITION", "FEMALE_GENITAL", "", True),
    ("labia_clamps", "女性器のひだに器具を付ける", "下半身に小さな留め具", "female_genital", "TOOL_OBJECT", "FEMALE_GENITAL", "BDSM_RESTRAINT", True),
    ("pussy_focus", "人物の顔より下半身を画面の主役にしたい", "下半身を画面の中心に", "composition", "COMPOSITION_CAMERA", "FEMALE_GENITAL", "", False),
    ("pussy_juice", "行為の後に下半身の濡れを描きたい", "行為の後の下半身の濡れ", "fluid", "FLUID_EXCRETION", "FEMALE_GENITAL", "", True),
    ("handjob", "手で相手の男性器を刺激する", "手で相手を刺激する", "male_genital", "ACTION_CONTACT", "MALE_GENITAL", "", False),
    ("penis_focus", "画面を男性器のクローズアップにする", "男性器のアップを中心に", "composition", "COMPOSITION_CAMERA", "MALE_GENITAL", "", False),
    ("testicle_sucking", "口で睾丸を刺激する", "口で下半身を刺激", "male_genital", "ACTION_CONTACT", "MALE_GENITAL", "MOUTH_ORAL", True),
    ("prostate_milking", "前立腺を刺激する器具を使う", "内部を器具で刺激する", "male_genital", "TOOL_OBJECT", "MALE_GENITAL", "", True),
    ("cock_ring", "男性器の根元にリング状の器具", "根元に輪の器具を付ける", "male_genital", "TOOL_OBJECT", "MALE_GENITAL", "", True),
    ("sounding", "尿道に細い器具を使う描写", "細い器具を使う場面", "male_genital", "TOOL_OBJECT", "MALE_GENITAL", "", True),
    ("penis_in_panties", "下着越しに男性器の形が出ている", "下着越しの男性器の形", "male_genital", "CLOTHING_EXPOSURE", "MALE_GENITAL", "", True),
    ("penis_on_face", "顔のすぐ近くへ男性器を寄せる構図", "顔の前に相手の下半身", "composition", "COMPOSITION_CAMERA", "MALE_GENITAL", "", True),
    ("sex", "二人の性行為を描きたい", "二人の親密な行為", "action", "ACTION_CONTACT", "", "", False),
    ("masturbation", "一人で性的に自分を刺激する", "ひとりで自分を刺激", "action", "ACTION_CONTACT", "", "", False),
    ("frottage", "服を着たまま身体をこすり合わせる", "服越しに身体をこすり合わせる", "action", "ACTION_CONTACT", "", "", True),
    ("tribadism", "二人の女性が下半身を密着させる", "二人で下半身を密着", "action", "ACTION_CONTACT", "FEMALE_GENITAL", "", True),
    ("group_masturbation", "複数人が同じ場で自分を刺激する", "複数人でそれぞれ自分を刺激", "multi_person", "ACTION_CONTACT", "", "", True),
    ("foreplay", "本番の前に触れ合う親密な場面", "行為の前に触れ合う", "action", "ACTION_CONTACT", "", "", False),
    ("groping", "服の上から身体をまさぐる接触", "服の上から身体をまさぐる", "action", "ACTION_CONTACT", "", "", False),
    ("guided_breast_grab", "相手の手を自分の胸へ導く", "相手の手を胸元へ連れていく", "action", "ACTION_CONTACT", "BREAST_NIPPLE", "", True),
    ("sex_toy", "性具を使った一人または二人の場面", "器具を使った親密な行為", "action", "TOOL_OBJECT", "", "", False),
    ("cowgirl_position", "相手の上にまたがる体位", "相手の上にまたがる", "pose", "POSE_POSITION", "", "", False),
    ("missionary", "向かい合って横になる体位", "向かい合って横になる二人", "pose", "POSE_POSITION", "", "", False),
    ("doggystyle", "後ろからの体位を描きたい", "後ろからの体位", "pose", "POSE_POSITION", "", "", False),
    ("amazon_position", "相手を押さえ込む上下関係の体位", "相手をまたいで主導する体位", "pose", "POSE_POSITION", "", "", True),
    ("reverse_cowgirl_position", "相手に背を向けてまたがる", "背を向けて相手にまたがる", "pose", "POSE_POSITION", "", "", True),
    ("suspended_congress", "吊り上げられた状態で行う体位", "吊られたままの体位", "pose", "POSE_POSITION", "", "BDSM_RESTRAINT", True),
    ("mating_press", "相手を押し倒して密着する体位", "押し倒して覆いかぶさる", "pose", "POSE_POSITION", "", "", True),
    ("standing_sex", "立ったまま行う二人の性行為", "立ったままの二人の行為", "pose", "POSE_POSITION", "", "", True),
    ("bondage", "縄や拘束具で身動きを制限する", "縄で身動きを制限", "bdsm", "ACTION_CONTACT", "", "BDSM_RESTRAINT", False),
    ("bound_wrists", "手首を縛られた人物", "両手首を縛る", "bdsm", "ACTION_CONTACT", "", "BDSM_RESTRAINT", False),
    ("ball_gag", "口にボール型の猿ぐつわを付ける", "口を器具でふさぐ", "bdsm", "TOOL_OBJECT", "MOUTH_ORAL", "BDSM_RESTRAINT", True),
    ("shibari_over_clothes", "服の上から縄で縛る", "服の上から縄で拘束", "bdsm", "ACTION_CONTACT", "", "BDSM_RESTRAINT", True),
    ("chastity_cage", "男性器を檻状の器具で覆う", "下半身を檻状の器具で拘束", "bdsm", "TOOL_OBJECT", "MALE_GENITAL", "BDSM_RESTRAINT", True),
    ("predicament_bondage", "動くと別の拘束が強まる仕掛け", "動くほど苦しくなる拘束", "bdsm", "ACTION_CONTACT", "", "BDSM_RESTRAINT", True),
    ("self_bondage", "自分で自分を拘束する場面", "自分の身体を自分で拘束", "bdsm", "ACTION_CONTACT", "", "BDSM_RESTRAINT", True),
    ("spreader_bar", "脚を開いた状態で器具に固定する", "脚を開いて器具で固定", "bdsm", "TOOL_OBJECT", "", "BDSM_RESTRAINT", True),
    ("blindfold", "目隠しされた人物の拘束場面", "目隠しをして身動きを制限", "bdsm", "ACTION_CONTACT", "", "BDSM_RESTRAINT", True),
    ("pregnant", "妊娠した人物を描きたい", "妊娠中の人物", "pregnancy_lactation", "BODY_SITE", "", "REPRO_PREGNANCY_LACTATION", False),
    ("breastfeeding", "胸から子へ授乳している場面", "授乳", "pregnancy_lactation", "ACTION_CONTACT", "BREAST_NIPPLE", "REPRO_PREGNANCY_LACTATION", False),
    ("lactation", "母乳が出ている身体表現", "母乳", "pregnancy_lactation", "BODY_SITE", "BREAST_NIPPLE", "REPRO_PREGNANCY_LACTATION", False),
    ("forced_lactation", "望まない授乳を強いられる場面", "授乳を強制される", "pregnancy_lactation", "ACTION_CONTACT", "BREAST_NIPPLE", "REPRO_PREGNANCY_LACTATION", True),
    ("impregnation", "妊娠を目的とした行為を描きたい", "妊娠を望む二人の行為", "pregnancy_lactation", "ACTION_CONTACT", "", "REPRO_PREGNANCY_LACTATION", True),
    ("requesting_impregnation", "妊娠させてほしいと求める場面", "妊娠を求める仕草", "pregnancy_lactation", "RELATION_ROLE", "", "REPRO_PREGNANCY_LACTATION", True),
    ("cum_in_mouth", "口の中に体液が残る行為後の場面", "口元に体液が残る", "fluid", "FLUID_EXCRETION", "MOUTH_ORAL", "", False),
    ("cum_on_breasts", "胸に体液が付着した構図", "胸に体液が付着", "fluid", "FLUID_EXCRETION", "BREAST_NIPPLE", "", False),
    ("cum_in_pussy", "女性器内に体液がある事後表現", "行為後の体液を下半身に", "fluid", "FLUID_EXCRETION", "FEMALE_GENITAL", "", True),
    ("ejaculation", "体液が放出される瞬間", "体液が飛ぶ瞬間", "fluid", "FLUID_EXCRETION", "", "", False),
    ("facial", "顔に体液が付着した構図", "顔に体液がかかる", "fluid", "FLUID_EXCRETION", "", "", False),
    ("bukkake", "複数人の体液が一人にかかる場面", "複数人から一人に体液", "fluid", "FLUID_EXCRETION", "", "", True),
    ("cum_string", "体液が糸を引く事後表現", "体液が糸を引く", "fluid", "FLUID_EXCRETION", "", "", True),
    ("female_ejaculation", "女性の体液放出を描きたい", "女性の体液が飛ぶ", "fluid", "FLUID_EXCRETION", "FEMALE_GENITAL", "", True),
    ("threesome", "三人が関わる性的場面", "三人で行う親密な場面", "multi_person", "RELATION_ROLE", "", "", False),
    ("group_sex", "四人以上が参加する性的場面", "大勢が関わる親密な場面", "multi_person", "RELATION_ROLE", "", "", False),
    ("ffm_threesome", "女性二人と男性一人の三人構図", "二人の女性と一人の男性", "multi_person", "PEOPLE_COUNT", "", "", True),
    ("mmf_threesome", "男性二人と女性一人の三人構図", "二人の男性と一人の女性", "multi_person", "PEOPLE_COUNT", "", "", True),
    ("gangbang", "複数人が一人を相手にする場面", "一人に複数人が関わる", "multi_person", "RELATION_ROLE", "", "", True),
    ("mutual_masturbation", "二人が互いを見ながら自分を刺激する", "二人で見せ合いながら自分を刺激", "multi_person", "ACTION_CONTACT", "", "", True),
    ("multiple_penis_fellatio", "一人が複数人を口で相手にする", "一人が複数人に口を使う", "multi_person", "ACTION_CONTACT", "MOUTH_ORAL", "", True),
    ("male_spitroast", "一人が二人の間にいる多人数構図", "二人の間に一人がいる行為", "multi_person", "RELATION_ROLE", "", "", True),
    ("tentacle_sex", "触手状の生物が人物に絡みつく", "触手が人物に絡みつく", "nonhuman", "NONHUMAN_TRANSFORM", "", "", False),
    ("consensual_tentacles", "人物と触手が合意的に関わる場面", "触手と人物が親密に関わる", "nonhuman", "NONHUMAN_TRANSFORM", "", "", True),
    ("slime_sex", "スライム状の存在と人物が関わる", "粘液状の存在が人物に触れる", "nonhuman", "NONHUMAN_TRANSFORM", "", "", True),
    ("tail_sex", "尻尾を使った異種間の行為", "尻尾が人物に絡み行為に使われる", "nonhuman", "NONHUMAN_TRANSFORM", "", "", True),
    ("plant_sex", "植物が人物に絡む性的な場面", "植物が人物に巻き付く", "nonhuman", "NONHUMAN_TRANSFORM", "", "", True),
    ("sex_with_insects", "昆虫型の生物が人物と関わる", "虫のような生物が人物に接触", "nonhuman", "NONHUMAN_TRANSFORM", "", "", True),
    ("pov_crotch", "見る側の視点で相手の下半身を捉える", "こちらから相手の下半身を見る", "composition", "COMPOSITION_CAMERA", "MALE_GENITAL", "", False),
    ("pov_breasts", "見る側の視点で胸を近くに捉える", "こちらに迫る胸を見上げる", "composition", "COMPOSITION_CAMERA", "BREAST_NIPPLE", "", False),
    ("pov", "一人称の視点で相手との距離を近く見せる", "相手の目の前にいる視点", "composition", "COMPOSITION_CAMERA", "", "", False),
    ("crotch_focus", "顔を外して股間に視線を集める構図", "股間を画面の中心にする", "composition", "COMPOSITION_CAMERA", "MALE_GENITAL", "", False),
    ("ass_focus", "後ろ姿の尻へ画面の焦点を合わせる", "尻を画面の中心に寄せる", "composition", "COMPOSITION_CAMERA", "BUTTOCK_ANAL", "", False),
    ("close-up", "身体の一部を大きく切り取る画角", "身体の一部を大きく写す", "composition", "COMPOSITION_CAMERA", "", "", False),
    ("pussy_out_of_frame", "下半身の行為を画面外から想像させる", "行為の中心をあえて画面外に", "composition", "COMPOSITION_CAMERA", "FEMALE_GENITAL", "", True),
    ("imminent_penetration", "挿入の直前で止めた緊張感のある構図", "行為が始まる直前の二人", "composition", "COMPOSITION_CAMERA", "", "", True),
    ("sucking_own_breasts", "自分の胸へ口を寄せる柔軟なポーズ", "自分の胸を口で愛撫", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "", True),
    ("nipple_tweak_through_clothes", "服越しに乳首を指で刺激する", "服越しに胸の一点をつまむ", "breast", "ACTION_CONTACT", "BREAST_NIPPLE", "", True),
    ("standing_fellatio", "立っている相手へ口を寄せる体位", "立った相手に口を寄せる", "oral", "POSE_POSITION", "MOUTH_ORAL", "", True),
    ("double_vaginal", "二人が一人の前側へ同時に関わる", "一人に二人が同時に関わる", "female_genital", "ACTION_CONTACT", "FEMALE_GENITAL", "", True),
    ("spread_pussy_under_clothes", "服の隙間から下半身を見せる", "服越しに下半身を見せる", "female_genital", "CLOTHING_EXPOSURE", "FEMALE_GENITAL", "", True),
    ("clitoris_tweak", "指でクリトリスをつまむ接触", "特定の部位を指でつまむ", "female_genital", "ACTION_CONTACT", "FEMALE_GENITAL", "", True),
    ("testicle_grab", "手で睾丸をつかむ場面", "手で下半身をつかむ", "male_genital", "ACTION_CONTACT", "MALE_GENITAL", "", True),
    ("vibrator_on_penis", "振動する器具を男性器に当てる", "振動する器具を下半身に当てる", "male_genital", "TOOL_OBJECT", "MALE_GENITAL", "", True),
    ("mutual_handjob", "二人が互いに手で刺激し合う", "二人で手を使い合う", "action", "ACTION_CONTACT", "MALE_GENITAL", "", True),
    ("mutual_penetration", "二人が同時に互いへ挿入する構図", "二人が互いに同時に関わる", "action", "ACTION_CONTACT", "", "", True),
    ("guided_handjob", "相手の手を導いて刺激する場面", "手を添えて動きを教える", "action", "ACTION_CONTACT", "MALE_GENITAL", "", True),
    ("standing_doggystyle", "立ったまま後ろ向きに密着する体位", "立ち姿の後方体位", "pose", "POSE_POSITION", "", "", True),
    ("reverse_squatting_cowgirl_position", "しゃがみながら背を向けてまたがる", "背を向けてしゃがみまたがる", "pose", "POSE_POSITION", "", "", True),
]

# General set: 80 varied beginner intents. The broad route is the one a novice is
# most likely to try from the natural-language description.
GENERAL = [
    ("long_hair", "背中まで伸びた髪の人物", "背中まで長い髪", "hair", "HAIR_FACE"),
    ("short_hair", "耳が見える短い髪型", "耳の出る短い髪", "hair", "HAIR_FACE"),
    ("ponytail", "髪を後ろで一つにまとめた姿", "ポニーテール", "hair", "HAIR_FACE"),
    ("twintails", "左右に髪を結んだ髪型", "ツインテール", "hair", "HAIR_FACE"),
    ("braid", "髪を編み込んだ人物", "編み込みの髪", "hair", "HAIR_FACE"),
    ("messy_hair", "寝起きのように乱れた髪", "くしゃっと乱れた髪", "hair", "HAIR_FACE"),
    ("hair_ornament", "髪に飾りを付けた人物", "髪に小さな飾り", "hair", "HAIR_FACE"),
    ("hair_ribbon", "髪をリボンで結んでいる", "髪にリボンを結ぶ", "hair", "HAIR_FACE"),
    ("glasses", "眼鏡をかけた人物", "眼鏡", "hair", "HAIR_FACE"),
    ("blush", "頬を赤らめた表情", "頬が赤い", "expression", "EXPRESSION_GAZE"),
    ("smile", "穏やかな笑顔", "笑顔", "expression", "EXPRESSION_GAZE"),
    ("frown", "不機嫌そうに眉を寄せる", "眉を寄せた表情", "expression", "EXPRESSION_GAZE"),
    ("closed_eyes", "目を閉じている人物", "目を閉じている", "expression", "EXPRESSION_GAZE"),
    ("looking_at_viewer", "こちらをまっすぐ見る人物", "こちらを見つめる", "expression", "EXPRESSION_GAZE"),
    ("looking_to_the_side", "視線を横へそらした人物", "視線をそらす", "expression", "EXPRESSION_GAZE"),
    ("open_mouth", "口を開けて驚いた表情", "驚いて口を開ける", "expression", "EXPRESSION_GAZE"),
    ("tears", "涙を流している人物", "頬を涙が流れる", "expression", "EXPRESSION_GAZE"),
    ("sweat", "緊張して汗をかいている", "額に汗をかく", "expression", "EXPRESSION_GAZE"),
    ("school_uniform", "学生服を着た人物", "日本の学生服", "clothing", "CLOTHING_EXPOSURE"),
    ("sailor_senshi_uniform", "戦士風のセーラー服姿", "戦士風のセーラー服", "clothing", "CLOTHING_EXPOSURE"),
    ("blazer", "ブレザーを着た人物", "ブレザー姿", "clothing", "CLOTHING_EXPOSURE"),
    ("hoodie", "ゆったりしたパーカー姿", "大きめのパーカー", "clothing", "CLOTHING_EXPOSURE"),
    ("sweater", "厚手のセーターを着る", "編み目のあるセーター", "clothing", "CLOTHING_EXPOSURE"),
    ("jacket", "上着を羽織った人物", "上着を羽織る", "clothing", "CLOTHING_EXPOSURE"),
    ("apron", "エプロンを身に付けた人物", "料理用のエプロン", "clothing", "CLOTHING_EXPOSURE"),
    ("kimono", "和服を着た人物", "伝統的な着物", "clothing", "CLOTHING_EXPOSURE"),
    ("police_uniform", "警官の制服を着た人物", "警官の制服", "clothing", "CLOTHING_EXPOSURE"),
    ("necktie", "ネクタイを締めた人物", "首元にネクタイ", "clothing", "CLOTHING_EXPOSURE"),
    ("striped_clothes", "縞模様の服を着ている", "しましま模様の服", "color_pattern", "COLOR_PATTERN_SHAPE"),
    ("polka_dot", "水玉模様の小物や服", "丸い水玉模様", "color_pattern", "COLOR_PATTERN_SHAPE"),
    ("plaid_clothes", "格子柄の布地", "チェック柄の服", "color_pattern", "COLOR_PATTERN_SHAPE"),
    ("floral_print", "花柄の服を着た人物", "小花柄の服", "color_pattern", "COLOR_PATTERN_SHAPE"),
    ("camouflage", "迷彩柄の服装", "迷彩模様の上着", "color_pattern", "COLOR_PATTERN_SHAPE"),
    ("gradient_background", "色が滑らかに変わる背景", "端から色が変わる背景", "color_pattern", "COLOR_PATTERN_SHAPE"),
    ("monochrome", "一色調でまとめた画面", "白黒に近い一色の画面", "color_pattern", "COLOR_PATTERN_SHAPE"),
    ("polka_dot_background", "背景全体に水玉を散らす", "背景に丸い模様", "color_pattern", "COLOR_PATTERN_SHAPE"),
    ("standing", "人物がまっすぐ立っている", "まっすぐ立つ人物", "pose", "POSE_POSITION"),
    ("sitting", "椅子や床に座っている", "座っている人物", "pose", "POSE_POSITION"),
    ("kneeling", "膝をついて座る姿勢", "膝をついた姿", "pose", "POSE_POSITION"),
    ("lying", "床やベッドに横になる", "横になった人物", "pose", "POSE_POSITION"),
    ("walking", "歩いている途中の姿", "歩く人物", "pose", "POSE_POSITION"),
    ("running", "走っている動きのある場面", "走る人物", "pose", "POSE_POSITION"),
    ("jumping", "空中へ跳び上がった姿", "ジャンプする人物", "pose", "POSE_POSITION"),
    ("arms_up", "両腕を高く上げたポーズ", "両手を上に上げる", "pose", "POSE_POSITION"),
    ("hand_on_own_hip", "片手を腰に当てた姿", "片手を腰に置く", "pose", "POSE_POSITION"),
    ("looking_back", "歩きながら振り返る人物", "肩越しに振り返る", "pose", "POSE_POSITION"),
    ("holding_book", "本を手に持って読んでいる", "本を手に持つ", "object", "ACTION_CONTACT"),
    ("holding_sword", "剣を手にした人物", "剣を持っている", "object", "TOOL_OBJECT"),
    ("holding_umbrella", "雨傘を差している人物", "傘を手に持つ", "object", "TOOL_OBJECT"),
    ("holding_flower", "花を手に持っている", "一輪の花を持つ", "object", "TOOL_OBJECT"),
    ("holding_phone", "スマートフォンを操作する人物", "携帯電話を手に持つ", "object", "TOOL_OBJECT"),
    ("holding_cup", "飲み物のカップを持つ", "飲み物のカップを手に", "object", "TOOL_OBJECT"),
    ("holding_bag", "鞄を持って出かける人物", "鞄を持った姿", "object", "TOOL_OBJECT"),
    ("holding_weapon", "武器を構えた人物", "武器を手に持つ", "object", "TOOL_OBJECT"),
    ("holding_food", "食べ物を手に持っている", "食べ物を持った人物", "object", "TOOL_OBJECT"),
    ("holding_stuffed_toy", "ぬいぐるみを抱えている", "ぬいぐるみを持つ", "object", "TOOL_OBJECT"),
    ("outdoors", "屋外の開けた場所にいる人物", "屋外で過ごす人物", "scene", "SCENE_BACKGROUND"),
    ("indoors", "部屋の中にいる人物", "室内で過ごす人物", "scene", "SCENE_BACKGROUND"),
    ("classroom", "机が並ぶ教室の風景", "教室", "scene", "SCENE_BACKGROUND"),
    ("bedroom", "寝室でくつろぐ人物", "寝室", "scene", "SCENE_BACKGROUND"),
    ("kitchen", "台所で料理をする人物", "台所の料理風景", "scene", "SCENE_BACKGROUND"),
    ("street", "街路を背景にした場面", "街の通りを歩く", "scene", "SCENE_BACKGROUND"),
    ("forest", "木々に囲まれた森の中", "森の中にいる人物", "scene", "SCENE_BACKGROUND"),
    ("beach", "海辺で過ごす人物", "砂浜と海の場面", "scene", "SCENE_BACKGROUND"),
    ("night", "夜の暗い時間帯の情景", "夜", "light", "LIGHT_TIME_WEATHER"),
    ("sunset", "夕焼けに照らされた人物", "夕日の光が差す", "light", "LIGHT_TIME_WEATHER"),
    ("rain", "雨が降る屋外の場面", "雨", "light", "LIGHT_TIME_WEATHER"),
    ("snowing", "雪が降り積もる情景", "雪の中を歩く", "light", "LIGHT_TIME_WEATHER"),
    ("backlighting", "人物の後ろから光が差す画面", "逆光で人物を照らす", "light", "LIGHT_TIME_WEATHER"),
    ("spotlight", "一人だけを照らす舞台照明", "人物だけに光を当てる", "light", "LIGHT_TIME_WEATHER"),
    ("shadow", "強い影が落ちる画面", "顔に濃い影ができる", "light", "LIGHT_TIME_WEATHER"),
    ("sunbeam", "窓から光の筋が差し込む", "室内に光の筋が伸びる", "light", "LIGHT_TIME_WEATHER"),
    ("close-up", "顔を大きく切り取った画角", "顔を大きく写す", "composition", "COMPOSITION_CAMERA"),
    ("upper_body", "腰より上を中心に見せる構図", "上半身を中心に写す", "composition", "COMPOSITION_CAMERA"),
    ("full_body", "頭から足先まで入れた構図", "全身を画面に入れる", "composition", "COMPOSITION_CAMERA"),
    ("wide_shot", "人物と周囲の場所を広く見せる", "周囲を広く入れる画角", "composition", "COMPOSITION_CAMERA"),
    ("from_above", "高い場所から見下ろすカメラ", "上から見下ろす視点", "composition", "COMPOSITION_CAMERA"),
    ("from_below", "低い位置から見上げるカメラ", "足元から見上げる視点", "composition", "COMPOSITION_CAMERA"),
    ("profile", "横顔を見せる構図", "人物の横顔を写す", "composition", "COMPOSITION_CAMERA"),
    ("silhouette", "逆光で人物を影絵のように見せる", "人物をシルエットにする", "composition", "COMPOSITION_CAMERA"),
    ("cat", "猫と一緒にいる人物", "猫", "living", "LIVING"),
    ("dog", "犬と散歩する人物", "犬", "living", "LIVING"),
    ("bird", "鳥が肩や手に止まっている", "小鳥が手に止まる", "living", "LIVING"),
    ("butterfly", "蝶が周囲を飛ぶ庭の場面", "蝶が舞う人物", "living", "LIVING"),
    ("flower", "花に囲まれた人物", "花が咲く場所に立つ", "living", "LIVING"),
    ("tree", "大きな木のそばに立つ人物", "木の下の人物", "living", "LIVING"),
]

def load_catalog() -> dict[str, dict]:
    connection = sqlite3.connect(f"file:{CATALOG.as_posix()}?mode=ro", uri=True)
    try:
        return {entry.get("Canonical"): entry for (payload,) in connection.execute("SELECT payload FROM entries")
                if (entry := json.loads(payload)).get("Canonical")}
    finally:
        connection.close()

def row(i: int, raw: tuple, catalog: dict[str, dict], sexual: bool) -> dict:
    if sexual:
        target, intent, query, family, route, body, theme, *rest = raw
    else:
        target, intent, query, family, route = raw
        body, theme, rest = "", "", []
    entry = catalog.get(target)
    if entry is None:
        print(f"missing target: {target}")
        return None
    body = body or ""
    theme = theme or ""
    deep = bool(rest[0]) if rest else False
    local = {
        "school_uniform": "CLOTHING/UNIFORM",
        "blazer": "CLOTHING/EVERYDAY",
        "hoodie": "CLOTHING/EVERYDAY",
        "sweater": "CLOTHING/EVERYDAY",
        "jacket": "CLOTHING/EVERYDAY",
        "apron": "CLOTHING/EVERYDAY",
        "kimono": "CLOTHING/EVERYDAY",
        "holding_book": "ACTION_CONTACT/OBJECT_USE",
    }.get(target, "")
    return {
        "id": f"{'S' if sexual else 'G'}{i:03d}",
        "scenarioClass": family,
        "sexual": sexual,
        "intent": intent,
        "query": query,
        "expected": [target],
        "acceptableAlternatives": [],
        "route": route or "",
        "local": local,
        "bodySite": body,
        "theme": theme,
        "contentIntent": "Sexual" if sexual else "All",
        "deepOnly": deep,
        "complex": sexual and bool(route) and bool(body or theme),
        "usage": entry.get("Usage"),
        "catalogCategory": entry.get("TagCategory") or ("Special" if entry.get("IsSpecial") else "General"),
        "sexualIntent": entry.get("SexualIntent"),
        "catalogJapanese": entry.get("Japanese"),
    }

def main() -> None:
    catalog = load_catalog()
    scenarios = [r for i, item in enumerate(SEXUAL, 1) if (r := row(i, item, catalog, True))]
    scenarios += [r for i, item in enumerate(GENERAL, 1) if (r := row(i, item, catalog, False))]
    ids = [item["id"] for item in scenarios]
    if len(ids) != len(set(ids)) or len(scenarios) < 180 or sum(item["sexual"] for item in scenarios) < 100:
        raise SystemExit("Scenario count/uniqueness contract failed")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(scenarios)} scenarios ({sum(item['sexual'] for item in scenarios)} sexual) to {OUT}")

if __name__ == "__main__":
    main()
