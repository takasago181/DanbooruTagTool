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

**S-COMM-032 — Chinese Anima Standalone Trainer tutorial**
- URL: https://www.bilibili.com/video/BV1EyQHBWEnF/
- Language: Chinese
- Class: `ECOSYSTEM / COMMUNITY`
- Scope: Anima-specific LoRA trainer.
- Value: current dedicated-training-stack adoption.
- Limitation: speed headline is environment-specific.

**S-COMM-033 — Chinese Anima auto-tag/cloud LoRA workflow**
- URL: https://www.bilibili.com/video/BV1YNLE62E4o/
- Language: Chinese
- Class: `ECOSYSTEM / COMMUNITY`
- Scope: auto-tagging + cloud Anima LoRA training.
- Limitation: tutorial workflow, not controlled quality evidence.

**S-COMM-034 — Chinese Anima ControlNet practice**
- URL: https://www.bilibili.com/video/BV1pGGv6NEFx/
- Language: Chinese
- Class: `PRACTICAL / COMMUNITY`
- Scope: Anima LLLite pose/depth/inpaint.
- Value: assisted-control ecosystem evidence.

**S-COMM-035 — Chinese current open-source Anima trainer**
- URL: https://www.bilibili.com/video/BV14ehG64EAq/
- Language: Chinese
- Class: `ECOSYSTEM / COMMUNITY`
- Scope: current open-source LoRA training wrapper.
- Value: trainer evolution/freshness lead.

**S-COMM-036 — Korean Anima LoRA application guide**
- URL: https://onebrotravel.tistory.com/entry/ComfyUI-%EC%B4%88%EA%B0%84%EB%8B%A8-%EC%9E%85%EB%AC%B8%EA%B0%80%EC%9D%B4%EB%93%9C-%E2%80%94-Anima%EC%97%90-LoRA-%EC%A0%81%EC%9A%A9%ED%95%98%EA%B8%B0
- Language: Korean
- Class: `PRACTICAL_CORROBORATION`
- Scope: Anima-base-model filtering for LoRA resources.
- Value: multilingual compatibility-practice corroboration.

**S-COMM-037 — Korean visual Danbooru Prompt Gallery**
- URL: https://kwoon.tistory.com/122
- Language: Korean
- Class: `UX_ECOSYSTEM / COMMUNITY`
- Scope: thumbnail-first Danbooru prompt discovery in ComfyUI.
- Value: independent visual-discovery UX convergence.

**S-COMM-038 — Korean simplified Anima front-end / LoRA metadata**
- URL: https://gall.dcinside.com/mgallery/board/view/?id=wrtnai&no=1044018
- Language: Korean
- Class: `UX_ECOSYSTEM / COMMUNITY`
- Scope: simplified prompt UI, style presets, Civitai LoRA trigger/base metadata retrieval.
- Value: resource-discovery and metadata-management signal.

**S-COMM-039 — Korean Anima LoRA pipeline project**
- URL: https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1129120
- Language: Korean
- Class: `TECHNICAL_LEAD / COMMUNITY`
- Scope: Anima-specific LoRA training/optimization/timestep concepts.
- Limitation: source-code confirmation required for mechanism claims.

**S-COMM-040 — Korean low-resource Anima staged workflow**
- URL: https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1184244
- Language: Korean
- Class: `RECIPE / COMMUNITY`
- Scope: low-res Turbo -> upscale -> low-denoise refinement.
- Limitation: hardware-specific speed/values.

**S-COMM-041 — Korean Anima artist-mixing custom node**
- URL: https://gall.dcinside.com/mgallery/board/view/?id=wrtnai&no=1037870
- Language: Korean
- Class: `TOOL_LEAD / COMMUNITY`
- Scope: cross-attention artist mixing / compatibility constraints.
- Limitation: no controlled benchmark.

**S-COMM-042 — Anima character-LoRA caption comparison**
- URL: https://note.com/kuon_noise/n/n5bd44f5bb1fb
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: trigger-only vs reduced captions vs full tagger captions, simple/detailed inference.
- Value: direct evidence about trigger absorption vs independently controllable traits.
- Limitation: author's training regime / one main character family.

**S-COMM-043 — synthetic Anima-only character-LoRA training**
- URL: https://lilting.ch/articles/wai-anima-keichan-lora-training
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: 45-image epoch × inference-format evaluation.
- Value: synthetic-data convergence and inherited base-model correlation evidence.
- Limitation: one character / synthetic-source dataset / Turbo-assisted evaluation.

**S-COMM-044 — Anima 0/1/3 LoRA same-seed stack comparison**
- URL: https://note.com/fresh_macaw9581/n/n7a3a7f6ed1e7
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: fixed seed, no/one/three adapters.
- Value: incremental adapter interference example.
- Limitation: one scene and selected LoRAs.

**S-COMM-045 — Anima style-LoRA weight sweep**
- URL: https://note.com/fresh_macaw9581/n/nc7bf40b8429c
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: Model strength 0/0.4/0.7/1.0, fixed CLIP/seed/settings.
- Value: weight spillover into identity/clothing/light/background.
- Limitation: one LoRA; author's preferred value is not generalizable.

**S-COMM-046 — Anima 162-image parameter sweep**
- URL: https://note.com/tasty_cougar8018/n/n7315197114a6
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: CFG / steps / shift / sampler on Aesthetic v1.1.
- Value: one-variable sweeps across two fixed scenes; includes measured timing.
- Limitation: subjective image-quality judgement / profile-local.

**S-COMM-047 — iterative 49→61-image character-LoRA repair**
- URL: https://note.com/ai_on_desk/n/nfed78c91d76a
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: WAI-Anima character-LoRA, first-pass residual body failure, second-pass targeted dataset recuration.
- Value: detailed failure-driven dataset iteration and leakage notes.
- Limitation: one character / cloud trainer / mostly synthetic data.

**S-COMM-048 — Anima Highres Boost 279-image test**
- URL: https://note.com/tasty_cougar8018/n/nf4cff0c56535
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: Highres/Aesthetic Boost v1.0, 9 strengths × 3 resolutions × multiple scenes/seeds.
- Value: resolution-dependent adapter behavior and excessive-weight failure.
- Limitation: one runtime/workflow and visually selected scenes.

