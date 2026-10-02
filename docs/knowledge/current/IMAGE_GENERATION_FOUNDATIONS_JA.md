# 画像生成 基礎教科書 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
役割: モデル別レシピより前に理解する**共通の基礎原理**  
現在判定: `CLAIM_REGISTRY.csv`

## 表記ルール

説明は日本語を主にし、実際のUIや資料と照合しやすいように英語原語を括弧で補助する。

例:
- 潜在表現（latent）
- 条件付け（conditioning）
- ノイズ除去（denoising）
- 文章エンコーダー（Text Encoder）

## 1. 画像ができるまで

大まかな流れ:

`プロンプト（Prompt）`  
→ `文字を分割するトークナイザー（Tokenizer）`  
→ `文章を数値表現へ変える文章エンコーダー（Text Encoder）`  
→ `生成条件（conditioning）`

同時に:

`シード（seed）`  
→ `初期ノイズ / 潜在表現（latent）`

そして:

`生成条件 + ノイズを含む潜在表現`  
→ `UNet / DiTが各ステップで修正方向を予測`  
→ `サンプラー / スケジューラが次の状態を計算`  
→ `反復`  
→ `完成した潜在表現`  
→ `VAEが画像へ復号`  
→ `完成画像`

モデルfamilyによって内部構成は違うが、設定項目を考える時の土台として使える。

## 2. 最低限の用語

| 用語 | 役割 |
|---|---|
| プロンプト（Prompt） | 作りたい内容をモデルへ伝える |
| トークナイザー（Tokenizer） | 文字列をモデルが扱う単位へ分ける |
| 文章エンコーダー（Text Encoder） | 文字情報を数値的な生成条件へ変える |
| 条件付け（conditioning） | 生成をどちらへ進めるか誘導する情報 |
| シード（seed） | 擬似乱数生成器の初期値 |
| ノイズ（noise） | 生成開始点などで使うランダムな数値 |
| 潜在表現（latent） | 画像を圧縮して扱う内部表現 |
| UNet / DiT | 各ステップで修正方向を予測する中心モデル |
| サンプラー（Sampler） | 予測を使って次の状態へ進む計算方法 |
| スケジューラ（Scheduler） | ノイズ量・時間刻みの進め方を決める仕組み |
| ステップ数（Steps） | ノイズ除去の更新回数 |
| CFG | プロンプト条件へどれだけ強く寄せるか |
| ネガティブプロンプト（Negative） | 避けたい方向も生成条件として与える |
| VAE | 画像と潜在表現を相互変換する |
| LoRA | 基本モデルへ追加する小型の学習差分 |
| ControlNet | ポーズ・奥行き・輪郭などの構造条件を追加する |
| 画像から画像生成（img2img） | 元画像へノイズを加えて描き直す |
| 部分修正（inpaint） | 指定範囲を中心に再生成する |
| 高解像度化（Hires） | 基本生成後の高解像度化・再生成工程 |
| VRAM | GPU上でモデルや計算途中のデータを保持するメモリ |

## 3. シードは「構図番号」ではない

シードは乱数生成の初期値。

同じシードで比較しやすいのは、他の実行条件を揃えているから。

結果が変わり得る要素:
- モデル
- VAE
- Prompt / Negative
- Sampler / Scheduler
- 解像度
- LoRA / Control
- runtimeや実装

使い方:
- 原因比較: シード固定
- 安定性確認: 固定した複数シードで反復

## 4. ステップ数は画質点数ではない

ステップ数は更新回数。

多くすると計算時間は増えるが、画質が比例して上がるわけではない。

- モデル
- Sampler
- Scheduler
- Turbo / 蒸留型かどうか

で適切な範囲が変わる。

まずモデル作者の基準値を使う。

## 5. サンプラーとスケジューラ

Forge系UIでは別項目として見えることが多い。

- **サンプラー**: 次の状態へどう進むか
- **スケジューラ**: 各ステップをどのノイズ量へ配置するか

ただしライブラリによっては両方をまとめてSchedulerと呼ぶ。

名称より、**更新方法**と**ノイズ量の進め方**を分けて理解する。

## 6. CFG

CFGは、プロンプト条件へ寄せる強さ。

