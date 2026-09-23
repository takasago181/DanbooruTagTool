# Issue #132 — Luna Pass A ledger contract

Date: 2026-09-23 JST
Status: **PRE-HANDOFF OUTPUT CONTRACT**

## 1. Purpose

This file defines the exact output contract for the continuous 31,003-identity Luna Pass A review.

It is a **research ledger**, not runtime data.

The ledger answers:

> このタグの正確な名前を知らない画像生成ユーザーが、この視覚概念を探すなら、どの既存入口が自然か。

It does not answer:
- whether the current app already exposes that route;
- whether #132 should ship the route;
- whether #64/#76 is wrong.

Those questions come later.

---

## 2. File

Recommended path:

`docs/issue132/full_review/pass_a_independent_discovery.csv`

One header + one row per reviewed identity.

The ledger must always be an **exact prefix** of `luna_neutral_review_input_v2.csv`.

No:
- skipped rows;
- out-of-order rows;
- duplicate rows;
- later-row prefill.

This makes restart deterministic.

---

## 3. Exact columns

1. `review_seq`
2. `identity_key`
3. `manual_seen`
4. `semantic_summary_ja`
5. `discovery_mode`
6. `route_1_id`
7. `route_1_strength`
8. `route_1_reason_ja`
9. `route_2_id`
10. `route_2_strength`
11. `route_2_reason_ja`
12. `route_3_id`
13. `route_3_strength`
14. `route_3_reason_ja`
15. `local_refinement_ids`
16. `body_site_ids`
17. `theme_ids`
18. `route_vocabulary_gap`
19. `route_vocabulary_gap_note`
20. `review_depth`
21. `evidence_urls`
22. `uncertainty_note`

Array fields are JSON arrays encoded inside CSV cells.

Example empty array:

`[]`

Do not use pipe-delimited lists in Pass A output.

---

## 4. manual_seen

Always:

`YES`

This means the identity was individually considered.

It does not mean:
- external web research was performed;
- the current product was inspected;
- a production change was approved.

Bulk-filling `manual_seen=YES` without semantic review is prohibited.

---

## 5. semantic_summary_ja

Short plain Japanese describing what the tag means visually.

Good:
- 「相手の胸を噛む行為」
- 「立った姿勢で行う後背位」
- 「性行為後などで乱れた髪」

Avoid:
- copying the canonical with underscores removed;
- route/category names instead of meaning;
- product recommendations;
- current-taxonomy commentary.

When the concept cannot be established after research, state the uncertainty plainly and use `SEMANTIC_UNRESOLVED`.

---

## 6. discovery_mode

### BROWSE_WORTHY

The concept has a natural **visual/category discovery path**.

Use when a user who does not know the exact tag could reasonably start from a route/facet.

It does not mean search is useless.

### MIXED

Both are materially natural:
- category/facet discovery; and
- name/reference-oriented search.

Use for concepts where neither mechanism alone captures the realistic discovery behavior.

Examples may include a named or reference-derived visual that also has a stable generic visual concept.

**MIXED is not an uncertainty bucket.**

If unsure about meaning, research it or use `SEMANTIC_UNRESOLVED`.

### SEARCH_ORIENTED

The concept is understood, but the natural discovery path is primarily its name/reference rather than a stable visual shelf.

Typical cases:
- named meme;
- named event;
- franchise-specific reference;
- idiosyncratic phrase.

Rules:
- no route IDs;
- no body/theme facets;
- route_vocabulary_gap = NO.

This is a legitimate positive result, not a failure.

### SEMANTIC_UNRESOLVED

After reasonable research, the identity's meaning still cannot be established confidently enough to choose visual discovery semantics.

Rules:
- no route IDs;
- no body/theme facets;
- route_vocabulary_gap = NO;
- review_depth = RESEARCHED;
- evidence_urls non-empty;
- uncertainty_note required.

Do not use this merely because route choice is difficult.

---

## 7. Route strength

### CORE

A central user mental model for finding the visual.

Question:

> このタグ名を知らない状態でも、その棚を最初に開くのが自然か？

### SUPPORTING

A real secondary discovery intent, but not one of the clearest starting points.

Do not mark SUPPORTING merely because the relationship is technically true.

### Route count

Normally:
- 1 CORE route; or
- 1 CORE + 1 SUPPORTING/second CORE.

A third route is exceptional and must represent another independent lookup intent.

When existing route vocabulary is sufficient and at least one route is selected, a browse-capable row must include at least one CORE route.

---

## 8. Route ordering

Order selected routes by discovery usefulness:

1. strongest CORE route;
2. next independently useful route;
3. optional third route.

Do not order alphabetically merely for convenience.

If two CORE routes are genuinely comparable, choose the more likely unknown-tag starting point first.

The order is research evidence only; it does not define a production primary taxonomy.

---

## 8.5. local_refinement_ids

JSON array of zero or more existing local refinement IDs defined by:

`docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md`

Rules:

- every selected local ID must belong to a selected top-level route in the same row;
- do not select a local merely because it is the current taxonomy assignment;
- zero local IDs is valid even when a top-level route is selected;
- normally use at most one local ID per selected parent route;
- local IDs are independent semantic audit output, not #132 production overlay authority.

