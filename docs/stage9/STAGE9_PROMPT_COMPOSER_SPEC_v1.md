# DanbooruTagTool — Stage9 Prompt Composer Specification v1

Date: 2026-09-07 JST
Status: APPROVED FOR STAGE9A IMPLEMENTATION
Previous fixed point: Stage8C FINAL / Pilot001 ACCEPTED / Exit Pilot PASS / Pilot003 NOT REQUIRED

## 0. Stage9 goal

Stage9 creates the Prompt Composer layer that converts the user's selected Special2788 entries and supporting knowledge into a practical English Danbooru-style Prompt without weakening Special meaning.

Runtime remains fully local and non-LLM.
Stage8C is not reopened.
Stage10 image-generation A/B validation is not performed here.

The Composer must answer four questions deterministically:

1. Which selected Special entries must remain in the Prompt?
2. Which support candidates are included, suggested, or withheld?
3. In which functional block is each output item rendered?
4. Why is each output item present, absent, merged, or warned about?

## 1. Non-negotiable invariants

1. Special2788 remains first-class and is never demoted to General support.
2. A support tag may help a Special, but must never replace the Special identity.
3. Distinct Special identities must never be silently collapsed merely because a General canonical or alias overlaps.
4. Canonical dedupe of support must preserve all owner relations/provenance.
5. No substring/regex/tag-text guessing may create semantic support.
6. No Stage8C relation count or coverage quota is a Composer success metric.
7. NO_SUGGESTION / UNRESOLVED / Special-only output remain valid.
8. No universal role-count threshold is introduced in Stage9A.
9. No automatic Prompt weighting is introduced in Stage9A.
10. No automatic LoRA Prompt contraction is introduced in Stage9A.
11. No general rule that duplicate tags strengthen generation is introduced.
12. Anima-specific behavior must not become the global default.
13. Negative conflicts generate warnings; Stage9A must not silently rewrite the user's Negative Prompt.
14. User-explicit choices are not silently removed to make the Composer look cleaner. If conflicting, retain them and warn.

## 2. Stage9 decomposition

### Stage9A — Pure Composer core

Implement deterministic data structures, block assembly, semantic support selection state, dedupe/provenance preservation, and warnings. No UI dependency.

### Stage9B — Candidate lanes and runtime integration

Integrate semantic-support candidates, semantic/search auxiliaries, and co-occurrence candidates without collapsing them into one opaque score. Add user selection state and final plan building.

### Stage9C — Local UI integration

Integrate the Composer into the existing local application flow:
Japanese search -> Special selection -> support review -> Prompt preview/output.
Keep interaction cost low and expose reasons only when needed.

### Stage9D — Stage10 experiment hooks

Expose reversible Composer profile options needed for controlled A/B tests, but do not decide image-generation winners inside Stage9.

Stage9 is complete only after 9A-9D gates pass. Stage10 remains a separate image-validation stage.

## 3. Composer block model

Stage9 uses role-based blocks. The baseline order is a project Composer profile, not a universal model truth.

Baseline high-level order:

1. META_QUALITY
2. COUNT
3. RELATION
4. IDENTITY
5. SPECIAL
6. SUPPORT_STRUCTURE
7. POSE_COMPOSITION
8. GENERAL_AUX
9. BACKGROUND_LIGHT
10. LORA

Negative Prompt is a separate channel and is never mixed into the positive block list.

### 3.1 Meaning of blocks

- META_QUALITY: quality/meta tokens already supported by the application/profile.
- COUNT: person count / subject-count tokens.
- RELATION: explicit multi-character relation tokens. When present, this block is immediately after COUNT.
- IDENTITY: character/identity tokens supplied by the user or existing character profile.
- SPECIAL: selected Special2788 entries. First-class; never treated as General support.
- SUPPORT_STRUCTURE: structural support such as body part, implement/object, action support, state/reaction, and other semantically approved support.
- POSE_COMPOSITION: pose and camera/composition items.
- GENERAL_AUX: clothing/situation/detail/other auxiliary items from later-stage candidate sources.
- BACKGROUND_LIGHT: background and lighting items.
- LORA: LoRA invocation items, kept separately addressable even if flattened at render time.

Exact Special placement must be configurable by ComposerProfile for Stage10 A/B. Baseline is after IDENTITY and before General/support blocks.

## 4. Special representation

Selected Specials are identity-keyed by `special_id`, not by General canonical.

Rules:

- Duplicate selection of the same `special_id` is removed deterministically.
- Distinct Special IDs are never silently merged because a General canonical overlaps.
- If two distinct selected Specials render to exactly the same Prompt token, the rendered token may appear once, but the atom must retain both Special owner identities. The selection/UI record must still preserve both entries.
- A support candidate that renders the same canonical/token as a selected Special must not create a second duplicate token. Its provenance is attached to the existing rendered atom as `satisfied_by_special`.
- This rendering dedupe must never be interpreted as semantic replacement of one Special by another.

## 5. Support-candidate selection policy

Stage8C support rows are semantic knowledge, not proof of generation effectiveness. Stage9 therefore distinguishes candidate class and selection state.

### 5.1 Default selection

For semantic support:

