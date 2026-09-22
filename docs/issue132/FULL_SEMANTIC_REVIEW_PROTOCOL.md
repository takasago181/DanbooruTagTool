# Issue #132 — Full semantic review protocol

Date: 2026-09-22
Status: **RESEARCH CONTRACT / ALL 31,003 IDENTITIES MUST BE SEEN**

## 1. Decision

Machine audit is no longer allowed to exclude identities from semantic review.

The complete Issue #118 runtime ordinary-tag identity universe — **31,003 identities** — must receive an explicit Codex semantic review row before #132 can be considered complete.

Machine analysis remains useful only for:
- ordering;
- grouping similar rows;
- showing current metadata;
- detecting conflicts;
- regression validation;
- completeness checks.

It must **not** supply final semantic verdicts.

The governing rule is:

> 全件を見る。機械は「何を見るか」を決めず、「どう並べれば効率よく見られるか」だけを助ける。

---

## 2. Why

#132 affects one of the core product functions: finding the right Danbooru tag.

A small benchmark or machine heuristic can miss:
- unexpected semantic overlaps;
- tags whose canonical wording hides the user's likely browse intent;
- odd historical classifications;
- missing secondary entrances;
- misleading but mechanically valid routes;
- search-only identities that should not be forced into browse;
- General/Special overlap behavior.

Therefore no identity may be accepted merely because a machine rule classified it as `OK`.

---

## 3. Review unit

One review unit = one canonical runtime identity from the #118 31,003-identity universe.

General and Special backing rows for the same identity are reviewed together.

Each identity is reviewed exactly once as an owner row, while all available backing metadata is shown beside it.

---

## 4. Efficient review strategy

### A. Group for consistency, never for bulk verdicts

Rows should be sorted into semantic review lanes so nearby rows are comparable.

Recommended exclusive lane priority:

1. `CURRENT_REVIEW_OR_CONFLICT`
2. `NO_AUTHORITY`
3. `MULTI_ROUTE`
4. one lane for each current Unified browse route
5. `FACET_ONLY`
6. `OTHER`

Within a lane:
- sort by current General primary path / Special kind;
- then by sexual intent;
- then by canonical identity.

This improves consistency because similar concepts appear together.

It does **not** authorize one verdict for the whole group.

Every row still needs its own decision.

### B. Two review depths

Every identity receives **CHECKED**.

#### CHECKED
Use when:
- meaning is unambiguous from canonical/Japanese/current accepted metadata;
- current discovery placement can be assessed directly;
- there is no conflicting evidence.

The reviewer still reads the row and records a verdict.

External research is not mandatory merely to prove an obvious concept.

#### RESEARCHED
Mandatory when any of these applies:
- canonical meaning is unclear or domain-specific;
- proper noun / meme / named event / franchise-specific meaning affects browse value;
- current routes conflict with the apparent meaning;
- a secondary route is being proposed;
- an existing route may be removed/replaced;
- accepted authorities disagree;
- sexual/contextual semantics are ambiguous;
- reviewer confidence would otherwise be below HIGH.

Evidence hierarchy:
1. tracked accepted repository authority;
2. Danbooru tag/wiki information when available;
3. authoritative external documentation/source pages when needed;
4. other reliable references as supporting evidence.

Search snippets alone are not final evidence.

### C. No quota pressure

There is no target percentage for PASS, FIX, secondary routes, or unresolved rows.

A valid review may conclude that almost nothing needs changing.

Do not invent changes to make the review appear productive.

---

## 5. Per-identity output schema

Every identity must output:

- `identity_key`
- `manual_seen` = YES
- `review_depth` = CHECKED / RESEARCHED
- `semantic_summary_ja` = short plain-Japanese meaning
- `current_discovery_fit`:
  - GOOD
  - PARTIAL
  - MISLEADING
  - NONE
  - SEARCH_ONLY_PREFERRED
- `decision`:
  - KEEP
  - ADD_SECONDARY
  - CHANGE_ROUTE
  - REMOVE_ROUTE
  - SEARCH_ONLY
  - UNRESOLVED
  - ESCALATE
- `suggested_route_ids` = zero or more existing Unified route IDs only
- `keep_current_routes` = YES / NO / N_A
- `browse_value` = HIGH / MEDIUM / LOW / SEARCH_ONLY
- `confidence` = HIGH / MEDIUM / LOW
- `evidence_urls`
- `evidence_note`
- `review_note`

No new route taxonomy may be invented inside a row.

If the existing route vocabulary is insufficient, use `ESCALATE`.

---

## 6. Decision meanings

