# Issue #132 — Current recommended direction v3

Date: 2026-09-23 JST
Status: **PRE-HANDOFF RESEARCH / NO PRODUCTION CHANGE**

This file contains the current #132 direction only.

Historical Phase 1–6 experiments remain evidence in their own documents, but older sample-first, bounded-population, 200-row-shard, and first-pass KEEP/ADD instructions are superseded here.

---

## 1. Product objective

The user goal is:

> 作りたい画像の見た目・行為・部位・体位・衣装・構図などから、Danbooruタグ名を知らなくても自然に目的タグへ辿れること。

Optimize for:
- unknown-tag discovery;
- understandable Japanese UI;
- actual image-generation control axes;
- adult/sexual generation workflows as a first-class use case;
- preservation of direct Japanese/English/alias search;
- low runtime cost;
- simple architecture.

Do not optimize for:
- taxonomy completeness;
- elegant ontology;
- percentage of classified rows;
- number of changes;
- recommendation/scene-completion behavior.

---

## 2. Completion scope

The complete ordinary runtime identity population is reviewed:

**31,003 identities**

No machine bucket, heuristic family, or bounded test may remove identities from semantic review.

No 32/64/100-row sample is used to approve the methodology.

The full population itself is the evaluation/calibration surface.

---

## 3. Pass A — independent Luna discovery map

Luna reviews all 31,003 identities without seeing the current product placement.

Neutral input is generated from tracked #118 authority only:

- `review_seq`
- `identity_key`
- `source_surfaces`

Generator:

`scripts/issue132/build_luna_neutral_input.py`

Pass A intentionally hides:
- current #64 path;
- current #76 kind/body/theme;
- current Unified routes;
- current local refinements;
- #118 sexual-intent verdict;
- General/Special membership;
- production Japanese overlay/search terms;
- aliases;
- usage/post count;
- machine audit labels;
- prior Phase 1/prototype proposals.

Reason:

The first question is semantic discovery:

> このタグを知らない状態で、この視覚概念を探すならどこを開くのが自然か。

It is not:

> 今の分類をKEEPするか変えるか。

---

## 4. Pass A output

Every identity is individually reviewed.

Output contract:

`docs/issue132/LUNA_PASS_A_LEDGER_CONTRACT.md`

Luna records:

- short Japanese semantic summary;
- discovery mode:
  - BROWSE_WORTHY
  - MIXED
  - SEARCH_ORIENTED
  - SEMANTIC_UNRESOLVED
- up to three existing Unified routes;
- route strength:
  - CORE
  - SUPPORTING
- existing local refinement intent where naturally applicable;
- existing body-site facets where intrinsic;
- existing theme facets where intrinsic;
- route-vocabulary gap;
- CHECKED / RESEARCHED;
- evidence URLs when research was required;
- meaningful residual uncertainty.

Route/local/facet semantics:

`docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md`

Important:

Pass A does **not** output KEEP / ADD_SECONDARY / CHANGE_ROUTE.

---

## 5. Continuous execution

The review is one continuous 31,003-identity job.

There are no semantic shards.

Neutral order is deterministic:

`SHA256("issue132-pass-a-v2|" + identity_key)`

The ledger must always be an exact prefix of that order.

Periodic commits/checkpoints are persistence only.

Resume from the first unreviewed identity.

No user "continue" input is required between checkpoints.

Validator:

`scripts/issue132/validate_luna_pass_a.py`

---

## 6. Pass B — deterministic diff

After Pass A is frozen, compare the independent result against current product metadata.

Derive review flags such as:

- COVERED
- MISSING_CORE_ROUTE
- MISSING_SUPPORTING_ROUTE
- CURRENT_ROUTE_NOT_REPRODUCED
- MISSING_LOCAL_REFINEMENT
- MISSING_BODY_FACET
- MISSING_THEME_FACET
- SEARCH_ORIENTED
- SEMANTIC_UNRESOLVED
- ROUTE_VOCABULARY_GAP

