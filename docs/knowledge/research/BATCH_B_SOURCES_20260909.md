# Batch B Source Registry — Minimum-Sufficient Prompt / Pruning — 2026-09-09

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Research target:
- minimum-sufficient Prompt rather than maximum tag accumulation;
- functional redundancy and anti-support;
- composition/token competition;
- broad + specific support;
- prompt phrasing/structure vs raw length;
- model-family-specific pruning constraints;
- A1111/Forge prompt chunking as an interpretation confound;
- stopping Prompt escalation before assisted control.

Evidence classes follow Issue #44. Language is metadata, not evidence rank.

---

## Primary / conference evidence

### B01 — Divide & Bind

- Title: Divide & Bind Your Attention for Improved Generative Semantic Nursing
- Venue: BMVC 2023
- Project: https://sites.google.com/view/divide-and-bind
- Language: English
- Class: `FACT_GENERAL`
- Scope: compositional diffusion, not exact project checkpoints
- Key use:
  - project page states that competition between tokens becomes more severe with more complex prompts;
  - separates attendance of multiple concepts from attribute binding.
- Product implication:
  - reducing unnecessary competing concepts is a justified research direction;
  - raw token count itself is not the causal variable.
- Do not infer:
  - a fixed maximum tag count;
  - a universal pruning percentage.

### B02 — Structured Diffusion Guidance

- Title: Training-Free Structured Diffusion Guidance for Compositional Text-to-Image Synthesis
- Venue: ICLR 2023
- Paper: https://arxiv.org/abs/2212.05032
- Google Research: https://research.google/pubs/training-free-structured-diffusion-guidance-for-compositional-text-to-image-synthesis/
- Code: https://github.com/weixi-feng/structured-diffusion-guidance
- Language: English
- Class: `FACT_GENERAL`
- Key use:
  - linguistic structure improves attribution binding/composition;
  - multi-object composition remains challenging;
  - official code notes improvement is system-level and correct images may still require several attempts.
- Product implication:
  - minimum sufficient does not mean deleting structural relation language;
  - structure can be more valuable than additional flat synonyms.

### B03 — Object-Attribute Binding

- Title: Object-Attribute Binding in Text-to-Image Generation: Evaluation and Control
- URL: https://arxiv.org/abs/2404.13766
- Language: English
- Class: `FACT_GENERAL`
- Key use:
  - prompt syntax can help disentangle object/attribute representations;
  - binding failure is not solved merely by presence of the right nouns/adjectives.
- Product implication:
  - pruning must preserve actor/target/attribute grouping where it carries structure.

### B04 — Attention Map Control

- Title: Compositional Text-to-Image Synthesis with Attention Map Control of Diffusion Models
- Venue: AAAI 2024
- URL: https://ojs.aaai.org/index.php/AAAI/article/view/28364
- Language: English
- Class: `FACT_GENERAL`
- Key use:
  - identifies attribute leakage, entity leakage and missing entities as composition defects;
  - reinforces that more prompt content can create binding problems that are not semantic-dictionary failures.

### B05 — ConceptMix++

- Title: ConceptMix++: Leveling the Playing Field in Text-to-Image Benchmarking via Iterative Prompt Optimization
- URL: https://arxiv.org/abs/2507.03275
- Language: English
- Class: `FACT_GENERAL`
- Key use:
  - prompt phrasing materially changes measured compositional capability;
  - spatial relationships and shapes benefit unevenly from optimization;
  - rigid prompt forms may underestimate model capability.
- Product implication:
  - `shorter` and `better` are not synonyms;
  - pruning experiments must distinguish removed concepts from rewritten structure/phrasing.

---

## Exact model / author evidence

### B06 — WAI Illustrious v17 model card

- Model: `LyliaEngine/waiIllustriousSDXL_v170`
- URL: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- Language: English / Chinese author-hosted page
- Class: `FACT_EXACT_MODEL`
- Exact use:
  - author warns not to add too many quality/aesthetic-related tags or overly long Negative prompts because image quality can decrease and become blurrier;
  - supplies a small positive quality baseline and a small Negative baseline.
- Product implication:
  - WAI v17 has direct author evidence against maximal quality/Negative stacks;
  - quality/aesthetic/Negative additions are legitimate pruning candidates.
- Do not infer:
  - exact optimal tag count;
  - that every long positive descriptive Prompt is harmful.

### B07 — Illustrious XL early model card

