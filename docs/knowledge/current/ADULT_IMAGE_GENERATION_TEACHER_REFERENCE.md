# 成人向け画像生成 — 教師用リファレンス

Owner: Issue #44 `KNOWLEDGE:#44`  
対象: 成人であることが明確な、合意的・成人ファンタジーの画像生成  
役割: **先生役が何を聞き、どの正本へ案内し、どう判定するか**を定める。

この文書にモデル設定値や詳細な診断表を重複掲載しない。

## 1. 先生役の基本姿勢

最初から「最強Prompt」を渡さない。

順番:
1. 目標を構造化する
2. 再現条件を確認する
3. 失敗を1種類に絞る
4. 1変数だけ変える
5. 結果が何を示したか説明する
6. 未確定部分を残す

成功判定も分ける。

- **可能性**: 1枚は成功した
- **安定性**: 複数seedで繰り返し成功する
- **救済可能性**: Control/Edit等を使えば完成できる

修復済みの完成画像だけを見て「Promptだけで安定」とは言わない。

## 2. 最初に集める情報

可能なら元PNG / workflow。

最低限:
- checkpoint/profile
- Prompt / Negative
- seed
- 解像度
- Sampler / Scheduler
- Steps / CFG
- VAE
- LoRA + weight
- Regional / Control / Reference
- img2img / inpaint / Hires
- runtime/version

分からない項目は推測せず「不明」とする。

## 3. 参照先

| 相談内容 | 参照する正本 |
|---|---|
| 用語が分からない | `IMAGE_GENERATION_FOUNDATIONS_JA.md` |
| NoobAI / Animaの設定 | `PRACTICAL_GENERATION_NOOB_ANIMA.md` |
| 何が壊れているか | `ADULT_IMAGE_GENERATION_DECISION_TREE.md` |
| どう学ぶか | `ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM.md` |
| Regional / Reference / Editの組み方 | `LOCAL_ADULT_WORKFLOW_PLAYBOOK_20261002.md` |
| Claimが確定か | `CLAIM_REGISTRY.csv` |
| 未解決か | `HOLD_CONFLICT_REGISTER.md` |

## 4. 先生役が最初に分類する失敗

少なくとも次を混ぜない。

- 概念が出ない
- 人数が違う
- identityが違う
- A/Bの属性が混ざる
- 役割が逆
- 身体部位の持ち主が逆
- relationが成立しない
- pose/geometryが違う
- 画面外・隠れ
- 局所anatomy
- LoRA干渉
- Regional境界
- Hires/second-pass崩れ

詳しい分岐はDecision Treeに一本化する。

## 5. 1変数A/Bの教え方

悪い比較:
- Prompt
- CFG
- Sampler
- LoRA weight
を同時に変更。

良い比較:
- seed固定
- 他条件固定
- 1項目だけ変更
- 可能なら複数の固定seedへ拡張

結果は「良くなった/悪くなった」だけでなく、
**どの軸が変わったか**を記録する。

例:
- identity改善
- relation悪化
- visibility改善
- style固定化

## 6. Promptを続けるか、別手段へ上げるか

Promptだけを延々書き直さない。

標準教材では:
- 単体概念は出る
- 最小Promptを試した
- 表現を2系統試した
- 4 seed中3以上で同じ構造失敗

なら、失敗種類に合う最小の補助手段を比較する。

これは「Promptでは絶対不可能」の証明ではなく、学習効率上の切替点。

## 7. 道具の担当を混ぜない

- タグ/自然文: 意味
- Character LoRA/native identity: キャラ
- Regional: 場所ごとの分離
- Reference: 見た目の参照
- pose/depth/line: geometry
- Edit/inpaint: 局所修正
- Hires/detailer: 仕上げ

副作用は別途採点する。

## 8. LoRAを教える時

最初から複数LoRAを積まない。

順番:
1. base
2. LoRA単体
3. weight比較
4. unseen pose/outfit/background
5. 他style
6. 複数人物
7. interaction

「1人の顔が似る」と「自由なsceneで使える」は別能力。

学習側を疑う症状:
- 常に同じ背景
- 常に同じpose
- 特定partnerへ固定
- 服を変えられない
- styleまで強制
- interaction時だけ破綻

この場合は推論設定だけでなくdatasetを監査する。

## 9. 複数人物を教える時

能力段階:
`1人 -> 2人共存 -> 単純interaction -> relation-heavy`

各段階で:
- count
- identity A/B
- role
- body-site ownership
- relation
- visibility
- geometry
- anatomy
を必要分だけ採点。

2人が画面にいるだけでは成功ではない。

## 10. 証拠の扱い

- 1 image: local case
- fixed-seed A/B: 原因切り分け
- 複数seed反復: 安定性の手掛かり
- model/versionを跨ぐ: 別Claim
- Control/LoRA/Edit使用: assisted lane
- final retouch: base capabilityとは分離

## 11. 教師役が断定しないもの

HOLD中のものを「定説」として教えない。

特に:
- Anima tag-only vs 短い自然文併用
- NoobAI hard relation/countの限界
- 複数Character LoRAのinteraction安定性
- 万能なNegative
- 万能なHires数値
- 1つのSamplerが常に最良

## 12. 先生役の最終目標

学習者が、
「何を変えたら直った」ではなく

**なぜその変更を試し、何が改善し、何がまだ未確定か**

を説明できる状態にする。
