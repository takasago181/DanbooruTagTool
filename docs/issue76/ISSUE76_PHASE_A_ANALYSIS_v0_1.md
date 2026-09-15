# Issue #76 Phase A analysis v0.1 — coarse browse + body/theme facets

Status: **DESIGN EVIDENCE / NOT PRODUCTION AUTHORITY**

This is the first full-data baseline for Issue #76. It does not replace Issue #56 production taxonomy and does not modify canonical Special identity.

## User constraint

The redesign must actively prefer fewer visible categories. A semantic distinction is **not** enough reason to create a browse node. A shelf survives only when it makes finding tags easier in actual WPF use.

Target interaction:

```text
◆ Special
  ▸ 種類から探す
  ▸ 部位から探す
  ▸ テーマから探す
```

No third hierarchy is proposed.

## Evidence input

Reused exact Issue #56 final-rollout artifact:

- source/mapped: 2,788 / 2,788
- unresolved review: 43
- v1: 14 top-level genres / 38 visible subgenres
- secondary paths: 0=1,545 / 1=1,196 / 2=47
- final audit: Issue #61 PASS

This v0.1 migration is computed from the accepted v1 primary/secondary browse paths. Because v1 secondary paths were intentionally sparse rather than exhaustive, facet counts below are **conservative route-derived baselines**, not final semantic coverage.

## First conclusion

The current 38 visible subgenres do not need to survive as permanent tree nodes.

v0.1 proposes:

- visible semantic homes: **9**
- permanent subgenres under those homes: **0**
- body-site facets: **6 candidate leaves**
- theme facets: **3 candidate leaves**
- navigation roots: **3**

So the visible classification surface changes from `14 top-level + 38 subgenres` to about `3 roots + 18 leaves`. Fine distinctions remain in tag names/search/metadata rather than permanent tree buttons by default.

## Candidate 種類から探す — mechanical v0.1 distribution

| 種類 | Rows |
|---|---:|
| 行為・接触 | 901 |
| 衣服・露出 | 503 |
| 身体・状態 | 319 |
| 道具・物 | 288 |
| 体液・排泄 | 273 |
| ポーズ・構図・場面 | 154 |
| 人物・関係 | 123 |
| 異形・変形 | 118 |
| 表現・メタ | 66 |
| REVIEW_REQUIRED | 43 |

These are **mechanical migration counts**, not final reviewed v2 counts.

The three mixed-axis v1 genres show why facets are needed:

- `拘束・BDSM・支配` 344 -> 行為・接触 183 / 道具・物 125 / 人物・関係 23 / ポーズ・構図・場面 13
- `生殖・妊娠・授乳` 18 -> 身体・状態 9 / 行為・接触 8 / 衣服・露出 1
- `損傷・R18G` 61 -> 身体・状態 48 / 行為・接触 8 / 体液・排泄 4 / 人物・関係 1

These are cross-cutting themes, not clean semantic-home shelves.

## Candidate 部位から探す — conservative route-derived counts

| 部位 | Rows |
|---|---:|
| 乳房・乳首 | 257 |
| 女性器 | 173 |
| 男性器 | 234 |
| 臀部・肛門（暫定） | 111 |
| 口・口内 | 174 |
| 尿道 | 20 |

Body-site facet multiplicity from existing routes:

- 0: 1,843
- 1: 921
- 2: 24
- 3+: 0

Cross-home evidence is strong. `口・口内` already spans 行為・接触 116 / 道具・物 43 / 体液・排泄 8 / ポーズ・構図・場面 3 / 異形・変形 2 / 表現・メタ 2.

`臀部・肛門` already spans 行為・接触 43 / 身体・状態 26 / 道具・物 14 / 衣服・露出 11 / ポーズ・構図・場面 8 / 体液・排泄 7 / 異形・変形 1 / 表現・メタ 1.

This directly explains the motivating problem: `anal beads` should not have to choose between “tool” and “anal”. Tool is its home; anal is its body-site entrance.

The current `BUTTOCK_ANUS` shelf mixes buttock and anus. v2 must inspect those rows before final facet naming; do not mechanically call every buttock row “anal”.

## Candidate テーマから探す — conservative route-derived counts

| テーマ | Rows |
|---|---:|
| 拘束・BDSM | 366 |
| 損傷・R18G | 66 |
| 生殖・妊娠・授乳 | 25 |

Theme multiplicity:

- 0: 2,332
- 1: 455
- 2: 1
- 3+: 0

`拘束・BDSM` already spans the projected homes: 行為・接触 185 / 道具・物 128 / 人物・関係 29 / ポーズ・構図・場面 15 / 身体・状態 6 / 異形・変形 2 / 表現・メタ 1. Keeping BDSM as a forced semantic home therefore makes browsing less natural.

## Combined facet pressure

Using only existing v1 browse evidence:

- 0 body/theme facets: 1,502
- 1 facet: 1,146
- 2 facets: 140
- 3+: 0

This is sparse enough for a lightweight facet model; it does not imply exhaustive ontology tagging.

## Current 38 visible subgenres — v0.1 decision

**Default decision: remove all 38 from the permanent left-tree hierarchy.**

They become one of three things:

1. body-site intent -> `部位から探す` facet;
2. theme intent -> `テーマから探す` facet;
3. fine semantic distinction -> flatten into the broad kind shelf and retain only as search/metadata evidence where useful.

A subkind may be reintroduced only if later task testing shows that the broad shelf is practically unusable **and** the extra visible choice makes discovery easier.

Exact 38-row migration is tracked in `docs/issue76/issue76_v1_to_v2_migration_v0_1.csv`.

## Sanity examples from current source + accepted v1 mapping

- `anal beads` ID 266 -> 道具・物 + 肛門系 body-site facet
- `anal tail` ID 267 -> 道具・物 + 肛門系 body-site facet
- `butt plug` ID 268 -> 道具・物 + 肛門系 body-site facet
- `vibrator in anus` ID 264 -> 道具・物 + 肛門系 body-site facet
- `urethral beads` ID 209 -> 道具・物 + 尿道
- `catheter` ID 207 -> 道具・物 + 尿道
- `cum in urethra` ID 208 -> 体液・排泄 + 尿道
- `urethral sounding` ID 219 -> 行為・接触 + 尿道
- `dildo gag` ID 270 -> 道具・物 + 口・口内 + 拘束・BDSM candidate

The accepted v1 already needed secondary paths to compensate for the single mixed tree; v2 makes that cross-cutting discovery explicit instead of hiding it in secondary-path implementation detail.

## Next before freeze

1. Re-read real rows for themed/mixed families instead of trusting the mechanical projection.
2. Resolve `臀部・肛門` naming/splitting from actual rows; do not add a small extra shelf unless it improves browsing.
3. Check whether every oral-act row belongs in `口・口内` or only body-site/topology-relevant rows.
4. Stress-test the 901-row `行為・接触` shelf. Do **not** automatically restore 10 action subgenres; first test search-within-shelf / sort / lightweight non-tree filtering.
5. Produce 30–50 named before/after examples across boundaries.
6. Keep the 43 unresolved rows fail-closed until a real browse home is justified.

## v0.1 decision

`PHASE_A_V0_1_COARSE_STRUCTURE_SUPPORTED`

The data supports moving away from one 14/38 mixed-axis tree toward a small semantic-home set plus independent body/theme entrances. This does **not** authorize production taxonomy replacement or WPF changes.