---

## 2026-10-02 adult-generation structural sources

**S-ADULT-001 — NoobAI XL 1.1 author content baseline**
- URL: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Class: `AUTHOR_GUIDE / EXACT_MODEL`
- Value: SFW-oriented safe/nsfw default, native Danbooru+e621 caption context, exact caption order and baseline settings.
- Current remote checkpoint SHA256: `6681e8e4b134c81f16533acedb0d406d7e5e366e1624b4105178c64d00b05d51`.

**S-ADULT-002 — WAI Illustrious v17 rating surfaces**
- URL: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- Class: `AUTHOR_GUIDE / EXACT_MODEL`
- Value: four rating surfaces and author filtering guidance; baseline/Hires settings.

**S-ADULT-003 — Anima official safety/prompting card**
- URL: https://huggingface.co/circlestone-labs/Anima
- Class: `AUTHOR_GUIDE / EXACT_FAMILY`
- Value: tag/NL mixture, safety surfaces, stronger weighting behavior and multi-character guidance.

**S-ADULT-004 — Anima censorship/watermark discussion**
- URLs:
  - https://huggingface.co/circlestone-labs/Anima/discussions/104
  - https://huggingface.co/circlestone-labs/Anima/discussions/132
  - https://huggingface.co/circlestone-labs/Anima/discussions/162
- Class: `COMMUNITY / MULTI_SOURCE`
- Value: repeated reports that artist/concept priors can carry censor/watermark artifacts that resist targeted Negatives.
- Limitation: mechanism attribution remains community-level.

**S-ADULT-005 — Anima adult relation-caption community practice**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/141
- Class: `COMMUNITY / PRACTICAL`
- Value: stable subject-ID and relation-focused caption workflow for complex adult multi-subject scenes.
- Limitation: explicit user system prompt is not copied into project knowledge; only the structural method is retained.

**S-ADULT-006 — Anima long-NL / structure discussion**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/140
- Class: `COMMUNITY / PRACTICAL`
- Value: reports of tag-first vs long-NL anatomy/framing tradeoffs relevant to complex adult relation scenes.

**S-RESEARCH-005 — T2I-CompBench**
- URL: https://arxiv.org/abs/2307.06350
- Class: `RESEARCH`
- Scope: attribute binding / spatial / non-spatial / complex composition.
- Value: supports predicate-level separation of presence, binding and relation.

**S-RESEARCH-006 — CompAlign / CompQuest**
- URL: https://arxiv.org/abs/2505.11178
- Class: `RESEARCH`
- Scope: 3+ subject numeracy / 3D relation / attribute-binding evaluation.
- Value: atomic sub-question evaluation for complex generation.

**S-RESEARCH-007 — T2I-FineEval**
- URL: https://arxiv.org/abs/2503.11481
- Class: `RESEARCH`
- Scope: fine-grained compositional evaluation.
- Value: aggregate similarity metrics can hide relation/binding failures.

**S-TOOL-004 — ComfyUI LoRA/model masking and scheduling**
- URL: https://blog.comfy.org/p/masking-and-scheduling-lora-and-model-weights
- Class: `OFFICIAL_RUNTIME`
- Scope: spatial LoRA masking and denoising-step scheduling.
- Value: independent spatial/time control axes for adapter interference experiments.

**S-TOOL-005 — FreeFuse**
- URL: https://github.com/yaoliliu/FreeFuse
- Class: `RESEARCH_TOOL`
- Scope: training-free multi-subject LoRA routing.
- Value: spatial adapter routing as a multi-LoRA contamination mitigation hypothesis.
- Limitation: do not assume Anima support from current public implementation.

**S-COMM-049 — Anima single multi-character LoRA dataset design**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/220
- Class: `COMMUNITY / TRAINING_PRACTICE`
- Scope: joint-image dataset design, feature bleed, subset balancing.
- Value: explicit distinction between genuine interaction examples and stitched composites.
- Limitation: exact sample/repeat recommendations are single-practitioner recipes.

**S-COMM-050 — Anima multi-LoRA coexistence training lead**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/222
- Class: `COMMUNITY / RESEARCH_LEAD`
- Scope: adding joint examples to separate character-LoRA datasets.
- Value: direct-coexistence training hypothesis.
- Limitation: claimed minimum sample count unverified.

**S-COMM-051 — Anima background-entanglement training discussion**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/162
- Class: `COMMUNITY / FAILURE_DIAGNOSIS`
- Scope: persistent background prior / captioning / optimizer discussion.
- Value: concrete context-entanglement troubleshooting.
- Limitation: multiple training variables changed.

**S-COMM-052 — Anima character-LoRA generalization failure**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/119
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: 46-image multi-angle dataset with poor non-frontal identity generalization.
- Value: angle/image-count diversity alone does not guarantee generalization.
- Limitation: unresolved cause / preview model.

**S-COMM-053 — Anima training-caption format discussion**
- URLs:
  - https://huggingface.co/circlestone-labs/Anima/discussions/105
  - https://huggingface.co/circlestone-labs/Anima/discussions/205
- Class: `COMMUNITY / TRAINING_PRACTICE`
- Scope: Danbooru vs mixed NL captions / official ordering.
- Limitation: practitioner advice, not author-prescribed universal training format.

**S-TOOL-006 — Forge Neo NegPiP (archived Anima path)**
- URL: https://github.com/Haoming02/sd-forge-negpip
- Class: `OFFICIAL_RUNTIME / ARCHIVED`
- Scope: Forge Classic/Neo, SD1/SDXL/Anima.
- Value: documents negative-in-positive conditioning for Anima.
- Freshness: repository archived 2026-09-30; pin local commit before use.

**S-TOOL-007 — NegPiP upstream**
- URL: https://github.com/hako-mikan/sd-webui-negpip
- Class: `OFFICIAL_RUNTIME`
- Scope: negative-effect prompt conditioning.
- Value: mechanism and runtime semantics for NegPiP.
- Limitation: exact Forge-Neo-Anima compatibility is branch/integration specific.

