# Issue #118 Final Design Checkpoint

Status: **RESEARCH COMPLETE / DESIGN FROZEN / IMPLEMENTATION REQUIRES EXPLICIT USER APPROVAL**

This document freezes the research outcome for Issue #118:

> Design a user-facing sexual / general-purpose intent filter for the unified ordinary-tag browse surface.

This checkpoint is research/design authority only. It does **not** mutate production classification data, `main`, Issue #117 implementation, `catalog.db`, or `UserData/user.db`.

## 1. Final research authority

Research branch:

`research/issue118-cluster-triage-v8`

Final research sidecar:

- `docs/issue118/research_sidecar_v96.csv`
- `docs/issue118/research_sidecar_summary_v96.json`

Final sidecar materialization commit:

`624dc7b1c2ea376a4b31e0839a7d55f79877d0f0`

Canonical ordinary-tag identity union:

- General: 30,629
- Special: 3,059
- normalized exact overlap: 1,936
- unique ordinary-tag identities: **31,752**

Final review-status counts:

- `AUTO_HIGH_CONF`: **22,371**
- `HUMAN_REVIEWED`: **9,376**
- `UNCLASSIFIED`: **5**

Final semantic counts:

- `SEXUAL`: **2,037**
- `CONTEXTUAL`: **1,951**
- `NON_SEXUAL`: **27,759**
- `null / UNCLASSIFIED`: **5**

The five deliberately unresolved identities are:

- `cock-tail`
- `insertion_threshold_(meme)`
- `knee_boobs`
- `lilistia`
- `powerful_ass`

They are intentionally retained as `UNCLASSIFIED`. Precision is preferred over forced coverage.

## 2. Frozen semantic model

`UNKNOWN` is not a semantic class. It is missing classification evidence.

Source model:

```text
sexual_intent
- SEXUAL
- NON_SEXUAL
- CONTEXTUAL
- null

review_status
- HUMAN_REVIEWED
- AUTO_HIGH_CONF
- UNCLASSIFIED
```

Valid combinations:

- classified intent + `HUMAN_REVIEWED`
- classified intent + `AUTO_HIGH_CONF`
- `null` + `UNCLASSIFIED`

Invalid combinations must fail closed.

### SEXUAL

Use when the canonical concept itself carries explicit sexual intent, a sexual act, sexual role, sexual-use device, or intrinsically sexual fetish meaning.

Representative reviewed examples:

- `plap`
- `tekoki_karaoke`
- `uncommon_stimulation`
- `verbal_degradation`
- `wet_and_messy`
- `mushikan`

The existence of Safe/General depictions does not automatically make an intrinsically sexual concept contextual.

### NON_SEXUAL

Use when the canonical concept is ordinarily general-purpose/non-sexual, even if it can appear in adult imagery or has an adult-source association.

Representative reviewed negative controls include:

- `bullet_wound`
- `tit_(bird)`
- `breast_slider`
- `wet_spot`
- `yjsnpi_interview_(meme)`
- ordinary objects, places, styles, identities, fandom references and camera/background concepts

A tag does not become sexual merely because it appears in an R18 image.

### CONTEXTUAL

Use only when the canonical concept itself has independently natural/substantial sexual **and** general-purpose discovery meanings.

Representative reviewed examples:

- `omegaverse`
- `tawawa_challenge`
- `umapyoi_(phrase)`
- `twitter_strip_game`
- `twitter_cutting_game`
- `ruined_for_marriage`

Do not use CONTEXTUAL merely because a normal tag can coexist with sexual content.

### UNCLASSIFIED

Use only when semantic evidence is insufficient to make a reliable identity-level decision.

UNCLASSIFIED must not silently become NON_SEXUAL.

## 3. Evidence/source precedence

Classification authority is frozen in this order:

1. **Exact identity human review**
   - highest authority for the reviewed identity;
   - explicit corrections supersede older research verdicts.

2. **Accepted AUTO_HIGH_CONF rule**
   - allowed only when the rule has independent validation/holdout support and no known boundary contradiction;
   - rule identity/provenance must remain auditable.

3. **Taxonomy / membership / rating / generation metadata**
   - #64 General paths;
   - #76 Special kind/body/theme;
   - General/Special membership;
   - rating/content severity;
   - generation family/role metadata.
   
   These may route discovery, propose review candidates, or corroborate an exact decision, but are **not direct sexual-intent authority**.

