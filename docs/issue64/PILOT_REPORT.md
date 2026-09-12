# Issue #64 General taxonomy pilot report

2026-09-12 / FROM: DEV implementation (Codex) / TO: DEV・AUDIT

**RESULT: exact populationと173件pilotを返却。taxonomy・意味分類は提案で、pilot受入待ち。full rollout・mergeは未実施。**

Branch: `codex/issue64-general-taxonomy-pilot`

Base: GitHub live main `293181686260a91398334a0fe2d794a5998388cc`。
提出commitはIssue #64のhandoff checkpointに完全SHAを記録する（このレポートを含むcommit）。
提出後に管理文書のroutingを次Issueへ進める権限はDEVにある。

## Authority / scope

指定順にlive mainのCURRENT_STATE、CURRENT_DEV_TASK、Issue #64本文、最新コメント、PERMANENT_RULES、PRODUCT_GOAL_LOCKを確認。
最新コメント `MANAGEMENT ACTIVATION CHECKPOINT — ISSUE #64 CURRENT DEV` は#63 accepted/merged/closed、#64 current、pilot後停止を要求。
開始時のGit接続制限を解消してfetchし、live main SHAとの一致後にbranchを作成した。古いローカル#63 mirrorからは実装していない。
handoff文書更新前にもfetchし、mainが同じSHAであることを確認した。

変更はoffline pilot tool、テスト、独立sidecar、監査成果物、handoff記録のみ。
production runtimeへのloader/UI統合は実施していない。
#56/#34/#42/Stage10の実装、翻訳修正、canonical正規化、automatic insertion、全universe分類は含まない。

## Exact target population evidence

| 項目 | 検証結果 |
| --- | --- |
| 対象 | production `data/runtime/japanese_overlay.json` のentriesキー集合 |
| 件数 / unique canonical | 30,629 / 30,629 |
| overlay bytes | 4,114,120 |
| overlay SHA-256 | `999b42fa76e036ad79f68ef7cd3ff958c94bd42c08ab00dd0394898d0205de76` |
| promotion anchor | `docs/testing/ISSUE55_PRODUCTION_PROMOTION_MANIFEST.json` のpost_sha256と一致 |
| V5 source SHA-256 | `a307a354f6e7c9fb2387464713765795d9949802b345b00eb3cb64659df7fdce` |
| 原表照合 | canonical順序、全display_ja、全search_jaがproductionと完全一致 |
| usage source | `data/source/danbooru-2026-09-02.csv`（snapshot; live usageではない） |
| usage SHA-256 | `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b` |
| exact join | targetのみ30,629件、missing 0、重複0、全件category 0 (General) |
| population materialization | `artifacts/population.txt`、canonicalをUnicode順ソート、UTF-8/LF、末尾LF |
| population SHA-256 | `ca5cc065c92aa38f9daa6b6c8a1f1c13db135057ebfabca076479dfa96872e2b` |

V5原表はpromotion manifestのsource.pathに存在し、そのhashも検証した。
protected原表・overlayは複製してGitへ追加していない。commitするpopulationはcanonical名だけのmembership証拠で、30,629件のtaxonomy割当ではない。
usage CSV全体は参照入力で、対象集合とのjoin以外の行を成果物や分類へ展開しない。
`highres`など元CSVのMeta項目は今回の対象ではない。

## Real population distribution

| usage帯（snapshot post_count） | 母集団 | pilotの実usage帯 |
| --- | ---: | ---: |
| high-usage: 100,000以上 | 581 | 63 |
| ordinary: 1,000–99,999 | 9,160 | 51 |
| rare: 1,000未満 | 20,888 | 59 |
| 合計 | 30,629 | 173 |

最小50、中央値339、25%点114、75%点1,700、90%点9,734、99%点196,931、最大8,363,808。
分位点はソート後のindex `floor(q*(n-1))` で算出する。
rareはこのoverlay内の相対的な低頻度層であり、全Danbooruの最下層を意味しない。

underscore区切りの語片数は1片5,780 / 2片16,832 / 3片5,727 / 4片1,596 / 5片以上694。
3片以上のcompound候補8,017、括弧を含むqualified名3,557。
表示にかな・CJK文字を含まない機械フラグ687件（記号・英字名称も含み、翻訳エラー件数ではない）。
これらは語彙形状の観察であり、全量の意味分類ではない。

## Taxonomy proposal — version `issue64-pilot-v1`

pilot内部の再現用versionを固定した。正式freeze/acceptanceはDEV/AUDIT待ち。
最大深さはgenre + optional subgenreの2段。17 top-level、必要な5ジャンルだけに計16のsubgenreを置いた。
`taxonomy.json` に日本語ラベル、発見の問い、境界、subgenreを定義した。

