using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue117UnifiedBrowseTests
{
    [Fact]
    public void ContentIntent_MapsContextualIntoBothNarrowedViews_AndKeepsUnclassifiedAllOnly()
    {
        var catalog = CatalogWithIntentFixtures();
        var index = new UnifiedBrowseIndex(catalog);

        var generalPurpose = UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.GeneralPurpose };
        var sexual = UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual };

        Assert.Equal(
            new[] { "blue_hair", "breastfeeding" },
            index.Browse(generalPurpose).Select(entry => entry.Canonical).OrderBy(value => value).ToArray());

        Assert.Equal(
            new[] { "anal_sex", "breastfeeding" },
            index.Browse(sexual).Select(entry => entry.Canonical).OrderBy(value => value).ToArray());

        Assert.Contains(index.Browse(UnifiedBrowseState.Neutral), entry => entry.Canonical == "mystery_tag");
        Assert.DoesNotContain(index.Browse(generalPurpose), entry => entry.Canonical == "mystery_tag");
        Assert.DoesNotContain(index.Browse(sexual), entry => entry.Canonical == "mystery_tag");
    }

    [Fact]
    public void FilterSearchHits_PreservesExistingSearchOrder()
    {
        var catalog = CatalogWithIntentFixtures();
        var index = new UnifiedBrowseIndex(catalog);
        var byCanonical = catalog.Entries.ToDictionary(entry => entry.Canonical!, StringComparer.Ordinal);

        SearchHit[] ranked =
        [
            new(byCanonical["breastfeeding"], 1),
            new(byCanonical["anal_sex"], 2),
            new(byCanonical["blue_hair"], 3),
            new(byCanonical["mystery_tag"], 4)
        ];

        var filtered = index.FilterSearchHits(
            ranked,
            UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual });

        Assert.Equal(new[] { "breastfeeding", "anal_sex" }, filtered.Select(hit => hit.Entry.Canonical).ToArray());
    }

    [Fact]
    public void DictionaryWorkspace_NeutralTagsDoesNotEagerlyEnumerateOrdinaryPopulation()
    {
        var catalog = CatalogWithIntentFixtures();
        var workspace = new PromptWorkspace(new PromptParser(catalog));
        var vm = new DictionaryWorkspaceViewModel(
            catalog,
            workspace,
            new PendingGeneralBrowseProvider(),
            () => { },
            () => true);

        vm.Restore(new UiState(BrowseScope: "Tags"));
        vm.RefreshResults();

        Assert.Equal(UnifiedBrowseScope.Tags, vm.Scope);
        Assert.True(vm.IsNeutralTags);
        Assert.Empty(vm.Results);
    }

    [Fact]
    public void DictionaryWorkspace_DedicatedScopesIgnoreOrdinaryContentIntent_AndKeepQuery()
    {
        CatalogEntry[] entries =
        [
            Entry("g1", "blue_hair", "General", SexualIntentClass.NonSexual),
            Entry("c1", "hatsune_miku", "Character", null),
            Entry("a1", "artist_name", "Artist", null)
        ];
        var catalog = new Catalog(entries);
        var workspace = new PromptWorkspace(new PromptParser(catalog));
        var vm = new DictionaryWorkspaceViewModel(
            catalog,
            workspace,
            new PendingGeneralBrowseProvider(),
            () => { },
            () => true);

        vm.Restore(new UiState(BrowseScope: "Character", ContentIntent: "SEXUAL"));
        vm.Query = "hatsune";
        vm.RefreshResults();

        Assert.Equal(ContentIntentFilter.Sexual, vm.ContentIntent);
        Assert.Equal(UnifiedBrowseScope.Character, vm.Scope);
        Assert.Single(vm.Results);
        Assert.Equal("Character", vm.Results[0].Entry.EffectiveCategory);

        vm.SetScope(UnifiedBrowseScope.Artist);

        Assert.Equal("hatsune", vm.Query);
        Assert.Equal(UnifiedBrowseScope.Artist, vm.Scope);
    }

    [Fact]
    public void FilterSearchHits_DeduplicatesOverlapWithoutRerankingFirstOccurrence()
    {
        CatalogEntry[] entries =
        [
            Entry("g-overlap", "shared_tag", "General", SexualIntentClass.Contextual),
            Entry("s-overlap", "shared_tag", "Special", SexualIntentClass.Contextual),
            Entry("g-other", "other_tag", "General", SexualIntentClass.NonSexual)
        ];
        var catalog = new Catalog(entries);
        var index = new UnifiedBrowseIndex(catalog);
        SearchHit[] hits =
        [
            new(entries[1], 10),
            new(entries[2], 9),
            new(entries[0], 8)
        ];

        var filtered = index.FilterSearchHits(hits, UnifiedBrowseState.Neutral);

        Assert.Equal(2, filtered.Count);
        Assert.Same(entries[1], filtered[0].Entry);
        Assert.Same(entries[2], filtered[1].Entry);
    }

    [Fact]
    public void NeutralGuidance_IsHiddenAsSoonAsQueryIsEntered()
    {
        var catalog = CatalogWithIntentFixtures();
        var workspace = new PromptWorkspace(new PromptParser(catalog));
        var vm = new DictionaryWorkspaceViewModel(
            catalog,
            workspace,
            new PendingGeneralBrowseProvider(),
            () => { },
            () => true);

        vm.Restore(new UiState(BrowseScope: "Tags"));
        Assert.True(vm.ShowNeutralGuidance);

        vm.Query = "blue";
        Assert.False(vm.ShowNeutralGuidance);
    }

    [Fact]
    public void UnifiedTaxonomy_HasExactlyNineteenOrdinaryDiscoveryRoutes()
    {
        Assert.Equal(19, UnifiedBrowseTaxonomy.Routes.Length);
        Assert.DoesNotContain(UnifiedBrowseTaxonomy.Routes, route => route.Label is "General" or "Special");
        Assert.Equal("内容区分・レーティング", UnifiedBrowseTaxonomy.Routes[^1].Label);
    }

    [Fact]
    public void UnifiedIndex_DeduplicatesGeneralSpecialOverlapByCanonicalIdentity()
    {
        CatalogEntry[] entries =
        [
            Entry("g-overlap", "shared_tag", "General", SexualIntentClass.Contextual),
            Entry("s-overlap", "shared_tag", "Special", SexualIntentClass.Contextual) with
            {
                SpecialBrowseV2 = new(
                    "ACTION_CONTACT",
                    [],
                    [],
                    SpecialBrowseV2Status.HumanResolved)
            }
        ];
        var index = new UnifiedBrowseIndex(new Catalog(entries));

        Assert.Single(index.Identities);
        Assert.Single(index.Browse(UnifiedBrowseState.Neutral));
    }

    [Fact]
    public void DeepDiscovery_RequiresDirectBrowseSpecialBacking()
    {
        var referenceOnly = Entry("s-ref", "reference_only_tag", "Special", SexualIntentClass.Sexual) with
        {
            ProductFit = "KEEP_REFERENCE_ONLY",
            SpecialBrowseV2 = new(
                "ACTION_CONTACT",
                [],
                [],
                SpecialBrowseV2Status.HumanResolved)
        };
        var direct = Entry("s-direct", "direct_tag", "Special", SexualIntentClass.Sexual) with
        {
            SpecialBrowseV2 = new(
                "ACTION_CONTACT",
                [],
                [],
                SpecialBrowseV2Status.HumanResolved)
        };
        var index = new UnifiedBrowseIndex(new Catalog([referenceOnly, direct]));
        var deepOnly = UnifiedBrowseState.Neutral with { DeepOnly = true };

        Assert.DoesNotContain(index.Browse(deepOnly), entry => entry.Canonical == "reference_only_tag");
        Assert.Contains(index.Browse(deepOnly), entry => entry.Canonical == "direct_tag");
    }

    [Fact]
    public void FrozenIssue118Authority_HasExactPopulationCountsAndFiveExplicitUnknowns()
    {
        var root = FindRepoRoot();
        var rows = AcceptedAssetImporter.Csv(Path.Combine(root, Issue118SexualIntentOverlay.RelativePath));

        Assert.Equal(Issue118SexualIntentOverlay.IdentityCount, rows.Count);
        Assert.Equal(Issue118SexualIntentOverlay.AutoHighConfidenceCount, rows.Count(row => row["review_status"] == "AUTO_HIGH_CONF"));
        Assert.Equal(Issue118SexualIntentOverlay.HumanReviewedCount, rows.Count(row => row["review_status"] == "HUMAN_REVIEWED"));
        Assert.Equal(Issue118SexualIntentOverlay.UnclassifiedCount, rows.Count(row => row["review_status"] == "UNCLASSIFIED"));
        Assert.Equal(Issue118SexualIntentOverlay.SexualCount, rows.Count(row => row["sexual_intent"] == "SEXUAL"));
        Assert.Equal(Issue118SexualIntentOverlay.ContextualCount, rows.Count(row => row["sexual_intent"] == "CONTEXTUAL"));
        Assert.Equal(Issue118SexualIntentOverlay.NonSexualCount, rows.Count(row => row["sexual_intent"] == "NON_SEXUAL"));

        var unknowns = rows.Where(row => row["review_status"] == "UNCLASSIFIED")
            .Select(row => row["identity_key"]).OrderBy(value => value, StringComparer.Ordinal).ToArray();
        Assert.Equal(
            new[] { "cock-tail", "insertion_threshold_(meme)", "knee_boobs", "lilistia", "powerful_ass" },
            unknowns);
        Assert.All(rows.Where(row => row["review_status"] == "UNCLASSIFIED"), row => Assert.Equal("", row["sexual_intent"]));
    }

    [Fact]
    public void SelectedZeroCountFacet_RemainsVisibleSoItCanBeRemoved()
    {
        var option = new BrowseFacetOptionViewModel(BrowseFacetKind.BodySite, "MOUTH_ORAL", "口・口内")
        {
            Count = 0,
            Selected = true
        };

        Assert.True(option.IsVisible);
        option.Selected = false;
        Assert.False(option.IsVisible);
    }

    [Fact]
    public void UnifiedOverlay_AddsOnlyExactOverridesAndPreservesPoseCameraSceneSemantics()
    {
        using var authority = new TempDirectory();
        WriteUnifiedProfile(authority.Path);

        var entries = OverrideEntries()
            .Concat([
                SpecialEntry(1001, "pose_fixture"),
                SpecialEntry(1002, "camera_fixture"),
                SpecialEntry(1003, "scene_fixture"),
                SpecialEntry(1004, "reaction_fixture")
            ]).ToArray();
        var catalog = new Catalog(entries);
        var baked = UnifiedBrowseOverlay.Bake(catalog, authority.Path);
        var byId = baked.ToDictionary(entry => entry.Id, StringComparer.Ordinal);

        foreach (var id in new[] { 436, 647, 649, 650, 735, 961 })
            Assert.Contains("EXPRESSION_GAZE", byId[$"S:{id}"].UnifiedBrowseRouteIds);

        Assert.Contains("ACTION_CONTACT", byId["S:436"].UnifiedBrowseRouteIds);
        Assert.Contains("POSE_POSITION", byId["S:1001"].UnifiedBrowseRouteIds);
        Assert.Contains("COMPOSITION_CAMERA", byId["S:1002"].UnifiedBrowseRouteIds);
        Assert.Contains("SCENE_BACKGROUND", byId["S:1003"].UnifiedBrowseRouteIds);
        Assert.DoesNotContain("EXPRESSION_GAZE", byId["S:1004"].UnifiedBrowseRouteIds);
    }

    [Fact]
    public void UnifiedOverlay_FailsClosedWhenOverrideIdAndCanonicalDoNotMatch()
    {
        using var authority = new TempDirectory();
        WriteUnifiedProfile(authority.Path);
        var entries = OverrideEntries().ToArray();
        entries[0] = entries[0] with { Canonical = "wrong_identity", English = "wrong_identity" };

        Assert.Throws<InvalidDataException>(() => UnifiedBrowseOverlay.Bake(new Catalog(entries), authority.Path));
    }

    private static IEnumerable<CatalogEntry> OverrideEntries()
    {
        yield return SpecialEntry(436, "rape_face") with { UnifiedBrowseRouteIds = ["ACTION_CONTACT"] };
        yield return SpecialEntry(647, "ahegao");
        yield return SpecialEntry(649, "naughty_face");
        yield return SpecialEntry(650, "torogao");
        yield return SpecialEntry(735, "looking_at_penis");
        yield return SpecialEntry(961, "looking_at_pussy");
    }

    private static CatalogEntry SpecialEntry(int id, string canonical)
        => Entry($"S:{id}", canonical, "Special", null);

    private static void WriteUnifiedProfile(string root)
    {
        var path = Path.Combine(root, AcceptedAssetImporter.ProductionProfileRelativePath);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        File.WriteAllText(path,
            "SpecialID,GenerationFamily,CompositionRoleOverride\r\n" +
            "1001,POSE_COMPOSITION,pose\r\n" +
            "1002,POSE_COMPOSITION,camera\r\n" +
            "1003,SCENE_CONTEXT,\r\n" +
            "1004,REACTION_STATE,\r\n");
    }

    private static string FindRepoRoot()
    {
        DirectoryInfo? dir = new(AppContext.BaseDirectory);
        while (dir != null && !File.Exists(Path.Combine(dir.FullName, "AGENTS.md"))) dir = dir.Parent;
        return dir?.FullName ?? throw new DirectoryNotFoundException("Repository root not found");
    }

    private static Catalog CatalogWithIntentFixtures()
        => new(
        [
            Entry("g1", "blue_hair", "General", SexualIntentClass.NonSexual),
            Entry("g2", "breastfeeding", "General", SexualIntentClass.Contextual),
            Entry("s1", "anal_sex", "Special", SexualIntentClass.Sexual),
            Entry("g3", "mystery_tag", "General", null)
        ]);

    private static CatalogEntry Entry(string id, string canonical, string category, SexualIntentClass? intent)
        => new(
            id,
            canonical,
            canonical,
            canonical,
            category == "Special",
            100,
            [],
            [],
            [],
            BrowseClassification: category == "General" ? BrowseClassificationStatus.Proposed : BrowseClassificationStatus.NotApplicable)
        {
            TagCategory = category,
            SexualIntent = intent,
            SexualIntentStatus = intent is null
                ? SexualIntentClassificationStatus.Unclassified
                : SexualIntentClassificationStatus.HumanReviewed
        };
}