4. **Insufficient evidence**
   - `sexual_intent = null`
   - `review_status = UNCLASSIFIED`

Conflicting authority or malformed state must fail closed rather than infer a class.

## 4. Rejected shortcuts

The research explicitly rejects:

- `Special == SEXUAL`
- `General == NON_SEXUAL`
- `R18 / R18G == SEXUAL`
- anatomy token => sexual
- breast token => sexual/contextual
- restraint/BDSM-related routing metadata => sexual
- adult/fetish-risk candidate => sexual
- broad taxonomy root => sexual
- broad semantic cluster => one shared verdict
- substring-only classification such as generic `sex`
- adult-source origin => sexual

General/Special membership, sexual intent, rating/severity, and generation semantics remain separate axes.

## 5. Frozen user-facing behavior

Visible content filter:

```text
内容
[すべて] [一般向け] [性的]
```

Mapping:

- `すべて`
  - SEXUAL
  - NON_SEXUAL
  - CONTEXTUAL
  - UNCLASSIFIED

- `一般向け`
  - NON_SEXUAL
  - CONTEXTUAL

- `性的`
  - SEXUAL
  - CONTEXTUAL

- UNCLASSIFIED
  - visible only in `すべて`

This prevents five unresolved identities from being silently assigned a meaning.

### Why CONTEXTUAL is in both visible filters

CONTEXTUAL is a semantic verdict that the concept itself has substantial natural use in both discovery intents. Hiding it from either side would make one of the two filtered views incomplete.

## 6. Scope behavior

The #118 authority covers the **31,752 ordinary General/Special identity union only**.

Therefore v1 behavior is frozen as:

- apply the content filter in ordinary `Tags` scope;
- Character / Copyright / Artist scopes do **not** apply sexual-intent filtering in v1;
- when switching temporarily to Character / Copyright / Artist, preserve the selected ordinary content filter state but ignore it in that scope;
- when returning to Tags scope, restore and apply the previous selection.

The filter persists across:

- primary route changes;
- local subroute changes;
- body-site facets;
- theme facets;
- `深掘りのみ`;
- query changes.

`クリア` remains query-only.
`全解除` should clear unified browse refinements including the content filter back to `すべて`, while preserving query text, consistent with the #117 browse-state contract.

## 7. Interaction contract with Issue #117

Extend the #117 unified ordinary browse state conceptually with one additional field:

```text
scope
primaryRoute?
localSubroute?
bodySites[]
themes[]
deepOnly
contentIntent   // ALL | GENERAL_PURPOSE | SEXUAL
```

Filtering semantics:

- existing query/ranking remains the authority for search order;
- route/local/body/theme/deepOnly/contentIntent compose with AND semantics;
- sexual-intent filtering removes non-matching identities but **must not rerank** survivors;
- one canonical identity remains one result card regardless of General/Special overlap;
- neutral Tags + empty query + no active browse constraints remains lightweight guidance and must not eagerly render all 31,752 identities.

No #117 General/Special membership mutation is authorized by this design.

## 8. Proposed production data contract

Recommended canonical-keyed production sidecar:

```text
canonical
sexual_intent          # SEXUAL | NON_SEXUAL | CONTEXTUAL | empty
review_status          # HUMAN_REVIEWED | AUTO_HIGH_CONF | UNCLASSIFIED
classification_source  # stable review/rule id
review_note            # short auditable reason
```

Production validation must reject:

- duplicate canonical identities;
- canonical outside the accepted ordinary identity union;
- invalid enum values;
- classified row with empty intent;
- UNCLASSIFIED row with non-empty intent;
- conflicting rows for the same canonical;
- identity-union count/hash drift without an explicit rebuild decision.

A manifest should record:

- source union identity count/hash;
- sidecar hash;
- semantic counts;
- review-status counts;
- retained UNCLASSIFIED identities;
- source/version provenance.

## 9. Catalog/runtime architecture

#118 should follow the accepted #114 runtime boundary.

Recommended flow:

```text
reviewed canonical-keyed source sidecar
        ->
explicit catalog build
        ->
CatalogEntry identity metadata
        ->
one-time RuntimeCatalogIndex sets/indexes
        ->
cheap query/browse set intersection
```

