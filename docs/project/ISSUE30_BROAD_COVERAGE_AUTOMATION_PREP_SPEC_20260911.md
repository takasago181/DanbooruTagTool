# Issue #30 Broad Coverage Automation PREP Spec — 2026-09-11

Status: **ACTIVE PREP / NO NEW GENERATION / STAGE10 PRODUCTION NOT STARTED**

## Purpose

Prepare a safe, repeatable high-volume real-image validation loop for the Special Core Dictionary without turning image count into the goal and without returning large manual-review burden to the user.

The target later flow is:

`stratified case selection -> frozen manifest -> generation -> provenance gate -> WD14/Kagami/CL -> evaluator-reference integrity -> machine route -> pair route -> visual false-safe audit sample -> human-required remainder -> coverage/failure metrics -> next-wave selection`

This PREP task does **not** authorize a new broad-coverage generation wave yet.

## Accepted Batch 2 checkpoint

Generation Batch 2 is complete on `codex/issue30-calibration-design`.

Accepted result anchors:
- execution/report commit: `7e516bd1ca27c862cdaf023c023bed74e34e6833`
- human-review commit: `1cd33c7ebec445c3e3870ebce360f9cfee1ffbf9`
- generated images: 16
- evaluator successes: 48/48 = WD14 16 / Kagami 16 / CL 16
- evaluator-reference integrity: PASS after report-reference repair
- machine-handled: 4 images / 2 pairs
- human-required: 12 images / 6 pairs
- blocked: 0
- image/pair review reduction: 25%
- human-required review result: 6/6 pairs `BOTH_PASS`

Do not regenerate or re-review the 12 human-reviewed images.

## Immediate Codex work

Before implementation, fetch latest `origin/main` and merge it into `codex/issue30-calibration-design`. No rebase and no force rewrite. A stale `origin/main` observation is not sufficient; verify the live fetched ref.

Then perform only the following PREP work:

1. Implement/test disposable audit-cache safety guards according to `docs/project/AUDIT_ARTIFACT_CACHE_POLICY.md`.
2. From the **existing Batch 2 source images only**, export one compact visual-audit contact sheet containing the 2 previously machine-handled A/B pairs (4 images total).
3. The contact sheet must use structured manifest/condition for A/B labels and include a large concrete Japanese question for each pair.
4. Write a lightweight audit manifest mapping displayed number/pair/image/A-B condition/source hash/source locator/machine route.
5. Do not add the audit image itself to the normal public Git history.
6. Report the local contact-sheet path so the user can attach that **one file** to ChatGPT for independent visual false-safe audit.
7. Add focused tests for cleanup containment and ownership-manifest behavior.
8. Stop after the audit export is ready. **Generate 0 new images in this PREP step.**

## Disposable audit-cache safety requirements

Cleanup-capable code must fail closed.

Mandatory:
- exact configured audit root; never guess an absolute path
- sentinel ownership marker
- canonical absolute path resolution for root and targets
- deletion targets must be strict descendants of the audit root
- per-batch ownership manifest; delete/replace only owned disposable files
- reject empty/relative/root/profile/repository/data/docs/model/source-generation paths
- reject traversal and symlink/junction/reparse escape
- unknown/unowned file in deletion set => STOP cleanup with 0 deletions
- no broad wildcard cleanup
- no `git clean -fdx` / `git clean -fdX`
- audit cleanup must never delete original PNGs, evaluator raw artifacts, protected data, accepted evidence, or model files

## Audit transfer decision

Google Drive is not used.

Long-term direction: a separate private repository or similarly isolated private cache may be used as **disposable non-canonical audit storage**, physically separated from the main repository. The main DanbooruTagTool repository must not accumulate generated audit images.

However, private Git repository binary visibility to the ChatGPT review path is not assumed. The reliable current handoff is therefore:
- Codex creates one current contact sheet for the requested audit set;
- user attaches that single sheet to ChatGPT;
- text results/manifest remain in GitHub;
- disposable visual copies can be replaced after audit according to the cache policy.

Do not make the user upload dozens of individual images.

## Broad-coverage design after this PREP passes

The first authorized broad-coverage wave should be designed from `docs/project/ISSUE30_BROAD_COVERAGE_AUTOMATION_DIRECTION_20260911.md`.

Initial design envelope:
- 12–20 independent experiments
- normally A/B × 2 fixed predetermined seeds
- approximately 48–80 new images per wave
- stratified across materially different Special semantic families
- adaptive later waves based on failure/variance/disagreement/product value
- no blind 2,788-entry sweep
- no automatic seed expansion merely to chase a preferred outcome

Machine-handled eligibility remains narrow. Relation/binding/count/actor-role/body-site/contact/topology/compound/multi-Special/ambiguous cases stay human-protected unless later evidence explicitly changes the rule.

Every broad wave must visually audit a risk/coverage sample of machine-handled pairs. Initial target: at least 10% of machine-handled pairs, floor 2 pairs when at least 2 exist, plus suspicious/borderline cases. A false-safe finding stops expansion of the affected automatic rule/class until recalibrated.

## PREP completion criteria

PREP is complete only when:
- latest-main synchronization is evidenced;
- cleanup guard tests pass;
- Batch2 machine-handled 2-pair contact sheet exists from existing images;
- audit manifest exists and A/B integrity passes;
- no new images were generated;
- no protected/original files were deleted or modified;
- Codex stops for DEV/ChatGPT visual audit.

After ChatGPT visually audits the 2 machine-handled pairs, DEV decides whether to authorize Broad Coverage Wave 1. Stage10 production A/B remains not started.
