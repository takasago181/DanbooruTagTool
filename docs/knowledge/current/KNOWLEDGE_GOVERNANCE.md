# KNOWLEDGE Governance — Claim-Level Current Rules

Owner: Issue #44 `KNOWLEDGE:#44`

## 1. Current verdict source of truth

`CLAIM_REGISTRY.csv` is the KNOWLEDGE lane's claim-level current verdict source of truth.

The registry answers:
- what the claim currently says;
- what kind of evidence supports it;
- whether it is accepted/candidate/hold/conflict/rejected/historical;
- exactly where it applies;
- whether revalidation is required;
- where the evidence lives;
- which downstream lane may consume it.

Readable category files explain the claims. Research files preserve proof/history. Neither silently overrides the Registry.

## 2. Claim ID rule

Stable form:
`K-<DOMAIN>-<NNN>`

Current domains include:
- `GOV`
- `MODEL-WAI`
- `MODEL-ILL`
- `MODEL-NOOB`
- `MODEL-ANIMA`
- `SEM`
- `PROMPT`
- `SUPPORT`
- `BIND`
- `HARD`
- `NEG`
- `QUALITY`
- `TOOL`
- `LORA`
- `EVAL`
- `EVID`
- `SOURCE`
- `HIST`
- `REJECT`

IDs are never recycled. A changed claim is updated in place when meaning remains the same; a materially different claim receives a new ID and uses `supersedes/contradicted_by`.

## 3. Required registry columns

1. `ID`
2. `Claim`
3. `SOURCE_CLASS`
4. `STATUS`
5. `SCOPE`
6. `VALIDATION_STATE`
7. `source/evidence`
8. `last_checked`
9. `supersedes/contradicted_by`
10. `downstream_relevance`

These columns are fixed so the CSV can later be converted to JSON/YAML without changing semantics.

## 4. SOURCE_CLASS — what kind of evidence is this?

Allowed current values:

- `OFFICIAL_MODEL` — official model facts such as architecture/training/caption capability
- `AUTHOR_GUIDE` — author-recommended inference/prompt usage or examples
- `OFFICIAL_RUNTIME` — official runtime/extension behavior
- `SEMANTIC_AUTHORITY` — canonical semantic/alias/implication authority
- `PROJECT_FACT` — a project-owned rule, baseline, verified state, or adopted methodology
- `CONTROLLED_PRACTICAL` — controlled practical comparison
- `RESEARCH` — primary/general research evidence
- `COMMUNITY` — community/practical observation, useful for discovery but lower authority
- `LEGACY` — preserved historical framing or superseded assumption

`SOURCE_CLASS` does **not** say whether the project adopts the conclusion.

## 5. STATUS — how should the claim be treated now?

- `ACCEPTED` — current KNOWLEDGE verdict; may still be exact-scope only
- `CANDIDATE` — plausible/useful but not yet strong enough for current-rule treatment
- `HOLD` — unresolved; do not choose a side
- `CONFLICT` — credible evidence currently disagrees after scope/version separation
- `REJECTED` — explicitly not accepted as a current rule/default
- `HISTORICAL` — preserved for context; not current guidance

Official evidence can still be `CANDIDATE` if the *interpretation* goes beyond what the source establishes.

Example:
- “WAI v17 author recommends Steps 15–30” -> `AUTHOR_GUIDE / ACCEPTED`
- “Steps 25 is optimal for hard targets” -> would require a separate `PROJECT_FACT` or `CONTROLLED_PRACTICAL` claim and remains `CANDIDATE/HOLD` until demonstrated
- “25 steps is the current isolation baseline” -> `PROJECT_FACT / ACCEPTED`, but it is not an optimum claim

## 6. SCOPE — where can the claim be applied?

Use one or more semicolon-separated scope tokens.

Core forms:
- `GLOBAL_PRINCIPLE`
- `FAMILY:<name>`
- `MODEL_VERSION:<name>`
- `PROFILE:<name>`
- `RUNTIME:<name>`
- `EVALUATOR:<name>`
- `PROJECT_ONLY`

Never drop scope when copying a claim to a downstream handoff.

## 7. VALIDATION_STATE — what validation is still needed?

- `NOT_REQUIRED` — no local validation required for the stated narrow fact/principle
- `LOCAL_RECHECK` — verify local installation/config/hash when environment changes
- `CONTROLLED_TEST_REQUIRED` — generation-effect claim needs controlled test
- `STAGE10_REQUIRED` — specifically unresolved for Stage10 representative evaluation
- `SOURCE_RECHECK_REQUIRED` — source/version can change and should be rechecked before promotion-critical use

A claim can be `ACCEPTED` and still have `SOURCE_RECHECK_REQUIRED` because freshness is separate from current interpretation.

## 8. Semantic vs generation separation

Never collapse:
1. canonical tag identity
2. Alias identity
3. implication/hierarchy
4. related/co-occurrence/semantic-near
5. UI Japanese/search wording
6. model trigger surface
7. generation support/effectiveness
8. Prompt-only capability
9. LoRA/control/postprocess-assisted capability
10. evaluator/human judgement

“Tag is semantically correct” and “this checkpoint responds well to this surface” require separate claims.

## 9. Promotion rules

To move `CANDIDATE/HOLD/CONFLICT` -> `ACCEPTED`:
- preserve exact scope;
- record evidence identity;
- meet the row's validation requirement;
- resolve contradictions rather than deleting them;
- update `last_checked`;
- update the category explanation only after Registry verdict changes.

General reusable generation rules require E3-level evidence under the existing evidence framework. Local practical rules may be accepted only under pinned local context.

## 10. Authority boundary

A KNOWLEDGE `ACCEPTED` claim means “the KNOWLEDGE lane currently accepts this statement within its scope.”

It does **not** automatically:
- edit production `data/**`;
- change DEV implementation;
- change PROMPT production grammar;
- alter AUDIT verdicts;
- authorize Stage10 production A/B/scoring.

Downstream fields are routing metadata, not cross-team commands.

## 11. Old labels

Do not bulk-rewrite old research documents. Interpret them through `LABEL_MIGRATION_MAP.md`; current verdict always comes from the Registry.