- Model: `OnomaAIResearch/Illustrious-xl-early-release-v0`
- URL: https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0
- Language: English
- Class: `FACT_EXACT_MODEL`
- Exact use:
  - author explicitly warns against overusing critical composition tags such as `close-up`, `upside-down`, `cowboy shot` because conflicts can confuse the model;
  - recommends choosing suitable composition tags such as `upper body`, `cowboy shot`, `portrait`, `full body` depending on use.
- Product implication:
  - same-role composition tags should be replacement candidates, not accumulated by default.

### B08 — NoobAI XL 1.1 model card

- Model: `Laxhar/noobai-XL-1.1`
- URL: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Language: English
- Class: `FACT_EXACT_MODEL`
- Exact use:
  - native caption order: `<count>, <character>, <series>, <artists>, <special tags>, <general tags>, <other tags>`;
  - exact positive/Negative baseline examples.
- Product implication:
  - pruning/reordering must not erase the model's documented structural lane distinction;
  - Special-before-General is a model-specific baseline, not a global order rule.

### B09 — NoobAI XL 1.1 CLIP configs

- URLs:
  - https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/text_encoder/config.json
  - https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/text_encoder_2/config.json
- Language: configuration JSON
- Class: `FACT_EXACT_MODEL`
- Exact use:
  - both CLIP text encoder configs declare `max_position_embeddings: 77`.
- Product caution:
  - this is an encoder architecture fact, not a proof that Forge/A1111 rejects prompts beyond 77 tokens; web UI chunking changes effective handling.

### B10 — Anima model card

- Model: `circlestone-labs/Anima`
- URL: https://huggingface.co/circlestone-labs/Anima
- Language: English
- Class: `FACT_EXACT_MODEL`
- Exact use:
  - random tag dropout was used;
  - author says every single relevant tag does not need to be included;
  - natural-language mode benefits from sufficient description and extremely short pure-NL prompts can behave unexpectedly;
  - multiple characters especially benefit from naming plus basic appearance descriptions;
  - tag and natural language can be mixed.
- Product implication:
  - Anima gives exact evidence against `include every relevant tag`;
  - but it also rejects the opposite simplification `make every prompt as short as possible`;
  - pruning must be information-aware and mode-aware.

### B11 — Anima whitespace author discussion

- Discussion: https://huggingface.co/circlestone-labs/Anima/discussions/57
- Language: English
- Class: `AUTHOR_STATEMENT` where author/team comment is identified; otherwise discussion material is `PRACTICAL`
- Key use:
  - author notes comma/space formatting matters under Anima's LLM text encoder in ways that differ from SDXL-style handling.
- Product implication:
  - formatting is part of model-family prompt knowledge and must not be removed as mere cosmetic whitespace during pruning.

### B12 — Anima long-prompt discussion

- Discussion: https://huggingface.co/circlestone-labs/Anima/discussions/140
- Language: English
- Class: `PRACTICAL` unless an author/team statement is explicitly separated
- Key use:
  - users report tag-based structure plus limited targeted natural language can outperform large unstructured descriptions for some compositions;
  - long environment description can overpower framing in reported cases;
  - reports are observational, not a universal paragraph threshold.
- Product implication:
  - concept strength/competition matters more than a hard character/token count.

---

## WebUI / encoder handling evidence

### B13 — AUTOMATIC1111 infinite prompt length / BREAK

- Official wiki: https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features
- Language: English
- Class: `FACT_TOOL`
- Key use:
  - A1111 processes text beyond standard 75 prompt tokens as additional 75-token chunks;
  - `BREAK` starts a new chunk by padding the current one.
- Product implication:
  - `>75 tokens = truncated/invalid` is not a valid A1111-style WebUI assumption;
  - prompt edits that cross chunk boundaries can alter encoding structure.

### B14 — Forge prompt word-wrap option

- Forge source: https://github.com/lllyasviel/stable-diffusion-webui-forge/blob/main/modules/shared_options.py
- Language: code
- Class: `FACT_TOOL`
- Key use:
  - Forge includes a prompt word-wrap/chunk setting around the 75-token chunk boundary.
- Product implication:
  - exact local Forge Neo build/runtime behavior must be captured before interpreting token-count experiments;
  - chunk layout is a confound when prompt pruning/reordering changes token boundaries.

### B15 — Forge discussion on chunk boundaries

- URL: https://github.com/lllyasviel/stable-diffusion-webui-forge/discussions/2899
- Language: English
- Class: `COMMUNITY_TOOL_OBSERVATION`
- Key use:
  - discussion illustrates that commas/BREAK/chunk boundaries can change output in practice.
- Do not infer:
  - a universal superior BREAK strategy.

---

## Japanese controlled/practical evidence

### B16 — Fixed-seed conflicting frame tags

