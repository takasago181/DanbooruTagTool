using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>
/// Explicit Issue #76 prototype loader. It reads only a generated v0.8 analysis CSV;
/// it is not part of the accepted production catalog import path.
/// </summary>
public static class Issue76SpecialBrowseV2Loader
{
    public static SpecialBrowseV2Index Load(string path, bool requireFullCoverage = true)
    {
        if (!File.Exists(path)) throw new FileNotFoundException("Issue #76 v2 prototype sidecar not found", path);
        var rows = AcceptedAssetImporter.Csv(path);
        if (requireFullCoverage)
        {
            var ids = rows.Select(row => int.Parse(row["special_id"], System.Globalization.CultureInfo.InvariantCulture)).Order().ToArray();
            if (ids.Length != 2788 || !ids.SequenceEqual(Enumerable.Range(1, 2788)))
                throw new InvalidDataException("Issue #76 v2 sidecar must cover exact Special IDs 1..2788");
        }

        var entries = rows.Select(row => new SpecialBrowseV2Entry(
            "S:" + row["special_id"],
            EmptyToNull(row["v2_kind_id"]),
            Split(row["v2_body_sites"]),
            Split(row["v2_themes"]),
            ParseStatus(row["v2_status"]))).ToArray();

        if (entries.Select(entry => entry.CatalogId).Distinct(StringComparer.Ordinal).Count() != entries.Length)
            throw new InvalidDataException("Issue #76 v2 sidecar contains duplicate Special IDs");

        return new(entries);
    }

    private static string? EmptyToNull(string value) => string.IsNullOrWhiteSpace(value) ? null : value.Trim();

    private static IReadOnlySet<string> Split(string value) => value
        .Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
        .ToHashSet(StringComparer.Ordinal);

    private static SpecialBrowseV2Status ParseStatus(string value) => value switch
    {
        "AUTO_CANDIDATE" => SpecialBrowseV2Status.AutoCandidate,
        "HUMAN_RESOLVED" => SpecialBrowseV2Status.HumanResolved,
        "REFERENCE_ONLY_NO_DIRECT_BROWSE" => SpecialBrowseV2Status.ReferenceOnlyNoDirectBrowse,
        "DEFER_PRODUCT_FIT_REVIEW" => SpecialBrowseV2Status.DeferProductFitReview,
        "OUT_OF_SCOPE_NO_BROWSE" => SpecialBrowseV2Status.OutOfScopeNoBrowse,
        _ => throw new InvalidDataException("Unknown Issue #76 v2 status: " + value)
    };
}
