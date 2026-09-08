# Validation Rules

Active rule version: R2
Issue: #32

## R1 — Initial full-audit rules

### Product-direction guardrails
1. Special2788 remains first-class generation identity.
2. Support may clarify or stabilize a Special but must not silently replace/generalize it.
3. Statistical common/rare/co-occurrence evidence and semantic support are separate lanes.
4. Model-family-specific findings must not become global truth without evidence.
5. Stage10 HOLD items remain unresolved until controlled image evidence exists.
6. Existing production data is read-only during this audit.

### Missing-data interpretation
- Blank/None is not automatically an error.
- UNKNOWN / NOT ASSERTED is valid where current schema uses tri-state semantics.
- PROVISIONAL / REVIEW_REQUIRED rows must not be filled merely for completeness.

### Evidence order
Prefer independent evidence in this order:
1. Special identity/meaning authority
2. current KNOWLEDGE evidence / exact model-family sources when relevant
3. PROMPT evidence / controlled generation observations
4. production metadata under test

Do not validate an assertion solely by citing the artifact that originally generated the same assertion.

### Validation states
- PASS: current asserted metadata is acceptable under available evidence.
- FIX: concrete correction is supported by adequate evidence.
- REVIEW: unresolved, conflicting, or insufficient evidence.
- IMAGE_TEST_REQUIRED: image-generation behavior cannot be safely decided statically.

### Risk priority
S:
- Special meaning/identity implication error
- materially wrong GenerationFamily / GenerationRole / PromptUseMode
- wrong `CORE_SUPPORT + ADDITIVE`

A:
- Actor/Bodypart/Implement/Pose/Camera/SpatialAssignment requirements
- support slot/class/combination mode
- SpecialFlags / RecommendedHandling

B:
- OPTIONAL_VARIATION
- priority
- confidence/evidence wording
- Japanese explanatory quality

C:
- intentional blanks
- formatting
- non-execution metadata

### Semantic support rules
- `CORE_SUPPORT + ADDITIVE` receives mandatory deep review because current Composer may default-select it.
- ALTERNATIVE and CONTEXTUAL must not be promoted to automatic inclusion without explicit support for that behavior.
- OPTIONAL_VARIATION is not a required meaning component merely because it helps a prompt.
- Candidate canonical validity is necessary but not sufficient for semantic correctness.

### Generation-profile rules
- Requirement metadata describes structural need; it is not itself an instruction to inject a support tag.
- Preserve `AllowsAutomaticExpansion=False` semantics unless a future separately approved production decision changes it.
- Model observations do not rewrite static model-independent metadata automatically.

### Statistical lanes
- A statistically surprising common/rare result is not automatically a semantic error.
- Never rewrite semantic support to make it resemble co-occurrence ranking, or vice versa.

### Batch process
1. Load fixed deterministic Special order.
2. Validate 100 Specials per batch.
3. Internally checkpoint every 20.
4. Run static integrity checks.
5. Fast-screen all 100.
6. Deep-review S/A risk and all non-PASS rows.
7. Sample PASS rows for false-PASS audit.
8. Cross-check related rows for inconsistent classification.
9. Persist results and progress before continuing.

### Rule changes
If R1 is changed:
- create R2 rather than silently editing historical interpretation;
- document what changed and why;
- identify affected previously validated rows;
- add them to `revalidation_queue.csv`;
- never pretend all older PASS results used the new rule.

### Chat migration
Before moving chats:
- update `progress.json`;
- update `handoff.md`;
- persist unresolved findings and revalidation queue;
- record next exact batch/start position.

New chat must read these files and Issue #32 before validation resumes.

## R2 — Full sidecar coverage, generation-evidence cross-check, and false-PASS control

R1 remains historical and unchanged.
R2 becomes active after sequence 40. Sequences 1-40 retain their R1 Special-level results and enter R2 backfill where required.

### Change reason
R1 prioritised high-risk semantic support, especially `CORE_SUPPORT + ADDITIVE`, but did not explicitly require row-complete coverage of every semantic support record, did not define numeric false-PASS escalation thresholds, and did not explicitly force generation-oriented evidence cross-checks for high-impact rows.

R2 closes those gaps without rewriting historical R1 results.

### Generation-evidence cross-check gate
The following cases must not be marked `PASS` based only on production metadata, family rules, or prompt-reference text:

- S/A priority findings
- `CORE_SUPPORT + ADDITIVE`
- any default-on / automatic inclusion effect
- model-family-sensitive behavior
- camera / pose / visibility / geometry support
- unusual anatomy or anatomy-negative interaction
- broad + specific support combinations
- canonical / Alias / Semantic rows whose generation impact is under review
- multiple-Special interaction support
- LoRA interaction, prompt-density, or other generation-behavior claims

