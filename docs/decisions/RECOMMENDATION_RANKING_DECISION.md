# Stage 6 最終Ranking Decision監査

監査日: 2026-09-05。判定 **C：現結果では製品defaultの最終決定不能**。

技術的な第一候補は **Conditional Rate**。ただし本人の候補採用評価がなく、「上位に安定して出る」と「補助として追加したくなる」を同一視できないため、defaultとして確定しない。新方式・parameter変更・実装のdefault変更・Stage 7着手は行わない。

## 1. 製品目的と判定の意味

Special2788の複数語をCore Tag Setとして保持し、true ANDから不足する補助候補を探し、本人が選択する主従を維持する。一般頻出語の一覧を作ることも、珍しい語の発見だけも、製品の完成条件ではない。Coreに既に含意される候補、場面と無関係な偶発的候補、本人が固定したい衣服・表情・構図などを区別する実用評価が必要である。

今回確認できたのは、6条件での統計・順序・再現性である。評価CoreはStage 5の負荷試験由来であり、本人が選んだ代表的利用条件や利用ログではない。単一Special、base=0/1の実評価もこの保存結果にはない。したがって、Aとして有用性まで承認したり、Bとして未評価のsecondary viewや複合sortを追加する根拠は不足している。

## 2. 証拠・同一性確認

- 読んだ資料: `docs/stage_reports/RECOMMENDATION_RANKING_EVALUATION.md`、Stage 6 CSV/JSON、recommendations.py、Stage 6テスト、評価runner、PRODUCT_GOAL_LOCK、Stage 5 Decision/manifest、canonical overlay。
- 母集団: 11,218,362 posts。snapshot: `nyanko-devs/danbooru2026@ebb02a630201c7b51487e45fb90b3fcf4cbedc20:metadata/posts-snapshot.parquet`。
- physical: `stage5-packed-csr-v1`。logical: raw source + current canonical overlay。scope=general、model_agnostic_statistics=true。
- 6 Core × 4方式 × top20 = **480行**について、CSVとJSONの全保存フィールドを照合し、現indexから再計算して一致。
- Coreの各canonicalに実Special IDが存在し、Core内のdistinct canonical数が2/3/5であることを確認。対応IDは `benchmarks/stage6/decision_audit.json` に保存。
- 記録済みinput hashes一致、overlay payload検証、snapshot一致、監査入力の実行前後hash一致を確認。今回はmulti-GB physical index全体の再hash・raw parquet再走査は行っていない。
- 通常候補のcurrent General制約、Core完全一致除外、alias union/dedup、current_post_count非使用をコードと既存回帰で確認。Special IDの保存主体は引き続きCore Tag Setであり、statistics canonicalは統計取得の橋である。

## 3. 数式監査：4方式は実質2順序

以下、n=base_count、k=co_count、g=global_rate、a=20とする。

| 方式 | score | 監査結論 |
|---|---|---|
| Conditional Rate | k/n | 同一Core内ではkの降順。第一候補。 |
| Raw Lift | (k/n)/g | 稀少なglobal分母に強く反応。defaultには推奨しない。 |
| Wilson lower bound | z=1.959963984540054の二項比率下限 | n共通ではkに単調増加し、Conditional Rateと同じ順序。 |
| Shrunk Lift | ((k+a g)/(n+a))/g | Raw Liftの正の一次変換で、同じ順序。 |

特に、**shrunk_lift = n/(n+a) × raw_lift + a/(n+a)**。
同一Coreではn,aは全候補共通なので、有限の共通priorを20から増やしても順位改善は起こらない。候補ごとのco_count信頼度を選別する補正としては働かない。旧Evaluationの「priorが小さすぎる」「より大きなpriorを検討」という説明は、順位の改善については成立しない。本監査の説明を優先する。

Wilsonも同一Core内ではConditional Rateに対する低support順位改善を提供しない。1/1の下限は約0.2065になるが、n=1では観測された全候補がk=1であるため上位の選別にはならない。小baseで「Wilsonだから安全」と表示してはいけない。

全6条件のtop20は Rate=Wilson、Lift=Shrunk で**順番まで一致**。全候補ではRate=Wilsonが全件一致し、Lift/Shrunkは3条件で厳密な同率内の浮動小数点丸めによる並び差があった。差が数学的に同率の組だけであることを有理数比較で検証した。これは信頼度改善ではない。

