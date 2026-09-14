# CURRENT STATE

最終更新: 2026-09-14

## Current Stage

**Stage9 completed / beginner-first practical v1 accepted / #64 General taxonomy accepted and integrated / #66 completed / #68 completed / #69 active local final cleanup.**

Current maintenance route:
- **Issue #69** — one-pass local workspace cleanup, explicitly prioritized before Stage10. Its latest DEV routing override is comment `5665797636`.
- Issue #68 is complete. The tracked root was normalized at `e9dae6d82b6db9fe22afe3f123b50405883801a4`; Phase 2E was accepted as a safe no-op. The old #64 checkout's local-only `benchmarks/`, `backups/`, and `_handoff/` remain protected by active consumers/provenance until this final local pass can preserve and safely normalize the primary checkout.
- **Stage10 learning Issue #65 is paused by current user priority until #69 completes.** Stage10 remains a user learning lane, not a Codex product implementation task.

Current workstation WPF launch:
- The current WPF runtime and production `Data/catalog.db` are available under local `artifacts/current/`.
- The local root shortcut `DanbooruTagTool.lnk` launches that WPF app; this shortcut and runtime output are workstation-local conveniences, not tracked product files.

Current Stage10 definition:
- Issue #65
- `docs/stages/STAGE_10_LEARNING.md`

Stage10 is the practical image-generation learning stage (NoobAI XL 1.1 EPS + Forge Neo primary), **not** the old broad Special production A/B stage. It may resume after #69 completion; it is not a Codex implementation gate unless separately assigned by the user.

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
- discover Special through deep browse;
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
- Special deep browse;
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

- Legacy Python/Tk remains reference/evidence during active WPF work.
- Do not make WPF call Python as a required runtime dependency.
- Keep existing protected/source data paths stable during #66 integration.
- `catalog.db` is rebuildable catalog knowledge.
- `user.db` / `UserData` is user-specific state.
- Normal startup must not perform taxonomy/audit rebuilds.
- Broad legacy/data cleanup is a separate post-baseline decision.

## Current route

`#66 practical v1 accepted -> #68 cleanup completed -> #69 local final cleanup -> Stage10 #65 learning may resume`

Issue #69 is the active one-pass local-maintenance lane, explicitly prioritized before Stage10. Preserve unique local evidence first, normalize the primary checkout to live main only after the preserve check, and leave protected data/audit/tooling/UserData/current WPF runtime intact.

Stage10 #65 remains paused until #69 completes. Afterward it returns as the user's practical image-generation learning route; it is not a Codex implementation task unless separately assigned.

Short form:

`#64 accepted/integrated + #66 practical v1 accepted -> #68 completed -> #69 local final cleanup -> Stage10 #65 may resume`

Portable/second-PC acceptance is not in this critical path.

## Workstreams Registry

| TEAM_ID | Status | Scope | Restore anchor |
| --- | --- | --- | --- |
| `GENERAL-DICT:#64` | **COMPLETED / ACCEPTED + INTEGRATED** | General 30,629 practical taxonomy | Issue #64 acceptance comment + production candidate on main |
| `V1-APP:#66` | **COMPLETED / PRACTICAL_V1_ACCEPTED** | beginner-first WPF app, accepted General integration, final Windows acceptance | Issue #66 acceptance comment `5662680719` + main `1486fc242d2eadf9ca24ed803e50ad7af7294004` |
| `MAINT:#68` | **COMPLETED** | tracked-root normalization complete; Phase 2E accepted safe no-op | Issue #68 completion checkpoint `5665690628` |
| `MAINT:#69` | **ACTIVE / ONE-PASS LOCAL FINAL CLEANUP** | normalize primary everyday checkout and safely retire/preserve local workspace material | Issue #69 latest DEV routing override `5665797636` |
| `STAGE10-LEARNING:#65` | **PAUSED BY CURRENT PRIORITY (#69)** | practical image-generation mastery; not a Codex implementation task | Issue #65 + `STAGE_10_LEARNING.md` |
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
- Japanese overlay production 30,629 — completed
- Issue #64 General taxonomy — accepted and integrated at `d69e8b06916b637efd03c05b820ad13dd05e8ec1`
- Issue #66 Phase B clean WPF baseline — merged
- Issue #66 accepted UX refinement — merged at `3f4e47d7331809b2e6a234824799fb3bc179bae8`
- Issue #66 Phase C General integration and practical-v1 acceptance — completed at main `1486fc242d2eadf9ca24ed803e50ad7af7294004`; final Windows acceptance PASS, Release tests 77/77 PASS

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

Stage10 definition:
- Issue #65 + `docs/stages/STAGE_10_LEARNING.md`

Chat history and old Stage/Issue material are supporting evidence only, not current authority.
