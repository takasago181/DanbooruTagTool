using System.IO;
using System.Globalization;
using System.Reflection;
using Microsoft.VisualBasic.FileIO;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>
/// Adds the accepted Issue #132 secondary browse memberships during catalog
/// construction. The resulting routes still flow through UnifiedBrowseIndex.
/// </summary>
public static class Issue132RouteOverlay
{
    private const string ResourceSuffix = "issue132_secondary_routes_v1.csv";
    private const string CandidateInputSha256 = "a2d05d872430fb0aaffbe93953bbfc4a27e35def5297322edbb383bf6a895e64";
    private const int ExpectedPairs = 274;
    private const int ExpectedIdentities = 273;

    internal sealed record Addition(string IdentityKey, string RouteId);

    public static CatalogEntry[] Bake(IRuntimeCatalogQuery catalog)
    {
        var additions = ReadAdditions();
        var ordinary = catalog.Entries
            .Where(entry => entry.EffectiveCategory is "General" or "Special")
            .ToArray();

        var index = new UnifiedBrowseIndex(catalog);
        var identitiesBySourceKey = index.Identities
            .SelectMany(identity => identity.BackingEntries.Select(entry =>
                (Key: Issue118SexualIntentOverlay.NormalizeIdentity(entry.Canonical ?? entry.English), Identity: identity)))
            .GroupBy(row => row.Key, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.Select(row => row.Identity).DistinctBy(identity => identity.IdentityKey).ToArray(), StringComparer.Ordinal);

        var additionsByIdentity = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
        foreach (var addition in additions)
        {
            var key = Issue118SexualIntentOverlay.NormalizeIdentity(addition.IdentityKey);
            if (!identitiesBySourceKey.TryGetValue(key, out var resolved) || resolved.Length != 1)
                throw new InvalidDataException("Issue #132 overlay identity does not resolve exactly: " + addition.IdentityKey);
            var identity = resolved[0];
            if (!identity.BrowseableDiscovery)
                throw new InvalidDataException("Issue #132 overlay target is not already browseable: " + addition.IdentityKey);
            if (identity.RouteIds.Contains(addition.RouteId))
                throw new InvalidDataException("Issue #132 overlay route already exists: " + addition.IdentityKey + "," + addition.RouteId);

            if (!additionsByIdentity.TryGetValue(key, out var routes))
                additionsByIdentity[key] = routes = new(StringComparer.Ordinal);
            routes.Add(addition.RouteId);
        }

        var ordinaryKeys = ordinary
            .Select(entry => Issue118SexualIntentOverlay.NormalizeIdentity(entry.Canonical ?? entry.English))
            .ToHashSet(StringComparer.Ordinal);
        if (additionsByIdentity.Keys.Any(key => !ordinaryKeys.Contains(key)))
            throw new InvalidDataException("Issue #132 overlay contains an identity outside the ordinary catalog.");

        return catalog.Entries.Select(entry =>
        {
            if (entry.EffectiveCategory is not ("General" or "Special"))
                return entry;
            var key = Issue118SexualIntentOverlay.NormalizeIdentity(entry.Canonical ?? entry.English);
            if (!additionsByIdentity.TryGetValue(key, out var routeIds)) return entry;
            var merged = entry.UnifiedBrowseRouteIds.ToHashSet(StringComparer.Ordinal);
            merged.UnionWith(routeIds);
            return entry with
            {
                UnifiedBrowseRouteIds = merged.OrderBy(route => route, StringComparer.Ordinal).ToArray()
            };
        }).ToArray();
    }

    internal static IReadOnlyList<Addition> ReadAdditions()
    {
        var assembly = typeof(Issue132RouteOverlay).Assembly;
        var name = assembly.GetManifestResourceNames()
            .SingleOrDefault(value => value.EndsWith(ResourceSuffix, StringComparison.Ordinal))
            ?? throw new InvalidDataException("Missing Issue #132 secondary route asset.");
        using var resource = assembly.GetManifestResourceStream(name)
            ?? throw new InvalidDataException("Cannot open Issue #132 secondary route asset.");
        using var bytes = new MemoryStream();
        resource.CopyTo(bytes);
        var content = bytes.ToArray();
        var sha256 = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(content)).ToLowerInvariant();
        if (sha256 != CandidateInputSha256)
            throw new InvalidDataException("Issue #132 candidate asset SHA-256 does not match the accepted reconciliation input.");
        using var stream = new MemoryStream(content, writable: false);
        using var parser = new TextFieldParser(stream, System.Text.Encoding.UTF8)
        {
            TextFieldType = FieldType.Delimited,
            HasFieldsEnclosedInQuotes = true,
            TrimWhiteSpace = false
        };
        parser.SetDelimiters(",");
        var header = parser.ReadFields() ?? throw new InvalidDataException("Empty Issue #132 route asset.");
        if (!header.SequenceEqual(["identity_key", "route_id"], StringComparer.Ordinal))
            throw new InvalidDataException("Issue #132 route asset must contain only identity_key,route_id.");

        var additions = new List<Addition>();
        while (!parser.EndOfData)
        {
            var values = parser.ReadFields() ?? [];
            if (values.Length != 2 || values.Any(string.IsNullOrWhiteSpace))
                throw new InvalidDataException("Issue #132 route asset has an invalid row.");
            additions.Add(new(values[0], values[1]));
        }

        var validRoutes = UnifiedBrowseTaxonomy.Routes.Select(route => route.Id).ToHashSet(StringComparer.Ordinal);
        if (additions.Count != ExpectedPairs ||
            additions.Select(row => Issue118SexualIntentOverlay.NormalizeIdentity(row.IdentityKey)).Distinct(StringComparer.Ordinal).Count() != ExpectedIdentities ||
            additions.Select(row => (Issue118SexualIntentOverlay.NormalizeIdentity(row.IdentityKey), row.RouteId)).Distinct().Count() != ExpectedPairs)
            throw new InvalidDataException("Issue #132 route asset must contain exactly 274 unique pairs across 273 identities.");
        if (additions.Any(row => !validRoutes.Contains(row.RouteId)))
            throw new InvalidDataException("Issue #132 route asset contains an unknown Unified route.");

        var sorted = additions.OrderBy(row => row.IdentityKey, StringComparer.Ordinal)
            .ThenBy(row => row.RouteId, StringComparer.Ordinal).ToArray();
        if (!additions.SequenceEqual(sorted))
            throw new InvalidDataException("Issue #132 route asset is not deterministically sorted.");
        return additions;
    }
}