## 4. 2/3/5 Special実データ比較

条件名は既存JSON/CSVのcase列と一致する。具体的Core語とSpecial IDは同JSONおよびdecision_audit.jsonを参照。以下の「率系」はConditional RateとWilson、「Lift系」はRaw LiftとShrunkを表し、4方式を省略せず同順位の組で表示する。

「≤1/≤5/≤10」はtop20内の該当件数。broadは便宜的にglobal_rate≥10%、大supportはco_count≥100であり、意味的な有用/不要の分類ではない。

| Core条件 | base | 率系 ≤1/≤5/≤10 | Lift系 ≤1/≤5/≤10 | broad 率/Lift | 大support 率/Lift | 高Lift低support 率/Lift |
|---|---:|---|---|---|---|---|
| two_special_small | 101 | 0/0/0 | 11/18/18 | 8/0 | 1/0 | 0/18 |
| two_special_medium | 8,805 | 0/0/0 | 0/2/8 | 12/0 | 20/1 | 0/8 |
| three_special_small | 92 | 0/0/0 | 9/20/20 | 11/0 | 0/0 | 0/20 |
| three_special_medium | 3,902 | 0/0/0 | 1/6/10 | 7/0 | 20/4 | 0/10 |
| five_special_small | 21 | 0/0/4 | 12/20/20 | 8/0 | 0/0 | 2/20 |
| five_special_medium | 275 | 0/0/0 | 12/19/20 | 7/0 | 17/0 | 0/20 |

高Lift低supportはraw_lift≥5かつco_count≤10。base<100では大support候補が0なのは定義上当然であり、ランキングの欠陥とはしない。

率系は大supportを優先して安定するが、broadが7～12/20（35～60%）を占める。一般的な表情・衣服・構図を選ぶ入口になり得る一方、Coreが既に示す内容の反復も多い。完全一致Coreを除外しても、上位に100%共起の語が残る。これは意味的冗長性の可能性であり、含意関係を本監査で証明したものではない。

Lift系はbroadの占有0だが、それを品質改善と即断できない。base275ではco≥100候補が率系top20に17件あるのにLift系には0件となり、base8,805でも20件→1件になる。高support候補を押し下げる事実は確認できるが「不当に」下げているかは本人の採用判断が必要。逆に、Liftは個別の関連を拾う場合もあり、稀少という理由だけで全件を削除する根拠もない。

top20全件は既存 `benchmarks/stage6/top20_by_method.csv` に保存済みで、今回480行を再検算した。

## 5. Stability

| 条件 | Rate / Wilson | Lift / Shrunk |
|---|---:|---:|
| two_special_small | 16/20 (0.80) | 6/20 (0.30) |
| two_special_medium | 19/20 (0.95) | 9/20 (0.45) |
| three_special_small | 18/20 (0.90) | 8/20 (0.40) |
| three_special_medium | 20/20 (1.00) | 8/20 (0.40) |
| five_special_small | 16/20 (0.80) | 7/20 (0.35) |
| five_special_medium | 17/20 (0.85) | 5/20 (0.25) |

実post IDの偶奇splitを再現して一致した。指標は集合共通数/20で、順位相関やJaccardではない。global frequencyは元の同一snapshot全体で固定し、conditional側だけを分けた簡易感度検査である。独立なholdout global推定、複数seed、時期や作者への頑健性までは測っていない。安定性の優位は率系について示せるが、WilsonやShrunk固有の改善とは言えない。

## 6. Drop-one / Combination specificity

Drop-one: 各行の除外後baseは、保存JSONのCore配列順に対応する。全結果を再計算して一致。Specialを除外する操作やscore加算は行わない。

| 条件 | full base | 各Core項目を1つ除いたbase（順番固定） |
|---|---:|---|
| two_special_small | 101 | 57,226 / 53,852 |
| two_special_medium | 8,805 | 711,321 / 135,385 |
| three_special_small | 92 | 37,803 / 1,085 / 665 |
| three_special_medium | 3,902 | 36,234 / 97,323 / 5,861 |
| five_special_small | 21 | 328 / 123 / 26 / 1,174 / 30 |
| five_special_medium | 275 | 277 / 8,515 / 4,238 / 597 / 658 |

