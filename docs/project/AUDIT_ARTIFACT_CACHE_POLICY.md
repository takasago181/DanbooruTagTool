# Disposable Audit Artifact Cache Policy

Status: **ADOPTED / PROJECT-WIDE SAFETY RULE**

Purpose: large image-generation/evaluator tests need temporary visual evidence for ChatGPT/DEV audit without bloating Git history or risking deletion of unrelated local data.

## Core separation

Three classes are mandatory:

1. **Original/generated source images** — protected evidence. Audit cleanup must never delete or overwrite them.
2. **Disposable audit copies** — compressed/downsized/contact-sheet copies used only for current visual audit. These may be replaced or deleted.
3. **Textual evidence** — manifest, hashes, evaluator results, routes, metrics, decisions. These remain normal Git evidence.

Generated audit images must **not** be committed to the public repository's normal Git history by default. Use local/private storage or an explicitly approved private sync location. Public GitHub/release/issue upload of generated audit images is prohibited unless DEV explicitly approves the exact content and exposure.

## Disposable cache root

All cleanup-capable code must operate only inside one explicitly configured disposable audit root, for example a path conceptually equivalent to:

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

## Private handoff

Preferred order:

1. local/private synced folder accessible to the reviewing tool/account;
2. one current contact sheet/audit package manually attached when private sync is unavailable;
3. other private temporary storage explicitly approved by DEV.

Do not solve review convenience by publishing generated images into the public project repository.

## Scope

This policy applies to Issue #30 and future generation/evaluator audit workflows. Task-specific specs may tighten retention/sample rules but may not weaken the deletion containment/protected-data safeguards without an explicit DEV decision.
