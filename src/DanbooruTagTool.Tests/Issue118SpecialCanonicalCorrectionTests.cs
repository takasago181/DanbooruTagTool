using System.Globalization;
using System.IO;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue118SpecialCanonicalCorrectionTests(ITestOutputHelper output)
{
    private const string LinkageSha256 = "d2691e774df0da762dbbf644c8aee4d68fe7d370ea91121c9ad083ccd3728ec2";
    private const string Issue76AuditSha256 = "be959fa5243d45963a5ef6baf5a90aa93eec753cb0fd57aa31a40323a3dac2e9";

    [ProductionFact]
    public void CorrectionAuthorityEnumeratesOnlyTheElevenSuspectGroupsAndPreservesProtectedRuntimeBaseline()
    {
        var sourceRoot = Environment.GetEnvironmentVariable("DTT_SOURCE_ROOT")!;
        var authorityRoot = Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT")!;
        var source = AcceptedAssetImporter.Csv(Path.Combine(sourceRoot, "data/special2788/illustrious_tag_knowledge_base_2788.csv"))
            .ToDictionary(row => row["ID"], StringComparer.Ordinal);
        var linkagePath = Path.Combine(sourceRoot, "data/derived/special2788_VERIFIED_LINKAGE.csv");
        var linkage = AcceptedAssetImporter.Csv(linkagePath).ToDictionary(row => row["ID"], StringComparer.Ordinal);
        var canonical = AcceptedAssetImporter.Csv(Path.Combine(sourceRoot, "data/source/danbooru-2026-09-02.csv"), false)
            .ToDictionary(row => row["0"], row => long.Parse(row["2"], CultureInfo.InvariantCulture), StringComparer.Ordinal);
        var path = Path.Combine(authorityRoot, "docs/issue118/special_canonical_corrections_v1.csv");
        var rows = AcceptedAssetImporter.Csv(path);

        var expected = Expected();
        Assert.Equal(expected.Keys.OrderBy(id => id), rows.Select(row => int.Parse(row["special_id"], CultureInfo.InvariantCulture)).OrderBy(id => id));
        Assert.Equal(rows.Count, rows.Select(row => row["special_id"]).Distinct(StringComparer.Ordinal).Count());

        foreach (var row in rows)
        {
            var id = int.Parse(row["special_id"], CultureInfo.InvariantCulture);
            Assert.True(expected.TryGetValue(id, out var decision), $"Unexpected correction id: {id}");
            var key = id.ToString(CultureInfo.InvariantCulture);
            Assert.Equal(source[key]["Tag"], row["special_tag"]);
            Assert.Equal(linkage[key]["ChosenCanonicalTag"], row["old_canonical"]);
            Assert.Equal(decision.Decision, row["decision"]);
            Assert.Equal(decision.NewCanonical, row["new_canonical"]);
            if (row["new_canonical"].Length > 0) Assert.True(canonical.ContainsKey(row["new_canonical"]), "Correction target is not a current canonical: " + id);
            if (row["decision"] == "ORIGINAL_IS_CANONICAL")
                Assert.Equal(Normalize(row["special_tag"]), row["new_canonical"]);
            if (row["decision"] is "NO_SAFE_CANONICAL" or "NEEDS_MANUAL_DECISION")
                Assert.Empty(row["new_canonical"]);
        }

        Assert.Equal(LinkageSha256, AcceptedAssetImporter.Hash(linkagePath));
        Assert.Equal(Issue118SpecialCanonicalCorrectionOverlay.AcceptedSha256, AcceptedAssetImporter.Hash(path));
        var imported = AcceptedAssetImporter.Read(sourceRoot, authorityRoot, CatalogBuildProfile.Ordinary);
        Assert.Equal(30_629, imported.Entries.Count(entry => entry.EffectiveCategory == "General"));
        Assert.Equal(AcceptedAssetImporter.ProductionSpecialCount, imported.Entries.Count(entry => entry.EffectiveCategory == "Special"));
        Assert.DoesNotContain(imported.SourceHashes.Keys, key => key == Issue70CatalogOverlayImporter.RelativePath);
        Assert.Equal(AcceptedGeneralTaxonomyImporter.AcceptedTaxonomySha256, imported.SourceHashes[AcceptedGeneralTaxonomyImporter.TaxonomyRelativePath]);
        Assert.Equal(AcceptedGeneralTaxonomyImporter.AcceptedSidecarSha256, imported.SourceHashes[AcceptedGeneralTaxonomyImporter.SidecarRelativePath]);

        var profile = AcceptedAssetImporter.Csv(Path.Combine(authorityRoot, AcceptedAssetImporter.ProductionProfileRelativePath));
        var profileIds = profile.Select(row => int.Parse(row["SpecialID"], CultureInfo.InvariantCulture)).OrderBy(id => id);
        var importedIds = imported.Entries.Where(entry => entry.IsSpecial).Select(entry => int.Parse(entry.Id.AsSpan(2), CultureInfo.InvariantCulture)).OrderBy(id => id);
        Assert.Equal(profileIds, importedIds);

        var fit = AcceptedAssetImporter.Csv(Path.Combine(authorityRoot, "data/special2788/product_fit_verdicts.csv"))
            .ToDictionary(row => row["special_id"], row => row["product_fit_verdict"], StringComparer.Ordinal);
        foreach (var entry in imported.Entries.Where(entry => entry.IsSpecial))
            Assert.Equal(fit[entry.Id[2..]], entry.ProductFit);

        foreach (var row in rows)
        {
            var entry = imported.Entries.Single(entry => entry.Id == "S:" + row["special_id"]);
            if (row["decision"] == "NO_SAFE_CANONICAL")
            {
                Assert.Null(entry.Canonical);
                Assert.Equal(Issue118SpecialCanonicalCorrectionOverlay.NormalizePromptToken(row["special_tag"]), entry.PromptToken);
                Assert.Equal(entry.PromptToken, entry.EffectivePromptToken);
                Assert.True(entry.CanAdd);
            }
            else
            {
                Assert.Equal(row["new_canonical"], entry.Canonical);
                Assert.Null(entry.PromptToken);
                Assert.Equal(entry.Canonical, entry.EffectivePromptToken);
                Assert.True(entry.CanAdd);
            }
        }

        var issue76Path = Path.Combine(authorityRoot, "src/DanbooruTagTool.Data/Issue76Data/issue76_v1_unresolved_audit_v0_5.csv");
        Assert.Equal(Issue76AuditSha256, AcceptedAssetImporter.Hash(issue76Path));
        output.WriteLine("25 affected Special IDs audited; 18 NO_SAFE_CANONICAL, 0 NEEDS_MANUAL_DECISION, 4 EXACT_CANONICAL, 3 ORIGINAL_IS_CANONICAL.");
        output.WriteLine("Protected linkage hash, Issue #64 hashes, production membership, and product-fit baseline preserved.");
    }

    [ProductionFact]
    public void NoSafeSpecialsResolveAndUseTheirOwnPromptTokensWithoutCanonicalDeduplication()
    {
        var sourceRoot = Environment.GetEnvironmentVariable("DTT_SOURCE_ROOT")!;
        var authorityRoot = Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT")!;
        var imported = AcceptedAssetImporter.Read(sourceRoot, authorityRoot, CatalogBuildProfile.Ordinary);
        var catalog = new Catalog(imported.Entries);
        var parser = new PromptParser(catalog);
        var noSafeIds = new[] { 550, 1251, 1252, 1253, 1254, 1255, 1256, 1361, 1502, 1575, 2528, 2529, 2530, 2531, 2537, 2546, 2634, 2635 };
        var workspace = new PromptWorkspace(parser);

        foreach (var id in noSafeIds)
        {
            var entry = imported.Entries.Single(candidate => candidate.Id == "S:" + id.ToString(CultureInfo.InvariantCulture));
            var token = Issue118SpecialCanonicalCorrectionOverlay.NormalizePromptToken(entry.English);
            Assert.Null(entry.Canonical);
            Assert.Equal(token, entry.PromptToken);
            Assert.Equal(entry.Id, catalog.Resolve(entry.English)?.Id);
            Assert.Equal(entry.Id, catalog.Resolve(token)?.Id);
            Assert.True(entry.CanAdd);
            Assert.True(workspace.Add(entry), entry.Id);
            Assert.False(workspace.Add(entry), entry.Id);
            Assert.Equal(token, Assert.Single(workspace.Items).Canonical);
            Assert.Equal(token, PromptOutputFormatter.SerializeCanonical(workspace.Items));
            workspace.Delete([workspace.Items[0].Id]);
        }

        var nakedSocks = imported.Entries.Single(entry => entry.Id == "S:2531");
        var generalSocks = imported.Entries.Single(entry => !entry.IsSpecial && entry.Canonical == "socks");
        Assert.NotEqual(UnifiedBrowseIndex.IdentityKey(generalSocks), UnifiedBrowseIndex.IdentityKey(nakedSocks));
        Assert.Contains(catalog.Search("naked socks"), hit => hit.Entry.Id == nakedSocks.Id);
        Assert.Contains(catalog.Search("naked socks"), hit => hit.Entry.Id == generalSocks.Id);

        var safeSpecial = imported.Entries.Single(entry => entry.Id == "S:725");
        Assert.Equal("covered_nipples", safeSpecial.Canonical);
        Assert.Equal("covered_nipples", safeSpecial.EffectivePromptToken);
        var coveredGeneral = imported.Entries.Single(entry => !entry.IsSpecial && entry.Canonical == "covered_nipples");
        Assert.Equal(UnifiedBrowseIndex.IdentityKey(coveredGeneral), UnifiedBrowseIndex.IdentityKey(safeSpecial));

        var row = new EntryViewModel(nakedSocks, workspace, entry => workspace.Add(entry));
        Assert.True(row.Add.CanExecute(null));
        row.Add.Execute(null);
        row.Refresh();
        Assert.Equal("✓ 追加済み（クリックで取消）", row.AddLabel);
        row.Add.Execute(null);
        Assert.Empty(workspace.Items);

        var blueHair = imported.Entries.Single(entry => !entry.IsSpecial && entry.Canonical == "blue_hair");
        Assert.True(blueHair.CanAdd);
        Assert.Null(blueHair.PromptToken);
        Assert.Equal(blueHair.Canonical, blueHair.EffectivePromptToken);
    }

    [ProductionFact]
    public void LegacyCatalogPayloadWithoutPromptTokenUsesCanonicalFallback()
    {
        var catalog = CatalogDatabase.Open(Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!);
        var blueHair = catalog.Entries.Single(entry => entry.Canonical == "blue_hair" && !entry.IsSpecial);
        Assert.Null(blueHair.PromptToken);
        Assert.Equal(blueHair.Canonical, blueHair.EffectivePromptToken);
        Assert.True(blueHair.CanAdd);
    }

    private static string Normalize(string value) => value.Trim().ToLowerInvariant().Replace(' ', '_');

    private static IReadOnlyDictionary<int, (string Decision, string NewCanonical)> Expected() => new Dictionary<int, (string, string)>
    {
        [550] = ("NO_SAFE_CANONICAL", ""), [722] = ("ORIGINAL_IS_CANONICAL", "loli"), [725] = ("EXACT_CANONICAL", "covered_nipples"),
        [783] = ("ORIGINAL_IS_CANONICAL", "tucked_penis"), [1251] = ("NO_SAFE_CANONICAL", ""), [1252] = ("NO_SAFE_CANONICAL", ""),
        [1253] = ("NO_SAFE_CANONICAL", ""), [1254] = ("NO_SAFE_CANONICAL", ""), [1255] = ("NO_SAFE_CANONICAL", ""),
        [1256] = ("NO_SAFE_CANONICAL", ""), [1361] = ("NO_SAFE_CANONICAL", ""), [1421] = ("EXACT_CANONICAL", "tucked_penis"),
        [1422] = ("EXACT_CANONICAL", "tucked_penis"), [1502] = ("NO_SAFE_CANONICAL", ""), [1575] = ("NO_SAFE_CANONICAL", ""),
        [1576] = ("EXACT_CANONICAL", "loli"), [1787] = ("ORIGINAL_IS_CANONICAL", "vaginal_prolapse"), [2528] = ("NO_SAFE_CANONICAL", ""),
        [2529] = ("NO_SAFE_CANONICAL", ""), [2530] = ("NO_SAFE_CANONICAL", ""), [2531] = ("NO_SAFE_CANONICAL", ""),
        [2537] = ("NO_SAFE_CANONICAL", ""), [2546] = ("NO_SAFE_CANONICAL", ""), [2634] = ("NO_SAFE_CANONICAL", ""),
        [2635] = ("NO_SAFE_CANONICAL", "")
    };
}