- Title: `NovelAIで構図が勝手に寄るときの直し方｜画角タグを先に固定する`
- URL: https://note.com/itsuki_ailab/n/n298758cec98e
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL` for the shown pair
- Key use:
  - same seed and settings; `full body` alone compared against `close-up, cowboy shot, full body`;
  - adding conflicting same-role frame tags cropped the lower body in the shown pair.
- Limitation:
  - one seed / one pair proves a concrete failure example, not a success-rate estimate.

### B17 — Anima hybrid Prompt structure test

- Title: `Animaに有効なプロンプトの構造を検証しました`
- URL: https://note.com/nemhiyo/n/n82455e6f9519
- Language: Japanese
- Class: `PRACTICAL`
- Key use:
  - practical comparison of tags, natural language, and a structured builder approach;
  - supports separating tag strengths from relation/layout language rather than blindly maximizing either.
- Limitation:
  - not an author source; exact controlled sample count/seed design should be inspected per claim before upgrading confidence.

### B18 — Anima tags + one English sentence, fixed-seed comparison

- Title: `Anima のプロンプトは「タグ＋英文 1 文」が効く。同シード比較で分かった書き方 2 つ、罠 2 つ、効かなかった 1 つ`
- URL: https://note.com/ai_on_desk/n/n553eac75840d
- Environment reported:
  - Anima-Aesthetic v1.1
  - fixed seed/settings
  - one-location changes in comparisons
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL` for the shown pairs
- Key use:
  - targeted relation/action sentence can add information not reliably carried by flat tags;
  - actor references in natural language can interfere with tag-defined character identity depending on phrasing.
- Product implication:
  - pruning should preserve high-information relational structure while removing low-information redundancy.

### B19 — Anima format comparison

- Title: `AnimaとKrea2、プロンプト形式でイラストはどう変わる？｜タグ・両方・自然文を同条件で比較`
- URL: https://note.com/tasty_cougar8018/n/n10b362494efd
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL` for shown same-seed/settings format comparisons
- Key use:
  - in reported Anima cases, tag-only, natural-language-only, and hybrid formats produce materially different action/composition/style behavior.
- Limitation:
  - small scenario set; do not generalize to all relation prompts.

### B20 — Illustrious practical prompt construction

- Title: `SDXL（Illustrious）におけるプロンプトの組み方`
- URL: https://note.com/asugonomi/n/nb16950a0549d
- Language: Japanese
- Class: `PRACTICAL`
- Key use:
  - practical warning that framing choice can make off-frame clothing/shoe tags undesirable or produce odd artifacts;
  - supports context-aware pruning of details that cannot be visible under chosen frame.
- Product implication:
  - a tag can be semantically true of the subject but operationally unnecessary/conflicting for the chosen view.

---

## Multilingual evidence handling

### B21 — Korean rendering of Japanese quality-tag comparison

- URL: https://note.com/drawthingsguide/n/n49f84ee6804f?hl=ko
- Language: Korean rendering of Japanese source
- Class: same underlying evidence as original, not independent confirmation
- Key use:
  - reminder that quality tags can alter composition/style, so they are not transparent quality switches.

### B22 — Chinese Anima prompt-rule repositories

- Example: https://github.com/shuaixn/anima-prompt-writing/blob/main/references/prompt-rules.md
- Language: Chinese
- Class: `PRACTICAL_GUIDE / COMMUNITY`, not author evidence
- Key use:
  - illustrates real-world efforts to reduce duplicate/synonymous concepts and preserve one high-information representation.
- Product use:
  - hypothesis support only; exact model card and controlled tests outrank it.

---

## Source-discipline conclusions

1. **Minimum sufficient is not minimum token count.** Primary research supports preserving structural language for binding while reducing competing concepts.
2. **Exact model guidance can directly justify pruning classes.** WAI v17 warns against excess quality/aesthetic/Negative content; Illustrious warns against conflicting composition tags; Anima says every relevant tag need not be supplied.
3. **Very short can also be wrong.** Anima's model card explicitly warns against extremely short pure-NL prompts and asks for enough description in that mode.
4. **A1111/Forge-style chunking invalidates a simple 75-token hard cutoff rule.** Chunk boundaries are a tool-level confound.
5. **One fixed-seed pair is good causal/counterexample evidence but not reliability evidence.** Use predetermined multi-seed ablations before promoting a support-removal rule.
6. **Broad + specific remains under-evidenced.** No strong exact-family source found that justifies always adding the parent or always deleting it. Keep pairwise empirical evaluation as `TEST_REQUIRED`.
7. **Community “best prompt” templates were not accepted as FACT.** They may inform hypotheses only.
