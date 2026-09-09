# Issue #36 — FINAL CONVERGENCE V3.1 AGENT REVIEW

Status: **PROPOSED / PENDING ISSUE #45 SPEC RE-AUDIT / QUARANTINE ONLY**

This contract supersedes V2 execution behavior and the pre-review V3 contract `c445dce177d870b88bcacc5cdfce67c13fc40176` where they conflict. It is **not authoritative for execution until Issue #45 explicitly returns `APPROVE_V3_SPEC_FOR_EXECUTION` for this replacement commit**.

Its purpose is to end repeated one-row/rework loops by separating development-time semantic judgement, blinded challenge judgement, deterministic validation, and finite stop conditions.

The product runtime remains fully local/non-LLM. Codex/agent use here is development-time only; all approved results are frozen as repository artifacts before any later production-promotion task.

## 0. Authority / branch / immutable source

Read in order:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #36 latest comments, especially V2 audit `5600982011`
4. Issue #45 pre-execution audit `5601089974`
5. Issue #41 final `PASS_PILOT` checkpoint `5589825869` as methodology evidence only
6. this contract

Execution branch after #45 approval:
`ui-ja/issue36-final-agent-convergence`

V2 audited-but-failed result HEAD:
`8d88f3f83462ab4a1fd322afc84c061c919d4a8e`

Semantic source table for V3.1 is the **pre-V2 source**, never the V2 95%-fallback output:
`translation_quarantine/full_accepted_quality_sweep_20260909/final_translation_table.csv`

Immutable source identity:
- Git blob: `5fc11c64235c7b32cb72f2e819cb2ed22ab46d8a`
- required normalized row count: `30,629`
- required unique canonical count: `30,629`
- required source accepted: `23,194`
- required source fallback: `7,435`
- required source `PHRASE_SEMANTICS_UNRESOLVED`: `1,677`

Start gate MUST fetch the source by Git identity and verify the counts above. Do not rely only on raw working-tree byte hashes because line endings may differ.

Preserve V2 infrastructure lessons, but do not inherit V2 final row decisions merely because V2 gates said PASS.

Production promotion remains `NOT_AUTHORIZED` until a later fresh independent promotion-quality audit.

---

# 1. Product definition and anti-collapse rule

Japanese exists so the user can glance/search and understand canonical meaning while canonical English remains authoritative and final Prompt syntax remains canonical English.

Priority:
1. semantic correctness
2. real/readable Japanese
3. useful coverage
4. polish

Do not trade correctness for coverage. Equally, do not destroy useful coverage by treating lack of an exact phrase map as evidence that an ordinary concept is unresolved.

**Core anti-collapse rule**
A source-accepted row may be demoted only when a row-specific semantic/language defect or genuine unresolved ambiguity is recorded **and then confirmed by the mandatory blinded challenge population in §8**.

These are never sufficient demotion reasons:
- `NO_EXACT_MAP`
- `MULTIWORD`
- `NO_STATIC_TEMPLATE`
- `UNKNOWN_TO_SCRIPT`
- `NO_LEXICON_ENTRY`
- any equivalent statement that only describes implementation convenience.

The global 20-point coverage alarm in §11 is secondary. It is not a target and does not replace mandatory challenge of every source-accepted demotion.

---

# 2. Three-role architecture — semantic producer, blinded challenger, deterministic validator

V3.1 has three distinct roles.

## A. Resolver / translator agent
A Codex agent invocation reviews rows in bounded batches and writes frozen first-pass semantic decisions.

It may:
- `KEEP_JA`
- `REPAIR_JA`
- `TRANSLATE_JA`
- `TRUE_EXCEPTION`
- `EVIDENCE_UNRESOLVED`

Python may not substitute for this semantic work.

## B. Blinded challenger agent
The challenge is a **separate agent invocation/context** from the resolver. It must not receive the resolver's:
- `decision`
- `decision_rationale_ja`
- lane/state
- resolver confidence
- first-pass verdict labels
- unresolved classification

The challenger may receive only:
- canonical English identity
- candidate display Japanese, if any
- candidate search Japanese, if any
- immutable/frozen authoritative semantic evidence needed to judge the canonical
- source facts that are not self-generated first-pass conclusions
- explicit task/risk stratum required for challenge routing, without revealing the first-pass verdict

The challenger MUST NOT edit the row. It only judges.

