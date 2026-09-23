using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>
/// Research-only projection for Issue #132 Luna Pass A.
/// Reads the already-baked ordinary catalog and emits semantic/search surfaces
/// without current browse/taxonomy/product-review placement.
/// </summary>
public static class Issue132NeutralReviewExporter
{
    public const int ExpectedIdentityCount = Issue118SexualIntentV2Overlay.IdentityCount;
    public const string SchemaVersion = "issue132-luna-neutral-v1";
    public const string SortSalt = "issue132-pass-a-v1|";

    public sealed record Row(
        int ReviewSeq,
        string IdentityKey,
        string Canonical,
        string EnglishSurfaces,
        string DisplayJa,
        string SearchTerms,
        string Aliases,
        string NeutralDescriptionJa);

    public static IReadOnlyList<Row> Build(ICatalog catalog)
    {
        var ordinary = catalog.Entries
            .Where(entry => entry.EffectiveCategory is "General" or "Special")
            .ToArray();

        var groups = ordinary
            .GroupBy(Issue118SexualIntentV2Overlay.SourceIdentity, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal);

        if (groups.Count != ExpectedIdentityCount)
            throw new InvalidDataException($"Issue #132 neutral identity count drift: {groups.Count} != {ExpectedIdentityCount}");

        var prepared = groups.Select(pair =>
        {
            var identity = pair.Key;
            var rows = pair.Value;
            var canonical = rows.Select(row => row.Canonical).FirstOrDefault(value => !string.IsNullOrWhiteSpace(value)) ?? "";
            var representative = canonical.Length > 0
                ? catalog.Resolve(canonical) ?? rows[0]
                : catalog.Resolve(rows[0].English) ?? rows[0];

            var english = rows.Select(row => row.English)
                .Where(value => !string.IsNullOrWhiteSpace(value))
                .Distinct(StringComparer.Ordinal)
                .OrderBy(value => value, StringComparer.Ordinal)
                .ToArray();

            var search = rows.SelectMany(row => row.JapaneseSearch)
                .Where(value => !string.IsNullOrWhiteSpace(value))
                .Distinct(StringComparer.Ordinal)
                .OrderBy(value => value, StringComparer.Ordinal)
                .ToArray();

            var aliases = rows.SelectMany(row => row.Aliases)
                .Where(value => !string.IsNullOrWhiteSpace(value))
                .Distinct(StringComparer.Ordinal)
                .OrderBy(value => value, StringComparer.Ordinal)
                .ToArray();

            return new
            {
                Identity = identity,
                Canonical = canonical,
                English = JsonSerializer.Serialize(english),
                DisplayJa = representative.Japanese ?? "",
                Search = JsonSerializer.Serialize(search),
                Aliases = JsonSerializer.Serialize(aliases),
                // Deliberately blank in v1: current descriptions may mix factual
                // semantics with metadata/provenance. Luna can RESEARCH unclear rows.
                Description = "",
                SortKey = StableSortKey(identity)
            };
        })
        .OrderBy(row => row.SortKey, StringComparer.Ordinal)
        .ThenBy(row => row.Identity, StringComparer.Ordinal)
        .ToArray();

        var result = prepared.Select((row, index) => new Row(
            index + 1,
            row.Identity,
            row.Canonical,
            row.English,
            row.DisplayJa,
            row.Search,
            row.Aliases,
            row.Description)).ToArray();

        Validate(result, groups.Keys);
        return result;
    }

