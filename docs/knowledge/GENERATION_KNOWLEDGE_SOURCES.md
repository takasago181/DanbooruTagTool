# Generation Knowledge Source Registry

Owner: Issue #44

This registry records sources separately from conclusions so future chats can re-check evidence strength, version scope, and language rather than inheriting uncited claims.

## Source ranking

1. exact checkpoint/version author model card or repository
2. author/team statement for the exact family/version
3. peer-reviewed/primary research
4. controlled practical comparison
5. practical corroboration
6. community observation
7. hypothesis

Language is not a rank.

---

## Exact model / author sources

### WAI Illustrious v17

**S-WAI-001**
- URL: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- Language: English / some multilingual text
- Class: `FACT_EXACT_MODEL`
- Scope: `waiIllustriousSDXL_v170`
- Key claims:
  - Steps 15-30
  - CFG 5-7
  - Euler a
  - original dimensions larger than 1024x1024 area; example 1024x1344
  - example quality prefix `masterpiece,best quality,amazing quality`
  - example negative `bad quality,worst quality,worst detail,sketch,censor`
  - warns against excessive quality/aesthetic tags and overly long negatives
  - documents Hires 1.5 / 20 hires steps / Anime6B / denoise 0.35-0.5
  - v17 explicitly attempts to improve Hires limb correction
- Audit consequence: Hires is not a neutral evidence-preserving pass; giant quality/negative stacks are not an exact-v17 default.

### Illustrious XL early

**S-ILL-001**
- URL: https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0
- Language: English
- Class: `FACT_EXACT_MODEL`
- Scope: Illustrious XL early release
- Key claims:
  - official quality vocabulary
  - Booru-oriented prompting
  - critical composition tags such as close-up / cowboy shot should not be overused or conflicted
  - examples include upper body / cowboy shot / portrait / full body
- Audit consequence: contradictory frame tags are Prompt conflict evidence, not Special-semantic evidence.

**S-ILL-002**
- URL: https://arxiv.org/abs/2409.19946
- Language: English
- Class: `FACT_GENERAL` / primary model paper
- Scope: Illustrious architecture/dataset/captioning context
- Key claims:
  - multi-level captioning combines tags and natural-language information
  - simple tag representations have limitations for complex relations/context
- Audit consequence: relation/composite semantics may require more than independent unary tags; do not infer exact downstream checkpoint behavior from the paper alone.

### NoobAI XL 1.1 EPS

**S-NOOB-EPS-001**
- URL: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Language: English
- Class: `FACT_EXACT_MODEL`
- Scope: NoobAI XL 1.1 EPS
- Key claims:
  - CFG 5-6
  - Steps 25-30
  - Euler a
  - resolution families around 1024^2
  - native caption order: count -> character -> series -> artist -> special -> general -> other
  - official quality/date/aesthetic tag scheme
  - official negative includes `bad hands`, `mutated hands`; broad `bad anatomy/extra limbs/extra arms` are not established as mandatory exact-model defaults
- Audit consequence: Special-before-General is strong exact structural evidence; exact camera placement remains unresolved.

### NoobAI V-Pred

**S-NOOB-VP-001**
- URL: https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blob/main/README.md
- Language: English
- Class: `FACT_EXACT_MODEL`
- Scope: NoobAI XL V-Pred 1.0
- Key claims:
  - explicitly distinct from EPS prediction
  - requires its own inference parameter regime
  - native Danbooru/e621 caption context
- Audit consequence: do not transfer EPS tuning claims into V-Pred or vice versa.

### Anima

**S-ANIMA-001**
- URL: https://huggingface.co/circlestone-labs/Anima
- Language: English
- Class: `FACT_EXACT_MODEL`
- Scope: Anima family / current model card
- Key claims:
  - 2B illustration-oriented model
  - trained on anime + artistic data
  - Danbooru-style tags and natural-language usage
  - profile-specific behavior exists
- Audit consequence: family-specific grammar and profiles must be kept separate from Illustrious-derived assumptions.

**S-ANIMA-002**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/99
- Language: English
- Class: `COMMUNITY` / official-hosted discussion
- Scope: direction/orientation practical behavior
- Key observations:
  - left/right and hand-direction ambiguity
  - strong Booru concepts can conflict with natural-language geometry
  - seed sensitivity reported
- Limitation: discussion evidence; exact deterministic rule not established.

