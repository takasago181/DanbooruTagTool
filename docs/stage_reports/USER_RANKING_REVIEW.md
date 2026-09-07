# Stage 6 ユーザー実用評価 — Ranking比較資料

この資料は保存済みの `ranking_evaluation.json` と静的Special2788辞書だけを整形したものです。再集計、parameter変更、ランキング変更はしていません。

統計snapshot: `nyanko-devs/danbooru2026@ebb02a630201c7b51487e45fb90b3fcf4cbedc20:metadata/posts-snapshot.parquet`  
統計母集団: 11,218,362 posts

SpecialのPrompt identityとstatistics canonicalは別です。評価データはstatistics canonicalのCoreしか保存しておらず、選択されたSpecial IDは保存していません。Core表には、そのcanonicalへ既存辞書で対応するSpecial2788エントリを全件載せます。

候補の日本語訳は、同じcanonicalへ対応する既存Special2788の日本語がある場合のみ表示します。`—`は今回参照した既存データには日本語訳がないことを示します。`role`は保存済み評価値のみで、全件 `other` です。

support区分: `1` / `2–5` / `6–10` / `11–99` / `100以上`。supportが小さいことは、候補の意味や有用性を決めるものではありません。

## two_special_medium

### 1. Core内容

base_count: **8,805**

| statistics canonical | 対応する既存Special2788エントリ（ID: Prompt identity — 日本語） |
|---|---|
| `erection` | 684: `erection` — 勃起<br>1260: `erect penis` — 勃起した・陰茎に関係する表現 |
| `open_clothes` | 2049: `open clothes` — 衣服を開いた状態 |

### Conditional Rate top20

| Rank | canonical tag | 日本語訳（既存Special2788にある場合） | co_count | support | conditional_rate | raw_lift | runtime_global_count | role | ユーザー確認 |
|---:|---|---|---:|---|---:|---:|---:|---|---|
| 1 | `penis` | 陰茎 / 陰茎に関係する表現 / 陰茎の別名・表記揺れ | 7,794 | 100以上 | 88.52% | 19.15 | 518,431 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 2 | `nipples` | 乳首が見える / 乳首に関係する表現 | 6,135 | 100以上 | 69.68% | 7.75 | 1,009,122 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 3 | `blush` | — | 6,005 | 100以上 | 68.20% | 2.00 | 3,823,437 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 4 | `1boy` | — | 5,910 | 100以上 | 67.12% | 3.87 | 1,945,837 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 5 | `breasts` | 乳房 / 乳房の別名・表記揺れ | 5,699 | 100以上 | 64.72% | 1.60 | 4,542,658 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 6 | `censored` | — | 5,597 | 100以上 | 63.57% | 12.04 | 592,432 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 7 | `1girl` | — | 5,586 | 100以上 | 63.44% | 0.92 | 7,773,799 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 8 | `hetero` | 男女・異性間の性的関係 | 5,320 | 100以上 | 60.42% | 9.65 | 702,398 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 9 | `shirt` | — | 4,512 | 100以上 | 51.24% | 2.09 | 2,745,570 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 10 | `long_hair` | — | 4,192 | 100以上 | 47.61% | 0.92 | 5,790,640 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 11 | `open_mouth` | — | 4,012 | 100以上 | 45.57% | 1.56 | 3,272,995 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 12 | `open_shirt` | シャツを開いた状態 | 3,680 | 100以上 | 41.79% | 33.21 | 141,185 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 13 | `navel` | — | 3,305 | 100以上 | 37.54% | 2.83 | 1,486,565 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 14 | `jacket` | — | 3,246 | 100以上 | 36.87% | 2.94 | 1,405,264 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 15 | `short_hair` | — | 3,070 | 100以上 | 34.87% | 1.34 | 2,926,954 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 16 | `solo_focus` | — | 3,014 | 100以上 | 34.23% | 8.38 | 458,279 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 17 | `testicles` | 睾丸 / 睾丸の俗称。球・スポーツ用品の意味もあるため単独はREVIEW | 2,824 | 100以上 | 32.07% | 29.58 | 121,630 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 18 | `large_breasts` | — | 2,814 | 100以上 | 31.96% | 1.74 | 2,064,758 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 19 | `long_sleeves` | — | 2,775 | 100以上 | 31.52% | 1.58 | 2,232,232 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 20 | `cum` | 精液 / 射精描写 / 精子に関係する表現 | 2,751 | 100以上 | 31.24% | 11.76 | 297,982 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |

