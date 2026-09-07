# Stage 5 追加監査 — 2026-09-05

**再判定: APPROVE WITH CONDITIONS。** raw sourceの双方向indexは保持可能。ただしcanonical query/countの意味統一と、大規模Specialの待ち時間対策は次の承認条件として残す。Stage 6、production rebuild、Counter最適化は実施していない。

## A. 全source General tagの対応

既存TagKnowledgeCore.resolve_exactとverified alias CSVを使用。literal canonicalを最優先し、次にnormalized canonical、aliasを評価。曖昧候補は統合しない。Semantic/Japaneseの概念一致だけでsource tagをcanonicalへ変換しない。今回normalized canonicalのみの一意一致も0件であり、下表の第5分類に一意一致は混入していない。

指定6分類に含まれないcurrent non-General canonical完全一致を第7分類として追加した。これはsource Generalという分類とcurrent dictionary分類の差であり、aliasではない。

| 分類 | unique tags | runtime occurrences | 全entries比 | 1語以上含むposts |
|---|---:|---:|---:|---:|
| 1. exact current General canonical | 30,591 | 353,514,880 | 99.702080% | 11,218,293 |
| 2. unique alias → current General | 98 | 99,509 | 0.028065% | 99,120 |
| 3. unique alias → current non-General | 4 | 71 | 0.000020% | 71 |
| 4. ambiguous alias | 0 | 0 | 0.000000% | 0 |
| 5. normalization衝突/曖昧 | 0 | 0 | 0.000000% | 0 |
| 6. runtime-only | 72,491 | 953,788 | 0.268998% | 820,086 |
| 7. exact current non-General（追加） | 14 | 2,972 | 0.000838% | 2,912 |

合計103,198語 / 354,571,220 entries。post列は分類間で重複するため加算しない。母集団は11,218,362 posts。今回のambiguous/normalizationが0件でも、辞書全体に曖昧aliasが存在しないことは意味しない。canonical exactにshadowされたaliasは優先順位どおり不採用。

前回「72,607語未解決」はGeneral canonical完全一致以外という意味だった。alias 102語とnon-General完全一致14語を除くとruntime-onlyは72,491語。語数は多いが出現比は0.268998%、それを含むpostは820,086（約7.31%）。少数出現だから無視してよいとは解釈しない。

代表例: alias `china_dress → qipao` 73,589回、`holding_shoes → holding_unworn_shoes` 4,197回。runtime-only `eyebrows` 37,203、`looking_away` 33,968、`uniform` 24,926。Semantic一致だけの65語（例 `areolae`）もruntime-onlyのまま。non-General完全一致例 `listen!!` 511回。分類ごとの最大50件はmapping_summary.json、全件はall_source_tags.csvに保存。

## Canonical統合の影響

同じcurrent canonicalへ複数source tagが対応するのは58グループ、source tag合計118語。うち36グループで同一post重複がある。重複postの和集合は398 posts、単純加算が余計に数えるentriesは398。全重複postはpost→tags側でも確認した。

global countは各source postingの和集合の件数。全current対応canonicalのraw count / source count合計 / union count / 増分をall_canonical_global_counts.csv、複数sourceグループと実post例をcanonical_merges.csvに保存。単独aliasだけが対応しcanonicalのraw postingがないケースも全件表に含めた。

| canonical | raw count | 統合後union count | 増分 |
|---|---:|---:|---:|
| `qipao` | 0 | 73,589 | 73,589 |
| `holding_unworn_shoes` | 10 | 4,206 | 4,196 |
| `flower_hairclip` | 182 | 2,590 | 2,408 |
| `opening_own_clothes` | 0 | 2,099 | 2,099 |
| `self-cosplay` | 0 | 1,874 | 1,874 |
| `k/da_(league)` | 0 | 1,802 | 1,802 |
| `tokyo` | 0 | 1,708 | 1,708 |
| `star_guardian_(league)` | 0 | 1,196 | 1,196 |

Specialはresolved **2,443エントリ / distinct canonical 1,724語**。2,443はunique canonical数ではない。統合で変わるのは13エントリ / 7 canonical。rawで0件の12エントリ中4エントリ（2 canonical）が回復し、8エントリは対応sourceなしのまま。

