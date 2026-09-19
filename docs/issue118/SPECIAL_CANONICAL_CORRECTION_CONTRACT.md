# Issue #118 Special canonical correction authority

`special_canonical_corrections_v1.csv` is the reviewed correction authority for the 11 mapping-suspect runtime groups identified by Issue #118. It enumerates every affected base Special ID, not merely the 11 runtime identities.

The importer consumes this authority explicitly. Eighteen rows have no safe current canonical, including ID 2634 whose alias index has two targets. These rows set `CatalogEntry.Canonical = null` and retain a normalized `PromptToken` from the original Special surface. This keeps discovery identity separate from the token emitted when the user explicitly adds the entry to a Prompt.

The future application order is:

1. protected linkage identity and field equality;
2. protected `ChosenCanonicalTag` validation;
3. correction overlay lookup by `special_id`;
4. corrected target existence and semantic-decision validation;
5. separate `CatalogEntry.Canonical` discovery identity from `CatalogEntry.PromptToken` output token;
6. `CatalogEntry` materialization.

For `NO_SAFE_CANONICAL`, the source Tag is normalized only for Prompt token syntax (`space` to `_`); no semantic rewriting or broader canonical substitution is performed.
