# Batch D — Runtime Prompt Processing, Reproducibility and Compositional Evaluation

Status: `FOCUSED_ENRICHMENT_COMPLETE / CLAIMS_REGISTERED`

Date: 2026-09-10  
Owner: Issue #44 `KNOWLEDGE:#44`

## 1. 目的

教科書化の前段として、既存KNOWLEDGEを「DanbooruTagToolの実運用に必要な知識が足りているか」で点検した。

既存資産は次の領域が比較的強い。

- Danbooru canonical / Alias / implication の意味分離
- Special / Support の分離
- actor-target / body-site / topology / count を含むbinding分解
- WAI / Illustrious / NoobAI / Anima のmodel-family差
- unary taggerをrelation ground truthにしない評価境界
- 1 seedと信頼性を分けるEvidence ladder

一方、次の4点は教科書・PROMPT設計・Stage10評価のすべてに関係するのに、独立したcurrent Claimとして弱かった。

1. Prompt文字列がruntimeでどのように前処理されるか
2. A1111由来の挙動をForge Neoへどこまで持ち込めるか
3. Seed固定と完全再現性の違い
4. 複合生成を一括スコアではなく原子的条件へ分解して評価する外部研究根拠

本調査はこの4点だけを補強する。新しい生成最適化ルールやStage10 verdictは作らない。

---

## 2. Finding A — Prompt文字列とモデル入力は同一ではない

### 確認できたこと

AUTOMATIC1111 WebUIの公式Wikiでは、長いPromptを75 token単位のchunkへ分け、それぞれをCLIPで処理した後に連結する挙動が説明されている。また、大文字の `BREAK` は現在のchunkをpaddingで埋め、後続テキストを新しいchunkから開始させるruntime機能として説明されている。

同じ公式Wikiはattention/emphasis構文も説明している。

- `(word)` : attentionを増加
- `[word]` : attentionを減少
- `(word:1.5)` : 数値weightを指定

したがって、DanbooruTagToolで扱う次の3層は分離する必要がある。

1. **Semantic layer** — tagが何を意味するか
2. **Prompt surface layer** — 実際に出力する文字列・タグ列
3. **Runtime preprocessing layer** — chunk、BREAK、weight等でconditioningへ渡す前にruntimeが行う処理

### 重要な境界

`BREAK` はDanbooru tagではない。canonical / Alias / implicationを変えるものでもない。

また、A1111に `BREAK` が存在することから、**「BREAKを入れるとWAI17のbindingが改善する」ことは導けない**。その効果はmodel/runtime/version/Promptに依存する生成効果であり、必要ならcontrolled testで別に検証する。

### Project relevance

Promptが長いときはraw tag数だけでなく、runtime上のtoken/chunk配置が実験identityの一部になり得る。ただし、既存の `K-PROMPT-002`（Prompt難度はraw lengthだけでは決まらない）は維持する。75-token境界を越えたこと自体を「悪いPrompt」と判定してはいけない。

**Registered Claim:** `K-TOOL-006`

---

## 3. Finding B — Forge Neoへの継承は「候補上流」と「ローカル実体」を分ける

2026-09-10に確認した `Haoming02/sd-webui-forge-classic` の `neo` branch READMEは、original WebUIをGradio 4ベースで再実装し、dynamic UI依存を除く多くのbase featureを維持する方針を記載している。

これはA1111由来のruntime仕様をForge Neo調査の出発点にする根拠にはなる。しかし、DanbooruTagToolで現在使っているローカルForge Neoについては、KNOWLEDGE側でremote/commitがまだpinされていない。

さらに `VERSION_FRESHNESS_LEDGER.csv` が既に記録している通り、Forge Neoという名前で複数のfork/repositoryが存在し得るため、次を分離する。

- inspected upstream/candidate repositoryの説明
- userのlocal installationのremote
- local commit/hash
- local config / parser behavior

よって、**A1111の仕様をそのままローカルForge Neoの確定事実として扱わない**。

Stage10等のpromotion-critical evidenceでchunk/BREAK/weight処理が結果解釈に関係するなら、local remote + commit + relevant settingを先にpinする。

**Registered Claim:** `K-TOOL-007`

---

## 4. Finding C — Seed固定だけでは「完全再現」にならない

Hugging Face DiffusersのReproducibility documentationは、diffusion生成のrandomnessを制御するためにseed / Generatorを使う一方、PyTorch release、commit、platform、CPU/GPUなどを跨いだ完全再現が保証されないことを明示している。deterministic algorithmを使える場合でも、環境差は再現性identityの一部である。

DanbooruTagToolでは既存の次の知識がある。

- `K-EVID-001`: 1 seedはcase/counterexampleでありreliability estimateではない
- `K-EVID-002`: E0–E3で証拠強度を分ける

今回追加する知識は別軸である。

- **multi-seed** = 統計的な繰り返し・一般化の問題
- **environment reproducibility** = 同じ条件を再生したつもりでもexecution environment差で完全一致しない問題

