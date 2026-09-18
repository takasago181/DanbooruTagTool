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
