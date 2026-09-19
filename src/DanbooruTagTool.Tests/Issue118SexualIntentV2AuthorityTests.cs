using System.IO;
using System.Text;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue118V2AuthorityFactAttribute : FactAttribute
{
    public Issue118V2AuthorityFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("DTT_ISSUE118_V2_GENERATE") != "1")
            Skip = "Issue #118 v2 authority generation is explicit opt-in.";
    }
}

public sealed class Issue118SexualIntentV2AuthorityTests(ITestOutputHelper output)
{
    [Issue118V2AuthorityFact]
    public void GenerateAndValidateRuntimeCanonicalV2Authority()
    {
        var sourceRoot = Environment.GetEnvironmentVariable("DTT_SOURCE_ROOT")!;
        var authorityRoot = Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT")!;
        var imported = AcceptedAssetImporter.Read(sourceRoot, authorityRoot, CatalogBuildProfile.Ordinary);
        var ordinary = imported.Entries.Where(entry => entry.EffectiveCategory is "General" or "Special").ToArray();
        var runtimeGroups = ordinary.GroupBy(Issue118SexualIntentV2Overlay.SourceIdentity, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal);
        Assert.Equal(Issue118SexualIntentV2Overlay.IdentityCount, runtimeGroups.Count);

        var v1Path = Path.Combine(authorityRoot, Issue118SexualIntentOverlay.RelativePath);
        var v1 = AcceptedAssetImporter.Csv(v1Path).ToDictionary(row => row["identity_key"], StringComparer.Ordinal);
        Assert.Equal(Issue118SexualIntentOverlay.IdentityCount, v1.Count);

        var reconciliationPath = Path.Combine(authorityRoot, "docs/issue118/runtime_identity_reconciliation_v2.csv");
        var reconciliation = AcceptedAssetImporter.Csv(reconciliationPath);
        var mappingErrors = reconciliation.Count(row => row["reconciliation_status"] == "IDENTITY_MAPPING_ERROR");
        Assert.Equal(0, mappingErrors);
        Assert.Equal(runtimeGroups.Keys.OrderBy(value => value, StringComparer.Ordinal),
            reconciliation.Where(row => row["runtime_identity"].Length > 0).Select(row => row["runtime_identity"])
                .Distinct(StringComparer.Ordinal).OrderBy(value => value, StringComparer.Ordinal));

        var conflictKeys = reconciliation.Where(row => row["reconciliation_status"] is "SEMANTIC_CONFLICT" or "UNCLASSIFIED_CONFLICT")
            .Select(row => row["runtime_identity"]).Distinct(StringComparer.Ordinal).ToHashSet(StringComparer.Ordinal);
        var decisionPath = Path.Combine(authorityRoot, "docs/issue118/runtime_identity_conflict_review_decisions_v2.csv");
        var decisions = AcceptedAssetImporter.Csv(decisionPath).ToDictionary(row => row["runtime_identity"], StringComparer.Ordinal);
        Assert.Equal(conflictKeys, decisions.Keys.ToHashSet(StringComparer.Ordinal));
        Assert.DoesNotContain(decisions.Values, row => row["mapping_quality"] != "VALID" || row["reviewer_action"] != "RESOLVED");

        var rows = runtimeGroups.OrderBy(pair => pair.Key, StringComparer.Ordinal)
            .Select(pair => BuildRow(pair.Key, pair.Value, v1, decisions))
            .ToArray();
        Assert.Equal(runtimeGroups.Count, rows.Length);
        Assert.Equal(rows.Length, rows.Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal).Count());
        Assert.DoesNotContain(rows, row => row.MappingQuality != "VALID" || row.SemanticConflict != "NO");
        Assert.Equal(0, rows.Count(row => row.ReviewerAction == "NEEDS_CANONICAL_FIX"));

        var candidatePath = Path.Combine(authorityRoot, Issue118SexualIntentV2Overlay.RelativePath);
        Directory.CreateDirectory(Path.GetDirectoryName(candidatePath)!);
        WriteCsv(candidatePath, rows);
        var summaryPath = Path.Combine(authorityRoot, Issue118SexualIntentV2Overlay.SummaryRelativePath);
        WriteSummary(summaryPath, rows, ordinary, v1Path, reconciliationPath, decisionPath,
            Path.Combine(authorityRoot, Issue118SpecialCanonicalCorrectionOverlay.RelativePath), reconciliation, conflictKeys);

