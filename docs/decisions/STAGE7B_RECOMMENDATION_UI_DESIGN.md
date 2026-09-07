# Stage 7B Recommendation UI design

Stage 7B connects the existing Stage 6 `RecommendationEngine` to the
Stage 7A Special-first window.  `conditional_rate` is shown under
「よく使われる」 and the unchanged `raw_lift` order is shown under
「珍しい関連」.  No new score, blacklist, support threshold, or ranking
adjustment is introduced.

The query is derived from the selected Special IDs, never from the search
entry.  A Special without one unambiguous `chosen_canonical` produces the
explicit unavailable message; partial AND is never presented as a complete
Core recommendation.  Candidates remain General canonical tags and are
added only to Stage 7A's Manual Auxiliary list when the user presses
「＋追加」.  Existing Auxiliary tags render as 「追加済み」 and cannot be
added twice.

The worker uses a single background executor, an order-independent canonical
cache key, a 350 ms Tk debounce, and request IDs for stale-result rejection.
It has one replaceable pending slot: while A is running, queued B/C are
discarded and only the latest D begins after A. Worker callbacks write to a
thread-safe queue; Tk drains it on the main thread. A recommendation error
leaves search, Prompt preview, and copy available. Candidate display uses the
existing Japanese Overlay lookup and falls back to the canonical Prompt
spelling.

The Stage 5 runtime index and canonical overlay are opened read-only.  The
Stage 6 arithmetic and the protected source files are not modified.  The
Stage 7B recommendation frame is hidden until a Special is selected. Its
candidate rows have a vertical scrollbar; the viewport contracts at 900x540
and expands at normal/maximized height. Prompt preview and copy remain in a
separate fixed bottom row.
