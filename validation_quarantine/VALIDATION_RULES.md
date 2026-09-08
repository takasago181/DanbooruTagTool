# Validation Rules

Active rule version: R1
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