    public static void Export(string catalogPath, string outputCsvPath)
    {
        if (File.Exists(outputCsvPath))
            throw new IOException("Issue #132 neutral export refuses to overwrite an existing file: " + outputCsvPath);

        var catalog = CatalogDatabase.Open(catalogPath);
        var rows = Build(catalog);
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(outputCsvPath))!);

        var csv = SerializeCsv(rows);
        File.WriteAllText(outputCsvPath, csv, new UTF8Encoding(false));

        var manifestPath = Path.ChangeExtension(outputCsvPath, ".manifest.json");
        if (File.Exists(manifestPath))
            throw new IOException("Issue #132 neutral export refuses to overwrite an existing manifest: " + manifestPath);

        var manifest = new
        {
            schema_version = SchemaVersion,
            generated_utc = DateTimeOffset.UtcNow.ToString("O"),
            source_catalog = Path.GetFullPath(catalogPath),
            source_catalog_sha256 = HashFile(catalogPath),
            output_csv = Path.GetFileName(outputCsvPath),
            output_csv_sha256 = HashFile(outputCsvPath),
            identity_count = rows.Count,
            expected_identity_count = ExpectedIdentityCount,
            sort = "sha256",
            sort_salt = SortSalt,
            fields = new[]
            {
                "review_seq", "identity_key", "canonical", "english_surfaces",
                "display_ja", "search_terms", "aliases", "neutral_description_ja"
            },
            hidden_by_contract = new[]
            {
                "usage/post_count", "sexual_intent", "general_paths", "special_kind/body/theme",
                "unified_route_ids", "local_subroute_ids", "machine_bucket",
                "machine_review_signals", "phase1/prototype verdicts"
            }
        };
        File.WriteAllText(manifestPath,
            JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine,
            new UTF8Encoding(false));
    }

    public static string SerializeCsv(IReadOnlyList<Row> rows)
    {
        var builder = new StringBuilder();
        builder.AppendLine("review_seq,identity_key,canonical,english_surfaces,display_ja,search_terms,aliases,neutral_description_ja");
        foreach (var row in rows)
        {
            var values = new[]
            {
                row.ReviewSeq.ToString(System.Globalization.CultureInfo.InvariantCulture),
                row.IdentityKey,
                row.Canonical,
                row.EnglishSurfaces,
                row.DisplayJa,
                row.SearchTerms,
                row.Aliases,
                row.NeutralDescriptionJa
            };
            builder.AppendLine(string.Join(',', values.Select(Escape)));
        }
        return builder.ToString();
    }

    private static void Validate(IReadOnlyList<Row> rows, IEnumerable<string> expectedIdentities)
    {
        if (rows.Count != ExpectedIdentityCount)
            throw new InvalidDataException($"Issue #132 neutral row count drift: {rows.Count} != {ExpectedIdentityCount}");
        if (rows.Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal).Count() != rows.Count)
            throw new InvalidDataException("Issue #132 neutral export contains duplicate identity_key.");
        if (!rows.Select(row => row.IdentityKey).ToHashSet(StringComparer.Ordinal)
            .SetEquals(expectedIdentities))
            throw new InvalidDataException("Issue #132 neutral export identity set mismatch.");
        if (!rows.Select(row => row.ReviewSeq).SequenceEqual(Enumerable.Range(1, rows.Count)))
            throw new InvalidDataException("Issue #132 neutral export review_seq is not contiguous.");
        if (rows.Any(row => row.IdentityKey.Length == 0))
            throw new InvalidDataException("Issue #132 neutral export contains blank identity_key.");

        var expectedOrder = rows
            .OrderBy(row => StableSortKey(row.IdentityKey), StringComparer.Ordinal)
            .ThenBy(row => row.IdentityKey, StringComparer.Ordinal)
            .Select(row => row.IdentityKey)
            .ToArray();
        if (!rows.Select(row => row.IdentityKey).SequenceEqual(expectedOrder, StringComparer.Ordinal))
            throw new InvalidDataException("Issue #132 neutral export order does not match the deterministic hash contract.");
    }

    public static string StableSortKey(string identityKey)
        => Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(SortSalt + identityKey)));

    private static string HashFile(string path)
        => Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(path)));

    private static string Escape(string value)
        => value.Contains(',') || value.Contains('"') || value.Contains('\r') || value.Contains('\n')
            ? '"' + value.Replace("\"", "\"\"") + '"' : value;
}
