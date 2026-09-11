# Issue #56 Special UI Genre Pilot Review v1

Status: **FORMAL_150_REVIEW_COMPLETE / INDEPENDENT_AUDIT_PENDING**

This document records the first formal, reproducibly selected UI-browsing taxonomy pilot for the frozen 2,788-entry Special Core Dictionary.

It is **not** a semantic revalidation of Special identity and does not mutate production/canonical data.

## 1. Evidence / reproducibility

Feature branch:
- `dev/issue56-special-dict-ui-taxonomy`

Selector:
- `tools/issue56_ui_genre_pilot_selector.py`
- selector version: `issue56-ui-pilot-v1`

Formal generated artifact metadata:
- source rows: **2,788**
- unique Special IDs: **2,788**
- formal pilot rows: **150**
- unique pilot IDs: **150**
- generated pilot CSV SHA-256: `3b970c6ec0d600087aaf89df642e669cd1744cc78a402e75027f9501f215a23e`
- materialized source CSV SHA-256: `d61b3ef93609db8d51f2e6ab4125bab86577a27ae95211dfc09523f49c1a9472`

GitHub Actions:
- run `34658973866`: selector/test/build/upload **SUCCESS**
- run `34659459056`: reviewed-map + taxonomy Japanese-label consistency tests **SUCCESS**

The formal global high-usage stratum is derived only after all current prompt-reference parts are materialized. The earlier exploratory part01 block is not treated as the global top-50.

## 2. Formal sample composition

Exact selection strata:

| Stratum | Rows |
|---|---:|
| Global high-usage from old `その他・文脈` | 50 |
| Alias | 15 |
| Alias canonical controls | 15 |
| Body / exposure boundary | 6 |
| Activity / contact boundary | 6 |
| Tools / BDSM boundary | 6 |
| Role / meta / context boundary | 6 |
| Injury / body / BDSM boundary | 6 |
| Rare numeric | 10 |
| Rare non-count | 10 |
| Deterministic pseudo-random | 20 |
| **Total** | **150** |

The formal global high-usage 50 actually spans multiple old `その他` files:
- part01: 24
- part06: 13
- part05: 6
- part07: 6
- part03: 1

This confirms the selector is not relying on source-file order.

## 3. Human review result

Classification state after the full 150-row review:

| Status | Rows |
|---|---:|
| `HUMAN_REVIEWED` | 124 |
| `AUTO_INHERITED_ALIAS` | 24 |
| `REVIEW_REQUIRED` | 2 |
| `AMBIGUOUS` | 0 |

Only **2 / 150** rows could not be given a defensible primary browsing path from current evidence.

Unresolved rows:
1. Special ID 1084 `arm slave (mecha)` — existing surface/Japanese description is not clear enough to determine the true identity/browse route.
2. Special ID 1227 `cum on fourth wall` — requires confirmation whether the human browsing intent is physical-fluid placement or a meta/presentation effect.

These are intentionally left unresolved rather than forced into a catch-all.

## 4. Primary-genre distribution in the formal pilot

| Japanese UI genre | Rows |
|---|---:|
| 身体・解剖 | 31 |
| 裸体・衣服・露出 | 28 |
| 性行為・性的刺激 | 19 |
| 体液・排泄・汚損 | 11 |
| 拘束・BDSM・支配 | 10 |
| 属性・関係・役割 | 9 |
| メタ・レーティング | 8 |
| 道具・性具・機械 | 7 |
| 接触・挿入・部位行為 | 6 |
| 異形・非人間・触手・変形 | 6 |
| 損傷・R18G | 6 |
| 状況・場面 | 4 |
| ポーズ・体位・構図 | 3 |
| 未確定 | 2 |

No candidate top-level genre became a new generic catch-all in this pilot. The largest category is 31 / 150 rather than an uncontrolled majority.

`生殖・妊娠・授乳` happened to receive zero rows from this selector. A direct review of the existing 14-row source confirms a coherent pregnancy/birth/lactation cluster remains, while also showing that old-reference placement is not authoritative: anatomy-only rows such as cervix/uterus and object rows such as breast pump can be relocated during the later 01–12 cross-audit. The top-level genre is therefore retained, but its old category membership is not frozen.

## 5. Secondary-path pressure

Number of secondary browsing paths per pilot row:
- 0 paths: **86**
- 1 path: **60**
- 2 paths: **4**
- 3+ paths: **0**

This supports the intended rule that secondary paths are sparse alternate entrances rather than semantic exhaustiveness.

## 6. Top-level taxonomy decision from this pilot

Current 14-genre candidate remains viable:

