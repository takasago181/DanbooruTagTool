# Issue #132 — Worker Execution Card V1

Status: **ACTIVE OPERATIONAL CACHE / NOT SEMANTIC AUTHORITY**

Purpose: let normal ChatGPT Automation workers execute Pass A without re-reading ~60k characters of frozen documents every run.

This card does **not** replace or modify the frozen Pass-A contract. It is a compact execution cache derived from it.

Frozen manifest:
`docs/issue132/parallel/pass_a_contract_manifest_v1.json`

Expected manifest GitHub blob SHA at card creation:
`3bd09dde3a0fd15b9a3f86b22f294135f96a707c`

Frozen neutral:
- population: **31,003**
- SHA256: `ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d`
- identity-order SHA256: `f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b`

If the frozen manifest changes, CI reports contract drift, neutral SHA/order differs, or this card conflicts with a frozen contract, **stop and read the full frozen documents**. Otherwise workers should use this card rather than repeatedly reading every full contract file.

---

## 1. Mission

For every identity, independently answer:

> If an image-generation user wants this visible concept but does not know the exact Danbooru tag, where would they naturally look?

Optimize for:
- unknown-tag discovery;
- actual image-generation usefulness;
- adult/sexual generation as a normal workflow;
- semantic accuracy.

Do not use current #64/#76/Unified placement, current JP aliases/search, machine buckets, old candidates, post counts, or prototype assignments as semantic guidance.

Current app placement is the audit target, not Pass-A evidence.

---

## 2. Accuracy rule — ambiguity must never be hidden

### CHECKED is allowed only when all material meaning is clear

Use `CHECKED` only when:
- the identity has an ordinary, unambiguous visual meaning;
- semantic_summary can be stated confidently without outside knowledge;
- route choice does not depend on a subtle definition;
- local/body/theme decisions are also clear.

### Mandatory RESEARCHED gate

Use actual external semantic research before finalizing if **any** of these apply:

- unfamiliar word, transliteration, foreign phrase, specialist term;
- proper noun, named item, brand/model, title, event, meme, quote, franchise-specific reference;
- parenthetical qualifier whose meaning matters;
- common word with multiple plausible meanings;
- exact object type or technical equipment affects route/refinement;
- cultural/historical/reference knowledge affects meaning;
- sexual concept where action vs position vs object vs role vs body-site/theme is not immediately clear;
- anatomy/fetish term where body/theme selection is not certain;
- the worker internally needs words like “probably”, “seems”, “likely”, or is inferring from spelling;
- any material field would otherwise be a guess.

Research should be batched for efficiency when several rows need it, but **each identity still receives its own semantic judgment and actually used evidence URL**.

Evidence preference:
1. Danbooru/Safebooru wiki/tag information;
2. official/reference source;
3. reliable secondary source.

If reasonable research still cannot establish the meaning confidently:
- `SEMANTIC_UNRESOLVED`;
- `RESEARCHED`;
- evidence URL required;
- uncertainty_note required;
- no route/local/body/theme;
- route_vocabulary_gap = NO.

Never convert uncertainty into a confident browse route merely to increase throughput.

---

## 3. Discovery modes

- `BROWSE_WORTHY`: stable visual/category shelf is a natural starting point.
- `MIXED`: both stable visual browse and name/reference search are materially natural. Not an uncertainty bucket.
- `SEARCH_ORIENTED`: meaning is understood but name/reference search is the natural path. No routes/local/body/theme; gap=NO.
- `SEMANTIC_UNRESOLVED`: meaning remains uncertain after research. Rules above apply.

---

## 4. Top-level routes

Use a route only if a user could realistically begin from that shelf **without already knowing the tag noun**.