例えばfive_special_smallの第4項目を外すと21→1,174、第3項目なら21→26。組合せを絞る程度が違うことは示すが、前者を削除すべきとは意味しない。five_special_mediumでも第1項目275→277、第2項目275→8,515で役割が違う。

Specificityは各CoreのRaw Lift首位を1候補ずつ選んだ診断であり、全候補を代表する標本ではない。保存されたfull率と各singleton率はすべて再現した。ただし首位のsupportはケース順に **2 / 20 / 2 / 2 / 1 / 3**。例えばfive_special_mediumの衣服候補 `vyshyvanka` は3/275=1.0909%に対しsingleton最大約0.00426%と増えるが、3投稿から強いinteractionや本人の有用性を確定できない。

singleton母集団はfull Coreを含み、互いに重なる。独立比較や因果効果の検証ではない。低共起は「相性が悪い」ことを示さない。現インターフェースはsingleton率のみで件数を返さないため、診断を理解するには将来singleton base/coも併記する余地がある。今回は仕様追加・scoreへの混入は行わない。

## 7. Performance監査

旧JSONの `ranking_overhead_ms` は **AND＋aggregation＋global lookup＋4スコアの候補構築**で、実際の `rank()` を含まない。1回の計測で、Core投稿cacheも一律warmではない。旧文書の表は初回runの数値、現JSONは再runの数値であり少し異なる。base275の約1.43秒を「rankingソートの追加負荷」と解釈してはいけない。

監査で明示warm-up後3回計測しmedianを分離した。同一process、OS cacheの制御なし、mmapおよびlogical postings cacheを再利用。独立した各計測のmedianを合算してend-to-end latencyとは呼ばない。値はms。

| 条件 | 候補構築（AND/集計/全score込み） | Rate sort | Lift sort | Wilson sort | Shrunk sort | Drop-one全項目 | specificity 1候補 |
|---|---:|---:|---:|---:|---:|---:|---:|
| two_special_small | 10.546 | 0.263 | 0.179 | 0.240 | 0.173 | 0.507 | 0.608 |
| two_special_medium | 182.586 | 2.776 | 2.056 | 2.739 | 2.052 | 4.123 | 6.432 |
| three_special_small | 12.129 | 0.330 | 0.230 | 0.442 | 0.234 | 5.632 | 4.685 |
| three_special_medium | 99.553 | 2.160 | 1.471 | 2.079 | 1.473 | 13.754 | 11.046 |
| five_special_small | 11.217 | 0.091 | 0.074 | 0.091 | 0.109 | 19.217 | 11.448 |
| five_special_medium | 33.504 | 0.604 | 0.425 | 0.691 | 0.414 | 87.416 | 49.432 |

ソート自体はこの6条件で0.074～2.776ms。候補構築と診断負荷は別に残る。スコア算出のみの時間は未分離。大base、cold起動、全候補specificity、Forge同居RAMを承認する計測ではない。Candidate Aggregationの大規模最適化は今回行っていない。

## 8. 各方式の採否と未解決判断

1. **Conditional Rate：default候補として推奨、最終採用保留。** 説明しやすく、6条件では少数supportの上位占有が少なく、共通要素を安定して選べる。ただしgeneric/冗長候補の占有と本人の有用性は未解決。base=1で信頼性を保証しない。
2. **Raw Lift：default不採用推奨。** 極小supportへの過敏性が大きい。raw factとして保持して頻出率と併読する価値はあるが、secondary viewの採用まで要求されるかは本人評価が必要。
3. **Wilson：別defaultとして選ぶ根拠なし。** 率系と同順位で、この用途の候補間信頼性を改善したとは言えない。比較用計算は保持する。
4. **Shrunk Lift：default/secondaryとも採用推奨しない。** 既存の順位はRaw Liftと同じで、補正済みだから信頼できるという誤解を招く。共通prior増加による順位修正案は出さない。

新方式や複合sort、threshold、blacklistは追加しない。個人用ツールであることを重視し、本人に最小の選択評価を求めることがCを解除する条件となる。数学的に4つを比較したという形式だけでFINAL defaultを確定しない。

## 9. Stage 7へ引き継ぐ表示要件（実装なし）

