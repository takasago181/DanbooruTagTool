# Issue #63 Product-Fit Sidecar — Implementation Report

Date: 2026-09-12 (JST)

Status: **Implemented; returned to DEV/AUDIT before merge.** No Stage10 production A/B was started. No Issue #34 ranking work was included.

## Authority and source

- Live `main` at implementation start: `a72c904ddc0537a8bc635a30620dec1ed0c2533c`.
- On final pre-commit refresh, `origin/main` had advanced to `abfdd65a07e2be221d7dcebd49554a75b7863eb7` with 17 management/product-document commits and no overlapping implementation-path changes. Live `CURRENT_STATE.md` and `CURRENT_DEV_TASK.md` still routed to Issue #63; the live Issue remained OPEN and unchanged in implementation scope.
- The latest live management checkpoints preserve #63 as current DEV, require review before merge, and route #64 next after acceptance.
- Current task branch: `codex/issue63-product-fit-sidecar-latest`, based on refreshed `origin/main`.
- Primary implementation commit: `6ac5d9874e696f550728df4f717ce82908ba3d2b` (the final pushed branch tip may include a report-only handoff checkpoint).
- Audit authority: `audit/special2788-product-fit-20260912`; manifest byte SHA-256 `187372bef6937028b16986b76a841719a3710e0ca21b7b885b9230556066a12d`. The manifest is validated against its pinned SHA before expansion/runtime load.

## Implementation

The audited ID sets deterministically produce `data/special2788/product_fit_verdicts.csv` with columns `special_id,product_fit_verdict`. The immutable `ProductFitPolicy` centralizes search, default browse, recommendation, explicit selection, statistics, support, and inspection eligibility. Production knowledge loading fails closed if the pinned manifest or derived CSV is absent, malformed, changed, or inconsistent.

- `KEEP`: standard browse/search/selection/statistics/candidate flow.
- `KEEP_REFERENCE_ONLY`: excluded from default browse and independent recommendation ranking, retained for exact/alias/search/explicit reference selection; the original tag term remains intact.
- `OUT_OF_SCOPE_PRODUCT`: excluded from product-facing search, browse, selection, ranking, and support while remaining in source/history and low-level reference resolution.
- `REVIEW`: searchable and inspectable with an explicit Japanese badge; excluded from automatic statistics/support/recommendation resolution; explicit selection preserves the original literal and shows a warning.
- A separate retained `KEEP` concept is not hidden when an alias/reference entry points to it.
- Stage 4 low-level data and ranking rules remain intact. Eligibility is applied at the product-facing result boundary and before top-K recommendations.

## Generated CSV validation

- Data rows: 2,788.
- IDs: unique, contiguous `1..2788`; duplicate IDs: 0; missing IDs: 0; verdict overlap: 0.
- Counts: `KEEP 1618`, `KEEP_REFERENCE_ONLY 1133`, `OUT_OF_SCOPE_PRODUCT 12`, `REVIEW 25`.
- SHA-256: `357427dfd542a4e582f6fe57bc966539210e794796e9ad93d6350950e1f61f68`.
- Materializer refuses to overwrite a differing existing CSV.

## Validation

- Focused product-fit, Stage 7/9 UI/session/composer, recommendation, and E2E tests: **122 passed**. (Initial run before correcting a synthetic alias fixture: 120 passed, 1 test error; rerun passed.)
- Product-fit + protected Stage-0 integrity test selection: **130 passed, 2 baseline environment/snapshot failures**. The two failures are the same protected README byte-count mismatch and absent stale `PACKAGE_MANIFEST.json` in the baseline.
- Full suite before implementation, using an isolated Pillow dependency because the user Python did not have it: **329 passed, 9 failed**.
- Full suite after syncing the task branch to refreshed `origin/main` (`abfdd65`), using the same Python, local Pillow 12.3.0 dependency, protected data, and writable temp root: **360 passed, 10 failed**. Nine failure identities exactly match the task-start baseline and concern existing manifest/source drift and Stage 8C audit snapshot/count expectations. The additional `tests/test_final_spec.py::test_goal_lock_exists_and_mentions_core_set` is an upstream docs/test mismatch: the refreshed product-goal document uses “Special Core Dictionary”, while the unchanged test still requires the retired “Core Tag Set” wording. No Issue #63 implementation failure was found; see `validation.json` and `archive/issue63-tests/full-latestmain.log`.
- Windows Tk runtime: real local-data app initialized successfully. Manual inspection confirmed reference-only search badges and availability, Review badge, original literal in the Prompt, and the unavailability of automatic statistics/support resolution for Review.
- Pre/post hashes of all 89 existing files under `data/`: unchanged. The only added data file is the requested sidecar. Protected Special canonical CSV, ID assignments, aliases, provenance, and source-layer files were not modified.
- `git diff --check`: PASS. The initial main checkout had no tracked-file changes before the task branch; no merge was performed.

## Changed files

- `.gitattributes`, `.gitignore`
- `danbooru_tag_tool/product_fit.py`
- `danbooru_tag_tool/knowledge.py`, `search.py`, `stage7a_presenter.py`, `stage7a_session.py`, `stage7a_warnings.py`, `stage7b_recommendations.py`, `stage8b_support.py`, `stage9b_runtime.py`, `stage9c_session.py`, `prompt_composer.py`, `ui.py`
- `tools/build_product_fit_verdicts.py`
- `tests/test_product_fit.py`, `tests/test_stage0_integrity.py`
- `data/special2788/product_fit_verdicts.csv`
- `docs/audit/SPECIAL2788_PRODUCT_FIT_VERDICT_MANIFEST_20260912.json`, `SPECIAL2788_PRODUCT_FIT_IMPLEMENTATION_CONTRACT_20260912.md`, `SPECIAL2788_PRODUCT_FIT_AUDIT_20260912.md`, `CODEX_PROMPT_PRODUCT_FIT_IMPLEMENTATION_20260912.md`
- `docs/issue63/validation.json`, this report

## Unresolved

The 9 full-suite failures are pre-existing in the matched baseline, so DEV/AUDIT should review their existing source/data/Stage 8C evidence separately. This report does not classify those historical failures as PASS. No other Issue #63 implementation blocker was found.

## Handoff

Stop here for DEV/AUDIT review. Do not self-merge or continue to Issue #34 until the result is accepted. Branch, final commit, push status, and final test rerun are recorded in the completion message.