These are audit queues.

They do not directly mutate production.

---

## 7. Pass C — full-population product reconciliation

Only after Pass A freezes, join real product context:

- #64 paths;
- #76 kind/body/theme;
- current Unified routes/local routes;
- #118 content intent;
- production Japanese display/search;
- approved aliases;
- usage/post count;
- result/shelf counts;
- machine pattern families.

Then evaluate:

1. semantic centrality;
2. unknown-tag lookup value;
3. incremental value beyond current search/facets;
4. route growth across the full population;
5. shelf coherence;
6. narrowability after entering the route;
7. adult/sexual workflow impact;
8. runtime/performance cost.

Authority:

`docs/issue132/FULL_POPULATION_PRODUCT_RECONCILIATION_GATE.md`

No quotas are used.

Distribution anomalies are bias alarms only.

---

## 8. Systemic fixes before row overrides

If thousands of identities disagree in the same way, first inspect whether the real problem is:

- one user-facing label;
- one General->Unified mapping;
- one Special->Unified mapping;
- one missing refinement distinction;
- owner taxonomy authority.

Do not automatically create thousands of identity overrides.

Examples already known for post-Pass-A inspection include:
- #64 POSE_MOVEMENT "ポーズ・動き" vs Unified "ポーズ・体位";
- General role concepts vs Special RELATION_ROLE;
- General body states/fluids vs Special FLUID_EXCRETION;
- broad Special POSE_SCENE projection.

Context:

`docs/issue132/UNIFIED_ROUTE_SYSTEMIC_RISK_AUDIT.md`

Resolution preference:

1. correct user-facing wording if sufficient;
2. correct one deterministic projection if that is the root cause;
3. return true taxonomy/local-refinement errors to #64/#76;
4. use identity-level #132 secondary routes only for genuine multi-entry exceptions.

---

## 9. #132 production ownership

#132 must not become a second taxonomy authority.

Default production scope:

> confirmed secondary Unified route additions for identities already browseable through accepted authority.

#132 does not directly:
- make unresolved General tags browseable;
- make non-browseable Special tags browseable;
- create primary classification;
- create local-subroute authority;
- rewrite #64;
- rewrite #76;
- rewrite #118;
- repair Japanese/search metadata;
- change canonical/PromptToken identity.

Owner rules:

- missing secondary route on already-browseable identity -> #132 candidate;
- missing/misleading local refinement -> #64 upstream review;
- no browse authority -> #64/#76 upstream review or SEARCH_ONLY;
- misleading current primary route -> owner-authority review;
- Japanese/search issue -> Japanese/search owner lane.

Architecture guardrail:

`docs/issue132/PRODUCTION_DELTA_ARCHITECTURE_GUARDRAILS.md`

---

## 10. Runtime architecture

Research can be exhaustive.

Runtime must remain simple.

The 31,003-row ledger, evidence, summaries, confidence, diagnostics, and web research do not ship.

Preferred production representation remains a small static delta through existing:

`CatalogEntry.UnifiedBrowseRouteIds -> UnifiedBrowseIndex`

Do not add:
- runtime LLM;
- embeddings;
- live web;
- runtime semantic parsing;
- co-occurrence recommendation;
- second browse index;
- second search engine;
- per-query #132 rule evaluation.

---

## 11. Performance gate

Before any production promotion, compare candidate against the exact pre-#132 production baseline.

Measure at minimum:
- catalog/runtime index construction;
- retained memory;
- Japanese search;
- English search;
- mixed search;
- Browse();
- FilterSearchHits();
- route/content/body/theme interactions;
- long-list scrolling/responsiveness;
- idle behavior after operations.

Reuse existing performance evidence/tests where applicable.

A material regression blocks promotion.

First response to a regression is to reduce/simplify the shipped delta, not add more caches/services.

---

## 12. Current verified technical state

The pre-handoff research pipeline is now mechanically executable from GitHub.

