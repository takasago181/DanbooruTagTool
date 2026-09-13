# Issue #66 v1 application-layer rebuild checkpoint

Status: **FEATURE BRANCH / NOT MERGED / FINAL ACCEPTANCE PENDING**

## Decision

The v1 desktop application layer is rebuilt around the current product goal instead of extending the historical Stage7A/8B/9C UI workflow.

The rewrite boundary is intentionally narrow:

- **reuse**: `TagKnowledgeCore`, canonical/Alias/Japanese overlay data, product-fit policy, existing unified search engine, Special identity, accepted Issue #56 browse taxonomy;
- **new v1 layer**: beginner-facing search policy, visible Prompt workspace, Special/General browse providers, Tk application shell;
- **retain for rollback/history**: legacy `ui.py`, Stage9 composer/session and advanced recommendation/support assets;
- **do not touch**: protected canonical/Special data and Issue #64 General classification work.

This avoids both extremes: keeping obsolete UI coupling and rewriting already-audited knowledge assets.

## v1 normal flow

`既存Promptを読む -> 検索 / Special browse / General browse -> 明示選択 -> 削除 / 並べ替え -> English Prompt preview/copy`

Rules:

- Japanese-first display; English/canonical remains visible and traceable.
- Japanese / English / mixed query stays in one search workflow.
- strong exact intent and word-prefix intent suppress incidental embedded-substring noise.
- unknown existing Prompt surfaces are preserved rather than guessed away.
- no hidden support insertion is used by the v1 workspace.
- preview and clipboard text are derived from the same visible ordered item list.

## Special browse

The v1 provider consumes the completed Issue #56 UI-side taxonomy directly:

- 14 top-level Japanese genres;
- 38 reviewed subgenres;
- complete 2,788-row mapping sources (pilot seed + reviewed rollout fragments);
- primary and meaningful secondary browse paths;
- 43 Issue #56 `REVIEW_REQUIRED` rows remain without a forced browse shelf and stay discoverable through search;
- Issue #63 product-fit `browse` eligibility remains authoritative for normal browse exposure.

The taxonomy is treated only as navigation metadata and never as canonical semantic authority.

## General browse

Issue #64 remains independent and in progress. v1 currently supplies only a stable provider contract and explicit empty state. No #64 candidate row is consumed, changed, or invented before acceptance.

## Current files

- `danbooru_tag_tool/v1_app.py`
- `danbooru_tag_tool/v1_search.py`
- `danbooru_tag_tool/v1_workspace.py`
- `danbooru_tag_tool/v1_browse.py`
- `tests/test_issue66_v1_app.py`
- `.github/workflows/issue66_v1_app.yml`
- `danbooru_tag_tool/__main__.py` points the branch startup at `v1_app.main`.

Legacy `danbooru_tag_tool/ui.py` is unchanged.

## Acceptance still required

- focused and full repository regression against the real branch checkout;
- representative real-data Japanese / English / mixed search review including the `anal` regression;
- Windows/Tk startup/layout/copy/browse round-trip smoke;
- accepted Issue #64 General browse integration;
- final ADOPT / HOLD / REJECT reconciliation against `PRODUCT_GOAL_LOCK.md`.

No main merge is authorized by this checkpoint.