- CoreのSpecial ID・原語・組合せを主表示に保ち、statistics canonicalは統計取得の対応として扱う。
- 共通のbase_countを明示し、各候補に **co_count/base_count、conditional_rate** を表示。
- 詳細で **runtime_global_count、total_posts、global_rate、raw_lift、statistics snapshot** を見せる。
- current_post_countを出す場合は「現在辞書の使用数」とsnapshotを別表示。計算分母に混ぜない。
- 補正scoreをraw率や倍率に見せかけない。baseが小さい場合はその事実を示す。raw 1/1=100%を改変しない。
- Drop-oneとspecificityは診断として独立表示し、候補やCoreの自動追加・削除に使わない。
- `RecommendationCandidate`自体にはsnapshot欄がない。現engineは同じoverlayから計算するが、将来の受渡し・保存時には結果とsnapshotの対応を維持する必要がある。

## 10. 本人確認用の代表条件と候補

既存CSVのcase列で抽出し、Conditional RateとRaw Liftのtop20を比較する。同順位のWilson/Shrunkを再度評価する必要はない。以下は既存結果からの非露骨な比較例であり、追加推奨の確定ではない。全20件とCore語はCSV/JSONで参照できる。

| 条件 | 率系の確認例（co_count） | Lift系の確認例（co_count） | 本人に確認したい点 |
|---|---|---|---|
| two_special_small | blush 69、solo_focus 30 | washboard 1、black_poncho 1 | 表情/構図を固定したいか、偶発的細部が邪魔か |
| two_special_medium | shirt 4,512、open_shirt 3,680、jacket 3,246 | open_wetsuit 14、jellyfish_hair_ornament 22 | 一般服装の補完と珍しい衣装のどちらが必要か |
| three_special_small | barefoot 48、smile 37、looking_at_viewer 35 | imminent_vomiting 2、eavesdropping 2 | 高liftでも意図と違う行為/状況を避けたいか |
| three_special_medium | blush 2,438、solo_focus 1,543 | the_loud_house_(style) 2 | 画風の偶発的上位化と汎用構図の価値 |
| five_special_small | sweat 10、teeth 10、thighhighs 10 | against_mirror 1、dance_studio 1 | base21で1投稿の構図/背景をどこまで参考にするか |
| five_special_medium | long_hair 193、smile 100、solo_focus 96 | vyshyvanka 3、ukrainian_clothes 3、towel_pull 2 | 衣服の特異性と高supportの共通要素のどちらが役立つか |

優先して本人が確認するのは two_special_medium、five_special_small、five_special_medium。各top20を「追加したい」「Coreから既に十分」「今回不要」に分ければ、安定な率系の冗長性が許容できるか、Liftを別表示する価値があるかを確認できる。この回答なしに本人の好みを推定して有用性を断言しない。

## 11. テスト・成果物・作業報告（8項目）

1. 変更した項目：監査文書、監査runner、監査結果を追加。旧Evaluationの数式/計測に関する結論は本書で訂正。
2. 変更しなかった項目：正本、Stage 5 index/overlay、recommendations.py、既存テスト、既存評価CSV/JSON、ranking parameter、default設定。Stage 7未着手。
3. 新規作成：`docs/decisions/RECOMMENDATION_RANKING_DECISION.md`、`tools/stage6_decision_audit.py`、`benchmarks/stage6/decision_audit.json`、`benchmarks/stage6/decision_audit_pytest.txt`。
4. バックアップ先：既存ファイルの上書きなしのため新規バックアップ不要。監査入力hashはdecision_audit.jsonに保存。
5. 実施したテスト：480行照合、実index再計算、Special対応確認、同順位の代数/有理数検証、split/診断再現、限定性能計測、full pytest。
6. テスト結果：監査6/6条件PASS、**73 passed in 8.25s**。既存Stage 6テストは4関数であり、全要求網羅を意味しない。Semanticと名付けたテストにも実Semantic入力はなく、snapshot混在やCoreTagSet経由の統合保証も追加監査の余地がある。
7. 未解決事項：本人の有用性評価、generic/冗長性、極小base、snapshot付き結果受渡し、より広い安定性・大base・RAM検証。共通priorを増やせば解決する問題ではない。
8. 次にChatGPTへ：本Decision、既存top20 CSV/評価JSON、本監査JSON/pytest記録。**C判定で停止。Stage 7には進まない。**
