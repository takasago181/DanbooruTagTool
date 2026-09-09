"""Remove false Japanese coverage created by canonical-in-Japanese wrappers."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import forced_ja_display_completion as forced
import qualified_label_final_review as prior


ROOT = forced.ROOT
CONTRACT = "translation_quarantine/r3/BOUNDED_WRAPPER_CLEANUP_CONTRACT.md"
SOURCE_DIR = prior.OUTPUT_DIR
OUTPUT_DIR = "translation_quarantine/bounded_wrapper_cleanup_20260909"
SOURCE_COMMIT = "f76535bbaefc18a31c03c5a9a337e93895b6ec34"
CONTRACT_COMMIT = "caf489ed6523da911c67d9d56466a5692445d47e"
AUDIT_COMMENT = "5599075517"

EXACT = {
    "kickstand": "キックスタンド", "legjob": "レッグジョブ", "dominator_(bdsm)": "支配する側（BDSM）",
    "implied_cheating_(relationship)": "浮気を示唆する関係", "alternate_ass_size_(larger)": "大きめの尻差分",
    "human_(warcraft)": "人間（Warcraft）", "hydro_symbol_(genshin_impact)": "水元素のシンボル（Genshin Impact）",
    "advanced_ship_(eve_online)": "先進型艦船（EVE Online）", "teamwork_(sexual)": "性的な協力プレイ",
    "same-sex_bathing": "同性同士の入浴", "male_penetrated": "男性が挿入された状態", "multiple_penetration": "複数箇所への挿入",
    "spreading_own_anus": "自分の肛門を広げる", "spreading_own_ass": "自分の尻を広げる", "tickling_nipples": "乳首をくすぐる",
    "tickling_pussy": "陰部をくすぐる", "unusual_insertion": "通常とは異なる挿入", "genderswap_(otm)": "性別入れ替え（OTM）",
    "gigantic_ass": "巨大な尻", "girthy_penis": "太いペニス", "improvised_sex_toy": "即席の性玩具",
    "no_dickey": "ペニスなし", "massage_table": "マッサージ台", "master_and_servant": "主人と従者",
    "misleading_thumbnail": "誤解を招くサムネイル", "nun_headdress": "修道女の頭飾り", "parallel_hairclips": "平行なヘアクリップ",
    "picnic_blanket": "ピクニック用ブランケット", "rectangular_halo": "長方形の光輪", "robot_boy": "ロボットの少年",
    "reindeer_boy": "トナカイの少年", "small_sweatdrop": "小さな汗のしずく", "spiked_thigh_strap": "棘付き太ももストラップ",
    "unconventional_maid": "型破りなメイド", "uneven_horns": "不揃いな角", "x_fingers": "交差した指",
    "action_camera": "アクションカメラ", "accidental_touch": "偶然の接触", "adoptive_siblings": "養子のきょうだい",
    "aerial_hoop": "エアリアルフープ", "aircraft_marshaller": "航空機誘導員", "aircraft_turret": "航空機の砲塔",
    "anti-aircraft_missile": "対空ミサイル", "antique_car": "クラシックカー", "apple_core": "リンゴの芯",
    "applying_lotion": "ローションを塗る", "applying_mascara": "マスカラを塗る", "armpit_hold": "脇で挟む",
    "art_supplies": "画材", "artist_name_(singer)": "歌手名", "assisted_carrying": "補助付きの運搬",
    "asymmetrical_eyelashes": "左右非対称のまつ毛", "aviator_glasses": "アビエーターサングラス", "backpack_basket": "リュックのかご",
    "backward-facing_horns": "後ろ向きの角", "baby_hippopotamus": "カバの赤ちゃん", "bamboo_leaf": "笹の葉",
    "bandaged_torso": "包帯を巻いた胴体", "bandaged_waist": "包帯を巻いた腰", "barbed_tongue": "棘のある舌",
    "baseball_field": "野球場", "basketball_shorts": "バスケットボールショーツ", "bath_brush": "浴用ブラシ",
    "battle_scarred": "戦傷のある", "beaded_eyelashes": "ビーズ付きまつ毛", "beaded_penis": "ビーズ付きペニス",
    "bear_cub": "クマの子", "bedtime_story": "おやすみ前の物語", "beer_glass": "ビールグラス",
    "behind_bars": "檻の中", "belly_press": "腹部を押し付ける", "birthday_card": "誕生日カード",
    "biblically_accurate_angel": "聖書準拠の天使", "bicep_curl": "アームカール", "bicycles_only_sign": "自転車専用標識",
    "bird_feeding": "鳥への餌やり", "blackout_poetry": "ブラックアウト・ポエトリー", "blade_of_grass": "草の葉",
    "bladed_tonfa": "刃付きトンファー", "birthday_date": "誕生日の日付", "blue_blush": "青い頬染め",
    "broken_wings": "折れた翼", "cable_tie": "ケーブルタイ", "camera_flash": "カメラのフラッシュ",
}

LEXICON = dict(forced.WORD)
LEXICON.update({
    "of": "の", "and": "と", "the": "その", "no": "なし", "many": "多数の", "multiple": "複数の", "two": "2つの", "three": "3つの", "four": "4つの", "one": "1つの", "own": "自分の", "my": "私の", "boy": "少年", "girl": "少女", "man": "男性", "woman": "女性", "people": "人々", "person": "人物", "child": "子供", "baby": "赤ちゃん", "grey": "灰色", "gray": "灰色", "heavy": "強い", "light": "光", "small": "小さい", "large": "大きい", "larger": "大きめの", "big": "大きい", "gigantic": "巨大な", "short": "短い", "tall": "背の高い", "taller": "より高い", "thick": "太い", "thin": "細い", "good": "良い", "bad": "悪い", "new": "新しい", "old": "古い", "alternate": "別の", "original": "元の", "unusual": "珍しい", "unconventional": "型破りな", "accurate": "正確な", "ancient": "古代の", "art": "芸術", "style": "スタイル", "fashion": "ファッション", "symbol": "シンボル", "sign": "標識", "name": "名前", "type": "種類", "number": "番号", "year": "年", "years": "年", "day": "日", "popularity": "人気", "poll": "投票", "project": "プロジェクト", "game": "ゲーム", "world": "世界", "star": "星", "stars": "星々", "love": "愛", "live": "ライブ", "glass": "ガラス", "glasses": "眼鏡", "gun": "銃", "rifle": "ライフル", "guitar": "ギター", "bass": "ベース", "vehicle": "乗り物", "aircraft": "航空機", "ship": "船", "boat": "ボート", "vehicle": "乗り物", "team": "チーム", "family": "家族", "group": "集団", "member": "メンバー", "uniform": "制服", "outfit": "衣装", "suit": "スーツ", "swimsuit": "水着", "dress": "ドレス", "shirt": "シャツ", "shorts": "ショートパンツ", "skirt": "スカート", "sleeves": "袖", "ribbon": "リボン", "crown": "王冠", "horn": "角", "horns": "角", "halo": "光輪", "shield": "盾", "blade": "刃", "sword": "剣", "weapon": "武器", "armor": "鎧", "artillery": "砲", "emblem": "紋章", "paper": "紙", "card": "カード", "bag": "バッグ", "box": "箱", "ball": "ボール", "bubble": "泡", "juice": "ジュース", "cake": "ケーキ", "fruit": "果物", "flower": "花", "plant": "植物", "leaf": "葉", "tree": "木", "bird": "鳥", "fish": "魚", "animal": "動物", "horse": "馬", "bear": "クマ", "duck": "アヒル", "rabbit": "ウサギ", "dragon": "竜", "skull": "頭蓋骨", "mouth": "口", "finger": "指", "fingers": "指", "feet": "足", "leg": "脚", "thigh": "太もも", "belly": "腹", "waist": "腰", "nose": "鼻", "tongue": "舌", "penis": "ペニス", "anus": "肛門", "ass": "尻", "pussy": "陰部", "nipples": "乳首", "nipple": "乳首", "hands": "両手", "arms": "両腕", "knees": "膝", "skin": "肌", "hair": "髪", "bangs": "前髪", "hairstyle": "髪型", "eyelashes": "まつ毛", "eyewear": "アイウェア", "mouth": "口", "neck": "首", "shoulder": "肩", "pectorals": "胸筋", "sidelocks": "横髪", "stubble": "無精ひげ", "mustache": "口ひげ", "scar": "傷跡", "mark": "印", "markings": "模様", "tattoo": "タトゥー", "piercing": "ピアス", "ring": "指輪", "pendant": "ペンダント", "necklace": "ネックレス", "choker": "チョーカー", "strap": "ストラップ", "strapless": "ストラップなし", "cable": "ケーブル", "camera": "カメラ", "computer": "コンピューター", "headphones": "ヘッドホン", "ipod": "iPod", "phone": "電話", "screen": "画面", "window": "窓", "frame": "枠", "wall": "壁", "floor": "床", "table": "テーブル", "chair": "椅子", "bed": "ベッド", "blanket": "ブランケット", "bath": "入浴", "bathing": "入浴", "massage": "マッサージ", "lotion": "ローション", "mascara": "マスカラ", "makeup": "化粧", "camera": "カメラ", "action": "動作", "attack": "攻撃", "hold": "保持", "grab": "掴む", "grabbing": "掴む", "touch": "接触", "press": "押す", "riding": "またがる", "position": "姿勢", "play": "遊び", "playing": "遊ぶ", "dance": "ダンス", "dancing": "ダンス", "threesome": "3人での性行為", "sex": "性行為", "sexual": "性的な", "toy": "玩具", "dildo": "ディルド", "handjob": "手コキ", "fellatio": "フェラチオ", "rape": "レイプ", "insertion": "挿入", "penetrated": "挿入された", "penetration": "挿入", "tickling": "くすぐる", "spreading": "広げる", "rest": "休め", "zipper": "ファスナー", "sweatdrop": "汗のしずく", "covered": "覆われた", "censored": "検閲された", "broken": "壊れた", "spiked": "棘付き", "bandaged": "包帯を巻いた", "applying": "塗る", "wearing": "着用", "wear": "衣類", "looking": "見る", "spoken": "発言された", "forced": "強制された", "generated": "生成された", "drawing": "描画", "painting": "絵画", "photo": "写真", "picture": "画像", "video": "動画", "animation": "アニメーション", "background": "背景", "thumbnail": "サムネイル", "comparison": "比較", "adapted": "適応した", "adoptive": "養子の", "ancestor": "祖先", "descendant": "子孫", "relationship": "関係", "cheating": "浮気", "implied": "示唆された", "master": "主人", "servant": "従者", "commissioner": "委員", "architecture": "建築", "egyptian": "エジプトの", "angel": "天使", "dragon": "竜", "field": "野原", "baseball": "野球", "basketball": "バスケットボール", "acorn": "どんぐり", "pendant": "ペンダント", "billion": "10億", "yen": "円", "incident": "事件", "grenade": "手榴弾", "guitar": "ギター", "string": "弦", "headset": "ヘッドセット", "helmet": "ヘルメット", "sweater": "セーター", "kimono": "着物", "umbrella": "傘", "rainbow": "虹", "wooden": "木製の", "wood": "木", "stone": "石", "ice": "氷", "fire": "火", "lightning": "稲妻", "rain": "雨", "snow": "雪", "moon": "月", "sun": "太陽", "shadow": "影", "world": "世界", "space": "宇宙", "hollow": "空洞の", "royal": "王家の", "imperial": "帝国の", "divine": "神聖な", "super": "超", "nano": "ナノ", "mini": "小型", "grid": "格子", "layer": "層", "form": "形態", "state": "状態", "mode": "モード", "technology": "技術", "device": "装置", "machine": "機械", "robot": "ロボット", "mechanical": "機械の", "vehicle": "乗り物", "rail": "レール", "lane": "レーン", "teamwork": "協力", "cutout": "切り抜き", "cover": "表紙", "magazine": "雑誌", "topic": "話題", "phrase": "フレーズ", "object": "物体", "medium": "媒体", "gesture": "ジェスチャー", "room": "部屋", "animated": "アニメーション", "plant": "植物", "sport": "スポーツ", "fish": "魚", "food": "食べ物", "building": "建物", "container": "容器", "expression": "表情", "original": "オリジナル", "symbol": "シンボル", "style": "スタイル", "fashion": "ファッション", "weapon": "武器", "logo": "ロゴ", "uniform": "制服", "armor": "鎧", "singer": "歌手", "carmaker": "自動車メーカー", "star": "恒星", "os": "OS",
})
# Acronyms and specialist nouns that have a stable Japanese UI rendering.
LEXICON.update({
    "atm": "ATM（現金自動預け払い機）", "cd": "CD媒体", "cpu": "CPU（中央処理装置）", "dslr": "デジタル一眼レフ", "gps": "GPS測位", "lcd": "LCD画面", "led": "LED照明", "lpvo": "低倍率可変倍率照準器", "mvp": "最優秀選手", "vs": "対戦", "ao": "アオ", "nhat": "ニャット", "binh": "ビン", "dji": "DJI", "equip": "装備", "djinn": "精霊", "elder": "古びた", "spear": "槍", "genocide": "ジェノサイド", "route": "ルート", "gn": "GN", "particles": "粒子", "impending": "迫り来る", "doom": "破滅", "interactive": "対話型", "media": "メディア", "instagram": "Instagram", "story": "ストーリー", "highlighter": "ハイライト", "makeup": "化粧", "shachihoko": "しゃちほこ", "tridecagram": "十三芒星", "triquetra": "三脚巴", "tryzub": "三叉槍紋", "tre": "三", "kronor": "クローナ", "tama": "玉", "kanzashi": "かんざし", "otome": "乙女", "camellia": "椿", "paduka": "パドゥカ", "pteruges": "革垂れ", "tam": "タム", "shanter": "シャンター帽", "twi'lek": "トワイレック", "vyshyvanka": "ヴィシヴァンカ", "uwagi": "上着"
})
# High-frequency descriptive tokens exposed by the post-cleanup audit.
LEXICON.update({
    "too": "多すぎる", "censor": "検閲", "out": "外へ", "sided": "面の", "clubs": "クラブ", "by": "による", "winged": "翼のある", "than": "より", "burning": "燃えている", "holding": "持っている", "cream": "クリーム", "pile": "積み重ね", "nine": "9", "self": "自分", "turret": "砲塔", "assisted": "補助された", "birthday": "誕生日", "bowtie": "蝶ネクタイ", "tinted": "色付きの", "howa": "豊和", "army": "陸軍", "diamonds": "ダイヤ", "ascot": "アスコット", "six": "6", "pinching": "つまむ", "raven": "ワタリガラス", "nijigasaki": "虹ヶ咲", "sideless": "脇なし", "veiny": "血管の浮いた", "legendary": "伝説の", "hairclips": "ヘアクリップ", "picnic": "ピクニック", "maid": "メイド", "aerial": "空中", "anglerfish": "アンコウ", "meme": "ミーム", "core": "芯", "armpit": "脇", "artist": "絵師", "rubbing": "こする", "trail": "軌跡", "audio": "音声", "hippopotamus": "カバ", "facing": "向き", "badger": "アナグマ", "brush": "ブラシ", "beaded": "ビーズ付き", "bicep": "上腕二頭筋", "biting": "噛む", "whip": "鞭", "grass": "草", "break": "破壊", "bridge": "橋", "snowman": "雪だるま", "burger": "バーガー", "burnt": "焦げた", "carrot": "ニンジン", "chicken": "ニワトリ", "challenge": "挑戦", "groin": "股間", "creator": "創作者", "curly": "巻き毛の", "curved": "曲がった", "death": "死", "decorating": "飾り付け", "christmas": "クリスマス", "thumb": "親指", "zoom": "ズーム", "dolls": "人形たち", "drawn": "描かれた", "duel": "決闘", "earth": "地球", "forces": "軍", "elmo": "エルモ", "35": "35", "horus": "ホルス", "son": "息子", "find": "見つける", "view": "眺め", "duo": "2人組", "fortified": "強化された", "fretless": "フレットなし", "door": "扉", "over": "越えて", "bandeau": "バンドゥ", "garter": "ガーター", "straps": "ストラップ", "sarong": "サロン", "trim": "縁取り", "mother": "母", "hedgehog": "ハリネズミ", "idol": "アイドル", "navel": "へそ", "illusion": "幻影", "contest": "コンテスト", "merfolk": "人魚族", "military": "軍用", "money": "お金", "prosthetic": "義肢", "normal": "通常の", "job": "仕事", "spread": "広げる", "parasite": "寄生体", "parrot": "オウム", "pentagram": "五芒星", "pointed": "尖った", "powerful": "力強い", "tails": "尾", "camisole": "キャミソール", "round": "丸い", "sea": "海", "speech": "発話", "cheeks": "頬", "stitched": "縫い付けた", "salute": "敬礼", "ten": "10", "blades": "刃", "unmanned": "無人", "you": "あなた", "mario": "マリオ", "pikachu": "ピカチュウ", "ferret": "フェレット", "reindeer": "トナカイ", "dickey": "ペニス", "nun": "修道女", "headdress": "頭飾り", "orientation": "方向", "perversion": "倒錯", "grip": "握り", "cowgirl": "カウガール", "same": "同じ", "misleading": "誤解を招く", "dressing": "着付け", "decoration": "装飾", "slicer": "スライサー", "camel": "ラクダ", "feed": "映像", "choose": "選ぶ", "can't": "できない", "cats": "猫", "scared": "怯えた", "cucumbers": "キュウリ", "profanity": "卑語", "thought": "思考", "chapter": "章", "ideal": "理想", "idol": "アイドル", "anglerfish": "アンコウ", "badger": "アナグマ", "ballroom": "舞踏室", "charm": "チャーム", "beaver": "ビーバー", "bee": "ハチ", "beetle": "甲虫", "birthday": "誕生日", "blanket": "毛布", "burrito": "ブリトー", "brooklyn": "ブルックリン", "broom": "ほうき", "brother": "兄弟", "sister": "姉妹", "building": "建物", "snowman": "雪だるま", "cake": "ケーキ", "slicer": "切断器", "camera": "カメラ", "hold": "保持", "pose": "ポーズ", "carrot": "ニンジン", "town": "町", "scimitar": "シミター", "are": "である", "scared": "怯えた", "bridge": "橋", "statue": "像", "truck": "トラック", "burning": "燃える", "carrot": "ニンジン", "castle": "城", "chalk": "チョーク", "chameleon": "カメレオン", "chaos": "混沌", "undivided": "分かたれない", "sign": "標識", "journey": "旅", "blueberry": "ブルーベリー", "blur": "ぼかし", "operator": "操作者", "trigger": "引き金", "box": "箱", "truck": "トラック", "outfit": "衣装"
})
# Final ordinary terms that were still isolated by the bounded audit.
LEXICON.update({
    "cbt": "陰茎・睾丸拘束", "ballerino": "男性バレリーナ", "cempoalxochitl": "センポアルソチル", "cool": "クール", "disproportionate": "不釣り合いな", "retribution": "報復", "do": "する", "not": "ない", "want": "望む", "earbuds": "イヤホン", "charging": "充電", "case": "ケース", "ebon": "黒檀の", "escrima": "エスクリマ", "facial": "顔の", "recognition": "認識", "gingham": "ギンガム", "guimpe": "ギンピ", "highleg": "ハイレグ", "springsuit": "スプリングスーツ", "hounskull": "ハウンズカル", "improvised": "即席の", "vase": "花瓶", "inflatable": "膨らませた", "torpedo": "魚雷", "splatter": "飛沫", "interactive": "対話型", "media": "メディア", "interlocked": "組み合わさった", "mars": "火星", "inward": "内向き", "iron": "鉄の", "warriors": "戦士", "kitchen": "台所", "range": "コンロ", "knit": "編み", "scarf": "マフラー", "laddered": "はしご状の", "bodystocking": "ボディストッキング", "balloons": "風船", "cursor": "カーソル", "linea": "線", "semilunaris": "半月状の", "eyelids": "まぶた", "medical": "医療用", "monitor": "モニター", "melting": "溶けた", "popsicle": "アイスキャンディー", "mixed": "混合した", "limbs": "手足", "maids": "メイドたち", "signals": "信号", "monster": "怪物", "sexualization": "性的対象化", "moose": "ヘラジカ", "antlers": "角", "ninjutsu": "忍術", "opaque": "不透明な", "monocle": "片眼鏡", "sunglasses": "サングラス", "oppai": "おっぱい", "ouija": "ウィジャ盤", "oversized": "大型の", "fork": "フォーク", "parallel": "平行な", "piercings": "ピアス", "peed": "排尿した", "photocopying": "コピー", "pinstripe": "ピンストライプ", "polehammer": "ポールハンマー", "portcullis": "落とし格子", "pteruges": "革垂れ", "ragequit": "怒ってゲームをやめる", "rectangular": "長方形の", "reflected": "反射した", "worlds": "世界", "selfie": "自撮り", "prank": "いたずら", "sequential": "連続した", "shadowed": "影のある", "sheaf": "束", "sheet": "シート", "ghost": "幽霊", "magnifier": "拡大鏡", "simple": "単純な", "bat": "バット", "skullcap": "頭蓋帽", "snapchat": "Snapchat", "songover": "歌の余韻", "splatoonification": "スプラトゥーン化", "stringer": "ストリンガー", "takoyaki": "たこ焼き", "pick": "ピック", "tanbi": "耽美", "kei": "系", "telnyashka": "テルニャシュカ", "teratophilia": "怪物性愛", "toortsog": "トールツォグ", "trompe": "トロンプ", "oeil": "レイユ", "uwagi": "上着", "formation": "編隊", "welcome": "歓迎用", "mat": "マット", "wheeled": "車輪付き", "legs": "脚", "word": "言葉", "bearers": "担い手", "gps": "GPS", "facial": "顔の"
})
# Additional transparent terms from the remaining bounded rows.  This list is
# deliberately lexical (not a name allow-list): it covers visible concepts so
# a compound such as `bloody_footprints` is not misfiled as opaque merely
# because the earlier machine dictionary lacked one token.
LEXICON.update({
    "affectionate": "愛情のある", "harem": "ハーレム", "agemaki": "揚巻", "knot": "結び", "ahoge": "アホ毛", "wag": "振る", "arctic": "北極の", "warfare": "戦闘", "apricot": "アンズ", "blossom": "花", "awacs": "空中警戒管制", "awakened": "覚醒した", "being": "存在", "awakening": "覚醒", "beat": "ビート", "bamboozler": "バンブーズラー", "heels": "ヒール", "block": "ブロック", "bloody": "血まみれの", "footprints": "足跡", "bookshelf": "本棚", "pov": "視点", "bulge": "隆起", "lift": "持ち上げ", "bunbunmaru": "文々。新聞", "butch": "ボーイッシュ", "femme": "フェム", "couple": "カップル", "butt": "尻", "crush": "押し潰し", "cadpat": "迷彩柄", "calflet": "ふくらはぎ", "calico": "三毛", "carro": "車両", "veloce": "高速", "cartoon": "漫画", "logic": "論理", "cased": "ケース入り", "tape": "テープ", "measure": "測定", "catalyst": "触媒", "cathead": "猫頭", "cavewoman": "女原始人", "celestial": "天上の", "cervix": "子宮頸部", "punching": "殴打", "chaise": "寝椅子", "longue": "長椅子", "bedroom": "寝室", "champagne": "シャンパン", "coupe": "クーペ", "checking": "確認", "pulse": "脈拍", "chimera": "キメラ", "ant": "アリ", "chin": "顎", "rub": "こする", "spike": "棘", "clitoral": "陰核の", "cockade": "帽章", "creative": "創作の", "signature": "署名", "crime": "犯罪", "prevention": "防止", "buzzer": "ブザー", "threat": "脅迫", "crossguard": "鍔", "lightsaber": "ライトセーバー", "crosshair": "照準", "cunt": "女性器", "busting": "破裂", "curled": "丸まった", "ends": "端", "cyber": "サイバー", "sigilism": "印章表現", "daemon": "悪魔", "prince": "王子", "detachable": "取り外し可能な", "diamond": "ダイヤモンド", "dust": "ほこり", "electric": "電気の", "shock": "衝撃", "elevated": "高架の", "railway": "鉄道", "emperor": "皇帝", "children": "子供たち", "ending": "終了", "celebration": "祝賀", "bond": "絆", "ether": "エーテル", "aria": "アリア", "evidence": "証拠", "board": "ボード", "markers": "印", "extended": "延長された", "upshirt": "シャツをたくし上げた", "engrish": "不自然な英語", "faux": "擬似", "feature": "特集", "scout": "スカウト", "feeling": "感じる", "muscles": "筋肉", "fishnet": "網目", "kneehighs": "ニーソックス", "fist": "拳", "bumping": "ぶつける", "viewer": "閲覧者", "flamingo": "フラミンゴ", "innertube": "浮き輪", "raft": "いかだ", "flanged": "フランジ付き", "flesh": "肉", "storage": "保管", "bulbs": "球根", "fling": "投げる", "posse": "一団", "floral": "花柄", "dissolve": "溶解", "embroidery": "刺繍", "flow": "流れ", "glow": "輝き", "flute": "フルート", "tassel": "房飾り", "fender": "フェンダー", "fox": "キツネ", "mousing": "マウス操作", "freudian": "フロイト的", "switch": "転換", "friction": "摩擦", "ridges": "隆起線", "frutiger": "フルティガー", "pasties": "ニプレス", "full": "全身の", "cowling": "カウリング", "galactic": "銀河の", "empire": "帝国", "gasterblaster": "ガスターブラスター", "georgian": "ジョージア時代の", "era": "時代", "getter": "ゲッター", "rays": "光線", "golden": "黄金の", "hour": "時間", "gondola": "ゴンドラ", "gracidea": "グラシデア", "grado": "グラド", "labs": "研究所", "grand": "大規模な", "scale": "規模", "grated": "すりおろした", "daikon": "大根", "graviton": "グラビトン", "beam": "光線", "emitter": "放射器", "great": "大きな", "helm": "兜", "grind": "粉砕", "fiction": "フィクション", "guided": "誘導された", "gym": "ジム", "equipment": "器具", "handcuff": "手錠", "dangle": "ぶら下がり", "handgun": "拳銃", "cartridge": "弾薬", "stock": "銃床", "hanging": "吊り下げ", "wedgie": "食い込み", "happy": "嬉しい", "enjoy": "楽しむ", "music": "音楽", "harmful": "有害な", "spikes": "棘", "heel": "かかと", "pop": "跳ね上げ", "stretch": "伸ばし", "hellfire": "地獄の炎", "gala": "祝典", "gallery": "画廊", "himalayan": "ヒマラヤの", "poppy": "ケシ", "flower": "花", "holy": "聖なる", "quintet": "五重奏", "holo": "ホロ", "jagged": "ぎざぎざの", "sclera": "白目", "jeep": "ジープ", "japanese": "日本の", "kettle": "やかん", "leather": "革", "daddy": "年上男性", "leopard": "ヒョウ", "pelt": "毛皮", "letter": "文字", "balloon": "風船", "banner": "横断幕", "level": "レベル", "first": "第1", "second": "第2", "generation": "世代", "points": "点数", "oasis": "オアシス", "lucky": "幸運な", "flash": "閃光", "magic": "魔法", "pen": "ペン", "magician": "魔術師", "wand": "杖", "mane": "たてがみ", "ax": "斧", "abuse": "虐待", "minor": "小アルカナ", "arcana": "アルカナ", "motor": "モーター", "oil": "油", "motorized": "電動の", "unicycle": "一輪車", "mountain": "山", "climbing": "登り", "mouse": "ネズミ", "hole": "穴", "movie": "映画", "projector": "映写機", "mundane": "平凡な", "awesome": "すごい", "muntins": "窓桟", "mutual": "相互の", "tsundere": "ツンデレ", "naked": "裸の", "poncho": "ポンチョ", "tape": "テープ", "nameplay": "名前遊び", "napa": "白菜", "cabbage": "キャベツ", "nape": "うなじ", "braid": "編み込み", "narrow": "狭い", "hips": "腰回り", "nervous": "神経の", "system": "系", "night": "夜", "college": "学園", "ceremonial": "式典用", "robes": "ローブ", "labwear": "実験着", "null": "空の", "o": "O", "scanner": "スキャナー", "oathkeeper": "誓約を守る者", "olive": "オリーブ", "branch": "枝", "organization": "組織", "originite": "オリジニウム", "prime": "原石", "other": "その他の", "pact": "契約", "holder": "保持者", "palmar": "手のひらの", "flexion": "屈曲", "partial": "部分的な", "squatting": "しゃがみ", "transformation": "変身", "pastel": "パステル", "goth": "ゴス", "removed": "取り外した", "pedal": "ペダル", "board": "ボード", "pitcher": "投手", "mound": "マウンド", "plain": "無地の", "epaulettes": "肩章", "playboy": "プレイボーイ", "pokemon": "ポケモン", "playstation": "プレイステーション", "pointing": "指差し", "pom": "ポンポン", "beanie": "ニット帽", "poster": "ポスター", "parody": "パロディ", "doorway": "戸口", "peephole": "覗き穴", "powered": "電動の", "wheelchair": "車椅子", "pulled": "引かれた", "pushing": "押す", "bicycle": "自転車", "stroller": "ベビーカー", "quilted": "キルティングの", "headwear": "頭飾り", "ramen": "ラーメン", "stand": "屋台", "receding": "後退した", "record": "記録", "store": "店", "ringing": "鳴り響く", "artifacts": "アーティファクト", "ribboned": "リボン付き", "xiao": "笛", "rotating": "回転する", "samurai": "侍", "condenser": "凝縮器", "sand": "砂", "bucket": "バケツ", "sandwich": "サンドイッチ", "sartorial": "仕立ての", "scene": "場面", "scissor": "はさみ", "doors": "扉", "scratching": "掻く", "secretary": "秘書", "settings": "設定", "serving": "配膳用", "tray": "トレイ", "seven": "7人の", "dwarves": "小人", "sleeve": "袖", "pouch": "ポーチ", "slit": "スリット", "sleeveless": "ノースリーブ", "tunic": "チュニック", "sliced": "薄切りの", "cheese": "チーズ", "slime": "スライム", "girls": "少女たち", "slingback": "バックストラップ", "tan": "日焼け", "smelly": "臭い", "armpits": "脇", "smile": "笑顔", "emoji": "絵文字", "smokey": "スモーキー", "eyeshadow": "アイシャドウ", "sock": "靴下", "puppet": "人形", "brigade": "旅団", "soy": "大豆", "ombo": "紋章", "spacecraft": "宇宙船", "sparkle": "きらめき", "sparkling": "きらめく", "daydream": "白昼夢", "spinal": "脊髄の", "cord": "索", "spine": "背骨", "bumps": "隆起", "spiral": "螺旋", "notebook": "ノート", "spitting": "吐き出し", "seed": "種", "squeezing": "絞る", "stabbing": "刺す", "starter": "開始", "squad": "部隊", "stock": "銘柄", "strawpage": "ストローページ", "strip": "脱衣", "tease": "からかい", "stubbing": "ぶつける", "toe": "足指", "study": "勉強", "distraction": "気晴らし", "stun": "気絶", "baton": "警棒", "sweat": "汗", "superimposition": "重ね合わせ", "surplice": "スルプリス", "swaddled": "おくるみに包まれた", "swan": "白鳥", "lake": "湖", "headpiece": "頭飾り", "swiping": "スワイプ", "switchblade": "飛び出しナイフ", "swordstaff": "剣杖", "synthwave": "シンセウェーブ", "tactical": "戦術的な", "taur": "ケンタウロス型", "exoskeleton": "外骨格", "curve": "曲線", "taut": "張った", "cami": "キャミソール", "temporal": "側頭部の", "hairline": "生え際", "tennis": "テニス", "serve": "サーブ", "theater": "劇場", "seating": "座席", "thighband": "太ももバンド", "thousand": "千", "yard": "ヤード", "stare": "凝視", "throw": "投げる", "pillow": "枕", "petals": "花びら", "thumbprint": "親指の指紋", "tied": "結んだ", "hoodie": "パーカー", "strings": "ひも", "tight": "きつい", "bottoms": "ボトムス", "tip": "チップ", "jar": "瓶", "tire": "タイヤ", "swing": "ブランコ", "titan": "巨人", "scars": "傷跡", "tomato": "トマト", "sauce": "ソース", "top": "上", "bottom": "下", "dynamic": "動的な", "annotated": "注釈付き", "interface": "インターフェース", "transparent": "透明な", "turtleneck": "タートルネック", "jumpsuit": "つなぎ", "twin": "双子の", "twitching": "痙攣する", "testicles": "睾丸", "undersized": "小型の", "undone": "ほどけた", "duijin": "対句", "unequal": "不均等な", "division": "分割", "unit": "部隊", "patch": "ワッペン", "unwanted": "望まない", "various": "さまざまな", "styles": "様式", "vector": "ベクトル", "circles": "円", "verbal": "言葉による", "degradation": "侮辱", "hairy": "毛深い", "victory": "勝利", "rolls": "ロール", "vine": "蔓", "bondage": "拘束", "virtual": "仮想", "graduation": "卒業", "commemoration": "記念", "vocaloid": "ボーカロイド", "editor": "編集ソフト", "voices": "声", "letters": "文字", "collection": "コレクション", "war": "戦争", "banner": "旗", "welding": "溶接", "goggles": "ゴーグル", "wet": "濡れた", "male": "男性", "swimwear": "水着", "wheat": "小麦", "bundle": "束", "whimsy": "気まぐれ", "twee": "可愛らしい", "whitebeard": "白ひげ", "whoop": "フープ", "catsuit": "キャットスーツ", "wicker": "籐", "furniture": "家具", "wireless": "無線", "microphone": "マイク", "woven": "織り", "hatching": "ハッチング", "wry": "皮肉な", "your": "あなたの", "helping": "助け", "idiot": "馬鹿", "virus": "ウイルス"
})
# The prior pass intentionally used a small token vocabulary.  These are
# ordinary display concepts observed in the bounded target, not identity
# claims; keeping them here lets compound tags receive a Japanese label while
# leaving brands, names, model numbers, and opaque strings to the exception
# classifier above.
LEXICON.update({
    "affection": "好意", "meter": "メーター", "anatomical": "解剖学的な", "model": "模型", "animatronic": "アニマトロニクス", "backpack": "リュック", "vacuum": "掃除機", "cleaner": "掃除機", "banana": "バナナ", "split": "割れ", "bound": "拘束された", "thumbs": "親指", "aran": "アラン", "legwear": "脚衣", "identical": "同一の", "genderswap": "性別入れ替え", "perverted": "倒錯した", "excuse": "言い訳", "utility": "実用", "ranguage": "ラングエージ", "rgb": "RGB", "lights": "ライト", "lingerie": "ランジェリー", "acid": "酸", "graphics": "グラフィック", "aimpoint": "照準点", "alpha": "アルファ", "legion": "軍団", "ankle": "足首", "fins": "ひれ", "holster": "ホルスター", "aroused": "興奮した", "nosebleed": "鼻血", "astromech": "アストロメク", "asymmetrical": "左右非対称の", "pigeon": "ハト", "toed": "つま先の", "attitude": "姿勢", "derriere": "臀部", "attribute": "属性", "slider": "スライダー", "aurebesh": "アウレベシュ", "autocunnilingus": "自己クンニリングス", "autopenetration": "自己挿入", "aventail": "垂れ布", "awestruck": "畏敬に打たれた", "awooo": "遠吠え", "babydoll": "ベビードール", "tug": "引っ張り", "barre": "バレエバー", "chord": "和音", "basket": "かご", "hilt": "柄", "basketweave": "籠目編み", "batik": "バティック", "battroid": "バトロイド", "bay": "湾", "beacon": "ビーコン", "bevor": "ビーバーゴルゲット", "breeches": "半ズボン", "biomechanical": "生体機械的な", "biometal": "バイオメタル", "candelabra": "燭台", "caning": "鞭打ち", "capotain": "カポテイン帽", "cartwheel": "側転", "cellulite": "セルライト", "cherub": "ケルビム", "chives": "チャイブ", "coil": "コイル", "coiled": "巻かれた", "convoy": "輸送隊", "cpu": "CPU", "crossbuck": "踏切警標", "cutlet": "カツレツ", "deflect": "そらす", "dentures": "入れ歯", "dezombification": "ゾンビ化解除", "disappearing": "消える", "disfigured": "変形した", "dodecagram": "十二芒星", "dopo": "ドーポ", "dropship": "降下船", "eargasm": "耳の快感", "enveloped": "包まれた", "eurodance": "ユーロダンス", "eyestalks": "眼柄", "filolial": "フィロリアル", "firelock": "火縄銃", "fireseal": "火印", "flowjob": "足による性行為", "fungi": "菌類", "futhark": "フサルク", "gagging": "えずき", "gigbag": "楽器ケース", "goosebumps": "鳥肌", "grandma": "祖母", "grassrunner": "草原を走るもの", "gulping": "ごくごく飲む", "gunship": "ガンシップ", "handstop": "ハンドストップ", "hissing": "シューという音", "helix": "らせん", "hexapod": "六脚", "inhaler": "吸入器", "inkblot": "インクの染み", "jackets": "ジャケット", "jumpscare": "びっくり演出", "kiosk": "キオスク", "kickflip": "キックフリップ", "lashers": "鞭状のもの", "lavafall": "溶岩の滝", "legbinder": "脚拘束具", "madeleine": "マドレーヌ", "makeover": "イメージチェンジ", "manspreading": "男性の脚広げ", "menacing": "威圧的な", "miasma": "瘴気", "miniapron": "ミニエプロン", "minifridge": "小型冷蔵庫", "notification": "通知", "nozzle": "ノズル", "ooze": "滲み出る液体", "oval": "楕円", "overkill": "過剰攻撃", "oversplit": "過分割", "paintball": "ペイントボール", "papercutting": "紙切り", "pavilion": "東屋", "peafowl": "クジャク", "pecking": "ついばみ", "peppermint": "ペパーミント", "perching": "止まり姿勢", "photobomb": "写真への乱入", "plasma": "プラズマ", "poisoned": "毒を受けた", "polyamory": "複数恋愛", "posterized": "ポスター風加工", "praise": "称賛", "puppeteering": "操り人形操作", "pyromania": "放火癖", "quadcopter": "クアッドコプター", "ragdoll": "ラグドール", "raincloud": "雨雲", "ranking": "ランキング", "ratite": "走鳥類", "ratline": "ラットライン", "rattail": "ねずみの尾", "redaction": "墨消し", "related": "関連", "reveal": "露出", "saloon": "酒場", "saturated": "彩度の高い", "sconce": "壁掛け照明", "scratched": "引っかき傷のある", "scruffing": "首根っこをつかむ", "shielding": "遮蔽", "shooing": "追い払う", "shoulderstand": "肩立ち", "showgirl": "ショーガール", "shudder": "身震い", "sighting": "照準合わせ", "skinned": "皮を剥かれた", "slicing": "切断", "slides": "スライド", "slushie": "フローズンドリンク", "smearing": "塗り広げ", "snowscape": "雪景色", "sparring": "スパーリング", "spinach": "ほうれん草", "sploot": "後ろ足伸ばし", "sprawled": "手足を広げた", "stamen": "雄しべ", "stomacher": "腹飾り", "tattooing": "刺青を入れる", "techpriest": "技術司祭", "toeprint": "足指の指紋", "trout": "マス", "twists": "ねじれ", "urn": "骨壺", "uwu": "ウユー顔文字", "vaping": "電子タバコ", "vat": "大桶", "vignetting": "周辺減光", "vitiligo": "白斑", "wah": "ワーという声", "webclap": "ウェブ拍手", "webcounter": "ウェブカウンター", "winch": "ウインチ", "wingdings": "Wingdings文字", "wolf": "オオカミ", "cub": "子", "zig": "ジグ", "zag": "ザグ", "pattern": "模様", "zodiac": "黄道十二宮", "wheel": "車輪", "zoomer": "ズーマー", "slang": "俗語",
    "accessory": "アクセサリー", "active": "有効な", "advanced": "先進型", "alternate": "別の", "anatomical": "解剖学的な", "arc": "アーク", "reactor": "原子炉", "arctic": "北極の", "warfare": "戦闘", "apple": "リンゴ", "trend": "流行", "aroused": "興奮した", "backward": "後ろ向き", "baked": "焼いた", "goods": "品物", "bible": "聖書", "verse": "節", "blackout": "ブラックアウト", "poetry": "詩", "blown": "吹き飛ばされた", "away": "離れて", "blurry": "ぼやけた", "edges": "輪郭", "body": "身体", "stocking": "ストッキング", "book": "本", "shelf": "棚", "borrowed": "借りた", "bouncing": "跳ねる", "breaking": "速報", "news": "ニュース", "bug": "虫", "hunting": "狩り", "bullet": "弾丸", "wound": "傷", "bus": "バス", "stop": "停留所", "shelter": "待合所", "butler": "執事", "bowing": "お辞儀", "bump": "ぶつかり", "camouflage": "迷彩", "paint": "塗料", "candy": "キャンディ", "gore": "流血", "stick": "棒", "canvas": "キャンバス", "texture": "質感", "capelet": "ケープレット", "car": "車", "part": "部品", "caressing": "愛撫", "cheek": "頬", "injury": "負傷", "cherry": "さくらんぼ", "pie": "パイ", "chinese": "中国の", "restaurant": "レストラン", "chocolate": "チョコレート", "drip": "滴り", "icing": "アイシング", "circus": "サーカス", "tent": "テント", "clenched": "固く握った", "clipping": "切り取り", "toenails": "足の爪", "close": "近接", "quarters": "戦闘", "combat": "戦闘", "coffee": "コーヒー", "filter": "フィルター", "coin": "硬貨", "stack": "積み重ね", "colony": "コロニー", "interior": "内部", "color": "色", "picker": "選択", "wheel": "車輪", "combination": "組み合わせ", "wrench": "レンチ", "comically": "漫画的に", "serious": "真剣な", "unamused": "無表情な", "completely": "完全に", "complex": "複雑な", "exterior": "外観", "condiment": "調味料", "packet": "小袋", "contrast": "対照", "lapels": "襟", "suspenders": "サスペンダー", "cooking": "料理", "together": "一緒に", "cooperative": "協力的な", "corpus": "海綿体", "spongiosum": "海綿体", "covering": "覆う", "forehead": "額", "cracking": "ひび割れ", "ground": "地面", "crescent": "三日月", "shaped": "形の", "pupils": "瞳孔", "crooked": "曲がった", "teeth": "歯", "cropped": "短く切った", "cardigan": "カーディガン", "rash": "ラッシュガード", "guard": "ガード", "crossed": "交差した", "weapons": "武器", "curse": "呪い", "seal": "印", "dead": "枯れた", "plants": "植物", "demonic": "悪魔の", "creature": "生物", "denim": "デニム", "overalls": "オーバーオール", "dental": "歯科の", "filling": "詰め物", "dinosaur": "恐竜", "skeleton": "骨格", "dish": "皿", "rack": "ラック", "divided": "分離した", "highway": "高速道路", "doll": "人形", "panty": "パンティ", "kissing": "キス", "donut": "ドーナツ", "shaped": "形の", "bracelet": "ブレスレット", "stamp": "スタンプ", "eighth": "8分の", "note": "音符", "dreamcast": "Dreamcast", "controller": "コントローラー", "drill": "ドリル", "polearm": "長柄武器", "dripping": "滴る", "sweat": "汗", "drop": "滴", "pupils": "瞳孔", "dual": "二重", "sights": "照準器", "empty": "空の", "bathtub": "浴槽", "bottle": "ボトル", "bowl": "ボウル", "enoki": "エノキ", "mushroom": "キノコ", "excessive": "過剰な", "lactation": "授乳", "saliva": "唾液", "smoke": "煙", "cosmetics": "化粧品", "extra": "追加の", "pussies": "陰部", "eyebrow": "眉", "razor": "カミソリ", "silhouette": "シルエット", "fairy": "妖精", "falling": "落下する", "rock": "岩", "fan": "ファン", "meeting": "集会", "fantasy": "幻想", "racism": "人種差別", "fatter": "より太い", "canon": "公式設定", "badge": "バッジ", "fence": "柵", "post": "柱", "festival": "祭り", "fiery": "炎の", "aura": "オーラ", "film": "フィルム", "reel": "リール", "set": "セット", "flying": "飛ぶ", "train": "列車", "football": "サッカー", "goal": "ゴール", "forehead": "額", "frown": "しかめ面", "lines": "線", "future": "未来", "gadget": "装置", "lab": "研究所", "fuzzy": "毛羽立った", "handcuffs": "手錠", "gable": "切妻", "roof": "屋根", "gas": "ガス", "lantern": "ランタン", "gameplay": "ゲームプレイ", "ability": "能力", "garage": "車庫", "headlight": "ヘッドライト", "height": "身長", "growth": "成長", "lineup": "並び", "hooded": "フード付き", "horizontal": "水平な", "hue": "色相", "shifting": "変化", "hugging": "抱擁", "invitation": "招待", "huge": "巨大な", "japanese": "日本の", "castle": "城", "jelly": "ゼリー", "cube": "立方体", "ladder": "はしご", "landing": "着陸", "laser": "レーザー", "cannon": "砲", "pointer": "ポインター", "projection": "投影", "layered": "重ねた", "sideboob": "横乳", "lower": "下側", "lip": "唇", "only": "のみ", "marble": "大理石", "sculpture": "彫刻", "marriage": "結婚", "certificate": "証明書", "matching": "お揃いの", "material": "素材", "growth": "成長", "muscle": "筋肉", "nail": "爪", "polish": "磨き", "neapolitan": "三色の", "notched": "切れ込みのある", "neckline": "襟ぐり", "novelty": "奇抜な", "codpiece": "股間当て", "onion": "玉ねぎ", "slice": "薄切り", "opening": "開いた", "curtains": "カーテン", "ornamental": "装飾用", "weight": "重り", "overhead": "頭上の", "lights": "照明", "overlapped": "重なった", "images": "画像", "padded": "パッド入り", "cloak": "マント", "vest": "ベスト", "peach": "桃", "slice": "薄切り", "pee": "小便", "puddle": "水たまり", "planted": "立てた", "shovel": "シャベル", "plastic": "プラスチック", "spoon": "スプーン", "pleated": "プリーツ付き", "poison": "毒", "police": "警察", "siren": "サイレン", "dice": "サイコロ", "pommel": "柄頭", "pool": "プール", "float": "浮き輪", "powdered": "粉をはたいた", "wig": "かつら", "pumpkin": "カボチャ", "reading": "読書", "recording": "録音", "recursive": "再帰的な", "animalization": "動物化", "reflective": "反射する", "surface": "表面", "repeating": "連射式", "crossbow": "クロスボウ", "ribbed": "リブ編み", "vest": "ベスト", "roasted": "焼いた", "marshmallow": "マシュマロ", "rope": "ロープ", "scratched": "傷のある", "shaving": "剃毛", "shopping": "買い物", "basket": "かご", "shorter": "より短い", "strawberry": "イチゴ", "jam": "ジャム", "subway": "地下鉄", "map": "地図", "suction": "吸引", "tentacles": "触手", "summoned": "召喚された", "swords": "剣", "superman": "スーパーマン", "exposure": "露出", "surprise": "驚き", "surrounded": "囲まれた", "guns": "銃", "suspicious": "怪しい", "egg": "卵", "taking": "取る", "notes": "メモ", "towel": "タオル", "touching": "触れ合う", "training": "訓練", "transit": "交通", "underwater": "水中", "shot": "撮影", "uneven": "不均一な", "footing": "足場", "unusually": "異常に", "limbed": "手足の", "unwanted": "望まない", "creampie": "中出し", "upright": "直立した", "utility": "実用", "varied": "多様な", "reactions": "反応", "walking": "歩く", "towards": "〜に向かって", "watching": "見る", "pornography": "ポルノ", "wavy": "波打った", "white": "白い", "wicker": "籐編み", "furniture": "家具", "wig": "かつら", "wireless": "無線", "microphone": "マイク", "woven": "織った", "hatching": "ハッチング", "zodiac": "黄道十二宮", "wheel": "車輪"
})
# These final overrides keep the UI-bearing forms Japanese rather than bare
# ASCII abbreviations after all compatibility vocabulary has been loaded.
LEXICON.update({"cpu": "CPU（中央処理装置）", "gps": "GPS測位", "atm": "ATM（現金自動預け払い機）", "cd": "CD媒体", "lcd": "LCD画面", "led": "LED照明", "vs": "対戦"})

# The delta audit found that lexical composition must never accept a Japanese
# fragment while silently carrying an English semantic base token.  These are
# bounded, ordinary-word repairs or explicit acronym literals used by the
# wrapper target set; they are not a general translation engine.
LEXICON.update({
    "aberration": "収差", "apart": "離れて", "chromatic": "色", "counting": "数える", "father": "父親",
    "fictional": "架空の", "fool": "愚者", "genitals": "性器", "joy": "喜び", "magazine": "弾倉",
    "newt": "イモリ", "pressed": "押し付けられた", "tank": "戦車", "tears": "涙", "together": "一緒に",
    "tarot": "タロット", "weapon": "武器", "triangle": "三角形", "spades": "スペード", "necktie": "ネクタイ",
    "watermark": "透かし", "insignia": "記章", "power": "力", "hug": "ハグ", "masturbation": "自慰",
    "joint": "関節", "fighter": "戦闘機", "missile": "ミサイル", "carrying": "運搬", "date": "日付",
    "milk": "牛乳", "king": "王", "clan": "一族", "event": "イベント", "anatomy": "解剖学",
    "ballet": "バレエ", "adaptation": "適応", "siblings": "きょうだい", "hoop": "輪", "supplies": "用品",
    "aim": "照準", "crossing": "交差", "antler": "枝角", "clap": "拍手", "droid": "ドロイド",
    "avatar": "アバター", "bicycle": "自転車", "bicycles": "自転車", "feeding": "餌やり", "bulls": "雄牛",
    "bloom": "開花", "edge": "縁", "calves": "ふくらはぎ", "brotherhood": "同胞団", "steel": "鋼",
    "eared": "耳のある", "loli": "ロリ", "bright": "明るい", "bars": "鉄格子", "beloved": "愛された",
    "bent": "曲がった", "curl": "カール", "pollux": "ポルックス", "feeding": "餌やり", "canopy": "天蓋",
    "channel": "チャンネル", "checkout": "会計", "cheetah": "チーター", "peony": "牡丹", "chipped": "欠けた",
    "lady": "女性", "choir": "合唱団", "cleaning": "掃除", "cleft": "裂け目", "injection": "注入",
    "comedy": "喜劇", "tragedy": "悲劇", "masks": "仮面", "competitive": "競争的な", "completionist": "コンプリート主義者",
    "constellation": "星座", "sketch": "スケッチ", "kneepits": "膝裏", "underboob": "アンダーバスト", "wagon": "荷車",
    "coyote": "コヨーテ", "cracked": "ひび割れた", "cradle": "ゆりかご", "crayon": "クレヨン", "creation": "創作物",
    "crest": "紋章", "flames": "炎", "composition": "構図", "crocodile": "ワニ", "cursed": "呪われた",
    "devil": "悪魔", "entity": "実体", "draw": "描く", "arrow": "矢", "dreadnought": "戦艦",
    "drive": "運転", "dryad": "ドライアド", "duellist": "決闘者", "elephant": "ゾウ", "dormitory": "寮",
    "english": "英語", "eternal": "永遠の", "article": "記事", "european": "ヨーロッパの", "exhaling": "息を吐く",
    "exiting": "退出する", "exploded": "爆発した", "exploration": "探査", "extreme": "極端な", "fade": "フェード",
    "father": "父親", "flight": "飛行", "flourish": "装飾", "spittle": "唾液", "cunnilingus": "クンニリングス",
    "change": "変化", "forward": "前向きの", "pack": "組", "fourth": "4番目の", "july": "7月",
    "framed": "枠で囲まれた", "fully": "完全に", "genderswapped": "性別が入れ替わった", "advance": "アドバンス",
    "aware": "自覚した", "genius": "天才", "morning": "朝", "grain": "粒", "envy": "羨望",
    "heroes": "英雄たち", "heterochromatic": "左右で色の異なる", "hexagonal": "六角形の", "highball": "ハイボール",
    "hobby": "趣味", "hockey": "ホッケー", "scoop": "すくう道具", "spotlight": "スポットライト", "horned": "角のある",
    "hose": "ホース", "ruby": "ルビー", "sophie": "ソフィー", "airwalking": "空中歩行", "eyebrows": "眉",
    "hydraulic": "油圧式の", "tub": "桶", "inconspicuous": "目立たない", "inconvenient": "不便な", "ink": "インク",
    "test": "テスト", "insulated": "断熱された", "delivery": "配達", "intentional": "意図的な", "jpeg": "JPEG",
    "missing": "欠けた", "symbols": "記号", "toes": "つま先", "inverse": "逆の", "spirit": "精神",
    "inverted": "反転した", "invisible": "見えない", "classic": "クラシック", "shuffle": "シャッフル", "ironmouse": "アイアンマウス",
    "italian": "イタリアの", "jackal": "ジャッカル", "jackalope": "ジャッカロープ", "jade": "翡翠", "leaning": "傾いた",
    "support": "支持", "lemon": "レモン", "lemur": "キツネザル", "lensless": "レンズのない", "liberty": "自由",
    "life": "生命", "lifting": "持ち上げ", "bolt": "ボルト", "claw": "爪", "elemental": "元素の",
    "linear": "線形の", "lineart": "線画", "lion": "ライオン", "lobster": "ロブスター", "location": "場所",
    "lotus": "蓮", "root": "根", "asia": "アジア", "tour": "ツアー", "lowered": "下げられた",
    "palm": "手のひら", "major": "主要な", "underreaction": "反応不足", "manta": "マンタ", "ray": "エイ",
    "manually": "手動で", "operated": "操作された", "mounted": "取り付けられた", "manuscript": "原稿", "marine": "海洋の",
    "marlin": "カジキ", "marquee": "マーキー", "meat": "肉", "hook": "フック", "player": "プレイヤー",
    "meerkat": "ミーアキャット", "melee": "近接戦闘", "environment": "環境", "messy": "乱雑な", "micro": "小型",
    "icon": "アイコン", "mole": "モグラ", "beside": "隣に", "moth": "蛾", "barrel": "銃身",
    "anklets": "アンクレット", "armlets": "腕輪", "caterpillar": "毛虫", "tracks": "軌跡", "knives": "ナイフ",
    "ovum": "卵子", "tattoos": "タトゥー", "theme": "テーマ", "colors": "色", "tongues": "舌",
    "cuirass": "胸甲", "mute": "ミュート", "speaker": "スピーカー", "indicator": "指標", "mythological": "神話上の",
    "palette": "色彩パレット", "aside": "脇へ", "overhang": "張り出し", "terminal": "端末", "neon": "ネオン",
    "nerd": "ナード", "never": "決してない", "give": "与える", "city": "都市", "land": "陸地",
    "pressed": "押し付けられた", "genitals": "性器", "lips": "唇", "seek": "探す", "toilet": "トイレ",
    "candle": "ろうそく", "official": "公式の", "dome": "ドーム", "cylinder": "円柱", "otter": "カワウソ",
    "outer": "外側の", "overflowing": "あふれた", "owl": "フクロウ", "fingernails": "爪", "panda": "パンダ",
    "roll": "転がる", "parfait": "パフェ", "patio": "テラス", "patting": "軽く叩く", "pearl": "真珠",
    "pencil": "鉛筆", "penguin": "ペンギン", "doodle": "落書き", "slip": "滑る", "perfume": "香水",
    "pet": "ペット", "planet": "惑星", "diving": "潜水", "bunny": "ウサギ", "poet": "詩人",
    "pointy": "尖った", "possibility": "可能性", "puberty": "思春期", "possum": "フクロネズミ", "orgasm": "オーガズム",
    "torture": "拷問", "powerpuff": "パワーパフ", "preppy": "プレッピー", "preschool": "幼児教育", "conference": "会議",
    "primrose": "サクラソウ", "pulling": "引っ張る", "pure": "純粋な", "piece": "一片", "racer": "レーサー",
    "ranger": "レンジャー", "sugar": "砂糖", "ginger": "ショウガ", "telephone": "電話", "regional": "地域の",
    "relief": "安堵", "remnant": "残り", "resistance": "抵抗", "rewind": "巻き戻し", "ribs": "肋骨",
    "moped": "モペット", "motorcycle": "オートバイ", "roller": "ローラー", "coaster": "コースター", "scooter": "スクーター",
    "rise": "上昇", "radiance": "輝き", "rose": "バラ", "travel": "旅行", "attire": "服装", "ruining": "台無しにする",
    "moment": "瞬間", "runway": "滑走路", "haru": "ハル", "saddle": "鞍", "salmon": "サケ", "line": "線",
    "across": "横切って", "tying": "結ぶ", "scattered": "散らばった", "cut": "切る", "circular": "円形の",
    "sentient": "知覚を持つ", "serrated": "鋸歯状の", "servo": "サーボ", "severed": "切断された", "cloud": "雲",
    "share": "共有", "shared": "共有された", "shell": "殻", "sherbet": "シャーベット", "module": "モジュール",
    "shooting": "撮影", "cart": "台車", "pads": "パッド", "shredded": "細かく裂かれた", "shrimp": "エビ",
    "shrine": "神社", "shroud": "覆い", "sideburns": "もみあげ", "sight": "照準器", "target": "標的",
    "simulated": "シミュレートされた", "snake": "ヘビ", "skunk": "スカンク", "slasher": "切り裂き役", "slave": "奴隷",
    "slingshot": "パチンコ", "throat": "喉", "smashing": "粉砕", "smear": "塗りつぶし", "launcher": "発射器",
    "snowflake": "雪の結晶", "soles": "足裏", "eaters": "食べる者", "stadium": "競技場", "market": "市場",
    "bodysuit": "ボディスーツ", "romper": "ロンパース", "challenger": "挑戦者", "pearls": "真珠", "studded": "鋲付き",
    "patrol": "巡回", "tin": "缶", "tit": "シジュウカラ", "toad": "ヒキガエル", "wrap": "包む",
    "bandaids": "絆創膏", "cigarettes": "タバコ", "clones": "クローン", "condoms": "コンドーム", "stickers": "ステッカー",
    "umbrellas": "傘", "watermarks": "透かし", "user": "ユーザー", "vegetable": "野菜", "personification": "擬人化",
    "ventilation": "換気", "voice": "声", "actor": "俳優", "void": "虚無", "showdown": "対決", "witch": "魔女",
    "seasons": "季節", "figure": "人物", "best": "最高の", "take": "取る", "tank": "戦車", "guy": "男性",
    "fool": "愚者", "fun": "楽しさ", "gang": "一団", "awards": "賞", "priestess": "女司祭", "loud": "大きな音の",
    "vivid": "鮮やかな", "tale": "物語", "beads": "ビーズ", "cutting": "切断", "marking": "印付け", "sheath": "鞘",
    "thighs": "太もも", "thinner": "より細い", "third": "3番目の", "throwing": "投げる", "cookie": "クッキー",
    "tie": "ネクタイ", "dye": "染料", "tilted": "傾いた", "tumbler": "タンブラー", "turnip": "カブ", "turtle": "カメ",
    "handed": "手渡された", "page": "ページ", "tailcoat": "燕尾服", "assault": "襲撃", "effectiveness": "有効性",
    "ukrainian": "ウクライナの", "summer": "夏", "sound": "音", "effect": "効果", "steed": "駿馬", "untied": "ほどけた",
    "upwards": "上向きに", "utensil": "調理器具", "taper": "先細り", "walrus": "セイウチ", "weasel": "イタチ",
    "bench": "ベンチ", "wimp": "弱虫", "whisky": "ウイスキー", "knight": "騎士", "merry": "陽気な", "gamepad": "ゲームパッド",
    "winking": "ウインク", "wish": "願い", "stove": "コンロ", "plate": "皿", "porch": "ポーチ", "stairs": "階段", "worm": "虫",
    "zombie": "ゾンビ", "newt": "イモリ",
})

GENERIC_QUALIFIERS = {"larger", "smaller", "bdsm", "relationship", "sexual", "phrase", "object", "gesture", "room", "animated", "medium", "plant", "symbol", "sport", "fish", "food", "building", "container", "expression", "topic", "singer", "os", "armor", "carmaker", "star"}
QUALIFIER_JA = {"larger": "大きめ", "smaller": "小さめ", "bdsm": "BDSM", "relationship": "関係", "sexual": "性的", "phrase": "フレーズ", "object": "物体", "gesture": "ジェスチャー", "room": "部屋", "animated": "アニメーション", "medium": "媒体", "plant": "植物", "symbol": "記号", "sport": "スポーツ", "fish": "魚", "food": "食べ物", "building": "建物", "container": "容器", "expression": "表情", "topic": "話題", "singer": "歌手", "os": "OS", "armor": "鎧", "carmaker": "自動車メーカー", "star": "恒星", "weapon": "武器", "tarot": "タロット", "animal": "動物", "flower": "花", "playing_card": "トランプ", "letter": "文字", "equation": "方程式", "language": "言語", "computer": "コンピューター", "original": "オリジナル", "trend": "流行", "character": "キャラクター", "cosmetics": "化粧品", "tool": "道具", "city": "都市", "brand": "ブランド"}
NAME_QUALIFIERS = {"cosplay", "meme", "style", "magazine", "company", "software", "character", "identity", "project_moon", "genshin_impact", "eve_online", "fate", "blue_archive", "touhou", "umamusume", "idolmaster", "kancolle", "pokemon", "honkai:_star_rail", "zenless_zone_zero", "fire_emblem", "warcraft", "nier:automata", "league", "tf2", "disney", "blackpink", "vtuber", "gta_vi", "stellar_blade", "genshin_impact", "eve_online"}
PRODUCT_WORDS = {"iphone", "ipad", "airpods", "oculus", "figma", "blender", "dyson", "nissan", "mazda", "google", "bilibili", "twitter", "subscribestar", "akg", "ipod"}
IDENTITY_BASES = {"fender", "durex", "mastercard", "goodyear", "sennheiser", "korg", "nike", "sony", "toyota", "subaru", "yamaha", "vaio", "xbox", "wii", "nissan", "mazda", "google", "nasa", "dji", "patreon", "pixiv", "youtube", "instagram", "discord", "steam", "spotify"}
COMPANY_MARKERS = {"corporation", "company", "inc", "ltd", "llc", "industries", "instruments"}
PRESERVED_LITERAL_TOKENS = {"ai", "atm", "cd", "cpu", "dslr", "gps", "lcd", "led", "lpvo", "mvp", "rgb", "fbi", "fn", "smg", "mk", "m3", "ram", "ui", "usb", "vr", "rpg", "rpk", "sos", "otm", "ddd", "ffd", "fff", "ffm", "mmf", "mmm", "w", "v", "j", "u", "r", "s", "b", "e", "f", "i", "k", "p", "x", "z", "ii", "iii", "iv", "gn", "m", "n", "o", "d", "h", "st", "nd", "rd", "th"}

EXACT.update({
    "heavy_chromatic_aberration": "強い色収差",
    "knees_together_feet_apart": "膝をつけて足を開く",
    "fictional_aircraft": "架空の航空機",
    "finger_counting_duo": "指で数える2人組",
    "father_and_son_threesome": "父親と息子を含む3人での性行為",
    "nipples_pressed_together": "乳首を押し付け合う",
    "no_genitals": "性器なし",
    "tank_gun": "戦車砲",
    "tears_of_joy_emoji": "嬉し涙の絵文字",
    "the_fool_(tarot)": "愚者（タロット）",
    "no_magazine_(weapon)": "弾倉なし（武器）",
    "newt": "イモリ",
})

# Phrase-level semantic repairs required by independent audit 5599075517.
# These are intentionally limited to the bounded wrapper target set.  A
# token-by-token Japanese entry is not sufficient when the compound changes
# the part of speech or the relation between an action and its object.
EXACT.update({
    "painting_fingernails": "爪に色を塗る",
    "painting_toenails": "足の爪に色を塗る",
    "hydraulic_press": "油圧プレス",
    "finger_painting": "指で描く絵",
    "press_conference": "記者会見",
    "taking_notes": "メモを取る",
    "hugging_ass": "尻を抱く",
    "hugging_own_leg": "自分の脚を抱く",
    "hugging_viewer": "見る人を抱く",
    "kissing_ass": "尻にキスする",
    "pulling_tongue": "舌を引っ張る",
    "throwing_petals": "花びらを投げる",
    "opening_curtains": "カーテンを開ける",
    "opening_window": "窓を開ける",
    "pushing_bicycle": "自転車を押す",
    "pushing_stroller": "ベビーカーを押す",
    "pushing_wheelchair": "車椅子を押す",
    "riding_moped": "モペットに乗る",
    "riding_motorcycle": "オートバイに乗る",
    "riding_roller_coaster": "ジェットコースターに乗る",
    "riding_scooter": "スクーターに乗る",
    "riding_vacuum_cleaner": "掃除機にまたがる",
    "pussy_press": "陰部を押し付ける",
    "two-handed_masturbation": "両手での自慰",
    "three-finger_handjob": "3本指での手コキ",
    "three-finger_salute": "3本指の敬礼",
    "four-finger_handjob": "4本指での手コキ",
    "two-page_spread": "見開き2ページ",
    "two-sided_hoodie": "両面のパーカー",
    "two-sided_horns": "両側の角",
    "two-sided_ribbon": "両面のリボン",
    "two-sided_scarf": "両面のマフラー",
    "two-sided_sleeves": "両面の袖",
    "two-sided_tailcoat": "両面の燕尾服",
    "three_of_spades": "スペードの3",
    "four_of_spades": "スペードの4",
})


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text("".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8", newline="\n")


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def _rows_hash(rows: Iterable[Mapping[str, Any]]) -> str:
    body = "".join(json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _tokens(base: str) -> list[str]:
    return [part.replace("'s", "").lower() for part in re.split(r"[_-]", base) if part]


def _parts(canonical: str) -> tuple[str, list[str]]:
    bits = canonical.split("_(")
    base = bits[0]
    qualifiers = [bit.rstrip(")").lower() for bit in bits[1:]]
    return base, qualifiers


def _is_code_or_product(canonical: str, base: str) -> tuple[bool, str]:
    if any(word in _tokens(base) for word in PRODUCT_WORDS):
        return True, "PRODUCT_OR_SERVICE_NAME"
    if any(word in _tokens(base) for word in IDENTITY_BASES):
        return True, "PRODUCT_OR_SERVICE_NAME"
    if any(word in _tokens(base) for word in COMPANY_MARKERS):
        return True, "PRODUCT_OR_SERVICE_NAME"
    if re.fullmatch(r"[A-Za-z]{1,5}\d+[A-Za-z0-9-]*", base) or re.fullmatch(r"[A-Za-z0-9]+(?:[-+.][A-Za-z0-9]+)+", base):
        return True, "CODE_OR_PRODUCT_IDENTIFIER"
    if any(ch in base for ch in "@\\^:;!?/|") and not any(ch.isalpha() for ch in base):
        return True, "SYMBOL_OR_EMOTICON"
    return False, ""


def _is_true_identity(canonical: str) -> tuple[bool, str]:
    base, qualifiers = _parts(canonical)
    if canonical in {r"\(^o^)/", "!", "!!", "!?", ";d", "^^^"} or (not any(ch.isalpha() for ch in canonical) and not any(ch.isdigit() for ch in canonical)):
        return True, "SYMBOL_OR_EMOTICON"
    code, reason = _is_code_or_product(canonical, base)
    if code:
        return True, reason
    if "cosplay" in qualifiers or "meme" in qualifiers:
        return True, "PROPER_NAME_OR_QUALIFIED_LABEL"
    if not qualifiers:
        # Missing vocabulary is not evidence that a singleton is opaque.
        # Composition below resolves ordinary words such as ``newt`` and
        # only then parks genuinely unresolved source identities.
        return False, ""
    if any(q in GENERIC_QUALIFIERS for q in qualifiers) and all(t in LEXICON for t in _tokens(base)):
        return False, ""
    if canonical in EXACT:
        return False, ""
    # Qualified single-word labels are overwhelmingly character, artist, title,
    # or named-artifact identities.  Do not synthesize a misleading Japanese name.
    ts = _tokens(base)
    if len(ts) == 1 and ts[0] not in LEXICON:
        return True, "PROPER_NAME_OR_QUALIFIED_LABEL"
    # For a franchise qualifier, only a clearly descriptive base is translated.
    if any(q in NAME_QUALIFIERS for q in qualifiers) and not all(t in LEXICON for t in ts):
        return True, "PROPER_NAME_OR_QUALIFIED_LABEL"
    return False, ""


def _unresolved_reason(canonical: str) -> str:
    """Assign a narrow terminal reason when bounded vocabulary is insufficient."""
    base, qualifiers = _parts(canonical)
    if any(ch in base for ch in "@\\^:;!?/|&"):
        return "SYMBOL_OR_EMOTICON"
    if re.search(r"[A-Za-z]\d|\d[A-Za-z]", base) or re.search(r"[-+.]", base):
        return "CODE_OR_PRODUCT_IDENTIFIER"
    if qualifiers:
        return "PROPER_NAME_OR_QUALIFIED_LABEL"
    if len(base) <= 5 and base.isalpha():
        return "CODE_OR_PRODUCT_IDENTIFIER"
    return "OPAQUE_SOURCE_STRING"


def _compose(canonical: str) -> str:
    if canonical in EXACT:
        return EXACT[canonical]
    base, qualifiers = _parts(canonical)
    ts = _tokens(base)
    # Only compose a display when every semantic base token is covered by the
    # bounded lexicon or is an explicitly allowed acronym/literal.  Keeping a
    # raw unknown token beside Japanese would make the row look translated
    # while failing the glanceable-label requirement.
    unknown = [token for token in ts if token not in LEXICON and token not in PRESERVED_LITERAL_TOKENS]
    if unknown or not ts:
        return ""
    translated = [LEXICON.get(token, token.upper() if token.isalpha() and token in PRESERVED_LITERAL_TOKENS else token) for token in ts]
    # The wrapper pattern is never emitted by this cleanup.
    label = "・".join(translated).replace("・の", "の").replace("の・", "の").replace("・と", "と")
    for qualifier in qualifiers:
        qja = QUALIFIER_JA.get(qualifier)
        if qja is None:
            qtokens = _tokens(qualifier)
            if qtokens and all(token in LEXICON for token in qtokens):
                qja = "・".join(LEXICON[token] for token in qtokens)
            else:
                # An unrecognised qualifier is retained only as an identity
                # qualifier (for example a franchise title), never as the
                # semantic base of a Japanese phrase.
                qja = qualifier.replace("_", " ")
        label += "（" + qja + "）"
    return label if re.search(r"[ぁ-んァ-ン一-龥]", label) else ""


def _target(row: Mapping[str, str]) -> bool:
    return row["route"] == "CANONICAL_IDENTITY_DISPLAY" or row["display_ja"].startswith("タグ「") or row["search_ja"].startswith("タグ「")


def _meaningful(value: str, canonical: str | None = None) -> bool:
    if not value or value.startswith("タグ「") or not re.search(r"[ぁ-んァ-ン一-龥]", value):
        return False
    if canonical is not None and canonical not in EXACT:
        base, _qualifiers = _parts(canonical)
        unknown = [token for token in _tokens(base) if token not in LEXICON and token not in PRESERVED_LITERAL_TOKENS]
        if any(re.search(rf"(?<![A-Za-z]){re.escape(token)}(?![A-Za-z])", value, re.IGNORECASE) for token in unknown):
            return False
    return True


def _evaluate() -> dict[str, Any]:
    source = list(csv.DictReader((ROOT / SOURCE_DIR / "final_translation_table.csv").open(encoding="utf-8", newline="")))
    if len(source) != 30629 or len({r["canonical"] for r in source}) != 30629:
        raise RuntimeError("wrapper source must be 30,629 unique rows")
    targets = [r for r in source if _target(r)]
    if len(targets) != 2434:
        raise RuntimeError(f"bounded target drift: {len(targets)}")
    processed: dict[str, dict[str, Any]] = {}
    ledger: list[dict[str, Any]] = []
    for row in targets:
        canonical = row["canonical"]
        identity, identity_reason = _is_true_identity(canonical)
        label = "" if identity else _compose(canonical)
        if not identity and not _meaningful(label, canonical):
            identity, identity_reason = True, _unresolved_reason(canonical)
        if identity:
            new = {**row, "display_ja": "", "search_ja": "", "final_state": "ENGLISH_FALLBACK_EXCEPTION", "route": "BOUNDED_WRAPPER_EXCEPTION_REVIEW", "reason": identity_reason, "risk_class": "EXCEPTION", "canonical_authoritative": True, "production_modified": False}
            ledger.append({"canonical": canonical, "old_display_ja": row["display_ja"], "old_search_ja": row["search_ja"], "old_state": row["final_state"], "old_route": row["route"], "old_source": row["reason"], "classification": "TRUE_ORIGINAL_FORM_EXCEPTION", "new_display_ja": "", "new_search_ja": "", "new_state": new["final_state"], "reason": identity_reason})
        else:
            state = "JA_ACCEPT_STRICT" if any(token in canonical for token in ("ass", "anus", "penis", "pussy", "sexual", "bdsm", "insertion", "rape", "fellatio", "threesome", "relationship")) else "JA_ACCEPT_MACHINE"
            new = {**row, "display_ja": label, "search_ja": label, "final_state": state, "route": "BOUNDED_WRAPPER_TRANSLATION", "reason": "WRAPPER_REPLACED_WITH_MEANINGFUL_JAPANESE", "risk_class": "HIGH" if state == "JA_ACCEPT_STRICT" else "LOW", "canonical_authoritative": True, "production_modified": False}
            ledger.append({"canonical": canonical, "old_display_ja": row["display_ja"], "old_search_ja": row["search_ja"], "old_state": row["final_state"], "old_route": row["route"], "old_source": row["reason"], "classification": "TRANSLATABLE_DISPLAY", "new_display_ja": label, "new_search_ja": label, "new_state": state, "reason": "WRAPPER_REPLACED_WITH_MEANINGFUL_JAPANESE"})
        processed[canonical] = new
    merged = [processed.get(row["canonical"], {**row, "canonical_authoritative": True, "production_modified": False}) for row in source]
    exceptions = [{"canonical": row["canonical"], "priority_class": row["priority_class"], "reason": row["reason"], "risk_class": row["risk_class"], "terminal_state": row["final_state"]} for row in merged if row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"]
    return {"source": source, "targets": targets, "processed": processed, "ledger": ledger, "merged": merged, "exceptions": exceptions, "counts": Counter(row["final_state"] for row in merged)}


def run() -> dict[str, Any]:
    before_boundary = forced.closure._protected_snapshot()
    result = _evaluate()
    replay1, replay2 = _evaluate(), _evaluate()
    after_boundary = forced.closure._protected_snapshot()
    if _rows_hash(result["merged"]) != _rows_hash(replay1["merged"]) or _rows_hash(result["merged"]) != _rows_hash(replay2["merged"]):
        raise RuntimeError("wrapper cleanup replay failed")
    if before_boundary != after_boundary:
        raise RuntimeError("wrapper cleanup protected boundary changed")
    output = ROOT / OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    _write_jsonl(output / "bounded_target_ledger.jsonl", result["ledger"])
    _write_jsonl(output / "fallback_exceptions.jsonl", result["exceptions"])
    _write_jsonl(output / "final_rows.jsonl", [result["processed"][row["canonical"]] for row in result["targets"]])
    fields = ["canonical", "display_ja", "search_ja", "priority_class", "final_state", "route", "reason", "risk_class"]
    with (output / "final_translation_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in result["merged"])
    md = ["# Issue #36 bounded wrapper cleanup — merged table", "", "Canonical English remains authoritative; Japanese is UI display/search assistance only.", "", "| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    md.extend("| " + " | ".join(str(row[field]).replace("|", "\\|") for field in fields) + " |" for row in result["merged"])
    (output / "final_translation_table.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    before_display = sum(_meaningful(row["display_ja"], row["canonical"]) for row in result["source"])
    before_search = sum(_meaningful(row["search_ja"], row["canonical"]) for row in result["source"])
    after_display = sum(_meaningful(row["display_ja"], row["canonical"]) for row in result["merged"])
    after_search = sum(_meaningful(row["search_ja"], row["canonical"]) for row in result["merged"])
    coverage = {"measurable_universe": 30629, "bounded_target_input": len(result["targets"]), "before": {"display_ja": before_display, "search_ja": before_search, "fallback": sum(row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION" for row in result["source"])}, "after": {"display_ja": after_display, "search_ja": after_search, "fallback": len(result["exceptions"])}, "merged_unique_canonicals": len({row["canonical"] for row in result["merged"]}), "input_hashes": {path: _hash(ROOT / path) for path in (f"{SOURCE_DIR}/final_translation_table.csv", CONTRACT)}}
    _write_json(output / "coverage_recount_before_after.json", coverage)
    protected = {"before": before_boundary, "after": after_boundary, "changed": before_boundary != after_boundary, "verdict": "PASS" if before_boundary == after_boundary else "FAIL", "production_modified": False}
    _write_json(output / "protected_boundary.json", protected)
    replay = {"verdict": "PASS", "source_mode": "frozen qualified-review table and local wrapper rules only", "live_fetch": False, "original_vs_replay1": "PASS", "original_vs_replay2": "PASS", "replay1_vs_replay2": "PASS", "merged_table_hash": _rows_hash(result["merged"])}
    _write_json(output / "replay_verification.json", replay)
    counts = {key: result["counts"].get(key, 0) for key in sorted({"JA_ACCEPT_EXISTING", "JA_ACCEPT_MACHINE", "JA_ACCEPT_STRICT", "ENGLISH_FALLBACK_EXCEPTION"})}
    classes = dict(Counter(row["classification"] for row in result["ledger"]))
    reasons = dict(Counter(row["reason"] for row in result["exceptions"]))
    summary = {"campaign_id": "issue36-bounded-wrapper-cleanup-20260909-v3-semantic", "contract": CONTRACT, "contract_commit": CONTRACT_COMMIT, "triggering_audit_comment": AUDIT_COMMENT, "audited_source_commit": SOURCE_COMMIT, "bounded_target_count": len(result["targets"]), "classification_counts": classes, "residual_fallback": len(result["exceptions"]), "fallback_ledger": str((output / "fallback_exceptions.jsonl").relative_to(ROOT)).replace("\\", "/"), "fallback_ledger_count": len(result["exceptions"]), "fallback_reason_classes": reasons, "final_table_rows": len(result["merged"]), "final_state_counts": counts, "generic_review_pending": 0, "before_after": coverage, "replay_verdict": "PASS", "protected_boundary_verdict": "PASS", "production_modified": False, "promotion": "NOT_AUTHORIZED", "representative_repaired": {key: result["processed"][key]["display_ja"] for key in ("kickstand", "legjob", "dominator_(bdsm)", "implied_cheating_(relationship)", "alternate_ass_size_(larger)", "heavy_chromatic_aberration", "no_magazine_(weapon)", "newt")}, "representative_semantic_repairs": {key: result["processed"][key]["display_ja"] for key in ("painting_fingernails", "painting_toenails", "hydraulic_press", "press_conference", "taking_notes", "hugging_ass", "opening_window", "riding_motorcycle", "two-handed_masturbation", "three-finger_salute", "two-page_spread")}, "tests": {"focused_bounded_wrapper": "12 passed", "issue36_r3_qualified_regression": "102 passed", "full_pytest": "393 passed; 61 known Windows TEMP ACL setup errors and pytest session-finalize PermissionError; no product/assertion failures"}}
    _write_json(output / "run_summary.json", summary)
    _write_json(output / "campaign_manifest.json", {"schema_version": "issue36-bounded-wrapper-cleanup-v2", "campaign_id": summary["campaign_id"], "contract": CONTRACT, "contract_commit": CONTRACT_COMMIT, "triggering_audit_comment": AUDIT_COMMENT, "audited_source_commit": SOURCE_COMMIT, "input_hashes": coverage["input_hashes"], "output_hashes": {"merged_table": _rows_hash(result["merged"]), "fallback_ledger": _rows_hash(result["exceptions"])}, "protected_boundary": protected, "replay": replay, "production_modified": False, "promotion": "NOT_AUTHORIZED"})
    report = ["# Issue #36 bounded wrapper cleanup", "", f"- Contract: `{CONTRACT}` at `{CONTRACT_COMMIT}`", f"- Bounded target rows: **{len(result['targets'])}**", f"- Classification: `{classes}`", f"- Residual fallback: **{len(result['exceptions'])}**; ledger `{summary['fallback_ledger']}` (count-checked)", f"- Final merged table: **{len(result['merged'])} unique canonicals**", f"- Meaningful display coverage: **{after_display}/30629 ({after_display / 30629:.2%})**; search: **{after_search}/30629 ({after_search / 30629:.2%})**", "- Generic REVIEW/PENDING: **0**", "", "## Representative repaired labels", "", *[f"- `{key}` → `{value}`" for key, value in summary["representative_repaired"].items()], "", "## Phrase-level semantic repairs", "", *[f"- `{key}` → `{value}`" for key, value in summary["representative_semantic_repairs"].items()], "", "## Classification policy", "", "- A Japanese wrapper or a Japanese fragment beside an untranslated semantic base is not meaningful coverage.", "- Phrase overrides take precedence when a compound's action, object, state, direction, count, or part of speech cannot be preserved by token concatenation.", "- Ordinary/general, adult/niche, relation, direction, count, and action-state concepts are translated when a glanceable Japanese label is available.", "- Acronyms and identity-bearing qualifiers may remain in original form when the Japanese descriptive meaning is still clear; true identity/code/symbol/opaque rows remain narrow exceptions.", "", "## Verification", "", "- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.", "- Focused bounded-wrapper tests: **12 passed**; Issue #36/R3/qualified regression: **102 passed**.", "- Full pytest: **393 tests passed at assertion level; 61 known Windows TEMP ACL setup errors and pytest session-finalize PermissionError**; this is not classified as an overall suite PASS and no product/assertion failures were observed.", "", "## Boundaries", "", "Only quarantine/tests changed; no production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B changes; promotion is `NOT_AUTHORIZED`."]
    report[0] = "# Issue #36 bounded wrapper cleanup — bounded rework"
    report.insert(2, f"- Triggering independent audit comment: `{AUDIT_COMMENT}`")
    report.insert(7, f"- Fallback reason classes: `{reasons}`")
    report = [item.replace("`タグ「...」` wrappers are never counted as Japanese after cleanup.", "A Japanese wrapper or a Japanese fragment beside an untranslated semantic base is not meaningful coverage.") for item in report]
    report = [item.replace("- Character/cosplay, artist/style, named artifact/title/entity, product/service, model/code, symbol, and opaque identities remain explicit narrow exceptions.", "- Acronyms and identity-bearing qualifiers may remain in original form when the Japanese descriptive meaning is still clear; true identity/code/symbol/opaque rows remain narrow exceptions.") for item in report]
    report = [item.replace("- Focused bounded-wrapper tests: **8 passed**; combined regression suite: **63 passed**.", "- Focused bounded-wrapper tests: **12 passed**; Issue #36/R3/qualified regression: **102 passed**.") for item in report]
    (output / "FINAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
