# CURRENT STATE

最終更新: 2026-09-16

## Current Stage

**Stage9 completed / beginner-first practical v1 accepted / #64 General taxonomy accepted and integrated / #66 completed / #68 completed / #69 local final cleanup completed.**

Current maintenance route:
- **Issue #83 — aggressive local cleanup is completed and integrated into `main` via PR #84 at merge commit `7ef69e6c7ffa6a76037f97226a9ed067d59c360d`.** The cleanup retired obsolete legacy Python/Tk/runtime-index assets and reclaimed `14,195,842,291` bytes while preserving the current WPF/catalog/UserData and active #70 dependencies.
- **Issue #76 — Special browse taxonomy v2 is completed and integrated into `main` via PR #81 at merge commit `0a1e94c8268cde97cfbc2305b3f2869d6919b5d6`.** The accepted v2 classification is baked only during explicit catalog build; normal startup reads precomputed `CatalogEntry.SpecialBrowseV2` from `catalog.db`.
- **Issue #80 — Forge bridge v1 is completed and integrated into `main` at `f5ced15e3a368cae29f869527a20bcb41c7237b4`.**
- **Issue #79 — Generation presets (reusable Positive sets + Negative copy) is completed and integrated into `main` at `8f0ba2a1133e4ad63f0a6ccd08eb17a3dda58d93`.**
- **Issue #77 — Prompt output profile switch + tolerant one-click import is completed and integrated into `main` at `60b15d8fef877c70eac5e4f0f5d67ebd358904d7`.**
- **Issue #75 — WQHD visual polish pass is completed and integrated into `main` at `a315bdf6933e5e089174bc32c3ad6a8abc021082`.**
- No successor active DEV implementation issue is designated. Do not infer one from this document.
- Issue #74 — WQHD-first dictionary workspace redesign is completed and integrated into `main` at `f6e8345391cb445010c5fe23f2b1e480b4c514fd`.
- Issue #73 — English Prompt pane density + dictionary add/remove toggle is completed and integrated into `main` at `079964b69192b5191b1bda5e9894b7138f8c75c2`.
- Issue #72 — Prompt category view prototype remains completed and integrated into `main` at `174fee90b23e4a350ffe71d7b60aa834b8cb1296`.
- **Issue #109 — Special reverse audit and production decision are completed.** Production Special is now **3,059 rows** with maximum Special ID **3,088**; the 29 user-approved removals remain stable-ID gaps and no IDs were renumbered. The production source is `data/generation/special2788_generation_profile.csv`; the legacy filename is retained for compatibility.
- **Issue #109 local integration is completed in the workstation runtime.** The catalog was explicitly rebuilt once from the completed production profile and the WPF runtime in `artifacts/current/` was refreshed from the same Release build; local Special is 3,059 and General is 30,629.
- Issue #70 translation/data work is a separate lane. Post-v1 UI/taxonomy/cleanup work must not modify #70 outputs, canonical/protected data, or translation lane state. Its operational authority is now the deterministic dynamic-claim queue in `docs/issue70/data/queue_state.json` with `scripts/issue70/queue_manager.py`; legacy four-lane progress remains immutable migration provenance. Bootstrap currently validates 21 / 186 chunks (10,500 / 92,739 rows), with 82,239 rows remaining.
- Issue #68/#69 cleanup foundations are completed. Issue #83 later retired additional obsolete/reproducible local and tracked legacy assets after dependency proof; active #70 data, current catalog inputs, modified #64 worktree state, current SDK/NuGet, and #24 backups were intentionally retained.
- **Stage10 learning Issue #65 may resume as the user's learning route.** It is not part of completed #76/#83.

Current workstation WPF launch:
- The current WPF runtime and production `Data/catalog.db` are available under local `artifacts/current/`.
- The local root shortcut `DanbooruTagTool.lnk` launches that WPF app; this shortcut and runtime output are workstation-local conveniences, not tracked product files.
- The pre-integration local `catalog.db` was the historical **2,788 Special** catalog. It was replaced once by the completed **3,059 Special** production profile; the 29 deleted IDs remain absent as stable-ID gaps. Existing `UserData/user.db` remains user-owned state and its hash was unchanged through the integration.

