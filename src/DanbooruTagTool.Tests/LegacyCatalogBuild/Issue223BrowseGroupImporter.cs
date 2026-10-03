using System.IO;
using System.Globalization;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>Build-time importer; research and CSV never read during startup.</summary>
public static class Issue223BrowseGroupImporter
{
    public const string GroupsPath = "src/DanbooruTagTool.Tests/LegacyCatalogBuild/Inputs/docs/issue223/BROWSE_GROUPS_V1.csv";
    public const string MembersPath = "src/DanbooruTagTool.Tests/LegacyCatalogBuild/Inputs/docs/issue223/BROWSE_GROUP_MEMBERS_V1.csv";
    public const string GroupsSha256 = "441faa745e5e2d783855c37342508f3597a4fb97cdec1440a7f9e29ae809035f";
    public const string MembersSha256 = "4c59c44b6c74d221b569815bdf3829d4cba2743cd3fada3c923789bdf2d7e715";

    public static CatalogEntry[] Apply(string groupsPath, string membersPath, CatalogEntry[] entries)
    {
        if (AcceptedAssetImporter.Hash(groupsPath) != GroupsSha256 || AcceptedAssetImporter.Hash(membersPath) != MembersSha256)
            throw new InvalidDataException("Issue223 Browse Group asset hash mismatch");
        return ApplyRows(AcceptedAssetImporter.Csv(groupsPath), AcceptedAssetImporter.Csv(membersPath), entries);
    }

    internal static CatalogEntry[] ApplyRows(IEnumerable<Dictionary<string, string>> groups,
        IEnumerable<Dictionary<string, string>> members, CatalogEntry[] entries)
    {
        var roots = entries.Where(e => e.EffectiveCategory == "Copyright").Select(e => e.Canonical!).ToHashSet(StringComparer.Ordinal);
        var characters = entries.Where(e => e.EffectiveCategory == "Character").ToDictionary(e => e.Canonical!, StringComparer.Ordinal);
        var definitions = new Dictionary<(string Home, string Id), CharacterBrowseGroup>();
        foreach (var row in groups)
        {
            var group = new CharacterBrowseGroup(row["home_copyright"], row["group_id"], row["group_label_ja"],
                int.Parse(row["sort_order"], CultureInfo.InvariantCulture));
            if (!roots.Contains(group.HomeCopyright) || string.IsNullOrWhiteSpace(group.Id) || group.Id == CharacterBrowseGroups.OtherId
                || string.IsNullOrWhiteSpace(group.Label) || group.SortOrder < 0 || !definitions.TryAdd((group.HomeCopyright, group.Id), group))
                throw new InvalidDataException("Invalid Browse Group definition: " + group.Id);
        }
        var mappings = new Dictionary<string, CharacterBrowseGroup>(StringComparer.Ordinal);
        foreach (var row in members)
        {
            var character = row["character_canonical"];
            if (row["review_status"] != "REVIEWED" || string.IsNullOrWhiteSpace(row["evidence_kind"]) || string.IsNullOrWhiteSpace(row["evidence_ref"])
                || !definitions.TryGetValue((row["home_copyright"], row["group_id"]), out var group)
                || !characters.TryGetValue(character, out var entry) || entry.EffectiveBrowseHome != group.HomeCopyright
                || entry.BrowseGroup is not null || !mappings.TryAdd(character, group))
                throw new InvalidDataException("Invalid Browse Group member: " + character);
        }
        if (definitions.Keys.Any(key => !mappings.Values.Any(g => (g.HomeCopyright, g.Id) == key)))
            throw new InvalidDataException("Empty reviewed Browse Group");
        return entries.Select(e => e.EffectiveCategory == "Character" && mappings.TryGetValue(e.Canonical!, out var group)
            ? e with { BrowseGroup = group } : e).ToArray();
    }
}
