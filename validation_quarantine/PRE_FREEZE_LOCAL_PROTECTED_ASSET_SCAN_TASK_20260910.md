# Issue #32 — local protected-asset completeness scan task

Purpose: close the one remaining evidence gap in pre-freeze Special completeness reconciliation.

This is a DATA/AUDIT-support task. It MUST run in a local workspace that can see protected/ignored project assets. GitHub Issue comments alone are not an executable contract; this tracked file is the task contract.

## Hard boundaries

- Do not modify production `data/**`.
- Do not delete, clean, regenerate, or normalize ignored/protected data.
- Never run `git clean -fdx`, `git clean -fdX`, or equivalent destructive cleanup.
- Do not change the completed 2,788 audit order/verdict history.
- Do not promote auxiliary/search-only/general tags to Special merely because they exist.
- Do not use Japanese wording as semantic authority.
- Do not use model-generation response as sole proof of Special identity.

## Inputs to inventory

Compare the frozen 2,788 Special identity set against every locally available asset in these categories:

1. historical/additional Special candidate lists or scratch/final candidate exports;
2. canonical / Alias / Semantic dictionaries and overlays;
3. local runtime/search indexes that retain candidate identity provenance;
4. local support/recommendation assets that may name an independently sourced Special identity;
5. missing-word / added-word / supplemental-word outputs from prior stages;
6. retained protected raw/derived Special source assets;
7. any local manifest/handoff that explicitly marks a term as a pending Special addition.

Record the actual paths discovered. Do not assume a path exists from historical documentation.

## Comparison rule

Normalize only for comparison mechanics (e.g. whitespace/underscore/case where the existing project normalization contract permits it). Preserve original terms and provenance in the report.

For every out-of-set term, classify exactly one:

- `NOT_SPECIAL_AUXILIARY`
- `NOT_SPECIAL_ALIAS_OF_EXISTING`
- `NOT_SPECIAL_SEARCH_ONLY`
- `NOT_SPECIAL_GENERAL_TAG`
- `NOT_SPECIAL_DUPLICATE_NORMALIZATION`
- `SPECIAL_CANDIDATE_NEEDS_EVIDENCE`
- `GENUINE_MISSING_SPECIAL`

A `GENUINE_MISSING_SPECIAL` requires independent evidence that the term is a first-class Special identity intended for the product's Special Core set, not merely a useful generation/support/search tag.

## Required evidence for a genuine missing Special

At minimum record:
- exact original term;
- normalized comparison key;
- local source path + source record identity;
- why it is not an alias/auxiliary/general/search-only term;
- independent semantic/source authority;
- relationship to any existing Special;
- applicable actor/target/body-site/relation/qualifier semantics;
- risk priority under #32;
- whether any generation behavior remains model-scoped/HOLD.

Do not infer generation reliability from semantic membership.

## Required output

Create a quarantine-only report, preferably:
`validation_quarantine/PRE_FREEZE_LOCAL_PROTECTED_ASSET_SCAN_RESULT_20260910.md`

Include:
- workspace/repo commit identity used;
- discovered local asset inventory (paths + counts/hashes where practical);
- frozen Special set identity/blob;
- number of unique out-of-set terms examined;
- classification counts;
- exact genuine missing-Special candidates, if any;
- unresolved inventory gaps, if any;
- confirmation production `data/**` unchanged.

Final enum must be exactly one:
- `LOCAL_COMPLETENESS_PASS_MISSING_0`
- `LOCAL_COMPLETENESS_DELTA_FOUND`
- `LOCAL_COMPLETENESS_BLOCKED_INVENTORY_UNKNOWN`

### If PASS_MISSING_0
No additional first-pass work is needed. Return the result to Issue #32 so completeness can be closed and final promotion audit can begin.

### If DELTA_FOUND
Do not edit production. Create a separate delta ledger and validate only those missing Specials under the applicable #32 R2 rules. The completed 2,788 results remain valid.

### If BLOCKED
List exactly which local asset category/path cannot be inventoried and why. Do not substitute an assumption of zero.
