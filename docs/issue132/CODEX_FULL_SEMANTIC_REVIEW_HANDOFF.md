# Issue #132 — Full semantic review handoff

> **Current execution note (2026-09-26):** semantic definitions in this document remain useful, but execution/scheduling/persistence authority now comes from `docs/issue132/parallel/RUNTIME_AUTHORITY.json` and the Codex runbook selected there. Normal ChatGPT Automations are paused. If execution wording below conflicts with live authority, live authority wins.

Status: **SEMANTIC HANDOFF AUTHORITY / EXECUTION STATUS SUPERSEDED BY RUNTIME_AUTHORITY**

CI/frozen pre-handoff compatibility marker retained intentionally:

Status: **READY FOR CODEX LUNA PASS A**

The line above is **not** the current execution state. It is preserved because the existing pre-handoff consistency check treats that frozen text as a contract marker.

> 2026-09-23 execution-routing update:
> This file remains the semantic review handoff/authority, but it is no longer the live scheduler or throughput authority.
> Pass A is currently executed by 3 normal ChatGPT Automation workers + 1 coordinator on `research/taxonomy-usability-audit`.
> Read `docs/issue132/parallel/CURRENT_AUTOMATION_OPERATION.md` for the current 300-row/50-row two-pass QA operation.
> Old references below to a single continuous Codex/Luna executor describe the semantic method, not the current worker scheduling model.
> Do not modify frozen semantic-contract files merely to modernize execution-status wording.

Repository:
`takasago181/DanbooruTagTool`

Working branch:
`research/taxonomy-usability-audit`

## Mission

Review **all 31,003 ordinary runtime identities**, one identity at a time, for image-generation tag discoverability.

The user goal is:

> 作りたい画像の見た目・行為・部位・体位・衣装・構図などから、Danbooruタグ名を知らなくても自然に目的タグへ辿り着けること。

This is not a taxonomy-cleanup exercise.

Do not optimize for:
- number of changes;
- percentage classified;
- elegant ontology;
- agreement with the current app.

Do optimize for:
- unknown-tag discovery;
- image-generation usefulness;
- understandable browse intent;
- adult/sexual generation as a normal target workflow;
- semantic accuracy.

## Hard rule — Pass A must be independent

During Pass A, do **not** inspect or use current product placement for semantic decisions.

Do not use:
- current #64 path assignment;
- current #76 kind/body/theme assignment;
- current Unified route assignment;
- machine OK/REVIEW/NO_AUTHORITY buckets;
- Phase 1 proposals;
- prototype route overrides;
- current Japanese search quality;
- aliases;
- post/usage count;
- route result counts.

Do not read historical Phase 1–6 candidate files to decide a row.

The current app is the audit target, not Pass-A guidance.

Semantic web research is allowed when needed.

## Read first — in this order

1. `docs/issue132/CURRENT_RECOMMENDED_DIRECTION.md`
2. `docs/issue132/FULL_SEMANTIC_REVIEW_PROTOCOL.md`
3. `docs/issue132/LUNA_NEUTRAL_INPUT_CONTRACT.md`
4. `docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md`
5. `docs/issue132/LUNA_PASS_A_LEDGER_CONTRACT.md`
6. live Issue #132 body and latest checkpoint
7. `docs/project/PERMANENT_RULES.md`

If old Issue #132 comments conflict with these files, the current files above win.

Do not substitute older shard-based instructions.

## Preflight

Confirm:
- branch is `research/taxonomy-usability-audit`;
- main is not modified;
- no production apply is attempted;
- no unrelated lane is touched.

Run:

```bash
python scripts/issue132/bootstrap_luna_pass_a.py
```

Expected result:

`READY_FOR_PASS_A`

This creates or validates:

- neutral input:
  `artifacts/issue132/luna-neutral/luna_neutral_review_input_v2.csv`

- frozen contract:
  `docs/issue132/full_review/pass_a_contract_manifest_v1.json`

- continuous ledger:
  `docs/issue132/full_review/pass_a_independent_discovery.csv`

- progress summary:
  `docs/issue132/full_review/pass_a_progress_summary.json`

