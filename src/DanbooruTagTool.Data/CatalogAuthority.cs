using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

public sealed record AuthorityAsset(string Path, string Sha256, int Count, string Category);
public sealed record CatalogAuthorityManifest(
    string Schema, string Snapshot, AuthorityAsset[] Assets,
    Dictionary<string, int> CategoryCounts, string IdentitySha256, string SpecialIdentitySha256);
public sealed record AuthorityRow(int Ordinal, CatalogEntry Entry);
public sealed record CatalogAuthority(CatalogEntry[] Entries, CatalogAuthorityManifest Manifest, Dictionary<string, string> SourceHashes);

/// <summary>Current accepted semantic input. Historical evidence is provenance, never a build step.</summary>
public static class CatalogAuthorityReader
{
    public const string Schema = "dtt.catalog-authority-v1";
    public static readonly JsonSerializerOptions Json = new()
    {
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
        RespectRequiredConstructorParameters = true,
        RespectNullableAnnotations = true,
        IgnoreReadOnlyProperties = true,
        Converters = { new JsonStringEnumConverter(allowIntegerValues: false) }
    };

    public static string Hash(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(stream));
    }

    public static string IdentityHash(IEnumerable<CatalogEntry> entries) =>
        Convert.ToHexStringLower(SHA256.HashData(Encoding.UTF8.GetBytes(string.Join("\n",
            entries.OrderBy(e => e.Id, StringComparer.Ordinal).Select(e => JsonSerializer.Serialize(new { e.Id, e.Canonical, e.English, e.IsSpecial, e.EffectiveCategory }))))));

    public static CatalogAuthority Read(string manifestPath)
    {
        var root = Path.GetDirectoryName(Path.GetFullPath(manifestPath))!;
        var manifest = JsonSerializer.Deserialize<CatalogAuthorityManifest>(File.ReadAllText(manifestPath), Json)
            ?? throw new InvalidDataException("Missing authority manifest.");
        if (manifest.Schema != Schema || string.IsNullOrWhiteSpace(manifest.Snapshot) || manifest.Assets.Length == 0)
            throw new InvalidDataException("Unsupported/empty authority manifest.");
        if (manifest.Assets.Select(a => a.Path).Distinct(StringComparer.OrdinalIgnoreCase).Count() != manifest.Assets.Length)
            throw new InvalidDataException("Duplicate authority assets.");
        var rows = new List<AuthorityRow>();
        var sources = new Dictionary<string, string>(StringComparer.Ordinal) { ["manifest.json"] = Hash(manifestPath) };
        foreach (var asset in manifest.Assets)
        {
            if (Path.IsPathRooted(asset.Path)) throw new InvalidDataException("Authority asset paths must be relative.");
            var path = Path.GetFullPath(Path.Combine(root, asset.Path));
            if (!path.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("Authority asset escapes its snapshot directory.");
            if (asset.Count < 0 || !string.Equals(Hash(path), asset.Sha256, StringComparison.Ordinal))
                throw new InvalidDataException("Authority asset hash/count mismatch: " + asset.Path);
            sources.Add(asset.Path, asset.Sha256);
            using var file = File.OpenRead(path);
            using var gzip = new GZipStream(file, CompressionMode.Decompress);
            using var reader = new StreamReader(gzip, Encoding.UTF8);
            var count = 0;
            while (reader.ReadLine() is { } line)
            {
                if (++count > asset.Count) throw new InvalidDataException("Authority asset exceeds declared population.");
                var row = JsonSerializer.Deserialize<AuthorityRow>(line, Json) ?? throw new InvalidDataException("Null authority row.");
                Validate(row.Entry);
                if (row.Entry.EffectiveCategory != asset.Category) throw new InvalidDataException("Authority category mismatch.");
                rows.Add(row);
            }
            if (count != asset.Count) throw new InvalidDataException("Authority asset population mismatch.");
        }
        var ordered = rows.OrderBy(r => r.Ordinal).ToArray();
        if (!ordered.Select(r => r.Ordinal).SequenceEqual(Enumerable.Range(0, ordered.Length)))
            throw new InvalidDataException("Authority ordinal must be unique and contiguous; preserve accepted runtime order.");
        var entries = ordered.Select(r => r.Entry).ToArray();
        if (entries.Select(e => e.Id).Distinct(StringComparer.Ordinal).Count() != entries.Length)
            throw new InvalidDataException("Duplicate authority identity.");
        var counts = entries.GroupBy(e => e.EffectiveCategory).ToDictionary(g => g.Key, g => g.Count(), StringComparer.Ordinal);
        if (counts.Count != manifest.CategoryCounts.Count || counts.Any(p => manifest.CategoryCounts.GetValueOrDefault(p.Key) != p.Value))
            throw new InvalidDataException("Authority category population mismatch.");
        if (IdentityHash(entries) != manifest.IdentitySha256 || IdentityHash(entries.Where(e => e.IsSpecial)) != manifest.SpecialIdentitySha256)
            throw new InvalidDataException("Authority canonical/stable Special identity mismatch.");
        // Exercise the same backend-neutral indexes used by runtime before emitting any database.
        var catalog = new Catalog(entries);
        _ = SpecialBrowseCatalogReader.FromCatalog(catalog);
        _ = new UnifiedBrowseIndex(catalog);
        return new(entries, manifest, sources);
    }

    private static void Validate(CatalogEntry entry)
    {
        if (string.IsNullOrWhiteSpace(entry.Id) || string.IsNullOrWhiteSpace(entry.English) || entry.Canonical == "")
            throw new InvalidDataException("Empty authority identity/surface.");
        if (entry.IsSpecial && (!entry.Id.StartsWith("S:", StringComparison.Ordinal) ||
            !int.TryParse(entry.Id.AsSpan(2), out var id) || id <= 0 || entry.SpecialBrowseV2 is null))
            throw new InvalidDataException("Special authority requires stable numeric IDs and accepted classifications.");
        if (entry.UnifiedBrowseRouteIds.Any(id => !UnifiedBrowseTaxonomy.Routes.Any(r => r.Id == id)))
            throw new InvalidDataException("Unknown Unified route.");
        if (entry.SpecialBrowseV2 is { } special)
        {
            if (special.KindId is { } kind && !SpecialBrowseV2Taxonomy.Kinds.Any(x => x.Id == kind)) throw new InvalidDataException("Unknown Special kind.");
            ValidateFacets(special.BodySiteIds, special.ThemeIds);
        }
        if (entry.UnifiedBrowseFacets is { } facets) ValidateFacets(facets.BodySiteIds, facets.ThemeIds);
    }

    private static void ValidateFacets(string[] body, string[] themes)
    {
        if (body.Any(id => !SpecialBrowseV2Taxonomy.BodySites.Any(x => x.Id == id)) || themes.Any(id => !SpecialBrowseV2Taxonomy.Themes.Any(x => x.Id == id)))
            throw new InvalidDataException("Unknown body/theme facet.");
    }
}

