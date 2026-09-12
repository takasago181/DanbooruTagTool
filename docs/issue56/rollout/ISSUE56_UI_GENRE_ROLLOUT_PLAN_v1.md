# Issue #56 UI Genre Rollout Plan v1

Status: **ACTIVE_AFTER_ISSUE59_PASS / PRE_STAGE10**

Audit anchor:
- Issue #59 final re-audit verdict: `PASS`
- comment: `5642183508`
- audited feature-branch HEAD: `65e9a352b62e9ac4ffbbeed101d20164b4149747`

Frozen taxonomy:
- `docs/issue56/rollout/issue56_ui_genre_taxonomy_v1.json`
- 14 top-level genres
- 38 visible subgenres
- no visible `その他` / `OTHER_*` fallback shelf

## Purpose

Expand the audited Pilot taxonomy to the frozen 2,788-entry Special Core Dictionary without mutating canonical Special identity, Alias relationships, #32/#43 evidence, production data, or Generation Profile authority.

The UI taxonomy remains a **human browsing index**. It is not semantic ground truth and is not generation-structure authority.

## Order

1. Freeze the audited taxonomy and Japanese labels.
2. Reclassify all rows from old `13_その他・文脈_part*`.
3. Apply safe canonical -> Alias UI-path inheritance where the canonical target is reviewed and no presentation conflict is known.
4. Cross-audit old categories 01–12 for misplaced rows.
5. Produce one complete 2,788-row UI mapping.
6. Audit final genre/subgenre distribution, unresolved pool, Alias consistency and catch-all pressure.
7. Run a fresh final #56 audit before completion/handoff to #42.

## Review authority

Final UI classification may be produced by manual/LLM-assisted development review, as allowed by Issue #56. Runtime LLM dependency is forbidden.

Regex/keyword/category heuristics may only:
- materialize a queue;
- prioritize review;
- suggest candidate paths;
- detect likely boundary cases.

They may **not** silently become final truth.

## Mapping source format

Reviewed mapping fragments use:

```text
special_id
primary_genre_id
primary_subgenre_id
secondary_paths
classification_status
classification_reason
ambiguity_note
```

Allowed statuses:
- `HUMAN_REVIEWED`
- `AUTO_INHERITED_ALIAS`
- `REVIEW_REQUIRED`
- `AMBIGUOUS`

`AUTO_INHERITED_ALIAS` is valid only when:
- canonical target resolves uniquely;
- canonical mapping is already reviewed/resolved;
- primary + secondary paths exactly match the canonical mapping;
- no known surface/canonical presentation conflict exists.

## Parent-level placement

A subgenre is optional. If no evidence-backed visible subgenre is useful, the row may live at the top-level genre with a blank `primary_subgenre_id`.

This is preferred over recreating a visible leftover shelf such as `その他部位`.

## Old-Other rollout

The eight `13_その他・文脈_part*` files are reviewed as separate source partitions for traceability, but classification decisions use the frozen taxonomy rather than the old file position.

Pilot-reviewed rows remain valid evidence unless the final cross-audit finds a concrete inconsistency.

## 01–12 cross-audit

Old source categories 01–12 are **not** automatically accepted as final UI placement. Cross-audit specifically checks recurring known boundaries:
- anatomy vs clothing-relative exposure;
- named activity vs site/contact topology;
- tools vs BDSM purpose;
- injury vs anatomy/BDSM pain;
- relation/role vs metadata vs situation;
- reproduction vs anatomy/tool rows.

## Final distribution Gate

Before #56 completion, report at minimum:
- count per top-level genre;
- count per visible subgenre;
- count of parent-level rows;
- secondary-path count distribution;
- `AUTO_INHERITED_ALIAS` count;
- `REVIEW_REQUIRED` count;
- `AMBIGUOUS` count;
- unresolved Special IDs;
- largest top-level genres/subgenres;
- `SITUATION_SCENE` size and representative sample.

A fresh independent audit must specifically challenge whether `SITUATION_SCENE / 状況・場面` or any other shelf has become a renamed catch-all after full 2,788 mapping.

## Protected boundary

Do not mutate:
- Special ID;
- canonical English identity;
- canonical/Alias relationship;
- Layer/source provenance;
- #32/#43 validation/freeze evidence;
- production Special data;
- Generation Profile generation-structure fields.

## Stage boundary

Passing the Pilot Gate does **not** activate Issue #42 or Stage10.

Required order remains:

`#56 complete -> #34 completed or explicitly separated -> #42 -> #5 -> only necessary Stage10 A/B`