### Raw Lift top20

| Rank | canonical tag | 日本語訳（既存Special2788にある場合） | co_count | support | conditional_rate | raw_lift | runtime_global_count | role | ユーザー確認 |
|---:|---|---|---:|---|---:|---:|---:|---|---|
| 1 | `tentacle_masturbation` | 触手を使った自慰 / 自動・触手・性行為に関係する表現 | 20 | 11–99 | 0.23% | 289.57 | 88 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 2 | `handjob_under_clothes` | 手淫が衣服の下・内側にある描写 | 14 | 11–99 | 0.16% | 198.19 | 90 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 3 | `mutual_penetration` | 相互の・挿入に関係する表現 | 6 | 6–10 | 0.07% | 182.01 | 42 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 4 | `sleevejob` | — | 15 | 11–99 | 0.17% | 176.96 | 108 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 5 | `no_male_underwear` | 下着を着けていない状態 / 通常下着を着用する状況で男性用下着を着けていない状態 / 通常下着を着用する状況で男性用下着を着けていない状態の別名・表記揺れ | 67 | 11–99 | 0.76% | 134.64 | 634 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 6 | `pecjob` | 男性の胸筋で性器を挟む・こする行為 / 男性・パイズリに関係する表現 / 原語「pec」・性交・性行為に関係する表現 / 男性の胸筋で性器を挟む・こする行為の別名・表記揺れ | 31 | 11–99 | 0.35% | 128.65 | 307 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 7 | `urethral_penetration` | 尿道への挿入 | 3 | 2–5 | 0.03% | 127.41 | 30 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 8 | `penis_on_tongue` | 陰茎が舌の上・表面にある、または接触している描写 | 6 | 6–10 | 0.07% | 121.34 | 63 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 9 | `open_wetsuit` | — | 14 | 11–99 | 0.16% | 119.71 | 149 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 10 | `jellyfish_hair_ornament` | — | 22 | 11–99 | 0.25% | 117.77 | 238 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 11 | `erection_under_clothes` | 覆われた・勃起に関係する表現 / 衣服越しに分かる勃起 | 1,192 | 100以上 | 13.54% | 107.91 | 14,074 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 12 | `fellatio_through_clothes` | フェラチオ・越し・衣服に関係する表現 | 7 | 6–10 | 0.08% | 103.70 | 86 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 13 | `male_underwear_aside` | — | 36 | 11–99 | 0.41% | 103.54 | 443 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 14 | `underwear_around_one_leg` | — | 15 | 11–99 | 0.17% | 102.75 | 186 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 15 | `penis_to_navel` | 陰茎とへそを接触・近接させる描写 | 6 | 6–10 | 0.07% | 98.01 | 78 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 16 | `precum_through_clothes` | 先走り液・越し・衣服に関係する表現 | 64 | 11–99 | 0.73% | 97.42 | 837 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 17 | `bra_aside` | — | 5 | 2–5 | 0.06% | 96.52 | 66 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 18 | `bulge_to_face` | — | 8 | 6–10 | 0.09% | 91.83 | 111 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 19 | `penis_under_mask` | 陰茎がマスクの下・内側にある描写 | 18 | 11–99 | 0.20% | 89.94 | 255 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 20 | `naked_vest` | 裸体・ベストに関係する表現 | 7 | 6–10 | 0.08% | 85.76 | 104 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |

### 差分

| 区分 | 候補 |
|---|---|
| 両方のtop20 | — |
| Conditional Rateだけ | `penis`, `nipples`, `blush`, `1boy`, `breasts`, `censored`, `1girl`, `hetero`, `shirt`, `long_hair`, `open_mouth`, `open_shirt`, `navel`, `jacket`, `short_hair`, `solo_focus`, `testicles`, `large_breasts`, `long_sleeves`, `cum` |
| Raw Liftだけ | `tentacle_masturbation`, `handjob_under_clothes`, `mutual_penetration`, `sleevejob`, `no_male_underwear`, `pecjob`, `urethral_penetration`, `penis_on_tongue`, `open_wetsuit`, `jellyfish_hair_ornament`, `erection_under_clothes`, `fellatio_through_clothes`, `male_underwear_aside`, `underwear_around_one_leg`, `penis_to_navel`, `precum_through_clothes`, `bra_aside`, `bulge_to_face`, `penis_under_mask`, `naked_vest` |

