# Prompt, Support and Composition

## Core design rule

Minimum sufficient Prompt does **not** mean shortest Prompt. Preserve the semantic nucleus and remove unsupported/redundant pressure around it.

Protected nucleus can include:
- selected Special(s)
- intrinsic actor/target/ownership
- intrinsic body-site
- intrinsic count
- intrinsic implement/modifier
- relation required by the concept
- justified model-specific trigger surface.

## Support taxonomy

Keep support separate from Special identity.

1. `MEANING_SUPPORT` — constituent/semantic support
2. `GEOMETRY_KINEMATIC` — physical arrangement needed for realization
3. `VISIBILITY` — frame/viewpoint/focus needed to judge result
4. `RESOURCE_DISAMBIGUATION` — actor/hand/object assignment to reduce binding conflict
5. `AESTHETIC` — style/lighting/expression/background quality, not semantics
6. `REDUNDANT_DECORATION` — no demonstrated semantic/observation value

A semantically compatible support can still be generation-harmful (`ANTI_SUPPORT`) through frame conflict, count pressure, binding pressure, trigger/context bleed, or Negative collision.

## Prompt pruning order

When simplifying, usually test removal in this order:
1. unrelated decoration / excessive quality-aesthetic content
2. duplicate/synonymous surfaces
3. conflicting same-role frame/viewpoint tags
4. unproven broad parent/constituent
5. optional natural-language/context with no structural value
6. visibility/geometry/resource supports one at a time
7. weighting only after structural conflict is cleaned.

Use paired leave-one-out tests instead of deleting many tags simultaneously.

## Composition workload

Prompt difficulty is better represented by semantic workload than raw length.

Track:
- Special count
- actor count
- object count
- relation/binding count
- body-site count
- count constraints
- frame/viewpoint requirements
- support-role count
- natural-language relation clause
- tag/token count as secondary data.

A long compatible Prompt can work; a short Prompt with several conflicting relations can fail.

## Multi-Special rule

Never infer `tag unknown` from AB failure before checking A and B alone.

Recommended progression:
`A_ONLY -> B_ONLY -> AB minimal -> one support role at a time -> assisted lane only after bounded Prompt attempts`.

If A and B work alone but one disappears in AB, first suspect:
- attention/concept competition
- binding/ownership
- geometry
- visibility
- support conflict
- Negative collision.

## Frame / viewpoint / orientation / visibility / relation

Keep these roles distinct:
- Frame = how much is shown
- Viewpoint = where camera observes from
- Orientation = subject/body direction
- Visibility = whether target can be judged
- Relation = who acts on what / ownership / contact / topology

Do not stack multiple same-role tags by default.

## Broad + specific

No universal rule. Test separately:
- specific only
- broad only
- broad + specific.

A broad parent can help rare exposure/context or can dilute the specific target. Implication does not automatically become Prompt support.

## Canonical / Alias / alternate trigger

Dictionary identity and model response are separate.

Controlled tests may compare:
- canonical surface
- known Alias
- historically relevant older spelling
- semantic-near phrase only as non-equivalence condition.

Never normalize the compared surfaces before generation.

## Runtime preprocessing boundary

入力したPrompt文字列と、モデルへ渡されるconditioningは同一レイヤーではない。

AUTOMATIC1111 WebUIのruntime仕様では、長いPromptを75-token chunkへ分けて処理し、`BREAK` で新しいchunkを開始できる。また `(word)` / `[word]` / `(word:weight)` のattention/emphasis構文がある。

このため次を分離する。

- Danbooru semantic identity
- Prompt surface / tag order
- runtime tokenization / chunking / weighting
- checkpointがそのconditioningへ実際にどう反応するか

`BREAK` はDanbooru tagでもsemantic supportでもない。さらに、`BREAK` やchunk境界がWAI17のbindingを改善することは現時点で確定していない。A1111由来のruntime仕様をローカルForge Neoへ適用する場合も、local remote/commit/configをpinするまでは完全同一とみなさない。

Current Claims: `K-TOOL-006`, `K-TOOL-007`.

## Primary originals

- `../research/BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md`
- `../research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`
- `../research/BATCH_D_RUNTIME_PROMPT_REPRO_COMPOSITION_20260910.md`
- `../GENERATION_KNOWLEDGE_CORPUS.md` sections 2 and 4
- `../research/AIARTRECIPE_PRACTICAL_FINDINGS_20260909.md`
- `../research/TOSHIAKI_WIKI_PRACTICAL_FINDINGS_20260909.md`