If repair is required, a **separate resolver repair step** produces a new candidate, and that candidate is re-challenged in a **fresh blinded invocation**.

This follows the #41 principle: judgement is frozen before unmasking/scoring.

## C. Deterministic validator
Python may validate:
- source identity/counts
- schema/completeness
- typed provenance
- deterministic queue/sample membership
- language contamination/malformed/raw-token checks
- challenge coverage
- transition consistency
- replay of frozen decisions
- protected boundaries
- tests/gates

Python MUST NOT invent semantic decisions or use lack of a mapping/template as a semantic fallback reason.

---

# 3. Durable artifacts and invocation traceability

Root:
`translation_quarantine/final_agent_convergence_v3_20260909/`

Required:
- `source_manifest.json`
- `trusted_exact_provenance.jsonl`
- `review_queue.jsonl`
- `batch_progress.json`
- `agent_semantic_decisions/`
- `challenge_inputs/`
- `agent_challenge_decisions/`
- `repair_decisions/`
- `merged_agent_decisions.jsonl`
- `residual_fallback_sample.jsonl`
- `residual_fallback_challenge.jsonl`
- `collision_review.jsonl`
- `adversarial_sample.jsonl`
- `adversarial_agent_audit.jsonl`
- `defect_ledger.jsonl`
- `final_rows.jsonl`
- `final_translation_table.csv`
- `final_translation_table.md`
- `coverage_summary.json`
- `transition_summary.json`
- `language_quality_summary.json`
- `semantic_quality_summary.json`
- `exception_ledger.jsonl`
- `replay_verification.json`
- `protected_boundary.json`
- `gate_status.json`
- `FINAL_REPORT.md`

The queue covers all 30,629 canonicals exactly once.

Recommended batch size: 100–150. Persist each completed batch before moving on. The task is restartable from durable batch files.

For each resolver/challenger batch record:
- agent model/configuration when available
- invocation/run identifier
- contract commit
- immutable source identity
- batch input hash
- output hash
- timestamp if available

---

# 4. `TRUSTED_EXACT` is a narrow, auditable skip lane

`TRUSTED_EXACT` may skip first-pass agent semantic review **only** when all conditions below hold.

Allowed provenance sources are limited to exact-canonical, previously validated evidence from:
1. `translation_quarantine/qualified_label_final_review_20260909/**` under the qualified-label contract commit `60fc740a0c6463f9aeef40293bd006c0037493da`, but only rows whose durable verdict explicitly validates the exact canonical and exact Japanese wording;
2. Issue #41 frozen exact-canonical evidence associated with final `PASS_PILOT` checkpoint `5589825869`, only for exact overlapping canonical + exact validated wording;
3. explicit exact repairs that were independently audited in prior #36 checkpoints and can be tied to an exact artifact path/hash/verdict.

Not allowed for `TRUSTED_EXACT`:
- alias-only evidence
- fuzzy/related evidence
- token composition
- broad pattern/template output
- `JA_ACCEPT_*` state by itself
- a whole directory or prior table treated as trusted without per-row provenance

Every skipped row must have a `trusted_provenance` record containing:
- canonical
- exact validated Japanese wording
- artifact path
- Git commit and/or blob/hash
- originating verdict/checkpoint
- evidence state proving exact-canonical validation

The deterministic validator requires for every final accepted row either:
- a full agent first-pass record, or
- a valid `TRUSTED_EXACT` provenance record.

No row may be assigned `TRUSTED_EXACT` merely to reduce review volume.

---

# 5. Initial lanes

Every row gets exactly one provisional lane:

## `TRUSTED_EXACT`
Only §4-qualified exact provenance.

## `AGENT_REVIEW_KEEP_OR_REPAIR`
Source-accepted Japanese without §4 proof. Current Japanese is a candidate, never semantic authority.

## `AGENT_REVIEW_TRANSLATE_OR_FALLBACK`
Ordinary translatable source fallback, including all 1,677 phrase-unresolved rows and prior language/raw/malformed demotions where the canonical concept is understandable.

## `TRUE_ORIGINAL_FORM_EXCEPTION_CANDIDATE`
Name/product/code/symbol/title/opaque identity candidates. This is only a candidate lane; a terminal `TRUE_EXCEPTION` still requires blinded challenge.

No route/state alone can skip semantic review except valid `TRUSTED_EXACT`.

---

# 6. Resolver decision schema — display and search are separate artifacts

