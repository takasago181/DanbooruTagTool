# 知識班 棚卸し・矛盾・重複・鮮度監査 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
監査時HEAD: `d2577843020287b20ebfbe27fe48f95d7bf04fac`  
状態: `AUDIT_COMPLETE / CLEANUP_REQUIRED`

## 1. 結論

知識内容の中核、特に `CLAIM_REGISTRY.csv` の状態管理は健全。

一方で、2026-10-02の急速な知識追加によって、次の管理負債が発生している。

1. Source RegistryのID衝突
2. 旧current/handoffが現行復元経路に残っている
3. `current/` に古い監査・backlogが残っている
4. research batch識別子が重複している
5. current向け説明文書同士の内容重複が大きい
6. 新しい日本語-first説明ルールに既存current文書が追いついていない
7. 一部のhistorical文書名・役割表示が「current」に見え、現行目的と衝突し得る

現時点で、Claim Registryそのものに大規模な意味矛盾は検出していない。

---

## 2. 監査規模

`docs/knowledge` 直下と主要サブディレクトリ:

- root: 8 files / 約217 KB
- current: 21 files / 約354 KB
- catalog: 12 files / 約91 KB
- research: 87 files / 約811 KB
- automation: 1 file / 約2 KB

合計:
- 129 files
- 約1.47 MB

---

## 3. Claim Registry健全性

監査時:

- total: 323
- ACCEPTED: 208
- CANDIDATE: 95
- HOLD: 8
- HISTORICAL: 2
- REJECTED: 10
- ID重複: 0
- CSV列崩れ: 0

高類似Claimを機械比較した結果、目立つ1組は:

- `K-SEM-006`: current Danbooru post_countはmodel knowledgeの直接確率ではない — ACCEPTED
- `K-REJECT-003`: current Danbooru post_countがmodel knowledgeを直接予測する — REJECTED

これは矛盾ではなく、採用原則と明示的に棄却した旧仮説の対であり正常。

### HOLDとの照合

現在の主要HOLD:

- canonical / Alias / historical trigger response
- NoobAIのcamera/visibility、hard count、actor/body-site、Negative
- Anima tag-only vs concise hybrid
- WAI broad+specific
- WAI hard relation ceilings
- unusual anatomy/count Negative
- LoRA × Special/support
- evaluator final coverage

current guideを照合した結果、これらを明確に「解決済み」と誤記した箇所は検出しなかった。

ただし `PRACTICAL_GENERATION_NOOB_ANIMA.md` の
`Anima — hybrid/explicit-relation workhorse`
等は、HOLDより強く読める表現。
「Animaではhybridも比較候補」「tag-onlyとの優劣はHOLD」と併記した方が安全。

---

# 4. HIGH — Source Registry ID衝突

`GENERATION_KNOWLEDGE_SOURCES.md`:

- Source ID記載: 256件
- unique ID: 223件
- 衝突ID: **30件**
- 余分な重複出現: **33件**

これは同じURLの再利用ではなく、**同じSource IDへ別の出典を割り当てた衝突を含む**。

例:

### S-RESEARCH-019
1. DreamBench++
2. LyCORIS evaluation paper

### S-TOOL-011
1. CCIP
2. LyCORIS current repository

### S-TOOL-012
1. waifuc character dataset pipeline
2. Regional Prompter current Anima support
3. Forge Hires UI implementation

### S-COMM-068
1. Anima character-LoRA hyperparameter discussion
2. Anima fixed-seed 0/1/3 LoRA stack

同様の衝突が:
- S-RESEARCH-020..024
- S-COMM-068..082
- S-TOOL-011..016
- S-PRACTICAL-004..006
等に存在。

### 影響

現在のClaim Registryの `source/evidence` を確認した範囲では、
この30個の衝突IDを直接参照しているClaimは **0件**。

したがって現時点でClaim verdictが即座に別Sourceへ誤接続している証拠はない。