Current Stage10 definition:
- Issue #65
- `docs/stages/STAGE_10_LEARNING.md`

Stage10 is the practical image-generation learning stage (NoobAI XL 1.1 EPS + Forge Neo primary), **not** the old broad Special production A/B stage. It resumed after #69 completion; it is not a Codex implementation gate unless separately assigned by the user.

## Product goal

Canonical authority:
- `docs/PRODUCT_GOAL_LOCK.md`

Core flow:

`理解 -> 発見 -> 選択 -> 出力`

The practical v1 must let the user:
- load/start a Prompt;
- understand recognized content Japanese-first while retaining canonical English;
- preserve unknown/raw/duplicate surfaces unless explicitly edited;
- search Japanese / English / mixed;
- discover Special through the accepted v2 `種類 / 部位 / テーマ` browse facets;
- discover General through shallow practical browse after #64 acceptance;
- explicitly add/remove/reorder/undo/redo;
- copy the canonical-English Prompt represented by the visible workspace.

## Completed Lane A — Issue #64 General 30,629 taxonomy

Issue #64 production taxonomy was accepted and fast-forwarded to main at `d69e8b06916b637efd03c05b820ad13dd05e8ec1`; its latest DEV acceptance is comment **`5661435196`**. The Issue is complete. The accepted taxonomy is available in the repository, while WPF catalog/provider integration remains #66 work.

Accepted production evidence:
- Effective population: **30,629 / 30,629**, ordered and unique
- PROPOSED: **28,226** / UNRESOLVED: **2,403**
- Confidence: **25,097 HIGH / 3,129 MEDIUM / 2,403 LOW**
- Residual semantic review: **76 bounded candidates**; no population-wide semantic reread
- Effective sidecar SHA-256: `a118f5f904c38cee5b63f0c83b06a56f50ee8afdb623c52eb354731bc0b846d9`
- Taxonomy SHA-256: `7311fa1bf1523fcd83134c975b579289d7dbc8aa4cdb1313952d906fc2beb70f`
- Canonical sequence SHA-256: `ca5cc065c92aa38f9daa6b6c8a1f1c13db135057ebfabca076479dfa96872e2b`
- Post-merge validator: PASS; focused test: **1 passed**; `git diff --check`: PASS

The sidecar is separate from canonical identity and Japanese overlay data. UNRESOLVED rows remain explicit and non-browsable; no catch-all taxonomy node was added.

## Lane B — Issue #66 WPF app/search/UI

### Accepted main baseline

Issue #66 Phase B clean WPF baseline is merged to live main at:

`837d08f259c52811ec7a97ae6235cd22e4e2d35c`

Main management sync later advanced through:

`f9cc24e870030182ba5a44916a5e8ad5b92f805e`

Accepted baseline includes:
- clean C#/.NET/WPF under `src/`;
- App/Core/Data/Tests separation;
- no required Python/Tcl/Tk runtime dependency;
- conservative Prompt import with raw/order/duplicate preservation;
- Special browse;
- Japanese/English/mixed search with intent-first regression coverage;
- explicit Prompt add/remove/reorder/multi-select/Undo/Redo;
- visible-state = copied-English-Prompt invariant;
- autosave/recovery;
- accepted #64 General taxonomy consumed through the explicit catalog build/provider boundary.

### Accepted UX refinement merged to live main

Issue #66 UX Refinement Passes 1/2 were accepted and integrated into live main at:

`3f4e47d7331809b2e6a234824799fb3bc179bae8`

The reviewed source was branch `codex/issue66-dictionary-selection-usability` at `ed389e976e48d98309a01b10bc11bae9e42fbdaf`. The accepted refinement includes the clearer dictionary result/detail layout, Current Prompt actions, safer direct-English editing, Prompt Edit toolbar/find/navigation polish, and manually verified drag reorder with Undo/Redo.

Validation on the accepted source: Debug/Release builds PASS, Debug/Release tests 75/75 PASS, `git diff --check` PASS, and Windows drag reorder + Undo/Redo PASS. No #64 taxonomy or protected/canonical data was included.

