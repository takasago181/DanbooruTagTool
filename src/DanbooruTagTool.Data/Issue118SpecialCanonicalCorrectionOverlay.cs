using System.Globalization;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

public sealed record SpecialCanonicalCorrection(
    int SpecialId,
    string SpecialTag,
    string OldCanonical,
    string NewCanonical,
    string Decision,
    string Reason,
    string Source);

/// <summary>
/// Applies the bounded Issue #118 mapping corrections without changing the
/// protected linkage. Discovery canonical identity and Prompt output token are
/// intentionally kept separate for NO_SAFE_CANONICAL rows.
/// </summary>
public static class Issue118SpecialCanonicalCorrectionOverlay
{
    public const string RelativePath = "docs/issue118/special_canonical_corrections_v1.csv";
    public const string AcceptedSha256 = "c82e2428669cf8db2b4727ac053fe34f305e6190be57ee01baf3a35a8b655a46";

    private static readonly int[] AffectedIds =
    [550, 722, 725, 783, 1251, 1252, 1253, 1254, 1255, 1256, 1361, 1421, 1422, 1502,
        1575, 1576, 1787, 2528, 2529, 2530, 2531, 2537, 2546, 2634, 2635];

    public static IReadOnlyDictionary<int, SpecialCanonicalCorrection> Read(
        string path,
        IReadOnlyDictionary<string, Dictionary<string, string>> source,
        IReadOnlyDictionary<string, Dictionary<string, string>> linkage,
        IReadOnlyDictionary<string, long> canonical)
    {
        var rows = AcceptedAssetImporter.Csv(path);
        var corrections = new Dictionary<int, SpecialCanonicalCorrection>();
        foreach (var row in rows)
        {
            var id = int.Parse(row["special_id"], CultureInfo.InvariantCulture);
            if (!corrections.TryAdd(id, new(
                    id, row["special_tag"], row["old_canonical"], row["new_canonical"], row["decision"], row["reason"], row["source"])))
                throw new InvalidDataException("Issue #118 correction authority has duplicate Special ID: " + id);
        }

        if (!corrections.Keys.ToHashSet().SetEquals(AffectedIds))
            throw new InvalidDataException("Issue #118 correction authority affected-ID set drift.");

        foreach (var correction in corrections.Values)
        {
            var key = correction.SpecialId.ToString(CultureInfo.InvariantCulture);
            if (!source.TryGetValue(key, out var sourceRow) || !linkage.TryGetValue(key, out var linkageRow))
                throw new InvalidDataException("Issue #118 correction references missing Special ID: " + correction.SpecialId);
            if (correction.SpecialTag != sourceRow["Tag"])
                throw new InvalidDataException("Issue #118 correction Special tag mismatch: " + correction.SpecialId);
            if (correction.OldCanonical != linkageRow["ChosenCanonicalTag"])
                throw new InvalidDataException("Issue #118 correction old canonical mismatch: " + correction.SpecialId);
            if (correction.Decision is not ("EXACT_CANONICAL" or "ORIGINAL_IS_CANONICAL" or "NO_SAFE_CANONICAL"))
                throw new InvalidDataException("Issue #118 correction has unresolved decision: " + correction.SpecialId);
            if (correction.Decision == "NO_SAFE_CANONICAL")
            {
                if (correction.NewCanonical.Length != 0) throw new InvalidDataException("NO_SAFE_CANONICAL has a target: " + correction.SpecialId);
            }
            else
            {
                if (correction.NewCanonical.Length == 0 || !canonical.ContainsKey(correction.NewCanonical))
                    throw new InvalidDataException("Issue #118 correction target is not a current canonical: " + correction.SpecialId);
                if (correction.Decision == "ORIGINAL_IS_CANONICAL" &&
                    NormalizePromptToken(correction.SpecialTag) != correction.NewCanonical)
                    throw new InvalidDataException("ORIGINAL_IS_CANONICAL does not normalize to its target: " + correction.SpecialId);
            }
            if (string.IsNullOrWhiteSpace(correction.Reason) || string.IsNullOrWhiteSpace(correction.Source))
                throw new InvalidDataException("Issue #118 correction rationale/source is incomplete: " + correction.SpecialId);
        }

        return corrections;
    }

    public static string NormalizePromptToken(string specialTag)
        => Issue118SexualIntentOverlay.NormalizeIdentity(specialTag);
}
