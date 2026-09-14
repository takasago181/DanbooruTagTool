using System.Text.Json;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

public sealed record GeneralTaxonomyAssignment(BrowseClassificationStatus Status, BrowsePath[] Paths);

public sealed record AcceptedGeneralTaxonomyImport(
    IReadOnlyDictionary<string, GeneralTaxonomyAssignment> Assignments,
    int ProposedCount,
    int UnresolvedCount,
    IReadOnlyDictionary<string, string> SourceHashes);

/// <summary>Reads only the hash-pinned Issue #64 production candidate assets during an explicit catalog build.</summary>
public static class AcceptedGeneralTaxonomyImporter
{
    public const string TaxonomyRelativePath = "docs/issue64/production_candidate/general_taxonomy.json";
    public const string SidecarRelativePath = "docs/issue64/production_candidate/effective_sidecar.csv";
    public const string ManifestRelativePath = "docs/issue64/production_candidate/manifest.json";
    public const string AcceptedTaxonomySha256 = "7311fa1bf1523fcd83134c975b579289d7dbc8aa4cdb1313952d906fc2beb70f";
    public const string AcceptedSidecarSha256 = "a118f5f904c38cee5b63f0c83b06a56f50ee8afdb623c52eb354731bc0b846d9";

    public static AcceptedGeneralTaxonomyImport Read(string authorityRoot)
    {
        var taxonomyPath = Path.Combine(authorityRoot, TaxonomyRelativePath);
        var sidecarPath = Path.Combine(authorityRoot, SidecarRelativePath);
        var manifestPath = Path.Combine(authorityRoot, ManifestRelativePath);
        foreach (var path in new[] { taxonomyPath, sidecarPath, manifestPath })
            if (!File.Exists(path)) throw new FileNotFoundException("Missing accepted Issue #64 production asset.", path);

        var hashes = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [TaxonomyRelativePath] = AcceptedAssetImporter.Hash(taxonomyPath),
            [SidecarRelativePath] = AcceptedAssetImporter.Hash(sidecarPath),
            [ManifestRelativePath] = AcceptedAssetImporter.Hash(manifestPath)
        };
        using var manifest = JsonDocument.Parse(File.ReadAllText(manifestPath));
        ValidateManifest(manifest.RootElement);
        if (hashes[TaxonomyRelativePath] != AcceptedTaxonomySha256 ||
            hashes[SidecarRelativePath] != AcceptedSidecarSha256)
            throw new InvalidDataException("Accepted Issue #64 production asset hash mismatch.");

        var browsePaths = ReadTaxonomy(taxonomyPath);
        var rows = AcceptedAssetImporter.Csv(sidecarPath);
        if (rows.Count != 30_629) throw new InvalidDataException("Issue #64 sidecar population must contain exactly 30,629 rows.");

        var assignments = new Dictionary<string, GeneralTaxonomyAssignment>(StringComparer.Ordinal);
        var proposed = 0;
        var unresolved = 0;
        foreach (var row in rows)
        {
            var canonical = row["canonical"];
            if (canonical.Length == 0) throw new InvalidDataException("Issue #64 sidecar contains an empty canonical identity.");

            GeneralTaxonomyAssignment assignment;
            switch (row["classification_status"])
            {
                case "PROPOSED":
                {
                    var paths = new List<BrowsePath> { ResolvePath(row["primary_path"], browsePaths) };
                    using var secondary = JsonDocument.Parse(row["secondary_paths"]);
                    if (secondary.RootElement.ValueKind != JsonValueKind.Array)
                        throw new InvalidDataException("Issue #64 secondary_paths must be a JSON array.");
                    foreach (var value in secondary.RootElement.EnumerateArray())
                    {
                        if (value.ValueKind != JsonValueKind.String) throw new InvalidDataException("Issue #64 secondary path must be a string.");
                        paths.Add(ResolvePath(value.GetString()!, browsePaths));
                    }
                    if (paths.Select(p => p.Key).Distinct(StringComparer.Ordinal).Count() != paths.Count)
                        throw new InvalidDataException("Issue #64 row repeats a taxonomy path.");
                    assignment = new(BrowseClassificationStatus.Proposed, paths.ToArray());
                    proposed++;
                    break;
                }
                case "UNRESOLVED":
                    if (row["primary_path"].Length != 0 || row["secondary_paths"] != "[]")
                        throw new InvalidDataException("Issue #64 unresolved rows must not have browse paths.");
                    assignment = new(BrowseClassificationStatus.Unresolved, []);
                    unresolved++;
                    break;
                default:
                    throw new InvalidDataException("Unsupported Issue #64 classification status: " + row["classification_status"]);
            }

            if (!assignments.TryAdd(canonical, assignment))
                throw new InvalidDataException("Issue #64 sidecar contains a duplicate canonical identity: " + canonical);
        }

