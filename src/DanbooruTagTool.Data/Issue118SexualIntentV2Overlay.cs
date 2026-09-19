using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>
/// Explicit catalog-build boundary for the runtime-canonical Issue #118 v2
/// authority. Normal startup reads only the baked CatalogEntry metadata.
/// </summary>
public static class Issue118SexualIntentV2Overlay
{
    public const string RelativePath = "docs/issue118/production_candidate/sexual_intent_v2.csv";
    public const string SummaryRelativePath = "docs/issue118/production_candidate/sexual_intent_v2_summary.json";
    public const int IdentityCount = 31_003;
    public const string ExpectedSha256 = "d2966dbc3c70617af2a985a94f81650785a29c1668b40b582d3c213ef2a68bc0";

    // These are pinned after the authority is generated and independently
    // validated from the current ordinary importer output.
    public const int AutoHighConfidenceCount = 22_206;
    public const int HumanReviewedCount = 8_793;
    public const int UnclassifiedCount = 4;
    public const int SexualCount = 1_506;
    public const int ContextualCount = 1_786;
    public const int NonSexualCount = 27_707;

    public static CatalogEntry[] Bake(ICatalog catalog, string authorityRoot, IDictionary<string, string>? sourceHashes = null)
    {
        var path = Path.Combine(authorityRoot, RelativePath);
        if (!File.Exists(path)) throw new FileNotFoundException("Missing Issue #118 runtime-canonical v2 authority.", path);
        var hash = AcceptedAssetImporter.Hash(path);
        if (!string.Equals(hash, ExpectedSha256, StringComparison.Ordinal))
            throw new InvalidDataException("Issue #118 v2 authority hash mismatch: " + hash);
        sourceHashes?[RelativePath] = hash;

        var rows = AcceptedAssetImporter.Csv(path);
        if (rows.Count != IdentityCount)
            throw new InvalidDataException($"Issue #118 v2 authority row count drift: {rows.Count} != {IdentityCount}");

        var byIdentity = new Dictionary<string, IReadOnlyDictionary<string, string>>(StringComparer.Ordinal);
        foreach (var row in rows)
        {
            RequireFields(row);
            var key = row["identity_key"];
            if (key.Length == 0 || !byIdentity.TryAdd(key, row))
                throw new InvalidDataException("Issue #118 v2 authority has empty/duplicate identity: " + key);
            ValidateVerdict(row);
        }

        var ordinary = catalog.Entries.Where(entry => entry.EffectiveCategory is "General" or "Special").ToArray();
        var groups = ordinary.GroupBy(SourceIdentity, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal);
        if (groups.Count != IdentityCount || !groups.Keys.ToHashSet(StringComparer.Ordinal).SetEquals(byIdentity.Keys))
            throw new InvalidDataException($"Issue #118 v2 authority/current ordinary identity union mismatch: catalog={groups.Count}, authority={byIdentity.Count}");

        ValidateCounts(byIdentity.Values);
        foreach (var (key, backing) in groups)
        {
            var row = byIdentity[key];
            var general = backing.Any(entry => entry.EffectiveCategory == "General");
            var special = backing.Any(entry => entry.EffectiveCategory == "Special");
            if (row["is_general"] != (general ? "YES" : "NO") || row["is_special"] != (special ? "YES" : "NO"))
                throw new InvalidDataException("Issue #118 v2 General/Special membership drift at " + key);
            if (row["mapping_quality"] != "VALID" || row["reviewer_action"] is not ("RESOLVED" or "NOT_APPLICABLE"))
                throw new InvalidDataException("Issue #118 v2 unresolved mapping review at " + key);
            if (row["semantic_conflict"] != "NO")
                throw new InvalidDataException("Issue #118 v2 semantic conflict remains at " + key);
        }

        return catalog.Entries.Select(entry =>
        {
            if (entry.EffectiveCategory is not ("General" or "Special")) return entry;
            var row = byIdentity[SourceIdentity(entry)];
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

    private static void RequireFields(IReadOnlyDictionary<string, string> row)
    {
        foreach (var field in new[] { "identity_key", "is_general", "is_special", "sexual_intent", "review_status", "rule_id", "evidence", "provenance", "source_identity_count", "source_identities", "runtime_backing_count", "mapping_quality", "reviewer_action", "semantic_conflict" })
            if (!row.ContainsKey(field)) throw new InvalidDataException("Issue #118 v2 authority missing field: " + field);
    }

    private static void ValidateVerdict(IReadOnlyDictionary<string, string> row)
    {
        if (row["is_general"] is not ("YES" or "NO") || row["is_special"] is not ("YES" or "NO"))
            throw new InvalidDataException("Issue #118 v2 invalid membership: " + row["identity_key"]);
        if (row["review_status"] == "UNCLASSIFIED")
        {
            if (row["sexual_intent"].Length != 0) throw new InvalidDataException("Issue #118 v2 UNCLASSIFIED row carries semantic intent: " + row["identity_key"]);
        }
        else
        {
            if (row["review_status"] is not ("AUTO_HIGH_CONF" or "HUMAN_REVIEWED"))
                throw new InvalidDataException("Issue #118 v2 invalid review status: " + row["review_status"]);
            _ = ParseIntent(row["sexual_intent"]) ?? throw new InvalidDataException("Issue #118 v2 classified row has empty intent: " + row["identity_key"]);
        }
        if (row["provenance"].Length == 0 || row["rule_id"].Length == 0 || row["evidence"].Length == 0)
            throw new InvalidDataException("Issue #118 v2 authority lacks provenance/evidence: " + row["identity_key"]);
    }

    private static void ValidateCounts(IEnumerable<IReadOnlyDictionary<string, string>> source)
    {
        var rows = source.ToArray();
        Expect(rows, "review_status", "AUTO_HIGH_CONF", AutoHighConfidenceCount);
        Expect(rows, "review_status", "HUMAN_REVIEWED", HumanReviewedCount);
        Expect(rows, "review_status", "UNCLASSIFIED", UnclassifiedCount);
        Expect(rows, "sexual_intent", "SEXUAL", SexualCount);
        Expect(rows, "sexual_intent", "CONTEXTUAL", ContextualCount);
        Expect(rows, "sexual_intent", "NON_SEXUAL", NonSexualCount);
        Expect(rows, "sexual_intent", "", UnclassifiedCount);
    }

    private static void Expect(IReadOnlyList<IReadOnlyDictionary<string, string>> rows, string field, string value, int expected)
    {
        var actual = rows.Count(row => row[field] == value);
        if (actual != expected) throw new InvalidDataException($"Issue #118 v2 {field}={value} drift: {actual} != {expected}");
    }

    private static SexualIntentClass? ParseIntent(string value) => value switch
    {
        "" => null,
        "SEXUAL" => SexualIntentClass.Sexual,
        "CONTEXTUAL" => SexualIntentClass.Contextual,
        "NON_SEXUAL" => SexualIntentClass.NonSexual,
        _ => throw new InvalidDataException("Issue #118 v2 invalid sexual intent: " + value)
    };

    private static SexualIntentClassificationStatus ParseStatus(string value) => value switch
    {
        "AUTO_HIGH_CONF" => SexualIntentClassificationStatus.AutoHighConfidence,
        "HUMAN_REVIEWED" => SexualIntentClassificationStatus.HumanReviewed,
        "UNCLASSIFIED" => SexualIntentClassificationStatus.Unclassified,
        _ => throw new InvalidDataException("Issue #118 v2 invalid review status: " + value)
    };
}
