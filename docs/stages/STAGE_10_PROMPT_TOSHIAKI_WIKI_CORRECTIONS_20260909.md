# Stage10 PROMPT Toshiaki diffusion Wiki corrections / holds

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: correction ledger. **Not production specification.**

## Purpose

としあきdiffusion Wikiは有用だが、official/author evidenceと衝突するclaimをそのままPrompt knowledgeへ取り込まないため、具体的な訂正・HOLDを保存する。

---

## C1 — Anima count tags

Wiki-side claim candidate:
- count表現は `1 boy`, `2 girls` のようにnumeralとnounをspaceで分ける方がよく、`1boy/2girls`を悪い例として扱う説明。

Higher-ranked evidence:
- Anima official tag order: `[quality/meta/year/safety] [1girl/1boy/1other etc] [character] ...`
- official full tag example explicitly contains `1girl`。

Verdict:
- `CONTRADICTED_BY_OFFICIAL / MODE_CONFUSION`
- Danbooru-style tag modeでは `1girl/1boy` を正当な公式surfaceとして扱う。
- natural-language sentence内の `one girl/two girls` とtag modeを混同しない。
- `1 girl`をAnima global defaultにしない。

Stage10 need:
- none for basic validity; official grammar takes priority.
- if spaced count has measurable derivative-specific benefit, test separately as optimization question.

---

## C2 — Anima Qwen “1k token limit” explanation

Wiki-side claim candidate:
- Qwen 0.6B text encoderに約1k token limitがあるため、natural-language Promptを~300 words以下にするという説明。

Higher-ranked evidence:
- Qwen3 encoder architecture/config is not intrinsically fixed to a 1k maximum-position limit.
- Anima tooling/training/inference can impose separate sequence lengths/padding behavior; these are implementation/configuration issues, not proof of a Qwen3-0.6B architectural 1k ceiling.

Verdict:
- `RATIONALE_INCORRECT`
- 「無意味に長いPromptを避ける」はpractical candidateとして残せる。
- 「Qwenが1kまでだから」「300 wordsが上限」という固定production ruleは採用しない。

Stage10 need:
- prompt density test: short → sufficient → long/overloaded.
- compare semantic retention and binding rather than token-count folklore.

---

## C3 — Illustrious generic long Negative vs WAI v17

Wiki-side generic practice:
- Illustrious系でquality/negative templateを一定量維持する運用・削らない助言。

Higher-ranked evidence:
- WAI Illustrious SDXL v17 author mirror explicitly warns not to add too many quality/aesthetic tags or overly long negative prompts because they can reduce image quality and make it blurrier.

Verdict:
- `CONTRADICTED_FOR_WAI_V17`
- Base/early Illustrious community ruleをWAI v17へ継承しない。
- WAI v17 default candidateはauthor minimal set側を優先。

Stage10 need:
- WAI v17 minimum negative vs expanded negative A/B.
- evaluate both target fidelity and final image quality.

---

## C4 — BREAK on Anima

Wiki-side observation:
- A1111/Forge系`BREAK`をAnimaで使うと期待どおりにconditioning分割されない、またはunexpected behaviorになる可能性への注意。

Higher-ranked evidence:
- `BREAK` is historically a WebUI/parser feature rather than a learned Anima caption rule.
- Forge Neo has different architecture paths and extensions.

Verdict:
- `ENV_SPECIFIC_HOLD`
- “AnimaはBREAK禁止”をuniversal model factにしない。
- parser/version/environmentを含めて検証する。

Stage10 need:
- only if BREAK remains operationally relevant after current block/region tooling selection.

---

## C5 — Underscore vs spaces

Wiki-side claim:
- Danbooru web tag uses underscores; AI Prompt usually spaces.

Evidence:
- broadly consistent with booru-style model guidance including Anima’s space-based tags.

Verdict:
- `COMMUNITY_VALIDATED`
- Important architectural correction to old “canonical string must be emitted literally” assumptions.

Caution:
- canonical identity remains underscore form where canonical says so.
- rendered surface is family/parser-specific.

---

## C6 — “Danbooru tag exists = usable Prompt”

Wiki itself often warns that low-exposure/recent tags may not be learned well.

Verdict:
- `ADOPT_CANDIDATE PRINCIPLE`
- tag ontology validity and model realization are separate.
- This supports Stage10 model-trigger validation and evaluator REVIEW fallback.

---

## C7 — Related tags as reinforcement

Wiki community practice:
- weak concepts/characters can sometimes be helped by related tags.

Verdict:
- `COMMUNITY_CANDIDATE`
- Meaning relation alone is insufficient to authorize automatic support insertion.
- Requires actual generation benefit and side-effect audit.

---

## C8 — Generic quality/negative inheritance

Wiki contains guidance from multiple generations: NAI, SD1.5, SDXL, Illustrious, Anima.

Verdict:
- `DO_NOT_PROMOTE_GLOBAL`
- quality/meta/negative profiles must be model-family + version scoped.

Examples:
- WAI v17: lean creator set candidate.
- Anima Base/Aesthetic/Turbo: separate profiles.
- Illustrious v0.1 advice: historical/version-scoped.

---

## C9 — Prompt weighting

Wiki provides common A1111 weighting syntax and many community weighting recipes.

Verdict:
- syntax: `UI_PARSER_SCOPED / VALIDATED`
- exact weight values: `COMMUNITY_CANDIDATE / MODEL_SPECIFIC`
- never convert a successful `(tag:1.x)` anecdote into global default.

---

## C10 — Tagger ranking

Wiki gives dated preferences among WD taggers.

Verdict:
- `DATED_RANKING`
- tool orientation useful, current project evaluator allocation must use current version-pinned capability evidence.
- no tagger is semantic ground truth for rare/composite/relation Special.

---

## C11 — “万能便利呪文” / old long prompt templates

Age:
- early NAI/SD era.

Verdict:
- `HISTORICAL_ONLY`
- useful as history of community practice, not modern product default.

---

## C12 — Natural-language relation support on Anima

Wiki practical advice:
- explicit role/relation/appearance descriptions often preferred over ambiguous pronouns or tag-position tricks for complex multi-character prompts.

Official alignment:
- Anima official says appearance description is especially important for multiple characters and supports mixing tags + NL.

Verdict:
- `COMMUNITY_CANDIDATE_WITH_OFFICIAL_DIRECTIONAL_SUPPORT`
- Stage10 should test:
  - tag-only
  - tag + one relation sentence
  - tag + relation + minimal appearance anchors

Do not conclude:
- natural language always wins
- more sentences always improve binding

---

## Summary correction policy

When Wiki and official disagree:
1. preserve Wiki observation as community evidence if it may describe a specific workflow;
2. do not silently delete it;
3. label conflict;
4. use official as semantic/authoritative baseline;
5. only re-promote the community exception if a version-pinned controlled test reproduces it.
