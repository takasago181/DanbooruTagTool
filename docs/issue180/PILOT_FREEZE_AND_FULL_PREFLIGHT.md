# Issue #180 — Pilot freeze and full-population preflight

Status: RESEARCH / NO MERGE / NO PRODUCTION APPLY

## Correct final pilot accounting

Artifact from workflow run 35621333428 (head `dee09c68c080c864269b1165b36d9a78ee0ac54b`) is authoritative:

- total: 250
- AUTO_CONFIRM_CANDIDATE: **205**
- NEEDS_AUTHORITY_REVIEW: **45**
- unexplained rows: **0**

Authority distribution:
- QUALIFIER_COPYRIGHT: 181
- CURATED_COPYRIGHT_LIST: 15
- CURATED_COPYRIGHT_LIST+ROOT_NORMALIZATION: 9
- NO_ACCEPTED_HOME_AUTHORITY: 31
- QUALIFIER_ALIAS_UNVERIFIED: 14

The earlier 194/45 report was a counting/reporting error. The 11-row discrepancy does not exist in the artifact; those rows are AUTO_CONFIRM_CANDIDATE. This document supersedes the earlier count.

Pilot mechanical coverage: **82.0%** (205/250). This is candidate coverage, not a claim that 82% of all Character rows can be safely confirmed.

## Expansion gates

Before applying the classifier to all 35,890 Character source rows:

1. preserve source rows and old RelatedCopyright only as provenance/sampling;
2. run qualifier extraction over the full population with no relation mutation;
3. count approved qualifier roots, unknown qualifiers, and unqualified rows;
4. detect qualifier-to-root conflicts and fail closed;
5. reuse only exact reviewed curated decisions and approved mappings;
6. emit candidates to a research artifact only;
7. sample each auto-confirm authority family plus long-tail/unknown controls;
8. do not merge or production-apply until semantic review passes.

## Stop rule

Full-population preflight may generate a census and candidate artifact. It must not write accepted relation data, main, or production runtime.