If the frozen contract already exists, do not regenerate/replace it.

If bootstrap reports contract drift, stop and report the contradiction. Do not silently continue under changed semantics.

## Review order

Review the neutral input in exact `review_seq` order.

The order is intentionally hash-shuffled.

Do not regroup rows by:
- current category;
- sexual intent;
- machine risk;
- token family;
- known candidate family.

The ledger must remain an exact prefix of the neutral input.

No skipping ahead.

## Per-identity review

For each identity:

1. Read `identity_key` and `source_surfaces`.
2. Determine what the tag/concept actually means.
3. Ask:
   > If a user wanted to generate this visual concept but did not know the exact Danbooru tag, where would they naturally look?
4. Select the existing discovery semantics that genuinely fit.
5. Record every required ledger field.
6. Continue to the next identity.

Every identity must be individually considered.

Do not bulk-fill semantic judgments from regex/token patterns.

Similar-looking identities may inform consistency awareness, but each row needs its own explicit judgment.

## Semantic research rule

Use `CHECKED` when:
- meaning is genuinely clear;
- route/refinement intent is clear;
- no subtle reference/domain knowledge is required.

Use `RESEARCHED` when:
- meaning is unclear;
- a meme/event/proper reference matters;
- a subtle semantic distinction changes discovery intent;
- route vocabulary may be insufficient;
- confidence would otherwise be weak.

For `RESEARCHED`:
- actually inspect semantic evidence;
- record the URLs actually relied on.

Prefer:
1. Danbooru wiki/tag information;
2. official/reference source;
3. reliable secondary source when necessary.

Do not infer a confident meaning from the tag spelling alone when meaning is unclear.

If required external evidence is unavailable, do not guess. Use the unresolved path defined by the ledger contract.

## Discovery mode

Allowed:

### BROWSE_WORTHY
A stable visual/category discovery path is natural.

### MIXED
Both browse and name/reference search are materially natural.

This is not an uncertainty bucket.

### SEARCH_ORIENTED
The concept is understood but is mainly something a user would find by name/reference.

Typical cases:
- named meme;
- named event;
- franchise-specific reference;
- idiosyncratic proper phrase.

### SEMANTIC_UNRESOLVED
Meaning still cannot be established after reasonable research.

Do not use this just because route choice is difficult.

## Top-level routes

Use only the existing 19 route IDs defined by:

`docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md`

For selected routes:

- `CORE` = central unknown-tag starting point;
- `SUPPORTING` = real secondary discovery intent.

Normally select:
- one CORE; or
- one CORE plus one independently useful second route.

A third route is exceptional.

Do not add a route merely because one word in the tag matches it.

A route must represent a realistic image-generation lookup intent.

## Local refinement

Use only the fixed existing local refinement vocabulary from the semantic contract.

Rules:
- its parent top-level route must also be selected;
- zero local refinements is valid;
- normally at most one per selected parent route;
- this is an independent audit signal, not current #64 confirmation.

Do not invent local IDs.

## Body/theme refinement

Use only the existing fixed vocabularies:

Body:
- MALE_GENITAL
- BREAST_NIPPLE
- FEMALE_GENITAL
- MOUTH_ORAL
- BUTTOCK_ANAL
- URETHRA

Theme:
- BDSM_RESTRAINT
- INJURY_R18G
- REPRO_PREGNANCY_LACTATION

Select only when intrinsic to the visual concept.

Do not treat these as generic sexual-content labels.

Adult/sexual concepts are a normal target workflow and should be reviewed with the same semantic care as other identities.

## Route vocabulary gap

Use:

`route_vocabulary_gap=YES`

only when:
- the concept is understood;
- browse discovery is genuinely useful;
- an important user mental model cannot be represented by the existing route vocabulary without distortion.

Do not invent a new route ID.

Do not use vocabulary gap as a convenience when an existing route is merely imperfectly worded.

Repeated gaps are analyzed only after all 31,003 identities are complete.

## Important anti-bias rules

Do not force a target distribution.

There is no required:
- ADD count;
- KEEP count;
- multi-route percentage;
- unresolved percentage.

Do not become artificially conservative just because production changes require later evidence.

