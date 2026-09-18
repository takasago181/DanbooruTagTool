using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>
/// Explicit catalog-build boundary for the Issue #118 frozen sexual-intent authority.
/// Normal startup never parses this CSV; the result is serialized into CatalogEntry.
/// </summary>
public static class Issue118SexualIntentOverlay
{
    public const string RelativePath = "docs/issue118/production_candidate/sexual_intent_v1.csv";
    public const int IdentityCount = 31_752;
    public const int AutoHighConfidenceCount = 22_371;
    public const int HumanReviewedCount = 9_376;
    public const int UnclassifiedCount = 5;
    public const int SexualCount = 2_037;
    public const int ContextualCount = 1_951;
    public const int NonSexualCount = 27_759;

    public static CatalogEntry[] Bake(ICatalog catalog, string authorityRoot, IDictionary<string, string>? sourceHashes = null)
    {
        var path = Path.Combine(authorityRoot, RelativePath);
        if (!File.Exists(path)) throw new FileNotFoundException("Missing frozen Issue #118 sexual-intent authority.", path);
        sourceHashes?[RelativePath] = AcceptedAssetImporter.Hash(path);

        var source = AcceptedAssetImporter.Csv(path);
        if (source.Count != IdentityCount)
            throw new InvalidDataException($"Issue #118 authority row count drift: {source.Count} != {IdentityCount}");

        var rows = new Dictionary<string, IReadOnlyDictionary<string, string>>(StringComparer.Ordinal);
        foreach (var row in source)
        {
            var key = row["identity_key"];
            if (key.Length == 0 || !rows.TryAdd(key, row))
                throw new InvalidDataException("Issue #118 authority has empty/duplicate identity: " + key);
            ValidateVerdict(row);
        }

        var ordinary = catalog.Entries.Where(entry => entry.EffectiveCategory is "General" or "Special").ToArray();
        var groups = ordinary.GroupBy(SourceIdentity, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal);

        if (groups.Count != IdentityCount || !groups.Keys.ToHashSet(StringComparer.Ordinal).SetEquals(rows.Keys))
            throw new InvalidDataException($"Issue #118 authority/current ordinary identity union mismatch: catalog={groups.Count}, authority={rows.Count}");

        foreach (var (key, backing) in groups)
        {
            var row = rows[key];
            var general = backing.Any(entry => entry.EffectiveCategory == "General");
            var special = backing.Any(entry => entry.EffectiveCategory == "Special");
            if (row["is_general"] != (general ? "YES" : "NO") || row["is_special"] != (special ? "YES" : "NO"))
                throw new InvalidDataException("Issue #118 General/Special membership drift at " + key);
        }

        ValidateCounts(rows.Values);

        return catalog.Entries.Select(entry =>
        {
            if (entry.EffectiveCategory is not ("General" or "Special")) return entry;
            var row = rows[SourceIdentity(entry)];
            return entry with
            {
                SexualIntent = ParseIntent(row["sexual_intent"]),
                SexualIntentStatus = ParseStatus(row["review_status"]),
                SexualIntentSource = row["rule_id"],
                SexualIntentEvidence = row["evidence"]
            };
        }).ToArray();
    }

    public static string SourceIdentity(CatalogEntry entry)
        => NormalizeIdentity(entry.Canonical ?? entry.English);

    public static string NormalizeIdentity(string value)
        => string.Join("_", value.Trim().ToLowerInvariant().Replace('_', ' ')
            .Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries));

    private static void ValidateVerdict(IReadOnlyDictionary<string, string> row)
    {
        var intent = row["sexual_intent"];
        var status = row["review_status"];
        if (status == "UNCLASSIFIED")
        {
            if (intent.Length != 0) throw new InvalidDataException("Issue #118 UNCLASSIFIED row carries semantic intent: " + row["identity_key"]);
            return;
        }
        if (status is not ("AUTO_HIGH_CONF" or "HUMAN_REVIEWED"))
            throw new InvalidDataException("Issue #118 invalid review status: " + status);
        _ = ParseIntent(intent) ?? throw new InvalidDataException("Issue #118 classified row has empty intent: " + row["identity_key"]);
    }

    private static void ValidateCounts(IEnumerable<IReadOnlyDictionary<string, string>> rows)
    {
        var list = rows.ToArray();
        void Expect(string field, string value, int expected)
        {
            var actual = list.Count(row => row[field] == value);
            if (actual != expected) throw new InvalidDataException($"Issue #118 {field}={value} drift: {actual} != {expected}");
        }
        Expect("review_status", "AUTO_HIGH_CONF", AutoHighConfidenceCount);
        Expect("review_status", "HUMAN_REVIEWED", HumanReviewedCount);
        Expect("review_status", "UNCLASSIFIED", UnclassifiedCount);
        Expect("sexual_intent", "SEXUAL", SexualCount);
        Expect("sexual_intent", "CONTEXTUAL", ContextualCount);
        Expect("sexual_intent", "NON_SEXUAL", NonSexualCount);
        Expect("sexual_intent", "", UnclassifiedCount);
    }

    private static SexualIntentClass? ParseIntent(string value) => value switch
    {
        "" => null,
        "SEXUAL" => SexualIntentClass.Sexual,
        "CONTEXTUAL" => SexualIntentClass.Contextual,
        "NON_SEXUAL" => SexualIntentClass.NonSexual,
        _ => throw new InvalidDataException("Issue #118 invalid sexual intent: " + value)
    };

    private static SexualIntentClassificationStatus ParseStatus(string value) => value switch
    {
        "AUTO_HIGH_CONF" => SexualIntentClassificationStatus.AutoHighConfidence,
        "HUMAN_REVIEWED" => SexualIntentClassificationStatus.HumanReviewed,
        "UNCLASSIFIED" => SexualIntentClassificationStatus.Unclassified,
        _ => throw new InvalidDataException("Issue #118 invalid review status: " + value)
    };
}
