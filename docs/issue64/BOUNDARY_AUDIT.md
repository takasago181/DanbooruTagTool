# Issue #64 pilot boundary / error-pattern audit

2026-09-12 — implementation-side inspection, **pending independent DEV/AUDIT acceptance**.

全173行のcanonical、production表示、usage、抽出理由、提案経路を照合した。
分類の正解ラベル集は存在せず、独立監査も未実施のため、誤分類率・precisionは計算しない。
以下は観察した曖昧性と、分類時に避けた誤りのパターンである。
実稼働classifierがこれらの誤りを出したという意味ではない。regex classifierは作成していない。
日本語表示は意味を調べる補助で、曖昧なcanonicalのsemantic authorityにはしない。

| 実例 | 避ける誤分類 | pilotでの扱い / 残る監査点 |
| --- | --- | --- |
| `bow`（リボン） | 英語の一般的多義から武器・お辞儀へ送る | 衣装/装飾が主、道具/小物が副。canonical定義との照合は独立監査対象 |
| `back`（背中） / `looking_back`（振り返る） | backの部分一致で一括する | 身体と視線に分離 |
| `cross`（十字） | 記号と十字架の物体を無条件に併合 | 記号を提案。物体副経路は定義確認まで追加しない |
| `;q` | 記号列だから画中文字とする | 表情。production表示のウインク・舌の表情を参照 |
| `heart` / `heart_hands` | heartの部分一致で同じ分類へ送る | 記号としぐさを分離。後者はポーズにも副経路 |
| `cowboy_shot` | cowboyという役柄へ送る | 構図・画角 |
| `from_above` / `looking_at_viewer` | カメラ位置と視線方向を併合 | 構図と視線に分離 |
| `human_tower` | towerから建築・背景へ送る | 集団ポーズ案。人数分類とは異なる発見用途 |
| `fruit_hair_ornament` / `fruit` | 修飾モチーフから両方を食べ物にする | 装飾と食べ物を分離 |
| `blue_eyes` / `black_boots` / `white_background` | 色修飾をすべて色の主経路へ送る | 髪・顔 / 衣装 / 背景。色副経路を無条件に増殖しない |
| `blood_writing` / `blood` | 材料名だけで文字を見失う | 文字を主、身体を副。血そのものは身体 |
| `bad_neck` / `bad_anatomy` | 部位名なので身体へ送る | 作画状態の経路。品質や生成効能の保証ではない |
| `personal_terminal`（PET） | 表示中のPETから動物へ送る | 道具案。固有装置の追加説明は作らない |
| `cat` / `cat_ears` / `wolf_tail` | 生物全体と身体部位を混ぜる | 生き物と身体に分離。耳・尾の副経路増殖は保留 |
| `tree` / `forest` / `bonsai` | 植物すべてを背景へ送る | 個体・植物と場所を分離 |
| `bootes_(constellation)` | 星座を天候と同義に扱う | 光・時間・天候 + 背景の暫定案。空・星の入口を含むラベルにするかDEV要判断 |
| `monochrome` / `greyscale` | 同義としてcanonicalを統合 | identityは別のまま画面表現が主、色が副 |
| `maid` / `witch` / `jester` | 役柄と衣服のタグを同一視 | 人物・役柄案。衣装にも入口が必要かDEV要判断 |
| `*_school_uniform` / `*_(cosplay)` | 固有人物や作品のontologyへ拡大 | 明示された制服・衣装の浅い経路。別canonicalへの置換なし |
| `holding_knife_behind_back` | knifeだけを見て関係・動作を失う | 行為/物を持つが主、武器が副 |
| `covering_breasts` / `partially_visible_vulva` | すべて身体部位一覧へ送る | 隠す・見えるという露出状態を主。前者は接触にも副経路 |
| `naked_cloak` / `naked_dress` | naked接頭辞で同じ規則を適用 | 前者は裸マントという着方を提案、後者はデザインとの境界が不明でunresolved |
| `screen_zoom` | screenから構図と断定 | 画面内表現とカメラ切り取りの境界が不明でunresolved |
| `light_in_heart` / `uma_stars_(umamusume)` / `koe_naki_sakana` | light/stars/fish等から語尾分類 | 固有句の対象が未確認でunresolved |
| `viewer_on_leash` / `hand_in_bra` | 接触語から性的行為へ断定 | 文脈・主経路が不足しunresolved。強度や年齢による除外ではない |
| `highres` / `text` / `see-through` | 自然な例だとしてpopulation外のtagを追加 | production populationにないため選ばない。別表記への自動正規化も行わない |

## Concentration / catch-all pressure

- 可視catch-allカテゴリは設けていない。161件の候補にprimary path、12件に明示的なUNRESOLVEDを設定した。
- 12/173 = **6.94%** は潜在的なcatch-all流入圧として別計上する。「その他が0だから問題なし」としない。
- 最大主経路は衣装40/161 = **24.84%**。内訳は服・下着・靴13、衣装・コスプレ・装備12、制服8、装飾7。今回、未解釈語を衣装に押し込んで0 unresolvedにすることは避けた。
- 道具・小物15/161 = 9.32%、画風・加工・画面表現9/161 = 5.59%。両者も曖昧語の隠れcatch-allになり得るため独立監査する。
- 色・柄・形の主経路は1件のみ、副経路込み3件。色修飾を対象物の経路に置く方針の影響であり、このpilotだけで色カテゴリの有用性を確定できない。
- 人物役柄、生物全体と部位、空の星座、文字の形についてラベル・副経路の受入判断が必要。
- usage層は対象母集団より高頻度を厚く抽出している。衣装24.84%やunresolved6.94%を30,629件の予測分布に外挿しない。

## Unresolved queue (12)

| canonical | 必要な次の確認 |
| --- | --- |
| `aa-12` | 型番のcanonical定義・武器候補の確認 |
| `hand_in_bra` | 接触と衣服状態の主経路方針 |
| `koe_naki_sakana` | 固有句が指す物・衣装・作品等のcanonical定義 |
| `light_in_heart` | 固有タイトルか描画現象か |
| `minna_de_enjoy!_spojoy_park_(project_sekai)` | 公園・衣装・イベント等の対象 |
| `naked_dress` | 衣服デザインと露出状態の区別 |
| `nijigasaki_7th_live!_new_tokimeki_land` | イベント名とタグの具体的対象 |
| `ribbon_bar` | 勲章・服飾等の多義の解決 |
| `saihate_e_to_tobu_kimi_e_(project_sekai)` | 固有句の具体的対象 |
| `screen_zoom` | 画面内の拡大表現と撮影構図の区別 |
| `uma_stars_(umamusume)` | 衣装・マーク等の対象 |
| `viewer_on_leash` | 視点・関係・接触の主経路方針 |

外部wiki取得や画像サンプル検証は今回実施していない。定義の根拠が不足する行は推測で確定せず、このqueueからDEV/AUDITが確認する。
UNRESOLVEDにはbrowse pathがなく、データが欠落したことを意味しない。対象集合には保持し、catalogにも明示する。
残る30,456件はNOT_SAMPLEDであり、unresolved12件に混ぜない。

## Proposed next Gate

DEV/AUDITがtaxonomy・主副経路・12件の扱い・追加pilotの必要性を判断する。
推奨確認は色/柄、空/星、役柄/衣装、希少固有名の追加例であり、実行はpilot受入後の指示に従う。
受入前のfull rollout、main merge、#34着手は行わない。機械的整合性のテスト成功は意味分類のGate PASSではない。