Do not:

- parse research CSVs during normal startup;
- classify per keystroke;
- inspect General/Special taxonomy per keystroke;
- rebuild content-intent sets on every query;
- rerank search results;
- enumerate all ordinary identities in neutral empty state.

A reasonable CatalogEntry design shape is:

```text
SexualIntentClass?
- NonSexual
- Contextual
- Sexual

SexualIntentClassificationStatus
- Unclassified
- AutoHighConfidence
- HumanReviewed
```

The runtime filter needs only precomputed identity metadata/sets. The provenance status may remain available for diagnostics/audit but must not change visible matching semantics.

No `UserData/user.db` schema migration is required for the classification authority itself.

## 10. Performance expectation

The feature is acceptable only if it preserves the #114 responsiveness invariants already frozen in #117:

- one-time runtime index construction;
- no per-keystroke classification;
- no eager 30k+ card creation;
- retain result virtualization/two-column behavior;
- retain SearchEngine/RuntimeCatalogIndex ranking;
- no synchronous user.db persistence regression;
- no full Prompt refresh caused by content-filter changes.

The intended operation after indexing is effectively a set membership/intersection check per candidate result.

## 11. Acceptance tests for implementation

Minimum gates:

### Authority/data

1. exactly **31,752** unique normalized ordinary identities in the accepted source union;
2. exactly:
   - 22,371 AUTO_HIGH_CONF
   - 9,376 HUMAN_REVIEWED
   - 5 UNCLASSIFIED;
3. exactly:
   - 2,037 SEXUAL
   - 1,951 CONTEXTUAL
   - 27,759 NON_SEXUAL
   - 5 null;
4. retained null identities exactly:
   - `cock-tail`
   - `insertion_threshold_(meme)`
   - `knee_boobs`
   - `lilistia`
   - `powerful_ass`;
5. no invalid class/status pair;
6. no duplicate canonical authority rows;
7. no General/Special membership mutation.

### Visible filtering

8. `すべて` includes all four source states;
9. `一般向け` includes NON_SEXUAL + CONTEXTUAL only;
10. `性的` includes SEXUAL + CONTEXTUAL only;
11. the five UNCLASSIFIED identities appear in `すべて` but not in either narrowed filter;
12. CONTEXTUAL representative identities appear in both narrowed filters;
13. SEXUAL-only representative identities do not appear under `一般向け`;
14. NON_SEXUAL-only representative identities do not appear under `性的`.

### #117 composition

15. content filter composes with route/local/body/theme/deepOnly/query using AND semantics;
16. filtering does not change search ranking among surviving results;
17. General/Special overlap still renders one canonical result card;
18. Character/Copyright/Artist ignore the ordinary content filter in v1;
19. returning to Tags restores the prior content filter selection;
20. `全解除` returns content filter to `すべて` and preserves query;
21. `クリア` clears query only;
22. neutral empty Tags state still does not enumerate the full identity population.

### Runtime/protected boundaries

23. no runtime parse of research corpora;
24. no user.db reset/schema migration;
25. no protected catalog/user data mutation during DEV validation;
26. full/focused tests and `git diff --check` pass;
27. available performance characterization shows no material regression against the accepted post-#114 behavior.

## 12. Final design decision

**Research verdict: IMPLEMENTATION RECOMMENDED, AFTER EXPLICIT USER APPROVAL.**

Reason:

- classification coverage is effectively complete for practical product use while preserving five honest unknowns;
- the semantic model survived adversarial examples and large-scale review;
- the visible mapping is explainable;
- the design fits #117 without changing General/Special membership;
- runtime cost can remain a cheap precomputed identity filter;
- unresolved identities have a safe explicit behavior rather than being silently misclassified.

Issue #118 research should therefore stop here unless a concrete regression or new semantic counterexample is demonstrated.

The next product gate is explicit approval to promote this frozen design into a production authority/build input and implement the #117 content filter on a feature branch.

## 13. Protected-boundary confirmation

This research sequence intentionally preserved:

- `production/main`: unchanged by #118 research;
- Issue #117 implementation code: unchanged;
- production catalog: unchanged;
- `UserData/user.db`: unchanged;
- review verdict provenance: external/human inputs, never generated by the sidecar materializer;
- research artifacts: non-production authority until explicit promotion approval.