**S-TOOL-008 — TrainTrain**
- URL: https://github.com/hako-mikan/sd-webui-traintrain
- Class: `OFFICIAL_RUNTIME`
- Scope: LoRA/iLECO/differential training; Forge Neo Anima support from 2026-09-04.
- Value: current local-training route and documented architecture constraints.

**S-COMM-054 — Anima censor/watermark prior cluster**
- URLs:
  - https://huggingface.co/circlestone-labs/Anima/discussions/94
  - https://huggingface.co/circlestone-labs/Anima/discussions/104
  - https://huggingface.co/circlestone-labs/Anima/discussions/152
  - https://huggingface.co/circlestone-labs/Anima/discussions/132
- Class: `COMMUNITY / MULTI_SOURCE_FAILURE`
- Scope: watermark/censorship/text persistence under Negative Prompt.
- Value: positive-prior/context-entanglement hypothesis.
- Limitation: no controlled universal frequency estimate.

**S-NOOB-EXACT-001 — NoobAI XL 1.1 exact file / dataset card**
- URLs:
  - https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
  - https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/NoobAI-XL-v1.1.safetensors
- Class: `AUTHOR_GUIDE / OFFICIAL_MODEL`
- Scope: EPS 1.1 settings, dataset window, ControlNet, checkpoint SHA.
- EPS SHA256: `6681e8e4b134c81f16533acedb0d406d7e5e366e1624b4105178c64d00b05d51`.

**S-NOOB-EXACT-002 — NoobAI XL V-Pred 1.0 exact file**
- URL: https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blame/main/NoobAI-XL-Vpred-v1.0.safetensors
- Class: `OFFICIAL_MODEL`
- Scope: V-Pred exact checkpoint identity.
- SHA256: `ea349eeae87ca8d25ba902c93810f7ca83e5c82f920edf12f273af004ae02819`.

**S-RESEARCH-008 — Whole-body pose / DWPose**
- URLs:
  - https://arxiv.org/abs/2007.11858
  - https://arxiv.org/abs/2307.15880
- Class: `RESEARCH`
- Scope: dense body/hand/face/foot keypoint estimation.
- Value: clarifies what pose control can encode and what semantic relation it cannot.

**S-TOOL-009 — ComfyUI preprocessor workflows**
- URL: https://blog.comfy.org/p/preprocessor-and-frame-interpolation
- Class: `OFFICIAL_RUNTIME`
- Scope: depth / lineart / pose / normals preprocessing.
- Value: reusable inspected preprocessing as separate evidence stage.

**S-TOOL-010 — ComfyUI masked inpaint example**
- URL: https://docs.comfy.org/tutorials/api-nodes/openai/gpt-image-1
- Class: `OFFICIAL_RUNTIME`
- Scope: image + mask local editing.
- Value: supports keeping local reconstruction separate from base generation.

**S-RESEARCH-009 — T2ICountBench**
- URL: https://arxiv.org/abs/2503.06884
- Class: `RESEARCH`
- Scope: numerical adherence / count-specific T2I evaluation.
- Value: exact count degrades with count and is not reliably repaired by simple prompt refinement.

**S-RESEARCH-010 — PreciseCam**
- URL: https://arxiv.org/abs/2501.12910
- Class: `RESEARCH`
- Scope: explicit intrinsic/extrinsic camera control.
- Value: demonstrates camera geometry as a control axis distinct from semantic text.

**S-RESEARCH-011 — Viewpoint Tokens**
- URL: https://arxiv.org/abs/2604.19954
- Class: `RESEARCH`
- Scope: learned parametric camera/viewpoint tokens.
- Value: corroborates limits of natural-language-only precise camera control.

**S-RESEARCH-012 — HandCraft**
- URL: https://arxiv.org/abs/2411.04332
- Class: `RESEARCH`
- Scope: local malformed-hand detection/restoration using mask + depth.
- Value: local anatomy repair without redoing the whole composition.

**S-RESEARCH-013 — HanDiffuser**
- URL: https://arxiv.org/abs/2403.01693
- Class: `RESEARCH`
- Scope: hand shape/joint/orientation/articulation conditioning.
- Value: richer hand-defect taxonomy than generic “bad hands”.

**S-RESEARCH-014 — Person-In-Situ**
- URL: https://arxiv.org/abs/2505.04052
- Class: `RESEARCH`
- Scope: pose-controlled human insertion with scene-consistent occlusion/depth.
- Value: separates skeleton pose from depth/layer/occlusion correctness.

**S-COMM-055 — Anima pairwise character-interference thread**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/93
- Class: `COMMUNITY / FAILURE_DIAGNOSIS`
- Scope: two-character pairings, descriptions, series/concept leakage.
- Value: A/B work alone but pair can fail; one scoped weighting mitigation.

**S-COMM-056 — Anima 3–4 subject binding stress**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/120
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: 3–4 identities with position/outfit/object constraints.
- Value: practical stress-class evidence and regional-prompt escalation signal.

**S-COMM-057 — Anima interaction-heavy adult feedback**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/13
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: interaction, subject-linked attribute swaps, unusual-concept control.
- Value: role/body-site ownership must be evaluated separately from subject presence.

**S-COMM-058 — Illustrious multi-character Reddit workflow cluster**
- URLs:
  - https://www.reddit.com/r/StableDiffusion/comments/1rg7cpj/how_to_make_multiple_character_on_same_image_but/
  - https://www.reddit.com/r/StableDiffusion/comments/1io5yxx
  - https://www.reddit.com/r/StableDiffusion/comments/1sla0rq/struggling_to_make_more_than_2_characters/
- Class: `COMMUNITY / MULTI_SOURCE_PRACTICE`
- Scope: character mixing, regional/inpaint escalation, 2→3+ subject stress.
- Limitation: heterogeneous checkpoints/workflows.

**S-COMM-059 — Masked OpenPose + LoRA + img2img multi-character workflow**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1irsq4o
- Class: `COMMUNITY / ASSISTED_WORKFLOW`
- Scope: per-character masks and prompts with pose + LoRA + img2img.
- Value: concrete divide-and-conquer assisted pipeline.