- `PEOPLE_COUNT`: number/group count.
- `RELATION_ROLE`: interpersonal relationship/role/dominance role.
- `BODY_SITE`: anatomical site is itself central.
- `HAIR_FACE`: hair/facial appearance; not emotion/gaze.
- `CLOTHING_EXPOSURE`: garments, worn accessories, clothing state, exposure.
- `TOOL_OBJECT`: props/tools/toys/weapons/vehicles/food/devices/foreground objects.
- `LIVING`: animals/plants/living scene elements.
- `NONHUMAN_TRANSFORM`: transformation/nonhuman/anatomically altered state.
- `ACTION_CONTACT`: actions/interactions/contact/sex acts/object manipulation.
- `POSE_POSITION`: posture/body position/limb arrangement/movement/sexual position where positional geometry itself is useful.
- `EXPRESSION_GAZE`: expression/emotion/gaze direction.
- `FLUID_EXCRETION`: bodily fluids/ejaculation/urination/excretion where intrinsic.
- `COMPOSITION_CAMERA`: viewpoint/crop/framing/camera angle/shot/POV.
- `SCENE_BACKGROUND`: location/environment/background/setting.
- `LIGHT_TIME_WEATHER`: lighting/time/weather/atmosphere.
- `COLOR_PATTERN_SHAPE`: color/pattern/shape when itself a meaningful generation control.
- `STYLE_PROCESSING`: art style/rendering/processing/medium-like presentation.
- `TEXT_SYMBOL`: visible text/symbol/layout element.
- `CONTENT_RATING`: true meta/content-presentation category; never generic “sexual”.

### Route strength

`CORE`: central unknown-tag starting point.

`SUPPORTING`: independently useful secondary starting point.

Normally use 1 CORE, occasionally 1 CORE + one independently useful second route. Third route is exceptional.

Do **not** add a route because:
- a word overlaps;
- it is technically related;
- it is an incidental modifier;
- many examples happen to contain it.

Hard anti-overclassification:
- color + target ≠ automatic COLOR route;
- object on/near body ≠ automatic POSE;
- action producing a pose ≠ automatic POSE unless geometry is independently useful;
- fixture/object ≠ automatic SCENE route;
- sexual content ≠ CONTENT_RATING.

---

## 5. Local refinements

Select only when parent top-level route is selected. Zero is valid. Normally max one local per selected parent.

ACTION_CONTACT:
- `ACTION_CONTACT/INTERACTION`
- `ACTION_CONTACT/INTIMATE`
- `ACTION_CONTACT/OBJECT_USE`

CLOTHING_EXPOSURE:
- `CLOTHING/ACCESSORY`
- `CLOTHING/COSTUME`
- `CLOTHING/EVERYDAY`
- `CLOTHING/UNIFORM`
- `CLOTHING_STATE_EXPOSURE/`

LIVING:
- `LIVING_NATURE/CREATURE`
- `LIVING_NATURE/PLANT`

TOOL_OBJECT:
- `OBJECT_PROP/DAILY`
- `OBJECT_PROP/FOOD`
- `OBJECT_PROP/VEHICLE`
- `OBJECT_PROP/WEAPON`

TEXT_SYMBOL:
- `TEXT_SYMBOL/LAYOUT`
- `TEXT_SYMBOL/SYMBOL`
- `TEXT_SYMBOL/TEXT`

EXPRESSION_GAZE:
- `EXPRESSION_EMOTION/`
- `GAZE_ORIENTATION/`

Do not force an identity into a local refinement just because its parent route was selected.

---

## 6. Body/theme facets

Body-site facets — select only when explicit and intrinsic:
- `MALE_GENITAL`
- `BREAST_NIPPLE`
- `FEMALE_GENITAL`
- `MOUTH_ORAL`
- `BUTTOCK_ANAL`
- `URETHRA`

Theme facets — select only when intrinsic:
- `BDSM_RESTRAINT`
- `INJURY_R18G`
- `REPRO_PREGNANCY_LACTATION`

Do not infer a body site from a broad sexual act when the exact site is not part of the identity meaning.
Do not use theme facets as generic sexual labels.

---

## 7. route_vocabulary_gap

YES only when:
- meaning is understood;
- concept is browse-useful;
- existing 19 routes cannot represent an important user mental model without distortion.

Do not invent IDs.

If SEARCH_ORIENTED or SEMANTIC_UNRESOLVED: gap=NO.

---

## 8. Exact output schema — 22 columns

