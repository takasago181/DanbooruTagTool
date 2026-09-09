# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2100
- Cumulative: PASS 1646 / FIX 174 / REVIEW 263 / IMAGE_TEST_REQUIRED 17
- Batch 1-21 R2 acceptance gates: PASS
- Batch 21: complete; integrity/false-PASS gate PASS
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2101
- Production/main modified: NO

## Batch 21 summary
Range 2001-2100: PASS 98 / FIX 0 / REVIEW 2 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2001_2020.csv`
- `results_blocks/2021_2040.csv`
- `results_blocks/2041_2060.csv`
- `results_blocks/2061_2080.csv`
- `results_blocks/2081_2100.csv`

A-risk REVIEW:
- 2029 `grabbing another's breast`: ActorRequirementOverride plausibly missing; exact row-specific independent evidence not attached.
- 2031 `guided breast grab`: analogous guided-grab precedent suggests ActorRequirementOverride=true, but exact row-specific independent evidence not attached.

A-risk PASS rows 2003, 2004, 2005, and 2028 received deep review. Camera/internal-view metadata remains structural only; no Stage10 camera tuning was promoted. Cooperative breast smother has internally consistent multi-actor/actor/spatial/separation structure and does not authorize support insertion.

R2 false-PASS audit sampled 20/98 PASS rows, including every A-risk PASS row in Batch21. New false-PASS: 0. Batch21 gate PASS. Details: `batch21_integrity_r2.md`.

Semantic-role rows remain search/support-only; alias rows preserve exact Special identity with canonical linkage statistics-only. `candidate_fixes.csv` and `revalidation_queue.csv` were checked and received no new entries. Semantic support remains 55/58.

## Exact restart
Resume first-pass at sequence 2101 (Batch 22). Checkpoint every 20. Do not modify production/main.