**S-COMM-060 — Illustrious adult-VN consistency discussion**
- URL: https://www.reddit.com/r/comfyui/comments/1v62676/illustrious_keeping_characters_consistent_for/
- Class: `COMMUNITY / FAILURE_DIAGNOSIS`
- Scope: pose consistency vs identity/style consistency.
- Value: geometry and identity fidelity are independent control axes.

**S-COMM-061 — NoobAI adult community review with source conflicts**
- URL: https://lewdly.ai/blog/noobai-xl-checkpoint-review-anime-nsfw
- Class: `COMMUNITY / SECONDARY_REVIEW`
- Scope: EPS/V-Pred, multi-subject, anatomy, settings.
- Value: large private-use experience and group-scene stress signal.
- Limitation: V-Pred configuration conflicts with current exact author guidance; exact recipe/percentages are not project authority.

---

## 2026-10-02 character / style reproduction sources

**S-RESEARCH-015 — B-LoRA style/content separation**
- URL: https://arxiv.org/abs/2403.14572
- Class: `RESEARCH`
- Scope: SDXL style/content disentanglement using selective LoRA blocks.
- Value: adaptation location affects style isolation and overfitting.
- Limitation: SDXL block prescription must not be copied directly to Anima.

**S-RESEARCH-016 — Mix-of-Show**
- URL: https://arxiv.org/abs/2305.18292
- Class: `RESEARCH`
- Scope: multi-concept LoRA fusion / identity conflict / regional sampling.
- Value: subject/style and multi-concept composition is a distinct fusion problem.

**S-RESEARCH-017 — Dynamic subject/style LoRA fusion**
- URL: https://arxiv.org/abs/2602.15539
- Class: `RESEARCH`
- Scope: training-free dynamic fusion of subject and style LoRAs.
- Value: static adapter weighting can be insufficient.

**S-RESEARCH-018 — AnimeAdapter**
- URL: https://arxiv.org/abs/2605.20237
- Class: `RESEARCH`
- Scope: zero-shot anime character appearance conditioning with pose-aware disentanglement.
- Value: non-LoRA character-reproduction baseline.

**S-OFFICIAL-ANIMA-LORA-001 — Anima finetuning guidance**
- URL: https://huggingface.co/circlestone-labs/Anima
- Class: `AUTHOR_GUIDE`
- Scope: Base-only training recommendation, frozen LLM adapter, low LR, rank-32 starting point.
- Value: exact family training baseline.

**S-COMM-062 — Anima LoRA native-style suppression**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/60
- Class: `COMMUNITY / FAILURE_CLUSTER`
- Scope: LoRA suppressing native artist/style-tag behavior.
- Limitation: mechanism not fully resolved.

**S-COMM-063 — Anima current LoRA prompt-response degradation**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/240
- Class: `COMMUNITY / CURRENT_FAILURE_REPORT`
- Scope: reduced tag-driven editability after training.
- Limitation: no controlled trainer matrix.

**S-COMM-064 — Anima character/style layer-ablation study**
- URL: https://note.com/studiomasakaki/n/nf39775327336
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: Self-Attention / Cross-Attention / MLP training ablation.
- Value: training-set reconstruction hides generalization differences.

**S-COMM-065 — Anima style-LoRA captioning discussion**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1wq972q/training_a_style_lora_for_anima_a_few_tagging/
- Class: `COMMUNITY / CURRENT_DISCUSSION`
- Scope: style captioning, false tags, content leakage.
- Limitation: conflicting practitioner preferences on dropout/tag density.

**S-COMM-066 — Anima style-LoRA weight sweep**
- URL: https://note.com/stray_dog0012/n/n6ebc324c1211
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: same-seed 0.4–1.2 adapter strength.
- Value: style fidelity vs composition lock/spillover.

**S-COMM-067 — Anima style-LoRA timestep experiment**
- URL: https://note.com/kuon_noise/n/n82be977f167d
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: style-specific timestep/noise distribution.
- Value: character and style recipes may differ.

**S-OFFICIAL-LORA-001 — sd-scripts LoRA rank/alpha documentation**
- URLs:
  - https://github.com/kohya-ss/sd-scripts/blob/main/docs/train_network.md
  - https://github.com/kohya-ss/sd-scripts/blob/main/docs/train_network_README-ja.md
- Class: `OFFICIAL_RUNTIME`
- Scope: rank/dim, alpha, dropout, Conv LoRA, DyLoRA.
- Value: rank is capacity and must be interpreted with alpha/task.

**S-RESEARCH-019 — DreamBench++**
- URL: https://arxiv.org/abs/2406.16855
- Class: `RESEARCH`
- Scope: human-aligned personalized image evaluation.
- Value: multimodal-model scoring aligned against human judgement.

**S-RESEARCH-020 — CSD style descriptors**
- URL: https://arxiv.org/abs/2404.01292
- Class: `RESEARCH`
- Scope: dedicated style similarity representation.
- Limitation: public repo currently warns of a model-weight/reported-number discrepancy.

**S-RESEARCH-021 — DiffSim**
- URL: https://arxiv.org/abs/2412.14580
- Class: `RESEARCH`
- Scope: diffusion-feature visual/style/instance similarity.
- Value: highlights limitations of CLIP/DINO for fine appearance.

**S-RESEARCH-022 — StyleID**
- URL: https://arxiv.org/abs/2604.21689
- Class: `RESEARCH`
- Scope: stylization-agnostic human-aligned identity evaluation.
- Value: photo-face identity encoders can be brittle under stylization.

**S-TOOL-011 — CCIP**
- URL: https://huggingface.co/deepghs/ccip
- Class: `TOOL_MODEL`
- Scope: anime character visual identity similarity for single-character images.
- Value: domain-specific automated character identity signal.

**S-RESEARCH-023 — IP-Adapter**
- URL: https://github.com/tencent-ailab/IP-Adapter
- Class: `RESEARCH_TOOL`
- Scope: tuning-free image-prompt conditioning.
- Value: reference-conditioning baseline against trained character LoRA.

**S-RESEARCH-024 — InstantStyle / InstantStyle-Plus**
- URLs:
  - https://arxiv.org/abs/2404.02733
  - https://arxiv.org/abs/2407.00788
  - https://github.com/instantX-research/InstantStyle
