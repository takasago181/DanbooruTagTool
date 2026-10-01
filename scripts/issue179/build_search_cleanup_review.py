from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay_2d_final.csv"
OUT = ROOT / "artifacts/issue179-search-cleanup"
OUT_CSV = OUT / "SEARCH_CLEANUP_CANDIDATES_V1.csv"

# Confirmed by retained B001/B002 review, then second-reviewed on 2026-10-01, or by an unambiguous
# non-identity/fandom pattern. This script only proposes removals; it does not
# modify Issue70 source data or production.
EXACT_REMOVE = {
    "ミクの日", "初音ミクイラスト", "ぼ喜多", "絵フブキ", "ドラゴンボールイラスト", "毎月七日はルーミアの日", "カリイラスト", "絵ニックス", "海未の日", "絵ンジュ", "るしあ大好きだよ", "絵クロマンサー", "ポルカおるか", "絵まる", "スイレンちゃんの日", "8月7日は八千慧の日", "エンイラ(アズールレーン)", "シャワーズの日", "絵リーラ", "ミズゴロウの日", "絵こころ", "チルタリスの日", "絵画コウ", "ヌオーの日", "絵ーちゃん", "オタチの日", "絵画らしぃ", "絵描キキ", "絵ッチグサ", "絵ーじぇんと", "ブルアカイラスト部", "ガルパンイラスト再投稿企画", "ガルパンクリスマスイラスト投稿企画", "ガルパンバレンタインイラスト投稿企画", "ガルパン最終章カウントダウンイラスト投稿企画", "FF14イラスト", "真夏の夜のクッキー迫真お絵描き", "協奏中応援イラスト", "フラワーナイトガールイラスト", "フォトナ美術部", "フォートナイトイラスト", "三国志大戦TCGカードイラストコンテスト",
    "腐レイバーン", "ス腐ラトゥーン", "VOICEROIDドット絵部", "コッショリ",
    "異端なるセイレム", "アビラヴィ", "おかころ", "絵かゆ", "エロおにぎり",
    "エンイラ", "性癖を露見・共有するための道具", "ぼっち・ざ・けいおん!",
    "サ腐マス", "ノボクダ",
    "東方うごイラ", "東方グラマラス", "東方ショタ化", "東方モータリゼーション",
    "東方好きな人RT", "東方版もうひとつの深夜の真剣お絵描き60分一本勝負",
    "ア艦これ", "シンスイカッコカリ", "北斗の艦",
    "艦これ版深夜の真剣お絵描き60分一本勝負", "艦これ版真剣お絵描き60分一本勝負",
    "艦これ集合絵", "艦ショタ",
    "pkg版深夜の真剣お絵描き60分一本勝負", "ポケモンFA", "ポケモン×人間",
    "ポケモンと生活", "ポケモンイラスト", "ポケモントレーナー版深夜の真剣お絵描き60分一本勝負",
    "ポケモン人間絵", "ポケモン擬人化", "ポケモン機械化", "ポケ擬", "星座タロット風ポケモン",
    "FE版深夜の真剣お絵描き60分一本勝負", "FE腐向け", "ガチホモエムブレム",
    "オリキュア", "オリジナルプリキュア", "マイプリキュア", "腐リキュア",
    "グラ腐ル", "夢アカ", "ゼルダの伝説【腐】", "ROお絵描き",
    "プロセカ衣装デザイン", "腐ロセカ", "ww版深夜の真剣お絵描き60分一本勝負", "ワンドロウィッチーズ",
    "腐ゼロ", "腐滅の刃", "進撃の巨人イラコン", "進撃の百合", "進撃の腐人",
    "あんさん腐るスターズ", "あんさん腐るスターズ!", "あんスタCPなし", "あんスタFA", "あんスタNL",
    "水星の腐女", "水星の魔女最終回", "逆裁腐向け", "百合パラ", "腐リパラ",
    "TF腐向け", "金カム腐", "金カ夢", "腐よ腐よ", "まじコナ腐", "腐向けKTR",
    "松野家次男版深夜の真剣お絵描き60分一本勝負", "エムマス【腐】", "腐ロメア",
    "bllプラス", "ブルーロックFA", "夢ルーロック", "夢ロック", "腐ルーロック", "青檻プラス",
    "モ腐サイコ100", "転腐ら", "東京【腐】リベンジャーズ", "鉄血のオル腐ェンズ",
    "ワートリ【腐】", "文スト【腐】", "黒バス【腐】", "dcst腐向け", "ヒ腐マイ",
    "腐パン", "モンスト腐", "ヴァンガ【腐】cf_vanguard", "逃げ若【腐】",
    "腐リチャン", "レインコード【腐】", "メギド【腐】", "プリマジファンアート", "腐リマジ",
    "DbDアートdbdfanart", "蒼穹のファ腐ナー", "マオのお絵描き帳", "エ腐ケーエイト",
    "忍たま-腐", "イニD腐向け", "ドリ腐", "忍殺腐向け", "【腐】ぼくまち",
    "ずとまよファンアート", "オルガルイラスト部", "戦コレイラコン3ファンアート",
    "ケムリクサファンアート", "星界ファンアート", "産子ギャルファンアート",
}