If a natural local refinement is later found missing from current #64 behavior, that becomes `UPSTREAM_REVIEW`, not an automatic #132 runtime addition.

---

## 9. Body-site facets

`body_site_ids` may contain only:

- MALE_GENITAL
- BREAST_NIPPLE
- FEMALE_GENITAL
- MOUTH_ORAL
- BUTTOCK_ANAL
- URETHRA

Select a facet only when the body site is explicit/intrinsic to the tag concept.

Do not infer body site from a broad act that could involve different sites.

The array has no CORE/SUPPORTING distinction: inclusion already means the site is sufficiently central for refinement.

---

## 10. Theme facets

`theme_ids` may contain only:

- BDSM_RESTRAINT
- INJURY_R18G
- REPRO_PREGNANCY_LACTATION

Select only when the theme is intrinsic to the visual concept.

Do not use these as generic sexual-content labels.

---

## 11. route_vocabulary_gap

### NO

The existing 19 route vocabulary is sufficient to express the useful browse intent, or browse is not appropriate.

### YES

The meaning is understood and browse would be useful, but the existing 19 route IDs cannot represent an important user mental model without distortion.

Requirements:
- `route_vocabulary_gap_note` explains the missing axis in Japanese.
- Do not invent a new ID in the row.
- Use BROWSE_WORTHY or MIXED, not SEARCH_ORIENTED/SEMANTIC_UNRESOLVED.

A row may have:
- existing natural routes plus a vocabulary gap; or
- only a vocabulary gap if no existing route adequately represents it.

Repeated gaps are analyzed after the full population is complete.

---

## 12. review_depth

### CHECKED

Use when tag meaning and discovery intent are sufficiently clear from the neutral source surfaces and ordinary language/domain knowledge.

Evidence URLs may be `[]`.

### RESEARCHED

Use when external semantic verification was necessary.

Requirements:
- `evidence_urls` contains at least one URL actually used;
- semantic_summary_ja reflects the researched meaning.

Do not mark RESEARCHED merely because a search was opened but not relied upon.

---

## 13. evidence_urls

JSON array of URLs actually used for semantic verification.

Prefer:
1. Danbooru wiki/tag documentation;
2. official/reference source for named concepts;
3. reliable secondary source when necessary.

Do not record search-engine result URLs as evidence when a source page was available.

For CHECKED:
`[]` is valid.

---

## 14. uncertainty_note

Use only for meaningful residual uncertainty.

Required for:
- SEMANTIC_UNRESOLVED.

Useful for:
- a researched concept whose exact visual boundary remains ambiguous;
- multiple plausible readings not captured by route_vocabulary_gap.

Do not fill generic boilerplate on every row.

---

## 15. Validation

Validator:

`scripts/issue132/validate_luna_pass_a.py`

It checks:
- exact header;
- exact prefix order;
- no skips/duplicates;
- allowed modes/routes/facets;
- route field consistency;
- browse modes have usable browse semantics;
- SEARCH_ORIENTED / SEMANTIC_UNRESOLVED constraints;
- local-refinement IDs and parent-route consistency;
- RESEARCHED evidence;
- vocabulary-gap consistency.

During progress, always validate against the frozen contract manifest:

```
python scripts/issue132/validate_luna_pass_a.py \
  --input <neutral.csv> \
  --ledger docs/issue132/full_review/pass_a_independent_discovery.csv \
  --contract-manifest docs/issue132/full_review/pass_a_contract_manifest_v1.json \
  --summary <progress-summary.json>
```

At completion add:

`--require-complete`

---

## 15.5. Frozen Pass-A contract manifest

Before the first semantic row is written, generate/freeze:

`pass_a_contract_manifest_v1.json`

Builder:

`scripts/issue132/build_pass_a_contract_manifest.py`

The manifest pins:

- neutral authority/input SHA;
- deterministic identity order SHA;
- Pass-A contract document SHA-256 values;
- neutral generator SHA;
- manifest-builder SHA;
- validator SHA;
- exact ledger field order;
- route IDs;
- local-refinement vocabulary;
- body/theme vocabulary;
- allowed modes/strengths/depths.

Copy the frozen manifest into:

`docs/issue132/full_review/pass_a_contract_manifest_v1.json`

and commit it before/with the first ledger checkpoint.

Every subsequent validator run must use `--contract-manifest`.

If any frozen contract file or vocabulary has changed, validation must fail.

Do not silently continue a ledger under changed semantics.

If a material contract correction becomes necessary:

1. stop Pass A;
2. document the reason;
3. decide whether the full Pass A must be rerun under the corrected contract;
4. do not mix old-contract and new-contract rows in one accepted ledger.

Checkpoint commits may change the ledger/progress summary only; they do not redefine the semantic contract.

---

## 16. Persistence and restart

This is one continuous review, not semantic shards.

Operational rule:
- append completed rows in neutral order;
- validate before checkpoint;
- commit periodically;
- resume from `reviewed_count + 1`.

Checkpoint frequency is operational and may vary.

Do not ask the user for `continue` after each checkpoint.

Do not create semantic conclusions from checkpoint boundaries.

---

## 17. No runtime impact

The ledger, evidence URLs, semantic summaries, and route strengths are research-only.

Nothing in this schema is automatically loaded by the application.
