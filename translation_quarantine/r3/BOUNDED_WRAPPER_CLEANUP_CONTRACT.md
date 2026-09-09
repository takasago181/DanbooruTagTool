# Issue #36 — Bounded wrapper false-JA cleanup contract

Status: ACTIVE cleanup handoff after independent audit `PASS_WITH_BOUNDED_CLEANUP`

## Authority / trigger

This contract is created from the final independent audit recorded in Issue #36 comment `5593895675`.

Audited source candidate before this contract:

- branch: `ui-ja/issue36-machine-convergence`
- audited HEAD: `f9e275f532f3e072ecde266eae8479ea52bcd31f`
- qualified-label final contract: `60fc740a0c6463f9aeef40293bd006c0037493da`
- audited artifact root: `translation_quarantine/qualified_label_final_review_20260909/`

The independent audit found one bounded systematic defect: rows accepted as Japanese through `JAPANESE_WRAPPER_WITH_EXACT_CANONICAL` / `CANONICAL_IDENTITY_DISPLAY` can contain labels such as `タグ「kickstand」`, which are English canonicals wrapped in Japanese punctuation/text rather than glanceable Japanese meanings.

This cleanup is required before production promotion. Production promotion remains NOT AUTHORIZED by this contract.

## User intent / acceptance rule

Japanese display/search exists so the user can glance at a label and understand its meaning.

- publication-grade Japanese is not required
- slightly awkward Japanese is acceptable
- material meaning errors are not acceptable
- do not reverse actor/target/body/direction/count/action-state
- do not broaden or narrow the concept materially
- do not force true proper names, character/cosplay identities, artist/style identities, franchise-specific named artifacts, products/services, model/code identifiers, symbols/emoticons, or genuinely opaque source strings into artificial Japanese merely to increase coverage
- canonical English identity remains authoritative and unchanged

A Japanese wrapper around unchanged English text is NOT sufficient Japanese coverage merely because Japanese characters such as `タグ`, brackets, or punctuation are present.

## Scope — bounded only

Start from the current Issue #36 branch after fetching latest remote state.

Primary target set is every final-table row whose accepted Japanese came through either of these signals, or any equivalent implementation path producing the same false-JA pattern:

- `proposal_source == JAPANESE_WRAPPER_WITH_EXACT_CANONICAL`
- `route == CANONICAL_IDENTITY_DISPLAY`
- display/search labels structurally equivalent to `タグ「<English canonical/readable canonical>」`

Do not reopen historical strict R3 review of all 30,629 rows.

Do not restart a general translation campaign.

It is allowed to inspect adjacent rows only when necessary to classify or safely repair the bounded target set.

## Required classification for every bounded target row

Each bounded target row must end in exactly one of these outcomes:

### A. TRANSLATABLE_DISPLAY

Use when the underlying concept has an ordinary/glanceable Japanese meaning without losing canonical identity.

Examples of the defect class that require real Japanese rather than a wrapper include ordinary/general or adult/niche concepts such as:

- `kickstand`
- `legjob`
- `dominator_(bdsm)`
- `implied_cheating_(relationship)`
- `alternate_ass_size_(larger)`

Exact Japanese wording is an implementation decision, but it must preserve the concept and qualifier meaning.

For qualified concepts, translate the descriptive base and preserve the identity qualifier when useful, e.g. the already accepted pattern `human_(warcraft) -> 人間（Warcraft）`.

### B. TRUE_ORIGINAL_FORM_EXCEPTION

Use only when retaining the original form is more correct/useful than inventing Japanese, including true:

- character/cosplay identity
- artist/style identity where transliteration/translation would be misleading
- named franchise-specific artifact/title/entity
- product/service/company name
- model/code identifier
- symbol/emoticon
- genuinely opaque source string

Such rows must not remain counted as Japanese merely because they are wrapped in `タグ「...」`. They should become explicit `ENGLISH_FALLBACK_EXCEPTION` (or the existing equivalent terminal exception representation) with a narrow reason.

## Residual 826 fallback ledger

Do not reopen all 826 residual exceptions.