**S-ANIMA-003**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/120
- Language: English
- Class: `COMMUNITY`
- Scope: multiple-character binding
- Key observations:
  - attribute bleed / poor binding at 3-4 characters
  - regional prompting suggested for difficult cases
- Limitation: not an official success-rate benchmark.

**S-ANIMA-004**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/140
- Language: English
- Class: `PRACTICAL` / community
- Scope: tags vs natural language
- Key observations:
  - tag-only can be structurally cleaner in reported tests
  - longer NL can add detail but may increase anatomy/hand problems
  - environment-heavy NL can overpower framing
  - hybrid tag + short relation sentence remains a useful candidate
- Limitation: not exact official rule.

**S-ANIMA-005**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/136
- Language: English
- Class: `PRACTICAL` / official-hosted discussion
- Scope: trigger spelling / tag naming
- Key observation: older/Gelbooru-style spelling can activate learned concepts differently from newer Danbooru spelling in some cases.
- Audit consequence: model trigger spelling must not overwrite database canonical identity.

---

## Primary research / mechanism sources

**S-RESEARCH-001 — ConceptMix**
- URL: https://arxiv.org/abs/2408.14339
- Language: English
- Class: `FACT_GENERAL`
- Scope: compositional T2I evaluation
- Key claim: compositional performance, especially for open models, drops substantially as the number of requested concepts increases.
- Audit consequence: record concept/relationship load; do not simplify to a universal token-length threshold.

**S-RESEARCH-002 — Attend-and-Excite**
- URL: https://arxiv.org/abs/2301.13826
- Mirror/implementation: https://github.com/yuval-alaluf/Attend-and-Excite
- Language: English
- Class: `FACT_GENERAL`
- Scope: diffusion concept omission / binding
- Key claims:
  - catastrophic neglect: requested subjects may disappear
  - attribute binding can attach attributes to the wrong subject
- Audit consequence: AB failure does not prove A or B is unknown; test A_ONLY / B_ONLY first.

**S-RESEARCH-003 — ControlNet**
- URL: https://arxiv.org/abs/2302.05543
- ICCV: https://openaccess.thecvf.com/content/ICCV2023/html/Zhang_Adding_Conditional_Control_to_Text-to-Image_Diffusion_Models_ICCV_2023_paper.html
- Language: English
- Class: `FACT_GENERAL`
- Scope: assisted spatial conditioning
- Key claims: pose/depth/edge/segmentation and other controls can impose spatial conditioning on diffusion generation.
- Audit consequence: ControlNet/OpenPose success belongs to an assisted-control lane and cannot certify Prompt-only capability.

**S-RESEARCH-004 — Negative prompt mechanism backlog**
- Class: `FACT_GENERAL` / mechanism research
- Scope: negative conditioning can actively suppress concepts rather than acting as neutral cleanup.
- Corpus status: mechanism accepted as high-risk rationale; exact family-specific anatomy-negative effects remain HOLD until controlled image evidence.
- Maintenance note: preserve exact paper references in future research batch when family-specific claims are added; do not turn broad mechanism into a fixed Negative list.

---

## Tool / post-processing sources

**S-TOOL-001 — ADetailer**
- URL: https://github.com/Bing-su/adetailer/blob/main/README.md
- Language: English
- Class: `FACT_GENERAL` for tool mechanism
- Key claims:
  - generate image -> detect target -> create mask -> inpaint
  - ADetailer Prompt/Negative may differ from base Prompt
  - supports separate inpaint/control parameters
- Audit consequence: final image can be materially altered after base generation; store ADetailer state/settings when interpreting evidence.

**S-TOOL-002 — ADetailer multi-object prompt behavior**
- URL: https://github.com/Bing-su/adetailer/wiki/Advanced
- Language: English
- Class: `FACT_GENERAL` for tool behavior
- Key claim: `[SEP]` can assign different prompts to detected objects, but detection order is described as highly arbitrary.
- Audit consequence: object-order binding under ADetailer is not a stable semantic authority.

**S-TOOL-003 — Illustrious LoRA trainer evaluation guidance**
- URL: https://github.com/NEC-O/illustrious-lora-trainer/blob/main/docs/TRAINING_GUIDE.md
- Language: Chinese
- Class: `PRACTICAL`
- Key recommendations:
  - evaluate checkpoints with fixed Prompt/Seed
  - compare trigger / no-trigger
  - simple / complex background
  - different characters/clothing
  - trigger is not a hard on/off switch; loaded LoRA can affect output without trigger
- Audit consequence: LoRA evidence must record loaded LoRAs and weights even when trigger text is absent.