        if (proposed != 28_226 || unresolved != 2_403)
            throw new InvalidDataException($"Issue #64 status counts changed: PROPOSED={proposed}, UNRESOLVED={unresolved}.");
        return new(assignments, proposed, unresolved, hashes);
    }

    private static Dictionary<string, BrowsePath> ReadTaxonomy(string path)
    {
        using var document = JsonDocument.Parse(File.ReadAllText(path));
        var root = document.RootElement;
        if (root.GetProperty("version").GetString() != "issue64-pilot-v2" ||
            root.GetProperty("max_path_depth").GetInt32() != 2 ||
            !root.GetProperty("no_visible_catch_all").GetBoolean())
            throw new InvalidDataException("Unexpected accepted Issue #64 taxonomy contract.");

        var paths = new Dictionary<string, BrowsePath>(StringComparer.Ordinal);
        foreach (var genre in root.GetProperty("genres").EnumerateObject())
        {
            var genreLabel = genre.Value.GetProperty("label_ja").GetString();
            if (string.IsNullOrWhiteSpace(genreLabel)) throw new InvalidDataException("Issue #64 genre has no Japanese label.");
            paths.Add(genre.Name, new(genre.Name, genreLabel));
            foreach (var subgenre in genre.Value.GetProperty("subgenres").EnumerateObject())
            {
                var label = subgenre.Value.GetString();
                if (string.IsNullOrWhiteSpace(label)) throw new InvalidDataException("Issue #64 subgenre has no Japanese label.");
                paths.Add(genre.Name + "/" + subgenre.Name, new(genre.Name, genreLabel, subgenre.Name, label));
            }
        }
        if (paths.Count == 0 || root.GetProperty("genres").EnumerateObject().Count() != 17)
            throw new InvalidDataException("Issue #64 accepted taxonomy must contain its 17 genres.");
        return paths;
    }

    private static BrowsePath ResolvePath(string key, IReadOnlyDictionary<string, BrowsePath> paths) =>
        paths.TryGetValue(key, out var path) ? path : throw new InvalidDataException("Unknown Issue #64 taxonomy path: " + key);

    private static void ValidateManifest(JsonElement manifest)
    {
        if (manifest.GetProperty("issue").GetInt32() != 64 ||
            manifest.GetProperty("final_verdict").GetString() != "ACCEPT_FOR_PRODUCTION_INTEGRATION")
            throw new InvalidDataException("Issue #64 manifest is not accepted for production integration.");

        var taxonomy = manifest.GetProperty("taxonomy");
        var sidecar = manifest.GetProperty("effective_sidecar");
        var population = manifest.GetProperty("population");
        if (taxonomy.GetProperty("path").GetString() != TaxonomyRelativePath ||
            taxonomy.GetProperty("version").GetString() != "issue64-pilot-v2" ||
            taxonomy.GetProperty("sha256").GetString() != AcceptedTaxonomySha256 ||
            sidecar.GetProperty("path").GetString() != SidecarRelativePath ||
            sidecar.GetProperty("sha256").GetString() != AcceptedSidecarSha256 ||
            sidecar.GetProperty("row_count").GetInt32() != 30_629 ||
            sidecar.GetProperty("proposed").GetInt32() != 28_226 ||
            sidecar.GetProperty("unresolved").GetInt32() != 2_403 ||
            population.GetProperty("count").GetInt32() != 30_629)
            throw new InvalidDataException("Issue #64 manifest does not match the accepted Phase C contract.");
    }
}
