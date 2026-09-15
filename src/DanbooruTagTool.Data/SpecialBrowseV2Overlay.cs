using DanbooruTagTool.Core;
using Microsoft.VisualBasic.FileIO;

namespace DanbooruTagTool.Data;

/// <summary>
/// Builds the accepted Issue #76 v2 browse index from the current production
/// Special v1 paths plus the bounded audited correction tables. The production
/// catalog remains immutable; this overlay affects browse discovery only.
/// </summary>
public static class SpecialBrowseV2Overlay
{
    private static readonly Dictionary<string, string> TypeMap = new(StringComparer.Ordinal)
    {
        ["BODY_ANATOMY"] = "BODY_STATE",
        ["NUDITY_CLOTHING_EXPOSURE"] = "CLOTHING_EXPOSURE",
        ["POSE_POSITION_COMPOSITION"] = "POSE_SCENE",
        ["SEXUAL_ACTIVITY_STIMULATION"] = "ACTION_CONTACT",
        ["CONTACT_INSERTION_BODY_SITE"] = "ACTION_CONTACT",
        ["TOOLS_TOYS_MACHINES"] = "TOOL_OBJECT",
        ["FLUID_EXCRETION_SOILING"] = "FLUID_EXCRETION",
        ["NONHUMAN_TENTACLE_TRANSFORMATION"] = "NONHUMAN_TRANSFORMATION",
        ["PERSON_RELATION_ROLE"] = "PERSON_RELATION",
        ["SITUATION_SCENE"] = "POSE_SCENE",
        ["META_RATING"] = "META_EXPRESSION"
    };

    private static readonly Dictionary<string, string> BdsmFallback = new(StringComparer.Ordinal)
    {
        [""] = "ACTION_CONTACT",
        ["BONDAGE_STATE"] = "ACTION_CONTACT",
        ["BONDAGE_POSITION"] = "POSE_SCENE",
        ["RESTRAINT_DEVICE"] = "TOOL_OBJECT",
        ["GAG_MOUTH_RESTRAINT"] = "TOOL_OBJECT",
        ["CHASTITY_CONTROL"] = "TOOL_OBJECT",
        ["PAIN_TORTURE"] = "ACTION_CONTACT",
        ["DOMINATION_SUBMISSION"] = "PERSON_RELATION",
        ["FORCE_NONCONSENT"] = "ACTION_CONTACT"
    };

    private static readonly Dictionary<string, string> KindJa = SpecialBrowseV2Taxonomy.Kinds
        .ToDictionary(x => x.Label, x => x.Id, StringComparer.Ordinal);
    private static readonly Dictionary<string, string> BodyJa = SpecialBrowseV2Taxonomy.BodySites
        .ToDictionary(x => x.Label, x => x.Id, StringComparer.Ordinal);

    private sealed class Working
    {
        public required string CatalogId { get; init; }
        public string? Canonical { get; init; }
        public string? KindId { get; set; }
        public HashSet<string> Body { get; set; } = new(StringComparer.Ordinal);
        public HashSet<string> Themes { get; set; } = new(StringComparer.Ordinal);
        public SpecialBrowseV2Status Status { get; set; } = SpecialBrowseV2Status.AutoCandidate;
    }

    public static SpecialBrowseV2Index Load(ICatalog catalog)
    {
        var specials = catalog.Entries.Where(entry => entry.IsSpecial)
            .OrderBy(entry => ParseSpecialId(entry.Id)).ToArray();
        if (specials.Length != 2788 || specials.Select(entry => ParseSpecialId(entry.Id)).SequenceEqual(Enumerable.Range(1, 2788)) == false)
            throw new InvalidDataException("Special v2 overlay requires exact Special IDs 1..2788");

        var rows = specials.ToDictionary(entry => ParseSpecialId(entry.Id), DeriveBase);
        ApplyChastity(rows);
        ApplyFormerUnresolved(rows);
        ApplyPracticalKnowledgePatch(rows);
        Validate(rows);

        return new SpecialBrowseV2Index(rows.OrderBy(pair => pair.Key).Select(pair => new SpecialBrowseV2Entry(
            pair.Value.CatalogId,
            pair.Value.KindId,
            pair.Value.Body,
            pair.Value.Themes,
            pair.Value.Status,
            pair.Value.Canonical)));
    }

