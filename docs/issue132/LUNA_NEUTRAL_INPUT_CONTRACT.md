# Issue #132 — Luna neutral input contract

Date: 2026-09-23 JST
Status: **RESEARCH INPUT CONTRACT / PRE-HANDOFF**

## 1. Purpose

Pass A must be an independent image-generation discovery judgment.

The input must help Luna understand what a tag means without telling it how the current product classifies that tag.

---

## 2. Source of truth

Build the neutral input from the **same accepted ordinary catalog build chain** used by production.

Do not independently re-create Japanese/alias identity logic from ad-hoc research CSVs if the accepted catalog pipeline can supply the same fields.

Relevant accepted catalog surfaces include:

- canonical identity;
- English/source surface;
- accepted aliases;
- accepted Japanese display;
- accepted Japanese search keys;
- factual Japanese description where available.

General/Special backing entries that resolve to the same runtime identity must be collapsed to one owner identity.

Expected owner count:

**31,003**

---

## 3. Pass-A input columns

Recommended neutral file:

`luna_neutral_review_input_v1.csv`

Columns:

- `review_seq`
- `identity_key`
- `canonical`
- `english_surfaces`
- `display_ja`
- `search_ja`
- `aliases`
- `neutral_description_ja`

No final-decision columns are prefilled.

### identity_key

Use the same identity normalization/reconciliation as current Unified browse.

Do not create new identity logic for #132.

### english_surfaces

Union the canonical/source English surfaces from all ordinary backing entries for the identity.

### display_ja

Use the accepted runtime display Japanese.

When General/Special overlap exists, use the same representative/display preference as the runtime catalog rather than inventing a new #132 preference.

### search_ja

Union accepted Japanese search surfaces.

These are linguistic aids, not browse authority.

### aliases

Use only accepted aliases.

### neutral_description_ja

Include only factual semantic description.

Strip:
- route/category breadcrumbs;
- review status;
- source confidence;
- post-count metadata;
- machine audit labels;
- #64/#76 classification names.

If a description cannot be separated safely from classification metadata, leave it blank.

---

## 4. Fields hidden from Pass A

Do not include:

- General/Special classification status;
- current #64 path;
- current #76 kind/body/theme;
- current Unified route IDs;
- Unified local route IDs;
- #118 content intent;
- usage/post count;
- machine bucket;
- machine review signals;
- Phase 1 pattern family;
- Phase 1 proposed route;
- prototype route additions;
- prior confidence;
- previous KEEP/ADD/REVIEW verdicts;
- route result counts;
- Special ID unless needed only as an opaque evidence locator during RESEARCHED lookup.

These fields belong to Pass B/C.

---

## 5. Why usage/post count is hidden initially

Post count is useful for product prioritization but is not semantic meaning.

Showing it during Pass A can bias the reviewer toward:
- treating high-use tags as more browse-worthy;
- treating rare tags as search-only even when their visual concept is clear.

Therefore:

- semantic route judgment first;
- popularity/product cost later.

---

## 6. Deterministic neutral ordering

Do **not** order Pass A by:
- current route;
- #64 genre;
- #76 kind;
- machine risk;
- Phase 1 family.

That would reveal the current answer indirectly.

Do not group all sibling/modifier families together during the independent pass.

Recommended order:

```
sort_key = SHA256("issue132-pass-a-v1|" + identity_key)
```

Sort ascending by the hexadecimal digest.

Properties:
- deterministic;
- resumable;
- independent of current taxonomy;
- breaks large color/action/object families into the full population;
- reduces local copy-pattern anchoring.

The sort key itself does not need to be shown to Luna.

---

## 7. Continuous processing

Pass A is one continuous job.

The ledger is keyed by identity_key.

On resume:
- regenerate the exact same neutral order;
- skip identities already having a complete Pass-A row;
- continue from the next unreviewed identity.

Periodic commits are persistence only.

They do not define semantic batches.

---

## 8. Pass-A output kept separate

Recommended output:

`full_review/pass_a_independent_discovery.csv`

Do not write Pass-A judgments into the neutral input file.

This keeps:
- source facts immutable;
- model output auditable;
- reruns comparable.

---

## 9. DEV/AUDIT context file

Create a separate file after/alongside the neutral export:

`full_review/dev_audit_context.csv`

It may contain:

- current #64 paths;
- current #76 kind/body/theme;
- current Unified routes;
- local routes;
- #118 content intent;
- usage/post count;
- machine bucket;
- heuristic family;
- route-load context;
- prototype history.

This file is **not shown during Pass A**.

Pass B/C joins it to the frozen Pass-A result by identity_key.

---

## 10. Validation gates

Before Pass A starts:

- neutral rows = 31,003;
- unique identity_key = 31,003;
- blank identity_key = 0;
- identities exactly match #118 ordinary runtime universe;
- no hidden forbidden columns;
- no current route/category text embedded in neutral descriptions;
- deterministic order hash reproduces exactly.

Before using Pass A output:

- output rows = 31,003;
- unique identity_key = 31,003;
- every identity exists in neutral input;
- invalid route IDs = 0;
- missing manual_seen = 0.

---

## 11. Runtime impact

Both neutral input and full-review output are research artifacts.

Neither ships in the application.
