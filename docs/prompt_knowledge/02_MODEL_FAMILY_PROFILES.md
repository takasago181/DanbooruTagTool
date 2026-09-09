# 02 Model family profiles

Owner: PROMPT / Issue #5
Status: family-scoped knowledge summary. Not production specification.

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

Evidence: `AUTHOR_GUIDE`
Current project candidate profile: `LEAN_TAG_FIRST`

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

PROMPT候補:
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

詳細: `10_WAI17_LOCAL_FIRST_PROFILE.md`

---

## NoobAI XL 1.1

Evidence: `OFFICIAL_FACT`
Candidate profile: `SPECIAL_FIRST_NATIVE_CAPTION`

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

Evidence: `OFFICIAL_FACT`, exact version required
Candidate profile: `VERSION_SENSITIVE_TAG_CENTERED`

公式方向:
- v1.0はDanbooru-style tag + natural language理解を掲げる
- v1.1はv1.0より natural-language focused と明記
- later versions/official platformもNL/high-resを前面に出す

PROMPT解釈:
- `Illustrious = booru-only` を普遍則にしない
- v0.1 / v1.0 / v1.1 / v2+ / derivativesを分離
- WAI derivativeの成功則をOnoma baseへそのまま移植しない
- tag-centered baselineから始め、relation/bindingが難しいときだけshort relation supportを候補化

高優先テスト:
1. tag-centered vs tag + short relation
2. simple vs relational Special
3. multi-actor binding
4. body-site precision
5. support density

---

## Anima

Evidence: `OFFICIAL_FACT`
Candidate profile: `HYBRID_RELATION_AWARE`

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
-必要時だけ short relation sentence
- multi actorならappearance anchor候補
-文章を増やしてattribute bleedが始まったら更に増やさず減らす

主な疑い:
- `ANIMA_RELATION_UNDERDESCRIBED`
- `ANIMA_APPEARANCE_LEAK`
- `ANIMA_OVERDESCRIPTION`
- `ANIMA_SCORE_SLOP`
- `ANIMA_WEIGHT_OVERSHOOT`

重要訂正:
- tag modeのcountは公式に `1girl / 1boy / 1other`。`1 girl`をglobal defaultにしない
- 「Qwenが1k tokenまでだから300 words以下」という説明はRATIONALE_INCORRECT扱い

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
| First style | lean tag-first | exact-version tag-centered | native caption order | tags or hybrid |
| Special placement | high | high/version scoped | very high | relation may use prose |
| NL relation | HOLD/targeted | candidate/version scoped | HOLD/targeted | strong candidate |
| Quality density | lean | version dependent | official prefix exists | profile dependent |
| Long Negative | avoid as default | HOLD | baseline exists; target collision test | profile dependent |
| Multi-actor | binding test | binding test | binding test | appearance-anchor priority |
| Weighting | targeted only | targeted only | targeted only | family-specific magnitude |
| Hires | separate pass | separate pass | separate pass | workflow-specific |

## 詳細証拠

- `docs/stages/STAGE_10_PROMPT_MODEL_OFFICIAL_SOURCE_MATRIX_20260909.md`
- `docs/stages/STAGE_10_PROMPT_HARD_TARGET_FAMILY_MATRIX_20260909.md`
- `docs/stages/STAGE_10_PROMPT_TOSHIAKI_WIKI_CORRECTIONS_20260909.md`
