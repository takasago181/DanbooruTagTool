# Batch J — Existing Prompt Conflict Explanation

Owner: Issue #44 `KNOWLEDGE:#44`
Date: 2026-09-13
Status: `P1_CONFLICT_EXPLANATION_RESEARCH_COMPLETE`

Covers backlog theme:
- K-RB-09 Existing Prompt conflict/explanation knowledge

This batch defines how KNOWLEDGE may explain possible Prompt tensions **without automatically rewriting or deleting user text**.

## 1. Core rule

Prompt understanding and Prompt correction are separate operations.

The tool may safely say:
- `同じ役割の指定が競合している可能性があります`
- `PositiveとNegativeが意味的に重なっています`
- `人数指定が一致していません`
- `同じcanonical identityの別表記が重複しています`
- `誰が誰に何をしているか曖昧です`

It must not silently conclude:
- which token is "wrong"
- which token should be deleted
- that the model will certainly fail
- that one exact rewrite is optimal

unless a separate product feature and evidence authorizes that action.

## 2. Conflict/explanation classes

### C1 — same-role composition tension

Examples:
- `close-up` + `full body`
- multiple incompatible viewpoint/frame requirements
- mutually incompatible orientation requirements

Current Illustrious author guidance explicitly warns against overusing critical composition tags because conflicting composition tags can confuse results.

Project behavior:
- explain role overlap/tension;
- do not auto-delete one surface;
- model effectiveness remains separate.

### C2 — count contradiction

Examples:
- `1girl` with `2girls`
- singular subject language plus multi-subject count token

Project behavior:
- identify explicit count mismatch as a semantic inconsistency;
- do not guess which count the user intended.

### C3 — canonical/Alias duplicate identity

Example structure:
- canonical tag + active Alias/historical spelling resolving to the same canonical identity

Danbooru active Alias means identity mapping, so this is stronger than ordinary semantic similarity.

Project behavior:
- explain `同じ意味の別表記が重複している可能性`;
- preserve raw input;
- do not assume both surfaces have equal checkpoint trigger effectiveness.

### C4 — implication/broad+specific overlap

Example structure:
- child/subtype + implied parent

Danbooru implication is hierarchy/entailment, not synonymy.

Project behavior:
- explain parent/child relation;
- do not call it duplicate identity;
- do not automatically remove or add the parent;
- generation benefit/harm remains model/test scoped.

### C5 — Positive / Negative semantic overlap

Examples:
- Positive requests an unusual anatomy/count/relation concept while Negative contains a broad concept that can suppress it
- Positive and Negative carry opposite quality/date/safety surfaces

Project behavior:
- surface semantic overlap as a possible intervention conflict;
- do not claim the Negative is always wrong;
- model-family author baseline may intentionally include some Negative convention.

### C6 — actor/target/ownership ambiguity

Examples:
- multiple actors with unbound clothing/body/action attributes
- action/relation with unclear actor and receiver
- object/body-site present but relation unspecified

Project behavior:
- explain ambiguity of assignment;
- distinguish `object exists` from `object is attached/held/inserted/used by X`;
- do not fabricate actor-target binding.

### C7 — raw syntax / wrapper conflict

Examples:
- malformed emphasis/weight parentheses
- template syntax that is unresolved at inspection time
- LoRA/embedding/runtime wrapper mixed into text expected to be a canonical tag

Project behavior:
- classify wrapper/runtime syntax first;
- preserve exact text;
- avoid canonical tag interpretation until inner payload is isolated.

### C8 — ambiguous lexical collision

Example already tracked by Issue #34:
- query `anal` surfacing unrelated substring/fuzzy matches such as `piano` or `analog...`

Project behavior for **Prompt interpretation**:
- exact canonical / exact approved Alias / exact known syntax outrank fuzzy similarity;
- a fuzzy search candidate must not become an asserted interpretation of pasted Prompt text;
- unresolved text stays ambiguous/unknown.

## 3. Severity vocabulary

Use explanation severity rather than automatic correction:

- `INFO` — informative overlap; not necessarily a problem
- `POSSIBLE_TENSION` — two surfaces may compete or confuse interpretation
- `SEMANTIC_CONTRADICTION` — explicit meanings cannot both be true as written (e.g. direct count contradiction)
- `AMBIGUOUS_BINDING` — assignment/ownership unclear
- `POS_NEG_OVERLAP` — Positive and Negative meaning overlap
- `DUPLICATE_IDENTITY` — confirmed canonical/Alias identity duplication
- `UNKNOWN_SYNTAX_OR_TOKEN` — insufficient evidence

These labels describe **Prompt text structure**, not expected image success probability.

## 4. Evidence boundaries

### Safe without image tests

- active Alias identity duplication
- direct count contradiction
- known runtime syntax classification
- explicit Positive/Negative lexical/semantic overlap
- documented parent/child implication
- exact same-role semantic incompatibility when definitions are clear

### Needs model-scoped evidence before claiming generation harm

- whether a duplicate surface improves or hurts output
- whether broad+specific helps or hurts
- whether a given viewpoint pair actually causes failure on a checkpoint
- whether a Negative overlap materially suppresses the target
- whether reordering fixes the issue

## 5. Beginner-facing explanation patterns

Recommended concise structures:

- `この2つは同じcanonical tagの別表記です。意味は重複していますが、モデル上の反応が同じとは限りません。`
- `この2つは親子関係です。同義語ではありません。`
- `人数指定が一致していません。どちらを意図したかは自動では決めません。`
- `このNegativeはPositive側の指定と意味が重なる可能性があります。`
- `複数人物のどちらにこの属性が付くか、Promptだけでは曖昧です。`
- `この部分はタグではなく実行構文として解釈されます。`
- `この文字列は確実にタグへ対応できません。元の文字列を保持します。`

## 6. Sources / existing project evidence

- Danbooru tag categories / Alias / implication:
  - https://safebooru.donmai.us/wiki_pages/help%3Atags
- Illustrious composition warning:
  - https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0/blob/main/README.md
- Existing project knowledge:
  - `docs/knowledge/catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md`
  - `docs/knowledge/catalog/03_FAILURE_TESTING_AND_EVALUATION.md`
  - `docs/knowledge/research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`
  - `docs/knowledge/research/BATCH_E_EXISTING_PROMPT_SURFACE_CLASSIFICATION_20260913.md`
  - `docs/knowledge/research/BATCH_F_PROMPT_SEMANTIC_ROLE_DECOMPOSITION_20260913.md`
  - `docs/knowledge/research/BATCH_H_DANBOORU_CATEGORY_RELATION_UNKNOWN_HANDLING_20260913.md`
- Search-noise product issue:
  - Issue #34

## 7. Durable conclusion

For v1-style Prompt understanding, conflict handling should be:

`detect -> explain -> preserve -> user decides`

not:

`detect -> auto-delete -> auto-rewrite`.

This aligns with the current beginner-first product goal and keeps KNOWLEDGE from becoming an automatic Prompt optimizer.
