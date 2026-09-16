using System.Globalization;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

public static class Issue70CatalogOverlayImporter
{
    public const string RelativePath = "docs/issue70/data/runtime/issue70_catalog_overlay.csv";
    public const string ExpectedSha256 = "1d346ad75655ea6091f9bce9a4cf58b1cf6f8fac18c7eb441f8edd009ee81433";
    public const int TotalCount = 92739;
    public const int CharacterCount = 35890;
    public const int CopyrightCount = 8536;
    public const int ArtistCount = 48313;

    public static CatalogEntry[] Read(string path)
    {
        if (AcceptedAssetImporter.Hash(path) != ExpectedSha256) throw new InvalidDataException("Issue #70 runtime overlay hash mismatch");
        var rows = AcceptedAssetImporter.Csv(path);
        if (rows.Count != TotalCount) throw new InvalidDataException($"Issue #70 runtime overlay count drift: {rows.Count} != {TotalCount}");
        var required = new[] { "row_id", "canonical_tag", "category", "category_name", "post_count", "display_ja", "search_ja", "aliases", "related_copyright", "translation_status" };
        if (rows.Count == 0 || required.Any(field => !rows[0].ContainsKey(field))) throw new InvalidDataException("Issue #70 runtime overlay schema mismatch");
        var expectedCodes = new Dictionary<string, string>(StringComparer.Ordinal) { ["Character"] = "4", ["Copyright"] = "3", ["Artist"] = "1" };
        var categoryCounts = new Dictionary<string, int>(StringComparer.Ordinal);
        var canonicals = new HashSet<string>(StringComparer.Ordinal);
        var copyrightCanonicals = rows.Where(row => row["category_name"] == "Copyright").Select(row => row["canonical_tag"]).ToHashSet(StringComparer.Ordinal);
        var entries = new List<CatalogEntry>(rows.Count);
        for (var i = 0; i < rows.Count; i++)
        {
            var row = rows[i];
            var expectedRow = $"I70-{i + 1:000000}";
            if (row["row_id"] != expectedRow) throw new InvalidDataException("Issue #70 row order mismatch at " + expectedRow);
            var category = row["category_name"];
            if (!expectedCodes.TryGetValue(category, out var categoryCode) || row["category"] != categoryCode) throw new InvalidDataException("Issue #70 category mismatch at " + row["row_id"]);
            categoryCounts[category] = categoryCounts.GetValueOrDefault(category) + 1;
            var canonical = row["canonical_tag"];
            if (string.IsNullOrWhiteSpace(canonical) || !canonicals.Add(canonical)) throw new InvalidDataException("Issue #70 duplicate/empty canonical: " + canonical);
            if (string.IsNullOrWhiteSpace(row["display_ja"])) throw new InvalidDataException("Issue #70 empty display_ja at " + row["row_id"]);
            if (row["translation_status"] is not ("ACCEPTED_AI" or "REVIEW_REQUIRED")) throw new InvalidDataException("Issue #70 invalid status at " + row["row_id"]);
            if (!long.TryParse(row["post_count"], NumberStyles.Integer, CultureInfo.InvariantCulture, out var postCount) || postCount < 0) throw new InvalidDataException("Issue #70 invalid post_count at " + row["row_id"]);
            var related = SplitPipe(row["related_copyright"]);
            if (category != "Character" && related.Length > 0) throw new InvalidDataException("Issue #70 relation attached to non-Character at " + row["row_id"]);
            if (related.Any(value => !copyrightCanonicals.Contains(value))) throw new InvalidDataException("Issue #70 unknown Copyright relation at " + row["row_id"]);
            var prefix = category switch { "Character" => "C:", "Copyright" => "R:", _ => "A:" };
            entries.Add(new CatalogEntry(prefix + canonical, canonical, canonical, row["display_ja"], false, postCount,
                SplitPipe(row["aliases"]), SplitPipe(row["search_ja"]), [], Description: row["translation_status"] == "REVIEW_REQUIRED" ? "日本語表示は要確認" : "")
            {
                TagCategory = category,
                RelatedCopyright = related
            });
        }
        if (categoryCounts.GetValueOrDefault("Character") != CharacterCount || categoryCounts.GetValueOrDefault("Copyright") != CopyrightCount || categoryCounts.GetValueOrDefault("Artist") != ArtistCount)
            throw new InvalidDataException("Issue #70 runtime category coverage mismatch");
        return entries.ToArray();
    }

    private static string[] SplitPipe(string value) => value.Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
}