    /// <summary>
    /// Explicit catalog-build boundary. Evidence CSVs are parsed here only,
    /// then the accepted mapping is persisted inside each Special catalog row.
    /// Normal application startup must use <see cref="FromCatalog"/> instead.
    /// </summary>
    public static CatalogEntry[] Bake(ICatalog catalog)
    {
        var index = Load(catalog);
        var byId = index.Entries.ToDictionary(entry => entry.CatalogId, StringComparer.Ordinal);
        return catalog.Entries.Select(entry =>
        {
            if (!entry.IsSpecial || !byId.TryGetValue(entry.Id, out var mapped)) return entry;
            return entry with
            {
                SpecialBrowseV2 = new SpecialBrowseV2Classification(
                    mapped.KindId,
                    mapped.BodySiteIds.OrderBy(value => value, StringComparer.Ordinal).ToArray(),
                    mapped.ThemeIds.OrderBy(value => value, StringComparer.Ordinal).ToArray(),
                    mapped.Status)
            };
        }).ToArray();
    }

    /// <summary>
    /// Runtime catalog boundary. This reads only precomputed classifications
    /// serialized in catalog.db; it never parses Issue #76 evidence CSVs.
    /// </summary>
    public static SpecialBrowseV2Index FromCatalog(ICatalog catalog)
    {
        var specials = catalog.Entries.Where(entry => entry.IsSpecial).ToArray();
        if (specials.Length == 0) return new SpecialBrowseV2Index([]);
        if (specials.Any(entry => entry.SpecialBrowseV2 is null))
            throw new InvalidDataException("Catalog is missing baked Special v2 browse data; run an explicit catalog build.");

        return new SpecialBrowseV2Index(specials.Select(entry => new SpecialBrowseV2Entry(
            entry.Id,
            entry.SpecialBrowseV2!.KindId,
            entry.SpecialBrowseV2.BodySiteIds.ToHashSet(StringComparer.Ordinal),
            entry.SpecialBrowseV2.ThemeIds.ToHashSet(StringComparer.Ordinal),
            entry.SpecialBrowseV2.Status,
            entry.Canonical)));
    }

    private static Working DeriveBase(CatalogEntry entry)
    {
        var paths = entry.Paths;
        var primary = paths.FirstOrDefault();
        var working = new Working { CatalogId = entry.Id, Canonical = entry.Canonical };
        if (primary != null) working.KindId = DeriveKind(primary, paths.Skip(1));

        foreach (var path in paths)
        {
            var body = BodyFacet(path);
            if (body != null) working.Body.Add(body);
            var theme = ThemeFacet(path.GenreId);
            if (theme != null) working.Themes.Add(theme);
        }
        return working;
    }

    private static string? DeriveKind(BrowsePath primary, IEnumerable<BrowsePath> secondary)
    {
        if (TypeMap.TryGetValue(primary.GenreId, out var direct)) return direct;
        if (primary.GenreId == "BONDAGE_BDSM_DOMINATION")
            return BdsmFallback.GetValueOrDefault(primary.SubgenreId, "ACTION_CONTACT");
        if (primary.GenreId == "REPRODUCTION_PREGNANCY_LACTATION")
        {
            var types = secondary.Select(path => TypeMap.GetValueOrDefault(path.GenreId)).Where(value => value != null).ToHashSet(StringComparer.Ordinal);
            foreach (var preferred in new[] { "CLOTHING_EXPOSURE", "ACTION_CONTACT", "BODY_STATE" }) if (types.Contains(preferred)) return preferred;
            return "BODY_STATE";
        }
        if (primary.GenreId == "INJURY_R18G")
        {
            var types = secondary.Select(path => TypeMap.GetValueOrDefault(path.GenreId)).Where(value => value != null).ToHashSet(StringComparer.Ordinal);
            foreach (var preferred in new[] { "ACTION_CONTACT", "FLUID_EXCRETION", "PERSON_RELATION", "BODY_STATE" }) if (types.Contains(preferred)) return preferred;
            return "BODY_STATE";
        }
        return null;
    }