### Support確認

候補表のsupport列で確認できます。Conditional Rate / Raw Lift別のtop20内件数は以下です。

| 方式 | 1 | 2–5 | 6–10 | 11–99 | 100以上 |
|---|---:|---:|---:|---:|---:|
| Conditional Rate | 0 | 0 | 0 | 0 | 20 |
| Raw Lift | 0 | 2 | 6 | 11 | 1 |

---

## five_special_small

### 1. Core内容

base_count: **21**

| statistics canonical | 対応する既存Special2788エントリ（ID: Prompt identity — 日本語） |
|---|---|
| `drooling` | 2158: `drooling` — よだれ |
| `ejaculation` | 366: `ejaculation` — 射精<br>1287: `ejaculation between breasts` — 射精が乳房の間にある描写 |
| `hetero` | 2358: `hetero` — 男女・異性間の性的関係 |
| `see-through_clothes` | 2120: `see-through clothes` — 透ける衣服<br>2135: `see-through` — 透ける衣服<br>2136: `transparent clothing` — 透ける衣服<br>2768: `seethrough` — 透ける衣服の別名・表記揺れ |
| `sex` | 54: `sex` — 性交・性行為<br>66: `fuck` — 性交を表す露骨な俗語<br>67: `fucking` — 性交を表す露骨な俗語 |

### Conditional Rate top20

| Rank | canonical tag | 日本語訳（既存Special2788にある場合） | co_count | support | conditional_rate | raw_lift | runtime_global_count | role | ユーザー確認 |
|---:|---|---|---:|---|---:|---:|---:|---|---|
| 1 | `cum` | 精液 / 射精描写 / 精子に関係する表現 | 21 | 11–99 | 100.00% | 37.65 | 297,982 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 2 | `1girl` | — | 19 | 11–99 | 90.48% | 1.31 | 7,773,799 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 3 | `pussy` | 女性器 / 膣に関係する表現 / 外陰部に関係する表現 / 女性器の別名・表記揺れ | 19 | 11–99 | 90.48% | 22.45 | 452,063 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 4 | `blush` | — | 18 | 11–99 | 85.71% | 2.51 | 3,823,437 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 5 | `vaginal` | 膣性交 / 膣への挿入 | 18 | 11–99 | 85.71% | 37.76 | 254,668 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 6 | `breasts` | 乳房 / 乳房の別名・表記揺れ | 17 | 11–99 | 80.95% | 2.00 | 4,542,658 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 7 | `cum_in_pussy` | 体内の精液を示す語 / 膣内の精液 / 体内射精に関係する表現 / 膣・体内射精後の精液描写に関係する表現 / 膣・体内射精に関係する表現 | 17 | 11–99 | 80.95% | 72.29 | 125,629 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 8 | `penis` | 陰茎 / 陰茎に関係する表現 / 陰茎の別名・表記揺れ | 17 | 11–99 | 80.95% | 17.52 | 518,431 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 9 | `1boy` | — | 15 | 11–99 | 71.43% | 4.12 | 1,945,837 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 10 | `solo_focus` | — | 15 | 11–99 | 71.43% | 17.49 | 458,279 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 11 | `nipples` | 乳首が見える / 乳首に関係する表現 | 14 | 11–99 | 66.67% | 7.41 | 1,009,122 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 12 | `open_mouth` | — | 14 | 11–99 | 66.67% | 2.29 | 3,272,995 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 13 | `censored` | — | 13 | 11–99 | 61.90% | 11.72 | 592,432 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 14 | `long_hair` | — | 12 | 11–99 | 57.14% | 1.11 | 5,790,640 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 15 | `bar_censor` | — | 11 | 11–99 | 52.38% | 26.88 | 218,601 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 16 | `saliva` | 唾液 | 11 | 11–99 | 52.38% | 43.30 | 135,719 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 17 | `large_breasts` | — | 10 | 6–10 | 47.62% | 2.59 | 2,064,758 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 18 | `sweat` | — | 10 | 6–10 | 47.62% | 7.56 | 706,702 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 19 | `teeth` | — | 10 | 6–10 | 47.62% | 7.44 | 717,952 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 20 | `thighhighs` | 裸体・サイハイに関係する表現 / 太腿までの長い靴下・ニーハイの別名・表記揺れ | 10 | 6–10 | 47.62% | 3.73 | 1,430,723 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |

### Raw Lift top20

