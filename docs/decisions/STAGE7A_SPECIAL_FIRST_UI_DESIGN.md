# Stage 7A Special-first UI Design

## Inventory

Before Stage 7A the production package had no UI entry point, launcher, screen,
or clipboard utility. The production APIs were `TagSearchEngine.search_one()`,
`PromptSession`/`CoreTagSet`, `GenerationProfileStore`, `PromptFormatter`, and the
Stage 6 `RecommendationEngine`. Recommendation is inspected but not connected in
this stage.

Two archived prototypes use Tkinter. Their data/search/recommendation code is not
reused because it predates the fixed Stage 3–6.5 contracts. Stage 7A uses the
standard-library Tkinter framework and the current production APIs, adding no
dependency and no second application stack.

## Identity boundary

`SpecialSearchPresenter` preserves each Stage 4 parent result order, expands its
`special_ids` into one item per Special ID, and deduplicates only repeated paths
to the same ID. The within-parent tie-break prefers a direct Special term or
Japanese match. Selection stores the Special ID. Prompt output formats the
corresponding original `SpecialTag.term`; neither statistics canonical nor
`SearchResult.prompt_representation` becomes the Special prompt identity.

Non-Special canonical results become ordered Manual Auxiliary selections. Only
the reviewed overlay `display_ja` may be a General result's Japanese display;
search-only Japanese stays a search key.

Special and General results remain standard one-line Listbox rows in the form
`日本語 / English`. Each Listbox has its own explicit vertical Scrollbar. A
multi-line/custom card framework is outside this Stage 7A correction.

Both Listboxes request one row and use grid weight to consume remaining height;
their default ten-row request is not part of the window minimum. The supported
minimum is 900x540. Prompt preview remains a separate bottom row and is visible
at the normal, minimum, and maximized geometries. When a search has no General
result, the General LabelFrame is removed and its grid row weight becomes zero;
it is restored with the existing General search results when they exist.

## Warning boundary

Physical warnings read only tag-level boolean overrides that are explicitly
`true`. Family membership and blank/None fields do not produce physical
warnings. Other notices come only from explicit `SpecialFlags`, PromptUseMode,
PromotionStatus, or the fixed identity linkage. Warnings never alter selection or
prompt output. Shape conflict and inferred cross-tag compatibility are absent.

## Runtime boundary

The launcher loads only pinned local assets. Stage 7A performs no network access,
model call, translation, update, recommendation aggregation, persistence, or
automatic prompt expansion. The related-candidate widget boundary remains in
the code for Stage 7B, but its unconnected controls are not displayed in Stage
7A and do not consume vertical space.
