# NOW — いま何をやっているか

最終整理: 2026-10-01 JST (post-#180/#216 closeout + GitHub cleanup)

このファイルは、GitHubを開いたときに**現在の主作業・進捗・次の行動**を人間がすぐ把握するためのdashboardです。

正本の優先順位:

`live GitHub -> immutable checkpoint/result -> CURRENT_ROUTING.json -> CURRENT_STATE.md -> Issue / task-specific contract`

固定件数・固定HEADはsnapshotです。実作業前にはliveを再取得してください。

---

## Character / Copyright Browse — COMPLETE / production deployed

Issue #180 (formal HOME authority rebuild) and Issue #216 (remaining coverage + reviewed Browse fallback) are **completed and closed**.

PR #219 production-closeout merge checkpoint:
`a2896f27604c66f6beede84c3ff0d83c7ec92bb9`

Current repository main is **live GitHub main**; do not treat the checkpoint SHA above as a permanently pinned HEAD.

Current production runtime was built from:
`cbfab29134ed41e15c25ba24e1426c8411d65207`

Production:
- runtime: `C:\Codex\DanbooruTagTool-App`
- Character: **35,278**
- Copyright: **7,616**
- FORMAL_HOME: **25,533**
- REVIEWED_BROWSE_FALLBACK: **7,409**
- UNRESOLVED: **2,336**
- precedence: **FORMAL_HOME -> REVIEWED_BROWSE_FALLBACK -> UNRESOLVED**
- formal authority mutations: **0**
- UserData before/after: byte-identical; saved **13-tag Prompt** retained
- final candidate + installed catalog: **249 PASS / 3 explicit opt-in SKIP**
- Python #216/#180 regression: **121 PASS**
- CI / performance gates: **PASS**

Exact current runtime hashes and validation evidence are authoritative in:
- `docs/project/LAST_KNOWN_GOOD.json`
- `docs/issue216/PRODUCTION_PROMOTION_2026-10-01.json`

Known non-blocking limitation: automated Windows screenshot capture returns a white client area (also reproduced on the prior production runtime), so machine-captured final visual appearance is **NOT_VERIFIED**. Installed launch/title and saved Prompt accessibility passed.

Do **not** reopen HOME/source research by default. Reopen only for a concrete product regression or a separately approved new scope.


## 1. COMPLETE — #132 Tag classification usability / discoverability

2026-09-27 production promotion completed from live main f229ee4d2c3f5ea03dc964634a6d39d7f730710e.

- Pass A reviewed all **31,003 ordinary identities**; Pass B/C reconciliation and semantic QA are complete.
- PR **#197** merged the static secondary-route overlay into main.
- Clean self-contained win-x64 publish and isolated plus installed-catalog checks passed.
- Actual delta: **274 route pairs / 273 identities**, unexpected changes **0**, removals **0**, non-route catalog metadata changes **0**.
- Runtime: C:\Codex\DanbooruTagTool-App; runtime-manifest.json source main f229ee4d2c3f5ea03dc964634a6d39d7f730710e.
  - EXE SHA256: 4199BE55CF1E0A79600DDC6632756C3436F34DCA9E45DAF965A769E4288EA554
  - catalog SHA256: 24665D7C92B9DE9B22D92C7713F4E9876DC9C15B98E02324BBE670448BEA7FF9
  - manifest SHA256: 238809EA281AC938FFF832FF2F57F0D8363E56E9AE1231F8A8970FCC20C882F6
- Production process smoke passed: the actual EXE reached DanbooruTagTool v1, was responsive, and produced no matching crash event. Visual UI inspection was unavailable.
- UserData was excluded from deployment; README.txt and user.db hashes remained unchanged.

The following owner-level residuals were re-derived by #201. No high-confidence shared production rule was justified, so they remain non-default review topics rather than row-fix queues:
- #64 color/pattern semantic boundary;
- #64/#76 LIVING/NONHUMAN boundary;
- unreproduced routes and local refinements.

## 1.5 COMPLETE — #199 General body/theme facets

- PR **#200** merged and production-promoted.
- The General catalog carries **346 identities / 355 assignments**: BODY 247 and THEME 108, using the existing #76 facet vocabulary and UnifiedBrowseIndex.
- This closes the #132 “Unified facet architecture” follow-up. It is no longer an active issue.

## 1.6 COMPLETE — #201 practical discoverability finish

- PR **#202** merged at `164420b47b3ce6aebe49b59008eebed0c967d52b`.
- Live owner projections for accepted #64 color/LIVING/local paths showed **0 projection omissions**; the broader #132 deltas span multiple owners, so no taxonomy/catalog semantic change was shipped.
- Added production-size intent-first practical scenario regression coverage, including sexual body/action/theme, clothing/pattern, nonhuman, camera/composition, and General-purpose contextual cases.
- Updated the legacy production browse test from obsolete pre-Unified `general` navigation to current Unified route/local behavior.
- Catalog/runtime payload is unchanged from #199 production; no production apply or UserData operation is required for #201.

## 1.7 COMPLETE — #204 Unified filter refresh and visual stability

- PR #206 and production visual follow-up PR #207 are merged; the production visual follow-up is closed.
- Shared canonical state changes immediately refresh facet options/counts, result summary/cards, notification, and persistence.
- Refinement rows remain fixed-height; body/theme choices switch without the rows moving; content intent is mutually exclusive.
- Existing body/theme AND semantics, Undo/Clear All, and Prompt behavior are unchanged.

## 1.8 COMPLETE — #210/#211 maintenance pipeline and project finalization

- #210 merged as PR #212 at live main `a90f5b652d4239709005d020417a236ea9d97ebb`; #205 was superseded and closed without merge.
- Production was rebuilt from merged main with the canonical clean Release self-contained single-file publisher. UserData stayed byte-identical.
- Current runtime LKG is recorded in `docs/project/LAST_KNOWN_GOOD.json` and `.md`; canonical command/validators/promotion are documented in `docs/maintenance/PORTABLE_RUNTIME_PIPELINE.md`.
- Maintenance triage: #52, #138, #203, #210 complete/closed. #188 remains open only for residual efficiency/telemetry disposition; its former "next 10 #180 runs" wait condition is obsolete because #180 is now completed/closed.
- Default Release skip inventory is machine-readable at `docs/project/RELEASE_TEST_SKIP_INVENTORY.json`; all 19 are classified.
- Four clean, durable, duplicate/completed worktrees were removed through normal `git worktree remove`; active #179/#180, #132 evidence, dirty/local-only work and protected data were retained.

## 2. COMPLETE — #180 / #216 Character -> HOME Copyright

目的:
- Characterからsingle HOME Copyrightをhigh-precision authorityで再構築
- unresolved全件をterminal化
- product Browseではreviewed fallbackを安全に追加

最終状態:
- #180: **CLOSED / completed**
- #216: **CLOSED / completed**
- PR #219: **merged**
- production-closeout merge checkpoint: `a2896f27604c66f6beede84c3ff0d83c7ec92bb9`
- repository HEAD: use live `main`
- production: deployed
- research branches / immutable ledgers: provenanceとして保持

次:
- 原則なし
- concrete regressionが出た場合のみ、既存authorityを上書きせず別Issueで扱う


---

## 3. COMPLETE — #188 Execution efficiency / repository structure

目的:
- semantic精度を落とさず、AIの周辺事務処理・重複CI・巨大入力・重複routingを削る

Issue:
- **#188 OPEN**

mainへ反映済み:
- compact routing / cold-vs-warm guidance
- incremental transport / validation
- execution telemetry
- CI deduplication
- canonical publish / promotion authority

現在:
- **completed / closeout済み**
- cold/warm resume、compact routing、immutable-evidence-first progress、CI重複削減、canonical publish/promotionは導入済み
- staleだった #180 ACTIVE / #181 Draft / next-10-#180-runs のcurrent authority記述を最終整理で除去
- historical progress/status filesはcache/evidenceとして保持し、current authorityにはしない

再開条件:
- 新しい具体的なexecution-overhead defectが見つかった場合のみ、狭い新scopeで扱う


---

## 4. STANDBY — #179 Character/Copyright quality audit

目的:
- Character/Copyright identity
- 日本語display/search
- ranking
- 2D scope品質

状態:
- Issue: **#179 OPEN**
- research branch: `research/issue179-character-quality-audit` (evidence retained)
- old Draft PR **#181 CLOSED** as a stale merge path
- Stage A 44,426-row census evidence is retained
- Artist auditは対象外

重要:
- #179は#180/#216のHOME ownershipとは別テーマ
- 再開時はold PRをmergeしない
- live `main` からfresh branchを切り、Stage A evidenceをrevalidate/reuseする


---

## 5. 完了済み / default next taskではない

以下は「今やっている主作業」として復活させない:

- Performance / Runtime Load Audit
- portable/runtime hardening
- #117 implementation baseline
- #118 sexual intent baseline
- #132 taxonomy usability audit
- #199 General body/theme facet expansion
- #201 practical ordinary-tag discoverability finish

現行runtime:
- user-facing: `C:\Codex\DanbooruTagTool-App`
- self-contained `win-x64`
- real `UserData` はuser-owned protected state
- current repository main: use live `main` (dashboard does not pin a self-invalidating HEAD)
- production binary source main: `cbfab29134ed41e15c25ba24e1426c8411d65207`
- current production EXE SHA256: `1CF2A2E4CA9924E9372F6CDD8FCFA8B45C47F96A48079BBAEE325BD8A0652313`
- catalog SHA256: `72E81FF3123FF6872F4F7136C1EE19B9BC42BF58B5DC4CB96B49120893539A8C`
- runtime manifest SHA256: `83ACA3FDB3E9CFA00B1D38505EF269B9285DE213741A2072021EB2C4109E6CCF`
- exact runtime authority: `docs/project/LAST_KNOWN_GOOD.json`


---

## 6. 作業開始時にどこを読むか

### 新しいchat / lane変更 / contract不明

1. `docs/project/CURRENT_ROUTING.json`
2. この `NOW.md`
3. `docs/project/CURRENT_STATE.md`
4. target live Issue / PR / checkpoint
5. `docs/project/PERMANENT_RULES.md`
6. 必要なtask-specific contract

### 同じlaneのwarm resume

1. compact routing / contract fingerprint
2. immutable progress listing
3. changed state
4. next bounded input

変更されていないhistoryや巨大spec群を毎run全文再読しない。

---

## 7. やってはいけないこと

- unrelated active laneを混ぜる
- research branchからproduction apply
- valid immutable checkpointをstale statusで巻き戻す
- real UserDataをpublish output扱いする
- broad cleanup / `git clean -fdx` / `git clean -fdX`
- semantic uncertaintyを速度のためにCHECKED扱いする
- CSV/JSONのdelimiter整形をmodelの目視だけに任せる