---

## Japanese practical evidence

**S-JA-001 — WAI v17 quality/meta practical comparison**
- URL: https://note.com/drawthingsguide/n/n49f84ee6804f
- Language: Japanese
- Class: `PRACTICAL`
- Scope: model/quality-tag comparison including WAI v17
- Key observation: quality tags can change face, hair, clothing, painting style, composition and camera proximity, not just perceived detail.
- Limitation: use as corroboration, not universal causal proof.

**S-JA-002 — conflicting frame tags controlled example**
- URL: https://note.com/itsuki_ailab/n/n298758cec98e
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL`
- Key controls: same seed/model/settings; compares `full body` against conflicting `close-up + cowboy shot + full body`.
- Key observation: conflicting frame instructions produced narrower crop in the shown example.
- Limitation: one seed / one image per condition.

**S-JA-003 — location-tag comparison across derivative families**
- URL: https://note.com/mith_mmk/n/ne833c441c99f
- Language: Japanese
- Class: `PRACTICAL`
- Scope: large practical tag comparison across Pony/Illustrious derivatives
- Value: useful for candidate tag exposure hypotheses, not exact WAI v17 authority.

**S-JA-004 — WAI series fixed-seed practical comparison**
- URL: https://note.com/novapen_create/n/nf4a63d6e94e6
- Language: Japanese
- Class: `PRACTICAL`
- Key controls: fixed seed / prompt / sampler/CFG in reported comparison.
- Scope: WAI v16 and related versions, not exact v17.
- Use: cross-version practical behavior only; do not transfer as v17 FACT.

**S-JA-005 — Anima style prompt controlled practical test**
- URL: https://note.com/ai_0049/n/n74ccab5370e0
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL`
- Scope: Anima, same-seed style-prompt comparisons
- Use: evidence that common natural-language/style phrases vary in strength and cannot be assumed equivalent to trained tags.

