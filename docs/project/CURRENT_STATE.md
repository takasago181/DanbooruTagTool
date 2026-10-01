# CURRENT STATE

最終更新: 2026-10-01 (#179 reviewed overlay deployed; REVIEW/HOLD retained)

このファイルは **現在地だけ** を保持する人間向けsummary。
過去のrouting/runtime/taxonomy/完了記録は `docs/project/CURRENT_STATE_HISTORY.md` に保存する。

人間向けcurrent dashboard:
- `docs/project/NOW.md`

機械向けcompact routing:
- `docs/project/CURRENT_ROUTING.json`

作業開始時は固定SHAをcurrent truthとせず、live GitHubを再取得する。

## 1. Current routing

現在の主要な独立lane:

- **#132 — Tag classification usability / discoverability**
  - state: **complete; production promotion passed 2026-09-27**
  - Pass A complete for all 31,003 ordinary identities; Pass B/C reconciliation and semantic QA complete
  - PR #197 merged at implementation source main f229ee4d2c3f5ea03dc964634a6d39d7f730710e
  - production static secondary-route delta: 274 pairs / 273 identities; unexpected changes 0; removals 0
  - production runtime: C:\Codex\DanbooruTagTool-App; clean self-contained win-x64; manifest/executable/catalog hashes are recorded in docs/project/NOW.md
  - UserData remained unchanged and was excluded from the publish copy
  - separate semantic residuals were re-derived by #201; no safe shared production rule was accepted
- **#199 — General body/theme facets**
  - state: **complete; production-promoted through PR #200**
  - General: 346 identities / 355 assignments; BODY 247 / THEME 108
  - existing #76 facet IDs and UnifiedBrowseIndex are the production authority
- **#201 — Practical ordinary-tag discoverability finish**
  - state: **complete; PR #202 merged**
  - accepted #64 color/LIVING/local owner projections showed 0 projection omissions
  - no production taxonomy/catalog semantic change was justified
  - production-size intent-first scenario regression coverage added
  - catalog/runtime/UserData remain unchanged from #199 production
- **#179 — Character/Copyright quality audit**
  - state: **reviewed display/search overlay production-promoted; residual REVIEW/HOLD retained**
  - retained continuation branch: `audit/issue179-refresh-20261001`; merged PR #220/#221
  - historical research branch: `research/issue179-character-quality-audit` (evidence only)
  - old Draft PR #181: **closed as stale merge path**
  - Stage A 44,426-row census evidence is retained
  - keep existing continuation commits/evidence; do not restart from main
  - accepted projection 1,215 rows / 1,221 field changes (display 221, search 1,000); display HOLD 17
  - audit checkpoint: `docs/issue179/FINAL_CHECKPOINT_2026-10-01.json`
  - clean main source `a317efdc831b45b2a088fb9d4cdeb7873472253e` promoted; installed 252 PASS / 3 opt-in SKIP; all CI PASS; UserData byte-identical
  - production checkpoint: `docs/issue179/PRODUCTION_CHECKPOINT_2026-10-01.json`
  - Stage B REVIEW subjects 373 and post-overlay regex residuals 12 retained; no forced corrections
  - scope: Character/Copyright identity・日本語display/search・ranking・2D scope品質
  - Artist監査は対象外
  - completed #180/#216 HOME authority is separate and must not be reopened by default

- **#180 / #216 — Character -> HOME Copyright**
  - state: **complete / closed / production-promoted**
  - formal HOME authority + reviewed Browse fallback integrated
  - production fallback: 7,409 Characters
  - unresolved in runtime: 2,336
  - immutable production result: `docs/issue216/PRODUCTION_PROMOTION_2026-10-01.json`
  - research branches/ledgers remain provenance only

- **#188 — Project-wide execution efficiency**
  - state: **complete / closed**
  - cold/warm resume separation, compact routing, immutable-evidence-first progress, transport/CI efficiency and canonical promotion pipeline are in place
  - stale current-authority references to active #180 / next-10-run waiting condition were removed during final cleanup
  - historical progress/status files remain evidence/cache only and do not override immutable results
  - reopen only for a concrete new execution-overhead defect
- **#52 / #138 / #203 / #210 / #211 — maintenance**: complete and closed after #210 promotion and #211 hygiene finalization. PR #205 was superseded and closed without merge; PR #212 supplied the current pipeline.

## 2. Current product/runtime baseline

- user-facing runtime: `C:\Codex\DanbooruTagTool-App`
- distribution: self-contained `win-x64`
- `artifacts/current/` はfallback/reference
- real `UserData` はuser-owned protected state
- production ordinary catalog baseline:
  - General: **30,629**
  - Special: **3,059**
  - runtime ordinary identities: **31,003**
- #199 General body/theme baseline:
  - identities: **346**
  - assignments: **355**
  - BODY: **247**
  - THEME: **108**
- current Special authority: Issue #76 shallow kind/body/theme model
- production LKG: `docs/project/LAST_KNOWN_GOOD.json` and `.md` (source main `a317efdc831b45b2a088fb9d4cdeb7873472253e`)
- runtime shape: 7 total files; single-file self-contained win-x64; root DLL 0; PDB 0; external catalog/UserData/ForgeBridge/manifest schema 3
- current production EXE SHA256: `E14C3DAD00034C5E19EBFB57245BB609889328E1DAEC3C0127751787134511F2`; catalog SHA256 `FF98CA4E952907B1A9021DA21CDB7DEE867A42DD1ABA1D47619BB901A7C462C5`
- current UI mitigation authority: #177
  - Artist hidden
  - legacy RelatedCopyright remains excluded; #216 formal HOME / reviewed Browse fallback now powers Character-Copyright Browse/search
- Performance / Runtime Load Audit と portable/runtime hardening は完了済み。default next taskへ戻さない
- #117/#118 completed baselineをold current-task textから再開しない
- #65 Stage10はparallel learningでありv1 product Gateではない
- #44 KNOWLEDGEはlong-term generation-knowledge owner

## 3. Product goal

Canonical product goal:
- `docs/PRODUCT_GOAL_LOCK.md`

Core flow:

`理解 -> 発見 -> 選択 -> 出力`

v1の中心:
- Promptを日本語-first + canonical Englishで理解
- Japanese / English / mixed search
- General / Specialを実用分類から発見
- userが明示的に選択・削除・並べ替え
- canonical-English Promptを出力

runtime LLM依存、自動Prompt最適化、hidden automatic insertionをv1 defaultにしない。

## 4. Execution architecture

Project-wide authority:
- `docs/project/EXECUTION_ARCHITECTURE.md`
- `docs/project/EFFICIENT_EXECUTION_RULES.md`
- `docs/project/CHAT_START_PROTOCOL.md`

### Cold start

lane/contract/current authorityが未確定ならfull authority recoveryを行う。

### Warm resume

同一lane・同一frozen contract・immutable progress継続時は:
1. compact routing / contract fingerprint
2. live Issue/branch state
3. immutable progress listing
4. changed task-local state

だけを先に確認する。

hash/fingerprint一致時に、このhistoryや大型spec群を毎run全文再読しない。

## 5. Authority and progress rules

Routing precedence:

`live GitHub -> NOW.md / CURRENT_ROUTING.json -> CURRENT_STATE.md -> selected live Issue/latest checkpoint -> PERMANENT_RULES -> task-specific contract -> history`

Progress precedence:

`immutable checkpoint/result -> deterministic validator/reconstruction -> status/progress cache`

- checkpoint/resultは進捗authority
- status/progress summaryは原則derived cache
- stale cacheがvalid immutable progressを巻き戻してはいけない
- source/contract drift時はfail-closed
- protected data / production promotion / deleteは軽量warm-resume対象外

## 6. Protected boundaries

絶対に一般化しない:
- `git clean -fdx`
- `git clean -fdX`
- ignored/protected dataの広範囲cleanup
- real UserDataをpublish output扱いすること
- research laneからproduction apply
- unrelated active laneのbranch/data/authority混在

GitHubに見えないlocal/ignored dataを「不要」「削除済み」と推定しない。

## 7. Historical evidence

以前このファイルに蓄積されていた以下の詳細は:

- 2026-09-22以前のrouting snapshot
- 2026-09-20 runtime authority
- #64/#66/#68/#69/#70/#76/#83/#109/#114/#117/#118等の完了記録
- historical SHAs / CI / taxonomy counts
- old Stage / handoff / maintenance state

すべて:

`docs/project/CURRENT_STATE_HISTORY.md`

へ退避済み。

current taskをhistoryから選ばない。