### Phase C and practical-v1 acceptance — completed

The accepted #64 General taxonomy was integrated through the WPF catalog/provider boundary and is present in the live-main baseline `1486fc242d2eadf9ca24ed803e50ad7af7294004`. Catalog refresh remains an explicit build operation; normal app startup opens the built catalog.

Final Windows click-through acceptance passed on an isolated Release publish/UserData. It verified General browse/back navigation; Japanese `青い髪` and canonical `blue_hair` search; continued exclusion of all six #63 `OUT_OF_SCOPE_PRODUCT` rows; mixed Prompt preservation of raw/weighted/LoRA/BREAK/duplicates/order; reorder Undo/Redo; Prompt-local find navigation; copy matching the visible English preview; direct-edit operation lock and cancel; restart persistence; and item-level `long_hair` delete/Undo/Redo/final Undo restoring the original eight items. No obvious clipping was observed at the tested app area.

Release tests passed **77/77**. Protected/canonical/source data, real user `UserData`, and accepted #64/#63 assets were unchanged. The acceptance used only an isolated temporary publish/UserData.

DEV verdict: **PRACTICAL_V1_ACCEPTED**. Issue #66 is complete; do not reopen completed foundations or add another refinement pass without a concrete regression.

## Special browse v2 — Issue #76 completed

Issue #76 replaced the old visible Special 14/38 browse tree with the user-accepted shallow three-axis model while preserving canonical identity and search behavior.

Accepted production shape:
- `種類から探す`: 9 broad kind homes
- `部位から探す`: 6 body-site facets
- `テーマから探す`: 3 theme facets
- facets combine with AND semantics
- no visible catch-all `その他`
- canonical duplicates are deduplicated in result display
- `1つ戻す` removes only the latest facet condition
- `全解除` clears facet/history state without deleting ordinary search text
- fixed axis groups remain expanded while the Special root is open

Accepted data/runtime boundary:
- Current production Special population is 3,059 stable identities drawn from the 1..3,088 ID space; the 29 Issue #109 removals remain gaps.
- Current baked v2 status distribution is `2718 / 315 / 5 / 0 / 21` for `AutoCandidate / HumanResolved / DeferProductFitReview / OutOfScopeNoBrowse / ReferenceOnlyNoDirectBrowse`.
- The historical 2,788 base identity set, Issue #96 expansion, and Issue #107 expansion remain provenance layers; they are not the current production population.
- Issue #56 v1 evidence remains preserved as provenance
- Issue #76 evidence is parsed only during explicit `--build-catalog`
- baked v2 classification is stored in `catalog.db` as `CatalogEntry.SpecialBrowseV2`
- normal startup reads only precomputed classification data

Final implementation branch tip: `cf6f34919d163d346411d562e9075b3843f4b170`.
Merged through PR #81 at main merge commit `0a1e94c8268cde97cfbc2305b3f2869d6919b5d6`.
Issue #76 is closed completed; final checkpoint comment is `5679492819`.

## Aggressive local cleanup — Issue #83 completed

Issue #83 performed a dependency-proven retirement of obsolete local and tracked legacy assets after the current WPF/#76 baseline was validated.

Accepted result:
- before: `16,183,761,657` bytes
- after: `1,987,919,366` bytes
- reclaimed: `14,195,842,291` bytes (`14.196 GB` / `13.221 GiB`)
- retired obsolete 11M-post Parquet/runtime source, CSR/runtime index, stale worktrees, old publish/bin/obj, quarantine/archive/handoff/audit/benchmarks, and retired Python/Tk runtime/tests/tools/workflows
- current `catalog.db` and current `UserData/user.db` hashes unchanged
- at the time of #83, the local catalog remained Special `2,788` / General `30,629`; Issue #109 later established the current production Special population as 3,059
- WPF startup PASS
- full .NET: `126 passed / 6 skipped`
- #76 focused: `13 passed / 1 skipped`
- #70 queue bootstrap/status PASS; 10 tests PASS; claimed 0
- `git diff --check`: PASS

