from __future__ import annotations

import csv
from pathlib import Path

QUEUE = Path("docs/issue70/audit/EXTERNAL_QUEUE_LIVE.csv")
CANDIDATES = Path("docs/issue70/audit/EXTERNAL_QUEUE_BATCH077_CANDIDATES.csv")
OUT = Path("docs/issue70/audit/external_resolution_copyright_official_batch077.csv")

ITEMS = {'fate_(series)': ('KEEP', '', '', 'https://typemoon.com/contents/', 'TYPE-MOON official contents use Fate as the franchise/series identity; existing Fateシリーズ is identity-safe.'),
 'idolmaster_(classic)': ('KEEP', '', '', 'https://idolmaster-official.jp/', 'Bandai Namco official portal uses アイドルマスター branding.'),
 'atelier_(series)': ('FIX_BOTH', 'アトリエシリーズ', 'アトリエ', 'https://www.gamecity.ne.jp/atelier/', 'Koei Tecmo official Atelier portal/store uses アトリエシリーズ; short アトリエ remains useful for search.'),
 'axis_powers_hetalia': ('FIX_BOTH', 'ヘタリア Axis Powers', 'ヘタリア', 'https://www.deen.co.jp/works-archives/hetalia', 'Studio DEEN official work archive identifies ヘタリア Axis Powers.'),
 'punishing:_gray_raven': ('FIX_BOTH', 'パニシング：グレイレイヴン', 'パニグレ', 'https://pgr.kurogames.com/jp/', 'KURO official Japanese product surface uses パニシング：グレイレイヴン; パニグレ is retained as search alias.'),
 'my_little_pony': ('KEEP', '', '', 'https://www.tv-tokyo.co.jp/anime/mylittle-pony/', 'TV Tokyo official Japanese program page uses マイリトルポニー.'),
 'my_little_pony:_friendship_is_magic': ('FIX_BOTH', 'マイリトルポニー ～トモダチは魔法～', 'マイリトルポニー', 'https://www.tv-tokyo.co.jp/anime/mylittle-pony/', 'TV Tokyo official Japanese title is マイリトルポニー ～トモダチは魔法～.'),
 'zeta_gundam': ('KEEP', '', '', 'https://gba.ggame.jp/character/detail.php?s=z', 'Bandai Namco official Gundam page uses 機動戦士Ζガンダム.'),
 'rabbit_hole_(vocaloid)': ('KEEP', '', '', 'https://otoiro.co.jp/works/deco27-rh/', 'OTOIRO official work page uses ラビットホール.'),
 'fate/prototype': ('FIX_DISPLAY', 'Fate/Prototype', '', 'https://typemoon.com/contents/fate-prototype/', 'TYPE-MOON official title is Fate/Prototype.'),
 'wizarding_world': ('KEEP', '', '', 'https://www.warnerbros.co.jp/harrypotter/', 'Warner Bros. Japan official Harry Potter franchise surface supports the established ウィザーディング・ワールド identity.'),
 'grimms_notes': ('KEEP', '', '', 'https://www.jp.square-enix.com/grimms/', 'Square Enix official product surface uses グリムノーツ.'),
 'mon-musu_quest!': ('FIX_DISPLAY', 'もんむす・くえすと！', '', 'https://mon110.sakura.ne.jp/mong/top.html', 'Developer official site identifies the title as もんむすくえすと！; normalized punctuation preserves the canonical work identity.'),
 'toji_no_miko': ('FIX_DISPLAY', '刀使ノ巫女', '', 'https://tojinomiko.jp/', 'Official project site uses 刀使ノ巫女.'),
 'berserk': ('KEEP', '', '', 'https://www.berserk-anime.com/', 'Official anime site uses ベルセルク.'),
 'final_fantasy_x': ('FIX_BOTH', 'ファイナルファンタジーX', 'ファイナルファンタジー10 | FF10 | FFX', 'https://www.jp.square-enix.com/game/detail/ff10/', 'Square Enix official title uses Roman numeral X.'),
 'final_fantasy_iv': ('FIX_BOTH', 'ファイナルファンタジーIV', 'ファイナルファンタジー4 | FF4 | FFIV', 'https://www.jp.square-enix.com/ff4/', 'Square Enix official title uses Roman numeral IV.'),
 'harry_potter_(series)': ('FIX_BOTH', 'ハリー・ポッター', 'ハリポタ', 'https://www.warnerbros.co.jp/harrypotter/', 'Warner Bros. Japan official franchise surface uses ハリー・ポッター; ハリポタ is search-only shorthand.'),
 'dc_comics': ('FIX_DISPLAY', 'DC', '', 'https://www.warnerbros.co.jp/character/', 'Warner Bros. Japan official character/franchise page labels the property DC.'),
 'tales_of_symphonia': ('FIX_BOTH', 'テイルズ オブ シンフォニア', 'シンフォニア', 'https://tosre-nowagain.tales-ch.jp/', 'Bandai Namco official remaster site uses テイルズ オブ シンフォニア.'),
 'dragon_quest_iv': ('FIX_BOTH', 'ドラゴンクエストIV 導かれし者たち', 'ドラクエ4 | DQ4', 'https://www.dragonquest.jp/products/list/device/videogame/page/17/base/13/', 'Square Enix Dragon Quest official product listing uses ドラゴンクエストIV 導かれし者たち.'),
 'atelier_ryza_1': ('FIX_BOTH', 'ライザのアトリエ ～常闇の女王と秘密の隠れ家～', 'ライザのアトリエ', 'https://www.gamecity.ne.jp/atelier/ryza/', 'Koei Tecmo official title includes the full subtitle.'),
 'live_a_hero': ('FIX_DISPLAY', 'ライブ・ア・ヒーロー！', '', 'https://live-a-hero.jp/', 'Official product site uses ライブ・ア・ヒーロー！.'),
 'tokidoki_bosotto_roshia-go_de_dereru_tonari_no_alya-san': ('FIX_BOTH', '時々ボソッとロシア語でデレる隣のアーリャさん', 'ロシデレ', 'https://roshidere.com/', 'Official anime site uses the full Japanese title; ロシデレ is retained for search.'),
 'tales_of_xillia': ('FIX_BOTH', 'テイルズ オブ エクシリア', 'エクシリア', 'https://coexist.tales-ch.jp/', 'Bandai Namco official site uses テイルズ オブ エクシリア.'),
 'seiken_densetsu': ('KEEP', '', '', 'https://www.jp.square-enix.com/seiken/', 'Square Enix official franchise portal uses 聖剣伝説.'),
 'mahou_shoujo_ni_akogarete': ('FIX_BOTH', '魔法少女にあこがれて', 'まほあこ', 'https://mahoako-anime.com/', 'Official anime site uses 魔法少女にあこがれて; まほあこ is search shorthand.'),
 'mega_man_legends_(series)': ('KEEP', '', '', 'https://www.capcom.co.jp/support/faq/full_platform_psp_rockdash.html', 'Capcom official support surface uses ロックマンDASH; existing display preserves the franchise identity.'),
 'hayate_no_gotoku!': ('FIX_DISPLAY', 'ハヤテのごとく！', '', 'https://e-comi.shogakukan.co.jp/books/098525370000d0000000', 'Shogakukan official publication surface uses ハヤテのごとく！.'),
 'choukou_(alicesoft)': ('KEEP', '', '', 'https://www.alicesoft.com/information/game/valkyrie/', 'AliceSoft official site has the category 超昂シリーズ.'),
 'final_fantasy_v': ('FIX_BOTH', 'ファイナルファンタジーV', 'ファイナルファンタジー5 | FF5 | FFV', 'https://www.jp.square-enix.com/game/detail/ff5/', 'Square Enix official title uses Roman numeral V.'),
 'macross_delta': ('KEEP', '', '', 'https://macross.jp/pages/series?title=macrossdelta', 'Official Macross portal uses マクロスΔ.'),
 'fire_emblem_cipher': ('FIX_BOTH', 'ファイアーエムブレム0（サイファ）', 'ファイアーエムブレムサイファ | FEサイファ', 'https://www.nintendo.com/jp/topics/article/3eac536b-c4ba-11e5-baa2-0a6d14145cb1', 'Nintendo official article uses ファイアーエムブレム0（サイファ）.'),
 'brown_dust_2': ('KEEP', '', '', 'https://www.browndust2.com/ja-jp/', 'Official Japanese product site uses ブラウンダスト2.'),
 'getter_robo': ('KEEP', '', '', 'https://getterrobot-arc.com/', 'Official anime site uses ゲッターロボ.'),
 'di_gi_charat': ('FIX_DISPLAY', 'デ・ジ・キャラット', '', 'https://digicharat-reiwa.com/', 'Official project site uses デ・ジ・キャラット.'),
 'elden_ring_nightreign': ('FIX_BOTH', 'ELDEN RING NIGHTREIGN', 'エルデンリング ナイトレイン | ナイトレイン', 'https://www.fromsoftware.jp/jp/manual.html', 'FromSoftware official product/manual surface uses ELDEN RING NIGHTREIGN.'),
 'adventure_time': ('FIX_DISPLAY', 'アドベンチャー・タイム', '', 'https://www.cartoonnetwork.jp/cn_programs/view/00486', 'Cartoon Network Japan official program title uses アドベンチャー・タイム.'),
 '.live': ('FIX_BOTH', '.LIVE', 'どっとライブ | アイドル部', 'https://dotlive.jp/', 'Official .LIVE site uses .LIVE / どっとライブ branding; アイドル部 is retained only as search alias.'),
 'wild_arms': ('KEEP', '', '', 'https://www.playstation.com/ja-jp/games/wild-arms/', 'PlayStation official Japanese page uses ワイルドアームズ.'),
 'silent_hill_(series)': ('FIX_BOTH', 'SILENT HILL', 'サイレントヒル', 'https://www.konami.com/games/silenthill/jp/ja/', 'Konami official franchise portal uses SILENT HILL branding.'),
 'rance_(series)': ('KEEP', '', '', 'https://www.alicesoft.com/information/info/', 'AliceSoft official site explicitly groups content under ランスシリーズ.'),
 'avengers_(series)': ('KEEP', '', '', 'https://marvel.disney.co.jp/character/avengers', 'Marvel/Disney Japan official franchise surface uses アベンジャーズ.'),
 'hollow_knight:_silksong': ('KEEP', '', '', 'https://hollowknightsilksong.com/', 'Team Cherry official site uses Hollow Knight: Silksong.'),
 'shiguang_dailiren': ('FIX_BOTH', '時光代理人 -LINK CLICK-', '時光代理人', 'https://link-click.jp/1st/', 'Official Japanese anime site uses 時光代理人 -LINK CLICK-.'),
 "heaven's_feel": ('KEEP', '', '', 'https://www.fate-sn.com/1st/', 'Official film site uses Fate/stay night [Heaven’s Feel].'),
 'neverness_to_everness': ('KEEP', '', '', 'https://nte.perfectworld.com/jp/', 'Official Japanese site uses NTE: Neverness to Everness / Neverness to Everness.'),
 'xenoblade_chronicles_1': ('KEEP', '', '', 'https://www.nintendo.com/jp/xenoblade/index.html', 'Nintendo official Japanese site uses ゼノブレイド.'),
 'avatar:_the_last_airbender': ('KEEP', '', '', 'https://www.netflix.com/jp/title/70142405', 'Official Japanese distribution surface uses アバター 伝説の少年アン.'),
 'toaru_majutsu_no_index:_old_testament': ('KEEP', '', '', 'https://toaru-project.com/index_3/', 'Official anime project uses とある魔術の禁書目録.'),
 're:stage!': ('KEEP', '', '', 'https://rst-project.jp/', 'Official project site uses Re:ステージ！.'),
 'nu_carnival': ('KEEP', '', '', 'https://nucarnival.com/ja-JP/', 'Official Japanese site identifies the game as NU: カーニバル.'),
 'beatmania_iidx': ('KEEP', '', '', 'https://p.eagate.573.jp/game/2dx/', 'Konami official e-amusement surface uses beatmania IIDX.'),
 "heaven_official's_blessing": ('KEEP', '', '', 'https://tgcf-anime.com/1st.html', 'Official Japanese anime site uses 天官賜福.'),
 'fate/prototype:_fragments_of_blue_and_silver': ('KEEP', '', '', 'https://www.aniplex.co.jp/lineup/fate-pt-sougin/', 'Aniplex official title is Fate/Prototype 蒼銀のフラグメンツ.'),
 'senjou_no_valkyria_(series)': ('KEEP', '', '', 'https://portal.valkyria.jp/game/', 'SEGA official Valkyria portal groups the titles under 戦場のヴァルキュリア identity.'),
 'donkey_kong_(series)': ('KEEP', '', '', 'https://www.nintendo.com/jp/character/donkeykong/index.html', 'Nintendo official character/franchise surface uses ドンキーコング.'),
 'eve_online': ('KEEP', '', '', 'https://www.eveonline.com/ja', 'Official Japanese site uses EVE Online.'),
 '7th_dragon_(series)': ('KEEP', '', '', 'https://www.sega.jp/game/detail/7thdragon3/', 'SEGA official product lineage uses セブンスドラゴン; existing display safely preserves the series identity.'),
 'mother_3': ('KEEP', '', '', 'https://www.nintendo.com/jp/topics/article/f7eddb20-1bf0-48cb-b4e1-0e5e6c11b067', 'Nintendo official article uses MOTHER3.'),
 'the_elder_scrolls': ('KEEP', '', '', 'https://elderscrolls.bethesda.net/ja-JP', 'Bethesda official Japanese franchise site uses The Elder Scrolls.'),
 'da_capo': ('KEEP', '', '', 'https://circus-co.jp/product/dc/', 'CIRCUS official product surface uses D.C. ～ダ・カーポ～.'),
 'the_king_of_fighters_xv': ('KEEP', '', '', 'https://www.snk-corp.co.jp/official/kof-xv/', 'SNK official product title is THE KING OF FIGHTERS XV.'),
 'shirobako': ('KEEP', '', '', 'https://shirobako-anime.com/', 'Official anime site uses SHIROBAKO.'),
 "assassin's_creed_(series)": ('KEEP', '', '', 'https://www.ubisoft.com/ja-jp/game/assassins-creed', 'Ubisoft official Japanese franchise page uses アサシン クリード series.'),
 'plants_vs._zombies': ('KEEP', '', '', 'https://www.ea.com/ja-jp/games/plants-vs-zombies', 'EA official Japanese franchise surface uses Plants vs. Zombies.'),
 'helios_rising_heroes': ('FIX_BOTH', 'エリオスライジングヒーローズ', 'エリオスR | HELIOS Rising Heroes', 'https://helios-r.jp/', 'Official site states title エリオスライジングヒーローズ and abbreviation エリオスR.'),
 'fate/grand_order_arcade': ('KEEP', '', '', 'https://arcade.fate-go.jp/', 'Official arcade site uses Fate/Grand Order Arcade.'),
 'pixiv_fantasia_last_saga': ('KEEP', '', '', 'https://www.pixiv.net/special/pixivfantasia/', 'pixiv official Pixiv Fantasia event surface preserves the Pixiv Fantasia naming; existing Last Saga title is identity-safe.'),
 'dream_c_club_(series)': ('KEEP', '', '', 'https://www.d3p.co.jp/dreamclub/', 'D3 Publisher official portal identifies DREAM C CLUB / ドリームクラブ titles.'),
 'ikizulive!_love_live!_bluebird': ('KEEP', '', '', 'https://ikizulive.com/', 'Official project site uses イキヅライブ！ LOVELIVE! BLUEBIRD.'),
 'the_king_of_fighters_xiv': ('KEEP', '', '', 'https://www.snk-corp.co.jp/official/kof-portal/series/xiv/', 'SNK official series site uses THE KING OF FIGHTERS XIV.'),
 'apple_inc.': ('KEEP', '', '', 'https://www.apple.com/jp/', 'Apple Japan official site uses Apple brand identity.'),
 'dota_2': ('KEEP', '', '', 'https://www.dota2.com/home?l=japanese', 'Valve official Dota 2 site uses Dota 2.'),
 'pixiv': ('KEEP', '', '', 'https://www.pixiv.net/', 'Official service brand is pixiv.'),
 'trigun_stampede': ('KEEP', '', '', 'https://trigun-anime.com/stampede/', 'Official anime site uses TRIGUN STAMPEDE.'),
 'fate/unlimited_codes': ('KEEP', '', '', 'https://www.capcom.co.jp/support/faq/platform_psp_fate_uc_037523.html', 'Capcom official support identifies Fate/unlimited codes PORTABLE, preserving the base Fate/unlimited codes title.'),
 'armored_core_vi:_fires_of_rubicon': ('KEEP', '', '', 'https://www.fromsoftware.jp/jp/detail.html?csm=106', 'FromSoftware official product page uses ARMORED CORE VI FIRES OF RUBICON.'),
 'halo_(series)': ('KEEP', '', '', 'https://www.xbox.com/ja-jp/games/halo', 'Xbox official Japanese Halo Universe page identifies Halo series.'),
 'elden_ring:_shadow_of_the_erdtree': ('KEEP', '', '', 'https://www.fromsoftware.jp/jp/eldenring/shadowoftheerdtree.html', 'FromSoftware official Japanese product surface uses ELDEN RING SHADOW OF THE ERDTREE.')}

