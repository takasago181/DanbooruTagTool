# Issue #117 practical WPF smoke checklist

Use only **after**:
1. read-only baseline captured;
2. Release build passed;
3. staged catalog build passed;
4. `issue117_validate_staged_catalog.ps1` passed;
5. staged runtime was applied without touching `UserData`;
6. `issue117_verify_runtime_apply.ps1` passed before launch.

Record PASS / FAIL / BLOCKED for every row. Do not close #117 on any FAIL/BLOCKED item.

## A. Launch / navigation

| Check | Method | Expected |
| --- | --- | --- |
| Startup | Launch from root `DanbooruTagTool.lnk` | Main WPF window opens without catalog/build error |
| Old roots gone | Inspect left navigation | No visible `General` or `◆ Special` root |
| Presentation headings | Inspect left navigation | `何を描く`, `動き・状態`, `画面・表現` are visible |
| Ordinary routes | Count/use the ordinary entries under the three headings | Exactly 19 ordinary discovery routes are available |
| Dedicated scopes | Select `キャラクター`, `作品`, `作者` | Each works as an independent scope |
| Neutral state | Use `全解除`, empty query | Guidance shown; full 31,752 ordinary identity population is not eagerly rendered |
| Neutral highlight | Return to neutral Tags | No stale ordinary-route selection highlight remains |

## B. Search / query preservation

| Check | Method | Expected |
| --- | --- | --- |
| English search | Search a known canonical such as `blue_hair` | Matching ordinary tag is found |
| Japanese search | Pick one visible Japanese label from a known card, clear query, search that Japanese label | Same intended identity can be found without switching language mode |
| Mixed workflow | Search, then switch ordinary route | Query text stays in the search box |
| Dedicated scope query | Enter a query, then switch Character -> Artist -> Tags | Query text is preserved across scope changes |
| Clear query | Use `クリア` | Query clears; browse state is not implicitly reset |
| Clear browse | Enter query + one or more browse constraints, use `全解除` | Browse constraints reset; query remains |

Do not use result ordering from a narrowed filter to claim ranking changes. #117 filtering must only remove candidates; existing SearchEngine order remains authoritative.

## C. #118 content intent

Frozen mapping:
- `すべて` -> SEXUAL + NON_SEXUAL + CONTEXTUAL + UNCLASSIFIED
- `一般向け` -> NON_SEXUAL + CONTEXTUAL
- `性的` -> SEXUAL + CONTEXTUAL
- UNCLASSIFIED -> All only

Representative real/product identities used by automated acceptance coverage:
- `blue_hair` -> NON_SEXUAL example
- `breastfeeding` -> CONTEXTUAL example
- `anal_sex` -> SEXUAL example

Manual checks:

| Check | Method | Expected |
| --- | --- | --- |
| General-purpose narrow | Search/browse `blue_hair`; select `一般向け` | Remains eligible |
| Sexual narrow excludes clear non-sexual | Search `blue_hair`; select `性的` | Does not survive sexual intent narrowing |
| Contextual in general-purpose | Search `breastfeeding`; select `一般向け` | Eligible |
| Contextual in sexual | Keep/search `breastfeeding`; select `性的` | Eligible |
| Clear sexual | Search `anal_sex`; select `性的` | Eligible |
| Sexual excluded from general-purpose | Search `anal_sex`; select `一般向け` | Does not survive general-purpose intent narrowing |

Exact frozen UNCLASSIFIED identities:
- `cock-tail`
- `insertion_threshold_(meme)`
- `knee_boobs`
- `lilistia`
- `powerful_ass`

For each UNCLASSIFIED identity:
1. search under `すべて` -> searchable/visible where existing search eligibility permits;
2. select `一般向け` -> must not survive the intent filter;
3. select `性的` -> must not survive the intent filter.

Do not infer anything about the semantic meaning of these five during smoke; their frozen status is intentionally UNCLASSIFIED.

## D. Deep discovery / browseability boundary

| Check | Method | Expected |
| --- | --- | --- |
| Deep-only | Select `◆ 深掘りのみ` on an ordinary route with Special backing | Only identities with accepted direct-browse Special evidence survive |
| Reference-only protection | Use a known #76 reference-only/non-direct identity from accepted data/test evidence | It remains searchable where allowed but does not re-enter route/content-only browse |
| #64 unresolved protection | Use a known General UNRESOLVED/searchable identity if convenient | Searchable where allowed; not made browseable merely by unified/content filtering |
| Selected zero-count facet | Create a selected facet combination yielding zero results | Selected facet stays visible and removable |

If a convenient real reference-only/UNRESOLVED identity is not known during manual smoke, mark the manual row BLOCKED rather than inventing one. Automated #117 tests already cover the semantic boundary; local smoke must not guess identities.

## E. Canonical dedupe / result presentation

| Check | Method | Expected |
| --- | --- | --- |
| General/Special overlap | Search a known canonical that has both General and Special backing | One result card only |
| Deep marker | Inspect an overlap/direct Special-backed identity | `◆` / deep-discovery presentation is identity-level, not dependent on which backing row became representative |
| Two-column layout | Widen/maximize to normal WQHD usage | Two-column result composition remains intact |
| Odd tail | Use an odd result count if convenient | Last single card remains visible and correctly sized |
| No stale second-card collapse | Scroll/select through two-column results | Second card in a row does not disappear/collapse unexpectedly |

## F. Prompt regression smoke

Use a safe ordinary tag for this functional regression; the exact semantic content is irrelevant.

| Check | Method | Expected |
| --- | --- | --- |
| Add | Add a dictionary result to Prompt | Canonical English appears in Prompt workspace |
| Duplicate safety | Try adding the same canonical again using normal UI | Existing duplicate-safety behavior is preserved |
| Remove | Remove that Prompt item | It is removed cleanly |
| Copy | Copy canonical-English Prompt | Clipboard represents the visible Prompt state |
| Workspace tabs | Switch `辞書・検索` / `Prompt編集` | Switching works; selected blue edge is visually continuous on the right side |

## G. Final integrity gate

Close the app normally, then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\issue117_verify_runtime_apply.ps1 `
  -BaselineJson $baselineJson `
  -StagedCatalog (Join-Path $catalogStage "catalog.db")
```

Required:
- current runtime catalog SHA-256 == staged catalog SHA-256;
- real `artifacts/current/UserData/user.db` SHA-256 == pre-mutation baseline SHA-256;
- shortcut still targets current runtime executable.

If `user.db` hash differs, #117 is **not** ready to close. Report the exact before/after hashes and stop before trying to repair or reset it.

## Result template

```text
Main commit:
Release build:
Catalog build:
Staged catalog validator:
Runtime apply integrity (pre-smoke):
A Launch/navigation:
B Search/query:
C Content intent:
D Browseability/deep:
E Dedupe/layout:
F Prompt regression:
Runtime apply integrity (post-smoke):
user.db SHA before:
user.db SHA after:
Overall:
#117 close recommendation: YES / NO
Notes / blockers:
```
