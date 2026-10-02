# KNOWLEDGE クイックリファレンス

Owner: Issue #44 `KNOWLEDGE:#44`  
役割: **入口と索引だけ**  
判定の正本: `CLAIM_REGISTRY.csv`

## 現在地

- v1の目的: **理解 -> 発見 -> 選択 -> 出力**
- 生成学習の第一レーン: **NoobAI XL 1.1 EPS + Forge Neo**
- Anima: 複数人物・関係性・参照/Regional系を含む比較・補助レーン
- WAI Illustrious v17: 比較・履歴レーン
- NoobAI V-Pred: EPSとは別profileとして扱う

## 何を知りたい時にどこを見るか

| 質問 | 読むファイル |
|---|---|
| seed / VAE / Sampler / CFGとは何か | `IMAGE_GENERATION_FOUNDATIONS_JA.md` |
| NoobAI / Animaの設定・違い | `PRACTICAL_GENERATION_NOOB_ANIMA.md` |
| 成人向け生成が崩れた | `ADULT_IMAGE_GENERATION_DECISION_TREE.md` |
| 成人向け生成をゼロから学ぶ | `ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM.md` |
| 先生役としてどう教えるか | `ADULT_IMAGE_GENERATION_TEACHER_REFERENCE.md` |
| Regional / Reference / Edit等をどう組むか | `LOCAL_ADULT_WORKFLOW_PLAYBOOK_20261002.md` |
| 未解決事項 | `HOLD_CONFLICT_REGISTER.md` |
| モデルやruntimeの鮮度 | `VERSION_FRESHNESS_LEDGER.csv` |
| Claimの採用状態 | `CLAIM_REGISTRY.csv` |
| 根拠原文 | `../research/*` と `../GENERATION_KNOWLEDGE_SOURCES.md` |

## 現在の重要原則

- **存在した**ことと、役割・接触・部位・人数まで正しいことは別。
- 1枚成功は「可能性」の証拠で、安定性の証拠ではない。
- シード（seed）は構図番号ではない。
- ステップ数（Steps）は単純な画質スコアではない。
- CFGはモデルの理解力を増やす値ではない。
- ネガティブプロンプト（Negative）は生成後の消しゴムではない。
- LoRA成功、Regional/Control成功、部分修正後の成功を、Promptだけの能力と混ぜない。
- モデルfamily/version/profileを跨いで設定や結論を無断転用しない。
- current Danbooruの投稿数を、そのままモデルの学習量・認識率とみなさない。
- 失敗時はタグを増やす前に、**何が壊れているか分類する**。

## 成人向け実践の共通診断軸

必要なものだけ採点する。

- 人数
- キャラ同一性
- 役割
- 属性・身体部位の所有者
- 接触・関係
- 前後・重なり
- 可視性
- 構図
- 局所解剖
- LoRA/Reference/Controlの漏れ

詳しい分岐はDecision Treeへ。

## 現在HOLDの代表例

- NoobAIの難しい役割・部位・正確な人数の安定限界
- NoobAI EPSとV-Predの実用差
- Animaの「タグのみ」と「短い自然文併用」の普遍的な優劣
- Anima各profileの難しいsceneでの差
- Character LoRAを複数人物・強いinteractionへ持ち込んだ時の安定性
- PromptだけからRegional/Reference等へ切り替える最適な閾値
- evaluator/taggerの最終coverage

HOLDは「何も分からない」ではなく、**方向性は分かるが普遍的な結論をまだ固定しない**状態。

## 再現性の最低セット

- checkpoint/profile
- Prompt / Negative
- seed
- 幅・高さ
- Sampler / Scheduler
- Steps / CFG
- VAE
- LoRA + weight
- Regional / Control / Reference
- img2img / inpaint / Hires
- runtime/version

元PNGまたはworkflowを残す。

## 現在の整理状態

2026-10-02の棚卸しで:
- Claim ID重複: 0
- Source ID重複: 修復済み、0
- 旧current/handoff: historical化
- 研究Batchのprefix衝突: full filenameを正式identityとして扱う
- current説明文書: 役割分離・日本語-firstへ移行

整理監査:
`KNOWLEDGE_HYGIENE_AUDIT_20261002.md`
