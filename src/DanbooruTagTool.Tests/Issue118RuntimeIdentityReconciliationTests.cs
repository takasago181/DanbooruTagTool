using System.IO;
using System.Text;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue118RuntimeIdentityReconciliationTests(ITestOutputHelper output)
{
    [ProductionFact]
    public void ReconcileV1AuthorityToOrdinaryRuntimeIdentities()
    {
        var sourceRoot = Environment.GetEnvironmentVariable("DTT_SOURCE_ROOT")!;
        var authorityRoot = Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT")!;
        var imported = AcceptedAssetImporter.Read(sourceRoot, authorityRoot, CatalogBuildProfile.Ordinary);
        var authorityPath = Path.Combine(authorityRoot, Issue118SexualIntentOverlay.RelativePath);
        var authority = AcceptedAssetImporter.Csv(authorityPath);
        var authorityByIdentity = authority.ToDictionary(row => row["identity_key"], StringComparer.Ordinal);
        Assert.Equal(Issue118SexualIntentOverlay.IdentityCount, authorityByIdentity.Count);

        var ordinary = imported.Entries.Where(entry => entry.EffectiveCategory is "General" or "Special").ToArray();
        var runtimeGroups = ordinary
            .GroupBy(Issue118SexualIntentOverlay.SourceIdentity, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal);
        var sourceToRuntime = new Dictionary<string, string>(StringComparer.Ordinal);
        var sourceMappingErrors = new HashSet<string>(StringComparer.Ordinal);

        foreach (var entry in ordinary)
        {
            var sourceIdentity = SourceIdentity(entry);
            var runtimeIdentity = Issue118SexualIntentOverlay.SourceIdentity(entry);
            if (!sourceToRuntime.TryAdd(sourceIdentity, runtimeIdentity) && sourceToRuntime[sourceIdentity] != runtimeIdentity)
                sourceMappingErrors.Add(sourceIdentity);
        }

        var records = new List<AuditRecord>(authority.Count + runtimeGroups.Count);
        foreach (var row in authority)
        {
            var sourceIdentity = row["identity_key"];
            if (!sourceToRuntime.TryGetValue(sourceIdentity, out var runtimeIdentity) || sourceMappingErrors.Contains(sourceIdentity) || !runtimeGroups.TryGetValue(runtimeIdentity, out var backing))
            {
                records.Add(AuditRecord.Missing(sourceIdentity, row));
                continue;
            }

            var authoritySourceRows = backing
                .Select(SourceIdentity)
                .Distinct(StringComparer.Ordinal)
                .Where(authorityByIdentity.ContainsKey)
                .Select(identity => authorityByIdentity[identity])
                .ToArray();
            records.Add(AuditRecord.ForSource(sourceIdentity, row, runtimeIdentity, backing, authoritySourceRows));
        }

        foreach (var (runtimeIdentity, backing) in runtimeGroups.OrderBy(pair => pair.Key, StringComparer.Ordinal))
        {
            var sourceIdentities = backing.Select(SourceIdentity).Distinct(StringComparer.Ordinal).ToArray();
            if (sourceIdentities.Any(authorityByIdentity.ContainsKey)) continue;
            records.Add(AuditRecord.RuntimeOnly(runtimeIdentity, backing));
        }

        var auditPath = Path.Combine(authorityRoot, "docs/issue118/runtime_identity_reconciliation_v1.csv");
        var conflictPath = Path.Combine(authorityRoot, "docs/issue118/runtime_identity_conflicts_v1.csv");
        Directory.CreateDirectory(Path.GetDirectoryName(auditPath)!);
        WriteCsv(auditPath, records);
        WriteCsv(conflictPath, records.Where(record => record.ReconciliationStatus is "SEMANTIC_CONFLICT" or "UNCLASSIFIED_CONFLICT" or "IDENTITY_MAPPING_ERROR"));

        var statusCounts = records.GroupBy(record => record.ReconciliationStatus).ToDictionary(group => group.Key, group => group.Count(), StringComparer.Ordinal);
        var authoritySourceCount = records.Count(record => record.RecordKind == "SOURCE_AUTHORITY");
        var runtimeIdentityCount = runtimeGroups.Count;
        var collapseGroups = runtimeGroups.Values.Count(backing => backing.Select(SourceIdentity).Distinct(StringComparer.Ordinal).Count() > 1);
        var conflictGroups = runtimeGroups.Keys.Count(runtimeIdentity => records.Any(record => record.RuntimeIdentity == runtimeIdentity && (record.ReconciliationStatus is "SEMANTIC_CONFLICT" or "UNCLASSIFIED_CONFLICT")));
        var mappingErrors = records.Count(record => record.ReconciliationStatus == "IDENTITY_MAPPING_ERROR");

        output.WriteLine($"Issue #118 v1 source identities: {authoritySourceCount}");
        output.WriteLine($"Ordinary runtime identities: {runtimeIdentityCount}");
        output.WriteLine($"Reduction: {authoritySourceCount - runtimeIdentityCount}");
        output.WriteLine($"Affected collapse groups: {collapseGroups}");
        output.WriteLine($"Semantic conflict groups: {conflictGroups}");
        output.WriteLine($"Identity mapping errors: {mappingErrors}");
        output.WriteLine("Reconciliation status counts: " + string.Join(", ", statusCounts.OrderBy(pair => pair.Key).Select(pair => $"{pair.Key}={pair.Value}")));

        Assert.Equal(Issue118SexualIntentOverlay.IdentityCount, authoritySourceCount);
        Assert.Equal(Issue118SexualIntentOverlay.IdentityCount, authority.Count);
        Assert.Equal(30_985, runtimeIdentityCount);
        Assert.Equal(767, authoritySourceCount - runtimeIdentityCount);
        Assert.Equal(490, collapseGroups);
        Assert.Equal(116, conflictGroups);
        Assert.Equal(303, records.Count(record => record.ReconciliationStatus == "SEMANTIC_CONFLICT"));
        Assert.Equal(runtimeIdentityCount, records.Where(record => record.RuntimeIdentity.Length > 0).Select(record => record.RuntimeIdentity).Distinct(StringComparer.Ordinal).Count());
        Assert.Empty(sourceMappingErrors);
        Assert.Equal(0, mappingErrors);
        Assert.Equal(0, records.Count(record => record.MembershipStatus == "MISMATCH"));
        Assert.Equal(
            authorityByIdentity.Keys.OrderBy(value => value, StringComparer.Ordinal),
            records.Where(record => record.RecordKind == "SOURCE_AUTHORITY").Select(record => record.SourceIdentity).OrderBy(value => value, StringComparer.Ordinal));
        Assert.Equal(
            runtimeGroups.Keys.OrderBy(value => value, StringComparer.Ordinal),
            records.Where(record => record.RuntimeIdentity.Length > 0).Select(record => record.RuntimeIdentity).Distinct(StringComparer.Ordinal).OrderBy(value => value, StringComparer.Ordinal));
        Assert.Contains(ordinary, entry => entry.IsSpecial && entry.Canonical != null && Issue118SexualIntentOverlay.NormalizeIdentity(entry.English) != Issue118SexualIntentOverlay.NormalizeIdentity(entry.Canonical));
        Assert.Throws<InvalidDataException>(() => Issue118SexualIntentOverlay.Bake(new Catalog(imported.Entries), authorityRoot));
    }

    private static string SourceIdentity(CatalogEntry entry)
        => Issue118SexualIntentOverlay.NormalizeIdentity(entry.IsSpecial ? entry.English : entry.Canonical ?? entry.English);

    private static void WriteCsv(string path, IEnumerable<AuditRecord> records)
    {
        var rows = records.OrderBy(record => record.RecordKind, StringComparer.Ordinal).ThenBy(record => record.SourceIdentity, StringComparer.Ordinal).ToArray();
        var fields = new[]
        {
            "record_kind", "source_identity", "source_is_general", "source_is_special", "source_sexual_intent", "source_review_status", "source_rule_id", "source_evidence",
            "runtime_identity", "runtime_backing_count", "runtime_is_general", "runtime_is_special", "general_canonicals", "special_ids", "special_tags", "chosen_canonical_tags",
            "collapse_group_size", "semantic_classes", "review_statuses", "membership_status", "reconciliation_status"
        };
        var builder = new StringBuilder();
        builder.AppendLine(string.Join(',', fields));
        foreach (var row in rows)
            builder.AppendLine(string.Join(',', row.Values().Select(Escape)));
        File.WriteAllText(path, builder.ToString(), new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    }

    private static string Escape(string value)
    {
        if (!value.Contains(',') && !value.Contains('"') && !value.Contains('\r') && !value.Contains('\n')) return value;
        return '"' + value.Replace("\"", "\"\"") + '"';
    }

    private sealed record AuditRecord(
        string RecordKind,
        string SourceIdentity,
        string SourceIsGeneral,
        string SourceIsSpecial,
        string SourceSexualIntent,
        string SourceReviewStatus,
        string SourceRuleId,
        string SourceEvidence,
        string RuntimeIdentity,
        string RuntimeBackingCount,
        string RuntimeIsGeneral,
        string RuntimeIsSpecial,
        string GeneralCanonicals,
        string SpecialIds,
        string SpecialTags,
        string ChosenCanonicalTags,
        string CollapseGroupSize,
        string SemanticClasses,
        string ReviewStatuses,
        string MembershipStatus,
        string ReconciliationStatus)
    {
        public IEnumerable<string> Values()
        {
            yield return RecordKind; yield return SourceIdentity; yield return SourceIsGeneral; yield return SourceIsSpecial;
            yield return SourceSexualIntent; yield return SourceReviewStatus; yield return SourceRuleId; yield return SourceEvidence;
            yield return RuntimeIdentity; yield return RuntimeBackingCount; yield return RuntimeIsGeneral; yield return RuntimeIsSpecial;
            yield return GeneralCanonicals; yield return SpecialIds; yield return SpecialTags; yield return ChosenCanonicalTags;
            yield return CollapseGroupSize; yield return SemanticClasses; yield return ReviewStatuses; yield return MembershipStatus; yield return ReconciliationStatus;
        }

        public static AuditRecord Missing(string sourceIdentity, IReadOnlyDictionary<string, string> source)
            => new("SOURCE_AUTHORITY", sourceIdentity, source["is_general"], source["is_special"], source["sexual_intent"], source["review_status"], source["rule_id"], source["evidence"], "", "0", "", "", "", "", "", "", "0", "", "", "UNKNOWN", "IDENTITY_MAPPING_ERROR");

        public static AuditRecord RuntimeOnly(string runtimeIdentity, IReadOnlyList<CatalogEntry> backing)
            => Build("RUNTIME_ONLY", "", null, runtimeIdentity, backing, []);

        public static AuditRecord ForSource(string sourceIdentity, IReadOnlyDictionary<string, string> source, string runtimeIdentity, IReadOnlyList<CatalogEntry> backing, IReadOnlyList<IReadOnlyDictionary<string, string>> sourceRows)
            => Build("SOURCE_AUTHORITY", sourceIdentity, source, runtimeIdentity, backing, sourceRows);

        private static AuditRecord Build(string kind, string sourceIdentity, IReadOnlyDictionary<string, string>? sourceIdentityRow, string runtimeIdentity, IReadOnlyList<CatalogEntry> backing, IReadOnlyList<IReadOnlyDictionary<string, string>> sourceRows)
        {
            var semanticClasses = sourceRows.Select(row => row["sexual_intent"]).Where(value => value.Length > 0).Distinct(StringComparer.Ordinal).OrderBy(value => value, StringComparer.Ordinal).ToArray();
            var statuses = sourceRows.Select(row => row["review_status"]).Distinct(StringComparer.Ordinal).OrderBy(value => value, StringComparer.Ordinal).ToArray();
            var hasClassified = semanticClasses.Length > 0;
            var hasUnclassified = sourceRows.Any(row => row["review_status"] == "UNCLASSIFIED");
            var reconciliation = sourceRows.Count == 0
                ? "IDENTITY_MAPPING_ERROR"
                : semanticClasses.Length > 1
                    ? "SEMANTIC_CONFLICT"
                    : hasClassified && hasUnclassified
                        ? "UNCLASSIFIED_CONFLICT"
                        : sourceRows.Select(row => row["identity_key"]).Distinct(StringComparer.Ordinal).Count() == 1
                            ? "ONE_TO_ONE"
                            : "COLLAPSE_SAME_VERDICT";
            var runtimeGeneral = backing.Any(entry => entry.EffectiveCategory == "General");
            var runtimeSpecial = backing.Any(entry => entry.EffectiveCategory == "Special");
            var sourceGeneral = sourceRows.Any(row => row["is_general"] == "YES");
            var sourceSpecial = sourceRows.Any(row => row["is_special"] == "YES");
            var membership = sourceRows.Count == 0 || sourceGeneral != runtimeGeneral || sourceSpecial != runtimeSpecial ? "MISMATCH" : "MATCH";
            var source = sourceIdentityRow ?? new Dictionary<string, string>();
            return new(
                kind, sourceIdentity, source.GetValueOrDefault("is_general", ""), source.GetValueOrDefault("is_special", ""), source.GetValueOrDefault("sexual_intent", ""), source.GetValueOrDefault("review_status", ""), source.GetValueOrDefault("rule_id", ""), source.GetValueOrDefault("evidence", ""),
                runtimeIdentity, backing.Count.ToString(), runtimeGeneral ? "YES" : "NO", runtimeSpecial ? "YES" : "NO",
                Join(backing.Where(entry => entry.EffectiveCategory == "General").Select(entry => entry.Canonical ?? entry.English)),
                Join(backing.Where(entry => entry.EffectiveCategory == "Special").Select(entry => entry.Id.StartsWith("S:", StringComparison.Ordinal) ? entry.Id[2..] : entry.Id)),
                Join(backing.Where(entry => entry.EffectiveCategory == "Special").Select(entry => entry.English)),
                Join(backing.Where(entry => entry.EffectiveCategory == "Special").Select(entry => entry.Canonical ?? "")),
                sourceRows.Select(row => row["identity_key"]).Distinct(StringComparer.Ordinal).Count().ToString(), string.Join("|", semanticClasses), string.Join("|", statuses), membership, reconciliation);
        }

        private static string Join(IEnumerable<string> values) => string.Join("|", values.Where(value => value.Length > 0).Distinct(StringComparer.Ordinal).OrderBy(value => value, StringComparer.Ordinal));
    }
}
