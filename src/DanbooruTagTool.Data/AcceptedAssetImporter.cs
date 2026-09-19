using System.Globalization;
using System.Security.Cryptography;
using System.Text.Json;
using DanbooruTagTool.Core;
using Microsoft.VisualBasic.FileIO;

namespace DanbooruTagTool.Data;

public sealed record ImportResult(CatalogEntry[] Entries, Dictionary<string, string> SourceHashes);
public static class AcceptedAssetImporter
{
    public const int BaseSpecialCount = 2788;
    public const int Issue96ExpandedSpecialCount = 2983;
    public const int ExpandedSpecialCount = 3088;
    public const int ProductionSpecialCount = 3059;
    public const string ProductionProfileRelativePath = "data/generation/special2788_generation_profile.csv";
    public const string PromotionRelativePath = "docs/issue96/special_expansion_promotion_proposal_v1.csv";
    public const string Issue107PromotionRelativePath = "docs/issue107/promotion_metadata_v1.csv";
    private const string PromotionHash = "cdeef93802f8b1ebf0e70b2fe82211e2fd8955b064b063f10093a3ff0642dc1f";
    private const string Issue107PromotionHash = "84a31353d438001985b76793570417b6501f8ada220466c8508bf989544f26f5";
    public static readonly string[] ProtectedInputs = [
        "data/source/danbooru-2026-09-02.csv", "data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv",
        "data/special2788/illustrious_tag_knowledge_base_2788.csv", "data/derived/special2788_VERIFIED_LINKAGE.csv",
        "data/derived/ruleset2/01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv", "data/runtime/japanese_overlay.json"];
    public static ImportResult Read(string sourceRoot, string authorityRoot)
        => Read(sourceRoot, authorityRoot, CatalogBuildProfile.Full);