FIELDS = [
    "row_id","canonical_tag","post_count","display_ja","search_ja",
    "prior_audit_verdict","audit_verdict","proposed_display_ja","proposed_search_ja",
    "reason_code","confidence","evidence_refs","audit_note","approval_status"
]

def main() -> None:
    with QUEUE.open(encoding="utf-8-sig", newline="") as f:
        queue = list(csv.DictReader(f))
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidates = list(csv.DictReader(f))

    by_tag = {r["canonical_tag"]: r for r in queue}
    effective_unresolved = {r["canonical_tag"] for r in candidates}
    missing_from_effective = sorted(set(ITEMS) - effective_unresolved)
    assert not missing_from_effective, f"batch077 targets not effective unresolved anymore: {missing_from_effective}"
    missing_from_queue = sorted(set(ITEMS) - set(by_tag))
    assert not missing_from_queue, f"batch077 targets absent from root queue: {missing_from_queue}"

    rows = []
    for tag, spec in ITEMS.items():
        verdict, display, search, url, note = spec
        q = by_tag[tag]
        assert q["category"] == "Copyright", (tag, q["category"])
        assert q["audit_verdict"] == "NEEDS_EXTERNAL_CHECK", (tag, q["audit_verdict"])
        assert verdict in {"KEEP","FIX_DISPLAY","FIX_SEARCH","FIX_BOTH"}, (tag, verdict)
        pd = display if verdict in {"FIX_DISPLAY","FIX_BOTH"} else ""
        ps = search if verdict in {"FIX_SEARCH","FIX_BOTH"} else ""
        if verdict in {"FIX_DISPLAY","FIX_BOTH"}:
            assert pd and pd != q["display_ja"], (tag, q["display_ja"], pd)
        if verdict in {"FIX_SEARCH","FIX_BOTH"}:
            assert ps and ps != q["search_ja"], (tag, q["search_ja"], ps)
        rows.append({
            "row_id": q["row_id"],
            "canonical_tag": tag,
            "post_count": q["post_count"],
            "display_ja": q["display_ja"],
            "search_ja": q["search_ja"],
            "prior_audit_verdict": "NEEDS_EXTERNAL_CHECK",
            "audit_verdict": verdict,
            "proposed_display_ja": pd,
            "proposed_search_ja": ps,
            "reason_code": "OFFICIAL_OR_FIRST_PARTY_TITLE_CONFIRMED_BATCH077",
            "confidence": "HIGH",
            "evidence_refs": url,
            "audit_note": note,
            "approval_status": "PROPOSED",
        })

    assert len(rows) == 80
    assert len({r["row_id"] for r in rows}) == 80
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print({"rows": len(rows), "output": str(OUT), "production_modified": False})

if __name__ == "__main__":
    main()