    private static string? BodyFacet(BrowsePath path) => (path.GenreId, path.SubgenreId) switch
    {
        ("BODY_ANATOMY", "BREAST_NIPPLE") => "BREAST_NIPPLE",
        ("BODY_ANATOMY", "FEMALE_GENITAL") => "FEMALE_GENITAL",
        ("BODY_ANATOMY", "MALE_GENITAL") => "MALE_GENITAL",
        ("BODY_ANATOMY", "BUTTOCK_ANUS") => "BUTTOCK_ANAL",
        ("CONTACT_INSERTION_BODY_SITE", "ANAL_SITE") => "BUTTOCK_ANAL",
        ("CONTACT_INSERTION_BODY_SITE", "FEMALE_GENITAL_SITE") => "FEMALE_GENITAL",
        ("CONTACT_INSERTION_BODY_SITE", "URETHRAL_SITE") => "URETHRA",
        ("SEXUAL_ACTIVITY_STIMULATION", "ORAL_ACTIVITY") => "MOUTH_ORAL",
        ("BONDAGE_BDSM_DOMINATION", "GAG_MOUTH_RESTRAINT") => "MOUTH_ORAL",
        _ => null
    };

    private static string? ThemeFacet(string genreId) => genreId switch
    {
        "BONDAGE_BDSM_DOMINATION" => "BDSM_RESTRAINT",
        "INJURY_R18G" => "INJURY_R18G",
        "REPRODUCTION_PREGNANCY_LACTATION" => "REPRO_PREGNANCY_LACTATION",
        _ => null
    };

    private static void ApplyChastity(Dictionary<int, Working> rows)
    {
        foreach (var patch in CsvResource("issue76_chastity_control_patch_v0_4.csv"))
        {
            var row = rows[ParseId(patch)];
            row.KindId = EmptyToNull(patch["resolved_kind_id"]);
            row.Body = Split(patch["resolved_body_site_id"]);
            row.Themes = Split(patch["resolved_theme_id"]);
            row.Status = SpecialBrowseV2Status.AutoCandidate;
        }
    }

    private static void ApplyFormerUnresolved(Dictionary<int, Working> rows)
    {
        foreach (var patch in CsvResource("issue76_v1_unresolved_audit_v0_5.csv"))
        {
            var row = rows[ParseId(patch)];
            row.KindId = EmptyToNull(patch["v2_kind_id"]);
            row.Body = Split(patch["v2_body_sites"]);
            row.Themes = Split(patch["v2_themes"]);
            row.Status = patch["v2_resolution"] switch
            {
                "BROWSE_RESOLVED" => SpecialBrowseV2Status.HumanResolved,
                "REFERENCE_ONLY_NO_DIRECT_BROWSE" => SpecialBrowseV2Status.ReferenceOnlyNoDirectBrowse,
                "DEFER_PRODUCT_FIT_REVIEW" => SpecialBrowseV2Status.DeferProductFitReview,
                "OUT_OF_SCOPE_NO_BROWSE" => SpecialBrowseV2Status.OutOfScopeNoBrowse,
                _ => throw new InvalidDataException("Unknown Special v2 resolution: " + patch["v2_resolution"])
            };
        }
    }

    private static void ApplyPracticalKnowledgePatch(Dictionary<int, Working> rows)
    {
        foreach (var patch in CsvResource("issue76_practical_generation_patch_v0_6.csv"))
        {
            var row = rows[ParseId(patch)];
            if (patch["dimension"] == "kind")
            {
                var value = patch["after"].Trim();
                row.KindId = value.Length == 0 ? null : KindJa.TryGetValue(value, out var id)
                    ? id : throw new InvalidDataException("Unknown Special v2 kind label: " + value);
            }
            else if (patch["dimension"] == "body_site")
            {
                row.Body = new HashSet<string>(StringComparer.Ordinal);
                foreach (var label in SplitText(patch["after"]))
                {
                    if (!BodyJa.TryGetValue(label, out var id)) throw new InvalidDataException("Unknown Special v2 body label: " + label);
                    row.Body.Add(id);
                }
            }
            else throw new InvalidDataException("Unknown Special v2 patch dimension: " + patch["dimension"]);
        }
    }