    public static ImportResult Read(string sourceRoot, string authorityRoot, CatalogBuildProfile profile)
    {
        if (profile is not (CatalogBuildProfile.Full or CatalogBuildProfile.Ordinary))
            throw new ArgumentOutOfRangeException(nameof(profile));
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
        if (Hash(fitPath) != "d1c3d3fff12f48169458fa9967674022dc42456f2ee8ed9bee5156e53ced7834") throw new InvalidDataException("#63 accepted sidecar hash mismatch");
        var fit = Csv(fitPath).ToDictionary(r => r["special_id"], r => r["product_fit_verdict"]);
        var promotionPath = Authority(PromotionRelativePath);
        if (Hash(promotionPath) != PromotionHash) throw new InvalidDataException("Issue #96 promotion proposal hash mismatch");
        var promotion = Csv(promotionPath).OrderBy(row => int.Parse(row["proposed_special_id"], CultureInfo.InvariantCulture)).ToArray();
        ValidatePromotion(source, canonical, promotion);
        var issue107PromotionPath = Authority(Issue107PromotionRelativePath);
        if (Hash(issue107PromotionPath) != Issue107PromotionHash) throw new InvalidDataException("Issue #107 promotion metadata hash mismatch");
        var issue107Promotion = Csv(issue107PromotionPath).OrderBy(row => int.Parse(row["proposed_special_id"], CultureInfo.InvariantCulture)).ToArray();
        ValidateIssue107Promotion(source, canonical, promotion, issue107Promotion);
        var productionProfilePath = Authority(ProductionProfileRelativePath);
        var productionProfile = Csv(productionProfilePath);
        ValidateProductionProfile(productionProfile, source, promotion, issue107Promotion);
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
        var mappingFiles = Issue56Inputs.MappingHashes.Select(input =>
        {
            var path = Authority(input.Key);
            if (hashes[input.Key] != input.Value) throw new InvalidDataException("#56 accepted mapping hash mismatch: " + input.Key);
            return path;
        }).ToArray();
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
        if (source.Count != BaseSpecialCount || linkage.Count != BaseSpecialCount || !source.Keys.ToHashSet().SetEquals(mapping.Keys)) throw new InvalidDataException("Base Special/#56 coverage mismatch");
        var expectedFitIds = Enumerable.Range(1, ExpandedSpecialCount).Select(id => id.ToString(CultureInfo.InvariantCulture)).ToHashSet(StringComparer.Ordinal);
        if (fit.Count != ExpandedSpecialCount || !fit.Keys.ToHashSet().SetEquals(expectedFitIds)) throw new InvalidDataException("Special/#63 expanded coverage mismatch");
        var generalTaxonomy = AcceptedGeneralTaxonomyImporter.Read(authorityRoot);
        foreach (var hash in generalTaxonomy.SourceHashes) hashes.Add(hash.Key, hash.Value);
        using var overlay = JsonDocument.Parse(File.ReadAllText(Source(ProtectedInputs[5])));
        if (overlay.RootElement.GetProperty("format_version").GetInt32() != 1) throw new InvalidDataException("Overlay version");
        var general = overlay.RootElement.GetProperty("entries");
        if (general.EnumerateObject().Count() != 30629 || !general.EnumerateObject().Select(p => p.Name).ToHashSet(StringComparer.Ordinal).SetEquals(generalTaxonomy.Assignments.Keys))
            throw new InvalidDataException("Production overlay and accepted Issue #64 canonical population must match exactly");
        var entries = new List<CatalogEntry>();
        foreach (var property in general.EnumerateObject())
        {
            if (!canonical.TryGetValue(property.Name, out var count)) throw new InvalidDataException("Overlay canonical mismatch");
            var classification = generalTaxonomy.Assignments[property.Name];
            entries.Add(new("G:" + property.Name, property.Name, property.Name, property.Value.GetProperty("display_ja").GetString(), false, count,
                aliases.GetValueOrDefault(property.Name)?.ToArray() ?? [], property.Value.GetProperty("search_ja").EnumerateArray().Select(v => v.GetString()!).ToArray(),
                classification.Paths, BrowseClassification: classification.Status));
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
        foreach (var row in promotion)
        {
            var id = row["proposed_special_id"];
            var canonicalTag = row["canonical_tag"];
            var bodySites = SplitPipe(row["body_site_ids"]);
            var themes = SplitPipe(row["theme_ids"]);
            ValidatePromotionFacets(id, row["kind_id"], bodySites, themes);
            entries.Add(new("S:" + id, canonicalTag, canonicalTag, row["display_ja"], true,
                canonical[canonicalTag], aliases.GetValueOrDefault(canonicalTag)?.ToArray() ?? [],
                SplitPipe(row["search_ja"]), [], fit[id], "",
                BrowseClassificationStatus.NotApplicable,
                new SpecialBrowseV2Classification(row["kind_id"], bodySites, themes, SpecialBrowseV2Status.HumanResolved)));
        }
        foreach (var row in issue107Promotion)
        {
            var id = row["proposed_special_id"];
            var canonicalTag = row["canonical_tag"];
            var bodySites = SplitPipe(row["body_site_ids"]);
            var themes = SplitPipe(row["theme_ids"]);
            ValidatePromotionFacets(id, row["kind_id"], bodySites, themes);
            entries.Add(new("S:" + id, canonicalTag, canonicalTag, row["display_ja"], true,
                canonical[canonicalTag], aliases.GetValueOrDefault(canonicalTag)?.ToArray() ?? [],
                SplitPipe(row["search_ja"]), [], fit[id], "",
                BrowseClassificationStatus.NotApplicable,
                new SpecialBrowseV2Classification(row["kind_id"], bodySites, themes, SpecialBrowseV2Status.HumanResolved)));
        }
        var productionIds = productionProfile
            .Select(row => int.Parse(row["SpecialID"], CultureInfo.InvariantCulture))
            .ToHashSet();
        entries = entries.Where(entry => !entry.IsSpecial || productionIds.Contains(ParseSpecialId(entry.Id))).ToList();
        // #63 canonical eligibility must also prevent General duplicates from bypassing exclusion.
        var specialGroups = entries.Where(e => e.IsSpecial && e.Canonical != null).GroupBy(e => e.Canonical!).ToDictionary(g => g.Key, g => g.ToArray());
        for (int i = 0; i < entries.Count; i++)
            if (!entries[i].IsSpecial && specialGroups.TryGetValue(entries[i].Canonical!, out var related) && related.All(e => !e.CanSearch))
                entries[i] = entries[i] with { ProductFit = "OUT_OF_SCOPE_PRODUCT" };

        if (profile == CatalogBuildProfile.Full)
        {
            var issue70Path = Authority(Issue70CatalogOverlayImporter.RelativePath);
            var issue70 = Issue70CatalogOverlayImporter.Read(issue70Path);
            var existingCanonical = entries.Where(e => e.Canonical != null).Select(e => e.Canonical!).ToHashSet(StringComparer.Ordinal);
            var overlap = issue70.Where(e => e.Canonical != null && existingCanonical.Contains(e.Canonical)).Select(e => e.Canonical!).Take(5).ToArray();
            if (overlap.Length > 0) throw new InvalidDataException("Issue #70 canonical overlaps existing General/Special: " + string.Join(", ", overlap));
            entries.AddRange(issue70);
        }
        return new(entries.ToArray(), hashes);
    }

    private static void ValidateProductionProfile(
        IReadOnlyList<Dictionary<string, string>> profile,
        IReadOnlyDictionary<string, Dictionary<string, string>> source,
        IReadOnlyList<Dictionary<string, string>> issue96Promotion,
        IReadOnlyList<Dictionary<string, string>> issue107Promotion)
    {
        if (profile.Count != ProductionSpecialCount)
            throw new InvalidDataException($"Production Special profile count drift: {profile.Count} != {ProductionSpecialCount}");
        var ids = profile.Select(row => int.Parse(row["SpecialID"], CultureInfo.InvariantCulture)).ToArray();
        if (ids.Distinct().Count() != ids.Length || ids.Any(id => id < 1 || id > ExpandedSpecialCount) || ids.Max() != ExpandedSpecialCount)
            throw new InvalidDataException("Production Special profile IDs are not a stable subset of 1..3088");
        var allTags = source.Values.ToDictionary(row => int.Parse(row["ID"], CultureInfo.InvariantCulture), row => row["Tag"]);
        foreach (var row in issue96Promotion.Concat(issue107Promotion))
            allTags[int.Parse(row["proposed_special_id"], CultureInfo.InvariantCulture)] = row["canonical_tag"];
        foreach (var row in profile)
        {
            var id = int.Parse(row["SpecialID"], CultureInfo.InvariantCulture);
            var tag = row["Tag"];
            if (!allTags.TryGetValue(id, out var expectedTag) || expectedTag != tag)
                throw new InvalidDataException("Production Special profile identity mismatch at " + id);
        }
    }
    private static void ValidatePromotion(
        IReadOnlyDictionary<string, Dictionary<string, string>> source,
        IReadOnlyDictionary<string, long> canonical,
        IReadOnlyList<Dictionary<string, string>> promotion)
    {
        var ids = promotion.Select(row => int.Parse(row["proposed_special_id"], CultureInfo.InvariantCulture)).ToArray();
        if (promotion.Count != Issue96ExpandedSpecialCount - BaseSpecialCount || !ids.SequenceEqual(Enumerable.Range(BaseSpecialCount + 1, Issue96ExpandedSpecialCount - BaseSpecialCount)))
            throw new InvalidDataException("Issue #96 promotion IDs must be contiguous 2789..2983");
        var existingSpecialSurfaces = source.Values.Select(row => row["Tag"]).ToHashSet(StringComparer.Ordinal);
        foreach (var row in promotion)
        {
            var tag = row["canonical_tag"];
            if (!canonical.TryGetValue(tag, out var postCount)) throw new InvalidDataException("Issue #96 promotion is not a current General canonical: " + tag);
            if (existingSpecialSurfaces.Contains(tag)) throw new InvalidDataException("Issue #96 promotion overlaps current Special surface: " + tag);
            if (long.Parse(row["frozen_post_count_2026_09_02"], CultureInfo.InvariantCulture) != postCount)
                throw new InvalidDataException("Issue #96 frozen post_count drift: " + tag);
            if (string.IsNullOrWhiteSpace(row["display_ja"]) || string.IsNullOrWhiteSpace(row["search_ja"]))
                throw new InvalidDataException("Issue #96 Japanese metadata incomplete: " + tag);
        }
    }
    private static void ValidateIssue107Promotion(
        IReadOnlyDictionary<string, Dictionary<string, string>> source,
        IReadOnlyDictionary<string, long> canonical,
        IReadOnlyList<Dictionary<string, string>> issue96Promotion,
        IReadOnlyList<Dictionary<string, string>> issue107Promotion)
    {
        var ids = issue107Promotion.Select(row => int.Parse(row["proposed_special_id"], CultureInfo.InvariantCulture)).ToArray();
        if (issue107Promotion.Count != ExpandedSpecialCount - Issue96ExpandedSpecialCount ||
            !ids.SequenceEqual(Enumerable.Range(Issue96ExpandedSpecialCount + 1, ExpandedSpecialCount - Issue96ExpandedSpecialCount)))
            throw new InvalidDataException("Issue #107 promotion IDs must be contiguous 2984..3088");
        var existing = source.Values.Select(row => row["Tag"]).Concat(issue96Promotion.Select(row => row["canonical_tag"])).ToHashSet(StringComparer.Ordinal);
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var row in issue107Promotion)
        {
            var tag = row["canonical_tag"];
            if (!seen.Add(tag)) throw new InvalidDataException("Duplicate Issue #107 promotion canonical: " + tag);
            if (!canonical.TryGetValue(tag, out var postCount)) throw new InvalidDataException("Issue #107 promotion is not a current General canonical: " + tag);
            if (existing.Contains(tag)) throw new InvalidDataException("Issue #107 promotion overlaps existing Special identity: " + tag);
            if (long.Parse(row["frozen_post_count_2026_09_02"], CultureInfo.InvariantCulture) != postCount)
                throw new InvalidDataException("Issue #107 frozen post_count drift: " + tag);
            if (row["metadata_status"] != "HUMAN_BOUNDED_RESOLVED" || string.IsNullOrWhiteSpace(row["display_ja"]) || string.IsNullOrWhiteSpace(row["search_ja"]))
                throw new InvalidDataException("Issue #107 product metadata incomplete: " + tag);
            if (string.IsNullOrWhiteSpace(row["generation_family"]) || string.IsNullOrWhiteSpace(row["generation_role"]) ||
                string.IsNullOrWhiteSpace(row["prompt_use_mode"]) || string.IsNullOrWhiteSpace(row["family_rule_id"]))
                throw new InvalidDataException("Issue #107 generation metadata incomplete: " + tag);
            ValidatePromotionFacets(row["proposed_special_id"], row["kind_id"], SplitPipe(row["body_site_ids"]), SplitPipe(row["theme_ids"]));
        }
    }

    private static void ValidatePromotionFacets(string id, string kind, string[] bodySites, string[] themes)
    {
        if (!SpecialBrowseV2Taxonomy.Kinds.Any(item => item.Id == kind)) throw new InvalidDataException("Invalid Issue #96 kind at " + id);
        if (bodySites.Any(value => !SpecialBrowseV2Taxonomy.BodySites.Any(item => item.Id == value))) throw new InvalidDataException("Invalid Issue #96 body facet at " + id);
        if (themes.Any(value => !SpecialBrowseV2Taxonomy.Themes.Any(item => item.Id == value))) throw new InvalidDataException("Invalid Issue #96 theme at " + id);
    }
    private static string[] SplitPipe(string value) => value.Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
    private static int ParseSpecialId(string catalogId)
        => catalogId.StartsWith("S:", StringComparison.Ordinal) && int.TryParse(catalogId.AsSpan(2), out var id)
            ? id : throw new InvalidDataException("Invalid Special catalog id: " + catalogId);
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