| Rank | canonical tag | 日本語訳（既存Special2788にある場合） | co_count | support | conditional_rate | raw_lift | runtime_global_count | role | ユーザー確認 |
|---:|---|---|---:|---|---:|---:|---:|---|---|
| 1 | `strapless_dildo` | 原語「strapless」・ディルドに関係する表現 | 1 | 1 | 4.76% | 10684.15 | 50 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 2 | `spreading_another's_legs` | — | 2 | 2–5 | 9.52% | 8978.28 | 119 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 3 | `squirting_dildo` | 射精を模擬する機構を持つディルド / 射精を模擬するディルドの別表記 | 1 | 1 | 4.76% | 6848.82 | 78 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 4 | `against_mirror` | — | 1 | 1 | 4.76% | 2282.94 | 234 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 5 | `pegging` | ストラップオン等で相手の肛門を挿入する行為 | 2 | 2–5 | 9.52% | 1989.60 | 537 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 6 | `coat_lift` | — | 1 | 1 | 4.76% | 1740.09 | 307 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 7 | `dance_studio` | — | 1 | 1 | 4.76% | 1623.73 | 329 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 8 | `ear_tufts` | — | 1 | 1 | 4.76% | 1417.00 | 377 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 9 | `belly-to-belly` | — | 1 | 1 | 4.76% | 1081.39 | 494 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 10 | `tying_footwear` | — | 1 | 1 | 4.76% | 1041.34 | 513 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 11 | `red_pubic_hair` | — | 2 | 2–5 | 9.52% | 1034.28 | 1,033 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 12 | `gerudo_set_(zelda)` | — | 1 | 1 | 4.76% | 863.02 | 619 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 13 | `kazamatsuri_institute_high_school_uniform` | — | 1 | 1 | 4.76% | 787.92 | 678 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 14 | `ornate_ring` | — | 2 | 2–5 | 9.52% | 703.83 | 1,518 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 15 | `guided_penetration` | 手などで位置を誘導しながら行う挿入 / 相手の挿入を手で誘導する行為の別名 | 2 | 2–5 | 9.52% | 644.79 | 1,657 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 16 | `torn_bodystocking` | — | 2 | 2–5 | 9.52% | 604.65 | 1,767 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 17 | `shared_object_insertion` | 共有された・物体・挿入に関係する表現 / 共有された・ディルドに関係する表現 / 共有された・挿入に関係する表現 | 1 | 1 | 4.76% | 589.63 | 906 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 18 | `grey_pubic_hair` | — | 1 | 1 | 4.76% | 583.83 | 915 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 19 | `uvula` | — | 2 | 2–5 | 9.52% | 504.92 | 2,116 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 20 | `blank_stare` | — | 2 | 2–5 | 9.52% | 468.40 | 2,281 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |

### 差分

| 区分 | 候補 |
|---|---|
| 両方のtop20 | — |
| Conditional Rateだけ | `cum`, `1girl`, `pussy`, `blush`, `vaginal`, `breasts`, `cum_in_pussy`, `penis`, `1boy`, `solo_focus`, `nipples`, `open_mouth`, `censored`, `long_hair`, `bar_censor`, `saliva`, `large_breasts`, `sweat`, `teeth`, `thighhighs` |
| Raw Liftだけ | `strapless_dildo`, `spreading_another's_legs`, `squirting_dildo`, `against_mirror`, `pegging`, `coat_lift`, `dance_studio`, `ear_tufts`, `belly-to-belly`, `tying_footwear`, `red_pubic_hair`, `gerudo_set_(zelda)`, `kazamatsuri_institute_high_school_uniform`, `ornate_ring`, `guided_penetration`, `torn_bodystocking`, `shared_object_insertion`, `grey_pubic_hair`, `uvula`, `blank_stare` |

### Support確認

候補表のsupport列で確認できます。Conditional Rate / Raw Lift別のtop20内件数は以下です。

| 方式 | 1 | 2–5 | 6–10 | 11–99 | 100以上 |
|---|---:|---:|---:|---:|---:|
| Conditional Rate | 0 | 0 | 4 | 16 | 0 |
| Raw Lift | 12 | 8 | 0 | 0 | 0 |

---

## five_special_medium

### 1. Core内容

base_count: **275**

