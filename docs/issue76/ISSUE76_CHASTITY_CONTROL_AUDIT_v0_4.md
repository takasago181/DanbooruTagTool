# Issue #76 Phase B — CHASTITY_CONTROL audit v0.4

## Result

The 21 rows previously flagged as `REVIEW_MIXED_FAMILY` under v1 `CHASTITY_CONTROL` were reviewed individually against the Japanese display text, English tag identity, Alias target where applicable, and the Issue #76 principle that **kind/home, body-site, and theme are independent browse axes**.

All 21 are resolved. No new unresolved row is introduced.

### Semantic-home result

- `道具・物`: 17
- `行為・接触`: 3
  - ID949 `revealing chastity cage`
  - ID1194 `touching another's chastity cage`
  - ID1225 `holding unworn chastity cage`
- `体液・排泄`: 1
  - ID856 `chastity cage emission`

This confirms that old `CHASTITY_CONTROL` was a mixed browse family rather than a useful permanent visible subcategory.

### Body-site result

Penis/chastity-cage concepts receive `男性器` even when the cage is unworn or being held. This is intentional: Issue #76 body-site facets are discovery routes for concepts related to a body site, not only direct anatomical-state tags.

- `男性器`: 17 cage-related rows
- `女性器`: ID1818 `chastity belt`
- `乳房・乳首`: ID1819 `chastity bra`
- no site facet: ID1845 `chastity device`, ID2737 `chastity key`

Generic device/accessory concepts are not force-assigned to a body site.

### Theme result

All 21 retain `拘束・BDSM` as a cross-cutting theme.

## Alias handling

ID1558 `chastity cage removed` is an Alias of ID1089 `unworn chastity cage` and inherits the same v2 browse classification:
- kind: `道具・物`
- body site: `男性器`
- theme: `拘束・BDSM`

## Candidate distribution after this audit

Kinds:
- 行為・接触: 904
- 衣服・露出: 503
- 身体・状態: 319
- 道具・物: 284
- 体液・排泄: 274
- ポーズ・構図・場面: 154
- 人物・関係: 123
- 異形・変形: 118
- 表現・メタ: 66
- pre-existing v1 REVIEW_REQUIRED: 43

Body-site facets:
- 乳房・乳首: 257
- 男性器: 250
- 口・口内: 174
- 女性器: 173
- 尻・肛門: 111
- 尿道: 20

Themes:
- 拘束・BDSM: 366
- 損傷・R18G: 66
- 生殖・妊娠・授乳: 25

## Review queue

Previous v0.3 queue:
- v1 unresolved: 43
- CHASTITY_CONTROL mixed family: 21
- total: 64

After v0.4:
- v1 unresolved: 43
- new v2 ambiguity: 0
- total: **43**

Therefore the v2 redesign itself currently creates **no remaining new ambiguity queue**. The only unresolved rows are inherited from the accepted v1 evidence and should be reviewed as a separate next step.

## UX decision

Do **not** add a visible `貞操・管理` subcategory.

A Japanese user can reach these rows more naturally through:
- `種類 -> 道具・物` for cage/belt/bra/device/key;
- `種類 -> 行為・接触` for revealing/touching/holding;
- `種類 -> 体液・排泄` for emission;
- `部位 -> 男性器 / 女性器 / 乳房・乳首`;
- `テーマ -> 拘束・BDSM`.

This follows the user constraint that visible categories should exist only when they make browsing easier, not merely because a semantically coherent family can be named.

## Protected boundary

No canonical Special ID, tag, Alias relationship, Japanese dictionary identity, General taxonomy, Issue #70 data, or production WPF taxonomy was mutated.