| 影響するSpecial canonical | raw | union |
|---|---:|---:|
| `box_tie` | 896 | 911 |
| `mechanical_penis` | 117 | 149 |
| `off-color_cum` | 0 | 56 |
| `penetrating_while_penetrated` | 0 | 223 |
| `penis_doodle` | 35 | 52 |
| `presenting_own_body` | 18722 | 18723 |
| `pussyjob` | 5120 | 5147 |

全Special ID・原語・日本語・対応source・増分はspecial_impact.csvに保存。current dictionary post_countはこの統計計算に使用していない。General-only source列からcurrent non-Generalへ対応するcountは、そのcanonicalの全カテゴリpost数を網羅する保証がないため別扱いが必要。

## A/B/C案の評価（提案のみ）

| 案 | 評価 |
|---|---|
| A: raw ID維持＋canonical mapping layer | **推奨**。既存indexと証拠post/source名を保ち、少数のalias差分を明示できる。dictionary/alias hashと解決方針versionを対応表に固定する。 |
| B: build時collapse | 現時点で不要。raw identityを失うか別保存が必要になり、再buildも必要。General/current非Generalの扱いを未決定のまま固定すべきでない。 |
| C: raw exactのみ＋未対応を表示 | 暫定監査閲覧には最小だが、回復可能なSpecialを0件扱いする問題が残り完成版には不十分。 |

Aの意味契約: 1 canonical内では対応source postingをOR、異なるCore canonical間ではAND。candidateもpostごとにcanonicalで重複除去し、global/base/coすべてに同一mappingを適用する。raw co_countを表示名だけ変えて加算してはいけない。曖昧aliasは保留し、raw-onlyとresolved canonicalのnamespaceを区別する。これは設計提案でありruntime APIは変更していない。

## B. 実Special workload

Generalかつraw postingのあるresolved Specialから選定。unique canonicalでbase>100,000は53語、>500,000は12語、>1,000,000は4語。各閾値を超える実条件を測定した。最小の正のbaseは11であり、base=1を捏造していない。

単一6条件＋2/3/5 Special各2条件、計12条件。複数Specialは上位100 canonicalから固定seed 20260905で各60組抽出し、base≈100/10,000に近い組を選定。全語に実Special IDを記録し、同一canonicalを別Specialとして水増ししない。これは実在語による負荷試験であり、人間のCore選択分布を代表する利用ログではない。

条件ごとに新しいprocessを起動し、TagKnowledgeCoreや対応監査のメモリを持ち込まない。1回warm-up後、ANDは15回、aggregate/totalはbase>100,000で5回、その他15回。p95はNumPy線形percentileで、5標本のtail推定は粗い。OS cacheはwarmの可能性があるためcold startとは呼ばない。totalはANDとaggregateをまとめて別に反復測定しており、各medianの単純和ではない。RSSは各条件内のaggregate反復終了直後のworking set。mmapのfile sizeやvirtual sizeではない。

| Special条件（canonical） | base | AND median/p95 ms | Aggregate median/p95 ms | Total median/p95 ms | aggregate後RSS MiB |
|---|---:|---:|---:|---:|---:|
| cum_on_figure | 11 | 0.005 / 0.009 | 0.114 / 0.177 | 0.115 / 0.157 | 47.9 |
| gold_chastity_cage | 100 | 0.005 / 0.013 | 1.221 / 1.501 | 1.223 / 1.574 | 48.9 |
| backboob | 10,039 | 0.022 / 0.064 | 106.942 / 115.943 | 104.080 / 107.268 | 131.1 |
| shirt_lift | 101,527 | 0.157 / 0.655 | 1070.088 / 1077.005 | 1127.547 / 1165.392 | 479.3 |
| penis | 518,431 | 2.425 / 3.067 | 5857.133 / 5965.080 | 5474.607 / 5504.616 | 1028.0 |
| nipples | 1,009,122 | 3.067 / 3.614 | 10085.886 / 10172.736 | 10027.547 / 10123.209 | 1348.1 |
| clothed_female_nude_male + genderswap | 101 | 0.256 / 0.415 | 1.183 / 1.638 | 1.438 / 1.630 | 49.3 |
| erection + open_clothes | 8,805 | 2.953 / 3.079 | 110.421 / 113.227 | 114.109 / 117.017 | 116.4 |
| bare_legs + completely_nude + uncensored | 92 | 1.894 / 1.974 | 1.285 / 1.497 | 3.189 / 3.639 | 51.3 |
| ass + facial + penis | 3,902 | 4.854 / 5.950 | 49.144 / 50.800 | 55.056 / 56.622 | 90.7 |
| drooling + ejaculation + hetero + see-through_clothes + sex | 21 | 4.365 / 4.717 | 0.299 / 0.376 | 4.590 / 5.177 | 53.8 |
| breasts + covered_nipples + groping + pussy + spread_legs | 275 | 19.716 / 20.308 | 3.732 / 3.979 | 24.356 / 25.809 | 72.1 |