しかしSource Registryのstable IDとしては壊れている。
今後このIDをClaimへ使う前に修復必須。

### 修復方針

- 既存Source entryを削除しない
- 各衝突entryへ一意な新IDを割り当てる
- repository全体で旧ID参照を検索
- migration mapを作る
- Claim / research / catalog参照を一括更新
- 修復後にSource ID uniqueness gateを追加

---

# 5. HIGH — 旧handoffがcurrent復元経路に残る

現行のmain `PERMANENT_RULES.md` はlive authorityを:

1. live main
2. `CURRENT_STATE.md`
3. current live GitHub Issue
4. latest checkpoint
5. `PERMANENT_RULES.md`

としている。

しかし以下は依然として
`KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
をcurrent restore orderへ含める。

- Issue #44 body
- `KNOWLEDGE_CATALOG.md`
- `current/README.md`
- `catalog/README.md`

handoff本文自体は後日追記されているものの、
固定日付ファイルをlive authorityより前面へ残すのは現在のproject ruleと不整合。

### 推奨

current restore orderから削除し、
historical/recovery snapshotへ降格。

---

# 6. HIGH — Legacy Mapの役割誤分類

`current/LEGACY_MAP.md` は現在:

- `CURRENT_PRODUCT_GOAL_20260909.md` -> `current purpose evidence`
- `KNOWLEDGE_HANDOFF_CURRENT_20260909.md` -> `current lane restart`

と記載。

しかしmain `PRODUCT_GOAL_LOCK.md` は、
2026-09-12に旧
`Special -> 共起補助 -> Prompt`
主目的から
`理解 -> 発見 -> 選択 -> 出力`
へ更新したと明記している。

`CURRENT_PRODUCT_GOAL_20260909.md` は実際に:
- Special-first
- minimum useful support
- model-family Prompt
を「current product goal」として記述。

よって現在はhistorical product-goal evidenceとして扱うべき。

同様に旧handoffもhistorical snapshotへ降格すべき。

---

# 7. HIGH — current/に古い監査・backlogが残る

次のファイルは `current/` にあるが、現在状態を表していない。

## SELF_AUDIT_20260909.md

旧状態:
- DEV/PROMPT/AUDIT authority unchanged
- #32 verdict / old Stage10 production前提
等が残る。

現在の2班 + 必要時AUDIT、PROMPT統合後の構造とは異なる。

## PRACTICAL_GENERATION_READINESS_AUDIT_20260913.md

当時の弱点として:
- sampler/scheduler
- resolution
- LoRA
- Hires
- img2img/inpaint
- regional/control
- runtime/performance

等を列挙。

2026-10-02のBATCH_AZ〜BCおよび大量の実践研究で、
この評価は大幅に古くなっている。

## RESEARCH_BACKLOG_20260913.md

9/13〜9/17時点のP0/P1/backlog構造であり、
10/2のBATCH_O〜BC、成人向け教材、LoRA、Reference、Regional等を反映しない。

## ASSET_INVENTORY.md

初期inventoryとして有用だが、
10/2追加の大量research/current資産を十分反映していない。

### 推奨

削除ではなく:
- `SUPERSEDED / HISTORICAL SNAPSHOT` bannerを追加
- current reading routeから外す
- 最新audit / current guideへのリンクを追加

---

# 8. MEDIUM-HIGH — research batch識別子衝突

独立したresearch fileに同じBatch prefixが複数存在。

### 実質的な衝突

- BATCH_N: 2 files
- BATCH_AJ: 2 files
- BATCH_AK: 2 files
- BATCH_AL: 2 files
- BATCH_AM: 2 files
- BATCH_AN: 3 files
- BATCH_AO: 3 files

A/B/Cの `*_SOURCES` は元BatchとSource companionなので意図的な組として扱える。

AJ〜AOは別テーマの独立研究であり、
`BATCH_ANを参照`
のような短縮参照が一意にならない。

### 推奨

既存research原本をrename/deleteしてprovenanceを壊さない。

代わりに:
- full filenameをcanonical research identityとする
- bare Batch prefix参照を禁止
- future batchは一意な連番/UUID的suffixを採用
- File Mapでcollisionを明記

必要なら後からalias/migration mapを作る。

---

# 9. MEDIUM — Character / Style / LoRA researchの重複

研究14本を語彙ベースで比較。

高い類似例:

- AJ Character/style evaluation ↔ AJ LoRA capacity/reference/evaluation: 0.602
- AJ capacity/reference ↔ AL reference adapter vs LoRA: 0.593
- AL reference adapter ↔ AO Ill/Noob character/style training: 0.587
- AL native style ↔ AO Ill/Noob training: 0.553
- AM practical workflow ↔ AN failure-driven recipes: 0.544
- AM identity/outfit ↔ AN identity-core: 0.538
- AO model profiles ↔ AO prompt tuning: 0.528
- AK dataset curation ↔ AK disentanglement dataset: 0.520

完全コピペ段落は検出しなかった。
したがって「同じ文書のコピー」ではなく、
**近接テーマを別研究で繰り返し説明している状態**。

研究原本としては許容。
current層へ同じ説明を全て再投影しないことが重要。

---

# 10. MEDIUM — Community researchのumbrella重複

BATCH_O〜Xでも重複が大きい。

例:

- O ↔ Q: 0.544
- O ↔ R: 0.532
- O ↔ P: 0.527
- O ↔ U: 0.510
- R ↔ U: 0.486
- P ↔ S: 0.482

BATCH_Oが広いharvestで、
後続P/Q/R/S/U等が同じsource群をtopic別に再整理している構造。

### 推奨

researchはevidence/historyなので保持。
ただし今後:
- umbrella harvestはSource Registryへの入口
- focused batchは新規解釈/新規Claimだけを書く
- 既にpromotion済みの共通原則を再説明しない

---

# 11. MEDIUM-HIGH — current説明文書の役割重複

主要current文書を語彙ベースで比較した参考値:

- Teacher Reference ↔ Practical Noob/Anima: **0.757**
- Practical Noob/Anima ↔ Current Quick Reference: **0.688**
- Teacher Reference ↔ Teaching Curriculum: **0.667**
- Practical Noob/Anima ↔ Adult Catalog: **0.645**
- Teaching Curriculum ↔ Practical Noob/Anima: **0.638**
- Decision Tree ↔ Local Adult Workflow Playbook: **0.558**

役割は違うが、
model cards / failure taxonomy / LoRA / Regional / Negative / finishing等を
複数current文書へ繰り返し書いている。

これは更新時に片方だけ古くなるリスクが高い。

### 推奨するcurrentの役割

1. `CURRENT_QUICK_REFERENCE.md`
   - 数ページの索引
   - current authorityへのリンク
   - 詳細説明を持たない

2. `IMAGE_GENERATION_FOUNDATIONS_JA.md`
   - 基礎理論だけ

3. `PRACTICAL_GENERATION_NOOB_ANIMA.md`
   - model/profile固有の実践差だけ

4. `ADULT_IMAGE_GENERATION_DECISION_TREE.md`
   - failure -> 診断 -> 次の操作だけ

5. Teaching Curriculum
   - 教える順番だけ

6. Teacher Reference
   - Decision Tree / Practical guideへの索引中心へ薄くする

7. Local Adult Workflow Playbook
   - Decision TreeまたはTeacher Referenceへ吸収候補

8. catalog/05
   - semantic/domain構造と研究への入口に限定

---

# 12. MEDIUM-HIGH — 日本語-firstルール違反

2026-10-02に追加した恒久ルール:
**人間向け説明は日本語を主、英語は補助。**

既存current文書はまだこのルールへ移行していない。

機械集計の参考値
（URL/コード行等をある程度除外した「英語のみ行」割合）:

- CURRENT_QUICK_REFERENCE: 約94%
- PRACTICAL_GENERATION_NOOB_ANIMA: 約92%
- ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM: 約92%
- ADULT_IMAGE_GENERATION_TEACHER_REFERENCE: 約87%
- IMAGE_GENERATION_FOUNDATIONS_JA: 約39%
- ADULT_IMAGE_GENERATION_DECISION_TREE: 約33%
- LOCAL_ADULT_WORKFLOW_PLAYBOOK: 約28%
- LOCAL_ADULT_IMAGE_GENERATION_TREND_MAP: 約32%

これは厳密な文章品質指標ではないが、
上位4文書が日本語-firstでないことは明白。

### 推奨

current/user-facing文書だけ優先して日本語化。
research/source/Claimの内部英語は無理に翻訳しない。

---

# 13. 現時点で「重大な意味矛盾」と判定しなかったもの

### Anima tag-only vs hybrid

Claim RegistryはHOLD:
どちらが普遍的に優れるか未確定。

current guideの:
- tag-onlyで曖昧なら短い自然文も比較
- hybridを使える

は「比較手段」としてなら矛盾しない。

ただし `hybrid workhorse` は強すぎるため表現修正推奨。

### Negative

unusual anatomy/countの正確な効果はHOLD。

一方:
- suppressive Negativeを成人向け能力試験の中立baselineにしない
- ON/OFF A/Bする

は診断方法であり、HOLDと矛盾しない。

### WAI17

current文書はWAI17をhistorical/comparisonへ降格しており、
NoobAI primary / Anima secondaryと概ね整合。

---

# 14. Source URL重複

Source Registry:
- URL記載: 337
- unique URL: 270

同じ公式model cardを複数topicで使うこと自体は正常。

問題はURL重複ではなく**Source ID衝突**。

将来的には:
- canonical source entryを1つ
- 各Batch/ClaimはそのIDを参照
へ寄せるとRegistryが薄くなる。

---

# 15. 修復優先順位

## P0 — 先に直す

1. Source ID 30衝突の解消
2. Issue #44 / KNOWLEDGE_CATALOG / current README / catalog READMEのrestore orderから旧handoffを外す
3. LEGACY_MAPの旧Product Goal / Handoff役割をhistoricalへ修正
4. currentの旧audit/backlogへSUPERSEDED banner

## P1 — 次

5. current説明文書の役割分離・重複削減
6. 日本語-firstへcurrent文書を改稿
7. Batch prefix collisionをFile Mapで明示し、今後のIDルールを固定
8. Source Registryのcanonical source重複整理

## P2 — 最後

9. research本文の冗長な説明を今後増やさない運用
10. historical root文書の命名/配置を将来整理
11. current/corpus/catalogの同一結論コピーをpointer化

---

# 16. 削除方針

今回の監査では削除・rename・Source ID書換えは行わない。

理由:
- research原本はprovenance
- Source ID変更は参照全件確認が必要
- Batch renameはFile Map / Claim / research相互参照を壊し得る

まずmigration-safe cleanupを別作業として実施する。

---

# 17. 最終判定

## Knowledge correctness
**PASS with scoped HOLD**

Claim Registryの状態管理は健全。
大規模な技術Claim矛盾は未検出。

## Knowledge organization
**FAIL / CLEANUP REQUIRED**

理由:
- Source ID collision
- stale current routing
- stale current documents
- research identifier collision
- current-layer duplication
- Japanese-first migration incomplete

## Production impact
None.

この監査はknowledge branchのみ。
production `data/**` / runtime defaultsは変更していない。


---

## 18. P0 remediation — 2026-10-02

監査後にmigration-safe cleanupを実施。

完了:
- Source Registryの30 collision ID / 33 duplicate occurrencesを修復
- 修復後Source ID duplicate = 0
- `SOURCE_ID_MIGRATION_20261002.md` を追加
- Issue #44 restore orderから固定日付handoffを削除
- `KNOWLEDGE_CATALOG.md` / `current/README.md` / `catalog/README.md` のlive restore orderから固定日付handoffを削除
- `LEGACY_MAP.md` で旧Product Goal / handoffをhistoricalへ再分類
- `CURRENT_PRODUCT_GOAL_20260909.md` / `KNOWLEDGE_HANDOFF_CURRENT_20260909.md` / `GENERATION_KNOWLEDGE_INDEX.md` にhistorical/superseded bannerを追加
- `SELF_AUDIT_20260909.md` / `PRACTICAL_GENERATION_READINESS_AUDIT_20260913.md` / `RESEARCH_BACKLOG_20260913.md` にsuperseded bannerを追加
- `ASSET_INVENTORY.md` をpartial/historical inventoryとして明示
- Source ID uniqueness / research full-filename identity ruleをGovernanceへ追加

追加整合:
- WAI17の `VERSION_FRESHNESS_LEDGER.csv` applicabilityを `COMPARISON_HISTORICAL_LOCAL_EVIDENCE` へ修正
- `PRACTICAL_GENERATION_NOOB_ANIMA.md` のAnima hybrid表現を、tag-only vs concise hybridがHOLDであることを明示する表現へ修正
- Issue #44 restore orderへ `current/README.md` をlive management entryとして追加

未実施:
- current説明文書の大規模重複削減
- current説明文書の全面日本語-first改稿
- repeated Source URLのcanonicalization
- research本文の統合/削除

これらはP1/P2。P0修復ではprovenanceを壊すrename/deleteを行っていない。


---

## 19. P1 remediation — 2026-10-02

P1のcurrent層整理を実施。

完了:
- current管理READMEに文書ごとの役割表を追加
- `CURRENT_QUICK_REFERENCE.md` を詳細解説から索引へ縮小
- `PRACTICAL_GENERATION_NOOB_ANIMA.md` をモデル固有情報へ限定
- `ADULT_IMAGE_GENERATION_TEACHER_REFERENCE.md` を先生役の進め方・参照先へ限定
- `ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM.md` を学習順・演習・合格条件へ限定
- `ADULT_IMAGE_GENERATION_DECISION_TREE.md` を失敗診断へ限定
- `LOCAL_ADULT_WORKFLOW_PLAYBOOK_20261002.md` をworkflow型集へ限定
- `LOCAL_ADULT_IMAGE_GENERATION_TREND_MAP_20261002.md` をecosystem動向だけへ限定
- `IMAGE_GENERATION_FOUNDATIONS_JA.md` を日本語-firstで再構成
- `READING_ROUTES.md` を現行正本だけへ更新し、旧backlog/handoffを現役導線から除外
- `catalog/README.md` を日本語-first化
- `KNOWLEDGE_GOVERNANCE.md` を日本語-first化し、current文書の役割分離ルールを追加
- `KNOWLEDGE_CATALOG.md` の復元順番号抜けを修正し、current READMEを導線へ追加

再監査:
- Claim Registry: 323件 / duplicate ID 0 / malformed row 0
- Source Registry: 256件 / duplicate Source ID 0
- 主要current guide間の完全重複段落: 0
- 旧固定日付資料: live reading routeから除外
- HOLD/ACCEPTEDのstatusはP1整理で変更していない

重複削減の代表:
- Quick Reference: 約15.1k字 -> 約2.2k字
- Noob/Anima practical guide: 約38.4k字 -> 約4.2k字
- Teacher Reference: 約11.6k字 -> 約2.9k字
- Teaching Curriculum: 約11.2k字 -> 約2.6k字

詳細情報は削除ではなく、Claim Registry / focused research / model freshness /専門正本へ寄せた。

### 残るP2

- Source Registry内の同一URL再登録のcanonical化
- research原本の将来追加時に既出結論を再説明しない運用の徹底
- root/corpus/catalogの古い英語説明を、必要に応じて日本語-firstへ段階的に整理
- 既存Batch prefix衝突はprovenance保護のためrenameせず、full filename参照を継続