- Class: `RESEARCH`
- Scope: content/style disentanglement in reference-guided stylization.
- Value: style fidelity must be balanced with semantic/spatial preservation.

**S-COMM-068 — Anima current character-LoRA hyperparameter discussion**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1wpjl3p/advice_on_anima_character_lora_training_parameters/
- Class: `COMMUNITY / CURRENT_TRAINING_FAILURE`
- Scope: facial-detail drift under rank32/alpha16/LR setup.
- Limitation: no controlled sweep; numeric advice is not authoritative.

**S-OFFICIAL-ANIMA-CAPTION-001 — Anima multi-caption training variants**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/9
- Class: `AUTHOR_STATEMENT`
- Scope: full tags, dropout, mixed tag/NL, short/long caption variants.
- Value: disproves the idea that one single caption surface is required for Anima LoRA alignment.

**S-TOOL-012 — waifuc character dataset pipeline**
- URL: https://github.com/deepghs/waifuc
- Class: `OFFICIAL_TOOL`
- Scope: anime image collection, dedupe, person split, CCIP filtering, tagging.
- Value: auditable end-to-end anime character dataset curation.

**S-COMM-069 — full-body framing retraining case**
- URL: https://note.com/imbolc_02/n/na8d6a1213783
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: adding full-body data/margins to correct full-body generation.
- Limitation: one training setup.

**S-COMM-070 — 36-image structured Anima character dataset**
- URL: https://note.com/seal309midorin/n/nab2b785e4d13
- Class: `PRACTICAL / COMMUNITY`
- Scope: front/profile/back/face/full-body structured source set.
- Value: concrete dataset-coverage example.

**S-COMM-071 — character-dataset coverage discussion**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1q4h3mp/character_lora_training_dataset_howto/
- Class: `COMMUNITY / DATASET_PRACTICE`
- Scope: face/medium/full-body variation, outfits, lighting/background variation.
- Limitation: anecdotal advice, no controlled result.

**S-COMM-072 — Anima 46-image coverage counterexample**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/119
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: multi-angle dataset with poor non-frontal generalization.
- Value: nominal coverage does not guarantee learned editability.

**S-TOOL-013 — Anima Style Explorer**
- URLs:
  - https://github.com/ThetaCursed/Anima-Style-Explorer
  - https://huggingface.co/circlestone-labs/Anima/discussions/227
- Class: `COMMUNITY_TOOL`
- Scope: 40k+ standardized visual artist/style previews.
- Value: native-style discovery and benchmark design.
- Limitation: preview/work-count/uniqueness metadata is not exact model-authority evidence.

**S-TOOL-014 — Illustrious / NoobAI Style Explorer**
- URLs:
  - https://github.com/ThetaCursed/Illustrious-NoobAI-Style-Explorer
  - https://github.com/Faildes/Illustrious-NoobAI-Style-Explorer-plus
- Class: `COMMUNITY_TOOL`
- Scope: visual Danbooru artist-style browsing for Illustrious/NoobAI.
- Value: native style discovery.
- Limitation: claims of universal compatibility require exact-checkpoint verification.

**S-COMM-073 — Anima artist-context sensitivity experiment**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/112
- Class: `COMMUNITY / TECHNICAL_EXPERIMENT`
- Scope: prompt position/context/multiple artists and artist representation stability.
- Value: evidence that native artist response is context-sensitive.
- Limitation: proposed internal mechanism is not author-confirmed.

**S-COMM-074 — Anima raw-style benchmark methodology**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/49
- Class: `COMMUNITY_TOOL_METHODOLOGY`
- Scope: standardized character benchmark with quality tags removed.
- Value: isolates raw artist influence.

**S-COMM-075 — Anima default-outfit prompting request**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/206
- Class: `COMMUNITY / CURRENT_FEEDBACK`
- Scope: character identity vs official/default outfit recall.
- Value: motivates separate identity/outfit evaluation.
- Limitation: user feedback, not controlled benchmark.

**S-COMM-076 — Character LoRA clothing captioning discussion**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1gkqi9f
- Class: `COMMUNITY / TRAINING_PRACTICE`
- Scope: caption mutable clothing vs absorb default clothing into trigger.
- Limitation: heuristic, architecture-dependent.

**S-COMM-077 — Multi-outfit trigger-token discussion**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1vgrr7b
- Class: `COMMUNITY / CURRENT_TRAINING_PRACTICE`
- Scope: one character LoRA with outfit-specific triggers.
- Limitation: numeric image/balance advice is unverified.

**S-COMM-078 — Character + clothing LoRA interference**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1qkrofm/train_clothes_and_cosplay_outfit_loras/
- Class: `COMMUNITY / WORKFLOW_DISCUSSION`
- Scope: separate clothes LoRA vs prompting/reference edit vs multi-concept LoRA.
- Value: separate outfit adapters can affect identity.

**S-COMM-079 — Anima custom-character prompt drift**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1v7h6b2/anima_struggling_to_maintain_consistency_with/
- Class: `COMMUNITY / CURRENT_FAILURE_REPORT`
- Scope: prompt-only custom character hairstyle/face consistency.
- Value: current workflow signal for when LoRA becomes useful.
- Limitation: one user/merge workflow.

**S-COMM-080 — Anima viewpoint-generalization failure**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/119
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: 46-image multi-angle character dataset with poor non-frontal identity retention.
- Value: nominal viewpoint coverage does not guarantee pose-invariant identity.

**S-COMM-081 — Illustrious character plus source-style entanglement**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1rsqv6y/lora_training_illustrious/
- Class: `COMMUNITY / TRAINING_PRACTICE`
- Scope: character and source style captured together.
- Limitation: practitioner observation, no controlled ablation.

**S-COMM-082 — Illustrious curated-dataset face/style drift**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1r318hl/helpquestion_sdxl_lora_training_on_illustriousxl/
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: 25-image curated character dataset with remaining face/style drift.
- Value: curation/caption pruning alone is not sufficient.

**S-COMM-083 — NoobAI V-Pred style-LoRA global tint**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1vbsj8k/what_am_i_doing_wrong_in_my_lora_training/
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: 21-image style LoRA with unwanted brown tint.
- Value: palette/context leakage failure example.