最大測定base 1,009,122ではAggregate median 10.09秒、total median 10.03秒。現Counter実装は大きい核を選ぶ操作で秒単位の待ち時間になり、インタラクティブな完成版として即時更新を保証できない。論理双方向構造やpacked CSRの問題とCounter traversalの問題は分けて評価する。今回最適化していない。

## 再判定と停止条件

**APPROVE WITH CONDITIONS**: raw統計基盤としてのStage 5は維持。無条件の製品完成承認ではない。条件は (1) Aのcanonical/raw namespaceと統計意味契約を監査承認する、(2) 大規模Specialの応答時間目標と集計改善を別依頼で検証する、(3) Forge同居の実測を行う。今回のデータでphysical format再設計やproduction再buildを正当化する根拠はない。Stage 6に進まず停止する。

## 作業報告（8項目）

1. 変更した項目: 追加監査のrunner・CSV/JSON・本報告のみ追加。
2. 変更しなかった項目: production index全ファイル、runtime/knowledge/search実装、正本、Stage 2/5既存Decision、Stage 6。前後SHA-256一致を保存。
3. 新規作成ファイル: tools/stage5_post_audit.py、tools/stage5_post_audit_report.py、benchmarks/stage5_post_audit/配下、docs/stage_reports/STAGE5_POST_AUDIT.md。
4. バックアップ先: 既存ファイルの上書きなし。入力hash記録はbenchmarks/stage5_post_audit/input_hashes_*.json。
5. 実施したテスト: 全分類合計・全posting長/global count一致・全重複postのreverse照合・既存index hash/構造検証・保護ファイル前後hash・既存pytest。
6. テスト結果: 数値検算とhash検証PASS。既存pytest 61 passed in 8.73s。実行記録はbenchmarks/stage5_post_audit/pytest_result.txt。
7. 未解決事項: 上記3条件、p95の標本数制約、未測定の他Special/実利用分布。raw Parquetの再走査は今回行わず、既存検証済みindex上の監査である。
8. 次にChatGPTへ渡す情報: 本書、mapping_summary.json、all_source_tags.csv、all_canonical_global_counts.csv、canonical_merges.csv、special_impact.csv、special_workloads.json、validation.json。既存docs/decisions/DATA_SOURCE_DECISION.md / docs/architecture/INDEX_ARCHITECTURE_DECISION.mdと併読。

## 最終Stage 5修正（2026-09-05）

監査後の確定方針に従い、既存 `stage5-packed-csr-v1` raw physical indexは変更せず、`data/runtime_index/canonical_overlay.json` を追加した。overlayはcurrent canonical → source tag IDの対応、7種類のidentity status、dictionary snapshot/hash、merge group数、payload hashを保持する。unique aliasは論理的にcurrent canonicalへ対応し、複数source tagのcount/post/co_countはpost集合unionで扱う。

runtime-only 72,491語、Semantic Bridge一致、source Generalだがcurrent non-Generalのtagは元source identityを維持する。ModelProfile、UI、Recommendation、Stage 6は実装していない。追加テスト後のfull pytestは **63 passed in 8.15s**。
