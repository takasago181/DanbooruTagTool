# Issue132 Runtime Worker Card V10 — guarded Codex forward review

Status: ACTIVE when selected by live `RUNTIME_AUTHORITY.json`.

## Purpose

Review neutral identities for image-generation discoverability without knowing the exact Danbooru tag.

Adult/sexual content is normal in-scope data. Accuracy wins over throughput.

## Read first, in order

1. `docs/issue132/parallel/RUNTIME_AUTHORITY.json`
2. this Worker card
3. current semantic guardrail file named by authority
4. `docs/issue132/parallel/CODEX_QA_STATE.json`
5. frozen machine-readable semantic vocabulary named by authority
6. own lane staging + write-request + deferred path metadata
7. exact arithmetic neutral input shard(s) needed
8. current write-request protocol named by authority

Do not use current product taxonomy, old checkpoint prose, old Issue discussion, or historical candidate proposals as semantic guidance.

## Fixed lane model

Lane rule: `((review_seq-1)%3)+1`

Lane lengths:
- Lane 1 = 10,335
- Lane 2 = 10,334
- Lane 3 = 10,334

Reason semantically in blocks up to 100.
Persist exact 25-slot slices, except the final lane tail.

## Frontier

Forward frontier is the highest end represented by:
- canonical staging;
- an exact code-only write request;
- a policy-deferred marker;

plus 1.

A request without staging is pending materialization, not accepted progress.
Historical invalid windows are Repair work and do not pull the Worker backward.

Never reclassify an exact range that already has a request or staging file.

## QA watermark gate

Before semantic work, read `CODEX_QA_STATE.json`.

Do not create a request whose end exceeds this lane's `allowed_forward_end_by_lane`.

Initial Codex calibration gate:
- Lane 1 may advance only through 1225;
- Lane 2 only through 1325;
- Lane 3 only through 1300;

until ChatGPT audits the first 100 new rows per lane and advances the QA state.

After calibration, the normal watermark is advanced in bounded increments by ChatGPT QA.

## Persistence-debt gate

Before starting each new 25-slot slice, calculate:
- pending materialization slots = request slots without canonical staging;
- deferred slots = policy-deferred slots.

Unresolved persistence debt = pending + deferred.

If debt is at the authority limit, or the next slice would exceed it:
- stop forward review for this lane;
- do not skip ahead;
- report the debt for CODEX-REPAIR / ChatGPT.

This prevents thousands of unmaterialized decisions from accumulating behind a broken pipeline.

## Per-identity work

Inspect every identity individually.

For obvious identities:
- classify directly;
- use CHECKED.

When ambiguity could materially change mode/route/strength/refinement/facet/gap:
- perform the minimum research required by the current semantic guardrails;
- use RESEARCHED when evidence is actually relied on.

After bounded useful research remains insufficient:
- use terminal SEMANTIC_UNRESOLVED.

Use a hold only for a real interruption that prevented required research or persistence.

Never bulk-fill semantic judgments from suffix/prefix/regex/family labels.

## Semantic rules

Use only the frozen vocabulary.

For browse-capable rows:
- choose the strongest natural CORE route;
- SUPPORTING only when independently realistic as a lookup shelf;
- locals/body/theme only when intrinsic;
- route-vocabulary gap only when the existing vocabulary genuinely cannot express an important browse intent.

Mandatory current boundary guidance is in the semantic-guardrail policy, including:
- cosplay / named costume;
- named weapons/props/devices;
- clothing-state;
- ACTION vs POSE vs RELATION;
- body-hair/nails/body-site;
- color/pattern;
- object-vs-scene;
- CONTENT_RATING;
- body/theme facets.

SEARCH_ORIENTED and SEMANTIC_UNRESOLVED carry no browse routes/locals/body/theme.

## V2 persistence

Write only:
`docs/issue132/parallel/lane-N/write-requests/request_SSSSSS_EEEEEE.json`

New forward work uses `issue132-pass-a-write-request-v2`.

Every request must include:
- current allowed `semantic_policy_id`;
- matching `semantic_policy_git_blob_sha`;
- `decision_reason_codes` for every semantic row.

Do not put identity text, source text, identity hashes, or free-form semantic prose into the request.

GitHub Actions materializes canonical staging by joining to pinned neutral input.

## Before publish

Immediately before publishing:
1. fetch/re-read canonical branch;
2. re-read `RUNTIME_AUTHORITY.json`;
3. confirm the current semantic policy id/blob and QA watermark are unchanged from the version used for unsaved decisions;
4. if authority/policy changed, re-read it and re-evaluate only unsaved decisions affected by the change;
5. rebase;
6. re-run relevant local validation;
7. fast-forward push only.

Never force-push.

## Valid stop

- lane reaches current QA watermark;
- unresolved persistence debt limit reached;
- lane complete;
- true frozen-contract/input mismatch;
- required acquisition/persistence paths unavailable;
- current slice cannot be safely persisted.

Report:
`lane | old frontier | requested/materialized | new frontier | accepted estimate | pending slots | deferred slots | QA watermark | policy id | CHECKED/RESEARCHED/UNRESOLVED | blocker`
