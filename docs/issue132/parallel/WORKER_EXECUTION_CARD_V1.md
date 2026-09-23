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

Use actual external semantic research before finalizing whenever **material uncertainty remains**.

Research is required for:
- unfamiliar words, transliterations, foreign phrases, specialist terms, or polysemous words;
- proper nouns / brands / titles / events / memes / franchise references **when the exact referent or semantic scope is not already confidently known, or when that scope affects browse-vs-search / route / facet judgment**;
- parenthetical qualifiers whose meaning materially changes the concept;
- technical object types whose exact function affects route/refinement;
- cultural/historical/reference knowledge that is necessary for the classification;
- sexual/anatomical/fetish concepts where action vs position vs object vs role or body/theme selection is not immediately certain;
- any case where the worker internally needs words like “probably”, “seems”, or “likely”, or is inferring from spelling;
- any material field that would otherwise be a guess.

**A proper noun alone is not sufficient reason to research.** If the exact referent is genuinely common/clear and no material classification choice depends on hidden scope, CHECKED is allowed. Example: an unambiguous country name or year used only as a name/reference can be CHECKED + SEARCH_ORIENTED without wasting a web lookup.

The optimization rule is: remove redundant verification of already-certain meaning, never remove research needed to resolve uncertainty.

Research should be batched for efficiency when several rows need it, but **each identity still receives its own semantic judgment and actually used evidence URL**.

Evidence preference:
1. Danbooru/Safebooru wiki/tag information;
2. official/reference source;
3. reliable secondary source.

The evidence must support the **actual identity meaning/scope being asserted**. A generic adjacent-topic page, franchise overview, or unrelated tag page is not sufficient merely because it shares vocabulary. If the source only proves surrounding context but not the material meaning used for routing, keep researching or record the uncertainty.

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
- about 10% of ordinary CHECKED single-route rows in that block, with a minimum of 10 when available.
- Coordinator provides an independent second-line sample, so workers should not reread a large ordinary subset without a concrete signal.

Look for systematic drift/family inconsistency and repair before continuing past the boundary.

Escalation rule:
- if **2 or more** deterministic ordinary-CHECKED spot checks need semantic correction; or
- one error indicates a repeated family/rule problem that may affect multiple rows;

then expand QA to **all ordinary CHECKED rows in that 100-row block** before continuing.

This makes the cheap sample a detector, not a license to leave a suspicious block partially checked.

Do not reread all 100 ordinary rows when the sample/high-risk review remains clean.

---

## 11. Tool-efficiency rules

- Batch independent web searches for several ambiguous identities in one tool call when possible; still record evidence per RESEARCHED row.
- Do not research obvious/common/unambiguous concepts merely to prove that they are obvious.
- Normal preflight must not fetch this card body or the full frozen manifest if their GitHub blob SHAs match the pinned expected values; use one metadata/directory read to verify SHAs.
- Do not repeatedly fetch full frozen documents when pinned SHAs are unchanged.
- Retrieve the neutral artifact as data, then **programmatically filter/extract only the next lane-local work window**. Do not inject/read all 31,003 neutral rows into semantic model context.
- Do not repeatedly recompute neutral SHA/order after a latest successful CI has validated the same frozen artifact; verify pinned artifact/manifest identity and proceed.
- Do not poll CI/checkpoint status between every save.
- Do not update status after every 25 rows.
- GitHub live checkpoints are progress authority; stale status.json is recoverable.

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
