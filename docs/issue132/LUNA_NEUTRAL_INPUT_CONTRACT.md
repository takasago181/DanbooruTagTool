# Issue #132 — Luna neutral input contract v2

Date: 2026-09-23 JST
Status: **RESEARCH INPUT CONTRACT / GITHUB-REPRODUCIBLE**

## 1. Purpose

Pass A must be an independent image-generation discovery judgment.

The input must let Luna identify the tag concept without telling it how the current product classifies, searches, ranks, or prioritizes that identity.

The user goal remains:

> 作りたい画像の見た目・行為・部位・体位・衣装・構図から、タグ名を知らなくても目的タグへ辿れること。

---

## 2. Important design correction

Pass A does **not** need production Japanese overlay, aliases, usage count, or current browse metadata.

Those are product/search context and belong to Pass C.

Keeping them out of Pass A has four advantages:

1. current classification/search quality cannot anchor the independent semantic judgment;
2. the input is reproducible from tracked GitHub authority;
3. protected local Japanese/alias/runtime data does not need to be committed or uploaded;
4. Codex cloud can execute the full semantic pass from the repository alone.

---

## 3. Pass-A authority

Use only the accepted runtime identity authority:

`docs/issue118/production_candidate/sexual_intent_v2.csv`

The generator verifies its accepted SHA-256 and exact 31,003-row population.

Important:

The source file contains more fields than Pass A is allowed to see.

The generator must project only the neutral identity surfaces below.

---

## 4. Generated neutral file

Generator:

`scripts/issue132/build_luna_neutral_input.py`

Output:

`luna_neutral_review_input_v2.csv`

Columns:

- `review_seq`
- `identity_key`
- `source_surfaces`

### identity_key

The accepted runtime-canonical ordinary identity key.

For most identities this is effectively the canonical Danbooru tag spelling.

For reconciled Special/General cases it is the accepted runtime identity.

### source_surfaces

JSON array containing:
- identity_key;
- accepted source identity spelling(s) preserved by #118 reconciliation.

This is semantic lookup help only.

It does not expose whether a source came from General or Special.

---

## 5. Explicitly excluded from Pass A

Do not include:

- sexual_intent;
- #118 review_status/evidence/rule;
- General/Special membership;
- #64 path;
- #76 kind/body/theme;
- current Unified route IDs;
- current local subroutes;
- current body/theme facets;
- Japanese display/search overlay;
- aliases;
- usage/post count;
- search rank;
- machine bucket;
- machine review signals;
- Phase 1 pattern/fix proposals;
- prototype route additions;
- previous KEEP/ADD/REVIEW judgments;
- route result counts.

These fields become available only after Pass A is frozen.

---

## 6. Why Japanese/search metadata is delayed

The end product is Japanese-first, but Pass A is not evaluating current search quality.

Showing:
- display_ja;
- search_ja;
- aliases;
- usage

would mix two questions:

1. what is this visual concept and where would a user naturally browse for it?
2. can the current app already find it easily by search?

The first question must be answered independently.

The second is evaluated later in Pass C using the actual production catalog.

This separation is important because:

- good Japanese search can make a natural secondary route unnecessary;
- poor Japanese search can make a route more valuable;
- neither fact should change what the tag itself means.

---

## 7. Unclear identities

If identity_key/source_surfaces are not enough to understand the concept, Luna must use `RESEARCHED`.

Preferred semantic evidence:
1. Danbooru wiki/tag information when available;
2. reliable source/reference information for proper nouns or memes;
3. other authoritative semantic sources as needed.

Do not infer a confident route from token shape alone.

---

## 8. Deterministic neutral ordering

Do not sort by:
- current route;
- #64 genre;
- #76 kind;
- sexual intent;
- machine risk;
- Phase 1 family.

Generator order:

```
SHA256("issue132-pass-a-v2|" + identity_key)
```

ascending.

This order is:
- deterministic;
- resumable;
- independent of current taxonomy;
- resistant to long local runs of one known modifier/family.

The hash key itself is not shown to Luna.

---

## 9. Validation gates

Before Pass A starts:

- authority SHA matches accepted #118 SHA;
- source rows = 31,003;
- generated rows = 31,003;
- unique identity_key = 31,003;
- blank identity_key = 0;
- review_seq = 1..31,003 exactly;
- output contains only the three approved columns;
- deterministic identity-order SHA is recorded;
- output file SHA is recorded.

The generator writes a manifest with these facts.

---

## 10. GitHub Actions behavior

The Issue #132 research workflow generates the neutral input on every relevant research-branch push and includes it in the research artifact.

This makes the Luna Pass-A input reproducible without:
- production catalog.db;
- local ignored source data;
- protected Japanese overlay;
- local runtime access.

The artifact is research input only.

Do not merge the generated CSV into production runtime assets.

---

## 11. Pass-A output remains separate

Luna writes a separate independent ledger.

The neutral input is immutable source context.

Do not overwrite it with judgments.

Recommended logical output:

`pass_a_independent_discovery.csv`

containing the schema defined by:

- `FULL_SEMANTIC_REVIEW_PROTOCOL.md`
- `LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md`

---

## 12. Pass C local/product context

After Pass A freezes, product reconciliation may use the actual baked production catalog to join:

- accepted Japanese display;
- Japanese search terms;
- approved aliases;
- usage/post count;
- current #64/#76 metadata;
- current Unified routes;
- body/theme/local facets.

That join is a separate audit step.

It is not part of Luna's independent semantic input.

---

## 13. Protected-data rule

Do not copy the full ignored production Japanese/alias/runtime source into GitHub merely to help Pass A.

GitHub remains the authority for tracked code/docs/state, not a backup of local protected data.

If a later Pass C operation requires local protected catalog data, run that reconciliation in an authorized environment where the current production catalog already exists.

---

## 14. Runtime impact

The Pass-A neutral input and Luna output are research artifacts.

Neither ships in the application.
