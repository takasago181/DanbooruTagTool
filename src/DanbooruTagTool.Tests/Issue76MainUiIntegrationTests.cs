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
    public void Special_navigation_uses_three_shallow_v2_axes_not_old_tree()
    {
        var vm = Vm();
        var special = Assert.Single(vm.Navigation, node => node.Key == "special");
        Assert.Equal(["種類から探す", "部位から探す", "テーマから探す"], special.Children.Select(node => node.Label).ToArray());
        Assert.DoesNotContain(special.Children.SelectMany(node => node.Children), node => node.Label == "旧細分類");
    }

    [Fact]
    public void Tool_mouth_bdsm_and_filter_keeps_current_cards_and_deduplicates_canonical()
    {
        var vm = Vm();
        vm.NavigateTo("special-v2:kind:TOOL_OBJECT");
        vm.ToggleSpecialFacet.Execute(vm.SpecialBodyOptions.Single(option => option.Id == "MOUTH_ORAL"));
        vm.ToggleSpecialFacet.Execute(vm.SpecialThemeOptions.Single(option => option.Id == "BDSM_RESTRAINT"));

        var row = Assert.Single(vm.Results);
        Assert.Equal("ball_gag", row.English);
        Assert.Equal("道具・物 × 口・口内 × 拘束・BDSM", vm.BrowseLabel);
        Assert.Contains("種類 > 道具・物", row.Breadcrumb);
        Assert.Contains("部位 > 口・口内", row.Breadcrumb);
        Assert.Contains("テーマ > 拘束・BDSM", row.Breadcrumb);
    }

    [Fact]
    public void Active_facets_intersect_existing_search_without_changing_relevance_order()
    {
        var vm = Vm();
        vm.NavigateTo("special-v2:body:MOUTH_ORAL");
        vm.Query = "ball_gag";
        vm.RefreshResults();

        Assert.Equal(["ball_gag"], vm.Results.Select(row => row.English).ToArray());
    }

    [Fact]
    public void Clearing_facets_returns_to_special_root_and_keeps_search_text()
    {
        var vm = Vm();
        vm.NavigateTo("special-v2:theme:BDSM_RESTRAINT");
        vm.Query = "ball_gag";
        vm.RefreshResults();

        vm.ClearSpecialFacets.Execute(null);

        Assert.Equal("special", vm.BrowseKey);
        Assert.Equal("ball_gag", vm.Query);
        Assert.False(vm.HasSpecialFacets);
    }

    [Fact]
    public void One_step_back_removes_only_the_latest_special_filter_condition()
    {
        var vm = Vm();
        vm.NavigateTo("special-v2:kind:TOOL_OBJECT");
        vm.ToggleSpecialFacet.Execute(vm.SpecialBodyOptions.Single(option => option.Id == "MOUTH_ORAL"));
        vm.ToggleSpecialFacet.Execute(vm.SpecialThemeOptions.Single(option => option.Id == "BDSM_RESTRAINT"));

        vm.UndoSpecialFacet.Execute(null);
        Assert.Equal("道具・物 × 口・口内", vm.BrowseLabel);
        Assert.True(vm.HasSpecialFacets);

        vm.UndoSpecialFacet.Execute(null);
        Assert.Equal("道具・物", vm.BrowseLabel);

        vm.UndoSpecialFacet.Execute(null);
        Assert.Equal("special", vm.BrowseKey);
        Assert.False(vm.HasSpecialFacets);
    }

    [Fact]
    public void Fixed_special_axis_headings_do_not_replace_the_active_leaf_filter()
    {
        var vm = Vm();
        vm.NavigateTo("special-v2:kind:TOOL_OBJECT");
        var special = Assert.Single(vm.Navigation, node => node.Key == "special");
        var heading = Assert.Single(special.Children, node => node.Key == "special-v2:body");

        vm.Navigate.Execute(heading);

        Assert.Equal("special-v2:kind:TOOL_OBJECT", vm.BrowseKey);
        Assert.Equal("道具・物", vm.BrowseLabel);
    }

    [Fact]
    public void Persisted_old_special_path_is_migrated_to_v2_root_without_touching_prompt_state()
    {
        var state = new UserState(new WorkspaceSnapshot([], null), new UiState(Browse: "special:OLD>OLD_CHILD"));
        var vm = Vm(new MemoryStore(state));
        Assert.Equal("special", vm.BrowseKey);
    }
}