For these cases, cross-check relevant `STAGE_10_KNOWLEDGE_HANDOFF` material and PROMPT evidence/controlled observations when available. Preserve exact model-family scope. Knowledge/PROMPT material remains evidence, not automatic production truth.

If sufficient independent evidence does not exist:
- use `REVIEW` when evidence is insufficient or conflicting;
- use `IMAGE_TEST_REQUIRED` when controlled image comparison is required.

Do not let a production artifact and rules derived from that same artifact self-certify generation correctness.

### Semantic support full coverage
1. Every row in the frozen `data/semantic/semantic_support_profiles.csv` snapshot must receive an audit record.
2. `CORE_SUPPORT + ADDITIVE` remains mandatory deep review.
3. ALTERNATIVE / CONTEXTUAL / OPTIONAL_VARIATION and all other support rows receive at least static screening.
4. Any row with semantic ambiguity, structural conflict, high-risk execution effect, insufficient evidence, or uncertain generation value receives deep review.
5. Image-dependent questions are classified `IMAGE_TEST_REQUIRED`, not guessed.
6. Row-complete results are stored separately from Special-level results in `semantic_support_results.csv`.
7. Completion requires exact reconciliation between the frozen snapshot row count and audited support-row count.
8. Orphan rows, unknown Special IDs, unknown candidate canonicals, duplicates, and conflicting rows are still part of coverage and must receive an explicit recorded verdict.
9. `REVIEW` / `IMAGE_TEST_REQUIRED` count as audited-but-unresolved only when the row, reason, and evidence trail are recorded.

### Support-row audit identity
Each audited semantic-support record must preserve enough identity to map uniquely back to the frozen input row. Required ledger fields:

- source_row
- special_id
- special_tag
- candidate_canonical
- support_class
- combination_mode
- rule_version
- risk_priority
- verdict
- problem_fields
- reason
- evidence_refs
- needs_deep_review
- image_test_required
- revalidation_status
- notes

### False-PASS sampling
For every completed 100-Special batch:

- sample 20% of PASS rows;
- minimum 10, maximum 20;
- use deterministic/reproducible sampling;
- stratify across risk/family/support categories where practical;
- include S/A PASS rows preferentially when present.

#### Escalation rules
**0 false-PASS**
- batch sampling gate PASS; continue.

**Exactly 1 false-PASS and B/C priority only**
- expand the sample up to 40 PASS rows;
- record root cause;
- add all plausibly affected prior rows to `revalidation_queue.csv`;
- proceed only if the expanded sample finds no further false-PASS and the cause is demonstrated to be local.

**2 or more false-PASS**
- batch sampling gate FAIL;
- do not continue to the next external batch until root cause is identified;
- revalidate the full current 100-Special batch under the applicable rule.

**Any S/A false-PASS**
- batch sampling gate FAIL regardless of count;
- do not continue to the next external batch until root cause is identified;
- revalidate the full current 100-Special batch.

### Systemic-error rule
If the same false-PASS root cause appears across multiple batches, treat it as systemic regardless of apparent overall error rate.

Retroactively revalidate all previously PASS rows matching the affected pattern, including by:
- field
- GenerationFamily
- support_class
- combination_mode
- model-family scope
- Special subtype / semantic pattern

If interpretation changes are required, create a new rule version (R3, etc.) rather than silently editing R2.

### R1 backfill
Sequences 1-40 were validated before R2 activation.

Add them to the revalidation queue for:
1. semantic-support row-complete coverage where associated support rows exist;
2. generation-evidence cross-check where R2 says it is mandatory.

This does not automatically invalidate their existing R1 Special-level verdicts. It closes the additional R2 coverage/evidence obligations only.

### Promotion gate
No production promotion until all of the following are true:

1. `special2788_generation_profile.csv`: 2,788 / 2,788 Special coverage
2. frozen `semantic_support_profiles.csv`: every input row explicitly covered in `semantic_support_results.csv`
3. revalidation queue resolved or explicitly parked with evidence as `REVIEW` / `IMAGE_TEST_REQUIRED`
4. false-PASS gates satisfied
5. candidate fixes cross-consistency checked
6. separate final promotion audit PASS

### Chat migration under R2
Before moving chats, persist both Special-level progress and semantic-support row coverage. A new chat must read Issue #32, this rule file, `progress.json`, `semantic_support_results.csv`, `revalidation_queue.csv`, and `handoff.md` before resuming.
