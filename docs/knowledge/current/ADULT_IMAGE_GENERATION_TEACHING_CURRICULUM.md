# 成人向け画像生成 — 学習カリキュラム

Owner: Issue #44 `KNOWLEDGE:#44`  
対象: 成人であることが明確な、合意的・成人ファンタジーの二次元ローカル生成  
役割: **学ぶ順番・演習・合格条件だけを定める**。

モデル固有設定は `PRACTICAL_GENERATION_NOOB_ANIMA.md`、失敗診断は `ADULT_IMAGE_GENERATION_DECISION_TREE.md` を見る。

## レベル0 — 再現できる

学ぶ:
- モデル / checkpoint / profile
- シード（seed）
- 解像度
- サンプラー / スケジューラ
- ステップ数 / CFG
- Prompt / Negative
- metadata保存

演習:
同じ条件をmetadataから再現し、1項目だけ変える。

合格:
「何を固定し、何を変えたか」を説明できる。

## レベル1 — 基礎原理を説明できる

学ぶ:
- 潜在表現（latent）
- VAE
- トークナイザー（Tokenizer）
- 文章エンコーダー（Text Encoder）
- seedと初期ノイズ
- Sampler / Scheduler
- CFG
- Negative

教材:
`IMAGE_GENERATION_FOUNDATIONS_JA.md`

合格:
`Prompt -> 条件付け -> ノイズ除去 -> VAE -> 画像`
を日本語で説明できる。

## レベル2 — 単純な1人sceneを作る

学ぶ:
- 最小Prompt
- カメラ / framing
- seed差
- style / backgroundを後から足す

合格:
「概念失敗」と「構図の個体差」を分けられる。

## レベル3 — キャラ同一性（identity）

学ぶ:
- モデルが元から知るキャラ
- Character LoRA
- Reference
- identity featureの採点

演習:
同じキャラで:
- 別pose
- 別背景
- 別衣装
- 別style

合格:
顔が似るだけでなく、identity以外を変更できる。

## レベル4 — 画風（style）

学ぶ:
- native artist / style
- Style LoRA
- Reference style
- 内容の漏れ（content leakage）

合格:
画風を保ちつつ、訓練例と違う内容・構図へ変更できる。

## レベル5 — 2人を分離する

順番:
1. 2人、相互作用なし
2. 相対位置
3. 単純な接触
4. 重なり・遮蔽あり

採点:
- 人数
- identity A
- identity B
- 属性の持ち主
- 可視性

合格:
「2人がいる」と「2人が正しく分離されている」を区別できる。

## レベル6 — 関係性（relation）

学ぶ:
- 行為者 / 対象（actor / target）
- 役割
- 身体部位の所有者
- 接触
- 起点 / 到達先
- 前後関係
- 可視性

合格:
relation失敗、geometry失敗、visibility失敗を分けられる。

## レベル7 — LoRA干渉

演習:
`base -> A -> B -> A+B`

見る:
- identity
- outfit
- style
- pose
- relation
- background

合格:
どの追加時点から崩れたか説明できる。

## レベル8 — Controlを役割別に使う

学ぶ:
- Regional = 場所ごとの分離
- Reference = 見た目
- pose = 骨格
- depth = 前後
- line / edge = 輪郭
- inpaint = 局所修正

合格:
「この道具を使う理由」を説明できる。

## レベル9 — 部分修正と仕上げ

学ぶ:
- 画像から画像生成（img2img）
- 部分修正（inpaint）
- detailer
- Hires
- 通常拡大と再生成型upscaleの違い

合格:
仕上げで崩れた時にbase Promptの失敗へ戻さない。

## レベル10 — LoRA学習

学ぶ:
- datasetの範囲
- caption
- 不要要素
- rank / alpha
- learning rate
- step / epoch
- 途中checkpoint評価

評価:
- identityの再現
- 編集自由度
- 未学習pose / outfit / background
- style leakage
- 複数人物共存
- interaction

合格:
lossだけでなく画像結果からdataset/学習設定を診断できる。

## レベル11 — 実践sceneを統合する

`意味構造 -> identity -> geometry -> 必要なら分離 -> relation再確認 -> 局所修正 -> 仕上げ -> 最終監査`

合格:
各手段が何を担当しているか説明できる。

## レベル12 — 自力診断

未知の失敗に対して:
1. 再現条件固定
2. 主症状を1つ選ぶ
3. 最小Prompt
4. 1変数A/B
5. 複数seed
6. 必要なら最小Control
7. 結果記録

合格:
先生から完成レシピをもらわず、次の実験を自分で設計できる。

## 証拠区分

- 1枚成功 = 可能性
- 複数seed = 安定性
- 補助機能で救済 = 救済可能性
- model/version変更 = 別条件

## 読む順番

1. `IMAGE_GENERATION_FOUNDATIONS_JA.md`
2. `PRACTICAL_GENERATION_NOOB_ANIMA.md`
3. `ADULT_IMAGE_GENERATION_DECISION_TREE.md`
4. このカリキュラム
5. 必要な時だけ `LOCAL_ADULT_WORKFLOW_PLAYBOOK_20261002.md`