| genre_id | 日本語の入口 | pilot primary数 |
| --- | --- | ---: |
| PERSON_COUNT | 人物・人数・役柄 | 7 |
| BODY_PART | 身体・部位・状態 | 12 |
| HAIR_FACE | 髪・顔 | 10 |
| EXPRESSION_EMOTION | 表情・感情 | 6 |
| POSE_MOVEMENT | ポーズ・動き | 5 |
| COMPOSITION_CAMERA | 構図・画角 | 5 |
| GAZE_ORIENTATION | 視線・向き | 3 |
| CLOTHING | 衣装 | 40 |
| CLOTHING_STATE_EXPOSURE | 着脱・露出 | 6 |
| ACTION_CONTACT | 行為・接触 | 14 |
| OBJECT_PROP | 道具・小物 | 15 |
| PLACE_BACKGROUND | 場所・背景 | 8 |
| LIGHT_TIME_WEATHER | 光・時間・天候 | 4 |
| COLOR_APPEARANCE | 色・柄・形 | 1 |
| STYLE_QUALITY_META | 画風・加工・画面表現 | 9 |
| LIVING_NATURE | 生き物・植物 | 6 |
| TEXT_SYMBOL | 文字・記号・マーク | 10 |
| 明示的UNRESOLVED | 可視catch-allへの割当なし | 12 |

Issue候補15分類からの変更理由:

- 動物・植物を道具や背景へ押し込まないよう「生き物・植物」を追加。部位は身体、森は場所、食べ物は道具/食べ物に分ける。
- 文字・記号を画風の巨大な受け皿にしないよう「文字・記号・マーク」を追加。顔文字の表情タグとは区別する。
- 人物に役柄、身体に状態、色に柄・形を含む日本語ラベルに変更し、実例から探せる入口にする。
- 画風・品質・メタは「画風・加工・画面表現」と表示。作画状態や漫画形式を含むが、良い品質や生成成功を保証しない。
- 衣装は服13 / costume12 / uniform8 / accessory7に分ける。固有作品のontologyは作らない。
- 色修飾語だけで全件に色の副経路を複製しない。`blue_eyes`は髪・顔、`white_background`は背景を主とする。

## Reproducible pilot and classification method

1. high-usage上位16件（count降順、同数はcanonical昇順）。
2. high-usageの残りからSHA-256順16件。
3. ordinaryからSHA-256順32件、rareから32件。
4. 3片以上compoundから既抽出行を除きSHA-256順32件。
5. 曖昧性・カテゴリ境界を調べる51件をunion。6件は既抽出と重複し、unique合計173件。

hashはUTF-8の `issue64-pilot-v1:` + exact canonical。乱数・実行時時刻・入力順に依存しない。
challenge一覧は`selection.json`に固定し、対象外名・重複・256件超のpilotを拒否する。
high/ordinary/rareの抽出枠と最終pilotの実usage帯は別集計。
compoundは語片数による機械的なstress sampleであり、言語学上の複合語を完全列挙するものではない。

173行をCodexがcanonical、production表示、元CSV alias情報とともに個別に確認して候補経路を記録した。
regex一括分類器、runtime LLM、外部モデル呼出しは実装していない。
`pilot_sidecar.json`はcanonicalキーの独立した分類提案入力。ツールは分類を再推論せず、凍結された提案を検証し、サンプル・分布・catalogを再生成する。
各行にprimary_path / secondary_paths / classification_status / reason / source / reviewed / reviewer / reviewed_atを保持。
日本語表示と検索語はsidecarへ埋め込まず、レビュー用catalog生成時だけoverlayとjoinする。

| 層・境界 | 観察例（production表示を保持） | 提案 / 保留 |
| --- | --- | --- |
| high-usage | `1girl`（1人の女の子）, `smile`（笑顔）, `looking_at_viewer`（こちらを見る） | 人物 / 表情 / 視線 |
| ordinary | `snake`（へび）, `clock`（時計）, `anime_coloring`（アニメ塗り） | 生き物 / 道具 / 画面表現 |
| rare | `under_bridge`（橋の下）, `arzuros_(armor)`（アルツロス（鎧）） | 背景 / 衣装候補 |
| compound | `fruit_hair_ornament`, `holding_knife_behind_back`, `yurigaoka_girls_academy_school_uniform` | 装飾 / 物を持つ + 武器 / 制服 |
| ambiguous | `bow`, `naked_dress`, `screen_zoom`, `light_in_heart` | bowはリボンの候補経路、後3件は定義不足を保留 |

## Pilot result / discovery review

- 提案経路あり **161/173 = 93.06%**。独立review済みは**0**。
- UNRESOLVED **12/173 = 6.94%**（ordinary 2 / rare 10 / high 0）。全件は`BOUNDARY_AUDIT.md`に列挙。
- multi-path **10件**、primary + secondaryの到達経路計**171**。
- 対象集合との差分 **30,456件はNOT_SAMPLED**。全量分類0、production適用0。
- `General → 構図・画角 → カウボーイショット (cowboy_shot)`、`表情・感情 → 笑顔 (smile)`、`衣装 → 装飾・服の細部 → 果物の髪の飾り (fruit_hair_ornament)` の静的な発見経路をcatalogで確認できる。
- canonicalは変換・分割・別名置換していない。上の表示例はofflineレビュー例であり、Prompt出力やUI操作を実装・受入したという意味ではない。