public static class CatalogCompiler
{
    public static CatalogAuthority Compile(string manifestPath, string output, CatalogBuildProfile profile = CatalogBuildProfile.Full)
    {
        if (profile is not (CatalogBuildProfile.Full or CatalogBuildProfile.Ordinary)) throw new ArgumentOutOfRangeException(nameof(profile));
        var authority = CatalogAuthorityReader.Read(manifestPath);
        var full = Path.GetFullPath(output);
        var root = Path.GetDirectoryName(Path.GetFullPath(manifestPath))!;
        if (full.Equals(root, StringComparison.OrdinalIgnoreCase) || full.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) ||
            full.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar).Any(s => s.Equals("UserData", StringComparison.OrdinalIgnoreCase)))
            throw new ArgumentException("Output must be separate from accepted authority and UserData.");
        for (var parent = new DirectoryInfo(full); parent is not null; parent = parent.Parent)
            if (parent.Exists && (parent.Attributes & FileAttributes.ReparsePoint) != 0) throw new ArgumentException("Output must not traverse a filesystem link.");
        if (Directory.Exists(full) && Directory.EnumerateFileSystemEntries(full).Any()) throw new IOException("Output must be fresh and empty; no overwrite or cleanup performed.");
        var entries = profile == CatalogBuildProfile.Full ? authority.Entries : authority.Entries.Where(e => e.EffectiveCategory is "General" or "Special").ToArray();
        Directory.CreateDirectory(full);
        CatalogDatabase.Build(Path.Combine(full, "catalog.db"), entries, JsonSerializer.Serialize(authority.SourceHashes));
        File.WriteAllText(Path.Combine(full, "import-report.json"), JsonSerializer.Serialize(new
        {
            Profile = profile.Name(), Total = entries.Length, AuthoritySchema = authority.Manifest.Schema,
            Snapshot = authority.Manifest.Snapshot, Sources = authority.SourceHashes,
            CategoryCounts = entries.GroupBy(e => e.EffectiveCategory).ToDictionary(g => g.Key, g => g.Count()),
            IdentitySha256 = CatalogAuthorityReader.IdentityHash(entries),
            SpecialIdentitySha256 = CatalogAuthorityReader.IdentityHash(entries.Where(e => e.IsSpecial))
        }, new JsonSerializerOptions { WriteIndented = true }));
        return authority with { Entries = entries };
    }
}
