using System.Security.Cryptography;
using DanbooruTagTool.Core;
using Microsoft.VisualBasic.FileIO;

namespace DanbooruTagTool.Data;

/// <summary>
/// Bakes the accepted General body/theme memberships into generic catalog
/// metadata. Runtime browse uses the existing UnifiedBrowseIndex only.
/// </summary>
public static class Issue199GeneralFacetOverlay
{
    public const string RelativePath = "src/DanbooruTagTool.Data/UnifiedBrowseData/issue199_general_facets_v1.csv";
    public const int IdentityCount = 346;
    public const int AssignmentCount = 355;
    public const int BodyAssignmentCount = 247;
    public const int ThemeAssignmentCount = 108;
    public const string ExpectedSha256 = "b63b76205cb7202be9f0e613027be2761332f6aa3c1fce25f5fb5baaa1a2b026";
    private const string ResourceSuffix = "issue199_general_facets_v1.csv";

    internal sealed record Assignment(string IdentityKey, string Axis, string FacetId);

    public static CatalogEntry[] Bake(IRuntimeCatalogQuery catalog)
    {
        var assignments = ReadAssignments();
        var index = new UnifiedBrowseIndex(catalog);
        var identitiesBySourceKey = index.Identities
            .SelectMany(identity => identity.BackingEntries.Select(entry =>
                (Key: Issue118SexualIntentV2Overlay.NormalizeIdentity(entry.Canonical ?? entry.English), Identity: identity)))
            .GroupBy(row => row.Key, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.Select(row => row.Identity).DistinctBy(identity => identity.IdentityKey).ToArray(), StringComparer.Ordinal);

        var byIdentity = new Dictionary<string, (HashSet<string> Body, HashSet<string> Themes)>(StringComparer.Ordinal);
        foreach (var assignment in assignments)
        {
            var key = Issue118SexualIntentV2Overlay.NormalizeIdentity(assignment.IdentityKey);
            if (!identitiesBySourceKey.TryGetValue(key, out var resolved) || resolved.Length != 1)
                throw new InvalidDataException("Issue #199 facet identity does not resolve exactly: " + assignment.IdentityKey);
            var identity = resolved[0];
            var canonical = identity.BackingEntries
                .Select(entry => entry.Canonical ?? entry.English)
                .Distinct(StringComparer.Ordinal)
                .ToArray();
            if (canonical.Length != 1 || !string.Equals(canonical[0], assignment.IdentityKey, StringComparison.Ordinal))
                throw new InvalidDataException("Issue #199 facet identity is not the exact current canonical identity: " + assignment.IdentityKey);
            if (identity.BackingEntries.Any(entry => entry.EffectiveCategory == "Special") ||
                !identity.BackingEntries.Any(entry => entry.EffectiveCategory == "General"))
                throw new InvalidDataException("Issue #199 facet target is no longer General-only: " + assignment.IdentityKey);
            if (!identity.BrowseableDiscovery || !identity.BackingEntries.Any(entry =>
                    entry.EffectiveCategory == "General" && entry.CanBrowse &&
                    entry.BrowseClassification == BrowseClassificationStatus.Proposed))
                throw new InvalidDataException("Issue #199 facet target is not already Proposed and browseable: " + assignment.IdentityKey);

            var site = assignment.Axis == "BODY";
            var currentFacets = site ? identity.BodySiteIds : identity.ThemeIds;
            if (currentFacets.Contains(assignment.FacetId))
                throw new InvalidDataException("Issue #199 facet already exists before the overlay: " + assignment.IdentityKey + "," + assignment.FacetId);

            if (!byIdentity.TryGetValue(key, out var sets))
                sets = (new HashSet<string>(StringComparer.Ordinal), new HashSet<string>(StringComparer.Ordinal));
            (site ? sets.Body : sets.Themes).Add(assignment.FacetId);
            byIdentity[key] = sets;
        }

        return catalog.Entries.Select(entry =>
        {
            if (entry.EffectiveCategory != "General") return entry;
            var key = Issue118SexualIntentV2Overlay.NormalizeIdentity(entry.Canonical ?? entry.English);
            if (!byIdentity.TryGetValue(key, out var facets)) return entry;
            if (entry.UnifiedBrowseFacets is not null)
                throw new InvalidDataException("Issue #199 generic facets are already baked: " + entry.Canonical);
            return entry with
            {
                UnifiedBrowseFacets = new(
                    facets.Body.OrderBy(value => value, StringComparer.Ordinal).ToArray(),
                    facets.Themes.OrderBy(value => value, StringComparer.Ordinal).ToArray())
            };
        }).ToArray();
    }

