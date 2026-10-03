using System.IO;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>Build-time projection only. Never reads research inputs during startup.</summary>
public static class Issue216BrowseHomeImporter
{
    public const string RelativePath = "src/DanbooruTagTool.Tests/LegacyCatalogBuild/Inputs/docs/issue216/BROWSE_HOME_RUNTIME_V1.csv";
    public const string ExpectedSha256 = "51a5099d422a4aa8acb0e8eddd14ccf4a9a42d9efa93a30f645b0a97d877ab95";

    public static CatalogEntry[] Apply(string path, CatalogEntry[] entries)
    {
        if (AcceptedAssetImporter.Hash(path) != ExpectedSha256)
            throw new InvalidDataException("Issue216 Browse HOME projection hash mismatch");
        var characters = entries.Where(e => e.EffectiveCategory == "Character").ToDictionary(e => e.Canonical!);
        var roots = entries.Where(e => e.EffectiveCategory == "Copyright").Select(e => e.Canonical!).ToHashSet();
        var mappings = new Dictionary<string, (string? Formal, string? Reviewed)>(StringComparer.Ordinal);
        foreach (var row in AcceptedAssetImporter.Csv(path))
        {
            var character = row["character"];
            string? formal = row["formal_home"].Length == 0 ? null : row["formal_home"];
            string? reviewed = row["reviewed_home"].Length == 0 ? null : row["reviewed_home"];
            if (!characters.ContainsKey(character) || (formal is null) == (reviewed is null)
                || !roots.Contains(formal ?? reviewed!) || !mappings.TryAdd(character, (formal, reviewed)))
                throw new InvalidDataException("Invalid Issue216 Browse HOME mapping: " + character);
        }
        return entries.Select(e => e.EffectiveCategory == "Character" && mappings.TryGetValue(e.Canonical!, out var home)
            ? e with { FormalHomeCopyright = home.Formal, ReviewedBrowseHome = home.Reviewed } : e).ToArray();
    }
}