1. 身体・解剖
2. 裸体・衣服・露出
3. ポーズ・体位・構図
4. 性行為・性的刺激
5. 接触・挿入・部位行為
6. 道具・性具・機械
7. 拘束・BDSM・支配
8. 体液・排泄・汚損
9. 生殖・妊娠・授乳
10. 異形・非人間・触手・変形
11. 損傷・R18G
12. 属性・関係・役割
13. メタ・レーティング
14. 状況・場面

### `状況・場面` decision

Retain as an **ADOPT candidate**, not a fallback category.

Formal pilot examples support it, and a conservative scan of the full materialized source already finds a broader coherent cluster around concepts such as public/stealth/discovered/watched/transactional/event context.

Its boundary remains strict:
- not rating/censorship metadata;
- not participant relation/role;
- not camera composition;
- not the underlying act itself;
- “difficult to classify” is never sufficient.

Final full-distribution audit must verify that this genre does not recreate old `その他` pressure.

## 7. Subgenre changes caused by real data

### ADOPT candidate: `BODY_ADORNMENT_MARK / 装飾・印`

Repeated pilot cases show a useful browse cluster for body-attached decoration/mark concepts. Pure anatomical morphology/color remains under body-part subgenres.

### ADOPT candidate: `PUBIC_HAIR / 陰毛`

The formal global high-usage stratum contains multiple distinct high-use pubic-hair rows. This is a recurring natural Japanese browsing intent and meaningfully shortens `身体・解剖` browsing.

### RENAME: `SEE_THROUGH / 透け・薄布`

Use:
- `THROUGH_CLOTHING_VISIBILITY / 透け・衣服越し`

Reason: real data includes clothing-relative visible shape/indentation where the material is not necessarily transparent. The broader Japanese label better matches the browse intent without claiming semantic identity.

### SPLIT the former orgasm/aftermath/implied timing mixture

Use three clearer browsing subgenres:
- `ORGASM_RESPONSE / 絶頂・反応`
- `BEFORE_AFTER_ACT / 直前・事後`
- `IMPLIED_GESTURE / 示唆・仕草`

Reason: the formal sample contains orgasm, gestures, and implied-after cases that users would naturally browse differently. Keeping them in two mixed buckets created avoidable ambiguity.

### KEEP the other current priority subgenre boundaries

The pilot did not show a systematic failure in:
- body vs clothing-relative visibility;
- named activity vs body-site/contact topology;
- ordinary sex-use tools vs restraint/pain/control purpose;
- injury itself vs BDSM pain vs anatomy;
- relation/role vs metadata vs situation.

## 8. Alias result

The formal 15 Alias/canonical control pairs were compatible with default canonical browsing-path inheritance.

The earlier exploratory audit also found a real contradictory-surface case outside this formal pair set. Therefore the rule remains:

```text
resolved canonical + no presentation conflict -> AUTO_INHERITED_ALIAS
otherwise -> REVIEW_REQUIRED
```

Alias inheritance is a default, not an unquestionable semantic rewrite.

## 9. Japanese-first UI decision

The pilot supports the fixed display contract:
- internal genre/subgenre IDs: English/ASCII is acceptable;
- every genre/subgenre: mandatory Japanese label;
- normal genre/subgenre UI: Japanese only;
- Special result row: Japanese + English tag;
- long classification reasoning: detail/audit only, never normal list UI.

The candidate taxonomy file is:
- `docs/issue56/pilot/issue56_ui_genre_taxonomy_candidate_v1_2.json`

The reviewed 150-row path map is:
- `docs/issue56/pilot/issue56_ui_genre_pilot_v1_classification_map.csv`

## 10. Safety / eligibility separation

Reference-only age-restricted identities remain classified for dictionary completeness/detection, but UI genre assignment does **not** make them Prompt-eligible. Adult-only Prompt eligibility and safety remain a separate existing layer and cannot be overridden by this taxonomy.

## 11. Gate decision

Current decision:

**`FORMAL_150_PILOT_PASS_WITH_REFINEMENTS / READY_FOR_INDEPENDENT_UI_TAXONOMY_AUDIT`**

Do not expand directly to all 2,788 yet.

Next sequence:
1. fresh independent audit of selector design, 150-row mapping, Japanese labels, boundary consistency and catch-all risk;
2. resolve or explicitly park the two `REVIEW_REQUIRED` pilot rows;
3. if audit passes, freeze the taxonomy version for expansion;
4. classify old `その他・文脈` population;
5. cross-audit old categories 01–12;
6. produce full 2,788 UI mapping and final distribution/unresolved-pool audit.
