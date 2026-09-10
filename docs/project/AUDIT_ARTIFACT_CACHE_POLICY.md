# Disposable Audit Artifact Cache Policy

Status: **ADOPTED / PROJECT-WIDE SAFETY RULE**

Purpose: large image-generation/evaluator tests need temporary visual evidence for ChatGPT/DEV audit without bloating the main repository history or risking deletion of unrelated local data.

## Core separation

Three classes are mandatory:

1. **Original/generated source images** — protected evidence. Audit cleanup must never delete or overwrite them.
2. **Disposable audit copies** — compressed/downsized/contact-sheet copies used only for current visual audit. These may be replaced or deleted.
3. **Textual evidence** — manifest, hashes, evaluator results, routes, metrics, decisions. These remain normal Git evidence in `DanbooruTagTool`.

Generated audit images must **not** be committed to the public `DanbooruTagTool` repository's normal Git history by default.

## Adopted handoff architecture — no Google Drive

Google Drive is not part of the approved workflow.

Preferred storage/organization target is a **separate private disposable audit-cache repository**, conceptually:

`DanbooruTagTool-AuditCache`

Rules for that repository:

- it is **not canonical project evidence**;
- it contains only current disposable audit copies/contact sheets plus a lightweight ownership manifest;
- original/source PNGs remain outside it and protected;
- textual verdict/evaluator/provenance evidence remains in the main `DanbooruTagTool` repository;
- cleanup code for the audit-cache repository must have no delete path into the main repository, protected data, original generation roots, models, or accepted evidence;
- current-audit-set replacement is allowed after all deletion guards pass;
- if history size becomes material, the cache repository may be archived/recreated because it is explicitly non-canonical, but accepted textual results must already exist in the main repository.

### Reviewer-access reality

A separate private GitHub repository is useful for isolation and cleanup safety, but it must **not** be assumed that ChatGPT can directly render/read every private binary image through the GitHub connector.

Until a verified binary-image retrieval path is proven on the actual connection, the guaranteed ChatGPT visual-audit handoff is:

1. Codex creates **one current contact sheet/audit sheet per wave** from the disposable cache.
2. The user attaches that one sheet to the ChatGPT conversation/File Library for visual inspection.
3. ChatGPT audits human-required items plus the selected machine-handled sample from that sheet.
4. The resulting textual verdict is committed back to the main repository.

This keeps manual work to one attachment per wave rather than per image while avoiding Google Drive and public exposure.

If future tooling proves direct private binary retrieval from `DanbooruTagTool-AuditCache`, that verified route may replace the manual one-sheet attachment without changing the safety model.

## Disposable cache root

All cleanup-capable local code must operate only inside one explicitly configured disposable audit root, for example a path conceptually equivalent to:

`<private-local-root>/DanbooruTagTool/audit_cache/current/`

The exact absolute path is environment-specific and must not be guessed.

The root must contain a sentinel file with exact project ownership identity, e.g.:

`.danbooru_audit_cache_v1`

The sentinel is necessary but not sufficient for deletion.

## Mandatory deletion guards

Before any overwrite/delete/cleanup:

1. Resolve the configured root and every target to canonical absolute paths.
2. Refuse empty, relative, drive-root, user-profile-root, repository-root, `data/**`, `docs/**`, model/checkpoint directories, original generation roots, or any path outside the configured audit root.
3. A deletion target must be a strict descendant of the audit root; never delete the audit root itself.
4. Reject path traversal and any symlink/junction/reparse-point path that could escape the canonical root.
5. Keep a per-batch ownership manifest of files created as disposable audit copies. Delete/replace only files owned by that manifest.
6. If an unexpected/unowned file exists in the proposed deletion set, **STOP cleanup**. Do not delete the unknown file to make the operation succeed.
7. Do not use broad recursive wildcard cleanup, `git clean -fdx`, `git clean -fdX`, or equivalent repository-wide/ignored-file cleanup for audit artifacts.
8. Do not couple audit-cache cleanup to deletion of source PNGs, evaluator raw artifacts, production data, protected data, previous accepted evidence, or model files.
9. Log the resolved root, batch id, owned file count, and cleanup result to textual evidence.

Fail closed: if containment, sentinel, ownership, or path-resolution checks are uncertain, cleanup performs **0 deletions**.

## Current-only retention

Default retention is **current audit set only**. A new accepted audit export may replace the previous disposable audit copies after the guards above pass.

This overwrite/delete policy applies only to disposable copies. Original evidence remains independently protected according to the active Issue contract and local protected-data rules.

## Visual audit export

A current audit export should contain only what is useful for visual judgment:

- all current `HUMAN_REVIEW_REQUIRED_PAIR` items when human review is needed;
- a risk/coverage sample of `MACHINE_HANDLED_PAIR` items for independent false-safe checking;
- correct large A/B markers;
- large concrete Japanese questions;
- a lightweight manifest mapping displayed items to `image_id`, pair id, A/B condition, source hash, route, and source locator.

Do not put full Prompt/Negative/evaluator logs on the visual sheet unless a specific audit requires them; keep those in textual evidence.

## Private handoff priority

1. Verified direct private binary retrieval from the separate audit-cache repository, if/when proven on the actual reviewer connection.
2. Otherwise, one current contact sheet/audit sheet manually attached to ChatGPT per wave.
3. Other private temporary storage only when explicitly approved by DEV.

Do not solve review convenience by publishing generated images into the public project repository.

## Scope

This policy applies to Issue #30 and future generation/evaluator audit workflows. Task-specific specs may tighten retention/sample rules but may not weaken the deletion containment/protected-data safeguards without an explicit DEV decision.