**S-COMM-084 — Anima vs Illustrious source-style capture**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1tdobjq/anima_loras_cant_learn_the_characters_style_no/
- Class: `COMMUNITY / CROSS_MODEL_REPORT`
- Scope: same/source-similar data, identity/outfit vs style capture.
- Limitation: training recipe not a formal controlled benchmark.

---

## 2026-10-02 character/style evaluation + adapter sources

**S-EVAL-CHAR-001 — CCIP anime character similarity**
- URL: https://huggingface.co/deepghs/ccip
- Class: `OFFICIAL_MODEL`
- Scope: anime character identity similarity.
- Limitation: base model card targets single-character images.

**S-EVAL-STYLE-001 — Contrastive Style Descriptors**
- URL: https://arxiv.org/abs/2404.01292
- Class: `RESEARCH`
- Scope: artistic style descriptors and style similarity.
- Value: style-specific metric and OOD style-generalization analysis.

**S-EVAL-VISUAL-001 — DiffSim**
- URL: https://arxiv.org/abs/2412.14580
- Class: `RESEARCH`
- Scope: diffusion-feature instance/style similarity.
- Value: complementary instance and style evaluation.

**S-RESEARCH-019 — LyCORIS evaluation paper**
- URL: https://arxiv.org/abs/2309.14859
- Class: `RESEARCH / ICLR-2024`
- Scope: LoRA/LoHa/LoKr/native fine-tuning and systematic T2I customization evaluation.
- Value: fidelity, controllability, diversity, base-preservation and quality framework; dim/alpha/factor interactions.

**S-TOOL-011 — LyCORIS current repository**
- URL: https://github.com/KohakuBlueleaf/LyCORIS
- Class: `OFFICIAL_RUNTIME`
- Scope: current adapter algorithms and implementation freshness.
- Freshness: 4.0.0 changelog dated 2026-09-01.

**S-RESEARCH-020 — DoRA**
- URL: https://arxiv.org/abs/2402.09353
- Class: `RESEARCH`
- Scope: magnitude/direction weight-decomposed low-rank adaptation.
- Limitation: not direct proof of superiority for anime diffusion customization.

**S-RESEARCH-021 — DisenBooth**
- URL: https://arxiv.org/abs/2305.03374
- Class: `RESEARCH`
- Scope: identity vs identity-irrelevant context disentanglement in subject-driven T2I.
- Value: theoretical backing for background/pose/style entanglement diagnosis.

**S-RESEARCH-022 — Infusion**
- URL: https://arxiv.org/abs/2404.14007
- Class: `RESEARCH`
- Scope: concept-agnostic and concept-specific overfitting.
- Value: separates base-model damage from target-concept modality collapse.

**S-RESEARCH-023 — Custom Diffusion**
- URL: https://arxiv.org/abs/2212.04488
- Class: `RESEARCH`
- Scope: efficient single/multi-concept customization and model combination.
- Value: multi-concept customization baseline.

**S-RESEARCH-024 — Break-A-Scene**
- URL: https://arxiv.org/abs/2305.16311
- Class: `RESEARCH`
- Scope: concept masks, cross-attention separation, union sampling.
- Value: anti-entanglement strategy for multi-concept source images.

**S-RESEARCH-025 — IP-Adapter**
- URL: https://arxiv.org/abs/2308.06721
- Class: `RESEARCH`
- Scope: tuning-free image-prompt adapter with decoupled cross-attention.
- Value: reference-conditioning baseline against trained LoRAs.

**S-RESEARCH-026 — InstantStyle**
- URL: https://arxiv.org/abs/2404.02733
- Class: `RESEARCH`
- Scope: tuning-free reference-style conditioning with content/style decoupling.
- Value: style leakage/content-preservation baseline.

**S-RESEARCH-027 — StyleAligned**
- URL: https://arxiv.org/abs/2312.02133
- Class: `RESEARCH`
- Scope: tuning-free shared-attention style consistency across image sets.
- Value: sequence-level style consistency baseline.

**S-RESEARCH-028 — StoryDiffusion**
- URL: https://arxiv.org/abs/2405.01434
- Class: `RESEARCH`
- Scope: subject/detail consistency across long image/video sequences.
- Value: cross-image character-consistency baseline.

---

## 2026-10-02 practical creation workflow sources

**S-PRACTICAL-001 — Anima production baseline**
- URL: https://huggingface.co/circlestone-labs/Anima
- Class: `AUTHOR_GUIDE`
- Scope: Base/Aesthetic/Turbo generation settings, samplers, prompt format and fast iteration.
- Value: exact family baseline for exploration vs final-profile validation.

**S-PRACTICAL-002 — NoobAI XL 1.1 EPS baseline**
- URL: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Class: `AUTHOR_GUIDE`
- Scope: CFG/steps/sampler/resolution/caption order.

**S-PRACTICAL-003 — WAI v17 generation + Hires baseline**
- URL: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- Class: `AUTHOR_GUIDE`
- Scope: Forge Neo baseline and author Hires example.
- Limitation: Hires recipe is model-specific.

**S-COMM-068 — Anima fixed-seed 0/1/3 LoRA stack**
- URL: https://note.com/fresh_macaw9581/n/n7a3a7f6ed1e7
- Class: `CONTROLLED_PRACTICAL / COMMUNITY`
- Scope: incremental adapter stacking.
- Value: additional LoRAs can improve detail while adding unwanted content/control loss.

**S-COMM-069 — Anima three-character LoRA production report**
- URL: https://note.com/moribro/n/na743c1e66884
- Class: `PRACTICAL / COMMUNITY`
- Scope: character-LoRA training captions and modular style/character/scene generation.
- Value: failure-driven production workflow.
- Limitation: exact dim/LR/weight recommendations are one project recipe.

**S-COMM-070 — Anima edit/inpaint workflow**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1totumo/anima_can_edit_images_and_this_is_possible_in_two/
- Class: `COMMUNITY / ASSISTED_WORKFLOW`
- Scope: reference-latent/edit-LoRA vs masked/control editing.

**S-COMM-071 — Anima reference-canvas edit workflow**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1v729sl/remake_you_character_in_the_new_style_anima/
- Class: `COMMUNITY / ASSISTED_WORKFLOW`
- Scope: masked reference-guided regeneration/pose expansion.