分布の最大は衣装24.84%（161件を分母）。可視catch-allは0だが、未解決6.94%を潜在的な流入圧として扱う。
色の主経路が1件、星座の配置、役柄と衣装の副経路、低頻度固有名の扱いは追加判断が必要。
samplingは高頻度と境界を厚くしたpilotなので、分布・未解決率を30,629件へ外挿しない。
詳細な誤分類リスク・境界監査は`BOUNDARY_AUDIT.md`。正解ラベルや独立監査がないため誤分類率は主張しない。

## Reproduction / tests

workspace rootで実行:

```powershell
python -X utf8 tools/issue64_taxonomy_pilot.py --check
```

原表が別の安全な読取場所にある場合は`--v5-source <audited V5 CSV path>`を指定。
overlay・V5・usageのhash不一致、target差分、sidecar逸脱で停止する。
`--check`は5成果物をbyte比較し、書き込まない。生成時の出力は`docs/issue64/artifacts/`だけ。
fresh cloneにはprotected入力が含まれないため、clone単独では全再生成できない。Git上のmembership、sidecar、catalogとfocused testはprotected入力なしでもレビュー可能。

実施結果:

- 新規focused test: **21 passed**（population重複・hash、抽出順序不変、範囲外、上限、unknown path、過剰階層、silent review昇格、未解決の経路混入、source driftを検証）。
- 最終関連回帰: **64 passed in 14.65s**。`test_issue64_taxonomy_pilot.py`、`test_stage6_5_japanese_overlay.py`、`test_issue55_promote_japanese_overlay.py`、`test_product_fit.py`。
- 生成後`--check`: **5 artifacts一致**。
- `git diff --check`: whitespace errorなし。
- 初回は既定Tempディレクトリの権限で19 passed / 2 setup errors。workspace内の新規basetempへ変更して全21件、その後全64件を再実行し成功。
- full suiteは未実施。live mainの既知9失敗を今回PASSへ読み替えない。
- UI変更なし。実Windows UI検証は今回の段階では対象外。実行環境はWindows / Python 3.12.10。

テスト再実行例（既存フォルダを消さないよう毎回新規名を使用）:

```powershell
python -X utf8 -m pytest tests/test_issue64_taxonomy_pilot.py tests/test_stage6_5_japanese_overlay.py tests/test_issue55_promote_japanese_overlay.py tests/test_product_fit.py -q --basetemp=.pytest_cache/issue64-review-new
```

## Protected / canonical integrity

`protected_before.json`と`protected_verification.json`に86 files、計7,119,591,754 bytesの前後SHA-256を記録。
対象はsource / derived / runtime / runtime_index / runtime_source / special2788 / generation / semantic各dataディレクトリと監査済V5原表。
**changed 0 / added 0 / removed 0 / all_equal true**。
baselineは初回のread-only population生成後、回帰実行前に採取。overlayはそれに加え、作業以前の#55 hashとも一致。
workspace全ignoredファイルの完全バックアップを実施したという意味ではない。
Special canonical CSV/XLSX、product-fit CSV、canonical overlay、巨大index/sourceも上記照合に含む。
旧branchから存在するuntrackedファイル群は追加・整理・削除していない。

## Changed files / handoff

- `.gitattributes`: Issue #64のLF再現性。
- `tools/issue64_taxonomy_pilot.py`: read-only入力、population照合、deterministic pilot、sidecar検証、監査/catalog生成（catalogは静的レビュー表）。
- `tests/test_issue64_taxonomy_pilot.py`: focused contracts / failure modes。
- `docs/issue64/selection.json`, `taxonomy.json`, `pilot_sidecar.json`: 抽出と分類提案の固定入力。
- `docs/issue64/artifacts/population.txt`, `population_evidence.json`, `pilot_samples.json`, `pilot_audit.json`, `pilot_catalog.md`: 再生成可能な証拠。
- `docs/issue64/BOUNDARY_AUDIT.md`, `PILOT_REPORT.md`: 境界・未解決・報告。
- `docs/issue64/protected_before.json`, `protected_verification.json`: protected照合。
- `docs/project/CURRENT_STATE.md`, `CURRENT_DEV_TASK.md`: task branch上のpilot返却checkpoint。current DEVは#64のまま。

VERDICT: **READY_FOR_DEV_AUDIT_PILOT_REVIEW — NOT ACCEPTED / NO FULL ROLLOUT**。

LIMITATION: 意味分類は実装担当の候補、外部定義確認・独立監査・初心者ユーザーテストは未実施。
NEXT: DEV/AUDITが17分類、境界、副経路、12 unresolved、追加pilotの要否を判定する。
受入前に30,629件全量rolloutへ進まない。mergeせず停止し、#34/#42/Stage10へ進まない。