- CORE_SUPPORT + ADDITIVE -> auto-selected by default when not an exact duplicate and not blocked by an explicit approved conflict rule.
- CORE_SUPPORT + ALTERNATIVE -> suggested, not auto-selected. User choice is required.
- CORE_SUPPORT + CONTEXTUAL -> suggested, not auto-selected unless the required context is explicitly known by the Composer.
- OPTIONAL_VARIATION -> suggested, not auto-selected.
- UNRESOLVED / NO_SUGGESTION -> no invented fallback support.

This rule intentionally uses no global maximum count.

### 5.2 User override

A user may explicitly include or exclude a support candidate.

- Explicit include overrides the default-off state.
- Explicit exclude overrides auto-selection.
- The Composer records the override reason/state.
- A conflicting explicit include remains present and produces a warning rather than being silently deleted.

### 5.3 Multiple-owner support

When one canonical support candidate is owned by multiple selected Specials:

- Render once.
- Preserve every `SemanticSupportRelation` owner_special_id and provenance.
- Preserve the strongest/most relevant class per relation rather than flattening the candidate to a single lossy label.
- UI may summarize the candidate, but the internal object must retain all relations.

## 6. Dedupe policy

Only safe identity-based dedupe is allowed in Stage9A.

Safe dedupe includes:

- exact same Special ID selected multiple times;
- exact same canonical General/support candidate;
- aliases already resolved by the existing canonical authority;
- exact same rendered token where duplicate emission would add no semantic distinction, while retaining all provenance.

Not allowed in Stage9A:

- substring dedupe;
- fuzzy semantic dedupe;
- automatically declaring broad + specific tags redundant;
- replacing a Special with a generic support term;
- assuming two similar English phrases are synonymous without approved authority.

The architecture may expose a future explicit `redundancy_group` or approved relation table, but Stage9A must not populate one by guessing.

## 7. Candidate-source lanes

Do not combine semantically different candidate sources into one opaque ranking score.

Present/retain separate lanes:

1. `SEMANTIC_CORE` — explicit curated CORE_SUPPORT.
2. `SEMANTIC_OPTIONAL` — explicit curated OPTIONAL_VARIATION.
3. `SEMANTIC_AUX` — approved semantic/search auxiliary candidates from earlier stages where available.
4. `COOCCURRENCE` — statistical candidates from true-AND co-occurrence.
5. `USER_EXPLICIT` — user-supplied additions.

Default behavior:

- Special is always first-class and outside these auxiliary lanes.
- Semantic CORE may auto-select according to section 5.
- OPTIONAL/AUX/COOCCURRENCE do not auto-maximize Prompt length.
- Co-occurrence suggestions remain suggestions and keep their raw evidence (`co_count`, `base_count`, `conditional_rate`, snapshot identity) when available.
- Stage6 Conditional Rate remains a technical first candidate for ordering co-occurrence results, but Stage9 must not misrepresent it as proven user utility.
- Do not create a combined semantic+statistical score in Stage9A/9B without a separate approved decision.

## 8. Conflict and warning policy

### 8.1 Explicit conflicts only

Stage9A may warn on conflicts that are directly known from approved structure or exact normalized identity.

Required warnings:

1. Positive/Negative exact canonical/token intersection.
2. Project NSFW/adult intent active while Negative contains `nsfw` (profile-aware rule).
3. A positive artist/style token is also present in Negative when both can be normalized/identified.
4. Multiple user-selected members of the same explicit `choice_group`.
5. Model-profile mismatch/unsupported profile selection where a model-scoped rule is being applied outside its scope.

### 8.2 No invented same-role threshold

Do not warn merely because there are N pose/action/composition tags.
Same-role density thresholds are WAIT_FOR_IMAGE_VALIDATION and belong to Stage10 A/B.

If an explicit choice_group or approved incompatibility relation exists, warn on that relation regardless of count.

### 8.3 Warning severity

Use non-destructive warnings. Suggested levels:

- INFO
- CAUTION
- CONFLICT

Warnings do not mutate the Prompt automatically.

## 9. Model-aware ComposerProfile

Composer behavior that may vary by model must be data/profile-driven, not hard-coded as one global truth.

Minimum profile fields:

- `profile_id`
- `model_family`
- `block_order`
- `special_slot_position`
- `negative_rule_set`
- `validation_status`
- `notes`

Recommended model-family values at minimum:

- ILLUSTRIOUS
- WAI_ILLUSTRIOUS
- NOOBAI
- ANIMA
- GENERIC

Rules:

- Anima is separate and must not inherit Illustrious/WAI/NoobAI-specific assumptions merely through GENERIC defaults.
- Baseline Stage9 order may be shared where no contrary rule is implemented, but profile scope and validation status must remain explicit.
- `validation_status` should distinguish Stage9 design candidate from Stage10 image-validated behavior.

## 10. Stage10-controlled knobs that Stage9 must make reversible

Stage9 architecture must allow later A/B variants for:

- Special position.
- 0/1/2 broad generic support additions.
- role density variants.
- weight variants.
- LoRA Prompt contraction variants.
- frontend/runtime comparison metadata.