        var hash = AcceptedAssetImporter.Hash(candidatePath);
        output.WriteLine($"V2 authority: {candidatePath}");
        output.WriteLine($"V2 SHA-256: {hash}");
        output.WriteLine($"Runtime identities: {rows.Length}; General={rows.Count(row => row.IsGeneral == "YES")}; Special={rows.Count(row => row.IsSpecial == "YES")}; overlap={rows.Count(row => row.IsGeneral == "YES" && row.IsSpecial == "YES")}");
        output.WriteLine("Intent counts: " + string.Join(", ", rows.GroupBy(row => row.SexualIntent.Length == 0 ? "UNCLASSIFIED" : row.SexualIntent).OrderBy(group => group.Key).Select(group => $"{group.Key}={group.Count()}")));
        output.WriteLine("Status counts: " + string.Join(", ", rows.GroupBy(row => row.ReviewStatus).OrderBy(group => group.Key).Select(group => $"{group.Key}={group.Count()}")));
        Assert.Equal(Issue118SexualIntentV2Overlay.IdentityCount, rows.Length);
        Assert.Equal(0, rows.Count(row => row.SemanticConflict != "NO"));
        Assert.Equal(0, rows.Count(row => row.MappingQuality != "VALID"));
    }

    private static V2Row BuildRow(string runtimeIdentity, IReadOnlyList<CatalogEntry> backing,
        IReadOnlyDictionary<string, Dictionary<string, string>> v1,
        IReadOnlyDictionary<string, Dictionary<string, string>> decisions)
    {
        var sourceIdentities = backing.Select(SourceIdentity)
            .Distinct(StringComparer.Ordinal).OrderBy(value => value, StringComparer.Ordinal).ToArray();
        var sourceRows = sourceIdentities.Select(identity => v1.TryGetValue(identity, out var row)
            ? row
            : throw new InvalidDataException("V2 authority has no v1 source row: " + identity)).ToArray();
        var semanticClasses = sourceRows.Select(row => row["sexual_intent"]).Where(value => value.Length > 0)
            .Distinct(StringComparer.Ordinal).ToArray();
        var hasUnclassified = sourceRows.Any(row => row["review_status"] == "UNCLASSIFIED");
        var isConflict = semanticClasses.Length > 1 || hasUnclassified && semanticClasses.Length > 0;

        string intent;
        string status;
        string rule;
        string evidence;
        string provenance;
        string mappingQuality;
        string reviewerAction;
        if (isConflict)
        {
            if (!decisions.TryGetValue(runtimeIdentity, out var decision))
                throw new InvalidDataException("V2 authority has no conflict decision: " + runtimeIdentity);
            intent = decision["final_sexual_intent"];
            status = decision["final_review_status"];
            rule = "RUNTIME_CANONICAL_REVIEW_V2";
            evidence = decision["review_reason"];
            provenance = "RUNTIME_CANONICAL_REVIEW_V2";
            mappingQuality = decision["mapping_quality"];
            reviewerAction = decision["reviewer_action"];
        }
        else if (semanticClasses.Length == 0)
        {
            intent = "";
            status = "UNCLASSIFIED";
            rule = sourceRows.Length == 1 ? SourceRule(sourceRows[0]) : "V1_COLLAPSE_UNCLASSIFIED";
            evidence = JoinEvidence(sourceRows);
            provenance = sourceRows.Length == 1 ? "V1_ONE_TO_ONE" : "V1_COLLAPSE_SAME_VERDICT";
            mappingQuality = "VALID";
            reviewerAction = "NOT_APPLICABLE";
        }
        else
        {
            intent = semanticClasses.Single();
            status = sourceRows.Any(row => row["review_status"] == "HUMAN_REVIEWED") ? "HUMAN_REVIEWED" : "AUTO_HIGH_CONF";
            rule = sourceRows.Length == 1 ? SourceRule(sourceRows[0]) : "V1_COLLAPSE_SAME_VERDICT";
            evidence = JoinEvidence(sourceRows);
            provenance = sourceRows.Length == 1 ? "V1_ONE_TO_ONE" : "V1_COLLAPSE_SAME_VERDICT";
            mappingQuality = "VALID";
            reviewerAction = "NOT_APPLICABLE";
        }

        var general = backing.Any(entry => entry.EffectiveCategory == "General");
        var special = backing.Any(entry => entry.EffectiveCategory == "Special");
        return new(runtimeIdentity, general ? "YES" : "NO", special ? "YES" : "NO", intent, status, rule, evidence,
            provenance, sourceIdentities.Length.ToString(), string.Join('|', sourceIdentities), backing.Count.ToString(), mappingQuality,
            reviewerAction, "NO");
    }

    private static string JoinEvidence(IEnumerable<IReadOnlyDictionary<string, string>> rows)
        => string.Join(" | ", rows.Select(row => row["identity_key"] + ": " + row["evidence"]).OrderBy(value => value, StringComparer.Ordinal));

    private static string SourceRule(IReadOnlyDictionary<string, string> row)
        => row["rule_id"].Length == 0 ? "V1_SOURCE_VERDICT" : row["rule_id"];

    private static string SourceIdentity(CatalogEntry entry)
        => Issue118SexualIntentOverlay.NormalizeIdentity(entry.IsSpecial ? entry.English : entry.Canonical ?? entry.English);

    private static void WriteCsv(string path, IReadOnlyList<V2Row> rows)
    {
        var fields = new[] { "identity_key", "is_general", "is_special", "sexual_intent", "review_status", "rule_id", "evidence", "provenance", "source_identity_count", "source_identities", "runtime_backing_count", "mapping_quality", "reviewer_action", "semantic_conflict" };
        var builder = new StringBuilder(string.Join(',', fields) + "\n");
        foreach (var row in rows) builder.AppendLine(string.Join(',', row.Values().Select(Escape)));
        File.WriteAllText(path, builder.ToString(), new UTF8Encoding(false));
    }

    private static void WriteSummary(string path, IReadOnlyList<V2Row> rows, IReadOnlyList<CatalogEntry> ordinary,
        string v1Path, string reconciliationPath, string decisionPath, string correctionPath,
        IReadOnlyList<IReadOnlyDictionary<string, string>> reconciliation, IReadOnlySet<string> conflictKeys)
    {
        var json = new
        {
            schema_version = 2,
            authority = Issue118SexualIntentV2Overlay.RelativePath,
            counts = new
            {
                total_identities = rows.Count,
                general_identities = rows.Count(row => row.IsGeneral == "YES"),
                special_identities = rows.Count(row => row.IsSpecial == "YES"),
                overlap_identities = rows.Count(row => row.IsGeneral == "YES" && row.IsSpecial == "YES"),
                sexual = rows.Count(row => row.SexualIntent == "SEXUAL"),
                non_sexual = rows.Count(row => row.SexualIntent == "NON_SEXUAL"),
                contextual = rows.Count(row => row.SexualIntent == "CONTEXTUAL"),
                unclassified = rows.Count(row => row.SexualIntent.Length == 0),
                auto_high_conf = rows.Count(row => row.ReviewStatus == "AUTO_HIGH_CONF"),
                human_reviewed = rows.Count(row => row.ReviewStatus == "HUMAN_REVIEWED"),
                unclassified_review_status = rows.Count(row => row.ReviewStatus == "UNCLASSIFIED"),
                ordinary_backing_rows = ordinary.Count
            },
            hashes = new
            {
                source_v1_sha256 = AcceptedAssetImporter.Hash(v1Path),
                reconciliation_v2_sha256 = AcceptedAssetImporter.Hash(reconciliationPath),
                runtime_conflict_decision_v2_sha256 = AcceptedAssetImporter.Hash(decisionPath),
                correction_authority_sha256 = AcceptedAssetImporter.Hash(correctionPath)
            },
            validation = new
            {
                runtime_identity_count = rows.Count,
                duplicate_identity = rows.Count - rows.Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal).Count(),
                semantic_conflict = rows.Count(row => row.SemanticConflict != "NO"),
                mapping_suspect = rows.Count(row => row.MappingQuality != "VALID"),
                mapping_error = reconciliation.Count(row => row["reconciliation_status"] == "IDENTITY_MAPPING_ERROR"),
                unresolved_review_omission = rows.Count(row => conflictKeys.Contains(row.IdentityKey) && row.ReviewerAction != "RESOLVED")
            }
        };
        File.WriteAllText(path, JsonSerializer.Serialize(json, new JsonSerializerOptions { WriteIndented = true }) + Environment.NewLine, new UTF8Encoding(false));
    }

    private static string Escape(string value)
        => value.Contains(',') || value.Contains('"') || value.Contains('\r') || value.Contains('\n')
            ? '"' + value.Replace("\"", "\"\"") + '"' : value;

    private sealed record V2Row(string IdentityKey, string IsGeneral, string IsSpecial, string SexualIntent, string ReviewStatus,
        string RuleId, string Evidence, string Provenance, string SourceIdentityCount, string SourceIdentities,
        string RuntimeBackingCount, string MappingQuality, string ReviewerAction, string SemanticConflict)
    {
        public IEnumerable<string> Values()
        {
            yield return IdentityKey; yield return IsGeneral; yield return IsSpecial; yield return SexualIntent; yield return ReviewStatus;
            yield return RuleId; yield return Evidence; yield return Provenance; yield return SourceIdentityCount; yield return SourceIdentities;
            yield return RuntimeBackingCount; yield return MappingQuality; yield return ReviewerAction; yield return SemanticConflict;
        }
    }
}
