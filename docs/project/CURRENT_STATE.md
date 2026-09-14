# CURRENT STATE

最終更新: 2026-09-14

## Current Stage

**Stage9 completed / beginner-first v1 direction locked / #64 bounded rollout review complete with clean integration candidate pending DEV review / #66 UX refinement accepted and merged; General integration and final Windows acceptance remain.**

Current active implementation owners:
- **Issue #64** — final bounded audit verdict and clean production-integration candidate review
- **Issue #66** — consume the accepted #64 taxonomy after it reaches main, then complete practical-v1 Windows acceptance

Current Stage10 definition:
- Issue #65
- `docs/stages/STAGE_10_LEARNING.md`

Stage10 is the practical image-generation learning stage (NoobAI XL 1.1 EPS + Forge Neo primary), **not** the old broad Special production A/B stage. By current user priority it remains paused until the practical v1 app baseline unless the user explicitly changes priority.

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

## Lane A — Issue #64 General 30,629 taxonomy

#64 owns the exact production General 30,629 population, the shallow browse taxonomy, its sidecar, and unresolved accounting.

Latest live DEV review and bounded result:
- Issue #64 latest DEV review comment: **`5660957158`**
- Full effective population: **30,629 / 30,629**, ordered and unique
- PROPOSED: **28,226** / UNRESOLVED: **2,403**
- Confidence: **25,097 HIGH / 3,129 MEDIUM / 2,403 LOW**
- Residual semantic candidates reviewed: **76**; no population-wide semantic reread
- Final bounded verdict: **`ACCEPT_FOR_PRODUCTION_INTEGRATION`**
- Rework branch: `codex/issue64-bounded-rework` at `7e10185a311ae8f0239cad0eb1bc879f7c69a2da`
- Clean candidate branch: `codex/issue64-clean-integration-candidate`, based on live main `3f4e47d7331809b2e6a234824799fb3bc179bae8`

The clean candidate contains only the accepted taxonomy, effective sidecar, concise provenance, focused validation, and this minimal routing sync. It is pending DEV review and remains unmerged. Do not start #66 General catalog/UI integration until that clean candidate is accepted.

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
- General provider boundary waiting for accepted #64.

### Accepted UX refinement merged to live main

Issue #66 UX Refinement Passes 1/2 were accepted and integrated into live main at:

`3f4e47d7331809b2e6a234824799fb3bc179bae8`

The reviewed source was branch `codex/issue66-dictionary-selection-usability` at `ed389e976e48d98309a01b10bc11bae9e42fbdaf`. The accepted refinement includes the clearer dictionary result/detail layout, Current Prompt actions, safer direct-English editing, Prompt Edit toolbar/find/navigation polish, and manually verified drag reorder with Undo/Redo.

Validation on the accepted source: Debug/Release builds PASS, Debug/Release tests 75/75 PASS, `git diff --check` PASS, and Windows drag reorder + Undo/Redo PASS. No #64 taxonomy or protected/canonical data was included.

### Remaining #66 scope

Issue #66 remains open for consuming the accepted General taxonomy through the existing provider/catalog boundary and completing final practical-v1 Windows acceptance. Do not begin General integration until the accepted #64 candidate is merged to main.

After that integration, verify General browse and bilingual search, then complete the final Prompt/copy and Windows workflow checks. No further UX refinement pass is currently required unless a concrete regression is found.

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
- Keep existing protected/source data paths stable while #64 and #66 are active.
- `catalog.db` is rebuildable catalog knowledge.
- `user.db` / `UserData` is user-specific state.
- Normal startup must not perform taxonomy/audit rebuilds.
- Broad legacy/data cleanup is a separate post-baseline decision.

## Current route

Current route:

`#64 accepted/merged -> #66 General integration -> final Windows acceptance -> practical v1 baseline -> Stage10 resume`

After #64 acceptance:
1. #66 consumes only the accepted General taxonomy sidecar through the existing provider/catalog boundary;
2. rebuild/refresh catalog;
3. rerun General browse + Japanese/English/mixed search regressions;
4. finish practical UI/Prompt interaction acceptance on Windows;
5. verify Prompt round-trip / visible-state copy behavior;
6. declare practical v1 baseline;
7. resume Stage10 #65 unless user priority changes.

Short form:

`#64 + #66 UX in parallel -> #64 accepted -> General integration -> final practical Windows acceptance -> v1 baseline -> Stage10 resume`

Portable/second-PC acceptance is not in this critical path.

## Workstreams Registry

| TEAM_ID | Status | Scope | Restore anchor |
| --- | --- | --- | --- |
| `GENERAL-DICT:#64` | **ACTIVE DEV** | General 30,629 practical taxonomy | Issue #64 latest checkpoint + rollout PROGRESS/MANIFEST |
| `V1-APP:#66` | **ACTIVE / PHASE B + UX REFINEMENT MERGED / GENERAL INTEGRATION + FINAL ACCEPTANCE** | WPF app/search/UI + accepted #64 integration + final v1 | Issue #66 body/latest comments + live main WPF implementation |
| `STAGE10-LEARNING:#65` | **PAUSED BY CURRENT PRIORITY** | practical image-generation mastery | Issue #65 + `STAGE_10_LEARNING.md` |
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
- Issue #66 Phase B clean WPF baseline — merged
- Issue #66 accepted UX refinement — merged at `3f4e47d7331809b2e6a234824799fb3bc179bae8`

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
