using System.Globalization;
using System.Security.Cryptography;
using System.Text.Json;
using DanbooruTagTool.Core;
using Microsoft.VisualBasic.FileIO;

namespace DanbooruTagTool.Data;

public sealed record ImportResult(CatalogEntry[] Entries, Dictionary<string, string> SourceHashes);
public static class AcceptedAssetImporter
{
    public static readonly string[] ProtectedInputs = [
        "data/source/danbooru-2026-09-02.csv", "data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv",
        "data/special2788/illustrious_tag_knowledge_base_2788.csv", "data/derived/special2788_VERIFIED_LINKAGE.csv",
        "data/derived/ruleset2/01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv", "data/runtime/japanese_overlay.json"];
    public static ImportResult Read(string sourceRoot, string authorityRoot)
    {
        var hashes = new Dictionary<string, string>();
        string Source(string relative)
        {
            var path = Path.Combine(sourceRoot, relative);
            if (!File.Exists(path)) throw new FileNotFoundException("Missing protected production input: " + relative, path);
            hashes[relative] = Hash(path); return path;
        }
        string Authority(string relative)
        {
            var path = Path.Combine(authorityRoot, relative); hashes[relative] = Hash(path); return path;
        }
        var canonical = Csv(Source(ProtectedInputs[0]), false).ToDictionary(r => r["0"], r => long.Parse(r["2"], CultureInfo.InvariantCulture));
        var aliases = new Dictionary<string, List<string>>();
        foreach (var row in Csv(Source(ProtectedInputs[1])))
        {
            var targets = row["TargetCount"] == "1" ? new[] { row["CanonicalTargets"] } : row["CanonicalTargets"].Split(';');
            foreach (var target in targets)
            {
                if (!canonical.ContainsKey(target)) throw new InvalidDataException("Unknown Alias target");
                if (!aliases.TryGetValue(target, out var list)) aliases[target] = list = [];
                list.Add(row["NormalizedAlias"]);
            }
        }
        var source = Csv(Source(ProtectedInputs[2])).ToDictionary(r => r["ID"]);
        var linkage = Csv(Source(ProtectedInputs[3])).ToDictionary(r => r["ID"]);
        var japanesePath = Source(ProtectedInputs[4]);
        if (Hash(japanesePath) != "12f6ccdc5d2dba33123cdfa97a636b2fdd49a519ed89d327d330471696762e02") throw new InvalidDataException("Ruleset2 accepted Japanese hash mismatch");
        var japanese = Csv(japanesePath).ToDictionary(r => r["ID"]);
        var fitPath = Authority("data/special2788/product_fit_verdicts.csv");
        if (Hash(fitPath) != "357427dfd542a4e582f6fe57bc966539210e794796e9ad93d6350950e1f61f68") throw new InvalidDataException("#63 accepted sidecar hash mismatch");
        var fit = Csv(fitPath).ToDictionary(r => r["special_id"], r => r["product_fit_verdict"]);
        using var taxonomy = JsonDocument.Parse(File.ReadAllText(Authority("docs/issue56/rollout/issue56_ui_genre_taxonomy_v1.json")));
        var paths = new Dictionary<string, BrowsePath>();
        foreach (var genre in taxonomy.RootElement.GetProperty("genres").EnumerateArray())
        {
            var id = genre.GetProperty("id").GetString()!; var label = genre.GetProperty("label_ja").GetString()!;
            paths[id + ">"] = new(id, label);
            foreach (var sub in genre.GetProperty("subgenres").EnumerateArray())
            {
                var subId = sub.GetProperty("id").GetString()!;
                paths[id + ">" + subId] = new(id, label, subId, sub.GetProperty("label_ja").GetString()!);
            }
        }
        var mappingFiles = new[] { Authority("docs/issue56/pilot/issue56_ui_genre_pilot_v1_classification_map.csv") }
            .Concat(Directory.GetFiles(Path.Combine(authorityRoot, "docs/issue56/rollout/reviewed"), "*.csv").OrderBy(p => p, StringComparer.Ordinal)).ToArray();
        var mapping = new Dictionary<string, BrowsePath[]>();
        foreach (var file in mappingFiles)
        {
            hashes[Path.GetRelativePath(authorityRoot, file).Replace('\\', '/')] = Hash(file);
            foreach (var row in Csv(file))
            {
                if (row["primary_genre_id"].Length == 0 && row["classification_status"] is "REVIEW_REQUIRED" or "AMBIGUOUS")
                {
                    // #56 covers all IDs but retains explicit unresolved classifications.
                    // Preserve the accepted empty path instead of inventing a catch-all.
                    mapping.Add(row["special_id"], []); continue;
                }
                var keys = new[] { row["primary_genre_id"] + ">" + row["primary_subgenre_id"] }
                    .Concat(row["secondary_paths"].Split('|', StringSplitOptions.RemoveEmptyEntries).Select(k => k.Trim()).Select(k => k.Contains('>') ? k : k + ">")).ToArray();
                mapping.Add(row["special_id"], keys.Select(k => paths.TryGetValue(k, out var p) ? p : throw new InvalidDataException("Invalid #56 path: " + k)).ToArray());
            }
        }
        if (source.Count != 2788 || !source.Keys.ToHashSet().SetEquals(mapping.Keys) || !source.Keys.ToHashSet().SetEquals(fit.Keys)) throw new InvalidDataException("Special/#56/#63 coverage mismatch");
        using var overlay = JsonDocument.Parse(File.ReadAllText(Source(ProtectedInputs[5])));
        if (overlay.RootElement.GetProperty("format_version").GetInt32() != 1) throw new InvalidDataException("Overlay version");
        var general = overlay.RootElement.GetProperty("entries");
        if (general.EnumerateObject().Count() != 30629) throw new InvalidDataException("Production overlay must contain exactly 30,629 entries");
        var entries = new List<CatalogEntry>();
        foreach (var property in general.EnumerateObject())
        {
            if (!canonical.TryGetValue(property.Name, out var count)) throw new InvalidDataException("Overlay canonical mismatch");
            entries.Add(new("G:" + property.Name, property.Name, property.Name, property.Value.GetProperty("display_ja").GetString(), false, count,
                aliases.GetValueOrDefault(property.Name)?.ToArray() ?? [], property.Value.GetProperty("search_ja").EnumerateArray().Select(v => v.GetString()!).ToArray(), []));
        }
        foreach (var (id, row) in source.OrderBy(p => int.Parse(p.Key, CultureInfo.InvariantCulture)))
        {
            var link = linkage[id]; var ja = japanese[id];
            if (row["Tag"] != ja["Tag"] || row.Any(p => link[p.Key] != p.Value)) throw new InvalidDataException("Special source identity/linkage mismatch " + id);
            var target = link["ChosenCanonicalTag"];
            if (target.Length > 0 && !canonical.ContainsKey(target)) throw new InvalidDataException("Invalid Special canonical");
            entries.Add(new("S:" + id, target.Length == 0 ? null : target, row["Tag"], ja["日本語"], true,
                target.Length == 0 ? null : canonical[target], target.Length == 0 ? [] : aliases.GetValueOrDefault(target)?.ToArray() ?? [],
                ja["検索キー"].Split(" | ", StringSplitOptions.RemoveEmptyEntries), mapping[id], fit[id], ja["元の日本語説明"]));
        }
        // #63 canonical eligibility must also prevent General duplicates from bypassing exclusion.
        var specialGroups = entries.Where(e => e.IsSpecial && e.Canonical != null).GroupBy(e => e.Canonical!).ToDictionary(g => g.Key, g => g.ToArray());
        for (int i = 0; i < entries.Count; i++)
            if (!entries[i].IsSpecial && specialGroups.TryGetValue(entries[i].Canonical!, out var related) && related.All(e => !e.CanSearch))
                entries[i] = entries[i] with { ProductFit = "OUT_OF_SCOPE_PRODUCT" };
        return new(entries.ToArray(), hashes);
    }
    public static string Hash(string path) => Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(path)));
    public static IReadOnlyList<Dictionary<string, string>> Csv(string path, bool header = true)
    {
        using var parser = new TextFieldParser(path, System.Text.Encoding.UTF8) { TextFieldType = FieldType.Delimited, HasFieldsEnclosedInQuotes = true, TrimWhiteSpace = false };
        parser.SetDelimiters(",");
        var first = parser.ReadFields() ?? throw new InvalidDataException("Empty CSV");
        var names = header ? first : Enumerable.Range(0, first.Length).Select(i => i.ToString(CultureInfo.InvariantCulture)).ToArray();
        var rows = new List<Dictionary<string, string>>();
        void Add(string[] values)
        {
            if (values.Length != names.Length) throw new InvalidDataException("CSV column count mismatch: " + path);
            rows.Add(names.Zip(values).ToDictionary(p => p.First, p => p.Second));
        }
        if (!header) Add(first);
        while (!parser.EndOfData) Add(parser.ReadFields()!);
        return rows;
    }
}