    private static void Validate(Dictionary<int, Working> rows)
    {
        var kindIds = SpecialBrowseV2Taxonomy.Kinds.Select(x => x.Id).ToHashSet(StringComparer.Ordinal);
        var bodyIds = SpecialBrowseV2Taxonomy.BodySites.Select(x => x.Id).ToHashSet(StringComparer.Ordinal);
        var themeIds = SpecialBrowseV2Taxonomy.Themes.Select(x => x.Id).ToHashSet(StringComparer.Ordinal);
        foreach (var (id, row) in rows)
        {
            if (row.KindId != null && !kindIds.Contains(row.KindId)) throw new InvalidDataException($"Invalid Special v2 kind at {id}");
            if (!row.Body.All(bodyIds.Contains)) throw new InvalidDataException($"Invalid Special v2 body facet at {id}");
            if (!row.Themes.All(themeIds.Contains)) throw new InvalidDataException($"Invalid Special v2 theme at {id}");
            var hasRoute = row.KindId != null || row.Body.Count > 0 || row.Themes.Count > 0;
            if (row.Status is SpecialBrowseV2Status.AutoCandidate or SpecialBrowseV2Status.HumanResolved)
            {
                if (!hasRoute) throw new InvalidDataException($"Browsable Special v2 row has no route: {id}");
            }
            else if (hasRoute) throw new InvalidDataException($"Non-browse Special v2 row still has route: {id}");
        }

        var counts = rows.Values.GroupBy(row => row.Status).ToDictionary(group => group.Key, group => group.Count());
        Expect(counts, SpecialBrowseV2Status.AutoCandidate, 2745);
        Expect(counts, SpecialBrowseV2Status.HumanResolved, 15);
        Expect(counts, SpecialBrowseV2Status.DeferProductFitReview, 6);
        Expect(counts, SpecialBrowseV2Status.OutOfScopeNoBrowse, 1);
        Expect(counts, SpecialBrowseV2Status.ReferenceOnlyNoDirectBrowse, 21);
    }

    private static void Expect(Dictionary<SpecialBrowseV2Status, int> counts, SpecialBrowseV2Status status, int expected)
    {
        if (counts.GetValueOrDefault(status) != expected)
            throw new InvalidDataException($"Special v2 status count drift for {status}: {counts.GetValueOrDefault(status)} != {expected}");
    }

    private static int ParseSpecialId(string catalogId)
        => catalogId.StartsWith("S:", StringComparison.Ordinal) && int.TryParse(catalogId.AsSpan(2), out var id)
            ? id : throw new InvalidDataException("Invalid Special catalog id: " + catalogId);

    private static int ParseId(IReadOnlyDictionary<string, string> row)
        => int.Parse(row["special_id"], System.Globalization.CultureInfo.InvariantCulture);

    private static string? EmptyToNull(string value) => string.IsNullOrWhiteSpace(value) ? null : value.Trim();

    private static HashSet<string> Split(string value)
        => value.Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries).ToHashSet(StringComparer.Ordinal);

    private static string[] SplitText(string value)
        => value.Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

    private static IReadOnlyList<Dictionary<string, string>> CsvResource(string suffix)
    {
        var assembly = typeof(SpecialBrowseV2Overlay).Assembly;
        var resource = assembly.GetManifestResourceNames().SingleOrDefault(name => name.EndsWith(suffix, StringComparison.Ordinal))
            ?? throw new InvalidDataException("Missing embedded Special v2 evidence: " + suffix);
        using var stream = assembly.GetManifestResourceStream(resource) ?? throw new InvalidDataException("Cannot open embedded Special v2 evidence: " + suffix);
        using var parser = new TextFieldParser(stream, System.Text.Encoding.UTF8) { TextFieldType = FieldType.Delimited, HasFieldsEnclosedInQuotes = true, TrimWhiteSpace = false };
        parser.SetDelimiters(",");
        var names = parser.ReadFields() ?? throw new InvalidDataException("Empty embedded Special v2 CSV: " + suffix);
        var result = new List<Dictionary<string, string>>();
        while (!parser.EndOfData)
        {
            var values = parser.ReadFields() ?? [];
            if (values.Length != names.Length) throw new InvalidDataException("Special v2 CSV column mismatch: " + suffix);
            result.Add(names.Zip(values).ToDictionary(pair => pair.First, pair => pair.Second));
        }
        return result;
    }
}
