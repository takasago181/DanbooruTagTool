# Stage 7B Recommendation UI report

## Scope

Implemented Stage 7B only.  Stage 0–7A behavior remains the fixed base, and
Stage 8–10 work was not started.

## Changes

- Added `stage7b_recommendations.py` as a small asynchronous adapter around the
  existing Stage 6 `RecommendationEngine`.
- Added order-independent cache keys, a 350 ms UI debounce, request IDs,
  stale-result rejection, latest-request-wins queued-work coalescing, and
  error isolation.
- Connected the existing read-only Stage 5 runtime index and canonical overlay
  to the Stage 7A right pane.
- Added 「よく使われる」 (Conditional Rate) and 「珍しい関連」 (Raw Lift) tabs,
  base-count text, low-support evidence text, and Manual Auxiliary
  「＋追加」/「追加済み」 controls.
- Candidate rows start with `日本語 / canonical` and do not expose the internal
  fallback role `other`. Future role display requires existing reviewed data
  and Japanese role labels.
- Kept ambiguous/unmapped Special identities out of partial recommendation
  queries while retaining their original Prompt identity.
- Returned worker results through a thread-safe queue polled by Tk's main
  thread; background workers never call Tk.
- Added a responsive, vertically scrollable candidate viewport. It contracts
  at 900x540 and expands at normal/maximized height without overlapping the
  fixed Prompt row.

## Preserved behavior

Conditional Rate, Raw Lift, true-AND, candidate filtering, Special IDs,
Special original terms, Alias identity, Japanese Overlay priority, Prompt
ordering, Stage 4 search behavior, and protected Special2788/source hashes are
unchanged.  No auto-add, auto-weight, Prompt rewrite, LLM, or runtime network
path was added.

## Validation results

- Final candidate-role display targeted pytest on Windows Python 3.12.10:
  `28 passed in 3.46s`.
- Final full Windows Python 3.12.10 regression: `141 passed in 25.03s`.
- The requested `py -3` initially selected Python 3.14.7, where NumPy was not
  installed. Global launcher settings were not changed; validation used the
  existing dependency-complete `py -3.12` environment.
- Production metric parity, core
  `clothed_female_nude_male AND genderswap`: base_count `101`, candidates
  `1087`; Conditional Rate order matched Stage 6, Raw Lift order matched
  Stage 6, and every displayed raw field matched exactly.
- The common result included `nude`, `1girl`, and `censored`. The raw candidate
  set retained `sex`; 681 low-support candidates remained available and a
  low-support result appeared in the Raw Lift view. No content filter or Stage
  7B score was applied.
- Cold Stage 6 calculation: `63.8314 ms`; cached Stage 7B result: `0.0133 ms`.
- Deterministic A/B/C/D test confirmed calculations `A, D`; queued B/C never
  started, and only D was delivered.
- Production Tk smoke passed with Special IDs `2266` and `1288`, both tabs,
  base_count, candidates, visible low-support wording, Manual Auxiliary add,
  `追加済み`, Prompt preview, visible copy action, and matching clipboard.
- The refreshed production screenshot confirms candidate rows begin with
  `日本語 / canonical`; the internal fallback role `other` is not displayed.
- 900x540, 1120x760, and maximized geometries all kept Recommendation,
  Prompt preview, and copy viewable and within the window without overlap.
- Stage 5 manifest hashes and canonical-overlay payload validation passed.
- Special2788 SHA-256 remained
  `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`.

## Outstanding

The formal standalone `DanbooruTagTool_STAGE7B_RECOMMENDATION_UI_SPEC.txt`
was not present in Downloads; the received All-in-One document supplied the
formal requirements used here. No unresolved implementation or validation
issue remains within Stage 7B scope.