Intentionally retained/HOLD:
- modified `.worktrees/issue64-full-rollout-audit`
- current SDK/NuGet under `.tools`
- #24 backups
- active #70 queue/source/results
- small #44/#65 candidates where current dependency was not disproven

Final implementation branch tip: `28ab39f111e438288619781f98311f3414a090ec`.
Merged through PR #84 at main merge commit `7ef69e6c7ffa6a76037f97226a9ed067d59c360d`.
Issue #83 DEV acceptance: comment `5680343047`.

## Portable / artifact decision — 2026-09-14

Portable/self-contained packaging is **not a practical-v1 completion Gate** for this personal local tool.

Keep:
- clean WPF architecture;
- no Python/Tcl/Tk runtime dependency;
- `catalog.db` vs `UserData/user.db` separation;
- relative/local paths where practical;
- existing self-contained publish capability if useful later.

Practical v1 does **not** require:
- self-contained publish on every iteration;
- portable-folder packaging as the standard completion format;
- second-PC folder-copy validation;
- .NET-runtime-absent machine validation;
- UserData migration to another PC.

Portable distribution is optional/post-v1 unless the user later reprioritizes it.

Routine UI work should use build/test/Windows launch. Do not proliferate versioned `artifacts/*-vN` and `screenshots-vN` folders. Prefer fixed disposable local paths such as:
- `artifacts/current/`
- `artifacts/screenshots/`
- `artifacts/publish/` only when publish is explicitly requested.

Artifacts remain untracked. Cleanup must be scoped to known disposable artifact paths; `git clean -fdx` / `git clean -fdX` remain forbidden.

## Architecture / migration boundaries

- Legacy Python/Tk runtime/tooling is retired from the current product by Issue #83; do not reintroduce it as a required runtime dependency without an explicit new decision.
- Keep current catalog build inputs and active-lane dependencies stable unless a dedicated maintenance task proves safe movement/deletion.
- `catalog.db` is rebuildable catalog knowledge.
- `user.db` / `UserData` is user-specific state.
- Normal startup must not perform taxonomy/audit rebuilds.
- Future cleanup should again be dependency-based rather than preserving or deleting assets solely because they are ignored/local.

## Current route

`#66 practical v1 accepted -> #68 cleanup completed -> #69 local final cleanup completed -> #72 completed/merged -> #73 completed/merged -> #74 completed/merged -> #75 completed/merged -> #77 completed/merged -> #79 completed/merged -> #80 completed/merged -> #76 completed/merged -> #83 completed/merged`

Issue #83 superseded the earlier broad-cleanup hold state: obsolete/reproducible legacy assets were removed after dependency proof while current product state, active #70, current catalog inputs, and unresolved HOLD items were preserved.

Issue #70 remains a separate translation/data lane and Stage10 #65 remains a separate learning lane.

Short form:

`#64 accepted/integrated + #66 practical v1 accepted -> #68/#69 completed -> #72/#73/#74/#75/#77/#79/#80/#76/#83 completed/merged`

Portable/second-PC acceptance is not in this critical path.

## Workstreams Registry

