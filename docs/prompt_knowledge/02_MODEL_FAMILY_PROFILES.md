# 02 Model family profiles

Owner: PROMPT / Issue #5
Status: family-scoped knowledge summary. Not production specification.

Current claim authority: `CLAIM_REGISTRY.md`
Label schema: `00_KNOWLEDGE_GOVERNANCE.md`

## 絶対原則

WAI Illustrious v17 / Illustrious XL / NoobAI XL 1.1 / Anima を一つのPrompt grammarへ統合しない。

共通化禁止項目:
- caption / block order
- natural-language reliance
- count syntax
- quality/meta
- Negative
- weighting
- safety/rating tags
- canonical vs model-trigger surface

作者/公式情報はbaselineとして最優先だが、hard-targetで最適という最終証明ではない。Stage10の実画像で確認する。

---

## WAI Illustrious v17

SOURCE_CLASS: `AUTHOR_GUIDE`
Official/author claims: `ACCEPTED`
Current project optimization profile: `CANDIDATE`
Profile: `WAI17_LOCAL_FIRST_20260909`
Claim group: `K-WAI-*`

作者側で保持:
- recommended software: Forge Neo
- Steps 15–30
- CFG 5–7
- Euler a
- VAE integrated
- original size >1024x1024推奨
- sample 1024x1344
- Hires example: 1.5 / hires steps 20 / denoise 0.35–0.5
- quality例: masterpiece / best quality / amazing quality
- Negative例: bad quality / worst quality / worst detail / sketch / censor
- quality/aesthetic過積載を警告
- overly long Negativeでquality低下/blurの可能性を警告
- trigger wordなし

PROMPT候補 `K-WAI-005`:
`subject/count -> Special/ACT -> SITE/OBJECT/relation -> needed pose/geometry -> needed visibility -> minimum finish`

初手:
- tag-first
- quality/Negativeは短く
- supportを一個ずつ足す
- Hiresは意味成立確認後の別pass

主な疑い:
- `WAI_Q_OVERLOAD`
- `WAI_NEG_OVERLOAD`
- `WAI_SUPPORT_COLLISION`
- `WAI_HIRES_MASKING`

重要:
- author guidance itself = `ACCEPTED`
- `LEAN_TAG_FIRST`がhard-target最適 = `CANDIDATE / STAGE10_REQUIRED`
- Steps25/CFG6等のproject baseline = `CANDIDATE / STAGE10_REQUIRED`

詳細: `10_WAI17_LOCAL_FIRST_PROFILE.md`

---

## NoobAI XL 1.1

SOURCE_CLASS: `OFFICIAL_MODEL`
Official claims: `ACCEPTED`
Optimization profile: `CANDIDATE`
Claim group: `K-NOOB-*`

公式で保持:
- native tags caption
- Danbooru + e621 training dataset
- CFG 5–6
- Steps 25–30
- Euler a
- ~1024² area
- caption order:
  `<count>, <character>, <series>, <artists>, <special tags>, <general tags>, <other tags>`

PROMPT解釈:
- SpecialをGeneral supportへ埋めない
- native caption orderをbaselineとして尊重
- canonical/Alias/model-triggerのresponse差は別A/B
- e621 exposureはnon-human系を調べる理由にはなるが、生成が強い証明ではない

Current status:
- caption order fact `K-NOOB-001` = ACCEPTED
- `SPECIAL_FIRST_NATIVE_CAPTION` hard-target optimum `K-NOOB-003` = CANDIDATE
- camera専用最適位置の公式確定 = REJECTED as claim (`K-NOOB-004`)

主な疑い:
- `NOOB_SPECIAL_DISPLACED`
- `NOOB_ALIAS_MISMATCH`
- `NOOB_NEG_CONFLICT`
- `NOOB_NONHUMAN_PRIOR`

高優先テスト:
1. canonical vs Alias
2. Special placement
3. Special + minimum general support
4. non-human familiarity
5. default Negativeとのtarget collision

---

## Illustrious XL

SOURCE_CLASS: `OFFICIAL_MODEL`
Official version claims: `ACCEPTED`
Optimization claim: `CANDIDATE`
Claim group: `K-ILL-*`

公式方向:
- v1.0はDanbooru-style tag + natural language理解を掲げる
- v1.1はv1.0より natural-language focused と明記
- later versions/official platformもNL/high-resを前面に出す