    internal static IReadOnlyList<Assignment> ReadAssignments()
    {
        var assembly = typeof(Issue199GeneralFacetOverlay).Assembly;
        var name = assembly.GetManifestResourceNames()
            .SingleOrDefault(value => value.EndsWith(ResourceSuffix, StringComparison.Ordinal))
            ?? throw new InvalidDataException("Missing Issue #199 General facet asset.");
        using var resource = assembly.GetManifestResourceStream(name)
            ?? throw new InvalidDataException("Cannot open Issue #199 General facet asset.");
        using var bytes = new MemoryStream();
        resource.CopyTo(bytes);
        var content = bytes.ToArray();
        var hash = Convert.ToHexString(SHA256.HashData(content)).ToLowerInvariant();
        if (!string.Equals(hash, ExpectedSha256, StringComparison.Ordinal))
            throw new InvalidDataException("Issue #199 General facet asset hash mismatch: " + hash);

        using var stream = new MemoryStream(content, writable: false);
        using var parser = new TextFieldParser(stream, System.Text.Encoding.UTF8)
        {
            TextFieldType = FieldType.Delimited,
            HasFieldsEnclosedInQuotes = true,
            TrimWhiteSpace = false
        };
        parser.SetDelimiters(",");
        var header = parser.ReadFields() ?? throw new InvalidDataException("Empty Issue #199 General facet asset.");
        if (!header.SequenceEqual(["identity_key", "axis", "facet_id"], StringComparer.Ordinal))
            throw new InvalidDataException("Issue #199 General facet asset must contain identity_key,axis,facet_id.");

        var assignments = new List<Assignment>();
        while (!parser.EndOfData)
        {
            var values = parser.ReadFields() ?? [];
            if (values.Length != 3 || values.Any(string.IsNullOrWhiteSpace))
                throw new InvalidDataException("Issue #199 General facet asset has an invalid row.");
            assignments.Add(new(values[0], values[1], values[2]));
        }

        var bodyIds = SpecialBrowseV2Taxonomy.BodySites.Select(item => item.Id).ToHashSet(StringComparer.Ordinal);
        var themeIds = SpecialBrowseV2Taxonomy.Themes.Select(item => item.Id).ToHashSet(StringComparer.Ordinal);
        if (assignments.Count != AssignmentCount || assignments.Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal).Count() != IdentityCount)
            throw new InvalidDataException("Issue #199 General facet asset identity/assignment count drift.");
        if (assignments.Count(row => row.Axis == "BODY") != BodyAssignmentCount ||
            assignments.Count(row => row.Axis == "THEME") != ThemeAssignmentCount)
            throw new InvalidDataException("Issue #199 General facet asset axis count drift.");
        if (assignments.Select(row => (row.IdentityKey, row.Axis, row.FacetId)).Distinct().Count() != assignments.Count)
            throw new InvalidDataException("Issue #199 General facet asset contains duplicate identity/axis/facet rows.");
        if (assignments.Any(row => row.Axis switch
            {
                "BODY" => !bodyIds.Contains(row.FacetId),
                "THEME" => !themeIds.Contains(row.FacetId),
                _ => true
            }))
            throw new InvalidDataException("Issue #199 General facet asset contains an invalid axis or #76 facet ID.");

        var sorted = assignments.OrderBy(row => row.IdentityKey, StringComparer.Ordinal)
            .ThenBy(row => row.Axis, StringComparer.Ordinal)
            .ThenBy(row => row.FacetId, StringComparer.Ordinal).ToArray();
        if (!assignments.SequenceEqual(sorted))
            throw new InvalidDataException("Issue #199 General facet asset is not deterministically sorted.");
        return assignments;
    }
}