**S-JA-006 — Anima tag vs NL vs hybrid**
- URL: https://note.com/tasty_cougar8018/n/n10b362494efd
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL`
- Scope: Anima and comparison model; same content expressed as tags / natural language / both with fixed seed/parameters.
- Use: supports keeping tag-only / short-hybrid / NL as separate experimental variables.

---

## Korean practical evidence

**S-KO-001 — WAI v17 asymmetric/local attribute difficulty**
- URL: https://crowsaint.tistory.com/entry/TensorAI%ED%95%A0%EB%A6%AC%ED%80%B8-%EB%A7%8C%EB%93%A4%EA%B8%B03%EC%B0%A8
- Language: Korean
- Class: `PRACTICAL`
- Scope: exact reported WAI v17 settings in one practical task
- Key observation: local/asymmetric hair-color assignment remained difficult despite explicit prompting.
- Limitation: practical case study, not controlled benchmark.

**S-KO-002 — Anima practical setup/prompt summary**
- URL: https://onebrotravel.tistory.com/entry/ComfyUI-%EC%B4%88%EA%B0%84%EB%8B%A8-%EC%9E%85%EB%AC%B8%EA%B0%80%EC%9D%B4%EB%93%9C-%E2%80%94-Anima%EB%A1%9C-%EC%B2%AB-%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%83%9D%EC%84%B1
- Language: Korean
- Class: `PRACTICAL_CORROBORATION`
- Scope: Anima tag order, spaces vs underscore, Gelbooru preference, tag dropout, tag/NL mixture.
- Use: multilingual corroboration of official guidance; official model card remains authority.

---

## Chinese practical evidence

**S-ZH-001 — Illustrious LoRA trainer guide**
- URL: https://github.com/NEC-O/illustrious-lora-trainer/blob/main/docs/TRAINING_GUIDE.md
- Language: Chinese
- Class: `PRACTICAL`
- Scope: Illustrious LoRA training/evaluation
- Key value: fixed prompt/seed checkpoint comparison; trigger/no-trigger contamination test; simple/complex background; different character/clothing checks.

**S-ZH-002 — Anima prompt-writing practical rules**
- URL: https://github.com/shuaixn/anima-prompt-writing/blob/main/references/prompt-rules.md
- Language: Chinese
- Class: `PRACTICAL`
- Scope: Anima prompting
- Use: candidate rules and multilingual corroboration only; not author authority.

---

## Evaluator/tagger sources to maintain after dictionary freeze

These are intentionally not treated as complete Special ground truth.

**S-EVAL-001 — WD EVA02 large tagger v3**
- URL: https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3
- Class: `FACT_EXACT_MODEL` for evaluator vocabulary/model card
- Known limitation relevant to project: rare tags below its training-frequency filter cannot be assumed covered.
- Use: high-throughput unary-tag evidence only; unsupported/low-confidence cases route to REVIEW.

**S-EVAL-002 — Kagami-24k**
- URL: https://huggingface.co/Redstonexs/kagami-24k
- Class: `FACT_EXACT_MODEL` for evaluator scope
- Use: broad-vocabulary candidate after final Special dictionary freeze; vocabulary breadth is not proof of rare-tag accuracy.

**S-EVAL-003 — CL Tagger v2**
- URL: https://huggingface.co/cella110n/cl_tagger_v2
- Language: Japanese/English documentation
- Class: `FACT_EXACT_MODEL` for evaluator scope
- Use: broad-vocabulary candidate with tag-level calibration/OOD information; must be empirically compared against final Special dictionary and human labels.

---

## Source maintenance rules

- Pin exact model/version or commit when a claim becomes promotion-critical.
- If a source is updated in place, record the retrieval date and compare changed guidance before replacing old conclusions.
- A downstream fine-tune or different prediction regime is not interchangeable with its base model.
- A Japanese/Chinese/Korean practical article may be more useful than generic English community advice when it gives exact model/settings/seed, but it still does not outrank exact author evidence.
- When two credible sources conflict, record the conflict and move the material conclusion to HOLD until the scope/version difference is resolved.

---

## 2026-10-02 public community evidence harvest

These sources are intentionally lower authority than exact author/runtime documentation. They are retained because they publish useful A/B structure, sample counts, failure cases, or multilingual practical experience.

**S-COMM-001 — Anima two-character leakage, 16-image A/B**
- URL: https://note.com/stray_dog0012/n/n74ad8ac4582f
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: Anima multi-character attribute leakage
- Value: separates flat tags vs natural-language grouping and tests the claimed left-side separator independently.
- Limitation: small sample and community setup; exact project checkpoint is not pinned.

**S-COMM-002 — Anima Prompt surface, 256-image comparison**
- URL: https://note.com/tasty_cougar8018/n/na0979098fa50
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: Anima Aesthetic v1.1 tags vs natural language vs mixed vs tag+supplement.
- Value: unusually large public comparison with fixed setup and scene-type breakdown.
- Limitation: human scoring / one profile and workflow.

**S-COMM-003 — Anima sampler/CFG, 21-image comparison**
- URL: https://note.com/stray_dog0012/n/n949c921640f8
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: sampler/CFG visual response
- Value: attempts measured line/detail differences rather than pure preference.
- Limitation: metrics are local and not a universal quality score.

**S-COMM-004 — Anima one-tag uniform behavior, 194 images**
- URL: https://note.com/tasty_cougar8018/n/nfc1d6a8cf973
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: garment/uniform tag generation behavior
- Value: direct evidence that canonical semantic scope and learned visual effect differ; includes a rerun after discovering prompt-context confounding.
- Limitation: exact profile and style context matter.

**S-COMM-005 — Anima fisheye/perspective, 30-image controlled test**
- URL: https://note.com/tasty_cougar8018/n/n8264b41bc5fa
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: existing tags vs descriptive perspective wording
- Value: author documents an initial confounded result and reruns after removing the overlap.
- Limitation: one profile / five scenes.

**S-COMM-006 — WAI-Anima Negative Prompt same-seed pairs**
- URL: https://note.com/ai_on_desk/n/nfa078139f8c6
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: targeted Negative additions / absent-target side effects
- Value: same-seed pair design; directly useful for failure diagnosis.
- Limitation: WAI-Anima v1.0 derivative; does not close official Anima/WAI/Noob Negative HOLDs.

**S-COMM-007 — WAI-Anima multi-character LoRA failure decomposition**
- URL: https://note.com/kla_cla/n/n801437941d2e
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: two custom character LoRAs, attribute leakage vs ownership swap
- Value: sequentially changes LoRA weights and prompt redundancy and reports 3/4 failure frequencies.
- Limitation: the author's architectural explanation is hypothesis; only observed behavior is promoted.

**S-COMM-008 — same-dataset WAI/Anima LoRA retraining**
- URL: https://zenn.dev/ojisan_ai_lab/articles/lora-wai-anima-howto-20260722
- Language: Japanese
- Class: `PRACTICAL / COMMUNITY`
- Scope: 64-image shared source dataset, WAI vs Anima training
- Value: documents earlier style-entanglement failure and revised caption/dataset design.
- Limitation: one project; training throughput/VRAM values are environment-specific.

**S-COMM-009 — Anima LoRA timestep parameter experiments**
- URL: https://note.com/kuon_noise/n/na40804c255b5
- Language: Japanese
- Class: `RESEARCH_LEAD / COMMUNITY`
- Scope: timestep_sampling / sigmoid_scale / discrete_flow_shift
- Value: directly targets Anima-specific training variables and notes a prior GUI configuration issue.
- Limitation: exact experiment detail was not fully recoverable in the current harvest; do not promote directional conclusions yet.

**S-COMM-010 — Anima upscale / USDU user report**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1tvhmrm/what_are_your_experiences_in_upscaling_anima_with/
- Language: English
- Class: `PRACTICAL / COMMUNITY`
- Scope: upscale model / denoise sensitivity
- Value: concrete same-user thresholds and artifact descriptions useful for hypothesis design.
- Limitation: single-user recipe; numeric denoise values are not family rules.

**S-COMM-011 — Anima style-LoRA caption discussion**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1wq972q/training_a_style_lora_for_anima_a_few_tagging/
- Language: English
- Class: `COMMUNITY / CURRENT_DISCUSSION`
- Scope: style triggers, character tags, tag dropout, auto-tag cleanup
- Value: fresh 2026-09 discussion showing current practitioner disagreement.
- Limitation: anecdotal comments; no controlled benchmark.

**S-COMM-012 — NoobAI V-Pred style LoRA tint failure**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1vbsj8k/what_am_i_doing_wrong_in_my_lora_training/
- Language: English
- Class: `FAILURE_REPORT / COMMUNITY`
- Scope: 21-image V-Pred style LoRA
- Value: concrete unwanted global tint failure for dataset/caption debugging.
- Limitation: unresolved first-time trainer case; source-map only.

**S-COMM-013 — Anima Regional Conditioning user workflow**
- URL: https://note.com/hkmclab/n/n1526e44f4df9
- Language: Japanese
- Class: `PRACTICAL / COMMUNITY`
- Scope: masked per-region Anima conditioning
- Value: reproduces current workflow structure and documents a CFG-vs-region-boundary tradeoff in one setup.
- Limitation: effectiveness observation is single-user; runtime project documentation wins for supported behavior.

**S-COMM-014 — Anima dataset-noise/tagger discussion**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/201
- Language: English
- Class: `COMMUNITY / DATASET_HYPOTHESIS`
- Scope: Danbooru-style label noise from a tagger developer's large manual-cleaning experience
- Value: concrete noise families useful for generation/tagger failure hypotheses.
- Limitation: does not prove exact Anima training-set composition.

**S-COMM-015 — Chinese Illustrious LoRA cross-derivative practice**
- URL: https://www.bilibili.com/opus/1181478497372078082
- Language: Chinese
- Class: `PRACTICAL / COMMUNITY`
- Scope: Illustrious-trained LoRA tested across derivatives / NoobAI
- Value: ecosystem evidence that loadable cross-derivative use often requires weight/CFG adjustment.
- Limitation: compatibility is not guaranteed and is not promoted as a family fact.

**S-COMM-016 — Anima 108-style same-seed study**
- URL: https://note.com/ai_0049/n/n74ccab5370e0
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: 108 style phrases under fixed seed/minimal prompt.
- Value: separates output-change magnitude from actual style fidelity and catalogs spillover into pose/clothing/background.
- Limitation: visual/manual scoring and one base setup.

**S-COMM-017 — Anima Base 5–40 step sweep**
- URL: https://note.com/nobrain/n/ncc77e7c3452b
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: Anima Base v1.0 er_sde/simple/CFG4 fixed-seed step sweep.
- Value: concrete time/VRAM/convergence observation.
- Limitation: one seed / one simple scene / one GPU.

**S-COMM-018 — Anima composition tags vs prose**
- URL: https://note.com/tasty_cougar8018/n/n713f5a8c1218
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: framing/visibility.
- Value: direct example of face-closeup tags outperforming prose and of feet/ground context defeating close-up.
- Limitation: derivative checkpoint / small condition set.

**S-COMM-019 — Illustrious habits imported into WAI-Anima**
- URL: https://note.com/ai_on_desk/n/n72f6f4e58dfe
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: quality/Negative/CFG/underscore/weight/BREAK.
- Value: one-variable same-seed comparisons with reported pixel-difference measurements.
- Limitation: WAI-Anima v1.0 + ComfyUI 0.34.0; implementation-cause claims require code verification.

**S-COMM-020 — WAI-Anima multi-character grouping, 48 images**
- URL: https://note.com/ai_on_desk/n/n462ad57df450
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: tags-only positional/name/relative/depth grouping vs per-subject English sentences.
- Value: published success/failure counts across seeds and orientations plus 3-character extension.
- Limitation: visual scoring / one derivative.

**S-COMM-021 — WAI-Anima quality/meta and face-prior test**
- URL: https://note.com/ai_on_desk/n/na0edcfbebe28
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: quality tags / safe / explicit face descriptors.
- Value: same-seed one-variable comparison.
- Limitation: small condition count; broad causal interpretation not accepted.

**S-COMM-022 — Anima Base color-name sweep**
- URL: https://note.com/mith_mmk/n/ndcd5709f47ff
- Language: Japanese
- Class: `PRACTICAL / COMMUNITY`
- Scope: basic/CSS color lexical behavior.
- Value: direct lexical-collision examples and attached result files.
- Limitation: rough automated checking with acknowledged false positives.

**S-COMM-023 — Anima preview2 body-tag sweep**
- URL: https://note.com/mith_mmk/n/n8f06ec51fba5
- Language: Japanese
- Class: `DISCOVERY / COMMUNITY`
- Scope: broad body-tag coverage.
- Value: modern retest-candidate discovery.
- Limitation: stale preview2 + machine-analysis errors.

**S-COMM-024 — real-world swimwear vocabulary test**
- URL: https://note.com/stray_dog0012/n/n9ece9bc66aef
- Language: Japanese
- Class: `PRACTICAL / COMMUNITY`
- Scope: externally selected garment terminology under fixed scene/camera.
- Value: real-world vocabulary vs learned visual vocabulary research lead.
- Limitation: detailed per-item results need full re-extraction.

**S-COMM-025 — Anima LoRA auto-tag vs manual-adjustment lead**
- URL: https://note.com/azrakuc/n/n3d6d5eaa850e
- Language: Japanese
- Class: `RESEARCH_LEAD / COMMUNITY`
- Scope: LoRA caption/tag curation.
- Limitation: current public retrieval is incomplete/paid.

**S-COMM-026 — Illustrious aesthetic-tag 100-image run**
- URL: https://note.com/alayaproject/n/ned0a95fb3c86
- Language: Japanese
- Class: `PRACTICAL / COMMUNITY`
- Scope: broad aesthetic prompt pressure on semi-real Illustrious derivative.
- Limitation: heavily confounded by style LoRA and large prompt stack.

**S-COMM-027 — Anima long-prompt / hybrid HF discussion**
- URLs:
  - https://huggingface.co/circlestone-labs/Anima/discussions/140
  - https://huggingface.co/circlestone-labs/Anima/discussions/141
- Language: English
- Class: `COMMUNITY / MULTI_SOURCE`
- Scope: NL length/workload, hands/anatomy, background/framing pressure.
- Value: independent users converge on concise hybrid practice.
- Limitation: no controlled token-length benchmark.

**S-COMM-028 — Anima prompt-weighting HF discussion**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/135
- Language: English/Chinese
- Class: `COMMUNITY / MECHANISM_DISCUSSION`
- Scope: weighting strength and runtime/text-encoder interpretation.
- Value: corroborates high-weight practical behavior and exposes mechanism uncertainty.
- Limitation: conflicting explanations; author guidance wins.

**S-COMM-029 — Anima multi-character LoRA-training lead**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/222
- Language: English
- Class: `RESEARCH_LEAD / COMMUNITY`
- Scope: training single-character LoRAs with a few multi-character samples.
- Limitation: specific “two images” sufficiency claim is unverified.

**S-COMM-030 — Anima regional-control user feedback**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/193
- Language: English
- Class: `COMMUNITY / TOOL_FEEDBACK`
- Scope: LLLite Regional ControlNet.
- Limitation: effectiveness report lacks benchmark details.

**S-COMM-031 — Illustrious local-vs-web reproducibility failure**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1rpqc8z/why_are_my_illustrious_images_so_bad/
- Language: English
- Class: `FAILURE_REPORT / COMMUNITY`
- Scope: nominally same visible settings, different output.
- Value: hidden runtime/evidence-identity diagnostic example.
- Limitation: unresolved cause.

