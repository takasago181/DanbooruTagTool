# Issue #179 — Character Quality Audit Design

Status: RESEARCH / NO PRODUCTION APPLY

Baseline main: `bea08712eb691ca867e218d211023d7206b6b7dc`

This audit deliberately separates Character identity quality from the Character↔Copyright relation problem tracked by #180.

## 1. Current runtime facts

Source of truth for this audit:

- `docs/issue70/data/runtime/issue70_catalog_overlay_2d_final.csv`
- SHA-256: `bf366734b41b2be9e6cb52de919ef55b7312445e1715f96a357db37abda8dad5`
- Character rows: **35,278**
- `ACCEPTED_AI`: **23,340**
- `REVIEW_REQUIRED`: **11,938**
- Character rows with old `related_copyright`: **34,986** (not product truth; #180 only)

Post-count distribution:

| percentile | post_count |
|---:|---:|
| min / p1 | 50 |
| p10 | 58 |
| p25 | 75 |
| p50 | 132 |
| p75 | 325 |
| p90 | 951 |
| p99 | 6,777.53 |
| max | 145,166 |

Other shape:

- canonical with final parenthesized qualifier: **18,929**
- non-empty aliases: **6,504**
- non-empty `search_ja`: **13,420**
- ASCII-only `display_ja`: **9,358**
  - ACCEPTED_AI: 211
  - REVIEW_REQUIRED: 9,147
- `display_ja` still containing underscore: 11

ASCII-only display is only a triage signal. It is not automatically wrong: official names such as KAITO, GUMI, IRyS, UMP9, 9S, IA, U-511, AK-12, etc. are legitimately Latin/alphanumeric.

## 2. Current search behavior

Runtime code: `src/DanbooruTagTool.Core/RuntimeCatalogIndex.cs`.

Search normalizes case, Unicode width, underscores→spaces and whitespace.

Match rank is:

0. exact English/canonical/English search term
1. exact Japanese display/search term
2. English whole-word containment
3. multi-part English/Japanese match, or Japanese substring
4. English word prefix
5. English substring (query length >= 3)
6. edit distance 1 (query length >= 4)

If any rank 0–3 hit exists, weaker rank 4–6 hits are suppressed.

Final ordering is:

1. match Rank
2. prefix distance
3. **post_count descending**
4. English ordinal

Therefore `post_count` is not the primary relevance model, but it does decide ordering among otherwise equivalent matches. Audit ranking separately from bad search terms: a bad alias/search term can create a strong Rank 0/1 hit that post_count then amplifies.

## 3. Audit dimensions

Every audited Character row receives independent statuses. Do not collapse them into one “good/bad Character” judgment.

### A. IDENTITY

Checks:
- canonical really denotes a Character identity
- canonical has not been confused with a group, meme, generic role, artist, or copyright
- verified aliases point to the same identity
- variant/form Character identities remain distinct when Danbooru intends them to be distinct

Statuses:
- PASS
- REVIEW
- FAIL_IDENTITY
- OUT_OF_PRODUCT_SCOPE

### B. DISPLAY_JA

Checks:
- display is a character name, not a description/event/search phrase
- Japanese/official Latin form is sensible
- qualifier is readable and ordered correctly
- no half-translated qualifier such as `（arknights）` mixed into otherwise Japanese display unless that is the intended official label
- no unnecessary Copyright suffix is added merely because old co-occurrence suggested it
- canonical qualifier semantics may be retained when needed for disambiguation

Statuses:
- PASS
- REVIEW
- FAIL_NAME
- FAIL_TRANSLATION
- FAIL_QUALIFIER
- FAIL_OVERDISAMBIGUATION

### C. SEARCH

Allowed search terms:
- official localized names
- readings/transliterations
- verified aliases
- stable nicknames that identify the Character

Review/fail candidates:
- event names
- fanart hashtags
- ship/pairing names
- work descriptors
- generic phrases that can create unrelated exact hits
- duplicate formatting-only variants that add no retrieval value

Statuses:
- PASS
- REVIEW
- FAIL_MISSING_ALIAS
- FAIL_NON_IDENTITY_TERM
- FAIL_COLLISION
- FAIL_DUPLICATE_NOISE

### D. RANKING / UX

Test the actual query results, not post_count in isolation.

Checks:
- exact canonical or verified alias produces the expected Character
- exact Japanese name produces the expected Character
- same-name collisions are understandable
- post_count tie-breaking does not hide the intended qualified Character
- noisy `search_ja` does not create false strong matches

Statuses:
- PASS
- REVIEW
- FAIL_RELEVANCE
- FAIL_AMBIGUITY

### E. RELATION

Only record:
- RELATION_OK_KNOWN
- RELATION_BAD_OLD_COOCCURRENCE
- RELATION_UNKNOWN

Do not fix relation in #179. Hand it to #180.

## 4. Existing semantic-fix history is an audit input, not authority

`FINAL_SEMANTIC_FIXES.csv` contains **8,612 Character fixes**:

- FIX_DISPLAY: 8,290
- FIX_SEARCH: 143
- FIX_BOTH: 179

Large reason families include:

- unverified Japanese candidate → canonical fallback
- variant Japanese candidate → canonical fallback
- adding Copyright context to duplicate/ambiguous Character names
- restoring base identity in variant display
- search-term deduplication

This history is useful for stratification, but some display decisions added Copyright context. Since #177 proved the old relation source unreliable, #179 must re-check Copyright-derived display context independently.

Important distinction:

- If the **canonical itself** contains a series qualifier and that qualifier is semantically part of the Danbooru Character identity, displaying a localized qualifier may be correct.
- If an **unqualified canonical** was given a work suffix solely for convenience/disambiguation, the suffix needs separate justification. Old `related_copyright` is not sufficient.

Example from current accepted data:

- `hatsune_miku` canonical is unqualified.
- semantic fix changed `初音ミク` → `初音ミク（ボーカロイド）`.
- this is a #179 DISPLAY_JA audit case, even though the Character identity itself is unquestionably stable.

## 5. Concrete issues already visible in the pilot

These are audit leads, not blanket rules.

### Search-term contamination

Current accepted examples include:

- `hatsune_miku`: `ミクの日`, `初音ミクイラスト`
- `gotoh_hitori`: `ぼ喜多`
- `shirakami_fubuki`: `絵フブキ`

These look like event/fanart/pairing terms rather than identity aliases and therefore must be reviewed under SEARCH, not silently retained because the Character itself is correct.

### Mixed / awkward qualifier display

High-post-count REVIEW_REQUIRED examples include:

- `cyrene_(demiurge)_(honkai:_star_rail)` → `キュレネ（崩壊）（demiurge）`
- `cyrene_(philia093)_(honkai:_star_rail)` → `キュレネ（崩壊）（philia093）`
- `aria_(human)_(zenless_zone_zero)` → `アリア（ゼンゼロ）（human）`
- `perlica_(arknights)` → `ペリカ（arknights）`
- `spider-man_(original_suit)` → `スパイダーマン（original suit）`

These should be prioritized because they are visible and have substantial post_count.

## 6. Sampling plan

Do not audit 35,278 rows in one pass.

### Pilot A — high-impact 60

- top 20 `REVIEW_REQUIRED` by post_count
- top 20 Characters from the five #180 pilot families
- 20 high-post-count `ACCEPTED_AI` rows with alias/search/display complexity

### Pilot B — structure 60

- 20 nested/multiple qualifier canonicals
- 10 alias-heavy rows
- 10 `search_ja`-heavy rows
- 10 unqualified canonicals with added display context
- 10 rows touched by display/search semantic fixes

### Pilot C — population 60

Deterministic post_count strata:
- 12 each from p0–10, p10–25, p25–50, p50–90, p90–100

Within each stratum, select deterministically by canonical ordering after a fixed seed/hash rule so later audits reproduce the sample.

Initial audit target: **180 rows**.

Expand only after the failure taxonomy stabilizes.

## 7. Acceptance gates before any Character rewrite

- identity/display/search/ranking failure rates are reported separately
- every proposed change states which dimension it fixes
- relation-only errors do not cause Character identity changes
- no bulk Japanese rewrite from machine translation alone
- no work suffix derived solely from old co-occurrence
- `ACCEPTED_AI` is not treated as “proven correct”
- `REVIEW_REQUIRED` is not treated as “proven wrong”
- original Issue #70 accepted assets remain immutable
- no production apply during audit

## 8. Likely implementation direction after audit

Prefer a **new correction overlay** over rewriting Issue #70 accepted rows.

A future correction row should identify:

- canonical
- field being corrected: display/search/identity metadata
- old value
- new value
- reason code
- evidence/provenance
- reviewer status

Ranking changes, if needed, should be implemented/tested independently from translation corrections.

## 9. Immediate pilot regression cases

See `docs/issue179/PILOT_CASES.csv`.

The file intentionally contains separate columns for identity, display, search, ranking and relation so a relation failure cannot contaminate the Character verdict.