したがって、controlled evidenceではseedだけでなく、少なくとも関係する範囲で次を保持する。

- checkpoint / hash
- runtime / commit
- sampler / scheduler
- steps / CFG
- resolution
- Positive / Negative Prompt
- loaded LoRA / weight
- Hires / ADetailer / Control / regional等のON/OFF
- seed
- promotion-criticalな場合は再現性へ影響し得る主要runtime/environment identity

この原則は「毎回すべてのGPU driver差を記録しなければ無効」という意味ではない。**結論の強さに応じて、再現性へ影響する変数を十分にpinする**という意味である。

**Registered Claim:** `K-EVID-004`

---

## 5. Finding D — 複合条件は原子的predicateへ分解して評価する

### GenEval

GenEvalは、FIDやCLIPScoreのようなholistic metricだけではfine-grained/instance-level analysisに不向きとして、object co-occurrence、position、count、color等へ分けたobject-focused evaluationを提案している。

### T2I-CompBench

T2I-CompBenchはcompositional text-to-image generationを、attribute binding、object relationships、complex compositionsに分け、さらにcolor/shape/texture binding、spatial relationships、non-spatial relationships等を評価する。

### DanbooruTagToolへの意味

これらはWAI17やSpecial2788を直接評価した研究ではない。しかし方法論として、既存のproject知識を外部研究で補強する。

たとえば難しいSpecialを、単に「Promptと画像が似ているか」という1スコアだけで判定せず、必要に応じて次へ分解する。

- required object / actor presence
- exact count
- body-site
- actor-target ownership
- source-destination
- spatial / non-spatial relation
- topology / connectivity
- simultaneous concept retention

これは既存の `K-EVAL-005`（unary taggerをrelation等のsole ground truthにしない）および `K-BIND-001`（presence != relation）と整合する。

**Registered Claim:** `K-EVAL-006`

---

## 6. 今回「確定知識」にしなかったもの

以下は調査中に考えられるが、今回のsourceだけではgeneration effectまで証明できないため昇格しない。

- `BREAK` を入れるとWAI17のbindingが改善する
- chunk先頭へSpecialを置けば必ず強くなる
- 75 token以内ならPrompt競合が起こらない
- token数が少ないほど生成成功率が上がる
- GenEval / T2I-CompBenchの自動metricをそのままSpecial2788の最終judgeにできる
- 同じseedなら異なるruntime/versionでも画像が完全一致する

必要なら将来、model/versionをpinしたcontrolled experimentとして扱う。

---

## 7. 教科書への配置

将来の日本語教科書では次の位置に入れる。

- **Prompt基礎編**: 「入力した文字列はそのままモデルへ届くわけではない」
- **Runtime編**: token / chunk / BREAK / attention weight
- **実験編**: Seed固定と再現性の違い
- **評価編**: compositional targetをpredicateへ分解する理由
- **注意事項**: A1111仕様、Forge Neo候補上流、ローカル実体、model generation effectを混同しない

人間向け説明は日本語を主にし、Claim ID / STATUS / SOURCE_CLASS / SCOPEなど機械管理ラベルは固定英語を維持する。

---

## 8. Sources

### OFFICIAL_RUNTIME

1. AUTOMATIC1111 Stable Diffusion WebUI Wiki — Features  
   https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features  
   Checked: 2026-09-10  
   Use: long-prompt chunking, `BREAK`, attention/emphasis syntax.

2. Hugging Face Diffusers — Reproducibility  
   https://huggingface.co/docs/diffusers/main/using-diffusers/reusing_seeds  
   Checked: 2026-09-10  
   Use: seed/Generator, deterministic controls, cross-release/platform reproducibility limits.

3. Haoming02 `sd-webui-forge-classic`, branch `neo` — README  
   https://github.com/Haoming02/sd-webui-forge-classic/tree/neo  
   Checked: 2026-09-10  
   Use: inspected candidate upstream's relationship to original WebUI.  
   Boundary: **not proof of the user's local Forge Neo remote/commit.**

### RESEARCH

4. Ghosh, Hajishirzi, Schmidt — GenEval: An Object-Focused Framework for Evaluating Text-to-Image Alignment  
   https://arxiv.org/abs/2310.11513  
   Use: object-focused compositional evaluation; presence/count/position/color; holistic-metric limitation.

5. Huang et al. — T2I-CompBench: A Comprehensive Benchmark for Open-world Compositional Text-to-image Generation  
   https://arxiv.org/abs/2307.06350  
   Use: attribute binding, spatial/non-spatial object relations, complex composition evaluation.

---

## 9. Change boundary

This enrichment does **not**:

- modify `data/**`
- change Special2788 semantic identity
- change Issue #32 verdicts
- authorize Stage10 production A/B
- change DEV/PROMPT/AUDIT ownership
- merge any branch to `main`
- promote Issue #49 or UI-JA assets
