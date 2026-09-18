using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue76MainUiIntegrationTests
{
    private sealed class MemoryStore(UserState? initial = null) : IUserStateStore
    {
        public UserState? State { get; private set; } = initial;
        public UserState? Load() => State;
        public void Save(UserState state) => State = state;
    }

    private sealed class Clipboard : IClipboardService
    {
        public string Text { get; set; } = "";
        public string Read() => Text;
        public void Write(string text) => Text = text;
    }

    private static HashSet<string> Set(params string[] values) => new(values, StringComparer.Ordinal);

    private static CatalogEntry Entry(string id, string canonical, string japanese, long usage) =>
        new(id, canonical, canonical, japanese, true, usage, [], [], [new BrowsePath("OLD", "旧分類", "OLD_CHILD", "旧細分類")], "KEEP");

    private static Catalog Catalog() => new([
        Entry("S:1", "ball_gag", "ボールギャグ", 100),
        Entry("S:2", "ball_gag", "ボールギャグ別表現", 90),
        Entry("S:3", "fellatio", "フェラチオ", 80),
        Entry("S:4", "anal_beads", "アナルビーズ", 70),
        Entry("S:5", "bdsm", "BDSM", 60)
    ]);

    private static SpecialBrowseV2Index Index() => new([
        new("S:1", "TOOL_OBJECT", Set("MOUTH_ORAL"), Set("BDSM_RESTRAINT"), SpecialBrowseV2Status.AutoCandidate),
        new("S:2", "TOOL_OBJECT", Set("MOUTH_ORAL"), Set("BDSM_RESTRAINT"), SpecialBrowseV2Status.AutoCandidate),
        new("S:3", "ACTION_CONTACT", Set("MOUTH_ORAL", "MALE_GENITAL"), Set(), SpecialBrowseV2Status.AutoCandidate),
        new("S:4", "TOOL_OBJECT", Set("BUTTOCK_ANAL"), Set(), SpecialBrowseV2Status.AutoCandidate),
        new("S:5", null, Set(), Set("BDSM_RESTRAINT"), SpecialBrowseV2Status.AutoCandidate)
    ]);

    private static MainViewModel Vm(MemoryStore? store = null)
        => new(Catalog(), store ?? new(), new Clipboard(), specialBrowse: Index());

    [Fact]
    public void Unified_navigation_replaces_visible_special_tree_with_nineteen_routes_and_three_scopes()
    {
        var navigation = Vm().Dictionary.Navigation;

        Assert.Equal(22, navigation.Count);
        Assert.Equal(UnifiedBrowseTaxonomy.Routes.Select(route => route.Label), navigation.Take(19).Select(node => node.Label));
        Assert.Equal(["キャラクター", "作品", "作者"], navigation.Skip(19).Select(node => node.Label).ToArray());
        Assert.DoesNotContain(navigation, node => node.Key is "special" or "general");
        Assert.All(navigation, node => Assert.Empty(node.Children));
    }

    [Fact]
    public void Tool_mouth_bdsm_filter_keeps_current_cards_and_deduplicates_canonical()
    {
        var vm = Vm().Dictionary;
        vm.NavigateTo("route:TOOL_OBJECT");
        vm.ToggleBodySite("MOUTH_ORAL");
        vm.ToggleTheme("BDSM_RESTRAINT");

        var row = Assert.Single(vm.Results);
        Assert.Equal("ball_gag", row.English);
        Assert.Equal("道具・小物", vm.BrowseLabel);
        Assert.Contains("道具・小物", row.Breadcrumb);
        Assert.Contains("部位 > 口・口内", row.Breadcrumb);
        Assert.Contains("テーマ > 拘束・BDSM", row.Breadcrumb);
    }

    [Fact]
    public void Active_unified_facets_intersect_existing_search_without_changing_relevance_order()
    {
        var vm = Vm().Dictionary;
        vm.ToggleBodySite("MOUTH_ORAL");
        vm.Query = "ball_gag";
        vm.RefreshResults();

        Assert.Equal(["ball_gag"], vm.Results.Select(row => row.English).ToArray());
    }

    [Fact]
    public void Clearing_unified_browse_returns_to_neutral_tags_and_keeps_search_text()
    {
        var vm = Vm().Dictionary;
        vm.ToggleTheme("BDSM_RESTRAINT");
        vm.Query = "ball_gag";
        vm.RefreshResults();

        vm.ClearUnifiedBrowse();

        Assert.Equal("tags", vm.BrowseKey);
        Assert.Equal("ball_gag", vm.Query);
        Assert.True(vm.IsNeutralTags);
    }

    [Fact]
    public void One_step_back_removes_only_latest_unified_condition()
    {
        var vm = Vm().Dictionary;
        vm.NavigateTo("route:TOOL_OBJECT");
        vm.ToggleBodySite("MOUTH_ORAL");
        vm.ToggleTheme("BDSM_RESTRAINT");

        vm.UndoUnifiedBrowse();
        Assert.Contains("MOUTH_ORAL", vm.BodySiteIds);
        Assert.Empty(vm.ThemeIds);
        Assert.Equal("TOOL_OBJECT", vm.PrimaryRouteId);

        vm.UndoUnifiedBrowse();
        Assert.Empty(vm.BodySiteIds);
        Assert.Equal("TOOL_OBJECT", vm.PrimaryRouteId);

        vm.UndoUnifiedBrowse();
        Assert.True(vm.IsNeutralTags);
    }

    [Fact]
    public void Body_site_facets_use_and_semantics()
    {
        var vm = Vm().Dictionary;
        vm.ToggleBodySite("MOUTH_ORAL");
        vm.ToggleBodySite("MALE_GENITAL");

        Assert.Equal(["fellatio"], vm.Results.Select(row => row.English).ToArray());
    }

    [Fact]
    public void Selecting_another_primary_route_replaces_the_route_condition()
    {
        var vm = Vm().Dictionary;
        vm.NavigateTo("route:ACTION_CONTACT");
        vm.NavigateTo("route:TOOL_OBJECT");

        Assert.Equal("道具・小物", vm.BrowseLabel);
        Assert.DoesNotContain(vm.Results, row => row.English == "fellatio");
        Assert.Contains(vm.Results, row => row.English == "ball_gag");
    }

    [Fact]
    public void Theme_facet_can_find_an_entry_without_a_primary_kind_route()
    {
        var vm = Vm().Dictionary;
        vm.ToggleTheme("BDSM_RESTRAINT");

        Assert.Contains(vm.Results, row => row.English == "bdsm");
    }

    [Fact]
    public void Toggling_one_body_facet_keeps_the_other_conditions()
    {
        var vm = Vm().Dictionary;
        vm.ToggleBodySite("MOUTH_ORAL");
        vm.ToggleBodySite("MALE_GENITAL");
        vm.ToggleBodySite("MALE_GENITAL");

        Assert.Contains(vm.Results, row => row.English == "ball_gag");
        Assert.DoesNotContain(vm.Results, row => row.English == "anal_beads");
    }

    [Fact]
    public void Non_browse_status_is_excluded_from_matching_and_counts()
    {
        var index = new SpecialBrowseV2Index([
            new("S:1", "TOOL_OBJECT", Set(), Set(), SpecialBrowseV2Status.AutoCandidate),
            new("S:2", "TOOL_OBJECT", Set(), Set(), SpecialBrowseV2Status.ReferenceOnlyNoDirectBrowse),
            new("S:3", "TOOL_OBJECT", Set(), Set(), SpecialBrowseV2Status.OutOfScopeNoBrowse)
        ]);

        Assert.True(index.Matches("S:1", SpecialBrowseV2Filter.Empty));
        Assert.False(index.Matches("S:2", SpecialBrowseV2Filter.Empty));
        Assert.False(index.Matches("S:3", SpecialBrowseV2Filter.Empty));
        Assert.Equal(1, index.Count(SpecialBrowseV2Filter.Empty));
    }

    [Fact]
    public void Facet_counts_dedupe_duplicate_canonical_identity()
    {
        var index = new SpecialBrowseV2Index([
            new("S:1", "TOOL_OBJECT", Set(), Set(), SpecialBrowseV2Status.AutoCandidate, "same_tag"),
            new("S:2", "TOOL_OBJECT", Set(), Set(), SpecialBrowseV2Status.AutoCandidate, "same_tag")
        ]);

        Assert.Equal(1, index.Count(SpecialBrowseV2Filter.Empty));
    }

    [ProductionFact]
    public void Production_baked_special_mapping_preserves_population_statuses_and_examples()
    {
        var catalog = CatalogDatabase.Open(Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!);
        var baked = new Catalog(SpecialBrowseV2Overlay.Bake(catalog));
        using var temp = new TempDirectory();
        var catalogPath = new PortablePaths(temp.Path).Catalog;
        CatalogDatabase.Build(catalogPath, baked.Entries, "Issue #76 production bake test");
        var persisted = CatalogDatabase.Open(catalogPath);
        var index = SpecialBrowseV2Overlay.FromCatalog(persisted);

        Assert.Equal(AcceptedAssetImporter.ProductionSpecialCount, index.Entries.Count);
        Assert.Equal(2718, index.Entries.Count(entry => entry.Status == SpecialBrowseV2Status.AutoCandidate));
        Assert.Equal(315, index.Entries.Count(entry => entry.Status == SpecialBrowseV2Status.HumanResolved));
        Assert.Equal(5, index.Entries.Count(entry => entry.Status == SpecialBrowseV2Status.DeferProductFitReview));
        Assert.Equal(0, index.Entries.Count(entry => entry.Status == SpecialBrowseV2Status.OutOfScopeNoBrowse));
        Assert.Equal(21, index.Entries.Count(entry => entry.Status == SpecialBrowseV2Status.ReferenceOnlyNoDirectBrowse));
        Assert.Equal(
            new[] { 977, 597, 324, 347, 304, 171, 119, 120, 60 },
            SpecialBrowseV2Taxonomy.Kinds.Select(kind => index.Entries.Count(entry => entry.KindId == kind.Id)).ToArray());
        Assert.Equal(
            new[] { 307, 361, 187, 189, 140, 20 },
            SpecialBrowseV2Taxonomy.BodySites.Select(body => index.Entries.Count(entry => entry.BodySiteIds.Contains(body.Id))).ToArray());
        Assert.Equal(
            new[] { 385, 87, 46 },
            SpecialBrowseV2Taxonomy.Themes.Select(theme => index.Entries.Count(entry => entry.ThemeIds.Contains(theme.Id))).ToArray());
        Assert.Equal(14, index.Entries.Count(entry => entry.CanBrowse && entry.KindId is null));

        var analBeads = catalog.Resolve("anal_beads");
        Assert.NotNull(analBeads);
        var analFilter = SpecialBrowseV2Filter.Empty
            .WithKind("TOOL_OBJECT")
            .ToggleBodySite("BUTTOCK_ANAL");
        Assert.True(index.Matches(analBeads.Id, analFilter));

        var ballGag = catalog.Resolve("ball_gag");
        Assert.NotNull(ballGag);
        var ballGagFilter = SpecialBrowseV2Filter.Empty
            .WithKind("TOOL_OBJECT")
            .ToggleBodySite("MOUTH_ORAL")
            .ToggleTheme("BDSM_RESTRAINT");
        Assert.True(index.Matches(ballGag.Id, ballGagFilter));

        var browsable = index.IntersectInInputOrder(
            catalog.Entries.Where(entry => entry.IsSpecial && entry.CanBrowse),
            SpecialBrowseV2Filter.Empty);
        Assert.Equal(browsable.Count, browsable
            .Select(entry => entry.Canonical ?? entry.Id)
            .Distinct(StringComparer.Ordinal)
            .Count());
        Assert.DoesNotContain(index.Entries, entry => entry.CanBrowse && entry.Status is
            SpecialBrowseV2Status.ReferenceOnlyNoDirectBrowse or
            SpecialBrowseV2Status.DeferProductFitReview or
            SpecialBrowseV2Status.OutOfScopeNoBrowse);
    }

    [Fact]
    public void Persisted_old_special_path_is_migrated_to_neutral_tags_without_touching_prompt_state()
    {
        var state = new UserState(new WorkspaceSnapshot([], null), new UiState(Browse: "special:OLD>OLD_CHILD"));
        var vm = Vm(new MemoryStore(state));

        Assert.Equal("tags", vm.Dictionary.BrowseKey);
        Assert.True(vm.Dictionary.IsNeutralTags);
    }
}
