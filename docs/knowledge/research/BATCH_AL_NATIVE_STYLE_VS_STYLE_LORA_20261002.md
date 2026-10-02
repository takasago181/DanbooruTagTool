# BATCH_AL — Native style knowledge vs style LoRA — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: style-explorer/tool audit + community controlled evidence
Focus: when to use native artist/style prompts, when to train/apply Style LoRA

## 1. Style LoRA should not be the first assumption

For a target style, first ask:

1. Does the base checkpoint already know the artist/style?
2. Is the response faithful?
3. Is it stable across seeds?
4. Does it survive different content?
5. Can it mix with the target character/concept?
6. Does another LoRA suppress it?

Only then decide whether a Style LoRA is needed.

Promoted:
- K-STYLE-003.

## 2. Anima native-style discovery

Community Style Explorer:
- https://github.com/ThetaCursed/Anima-Style-Explorer
- https://huggingface.co/circlestone-labs/Anima/discussions/227

Current community database:
- over 40k visual artist/style previews;
- search/favorites/swipe;
- standardized comparison images;
- approximate work-count / uniqueness metadata.

Use:
- discovery;
- quick visual elimination;
- selecting candidate native artist tags.

Do not use:
- work-count as exact model exposure;
- one preview as a fidelity guarantee;
- uniqueness rank as objective quality.

Promoted:
- K-TOOL-028.

## 3. Illustrious / NoobAI native-style discovery

Community projects:
- https://github.com/ThetaCursed/Illustrious-NoobAI-Style-Explorer
- current accessible fork:
  https://github.com/Faildes/Illustrious-NoobAI-Style-Explorer-plus

They provide:
- thousands of artist previews;
- large compatible-name lists;
- visual browsing and comparison.

The repository describes broad compatibility across Illustrious/NoobAI, but project policy is stricter:
every important style still needs exact checkpoint testing.

Promoted:
- K-TOOL-029.

## 4. Standardized raw-style benchmarking

The Anima Style Explorer explicitly revised its benchmark to:
- remove quality boosters;
- use a standardized character/content prompt;
- compare raw artist influence.

This is methodologically valuable.

Minimum test:
A0 — neutral baseline
A1 — artist only
A2 — artist + normal production quality support
A3 — artist + different content
A4 — artist + character LoRA
A5 — artist + Style LoRA if used

Use multiple seeds.

Promoted:
- K-EVAL-016
- K-STYLE-004.

## 5. Native artist style is context-sensitive

Anima discussion #112:
https://huggingface.co/circlestone-labs/Anima/discussions/112

The user ran a more technical analysis:
- same artist tag shifts under different neighboring prompt tokens;
- adding multiple artists increases drift;
- artist position affects output;
- replacing/caching an artist representation from a stable reference condition partially restores style consistency.

The proposed Qwen/RoPE mechanism is community analysis, not author-confirmed fact.

Durable observation:
artist behavior is context-sensitive.

Promoted:
- K-COMM-ANIMA-023.

## 6. One artist vs artist mixtures

Community reports show:
- one artist can still vary seed-to-seed;
- multi-artist mixtures can be less stable;
- stronger weights sometimes help but exact values are model/style dependent.

Project rule:
Do not store a universal “artist mix weight”.

Compare:
- A
- B
- A+B
- A then B scheduling if runtime supports it
- Style LoRA alternative

## 7. Decision tree: native style or Style LoRA?

### Use native artist/style prompt first when
- checkpoint clearly knows target style;
- output is sufficiently faithful;
- style remains responsive across desired subjects;
- you need maximum prompt flexibility.

### Consider Style LoRA when
- style is absent/weak;
- target is a custom/private style;
- native artist response is unstable;
- exact combination of several style traits is required;
- a fixed reusable style asset is desired.

### Consider reference style conditioning when
- only one/few style references exist;
- no training time is desired;
- content preservation matters more than persistent reusable trigger.

## 8. LoRA can make native style worse

Existing project evidence:
- K-COMM-ANIMA-020
- native artist response can weaken after applying LoRA.

Therefore before creating a new Style LoRA, test:
- native style alone;
- character LoRA + native style.

If the second condition already loses style:
a second Style LoRA may increase interference rather than solve it.

Possible escalation:
- retrain character LoRA for editability;
- scheduled/masked adapters;
- reference-style conditioning;
- dedicated combined training only after independent diagnostics.

## 9. Style fidelity is multi-dimensional

Do not treat style as only:
- color palette.

Evaluate:
- line weight/shape;
- anatomy/face stylization;
- eye rendering;
- color/palette;
- shading;
- texture/brush;
- detail density;
- background treatment;
- composition bias.

Native artist tags can reproduce some dimensions and miss others.
Style LoRA can also overfit composition/body prior.

## 10. Style search as product feature

DanbooruTagTool can eventually use:
- artist tag identity;
- model family;
- visual preview;
- approximate known/native behavior;
- context-sensitivity warnings;
- favorite style sets;
- similar-style discovery;
- “native style first / LoRA recommended” experiment state.

External community explorers prove strong demand for visual browsing, but their metadata is not automatically project authority.

## Promotion result

New ACCEPTED:
- K-STYLE-003
- K-TOOL-028
- K-TOOL-029
- K-EVAL-016
- K-STYLE-004

New CANDIDATE:
- K-COMM-ANIMA-023