**S-TOOL-012 — Regional Prompter current Anima support**
- URL: https://github.com/hako-mikan/sd-webui-regional-prompter/blob/main/README.md
- Class: `OFFICIAL_RUNTIME`
- Scope: Forge Neo Anima Latent/Attention regional prompting.
- Boundary: Region LoRA unsupported for Anima.

**S-TOOL-013 — Forge Couple**
- URL: https://github.com/Haoming02/sd-forge-couple/blob/main/README.md
- Class: `OFFICIAL_RUNTIME`
- Scope: region-targeted conditioning in Forge/Forge Neo including Anima.
- Value: total-subject-count and checkpoint-composition-understanding guidance.

**S-TOOL-014 — ComfyUI preprocessors**
- URL: https://blog.comfy.org/p/preprocessor-and-frame-interpolation
- Class: `OFFICIAL_RUNTIME`
- Scope: pose/depth/lineart/normals preprocessing.
- Value: preprocessor output as a separate debug artifact.

**S-TOOL-015 — ComfyUI upscaling handbook**
- URL: https://blog.comfy.org/p/upscaling-in-comfyui
- Class: `OFFICIAL_RUNTIME`
- Scope: modern pixel/generative/upscale workflow selection.
- Value: symptom/use-case based finishing selection.

**S-TOOL-016 — ComfyUI img2img denoise semantics**
- URL: https://docs.comfy.org/tutorials/api-nodes/stability-ai/stable-image-ultra
- Class: `OFFICIAL_RUNTIME`
- Scope: image-to-image preservation versus reinterpretation.
- Value: denoise as a workflow-intent axis rather than a fixed magic value.

**S-PRACTICAL-004 — Anima official model comparison workflow**
- URL: https://huggingface.co/circlestone-labs/Anima
- Class: `AUTHOR_GUIDE`
- Scope: multi-model × multi-seed comparison grid.
- Value: matrix comparison instead of cherry-picked pairs.

**S-PRACTICAL-005 — Anima sampler behavior descriptions**
- URL: https://huggingface.co/circlestone-labs/Anima
- Class: `AUTHOR_GUIDE`
- Scope: er_sde / Euler a / dpmpp_2m_sde_gpu / Euler rendering characteristics.

**S-PRACTICAL-006 — NoobAI EPS resolution grid**
- URL: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Class: `AUTHOR_GUIDE`
- Scope: near-1MP portrait/square/landscape resolution set.

**S-PRACTICAL-004 — ComfyUI upscaling handbook**
- URL: https://blog.comfy.org/p/upscaling-in-comfyui
- Class: `OFFICIAL_RUNTIME_GUIDE`
- Scope: upscale vs enhancement, conservative vs creative processing, production pipeline.
- Value: style-preservation and artifact-repair routing.

**S-TOOL-012 — Forge Hires UI implementation**
- URL: https://github.com/lllyasviel/stable-diffusion-webui-forge/blob/main/modules/ui.py
- Class: `OFFICIAL_RUNTIME`
- Scope: Hires checkpoint/VAE/TE/sampler/scheduler/prompt/negative/CFG options.
- Value: proves Hires is a configurable second generation pass.

**S-COMM-072 — Anima second-pass sampler observation**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1tmrh0l/the_not_so_anime_anima/
- Class: `COMMUNITY / PRACTICAL`
- Scope: sampler difference between raw generation and img2img/upscale.

**S-COMM-073 — Anima Forge Neo Hires discussion**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1t87xbc/anima_settings_in_forge_neo/
- Class: `COMMUNITY / FAILURE_DISCUSSION`
- Scope: Hires instability and low-denoise img2img alternatives.

**S-COMM-074 — Anima 2026-09 upscale discussion**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1wqb41q/anima_upscaling/
- Class: `COMMUNITY / CURRENT_PRACTICE`
- Scope: SeedVR/pixel/tiled/Forge Neo upscale ecosystem.

**S-COMM-075 — Anima detailer instability report**
- URL: https://www.reddit.com/r/StableDiffusion/comments/1tj1fw2/detailing_in_anima_is_really_confusing_any_guides/
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: local crop size and sampler/scheduler sensitivity.

**S-PRACTICAL-005 — Anima sampler/weight guide**
- URL: https://huggingface.co/circlestone-labs/Anima
- Class: `AUTHOR_GUIDE`
- Scope: sampler rendering tendencies, weight behavior, quality/prompt profile differences.

**S-PRACTICAL-006 — WAI v17 prompt-length warning**
- URL: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- Class: `AUTHOR_GUIDE`
- Scope: compact quality/Negative guidance plus recommended generation settings.
- Value: explicit warning against overloading quality/aesthetic/Negative terms.

**S-PRACTICAL-007 — NoobAI EPS tested resolution family**
- URL: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Class: `AUTHOR_GUIDE`
- Scope: ~1MP aspect-ratio options and baseline settings.

---

## 2026-10-02 adult practical learning sources

**S-ADULT-LEARN-001 — Anima relation-focused adult caption workflow**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/141
- Class: `COMMUNITY / PRACTICAL`
- Scope: VLM/LLM structure-only captioning for adult relation-heavy scenes.
- Value: stable subject IDs and isolation of relation/camera/contact from character/style/background.
- Limitation: user's exact explicit system prompt is not retained as project authority.

**S-ADULT-LEARN-002 — Regional LoRA conditioning workflow**
- URL: https://www.reddit.com/r/comfyui/comments/1dpwju8/
- Class: `COMMUNITY / ASSISTED_WORKFLOW`
- Scope: spatially restricting character LoRA influence to reduce cross-subject bleed.

**S-ADULT-LEARN-003 — Multi-character regional workflow experiment**
- URL: https://www.reddit.com/r/comfyui/comments/1arhe7s
- Class: `COMMUNITY / PRACTICAL`
- Scope: pose-first, inpaint, regional masks, multi-LoRA, Hires.
- Value: divide geometry and identity during construction.

**S-ADULT-LEARN-004 — Interaction-heavy multi-character difficulty**
- URL: https://www.reddit.com/r/comfyui/comments/1dzh275
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: interacting multiple LoRA characters, pose/merge/hand failures.
- Value: recurring beginner failure pattern.

