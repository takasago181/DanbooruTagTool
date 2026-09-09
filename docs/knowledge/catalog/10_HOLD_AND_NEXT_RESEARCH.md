# 10 — HOLD / Next Research

## HOLDの意味

HOLDは「知らない」ではなく、**根拠不足を正しく残している状態**。

ネット上の体感・旧モデル知識・別family結果で埋めない。

---

## 最優先 — WAI Illustrious v17 実画像テスト

現在のユーザー実環境を最初の実証レーンにする。

baseline:
- Forge Neo
- WAI Illustrious v17
- Euler a
- 25 steps
- CFG 5
- portrait 1024x1344 first candidate
- fixed paired seeds
- Hires OFF
- ADetailer OFF
- LoRA OFF
- Control/regional OFF

原本: `research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md`

### WAI17で未解決
1. canonical vs Alias activation
2. rare Special exposure
3. broad+specific benefit/harm
4. actor-target/body-site relation ceiling
5. restraint topology
6. machine functional relation
7. tentacle source/ownership
8. exact count / simultaneous Special ceiling
9. visibility supportの実効差
10. unusual anatomy/count Negative ON/OFF
11. LoRA x Special/support interaction
12. Prompt-only -> assisted-control escalation threshold

---

## evaluator関連HOLD

Dictionary finalization後:
- WD EVA02 v3
- Kagami-24k
- CL Tagger v2

のSpecial2788全件coverage比較。

未確定:
- Core/Extended/Alias/Semanticごとの実coverage
- Alias canonical-target mapping時のscore設計
- relation classの自動化可能範囲
- OOD handling
- REVIEWをどこまで減らせるか

---

## NoobAI HOLD

- current Danbooru canonical vs historical/e621 trigger
- actor/body-site relation
- visibility/camera support
- hard count ceiling
- anatomy Negative effects
- EPS/V-Pred差

WAI17のlocal evidenceが安定するまでは優先度を下げる。

---

## Anima HOLD

- tag-only vs concise hybrid relation delta
- exact wording/length
- hard relation success rate
- multi-character ceiling
- profile(Base/Aesthetic/Turbo)差
- unusual anatomy x Negative

---

## 実験で知識へ昇格させる条件

### local practical rule
exact contextを固定してrepeatable benefit/harmが見えること。

保存するcontext:
- checkpoint/version/hash
- target Special
- actual Prompt/Negative
- seed/settings
- LoRA/control/postprocess state
- evaluator
- result + uncertainty

### general rule
複数の代表caseと必要なmodel scopeを跨ぐE3 evidenceが必要。

---

## 今は低優先

- sampler微差の網羅比較
- aesthetic微調整だけの研究
- unrelated model family
- runtime LLM案
- large custom evaluator platformの先行実装

現在目的に直接効かない限り後回し。

---

## 研究停止条件

Prompt supportを無限に追加しない。

- semantic nucleus維持
- functional support roleを一通り試す
- repeatable benefitがない
- conflictだけ増える

なら、Prompt-only ceilingとしてHOLD/assisted-controlへ移す。

## 原本

- `GENERATION_KNOWLEDGE_INDEX.md`
- `KNOWLEDGE_REASSESSMENT_20260909.md`
- `research/BATCH_C_EVIDENCE_RELIABILITY_20260909.md`
- `research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md`