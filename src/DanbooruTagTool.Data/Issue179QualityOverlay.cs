using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>
/// Build-time reviewed display/search correction overlay for Issue #179.
/// The accepted Issue #70 source remains immutable; this projection only
/// changes Japanese display/search metadata for explicitly reviewed rows.
/// </summary>
public static class Issue179QualityOverlay
{
    public const string RelativePath = "docs/issue179/runtime/ISSUE179_RUNTIME_PROJECTION_V1.csv";
    public const string ExpectedSha256 = "ae18db177b455bbda3ea191a3ca5df7cbb8621174350393de119737b143df50e";
    public const int ExpectedRows = 1180;
    public const int ExpectedDisplayRows = 217;
    public const int ExpectedSearchRows = 969;
    public const int ExpectedEmptySearchRows = 2;

    public static CatalogEntry[] Apply(string projectionPath, string issue70Path, CatalogEntry[] entries)
    {
        if (AcceptedAssetImporter.Hash(projectionPath) != ExpectedSha256)
            throw new InvalidDataException("Issue179 runtime projection hash mismatch");

        var sourceRows = AcceptedAssetImporter.Csv(issue70Path);
        var sourceByRow = sourceRows.ToDictionary(
            row => row["row_id"],
            row => row["canonical_tag"],
            StringComparer.Ordinal);

        var byCanonical = entries
            .Where(e => e.Canonical is not null)
            .ToDictionary(e => e.Canonical!, StringComparer.Ordinal);

        var projection = AcceptedAssetImporter.Csv(projectionPath);
        if (projection.Count != ExpectedRows)
            throw new InvalidDataException($"Issue179 runtime projection row drift: {projection.Count} != {ExpectedRows}");

        var seenRows = new HashSet<string>(StringComparer.Ordinal);
        var displayCount = 0;
        var searchCount = 0;
        var emptySearchCount = 0;
        var changes = new Dictionary<string, (string? Display, bool HasDisplay, string[] Search, bool HasSearch)>(StringComparer.Ordinal);

        foreach (var row in projection)
        {
            var rowId = row["row_id"];
            if (!seenRows.Add(rowId) || !sourceByRow.TryGetValue(rowId, out var canonical))
                throw new InvalidDataException("Invalid Issue179 row identity: " + rowId);
            if (!byCanonical.TryGetValue(canonical, out var entry) ||
                entry.EffectiveCategory is not ("Character" or "Copyright"))
                throw new InvalidDataException("Issue179 target is not a Character/Copyright runtime row: " + rowId);

            var hasDisplay = ParseFlag(row["has_display"], rowId, "has_display");
            var hasSearch = ParseFlag(row["has_search"], rowId, "has_search");
            var display = row["display_ja"];
            var search = SplitPipe(row["search_ja"]);

            if (!hasDisplay && display.Length != 0)
                throw new InvalidDataException("Issue179 display value without has_display at " + rowId);
            if (hasDisplay && string.IsNullOrWhiteSpace(display))
                throw new InvalidDataException("Issue179 empty reviewed display at " + rowId);
            if (!hasSearch && row["search_ja"].Length != 0)
                throw new InvalidDataException("Issue179 search value without has_search at " + rowId);

            if (hasDisplay) displayCount++;
            if (hasSearch)
            {
                searchCount++;
                if (search.Length == 0) emptySearchCount++;
            }

            if (!changes.TryAdd(canonical, (hasDisplay ? display : null, hasDisplay, search, hasSearch)))
                throw new InvalidDataException("Duplicate Issue179 canonical target: " + canonical);
        }

        if (displayCount != ExpectedDisplayRows || searchCount != ExpectedSearchRows ||
            emptySearchCount != ExpectedEmptySearchRows)
            throw new InvalidDataException(
                $"Issue179 projection coverage drift: display={displayCount}, search={searchCount}, emptySearch={emptySearchCount}");

        return entries.Select(entry =>
        {
            if (entry.Canonical is null || !changes.TryGetValue(entry.Canonical, out var change))
                return entry;
            return entry with
            {
                Japanese = change.HasDisplay ? change.Display : entry.Japanese,
                JapaneseSearch = change.HasSearch ? change.Search : entry.JapaneseSearch
            };
        }).ToArray();
    }

    private static bool ParseFlag(string value, string rowId, string field)
        => value switch
        {
            "0" => false,
            "1" => true,
            _ => throw new InvalidDataException($"Invalid Issue179 {field} at {rowId}: {value}")
        };

    private static string[] SplitPipe(string value)
        => value.Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
}