| statistics canonical | 対応する既存Special2788エントリ（ID: Prompt identity — 日本語） |
|---|---|
| `breasts` | 2170: `breasts` — 乳房<br>2631: `boobs` — 乳房の別名・表記揺れ<br>2632: `breast` — 乳房の別名・表記揺れ<br>2633: `oppai` — 乳房の別名・表記揺れ<br>2784: `tits` — 乳房の別名・表記揺れ |
| `covered_nipples` | 725: `covered nipples` — 乳首を覆って隠している状態<br>1251: `covered erect nipples` — 覆われた・勃起した・乳首に関係する表現<br>1252: `erect nipple` — 勃起した・乳首に関係する表現<br>1253: `erect nipples` — 勃起した・乳首に関係する表現<br>1254: `erect nipples under clothes` — 勃起した・乳首が衣服の下・内側にある描写<br>1255: `errect nipples` — 原語「errect」・乳首に関係する表現<br>1256: `perky nipples` — 原語「perky」・乳首に関係する表現<br>1577: `erect nipplees` — 乳首を覆って隠している状態の別名・表記揺れ |
| `groping` | 35: `groping` — 身体を性的にまさぐる・触る行為<br>1585: `fondle` — 身体を性的にまさぐる・触る行為の別名・表記揺れ<br>1586: `fondling` — 身体を性的にまさぐる・触る行為の別名・表記揺れ<br>1587: `grope` — 身体を性的にまさぐる・触る行為の別名・表記揺れ |
| `pussy` | 509: `pussy` — 女性器<br>1248: `vagina` — 膣に関係する表現<br>1249: `vulva` — 外陰部に関係する表現<br>1574: `manko` — 女性器の別名・表記揺れ |
| `spread_legs` | 2360: `spread legs` — 開脚。単独は非性的文脈もあるので共起判定<br>2362: `legs spread` — 開脚の表記揺れ<br>2760: `open legs` — 開脚。単独は非性的文脈もあるので共起判定の別名・表記揺れ |

### Conditional Rate top20

| Rank | canonical tag | 日本語訳（既存Special2788にある場合） | co_count | support | conditional_rate | raw_lift | runtime_global_count | role | ユーザー確認 |
|---:|---|---|---:|---|---:|---:|---:|---|---|
| 1 | `grabbing_another's_breast` | 他人の乳房を掴む行為 / 他人の乳房を掴む行為の別名・表記揺れ | 241 | 100以上 | 87.64% | 116.10 | 84,680 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 2 | `hetero` | 男女・異性間の性的関係 | 210 | 100以上 | 76.36% | 12.20 | 702,398 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 3 | `censored` | — | 206 | 100以上 | 74.91% | 14.18 | 592,432 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 4 | `blush` | — | 205 | 100以上 | 74.55% | 2.19 | 3,823,437 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 5 | `1girl` | — | 203 | 100以上 | 73.82% | 1.07 | 7,773,799 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 6 | `long_hair` | — | 193 | 100以上 | 70.18% | 1.36 | 5,790,640 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 7 | `vaginal` | 膣性交 / 膣への挿入 | 188 | 100以上 | 68.36% | 30.11 | 254,668 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 8 | `penis` | 陰茎 / 陰茎に関係する表現 / 陰茎の別名・表記揺れ | 183 | 100以上 | 66.55% | 14.40 | 518,431 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 9 | `open_mouth` | — | 179 | 100以上 | 65.09% | 2.23 | 3,272,995 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 10 | `sex` | 性交・性行為 / 性交を表す露骨な俗語 | 173 | 100以上 | 62.91% | 20.68 | 341,256 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 11 | `1boy` | — | 161 | 100以上 | 58.55% | 3.38 | 1,945,837 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 12 | `large_breasts` | — | 149 | 100以上 | 54.18% | 2.94 | 2,064,758 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 13 | `sweat` | — | 136 | 100以上 | 49.45% | 7.85 | 706,702 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 14 | `nipples` | 乳首が見える / 乳首に関係する表現 | 132 | 100以上 | 48.00% | 5.34 | 1,009,122 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 15 | `mosaic_censoring` | — | 124 | 100以上 | 45.09% | 18.39 | 275,107 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 16 | `cum` | 精液 / 射精描写 / 精子に関係する表現 | 109 | 100以上 | 39.64% | 14.92 | 297,982 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 17 | `smile` | — | 100 | 100以上 | 36.36% | 1.04 | 3,905,723 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 18 | `solo_focus` | — | 96 | 11–99 | 34.91% | 8.55 | 458,279 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 19 | `thighs` | — | 96 | 11–99 | 34.91% | 5.15 | 760,010 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 20 | `nude` | 裸体・全裸 / 裸・裸体 | 95 | 11–99 | 34.55% | 6.36 | 609,823 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |

