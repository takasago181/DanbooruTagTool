using System.Globalization;
using System.IO;
using System.Text;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue118RuntimeConflictReviewTests(ITestOutputHelper output)
{
    [ProductionFact]
    public void ConflictReviewIsCompleteAndMaterializesRuntimeIdentityRows()
    {
        var authorityRoot = Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT")!;
        var conflictPath = Path.Combine(authorityRoot, "docs/issue118/runtime_identity_conflicts_v1.csv");
        var decisionPath = Path.Combine(authorityRoot, "docs/issue118/runtime_identity_conflict_review_decisions_v1.csv");
        var outputPath = Path.Combine(authorityRoot, "docs/issue118/runtime_identity_conflict_review_v1.csv");

        var conflicts = AcceptedAssetImporter.Csv(conflictPath);
        var conflictGroups = conflicts
            .GroupBy(row => row["runtime_identity"], StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal);
        var decisions = AcceptedAssetImporter.Csv(decisionPath)
            .ToDictionary(row => row["runtime_identity"], StringComparer.Ordinal);

        Assert.Equal(116, conflictGroups.Count);
        Assert.Equal(116, decisions.Count);
        Assert.Equal(
            conflictGroups.Keys.OrderBy(value => value, StringComparer.Ordinal),
            decisions.Keys.OrderBy(value => value, StringComparer.Ordinal));

        var reviewed = conflictGroups.Select(pair => Build(pair.Key, pair.Value, decisions[pair.Key])).OrderBy(row => row.RuntimeIdentity, StringComparer.Ordinal).ToArray();
        Assert.Equal(116, reviewed.Length);
        Assert.Equal(116, reviewed.Select(row => row.RuntimeIdentity).Distinct(StringComparer.Ordinal).Count());
        Assert.DoesNotContain(reviewed, row => row.ReviewerAction == "RESOLVED" && row.MappingQuality != "VALID");
        Assert.DoesNotContain(reviewed, row => row.ReviewerAction == "NEEDS_CANONICAL_FIX" && row.MappingQuality != "SUSPECT");
        Assert.All(reviewed, row => Assert.False(string.IsNullOrWhiteSpace(row.ReviewReason)));
        Assert.Equal(11, reviewed.Count(row => row.ReviewerAction == "NEEDS_CANONICAL_FIX"));

        WriteCsv(outputPath, reviewed);

        output.WriteLine($"Reviewed runtime conflict groups: {reviewed.Length}");
        output.WriteLine("Final intent counts: " + string.Join(", ", reviewed.GroupBy(row => row.FinalSexualIntent.Length == 0 ? "UNCLASSIFIED" : row.FinalSexualIntent).OrderBy(group => group.Key).Select(group => $"{group.Key}={group.Count()}")));
        output.WriteLine("Reviewer actions: " + string.Join(", ", reviewed.GroupBy(row => row.ReviewerAction).OrderBy(group => group.Key).Select(group => $"{group.Key}={group.Count()}")));
        output.WriteLine("Mapping quality: " + string.Join(", ", reviewed.GroupBy(row => row.MappingQuality).OrderBy(group => group.Key).Select(group => $"{group.Key}={group.Count()}")));
    }

    private static ReviewRow Build(string runtimeIdentity, IReadOnlyList<IReadOnlyDictionary<string, string>> sourceRows, IReadOnlyDictionary<string, string> decision)
    {
        var first = sourceRows[0];
        var sourceIdentities = sourceRows.Select(row => row["source_identity"]).Distinct(StringComparer.Ordinal).OrderBy(value => value, StringComparer.Ordinal).ToArray();
        var backingCount = int.Parse(first["runtime_backing_count"], CultureInfo.InvariantCulture);
        return new(
            runtimeIdentity,
            first["runtime_is_general"],
            first["runtime_is_special"],
            sourceIdentities.Length.ToString(CultureInfo.InvariantCulture),
            string.Join("|", sourceIdentities),
            JoinSpecialIds(sourceRows.SelectMany(row => Split(row["special_ids"]))),
            Join(sourceRows.SelectMany(row => Split(row["special_tags"]))),
            Join(sourceRows.SelectMany(row => Split(row["chosen_canonical_tags"]))),
            Join(sourceRows.SelectMany(row => Split(row["semantic_classes"]))),
            decision["final_sexual_intent"],
            decision["final_review_status"],
            decision["review_reason"],
            decision["mapping_quality"],
            decision["reviewer_action"]);
    }

    private static string[] Split(string value)
        => value.Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

    private static string Join(IEnumerable<string> values)
        => string.Join("|", values.Where(value => value.Length > 0).Distinct(StringComparer.Ordinal).OrderBy(value => value, StringComparer.Ordinal));

    private static string JoinSpecialIds(IEnumerable<string> values)
        => string.Join("|", values.Where(value => value.Length > 0).Select(value => int.Parse(value, CultureInfo.InvariantCulture)).Distinct().OrderBy(value => value).Select(value => value.ToString(CultureInfo.InvariantCulture)));

    private static void WriteCsv(string path, IReadOnlyList<ReviewRow> rows)
    {
        var fields = new[]
        {
            "runtime_identity", "runtime_is_general", "runtime_is_special", "source_identity_count", "source_identities",
            "special_ids", "special_tags", "chosen_canonical_tags", "old_semantic_classes", "final_sexual_intent",
            "final_review_status", "review_reason", "mapping_quality", "reviewer_action"
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

    private sealed record ReviewRow(
        string RuntimeIdentity,
        string RuntimeIsGeneral,
        string RuntimeIsSpecial,
        string SourceIdentityCount,
        string SourceIdentities,
        string SpecialIds,
        string SpecialTags,
        string ChosenCanonicalTags,
        string OldSemanticClasses,
        string FinalSexualIntent,
        string FinalReviewStatus,
        string ReviewReason,
        string MappingQuality,
        string ReviewerAction)
    {
        public IEnumerable<string> Values()
        {
            yield return RuntimeIdentity; yield return RuntimeIsGeneral; yield return RuntimeIsSpecial; yield return SourceIdentityCount; yield return SourceIdentities;
            yield return SpecialIds; yield return SpecialTags; yield return ChosenCanonicalTags; yield return OldSemanticClasses; yield return FinalSexualIntent;
            yield return FinalReviewStatus; yield return ReviewReason; yield return MappingQuality; yield return ReviewerAction;
        }
    }
}
