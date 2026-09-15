# Issue #76 — former v1 unresolved 43-row audit v0.5

Status: **ANALYSIS ONLY / NO PRODUCTION TAXONOMY OR WPF MUTATION**

## Result

All 43 rows that were still `REVIEW_V1_UNRESOLVED` in v0.4 were reviewed against:
- their existing v1 ambiguity note;
- the live `data/special2788/product_fit_verdicts.csv` sidecar from Issue #63;
- current Special source wording;
- conservative external tag-definition evidence only where it clarified the underlying concept.

The 43 rows split cleanly into:

- **15 `BROWSE_RESOLVED`** — product-fit `KEEP`, given a v2 browse route.
- **21 `REFERENCE_ONLY_NO_DIRECT_BROWSE`** — product-fit `KEEP_REFERENCE_ONLY`; do not invent an independent visible browse home merely to clear the queue.
- **6 `DEFER_PRODUCT_FIT_REVIEW`** — product-fit `REVIEW`; Issue #76 must not silently promote them.
- **1 `OUT_OF_SCOPE_NO_BROWSE`** — product-fit `OUT_OF_SCOPE_PRODUCT`.

Therefore:

> **Issue #76 taxonomy-specific review queue: 0 rows.**

There are still **6 explicit product-fit dependencies**, but they are not taxonomy ambiguity and remain governed by Issue #63 semantics.

## Important design consequence

This audit confirms that `kind_id` must remain optional.

Example:
- ID594 `penis awe`
  - no clean semantic kind shelf;
  - valid body-site browse route: `男性器`;
  - do **not** force it into `ポーズ・構図・場面` or `表現・メタ`.

The model is therefore:

```text
kind_id: optional
body_sites[]: 0..n
themes[]: 0..n
product_fit sidecar remains a separate eligibility gate
```

A row can be resolved for Issue #76 without receiving a visible kind shelf when a valid facet or product-fit policy already supplies the correct behavior.

## 15 newly browse-resolved KEEP rows

| ID | tag | kind | body-site | theme | key reason |
|---:|---|---|---|---|---|
| 594 | penis awe | — | 男性器 | — | reaction concept; use valid site facet rather than force scene/meta |
| 832 | foot pussy | ポーズ・構図・場面 | — | — | visual feet arrangement/presentation |
| 904 | tail anus | 異形・変形 | 尻・肛門 | — | nonhuman anatomy placement + anal site |
| 1128 | sex hair | 身体・状態 | — | — | post-sex hair/appearance state |
| 1227 | cum on fourth wall | 体液・排泄 | — | — | primary browse intent is cum placement/effect |
| 1741 | gagging | 行為・接触 | 口・口内 | — | mouth-centered action/reaction; no automatic BDSM |
| 1757 | doggy | ポーズ・構図・場面 | — | — | sexual-position identity in this source |
| 1758 | gaping | 身体・状態 | 女性器 / 尻・肛門 | — | generic bodily state applicable to both sites |
| 1759 | prolapse | 身体・状態 | — | — | generic anatomical state; site/R18G remain context-dependent |
| 1789 | castration | 行為・接触 | 男性器 | — | procedure/action; no forced R18G theme |
| 1790 | orchiectomy | 行為・接触 | 男性器 | — | procedure/action on testes |
| 1793 | hysterectomy | 行為・接触 | 女性器 | — | reproductive-organ procedure; no forced R18G theme |
| 1794 | oophorectomy | 行為・接触 | 女性器 | — | reproductive-organ procedure; no forced R18G theme |
| 1795 | salpingectomy | 行為・接触 | 女性器 | — | reproductive-organ procedure; no forced R18G theme |
| 1863 | all the way through | 行為・接触 | — | — | extreme insertion/penetration action; exact site can vary |

## Product-fit policy carried into browse behavior

Issue #63 remains authoritative:
- `KEEP`: normal product-facing Special candidate.
- `KEEP_REFERENCE_ONLY`: retain exact/alias/reference/search access but do not surface as an independent default browse candidate when the canonical/product-facing identity is available.
- `OUT_OF_SCOPE_PRODUCT`: preserve source/history, exclude from normal browse.
- `REVIEW`: inspectable, but never silently promote to ordinary resolved recommendation/browse.

Issue #76 does not reinterpret those verdicts merely to make its own review counter reach zero.

## v0.5 candidate distribution

Kinds:
- 行為・接触: 911
- 衣服・露出: 503
- 身体・状態: 322
- 道具・物: 284
- 体液・排泄: 275
- ポーズ・構図・場面: 156
- 人物・関係: 123
- 異形・変形: 119
- 表現・メタ: 66

Body-site facets:
- 乳房・乳首: 257
- 男性器: 253
- 女性器: 177
- 口・口内: 175
- 尻・肛門: 113
- 尿道: 20

Themes:
- 拘束・BDSM: 366
- 損傷・R18G: 66
- 生殖・妊娠・授乳: 25

Candidate status:
- AUTO_CANDIDATE: 2745
- HUMAN_RESOLVED: 15
- REFERENCE_ONLY_NO_DIRECT_BROWSE: 21
- DEFER_PRODUCT_FIT_REVIEW: 6
- OUT_OF_SCOPE_NO_BROWSE: 1

## Remaining dependency

The six product-fit `REVIEW` rows are:
- ID1005 `body onahole`
- ID1027 `poking penis`
- ID1028 `penis face`
- ID1308 `gang rape`
- ID1577 `erect nipplees`
- ID2770 `serving tray (bdsm)`

They remain intentionally outside ordinary visible browse classification until the product-fit gate is resolved. This is not an Issue #76 taxonomy backlog.

## Boundaries preserved

- no canonical Special ID/tag mutation
- no Alias/canonical relation mutation
- no product-fit verdict mutation
- no General/#64 change
- no #70 Character/Copyright/Artist change
- no WPF implementation yet
- no production taxonomy replacement yet