### Raw Lift top20

| Rank | canonical tag | 日本語訳（既存Special2788にある場合） | co_count | support | conditional_rate | raw_lift | runtime_global_count | role | ユーザー確認 |
|---:|---|---|---:|---|---:|---:|---:|---|---|
| 1 | `vyshyvanka` | — | 3 | 2–5 | 1.09% | 1274.81 | 96 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 2 | `towel_pull` | — | 2 | 2–5 | 0.73% | 971.29 | 84 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 3 | `ukrainian_clothes` | — | 3 | 2–5 | 1.09% | 893.30 | 137 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 4 | `pasties_removed` | 乳首用前貼り・外した・取り除いたに関係する表現 | 2 | 2–5 | 0.73% | 832.53 | 98 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 5 | `torn_buruma` | — | 1 | 1 | 0.36% | 832.53 | 49 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 6 | `announcer` | — | 1 | 1 | 0.36% | 755.45 | 54 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 7 | `pasteur_pipette` | — | 1 | 1 | 0.36% | 679.90 | 60 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 8 | `breast_sucking_through_clothes` | — | 3 | 2–5 | 1.09% | 672.43 | 182 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 9 | `unconventional_vibrator` | 原語「unconventional」・バイブレーターに関係する表現 | 1 | 1 | 0.36% | 657.97 | 62 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 10 | `borrowing_race` | — | 1 | 1 | 0.36% | 647.52 | 63 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 11 | `imminent_orgasm` | 絶頂の直前を示す表現 | 2 | 2–5 | 0.73% | 618.09 | 132 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 12 | `paizuri_while_penetrated` | パイズリ・〜しながら・挿入されたに関係する表現 | 1 | 1 | 0.36% | 608.87 | 67 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 13 | `weathergirl` | — | 1 | 1 | 0.36% | 591.22 | 69 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 14 | `parasite_suit_(darling_in_the_franxx)` | — | 8 | 6–10 | 2.91% | 512.33 | 637 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 15 | `las_plagas` | — | 1 | 1 | 0.36% | 503.63 | 81 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 16 | `breast_pull` | — | 1 | 1 | 0.36% | 485.64 | 84 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 17 | `hand_on_another's_headwear` | — | 1 | 1 | 0.36% | 479.93 | 85 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 18 | `cum_on_lips` | 唇に付いた精液 | 1 | 1 | 0.36% | 370.85 | 110 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 19 | `finger_pointer` | — | 1 | 1 | 0.36% | 367.51 | 111 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |
| 20 | `fortified_suit_(imperial_royal_guard)` | — | 2 | 2–5 | 0.73% | 345.71 | 236 | other | [ ] Promptに足したい<br>[ ] 場合によっては使う<br>[ ] 不要 |

### 差分

| 区分 | 候補 |
|---|---|
| 両方のtop20 | — |
| Conditional Rateだけ | `grabbing_another's_breast`, `hetero`, `censored`, `blush`, `1girl`, `long_hair`, `vaginal`, `penis`, `open_mouth`, `sex`, `1boy`, `large_breasts`, `sweat`, `nipples`, `mosaic_censoring`, `cum`, `smile`, `solo_focus`, `thighs`, `nude` |
| Raw Liftだけ | `vyshyvanka`, `towel_pull`, `ukrainian_clothes`, `pasties_removed`, `torn_buruma`, `announcer`, `pasteur_pipette`, `breast_sucking_through_clothes`, `unconventional_vibrator`, `borrowing_race`, `imminent_orgasm`, `paizuri_while_penetrated`, `weathergirl`, `parasite_suit_(darling_in_the_franxx)`, `las_plagas`, `breast_pull`, `hand_on_another's_headwear`, `cum_on_lips`, `finger_pointer`, `fortified_suit_(imperial_royal_guard)` |

### Support確認

候補表のsupport列で確認できます。Conditional Rate / Raw Lift別のtop20内件数は以下です。

| 方式 | 1 | 2–5 | 6–10 | 11–99 | 100以上 |
|---|---:|---:|---:|---:|---:|
| Conditional Rate | 0 | 0 | 0 | 3 | 17 |
| Raw Lift | 12 | 7 | 1 | 0 | 0 |

---