For each reviewed row persist at least:
- `canonical`
- `source_state`
- `source_display_ja`
- `source_search_ja`
- provisional lane
- `decision`: `KEEP_JA` / `REPAIR_JA` / `TRANSLATE_JA` / `TRUE_EXCEPTION` / `EVIDENCE_UNRESOLVED`
- `final_display_ja`
- `final_search_ja`
- **`display_verdict`**: `ACCEPT` / `ABSENT` / `UNRESOLVED`
- **`search_verdict`**: `ACCEPT` / `ABSENT` / `UNRESOLVED`
- `semantic_gloss_ja`
- `semantic_facets`
- `risk_class`
- `decision_rationale_ja`
- `evidence_refs` using typed provenance
- `attempted_evidence_routes`
- `unresolved_question_ja` when unresolved
- `review_mode = CODEX_AGENT_SEMANTIC_REVIEW`
- `batch_id`

Typed `evidence_refs` must use categories such as:
- `artifact_ref`
- `exact_canonical_source`
- `bridge_ref`
- `trusted_exact_provenance`
- `agent_ordinary_semantic_judgement`
- `domain_reference`

Free-form bookkeeping text is not evidence.

For unresolved rows:
- `attempted_evidence_routes` must be non-empty;
- `unresolved_question_ja` must describe the actual unresolved semantic question;
- lack of an exact map/template is invalid.

The validator must flag suspicious mass templating: repeated/near-identical rationale or evidence text across large unrelated classes is an audit defect, not proof of row-specific review.

Semantic facets when applicable:
- head concept
- action/state
- actor
- ownership
- target
- body site
- direction/spatial relation
- count/cardinality
- negation
- required modifier
- qualifier scope
- concept width

### Display vs search rule
A valid display does not certify search.

A row may finish with:
- valid display + conservative identical exact-safe search;
- valid display + absent search if no exact-safe Japanese search term exists;
- both valid;
- both absent only for a valid exception/unresolved fallback.

Do not add broad search synonyms merely to increase recall.

---

# 7. Resolver review rules

### Source-accepted rows
Do not demote merely for missing external proof. KEEP is allowed when the agent can semantically determine that current Japanese preserves canonical meaning.

Demote only for:
- actual meaning mismatch
- scope loss/expansion
- Chinese/non-Japanese
- raw semantic English leakage
- malformed display/search
- material unresolved ambiguity

Every source-accepted demotion enters mandatory blinded challenge under §8.

### Source fallback rows
For ordinary concepts, actually translate when whole-canonical meaning is clear from ordinary language/domain knowledge and semantic structure.

External evidence is useful for ambiguous/specialized cases but is not mandatory for every ordinary concept.

### 1,677 phrase rows
Every row receives a resolver decision. `EVIDENCE_UNRESOLVED` is allowed only for genuine ambiguity with typed attempted evidence and a specific Japanese unresolved question.

### TRUE_EXCEPTION
Original form is terminal only when identity would be harmed or Japanese translation is genuinely unnecessary. Every `TRUE_EXCEPTION` receives 100% blinded challenge.

---

# 8. Mandatory blinded challenge populations

After first-pass decisions are frozen, create blinded challenge inputs and run them in a separate agent invocation/context.

**100% challenge is mandatory for:**
1. every source-accepted row demoted to fallback/exception;
2. every `EVIDENCE_UNRESOLVED` row, regardless of source/lane;
3. every `TRUE_EXCEPTION` row;
4. every HIGH/CRITICAL accepted row;
5. every `REPAIR_JA` row;
6. every `TRANSLATE_JA` row;
7. every collision/sibling candidate.

In addition, challenge a deterministic 10% sample of remaining ordinary `KEEP_JA` rows not already covered above.

Challenge output has **separate display/search judgements**:
- `display_challenge`: `CONFIRM` / `REPAIR_REQUIRED` / `FALLBACK_REQUIRED` / `RESOLVABLE_FALLBACK`
- `search_challenge`: `CONFIRM` / `REMOVE_SEARCH` / `REPAIR_REQUIRED` / `RESOLVABLE_FALLBACK`
- row-level rationale in Japanese
- semantic facet comparison

The challenger cannot edit the candidate.

Repair flow:
1. challenger freezes verdict;
2. a separate resolver repair invocation receives the failure;
3. repaired candidate is frozen;
4. a fresh blinded challenger invocation re-judges it.

