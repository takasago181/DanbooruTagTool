# WQHD Dictionary Layout Draft

Status: implementation draft for the next post-v1 UI refinement.

Primary display target:
- 27-inch monitor
- WQHD 2560x1440
- maximized window usage

Design priority:
- optimize information density and simultaneous visibility for the primary WQHD/maximized workflow;
- smaller windows should remain usable and non-broken, but they are not the primary optimization target.

## Dictionary workspace target

Use three main columns:

1. Navigation / genre tree
   - fixed-ish practical width around 280-320px at WQHD
   - enough for Japanese category labels without aggressive truncation

2. Tag dictionary results
   - largest working area
   - use a two-column result layout when the available center width is sufficient
   - each tag card/row should show Japanese primary label, canonical English secondary label, usage count, and add/remove state
   - compact vertical spacing
   - preserve relevance/order from the existing Results sequence
   - do not regroup/sort differently merely because the visual layout has two columns

3. Details / Current Prompt
   - practical fixed/minimum width around 360-420px at WQHD
   - remove the need to switch tabs during normal use
   - show tag details in the upper section and Current Prompt in the lower section simultaneously
   - retain the accepted add/remove toggle behavior from Issue #73

## Result-item density

Current one-result-per-full-width-row wastes horizontal space at WQHD.

Target visual concept:

[ Japanese label ]       [ Japanese label ]
[ canonical ]  count [+] [ canonical ] count [✓]

Prefer compact cards/rows in a WrapPanel/UniformGrid-like two-column arrangement.

Requirements:
- Japanese label remains fully readable; wrapping is preferred over ellipsis for long labels.
- canonical English may use smaller muted text.
- usage count and add/remove state remain immediately visible.
- row/card click still selects the tag and updates details.
- no change to search ranking/order semantics.
- no hidden bulk add/remove behavior.

## Right-side combined pane

Replace the `タグ詳細 / 現在のPrompt` tab-switching requirement with simultaneous sections at the WQHD primary layout.

Upper section: Tag details
- Japanese label
- canonical English
- usage count
- category
- browse/taxonomy path
- add/remove toggle

Lower section: Current Prompt
- current item count
- Japanese-first compact list/chips
- item-level delete if already supported safely
- opening Prompt Edit remains available

A simple vertical split is preferred over adding a new framework. A GridSplitter is acceptable if cleanly implemented, but a fixed proportional split is also acceptable.

## Responsive fallback

Primary behavior is WQHD/maximized.

When the available width becomes meaningfully smaller:
- result area may fall back to one column rather than compressing cards into unreadable widths;
- right-side combined pane may retain a practical minimum width;
- avoid clipping controls or Japanese labels.

Do not optimize the whole product around the historical 1280x720 design baseline at the expense of WQHD density.

## Invariants

- no Prompt serialization changes;
- no search ranking changes;
- no taxonomy/canonical/translation changes;
- keep Issue #72 category view behavior;
- keep Issue #73 English pane and add/remove toggle behavior;
- no new top-level folders;
- no duplicate WPF app;
- no runtime LLM dependency.