### Neutral input

Accepted authority:
`docs/issue118/production_candidate/sexual_intent_v2.csv`

Verified:
- identities: **31,003**
- neutral input columns: **3**
- authority SHA-256:
  `d2966dbc3c70617af2a985a94f81650785a29c1668b40b582d3c213ef2a68bc0`
- identity-order SHA-256:
  `f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b`
- neutral CSV SHA-256:
  `ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d`

The neutral input does not require protected local catalog/Japanese/alias data.

### Review vocabulary vs actual application code

CI verifies that the research vocabulary matches current tracked application authority:

- Unified top-level routes: **19**
- local refinements: **19**
- body-site facets: **6**
- theme facets: **3**

Sources pinned into the Pass-A contract include:
- `src/DanbooruTagTool.Core/UnifiedBrowse.cs`
- `src/DanbooruTagTool.Core/SpecialBrowseV2.cs`
- `docs/issue64/production_candidate/general_taxonomy.json`

### Frozen Pass-A contract

Builder:
`scripts/issue132/build_pass_a_contract_manifest.py`

The manifest pins:
- neutral input/order SHA;
- semantic-contract documents;
- neutral generator;
- contract builder;
- vocabulary checker;
- Pass-A validator;
- application vocabulary authorities;
- exact ledger schema and allowed vocabularies.

Checkpoint validation fails if a frozen contract file/vocabulary changes.

### Pass-A validator

`scripts/issue132/validate_luna_pass_a.py`

Validated behavior includes:
- exact-prefix continuous ledger;
- no skips/duplicates;
- valid route/local/body/theme IDs;
- local-parent route consistency;
- SEARCH_ORIENTED/UNRESOLVED constraints;
- RESEARCHED evidence requirement;
- contract-drift rejection.

### Pass B

Deterministic diff builder:
`scripts/issue132/build_pass_b_diff.py`

It mechanically derives:
- COVERED;
- MISSING_CORE_ROUTE;
- MISSING_SUPPORTING_ROUTE;
- CURRENT_ROUTE_NOT_REPRODUCED;
- MISSING_LOCAL_REFINEMENT;
- MISSING_BODY_FACET;
- MISSING_THEME_FACET;
- SEARCH_ORIENTED;
- SEMANTIC_UNRESOLVED;
- ROUTE_VOCABULARY_GAP.

CI validates this path against a complete synthetic **31,003-row** population.

Pass B makes **zero semantic/product decisions**.

### Current CI status

The Issue #132 full-discovery workflow is green with:
- full census audit;
- neutral input generation;
- code-vocabulary consistency check;
- frozen Pass-A contract generation;
- Pass-A validator smoke;
- full-population Pass-B diff smoke.

Dynamic run IDs belong in Issue #132 checkpoints rather than this frozen semantic contract.

---

## 13. Remaining pre-handoff gates

Before replacing the blocking Codex/Luna handoff stub:

1. run one final cross-document consistency audit;
2. confirm Pass-A field list is frozen at 22 columns;
3. confirm operational checkpoint files may change without changing frozen semantic contracts;
4. freeze the first-run file locations for:
   - neutral input;
   - frozen contract manifest;
   - Pass-A ledger;
   - progress summary;
5. write the final Luna execution instruction only after those points are fixed.

The final instruction must not reintroduce:
- bounded calibration samples;
- semantic shards;
- current-classification anchoring;
- per-row production approval;
- automatic new-route/facet creation.

Until then:

`CODEX_FULL_SEMANTIC_REVIEW_HANDOFF.md`

remains **DRAFT / DO NOT RUN**.

---

## 14. Protected boundaries

Research branch only.

No merge.
No production apply.

Do not mutate:
- main;
- production catalog/runtime;
- UserData;
- #64/#76/#118 authority;
- canonical/PromptToken;
- Japanese production overlay;
- Character/Copyright/Artist lanes;
- search ranking.