No same-context self-repair/self-confirm cycle is accepted as independence.

---

# 9. Deterministic sampling — seed/selection frozen before semantic outcomes

Use this universal ranking key for deterministic samples:

`sample_key = SHA256(source_git_blob + "|" + sample_purpose + "|" + canonical)`

where `source_git_blob = 5fc11c64235c7b32cb72f2e819cb2ed22ab46d8a`.

Within each required stratum, sort ascending by `sample_key` and take the requested count. The algorithm/seed is therefore frozen before first-pass outcomes.

Persist the canonical selection list before each challenge judgement begins.

### Residual fallback sample
After all 100%-challenge populations in §8 are accounted for, select **at least 300 additional unchanged/legacy residual ordinary fallback rows** (or all if fewer) with explicit strata. Do not mix `TRUE_EXCEPTION` into these ordinary-fallback quotas.

Required residual strata, with deterministic redistribution only when a stratum lacks enough rows:
- 60 random ordinary residual fallback
- 50 common/simple ordinary concepts
- 50 multi-token phrases
- 40 action/relation rows
- 40 anatomy/adult/high-risk rows
- 30 source-accepted demotion siblings/root-cause neighbors not already challenged
- 30 previous `PHRASE_SEMANTICS_UNRESOLVED` residuals not already in a 100% population

If categories overlap, a canonical may satisfy multiple force-inclusion labels but counts once in the base 300; fill shortages with the next-ranked ordinary residual fallback.

### Final adversarial sample
Minimum **600 base rows**, historical blockers added on top if not already selected:
- 150 random accepted
- 150 HIGH/CRITICAL accepted
- 150 repaired/new translations
- 100 residual ordinary fallback
- 50 TRUE_EXCEPTION

If a category contains fewer rows, deterministically redistribute its deficit to the most relevant adjacent category while preserving at least one row from every non-empty category.

Display and search are judged separately.

---

# 10. Residual fallback anti-collapse challenge

For the §9 residual ordinary fallback sample, run a separate blinded challenger whose sole question is:

`Can this canonical be translated safely enough for glance-understanding without inventing meaning?`

Output:
- `TRULY_UNRESOLVED`
- `RESOLVABLE`

with a fresh Japanese rationale and semantic facets.

Any `RESOLVABLE` result is processed under the finite defect rules in §13. No ordinary residual fallback may be called safe merely because prior resolver/challenger states said fallback.

---

# 11. Coverage utility gate

Required report:
- source accepted 23,194
- source fallback 7,435
- kept accepted
- repaired accepted
- source-accepted demotions by concrete root-cause bucket
- translated source fallback
- true exceptions
- evidence-unresolved residual
- accepted/fallback rates by useful risk/common/rare strata when derivable

If final accepted coverage falls by more than **20 percentage points** from the source 23,194 / 30,629 level, terminal success is blocked as `HOLD_COVERAGE_COLLAPSE` unless the full §8 challenge evidence demonstrates the demotions are genuinely necessary.

This is an alarm, not a target. Passing it does not excuse unnecessary demotions.

---

# 12. Collision / sibling review

Duplicate Japanese is not automatically invalid.

Every collision candidate receives mandatory blinded challenge and records whether:
- duplicate is semantically legitimate;
- labels need differentiation;
- one/both are mistranslated;
- search scope is broader than display semantics.

Ownership/count/direction/action-state/body-site distinctions must be preserved.

---

# 13. Finite stopping rule — no infinite repair loop

Every defect must be assigned one machine-readable root-cause bucket, at minimum:
- `LANGUAGE_CONTAMINATION`
- `RAW_ENGLISH_LEAK`
- `MALFORMED_LABEL`
- `POLYSEMY_ACTION_STATE`
- `ACTOR_TARGET_OWNERSHIP`
- `BODY_SITE_RELATION`
- `DIRECTION_SPATIAL`
- `COUNT_CARDINALITY`
- `NEGATION_QUALIFIER_SCOPE`
- `SIBLING_COLLISION`
- `SEARCH_SCOPE_OVERREACH`
- `UNNECESSARY_FALLBACK`
- `TRUE_EXCEPTION_MISCLASSIFIED`
- `EVIDENCE_GAP`
- `VALIDATOR_OR_GATE_BYPASS`
- `OTHER_ROW_SPECIFIC`

### Isolated defect
A defect is isolated only when:
- the root cause is row-specific; and
- targeted sibling/root-cause neighbor recheck finds no second affected row/pattern; and
- there is no validator/gate bypass.