Stage9 must not declare the winning values.

For weighting specifically:

- atom structure may contain optional weight metadata;
- default weight is neutral/unset;
- no automatic 1.1/1.2/etc. behavior in Stage9A.

For LoRA specifically:

- LoRA invocations remain separately addressable;
- do not automatically remove artist/style/support tags when LoRA is active;
- no automatic CFG or model-setting changes.

## 11. Proposed pure-core data contract

Naming may be adapted to repository conventions, but equivalent information must exist.

### `ComposerAtom`

- stable atom id
- render token/text
- canonical if available
- block
- source lane
- selected state
- user override state
- Special owners (if any)
- support relations/provenance (if any)
- optional weight metadata (neutral by default)
- merge/suppression reason where relevant

### `ComposerPlan`

- selected Special IDs in user order
- candidate atoms
- selected atoms
- suppressed/merged atoms
- warnings
- active ComposerProfile

### `ComposeResult`

- structured positive blocks
- flattened positive Prompt
- Negative Prompt unchanged
- warnings
- provenance map from rendered token -> all owners/sources
- deterministic ordering metadata/profile id

## 12. Ordering rules

Within a block:

1. Preserve user-explicit order for user-owned input where practical.
2. Preserve selected Special order in the SPECIAL block.
3. Semantic support uses deterministic priority/order already supplied by SupportKnowledgeStore.
4. Statistical suggestions preserve their ranking order and evidence.
5. Never alphabetically reorder user intent merely for cosmetic consistency.

Across blocks:

- Use ComposerProfile block order.
- Baseline places RELATION immediately after COUNT.
- Baseline places SPECIAL after IDENTITY and before General/support.
- Do not call this order universally optimal; mark it Stage10-unvalidated.

## 13. Rendering rules

- Reuse the project's existing canonical/tag rendering convention.
- Do not redesign underscore/space handling in Stage9A.
- Do not tokenize Prompt input by spaces.
- Flatten blocks with the existing comma-separated Prompt convention.
- LORA remains a distinct block/object even if final output appends `<lora:...>` tokens.
- Negative Prompt is passed through unchanged except for analysis/warnings.

## 14. Required Stage9A tests

At minimum:

1. selected Special always survives even if a generic support overlaps;
2. same Special ID selected twice does not duplicate;
3. two selected Specials that share one support canonical render support once and retain both owner relations;
4. ID88-style explicit Special relation remains stronger than Family relation and auto-selection follows the explicit CORE/ADDITIVE relation;
5. family-only CONTEXTUAL OPTIONAL `solo` is suggested, not auto-selected;
6. UNRESOLVED Special produces valid Special-only plan;
7. a Special with multiple CORE/ADDITIVE rows is not truncated by a hard count cap;
8. ALTERNATIVE choice_group is not auto-fixed; selecting multiple alternatives warns;
9. exact positive/negative collision warns but does not alter either side;
10. Negative `nsfw` warning is profile-aware;
11. different model profile scopes do not leak Anima behavior into WAI/Illustrious;
12. block order is deterministic and RELATION follows COUNT in the baseline profile;
13. SPECIAL location can be changed by profile without changing semantic data;
14. user explicit support exclusion suppresses an otherwise auto-selected CORE support and records override;
15. user explicit conflicting inclusion remains and warns;
16. support canonical equal to Special render token does not create duplicate output and keeps provenance;
17. flattened Prompt is deterministic across repeated runs;
18. no network/LLM call occurs.

Use synthetic fixtures where current production data does not contain the required shape.
Do not mutate production semantic CSV merely to make a test possible.

## 15. Stage9A protected surfaces

Stage9A must not modify unless a concrete implementation dependency is proven and separately reported:

- Stage0-8B source identity/data authority;
- Special2788 source corpus;
- Ruleset2 authority;
- Stage8C accepted semantic support rows;
- family_support_rules.csv semantics;
- stage8c_review_status.csv decisions;
- Stage6 statistics formulas/ranking decision;
- full index logical semantics.

No new Stage8C curation is part of Stage9A.

## 16. Stage9A acceptance gate

Stage9A passes only if:

- pure Composer core exists without UI dependency;
- all required tests pass;
- full existing pytest suite passes;
- Stage8C protected hashes/identity remain unchanged where existing validators cover them;
- Special-specific meaning is never replaced by support;
- provenance survives canonical dedupe;
- no global same-role count threshold/weighting/LoRA contraction is introduced;
- no network or LLM runtime dependency is introduced;
- a concise Stage9A report lists modified files, tests, unresolved items, and exact Stage9B restart point.

## 17. Stage9B restart point after 9A

After Stage9A is accepted, Stage9B should connect the pure Composer core to the existing candidate systems while keeping source lanes separate.

Primary Stage9B questions:

- how semantic/search auxiliary roles map into Composer blocks;
- how co-occurrence suggestions are presented without auto-bloating the Prompt;
- how user selection state persists;
- how candidate reason/evidence is shown with minimal interaction cost;
- whether a lightweight redundancy authority is needed beyond canonical alias dedupe.

Do not begin Stage10 image A/B until Stage9 behavior is stable enough to generate reproducible Prompt variants.
