# Issue #118 Special canonical correction authority

`special_canonical_corrections_v1.csv` is the reviewed correction authority for the 11 mapping-suspect runtime groups identified by Issue #118. It enumerates every affected base Special ID, not merely the 11 runtime identities.

The authority is intentionally not consumed by `AcceptedAssetImporter` yet. Seventeen rows have no safe current canonical, and one row has an unresolved two-target alias. Treating an empty `new_canonical` as `CatalogEntry.Canonical = null` would change Prompt recognition/output and the add-to-Prompt contract. Treating the old or a broader canonical as the answer would preserve the semantic mismatch.

The future application order is:

1. protected linkage identity and field equality;
2. protected `ChosenCanonicalTag` validation;
3. correction overlay lookup by `special_id`;
4. corrected target existence and semantic-decision validation;
5. separate handling for unresolved Special surface identity versus Prompt output canonical, if the product contract accepts it;
6. `CatalogEntry` materialization.

Until that identity/output separation is accepted, this authority is audit-only and the local runtime reconciliation remains the pre-correction baseline.
