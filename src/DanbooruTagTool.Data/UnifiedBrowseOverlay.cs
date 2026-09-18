using System.Globalization;
using System.Reflection;
using DanbooruTagTool.Core;
using Microsoft.VisualBasic.FileIO;

namespace DanbooruTagTool.Data;

/// <summary>
/// Bakes only the Special route enrichments that cannot be recovered from the
/// already-baked #76 kind/body/theme metadata at normal runtime.
/// </summary>
public static class UnifiedBrowseOverlay
{
    private const string OverrideResourceSuffix = "special_route_overrides_v1.csv";

    public static CatalogEntry[] Bake(ICatalog catalog, string authorityRoot)
    {
        var profilePath = Path.Combine(authorityRoot, AcceptedAssetImporter.ProductionProfileRelativePath);
        if (!File.Exists(profilePath)) throw new FileNotFoundException("Missing accepted Special generation profile.", profilePath);
        var profile = AcceptedAssetImporter.Csv(profilePath)
            .ToDictionary(row => int.Parse(row["SpecialID"], CultureInfo.InvariantCulture));

        var overrides = ReadOverrides();
        ValidateOverrides(catalog, overrides);

        var overrideById = overrides.GroupBy(row => row.SpecialId)
            .ToDictionary(group => group.Key, group => group.ToArray());

        return catalog.Entries.Select(entry =>
        {
            if (!entry.IsSpecial) return entry;
            var id = ParseSpecialId(entry.Id);
            var routes = entry.UnifiedBrowseRouteIds.ToHashSet(StringComparer.Ordinal);
            if (profile.TryGetValue(id, out var row))
            {
                var family = row["GenerationFamily"];
                var role = row["CompositionRoleOverride"];
                if (family == "POSE_COMPOSITION" && role == "pose") routes.Add("POSE_POSITION");
                else if (family == "POSE_COMPOSITION" && role == "camera") routes.Add("COMPOSITION_CAMERA");
                else if (family == "SCENE_CONTEXT") routes.Add("SCENE_BACKGROUND");
            }
            if (overrideById.TryGetValue(id, out var additions))
                foreach (var addition in additions) routes.Add(addition.RouteId);
            return entry with { UnifiedBrowseRouteIds = routes.OrderBy(value => value, StringComparer.Ordinal).ToArray() };
        }).ToArray();
    }

    private sealed record Override(int SpecialId, string Canonical, string RouteId, string Mode, string Rationale);

    private static IReadOnlyList<Override> ReadOverrides()
    {
        var assembly = typeof(UnifiedBrowseOverlay).Assembly;
        var name = assembly.GetManifestResourceNames().SingleOrDefault(value => value.EndsWith(OverrideResourceSuffix, StringComparison.Ordinal))
            ?? throw new InvalidDataException("Missing unified browse override resource.");
        using var stream = assembly.GetManifestResourceStream(name) ?? throw new InvalidDataException("Cannot open unified browse override resource.");
        using var parser = new TextFieldParser(stream, System.Text.Encoding.UTF8)
        {
            TextFieldType = FieldType.Delimited,
            HasFieldsEnclosedInQuotes = true,
            TrimWhiteSpace = false
        };
        parser.SetDelimiters(",");
        var header = parser.ReadFields() ?? throw new InvalidDataException("Empty unified browse override resource.");
        var result = new List<Override>();
        while (!parser.EndOfData)
        {
            var values = parser.ReadFields() ?? [];
            if (values.Length != header.Length) throw new InvalidDataException("Unified browse override column mismatch.");
            var row = header.Zip(values).ToDictionary(pair => pair.First, pair => pair.Second);
            result.Add(new(
                int.Parse(row["special_id"], CultureInfo.InvariantCulture),
                row["canonical"],
                row["route_id"],
                row["mode"],
                row["rationale"]));
        }
        if (result.Count != 6 || result.Select(row => row.SpecialId).Distinct().Count() != 6)
            throw new InvalidDataException("Unified browse override asset must contain exactly six unique Special IDs.");
        return result;
    }

    private static void ValidateOverrides(ICatalog catalog, IReadOnlyList<Override> overrides)
    {
        var byId = catalog.Entries.Where(entry => entry.IsSpecial)
            .ToDictionary(entry => ParseSpecialId(entry.Id));
        var validRoutes = UnifiedBrowseTaxonomy.Routes.Select(route => route.Id).ToHashSet(StringComparer.Ordinal);
        foreach (var row in overrides)
        {
            if (!byId.TryGetValue(row.SpecialId, out var entry))
                throw new InvalidDataException("Unified browse override references missing Special ID: " + row.SpecialId);
            var actual = Issue118SexualIntentOverlay.NormalizeIdentity(entry.Canonical ?? entry.English);
            var expected = Issue118SexualIntentOverlay.NormalizeIdentity(row.Canonical);
            if (actual != expected)
                throw new InvalidDataException($"Unified browse override identity mismatch at {row.SpecialId}: {actual} != {expected}");
            if (row.Mode != "ADD_SECONDARY" || !validRoutes.Contains(row.RouteId))
                throw new InvalidDataException("Invalid unified browse override mode/route at " + row.SpecialId);
        }
    }

    private static int ParseSpecialId(string catalogId)
        => catalogId.StartsWith("S:", StringComparison.Ordinal) && int.TryParse(catalogId.AsSpan(2), out var id)
            ? id : throw new InvalidDataException("Invalid Special catalog id: " + catalogId);
}