| TEAM_ID | Status | Scope | Restore anchor |
| --- | --- | --- | --- |
| `POST-V1:#76` | **COMPLETED / MERGED** | Special browse taxonomy v2, shallow kind/body/theme facets, catalog bake-in | Issue #76 + PR #81 + main `0a1e94c8268cde97cfbc2305b3f2869d6919b5d6` |
| `POST-V1:#73` | **COMPLETED / MERGED** | English Prompt pane density and safe dictionary add/remove toggle | Issue #73 + main `079964b69192b5191b1bda5e9894b7138f8c75c2` |
| `POST-V1:#72` | **COMPLETED / MERGED** | Japanese Prompt category reading view in existing WPF Prompt editor | Issue #72 + main `174fee90b23e4a350ffe71d7b60aa834b8cb1296` |
| `GENERAL-DICT:#64` | **COMPLETED / ACCEPTED + INTEGRATED** | General 30,629 practical taxonomy | Issue #64 acceptance comment + production candidate on main |
| `V1-APP:#66` | **COMPLETED / PRACTICAL_V1_ACCEPTED** | beginner-first WPF app, accepted General integration, final Windows acceptance | Issue #66 acceptance comment `5662680719` + main `1486fc242d2eadf9ca24ed803e50ad7af7294004` |
| `MAINT:#68` | **COMPLETED** | tracked-root normalization complete; Phase 2E accepted safe no-op | Issue #68 completion checkpoint `5665690628` |
| `MAINT:#69` | **COMPLETED** | preserve unique local evidence, retire safe stale worktrees/caches, normalize primary root to live main, validate WPF/catalog/data | Issue #69 final DEV closeout comment |
| `MAINT:#83` | **COMPLETED / MERGED** | dependency-proven aggressive cleanup of obsolete/reproducible local assets and retired legacy runtime artifacts | Issue #83 + PR #84 + main `7ef69e6c7ffa6a76037f97226a9ed067d59c360d` |
| `POST-V1:#77` | **COMPLETED / MERGED** | generic persistent Prompt output profiles and conservative one-click import | Issue #77 + main `60b15d8fef877c70eac5e4f0f5d67ebd358904d7` |
| `POST-V1:#79` | **COMPLETED / MERGED** | local reusable Positive presets paired with opaque Negative Prompt copy | Issue #79 + main `8f0ba2a1133e4ad63f0a6ccd08eb17a3dda58d93` |
| `POST-V1:#80` | **COMPLETED / MERGED** | local Forge bridge for visible English Prompt delivery to txt2img fields without generation | Issue #80 + main `f5ced15e3a368cae29f869527a20bcb41c7237b4` |
| `STAGE10-LEARNING:#65` | **READY / USER LEARNING LANE** | practical image-generation mastery; not a Codex implementation task | Issue #65 + `STAGE_10_LEARNING.md` |
| `KNOWLEDGE:#44` | **ONGOING / V1 NON-BLOCKING** | knowledge corpus + Prompt/generation knowledge | Issue #44 |
| `MAINT:#24` | OPEN / SAFETY DEBT | protected-data backup/restore | Issue #24 |

Historical only:
- Issue #42 — retired/closed
- Issue #34 — retired/closed; search requirements absorbed into #66
- Issue #5 — retired/closed; responsibilities merged into #44
- old Stage10 production A/B definition — historical/testing evidence only

## Completed / frozen foundations

- Stage9 overall Gate — completed
- Special validation/promotion/freeze #32 -> #48 -> #49 -> #43 — completed
- Special Core Dictionary practical taxonomy #56 — completed
- Special product-fit #63 — completed/merged
- Special browse taxonomy v2 #76 — completed/merged
- Japanese overlay production 30,629 — completed
- Issue #64 General taxonomy — accepted and integrated at `d69e8b06916b637efd03c05b820ad13dd05e8ec1`
- Issue #66 Phase B clean WPF baseline — merged
- Issue #66 accepted UX refinement — merged at `3f4e47d7331809b2e6a234824799fb3bc179bae8`
- Issue #66 Phase C General integration and practical-v1 acceptance — completed at main `1486fc242d2eadf9ca24ed803e50ad7af7294004`; final Windows acceptance PASS, Release tests 77/77 PASS
- Issue #83 aggressive local cleanup — completed/merged; obsolete legacy/runtime-index assets retired and 14.196 GB reclaimed

Do not restart completed foundations wholesale without demonstrated regression or explicit redesign decision.

## Source-of-truth rule

Restore current work in this order:
1. live `main` HEAD
2. live `docs/project/CURRENT_STATE.md`
3. current live Issue body
4. latest Issue checkpoint/comment
5. `docs/project/PERMANENT_RULES.md`
6. relevant current feature branch/local worktree

Product goal:
- `docs/PRODUCT_GOAL_LOCK.md`

#66 UI baseline:
- `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md`

#66 WPF architecture/runtime boundary:
- `docs/product/V1_WPF_ARCHITECTURE_BASELINE.md`

Current DEV mirror:
- `docs/project/CURRENT_DEV_TASK.md`

Stage10 definition:
- Issue #65 + `docs/stages/STAGE_10_LEARNING.md`

Chat history and old Stage/Issue material are supporting evidence only, not current authority.