**S-LEARN-001 — ComfyUI parameter-grid practice**
- URLs:
  - https://www.reddit.com/r/StableDiffusion/comments/1dhdyt7
  - https://www.reddit.com/r/StableDiffusion/comments/1e9eqj6
- Class: `COMMUNITY / PRACTICAL_METHOD`
- Scope: XY/grid comparison under fixed surrounding settings.
- Value: visual response-curve learning.

**S-ADULT-LEARN-005 — Anima LoRA training-caption discussions**
- URLs:
  - https://huggingface.co/circlestone-labs/Anima/discussions/105
  - https://huggingface.co/circlestone-labs/Anima/discussions/205
- Class: `COMMUNITY / TRAINING_PRACTICE`
- Scope: tags, NL, mixed captions, tag dropout, official-style ordering.

**S-ADULT-LEARN-006 — Anima multi-character LoRA training practice**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/202
- Class: `COMMUNITY / TRAINING_PRACTICE`
- Scope: solo/joint subsets, coexistence examples, interaction images, balancing.

**S-TOOL-013 — Regional Prompter current Anima support**
- URL: https://github.com/hako-mikan/sd-webui-regional-prompter
- Class: `OFFICIAL_RUNTIME`
- Freshness: 2026-09-04 update.
- Scope: Forge Neo Anima Latent/Attention regional conditioning.
- Critical limitation: Region LoRA is not supported for Anima.

**S-TOOL-014 — ComfyUI Anima Regional Conditioning**
- URL: https://github.com/Sen-sou/Comfyui-Anima-Regional-Conditioning
- Class: `OFFICIAL_RUNTIME / EXPERIMENTAL`
- Scope: masked cross/self-attention routing for Anima.
- Value: region strength/schedule/base-ratio mechanics and documented coherence tradeoffs.

**S-COMM-076 — Anima directional-prompt ambiguity**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/99
- Class: `COMMUNITY / FAILURE_REPORT`
- Scope: left/right frame-vs-subject ambiguity and hand-direction instability.
- Value: directional language is not a reliable ownership guarantee.

**S-EVID-001 — ComfyUI SaveImage metadata**
- URLs:
  - https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_api/latest/_ui.py
  - https://github.com/comfyanonymous/ComfyUI_examples
- Class: `OFFICIAL_RUNTIME`
- Scope: prompt/workflow metadata embedded in saved PNG files.
- Value: reproducible experiment artifact and workflow recovery.

**S-TOOL-015 — ComfyUI Prompt Control**
- URL: https://github.com/asagi4/comfyui-prompt-control
- Class: `OFFICIAL_RUNTIME`
- Scope: prompt/LoRA scheduling, regional conditioning, advanced text encoding.
- Value: explicit timestep-dependent conditioning experiments.

**S-COMM-077 — Anima staged-quality conditioning example**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/146
- Class: `COMMUNITY / PRACTICAL`
- Scope: early structural conditioning with later quality-modifier injection.
- Limitation: asset-specific setup; exact switch fraction is not universal.

**S-LEARN-002 — Anima intermediate-checkpoint visual validation**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/157
- Class: `COMMUNITY / TECHNICAL_EXPERIMENT`
- Scope: distillation LoRA with stable loss but poor visual quality.
- Value: numerical convergence is insufficient; intermediate image tests matter.

**S-COMM-078 — Anima training-duration discussion**
- URLs:
  - https://huggingface.co/circlestone-labs/Anima/discussions/106
  - https://huggingface.co/circlestone-labs/Anima/discussions/129
- Class: `COMMUNITY / TRAINING_PRACTICE`
- Scope: widely varying style/character steps/epochs.
- Value: rejects universal absolute-step recipes.

**S-COMM-079 — Anima training determinism discussion**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/144
- Class: `COMMUNITY / REPRODUCIBILITY`
- Scope: nominally same training seed/config can differ without deterministic backend controls.
- Value: repeat-run caution and full training-identity logging.

**S-TOOL-016 — ComfyUI native advanced hooks**
- URL: https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_hooks.py
- Class: `OFFICIAL_RUNTIME / EXPERIMENTAL`
- Scope: Create Hook LoRA, mask-bound conditioning, timestep ranges and hook keyframe scheduling.
- Value: native primitives for spatial/time adapter-conditioning experiments.
- Limitation: exact Anima behavior requires local validation.

**S-COMM-080 — 2026-09-28 Anima/Illustrious multi-character thread**
- URL: https://www.reddit.com/r/comfyui/comments/1ws23ur/multiple_characters_in_one_single_generated_image/
- Class: `COMMUNITY / CURRENT_PRACTICE`
- Scope: attribute swapping in Anima/Illustrious; regional prompting and LoRA-hook localization discussion.
- Value: very recent practical confirmation of native-character vs LoRA-character distinction.

**S-TOOL-017 — ComfyUI-Impact-Pack RegionalSampler**
- URL: https://github.com/ltdrdata/ComfyUI-Impact-Pack
- Class: `OFFICIAL_RUNTIME`
- Scope: latent-level per-region sampling, masks, overlap_factor, restore_latent.
- Value: tool authority for RegionalSampler mechanics.

**S-COMM-081 — Anima crossover RegionalSampler guide**
- URL: https://huggingface.co/datasets/rouge-kasshoku/anima-crossover-couples-regional-sampler-guide
- Class: `COMMUNITY / DETAILED_PRACTICAL_GUIDE`
- Scope: native proxy references, RegionalSampler, LoRA isolation, masks and two-pass metadata synchronization.
- Value: months-of-testing practical workflow with strong mechanistic reasoning.
- Limitation: numeric parameter values are author-specific recipes.

**S-COMM-082 — Anima 3D-source character LoRA troubleshooting**
- URL: https://huggingface.co/circlestone-labs/Anima/discussions/187
- Class: `COMMUNITY / TRAINING_DIAGNOSIS`
- Scope: source-style entanglement, layer exclusions, explicit nuisance tags, dataset domain conversion.
- Value: strong example that dataset correction can matter more than parameter tuning.