### KEEP
Current discovery behavior is good enough.

### ADD_SECONDARY
Keep current route(s) and add one or more confirmed discovery entrances.

Use only when the secondary entrance is independently useful and semantically natural.

### CHANGE_ROUTE
Current route is materially misleading and should be replaced.

This is a high-bar decision and requires RESEARCHED evidence.

### REMOVE_ROUTE
A current secondary/discovery route is misleading and should be removed without replacement.

Requires RESEARCHED evidence.

### SEARCH_ONLY
The identity is useful/searchable but forcing it into browse would make the browse UI worse.

This is a valid final state, not a failure.

### UNRESOLVED
Meaning or best discovery placement cannot be established confidently.

Missing classification is preferable to a wrong classification.

### ESCALATE
The problem belongs outside #132, e.g. canonical identity/Japanese overlay/product-fit authority appears wrong.

Do not silently fix another authority from #132.

---

## 7. What Codex must examine for every row

At minimum:

1. canonical identity;
2. Japanese display/search metadata where available;
3. sexual intent;
4. General primary + secondary path;
5. Special kind/body/theme facets where available;
6. current Unified route(s);
7. General/Special overlap state;
8. neighboring rows in the same review lane;
9. whether direct search alone is sufficient;
10. whether another existing route is a natural discovery entrance.

This is the minimum meaning of `manual_seen=YES`.

---

## 8. What is forbidden

Do not:
- accept machine `OK` rows without opening/reviewing them;
- bulk-fill final verdicts from regex/string rules;
- generate final decisions from co-occurrence;
- infer secondary routes solely from token presence;
- require every tag to have a browse route;
- force proper nouns/memes into a category for coverage;
- invent a new hierarchy while processing rows;
- mutate #64/#76/#118 authority;
- change PromptToken/canonical/Japanese overlay/search ranking;
- merge or production-apply from the research run.

Scripts may prepare metadata and validate outputs, but final semantic columns must come from per-row review.

---

## 9. Sharding

Use deterministic review shards so work can resume safely.

Default shard size:
- **200 owner identities**

31,003 identities therefore produce:
- 155 full 200-row shards;
- 1 final 3-row shard;
- **156 shards total**.

A shard may be internally split during deep research, but its final output must still contain exactly its assigned owner identities.

Shard IDs:
`R001 ... R156`

No user interaction is required between shards.

Codex should continue autonomously until:
- all shards complete;
- an actual repository/evidence blocker occurs;
- execution quota/tool access prevents continuation.

Do not stop merely to request "continue".

---

## 10. Checkpoints

After each completed shard:
- write the shard result;
- validate exact identity membership;
- record PASS/flag counts;
- commit.

Every 10 shards:
- rebuild aggregate ledger;
- check duplicate/missing identities;
- report cumulative counts in Issue #132.

A checkpoint is progress accounting, not a semantic acceptance gate.

---

## 11. Final completeness gates

Before #132 semantic review can close:

- expected identities = **31,003**
- reviewed unique identities = **31,003**
- `manual_seen=YES` = **31,003**
- duplicate owner identity = **0**
- missing owner identity = **0**
- blank decision = **0**
- ADD_SECONDARY / CHANGE_ROUTE / REMOVE_ROUTE with LOW confidence = **0**
- CHANGE_ROUTE / REMOVE_ROUTE without RESEARCHED evidence = **0**
- invented route IDs = **0**

Then run:
1. consistency audit across lanes;
2. review of all non-KEEP decisions;
3. review of all LOW/MEDIUM confidence rows;
4. regression/full-census impact analysis;
5. only then design the minimal production change.

---

## 12. Relationship to Phase 6 machine audit

Phase 6 remains useful as:
- a baseline;
- a route-load census;
- a conflict detector;
- a way to build review lanes;
- a final regression comparator.

Its labels `OK / NO_AUTHORITY / REVIEW` are **not final review decisions**.

In particular:
- the 28,537 machine `OK` rows must still be seen;
- the 2,393 `NO_AUTHORITY` rows must still be seen;
- the 73 `REVIEW` rows must still be seen.

The earlier focus on only 98 adult/contextual NO_AUTHORITY rows and five strong pose rows is superseded as the completion scope.

Those groups remain useful priority groups only.

---

## 13. Product principle

The final product must feel simpler, not more classified.

The review should answer:

> If a user does not know this Danbooru tag, is the current search/browse path good enough, and if not, what is the smallest accurate change?

The expected outcome is a **small set of high-confidence changes derived from a complete semantic census**, not 31,003 new classifications.