Action:
- correct that row;
- deterministically recheck at least 20 nearest/root-cause siblings when available;
- do not restart the architecture or whole 30,629 rows.

### Systemic/structural defect
Systemic if any of:
- same root-cause bucket reproduces in 2+ independently selected rows in a challenge/audit sample;
- validator/gate can pass an invalid class;
- a reusable resolver/reviewer rule is wrong;
- a class-wide transition pattern is demonstrably affected.

Action:
- define deterministic affected-class membership before repair;
- repair/re-review the full class;
- rerun only required downstream gates/samples.

### Maximum cycles
Maximum **2 full repair/challenge cycles per row or deterministic affected class**.

After two unsuccessful cycles:
- unresolved semantic disagreement -> `BLOCKED_AGENT_DISAGREEMENT`;
- validator/architecture/systemic convergence failure -> `BLOCKED_STRUCTURAL_DEFECT`;
- genuinely unavailable external exact-canonical evidence for a finite enumerated set -> `HOLD_EXTERNAL_EVIDENCE`.

These are safe non-success stop states. Codex MUST stop and report them; it must not loop indefinitely.

`HOLD_EXTERNAL_EVIDENCE` cannot be used for ordinary internal disagreement or to hide unprocessed work.

---

# 14. Final adversarial AGENT audit

After final rows are frozen, create the deterministic §9 600-row sample and run a fresh agent semantic audit, not deterministic verifier reuse and not the resolver's original context.

For each row record:
- canonical
- final display Japanese/fallback
- final search Japanese/absent
- fresh semantic judgement
- `display_audit`: `PASS` / `REPAIR_REQUIRED` / `RESOLVABLE_FALLBACK`
- `search_audit`: `PASS` / `REPAIR_REQUIRED` / `REMOVE_SEARCH` / `RESOLVABLE_FALLBACK`
- Japanese rationale
- root-cause bucket on failure

Historical #36 blockers are force-included in addition to the base sample when necessary.

Failures follow §13. Do not patch a sampled row and regenerate indefinitely.

Terminal success requires zero unresolved `REPAIR_REQUIRED` / `RESOLVABLE_FALLBACK` and no unsafe search verdict in the final audited population.

---

# 15. Historical regressions

Carry forward all historical #36 fixtures/classes, including:
- fake Japanese wrappers
- raw English hidden in Japanese
- Chinese/non-Japanese accepted text
- noun/verb and action/state polysemy
- actor/target/ownership/body-site loss
- direction/count/negation/qualifier loss
- arbitrary per-token multiword composition
- malformed labels
- wrong sibling/adjacent concept
- unnecessary mass fallback
- verifier self-certification

Known exact repairs must remain exact unless a documented semantic correction supersedes them. Tests may not weaken them to “Japanese OR fallback is acceptable.”

---

# 16. Deterministic validator requirements

Validators enforce at minimum:
- immutable source blob/count/split
- 30,629 unique canonical rows
- canonical identity/order unchanged
- all queue rows have terminal first-pass or valid `TRUSTED_EXACT` provenance
- no generic REVIEW/PENDING in successful output
- language/malformed/raw-token controls
- typed provenance schema
- row-specific unresolved evidence/question
- mass-template rationale heuristic/escalation
- all §8 mandatory challenge populations complete
- blinded challenge inputs contain no forbidden resolver-state leakage
- separate display/search challenge verdicts
- deterministic sample memberships match §9
- no invalid fallback convenience reason
- final transition consistency
- finite cycle counts <=2 per row/class
- replay PASS from frozen decisions
- protected boundary PASS
- production modified NO

Python cannot decide that a Japanese candidate is semantically correct merely because these structural gates pass.

---

# 17. Final gates and terminal states

`gate_status.json` must include at least:
1. `source_identity_pass`
2. `row_count_30629_unique`
3. `canonical_identity_unchanged`
4. `review_queue_complete`
5. `trusted_exact_provenance_valid`
6. `agent_first_pass_or_trusted_complete`
7. `blinded_challenge_input_leakage_zero`
8. `mandatory_challenge_populations_complete`
9. `display_challenge_failures_zero`
10. `search_challenge_failures_zero`
11. `phrase_1677_agent_review_complete`
12. `fallback_reason_specificity_pass`
13. `residual_fallback_stratified_challenge_pass`
14. `coverage_anti_collapse_pass`
15. `collision_agent_review_pass`
16. `adversarial_agent_audit_600_pass`
17. `historical_regressions_pass`
18. `repair_cycle_bound_pass`
19. `deterministic_replay_pass`
20. `protected_boundary_pass`
21. `production_modified_no`
22. `focused_regression_tests_reported`
23. `full_pytest_reported_accurately`