Pass A is **independent discovery mapping**, not production approval.

Likewise, do not mark every technically related axis.

Examples:
- action + body target may be genuinely multi-entry;
- action + sexual position may be genuinely multi-entry;
- color + target is not automatically COLOR_PATTERN_SHAPE;
- object/place overlap is not automatically dual-route.

The final product gate handles route explosion later.

## Persistence

This is one continuous review, not semantic shards.

Do not stop after a fixed row block and wait for user input.

Periodically persist progress:

1. validate against the frozen contract;
2. update `pass_a_progress_summary.json`;
3. commit the ledger/progress;
4. continue autonomously.

Use:

```bash
python scripts/issue132/validate_luna_pass_a.py \
  --input artifacts/issue132/luna-neutral/luna_neutral_review_input_v2.csv \
  --ledger docs/issue132/full_review/pass_a_independent_discovery.csv \
  --contract-manifest docs/issue132/full_review/pass_a_contract_manifest_v1.json \
  --summary docs/issue132/full_review/pass_a_progress_summary.json
```

Checkpoint boundaries have no semantic meaning.

Do not ask the user to type `continue`.

## Contract drift

The Pass-A contract is frozen once review starts.

If validation reports drift:
- stop semantic continuation;
- report exactly which frozen authority changed;
- do not mix rows produced under different contracts.

Do not edit the contract merely to make existing output validate.

## Completion

After reviewing all 31,003 identities, run:

```bash
python scripts/issue132/finalize_luna_pass_a.py
```

This must first pass complete validation and then generate deterministic Pass B outputs.

Expected completion marker:

`PASS_A_COMPLETE_AND_PASS_B_READY`

Pass B is mechanical comparison only.

It may expose:
- COVERED
- MISSING_CORE_ROUTE
- MISSING_SUPPORTING_ROUTE
- CURRENT_ROUTE_NOT_REPRODUCED
- MISSING_LOCAL_REFINEMENT
- MISSING_BODY_FACET
- MISSING_THEME_FACET
- SEARCH_ORIENTED
- SEMANTIC_UNRESOLVED
- ROUTE_VOCABULARY_GAP

Do **not** convert those flags into production changes.

## Stop point after Pass B

After Pass B:

- commit the completed Pass-A ledger;
- commit the final progress summary;
- preserve/report Pass-B summary and diff location;
- report completion to Issue #132;
- return to DEV/AUDIT.

Do not proceed into Pass C product approval on your own.

Pass C intentionally joins:
- current product taxonomy;
- production Japanese search;
- aliases;
- usage/post count;
- shelf/result sizes.

Those are evaluated only after the independent full-population map is frozen.

## No production mutation

Do not:
- merge to main;
- production-apply;
- modify UserData;
- modify #64/#76/#118 authority;
- change current taxonomy during Pass A;
- add a new runtime route/facet;
- alter search ranking;
- alter PromptToken/canonical identity;
- alter Character/Copyright/Artist lanes.

Research branch only.

## Runtime architecture guardrail

The exhaustive ledger does not ship.

Evidence URLs, semantic summaries, review depth, uncertainty, and full census diagnostics are research-only.

The eventual #132 v1 runtime target remains a minimal static delta through existing browse infrastructure.

New top-level route IDs and new facet axes are default-deny and require a separate later design decision.

## Final report

Return:

- branch;
- final HEAD;
- Pass-A reviewed count;
- missing identity count;
- duplicate identity count;
- validator error count;
- CHECKED count;
- RESEARCHED count;
- discovery-mode counts;
- route CORE/SUPPORTING counts;
- local-refinement counts;
- body/theme counts;
- route-vocabulary-gap count;
- Pass-B flag counts;
- frozen contract manifest SHA;
- neutral input SHA/order SHA;
- final ledger SHA;
- blockers, if any.

Success requires:

- reviewed identities = **31,003**;
- unique identities = **31,003**;
- `manual_seen=YES` = **31,003**;
- missing identities = **0**;
- duplicate identities = **0**;
- invalid route/local/body/theme IDs = **0**;
- contract drift = **0**;
- complete validator PASS;
- Pass B generated;
- no production mutation.
