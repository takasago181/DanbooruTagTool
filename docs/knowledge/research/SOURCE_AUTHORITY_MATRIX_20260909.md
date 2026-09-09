# Generation Knowledge Source Authority Matrix

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `DURABLE_SOURCE_POLICY_V1`

## Purpose

DanbooruTagTool の知識班が、情報源の種類を混同せず、canonical意味・model trigger・generation practical・tool behavior・mechanismを別権限で扱うための恒久マトリクス。

---

## 1. Authority matrix

| Source class | Canonical meaning | Alias identity | Model trigger | Generation behavior | Tool behavior | General mechanism |
|---|---:|---:|---:|---:|---:|---:|
| Danbooru current Wiki | **HIGH** | MEDIUM | LOW | LOW | NONE | LOW |
| Danbooru active Alias records | **HIGH** | **HIGHEST** | MEDIUM-history | NONE | NONE | NONE |
| Danbooru active Implication records | **HIGH hierarchy** | NO | LOW | LOW hypothesis | NONE | NONE |
| e621 current Wiki | MEDIUM-secondary | MEDIUM | **MEDIUM-HIGH for NoobAI hypothesis** | LOW-MEDIUM | NONE | LOW |
| e621 active Alias/Implication | MEDIUM-secondary | HIGH within e621 | **MEDIUM-HIGH for NoobAI history** | LOW | NONE | NONE |
| Exact model author card | LOW semantic | NO | **HIGHEST model-specific** | **HIGHEST exact-family** | LOW | MEDIUM |
| Author Discussion reply | LOW semantic | NO | HIGH | HIGH exact-question | LOW | MEDIUM |
| Community Discussion on official host | LOW | NO | MEDIUM hypothesis | MEDIUM practical | LOW | LOW |
| Official GitHub README/docs | NONE | NONE | LOW | MEDIUM | **HIGHEST** | MEDIUM |
| GitHub Issues | NONE | NONE | LOW | MEDIUM practical | HIGH bug/version evidence | LOW |
| Primary research / paper | NONE | NONE | NONE | MEDIUM-general | LOW | **HIGHEST** |
| AIArtRecipe | NO | NO | PRACTICAL candidate | **MEDIUM practical/failure** | LOW-MEDIUM | LOW |
| としあきdiffusion Wiki | NO | NO | PRACTICAL candidate | MEDIUM practical | **MEDIUM-HIGH practical ops** | LOW |
| Civitai/Tensor.Art creator report | NO | NO | **HIGH for exact adapter** | MEDIUM adapter-specific | LOW | LOW |
| Reddit/general community | NO | NO | hypothesis only | LOW-MEDIUM failure discovery | LOW | LOW |

---

## 2. Canonical meaning order

For a Danbooru-origin Special:

1. current Danbooru canonical tag + wiki
2. active Alias / Implication records
3. relevant tag-group sibling distinctions
4. project protected source/provenance
5. e621 only as comparison/secondary semantics
6. practical sites only as generation observations

Never derive canonical meaning from:
- Prompt recipe success;
- LoRA trigger bundle;
- Tagger output;
- related/co-occurring tags;
- natural-language phrase that happens to work.

---

## 3. Model-trigger order

For exact model family:

1. author card / author reply
2. known training datasets/caption scheme
3. historical tag surface plausible at cutoff
4. controlled local A/B
5. creator/community practical reports

A model trigger may differ from current canonical identity.

Store separately:
- `canonical_tag`
- `alias_surface`
- `historical_surface`
- `model_trigger_candidate`
- `free_relation_phrase`

---

## 4. Generation-behavior order

1. exact author controlled guidance
2. project local paired A/B
3. controlled external practical comparison
4. primary mechanism research for plausibility
5. repeated practical failure reports
6. single-case community report

A single successful image is `CASE`, not a rule.

---

## 5. Source conflicts

When sources conflict:

### Canonical semantic conflict
Danbooru current canonical wins for DanbooruTagTool identity unless canonical project source explicitly freezes an older identity for traceability.

### Model-behavior conflict
Exact current model author evidence outranks older generic family advice.

Example:
- old Illustrious community: giant quality/Negative stacks
- WAI v17 author: too many quality/aesthetic tags and overly long Negative can reduce quality

For WAI v17, the current author guidance wins.

### Practical-vs-official conflict
Keep practical report as `FAILURE_CASE` or `TEST_CANDIDATE`; do not overwrite official fact unless local controlled evidence demonstrates a reproducible exact-version exception.

---

## 6. Multilingual rule

Language is not authority.

Japanese / English / Chinese / Korean / other-language evidence use the same rank.

A Japanese author card > English Reddit post.
A Chinese exact-model developer note > Japanese general blog.
A controlled Korean comparison > uncontrolled English anecdote for that exact practical claim.

---

## 7. Current trusted source stack

### Semantic/canonical
- Danbooru Wiki / Alias / Implication
- project protected Special2788 sources

### Alternate vocab / NoobAI
- e621 Wiki / aliases / implications
- NoobAI training-card evidence

### Exact models
- WAI v17 author card
- NoobAI EPS / V-Pred author cards
- Anima author card
- author replies where available

### Practical/failure
- AIArtRecipe
- としあきdiffusion Wiki
- exact LoRA/model creator reports
- selected HF Discussions

### Mechanism
- compositional generation papers
- rare-concept papers
- negative-prompt mechanism papers
- ControlNet / binding / evaluation research

### Tool behavior
- Forge Neo / ComfyUI / extension official GitHub docs/issues

---

## 8. Durable decision

No future KNOWLEDGE chat should say simply “source X says Y” without also recording:
- source class;
- exact model/tool/version scope;
- date/cutoff relevance;
- whether claim is semantic, trigger, generation, tool or mechanism;
- evidence rank;
- limitation/conflict.