PROMPT解釈:
- `Illustrious = booru-only` を普遍則にしない
- v0.1 / v1.0 / v1.1 / v2+ / derivativesを分離
- WAI derivativeの成功則をOnoma baseへそのまま移植しない
- tag-centered baselineから始め、relation/bindingが難しいときだけshort relation supportを候補化

Current claims:
- version flattening禁止 `K-ILL-001` = ACCEPTED
- v1.1 NL方向 `K-ILL-002` = ACCEPTED
- booru-only universal rule `K-ILL-003` = REJECTED
- tag + short relation optimization `K-ILL-004` = CANDIDATE / STAGE10_REQUIRED

高優先テスト:
1. tag-centered vs tag + short relation
2. simple vs relational Special
3. multi-actor binding
4. body-site precision
5. support density

---

## Anima

SOURCE_CLASS: `OFFICIAL_MODEL` for model-card facts; `COMMUNITY` for practical exceptions
Official claims: `ACCEPTED`
Optimization profile: `CANDIDATE`
Claim group: `K-ANIMA-*`

公式で保持:
- Danbooru-style tags + natural-language captions + combinationsで学習
- tagsはlowercase / spaces（score tags例外）
- tag section order:
  `[quality/meta/year/safety] [count] [character] [series] [artist] [general]`
- section内はarbitrary order
- tags + NL混在可能
- pure NLはdescriptive推奨
- multiple charactersではcharacter名だけでなくbasic appearanceが特に重要
- random tag dropout学習
- weightingは機能するがfamily-specific magnitude例あり
- Aesthetic profileではquality tags不要候補、score overuseへの警告あり

PROMPT解釈:
- relation/ownership/multi-actorを独立検証
- tag-only baseline
- 必要時だけ short relation sentence
- multi actorならappearance anchor候補
- 文章を増やしてattribute bleedが始まったら更に増やさず減らす

Current claims:
- tags + NL mix `K-ANIMA-001` = ACCEPTED
- appearance description official direction `K-ANIMA-002` = ACCEPTED
- official tag count `1girl/1boy` `K-ANIMA-003` = ACCEPTED
- `1 girl` global replacement `K-ANIMA-004` = REJECTED
- Qwen 1k/300-word rationale `K-ANIMA-005` = REJECTED
- `HYBRID_RELATION_AWARE` `K-ANIMA-006` = CANDIDATE / STAGE10_REQUIRED
- appearance-anchor A/B `K-ANIMA-007` = CANDIDATE / STAGE10_REQUIRED
- BREAK behavior `K-ANIMA-008` = runtime-scoped / local recheck
- Turbo CFG1 × Negative `K-ANIMA-009` = HOLD / local recheck

主な疑い:
- `ANIMA_RELATION_UNDERDESCRIBED`
- `ANIMA_APPEARANCE_LEAK`
- `ANIMA_OVERDESCRIPTION`
- `ANIMA_SCORE_SLOP`
- `ANIMA_WEIGHT_OVERSHOOT`

高優先テスト:
1. tag-only vs tag + one relation sentence
2. appearance anchor有無
3. short vs longer prose
4. profile別quality
5. weighting on/off

---

## Cross-family starting matrix

| Axis | WAI17 | Illustrious | NoobAI 1.1 | Anima |
|---|---|---|---|---|
| First style | lean tag-first candidate | exact-version tag-centered candidate | native caption baseline | tags or hybrid candidate |
| Special placement | high candidate | high/version scoped | official special-before-general baseline | relation may use prose candidate |
| NL relation | HOLD/targeted | candidate/version scoped | HOLD/targeted | strong candidate |
| Quality density | lean author direction | version dependent | official prefix exists | profile dependent |
| Long Negative | avoid as WAI default | HOLD | baseline exists; target collision test | profile dependent |
| Multi-actor | binding test | binding test | binding test | appearance-anchor priority candidate |
| Weighting | targeted only | targeted only | targeted only | family-specific magnitude |
| Hires | separate pass | separate pass | separate pass | workflow-specific |

## Version / freshness

Before applying any model claim:
- exact versionを確認
- `VERSION_AND_FRESHNESS.md` を参照
- source checked dateとlocal applicabilityを確認

## 詳細証拠

- `docs/stages/STAGE_10_PROMPT_MODEL_OFFICIAL_SOURCE_MATRIX_20260909.md`
- `docs/stages/STAGE_10_PROMPT_HARD_TARGET_FAMILY_MATRIX_20260909.md`
- `docs/stages/STAGE_10_PROMPT_TOSHIAKI_WIKI_CORRECTIONS_20260909.md`
