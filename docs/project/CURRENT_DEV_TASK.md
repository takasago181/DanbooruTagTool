# CURRENT DEV TASK

最終同期: 2026-09-11

## Source

- Source Issue: **#30**
- Issue state: **OPEN / ACTIVE**
- DEV state: **PHASE2_ACTIVE / BATCH2_COMPLETE / BROAD_COVERAGE_AUTOMATION_PREP / NO_NEW_GENERATION**
- Stage10 production A/B: **NOT STARTED**
- Working branch: `codex/issue30-calibration-design`
- Current continuation contract: `docs/project/ISSUE30_BROAD_COVERAGE_AUTOMATION_PREP_SPEC_20260911.md`

Supporting policy/direction:
- `docs/project/AUDIT_ARTIFACT_CACHE_POLICY.md`
- `docs/project/ISSUE30_BROAD_COVERAGE_AUTOMATION_DIRECTION_20260911.md`

This file is the Codex-readable mirror of Issue #30. If Issue #30 and this file differ, do not implement until DEV synchronizes them.

## Accepted Batch 2 checkpoint

Generation Batch 2 is complete.

Evidence:
- execution/report commit: `7e516bd1ca27c862cdaf023c023bed74e34e6833`
- human-review commit: `1cd33c7ebec445c3e3870ebce360f9cfee1ffbf9`

Accepted facts:
- generated images: **16**
- A/B pairs: **8**
- actual evaluator success: **48/48** = WD14 16 / Kagami-24k 16 / CL Tagger v2.00 16
- evaluator-reference integrity: PASS after report-reference repair
- A/B marker integrity: PASS
- machine-handled: **4 images / 2 pairs**
- human-required: **12 images / 6 pairs**
- blocked: **0**
- image/pair user-review reduction: **25% / 25%**
- human-required result: **6/6 pairs BOTH_PASS**

Do not regenerate or re-review the 12 already human-reviewed Batch 2 images.

## Immediate work

Before changing files or producing audit assets:

1. Fetch the latest live `origin/main`.
2. Merge latest `origin/main` into `codex/issue30-calibration-design`.
3. No rebase and no force rewrite.
4. Verify that the fetched main contains this mirror and `ISSUE30_BROAD_COVERAGE_AUTOMATION_PREP_SPEC_20260911.md`.

Then execute only the PREP contract:

1. Implement/test disposable audit-cache cleanup guards per `AUDIT_ARTIFACT_CACHE_POLICY.md`.
2. Reuse **existing Batch 2 images only**.
3. Create one visual-audit contact sheet for the two previously machine-handled pairs:
   - B2-001 / seed `44001`
   - B2-001 / seed `44002`
   - total: 2 pairs / 4 images.
4. A/B labels must come from structured manifest/condition.
5. Include large concrete Japanese audit questions.
6. Create a lightweight audit manifest mapping display number, pair, image ID, A/B condition, source hash, source locator, and machine route.
7. Do not commit the contact-sheet image or disposable generated audit copies into the normal public Git history.
8. Report the local contact-sheet path so the user can attach **one file** to ChatGPT.
9. Add focused tests proving deletion containment, sentinel/ownership-manifest checks, and unknown/unowned-file fail-closed behavior.
10. Report protected/original-file integrity and STOP for DEV/ChatGPT visual audit.

**Generate 0 new images in this PREP task.**

## Deletion safety — mandatory

Audit cleanup may delete/replace only files explicitly owned by the audit manifest and strictly below one configured disposable audit root.

Mandatory protections:
- exact configured audit root; never guess it;
- sentinel ownership marker;
- canonical absolute path resolution;
- every deletion target is a strict descendant of audit root;
- reject empty/relative/root/profile/repository/`data/**`/`docs/**`/model/source-generation paths;
- reject traversal and symlink/junction/reparse escape;
- unknown/unowned deletion target => STOP / 0 deletions;
- no broad recursive wildcard cleanup;
- no `git clean -fdx` or `git clean -fdX`;
- never couple audit cleanup to source PNG, evaluator raw artifact, production/protected data, accepted evidence, or model deletion.

## Audit handoff

Google Drive is not used.

A separate private audit cache can later be used as isolated disposable/non-canonical storage, but private Git binary visibility to ChatGPT is not assumed. Current reliable visual handoff is one compact contact sheet attached to chat; textual evidence stays in GitHub.

## Next gate after PREP

After DEV/ChatGPT independently reviews the two previously machine-handled pairs for false-safe behavior:

- PASS -> DEV may create/authorize a new Broad Coverage Wave 1 contract.
- false-safe -> affected automatic rule/class returns to human review and must be recalibrated before expansion.

Planned Wave 1 envelope is **not yet authorized**:
- 12–20 independent experiments
- normally A/B × 2 predetermined fixed seeds
- approximately 48–80 images
- stratified across multiple Special semantic families
- machine-first routing
- machine-handled visual audit sample >=10%, floor 2 pairs when >=2 exist, plus suspicious/borderline cases
- adaptive later waves based on failure/variance/disagreement/product value.

## Human-protected semantics

Keep human-protected by default:
- relation/binding
- exact count
- actor/subject/object assignment
- multi-person role assignment
- body-site ownership/correctness
- insertion/contact/spatial topology
- compound/multi-Special retention
- ambiguous identity/category
- evaluator disagreement/low confidence.

Machine Taggers remain assistive triage only; they are not broad structural semantic ground truth.

## Hard prohibitions

- any new image generation in current PREP
- Stage10 production A/B
- blind 2,788-entry image sweep
- automatic extra seeds merely to chase a desired result
- production/protected `data/**` mutation
- #32 verdict/canonical mutation
- runtime LLM dependency
- generated audit-image accumulation in normal public Git history
- unsafe broad filesystem cleanup
- machine promotion to structural semantic truth
- asking the user to review/upload dozens of individual images when a compact audit sheet can be used

#42 remains downstream; Issue #30 PREP does not bypass its existing gates.