### Success terminal
Only:
- `FINAL_READY_FOR_INDEPENDENT_AUDIT`

### Safe non-success terminals
- `HOLD_EXTERNAL_EVIDENCE`
- `HOLD_COVERAGE_COLLAPSE`
- `BLOCKED_AGENT_DISAGREEMENT`
- `BLOCKED_STRUCTURAL_DEFECT`

Non-success terminals are **not completion** and never authorize production promotion, but they are valid finite stop conditions and prevent endless loops.

Forbidden labels:
- `PARTIAL_DONE`
- `HOMEWORK_RETAINED`
- `SAFE_FOR_NOW`
- equivalent ambiguous “done” wording.

---

# 18. Tests

Tests validate the contract, not a convenient output distribution.

Forbidden tests:
- hardcoding a large expected fallback count because current resolver produces it;
- treating fallback as equivalent to accepted product quality;
- allowing known exact repairs to become fallback without documented superseding correction;
- testing challenger independence only by function name while using same unblinded context.

Required:
- immutable source identity/count checks
- trusted-provenance validation tests
- blind-input leakage tests
- 100% challenge population completeness tests
- display/search separation tests
- invalid convenience-fallback reasons rejected
- typed evidence tests
- repeated-template evidence escalation test
- deterministic stratified sampling tests
- finite repair-cycle/terminal-state tests
- residual fallback challenge
- coverage anti-collapse alarm
- language/malformed/raw-token controls
- semantic facet preservation fixtures
- collision/sibling behavior
- historical exact repairs/classes
- replay/protected boundary
- full pytest accounting

Full pytest reporting rule remains: known Windows TEMP ACL/setup/finalize errors must be reported exactly and must not be called an overall PASS. Product/assertion failures block success.

---

# 19. Scope / authority boundaries

Allowed:
- `translation_quarantine/**`
- tests directly required for #36 V3.1

Forbidden:
- production `data/**`
- `data/runtime/japanese_overlay.json`
- canonical English identity changes
- Prompt/cooccur/recommendation behavior changes
- semantic-support production changes
- generation metadata changes
- #32 data/verdict writes
- #35 UI changes
- #41 writes/reopen
- `docs/project/CURRENT_DEV_TASK.md`
- main merge
- Stage10 production A/B

Japanese wording remains UI/search assistance and never certifies canonical/source/generation semantics.

---

# 20. Governance and execution authorization

Until Issue #45 re-reviews **this exact replacement commit** and returns `APPROVE_V3_SPEC_FOR_EXECUTION`:
- do not run V3.1 as authoritative;
- do not post a Codex execution handoff;
- do not mark the contract authoritative.

After #45 approval:
1. update the contract status in a minimal governance-only commit to `AUTHORITATIVE EXECUTION CONTRACT FOR CODEX / QUARANTINE ONLY` without changing semantic requirements;
2. post the exact approved contract commit/status to Issue #36;
3. then run Codex once against that approved specification.

Any semantic/spec change after approval invalidates the approval and requires #45 delta re-review. Governance-only status/hash bookkeeping that does not alter requirements does not require a full new review; record it transparently.

---

# 21. Completion report

At any terminal, report:
- execution start HEAD
- final HEAD
- source blob/counts
- all transition counts
- trusted-exact count/provenance sources
- first-pass reviewed count
- mandatory blinded challenge counts by population
- phrase 1,677 outcomes
- residual fallback sample strata/outcomes
- final accepted/fallback counts/percentages
- coverage delta vs source
- demotion root-cause buckets
- translated prior-fallback count
- display/search challenge outcomes separately
- collision results
- adversarial 600 outcomes separately for display/search
- repair cycles and any blocked classes
- historical regressions
- replay/protected verdicts
- focused/full pytest accounting
- `production_modified: NO`
- `promotion: NOT_AUTHORIZED`

Fresh independent ChatGPT promotion-quality audit remains mandatory after `FINAL_READY_FOR_INDEPENDENT_AUDIT` and before any production promotion.