The independent audit sampled the residual ledger and found it predominantly consistent with narrow original-form exceptions. Only touch a residual fallback row if the bounded wrapper cleanup reveals direct, concrete evidence that the same row is necessary for consistency or a deterministic invariant. Otherwise leave the 826 set alone.

Any change in fallback count must be explained by exact row-level additions/removals from this cleanup; do not chase the previous 97.30% figure.

## Required implementation properties

1. Enumerate the complete bounded target set deterministically and record its exact count.
2. Produce a review/repair ledger containing at least canonical, old display/search label, old state/route/source, classification, new display/search label, new state, reason.
3. Ensure no accepted Japanese row remains a false positive solely because Japanese wrapper text surrounds otherwise unchanged English.
4. Preserve canonical English identities exactly.
5. Rebuild the merged final table at exactly 30,629 unique canonicals.
6. Generic REVIEW/PENDING must remain 0.
7. Recompute display/search coverage from actual nonblank meaningful Japanese display/search rows after cleanup; do not reuse 97.30% mechanically.
8. Recompute residual fallback ledger and count.
9. Replay/determinism must PASS.
10. Protected production boundary must PASS.

## Representative semantic audit categories

The cleanup report must include representative repaired/retained examples from all applicable categories present in the bounded target set:

- ordinary/general
- adult/niche
- relation / actor-target
- direction
- count
- action-state
- qualified concepts
- true identity/code/symbol/opaque exceptions

For relation/direction/count/action-state rows, explicitly confirm no semantic inversion or dropped qualifier occurred.

## Required artifacts

Create a new quarantine output root; do not overwrite the audited final-review root. Suggested name:

`translation_quarantine/bounded_wrapper_cleanup_20260909/`

At minimum produce:

- `FINAL_REPORT.md`
- `run_summary.json`
- `bounded_target_ledger.jsonl` (or CSV)
- `fallback_exceptions.jsonl`
- `final_translation_table.csv`
- `coverage_recount_before_after.json`
- `replay_verification.json`
- `protected_boundary.json`

A deterministic script and focused tests should be added under the existing quarantine/test structure as needed.

## Tests

Run and report separately:

1. focused bounded-wrapper cleanup tests
2. relevant Issue #36 / R3 / qualified-review regression tests
3. combined regression suite used by the prior final review where feasible
4. full `pytest`

Full pytest reporting rule is unchanged:

- do NOT call the full suite PASS if setup errors remain
- the prior baseline was `320 passed / 61 environment setup errors` from Windows TEMP ACL `WinError 5`
- separate environment/setup errors from product/assertion failures
- do not spend unbounded effort repairing the known TEMP ACL environment issue in this cleanup

Any new product/R3 assertion failure is a blocker.

## Protected boundaries / forbidden work

This contract authorizes quarantine/tests only.

Do NOT modify:

- production `data/**`
- `data/runtime/japanese_overlay.json`
- canonical English identity
- Prompt syntax
- co-occurrence data
- recommendation order/scoring
- semantic-support relations/classes/slots
- generation metadata/profiles/model observations
- #32 validation data/verdicts
- #35 UI/code/tests outside any pre-existing regression test that does not alter #35 behavior
- `docs/project/CURRENT_DEV_TASK.md`
- main branch
- Stage10 production A/B state

Do not merge main and do not perform production promotion in this run.

## Stop / handoff condition

Stop after all of the following are true:

- complete bounded target set classified
- no wrapper-only false-JA remains in that bounded set
- final table = exactly 30,629 unique canonicals
- generic REVIEW/PENDING = 0
- coverage and fallback count recomputed honestly
- replay PASS
- protected boundary PASS / production modified NO
- required tests reported accurately
- artifacts committed
- branch commit pushed to `ui-ja/issue36-machine-convergence`
- completion checkpoint contains commit SHA, exact target count, classification counts, resulting Japanese coverage/fallback count, representative semantic samples, test results, artifact root, and confirmation that production promotion was NOT performed

After Codex returns this cleanup, a fresh ChatGPT independent audit should review only the cleanup delta plus representative output samples. Do not automatically proceed to production promotion until that audit passes.