# Row-scoped removals avoid deleting a surface that is a valid identity for another row.
ROW_EXACT_REMOVE = {
    "I70-001111": {"イラストリアス"},
}

# These hit crude regexes but are identity/title terms. Explicitly protect them.
PROTECTED = {
    "腐敗の女神マレニア", "腐敗の女神、マレニア",
    "お絵描き娘", "お絵描き娘2009", "お絵描き娘2011", "お絵描き娘2012",
    "リトル・イラストリアス", "リトル・イラストリアス(アズールレーン)",
    "チェンジ!!ゲッターロボ世界最後の日", "世界最後の日",
}

SAFE_PATTERNS = [
    re.compile(r"深夜の真剣お絵描き"),
    re.compile(r"真剣お絵描き"),
    re.compile(r"ファンアート", re.I),
    re.compile(r"(?:^|[^敗])腐向け"),
    re.compile(r"【腐】"),
]

FIELDS = [
    "row_id", "canonical_tag", "category", "post_count",
    "old_search_ja", "proposed_search_ja", "removed_terms",
    "reason", "review_state",
]

def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower().replace("_", " ")
    return " ".join(value.split())

def split_pipe(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split("|") if x.strip()]

def should_remove(term: str, row_id: str) -> bool:
    if term in PROTECTED:
        return False
    if term in ROW_EXACT_REMOVE.get(row_id, set()):
        return True
    if term in EXACT_REMOVE:
        return True
    return any(p.search(term) for p in SAFE_PATTERNS)

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as fh:
        for src in csv.DictReader(fh):
            terms = split_pipe(src.get("search_ja", ""))
            noise_removed = [t for t in terms if should_remove(t, src["row_id"])]
            after_noise = [t for t in terms if t not in noise_removed]

            # SearchEngine.Normalize collapses Unicode width, case and
            # underscore/space differences. Keep the first normalized surface
            # and remove later formatting-only duplicates; retrieval semantics
            # are unchanged.
            seen: set[str] = set()
            kept: list[str] = []
            duplicate_removed: list[str] = []
            for term in after_noise:
                key = norm(term)
                if key in seen:
                    duplicate_removed.append(term)
                    continue
                seen.add(key)
                kept.append(term)

            removed = noise_removed + duplicate_removed
            if not removed:
                continue
            reasons: list[str] = []
            if noise_removed:
                reasons.append("CONFIRMED_NON_IDENTITY_OR_FANDOM_SEARCH_TERM")
            if duplicate_removed:
                reasons.append("NORMALIZED_DUPLICATE_SEARCH_TERM")
            rows.append({
                "row_id": src["row_id"],
                "canonical_tag": src["canonical_tag"],
                "category": src["category"],
                "post_count": src["post_count"],
                "old_search_ja": " | ".join(terms),
                "proposed_search_ja": " | ".join(kept),
                "removed_terms": " | ".join(removed),
                "reason": "+".join(reasons),
                "review_state": "SECOND_REVIEW_ACCEPTED",
            })

    rows.sort(key=lambda r: (-int(r["post_count"]), r["canonical_tag"]))
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    removed_count = sum(len(split_pipe(r["removed_terms"])) for r in rows)
    print(f"SEARCH_CLEANUP_CANDIDATES rows={len(rows)} removed_terms={removed_count}")

if __name__ == "__main__":
    main()
