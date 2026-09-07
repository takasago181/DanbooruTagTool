# Stage 8A v2 generation meaning decision

## Decision

Add a thin decorator after Stage 7B receives its fixed Stage 6 candidate
lists. The decorator loads two small reviewed sidecars, attaches a Japanese
meaning category, a semantic-role generation hint, and separate evidence/
context notes, then returns the original `RecommendationCandidate` unchanged
inside its view model.

Semantic-role hints and evidence notes are independent. Classified candidates
retain their role-derived generation explanation in common and rare buckets.
SAME_STAT, rare, and low-support facts add context without replacing it.
Common membership alone does not imply `INDIRECT_SUPPORT` for a body part,
state/reaction, or appearance/clothing tag.

The Stage 7B controller remains the owner of debounce, caching, request IDs,
single-worker execution, stale-result rejection, and latest-request-wins
coalescing. Stage 8A decoration runs only on the already selected 8 common and
5 rare display rows on Tk's UI thread.

## UI

Each classified row shows:

1. `[意味カテゴリ] 日本語 / canonical`
2. `co_count / base_count枚・率`; rare rows also expose the existing Raw Lift
3. a short Japanese explanation of likely generation use
4. zero or more `補足:` evidence/context lines

Unclassified candidates keep the candidate and statistics rows without a
mass `未分類` badge. Recommendation buttons still add only Manual Auxiliary.

## Boundary

The seed covers 34 reviewed canonicals. It is not expanded to the 124,016-tag
dictionary. No semantic candidate generation for ambiguous or unmapped
Specials was added. Stage 8B, Stage 9, and Stage 10 remain unimplemented.