高くすればモデルの理解力が上がるわけではない。

高過ぎると:
- 色やコントラストの崩れ
- 多様性低下
- 構図変化
- 品質低下
などが起こり得る。

## 7. ネガティブプロンプト

Negativeは生成後の消しゴムではない。

生成中の条件として効くため、意図した内容まで弱めることがある。

特に:
- 通常と違う人数
- 通常と違う身体構造
- 成人向けrating
を扱う時は、広いNegativeを中立と思わない。

## 8. 解像度と縦横比

解像度は見た目だけでなく:
- 構図
- 画面に入る身体範囲
- 人物間距離
- 計算量
- VRAM
へ影響する。

モデル推奨の画素量・縦横比から始める。

## 9. 画像から画像生成（img2img）

流れ:

`元画像 -> VAEで潜在表現化 -> ノイズ追加 -> 再生成 -> 画像化`

変化量（denoise / strength）が低い:
元画像を強く残す。

高い:
より自由に描き直す。

「保持」「画風変更」「大きく描き直す」のどれが目的か先に決める。

## 10. 部分修正（inpaint）

マスクした場所を中心に再生成する。

見るもの:
- マスク範囲
- 境界のぼかし
- 周辺をどこまで含めるか
- 変化量
- 周囲とのつながり

全体の人数・役割・構図が壊れているのに、小さいmaskだけで無理に直さない。

## 11. ControlNet

Promptが「何を描くか」なら、Controlは「どんな構造にするか」を補助する。

例:
- ポーズ（pose）: 骨格
- 奥行き（depth）: 前後関係
- 線画・輪郭（line / edge）: 外形や配置

Controlには:
- 強さ
- どの生成区間で効かせるか
がある。

元のControl画像に不要な髪・服・小物が残っていると、それも移ることがある。

## 12. LoRA

LoRAは基本モデル全部を入れ替えるものではなく、追加の学習差分。

扱う時は:
1. base
2. LoRA 1個
3. weight比較
4. 2個目
5. 組み合わせ

最初から多数積むと、どれが原因か分からなくなる。

学習側ではrankやalphaだけで品質を決めず、dataset・caption・学習時間等も見る。

## 13. VRAMと軽量化

VRAM不足時に確認する順:
1. 解像度
2. batch size
3. モデル規模
4. Control / adapter数
5. 数値精度（fp16 / bf16等）
6. attention最適化
7. VAE分割処理
8. CPUへの退避（offload）
9. 量子化（quantization）

VRAMを減らす方法は、速度・互換性・再現性へ影響し得る。

## 14. 保存する情報

最低限:
- checkpoint / hash
- VAE
- Prompt / Negative
- seed
- 幅・高さ
- Sampler / Scheduler
- Steps / CFG
- LoRA + weight
- Control / Reference
- img2img / inpaint / Hires
- runtime/version

元PNGやworkflowを残す。

## 15. safetensors / Clip Skip / Textual Inversion

### safetensors
モデルfamily名ではなく、tensor保存形式。
同じ拡張子でもcheckpoint、LoRA、VAE等があり得る。

### Clip Skip
CLIP系文章エンコーダーの、どの層の出力を使うか変える設定。
CFGやPrompt weightとは別。

### Textual Inversion
新しいtoken embeddingを学習するpersonalization手法。
LoRAとは仕組みが違う。

## 16. 基礎PASS判定

次を日本語で説明できれば最低基礎PASS:

- 潜在表現
- seed
- VAE
- Tokenizer / Text Encoder
- Sampler / Scheduler
- Steps
- CFG
- Negative
- 解像度
- img2imgの変化量
- inpaint mask
- Controlの強さ
- LoRA
- VRAM / precision / offload

詳細根拠:
- `../research/BATCH_AZ_GENERATION_FOUNDATIONS_PIPELINE_20261002.md`
- `../research/BATCH_BA_SAMPLING_GUIDANCE_FOUNDATIONS_20261002.md`
- `../research/BATCH_BB_EDITING_CONTROL_MEMORY_FOUNDATIONS_20261002.md`
- `../research/BATCH_BC_OUTPUT_METADATA_AUXILIARY_FOUNDATIONS_20261002.md`