1. review_seq
2. identity_key
3. manual_seen
4. semantic_summary_ja
5. discovery_mode
6. route_1_id
7. route_1_strength
8. route_1_reason_ja
9. route_2_id
10. route_2_strength
11. route_2_reason_ja
12. route_3_id
13. route_3_strength
14. route_3_reason_ja
15. local_refinement_ids
16. body_site_ids
17. theme_ids
18. route_vocabulary_gap
19. route_vocabulary_gap_note
20. review_depth
21. evidence_urls
22. uncertainty_note

`manual_seen=YES`.

Array fields are valid JSON arrays inside CSV cells.

Never hand-wave structural validation. Before each checkpoint write:
- exactly 22 fields per row;
- JSON arrays parse;
- route/local/facet IDs are allowed;
- SEARCH_ORIENTED/UNRESOLVED constraints hold;
- assigned rows form the exact lane-local prefix.

---

## 9. Efficient per-row finalization — one semantic pass, not two full passes

For each identity, do not draft a weak row and plan to fix it in a second full reread.

Instead finalize the row once using this gate:

1. Do I know exactly what it means?
   - no / not sure -> RESEARCHED.
2. Is browse, mixed, search, or unresolved truly the natural discovery mode?
3. What is the strongest realistic unknown-tag starting route?
4. Is any second route independently useful, rather than merely related?
5. Does a local refinement naturally fit?
6. Is a body/theme facet intrinsic?
7. Am I inferring anything from spelling alone?
   - yes -> RESEARCHED.
8. Are all 22 fields structurally valid?

Only then mark that row complete and move on.

This replaces the expensive “classify 25, then reread all 25 from scratch” operation.

---

## 10. Persistence and QA cadence

- checkpoint persistence unit: **25 completed rows**
- checkpoint is save-only; immediately continue
- do not update status after every 25-row checkpoint
- update status at run end, lane completion, or after a 100-row QA boundary
- do not wait for CI after each checkpoint
- check CI at run end or when an actual failure signal appears

### 100-row QA is lane-boundary based, not run-boundary based

Whenever cumulative lane-local reviewed_count crosses a multiple of 100, QA that completed lane-local 100-row block.

Re-review all high-risk rows in that block:
- RESEARCHED
- MIXED
- SEARCH_ORIENTED
- SEMANTIC_UNRESOLVED
- route_vocabulary_gap=YES
- route_2/route_3
- body/theme facets
- adult/sexual concepts

Also deterministic spot-check ordinary CHECKED single-route rows:
- at least every fifth such row, or 20 rows if available.

Look for systematic drift/family inconsistency and repair before continuing past the boundary.

Do not reread all 100 ordinary rows without a reason.

---

## 11. Tool-efficiency rules

- Batch web searches for multiple ambiguous identities when possible.
- Still record per-row evidence actually used.
- Do not research obvious common visual concepts merely to prove that they are obvious.
- Do not repeatedly fetch full frozen documents when manifest/card are unchanged.
- Do not repeatedly verify the entire 31,003-row neutral order if latest successful CI and frozen neutral manifest already validate it.
- Fetch only the next needed neutral/lane range when the connector permits range reads.
- Do not poll CI/checkpoint status between every save.
- GitHub live checkpoints are the progress authority; stale status.json is recoverable.

---

## 12. Stop/continue rule

300 new rows remains a ceiling.

**Do not self-stop merely because the worker estimates that execution time may be running low.**

Continue after every valid 25-row checkpoint unless:
- an actual tool/execution limit prevents further work;
- a GitHub write fails/conflicts;
- semantic research tool is unavailable when required;
- contract/neutral/prefix drift is detected;
- lane completes.

If forcibly interrupted later, already committed 25-row checkpoints preserve progress.

Allowed short-run stop reasons:
- `EXECUTION_LIMIT` only when an actual execution limit/interruption is encountered, not anticipated;
- `TOOL_LIMIT`;
- `CONTRACT_DRIFT`;
- `GIT_CONFLICT`;
- `SEMANTIC_TOOL_BLOCKER`;
- `REMAINING_LT_300`.

Do not trade semantic certainty for row count.
