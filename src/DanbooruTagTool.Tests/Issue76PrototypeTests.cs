using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue76PrototypeTests
{
    private static HashSet<string> Set(params string[] values) => new(values, StringComparer.Ordinal);

    private static SpecialBrowseV2Index Index() => new([
        new("S:104", "ACTION_CONTACT", Set("MOUTH_ORAL", "MALE_GENITAL"), Set(), SpecialBrowseV2Status.AutoCandidate),
        new("S:681", "ACTION_CONTACT", Set("MOUTH_ORAL", "FEMALE_GENITAL"), Set(), SpecialBrowseV2Status.AutoCandidate),
        new("S:266", "TOOL_OBJECT", Set("BUTTOCK_ANAL"), Set(), SpecialBrowseV2Status.AutoCandidate),
        new("S:1814", "TOOL_OBJECT", Set("MOUTH_ORAL"), Set("BDSM_RESTRAINT"), SpecialBrowseV2Status.AutoCandidate),
        new("S:416", null, Set(), Set("BDSM_RESTRAINT"), SpecialBrowseV2Status.AutoCandidate),
        new("S:470", null, Set(), Set("INJURY_R18G"), SpecialBrowseV2Status.AutoCandidate),
        new("S:9991", "TOOL_OBJECT", Set("BUTTOCK_ANAL"), Set(), SpecialBrowseV2Status.ReferenceOnlyNoDirectBrowse),
        new("S:9992", "ACTION_CONTACT", Set(), Set(), SpecialBrowseV2Status.DeferProductFitReview),
        new("S:9993", "BODY_STATE", Set(), Set(), SpecialBrowseV2Status.OutOfScopeNoBrowse)
    ]);

    private static Catalog TestCatalog() => new([
        Entry("S:104", "fellatio", "フェラチオ", 97833),
        Entry("S:681", "cunnilingus", "クンニリングス", 16303),
        Entry("S:266", "anal beads", "アナルビーズ", 5000),
        Entry("S:1814", "ball gag", "ボールギャグ", 4000),
        Entry("S:416", "bdsm", "BDSM", 3000),
        Entry("S:470", "guro", "グロ", 2000)
    ]);

    private static CatalogEntry Entry(string id, string english, string japanese, long usage) =>
        new(id, english, english, japanese, true, usage, [], [], [], "KEEP");

    [Fact]
    public void Body_sites_use_and_semantics()
    {
        var filter = SpecialBrowseV2Filter.Empty
            .ToggleBodySite("MOUTH_ORAL")
            .ToggleBodySite("MALE_GENITAL");

        Assert.Equal(["S:104"], Index().FilterIdsInInputOrder(["S:104", "S:681", "S:1814"], filter));
    }

    [Fact]
    public void Cross_axis_filters_use_and_semantics()
    {
        var filter = SpecialBrowseV2Filter.Empty
            .WithKind("TOOL_OBJECT")
            .ToggleBodySite("MOUTH_ORAL")
            .ToggleTheme("BDSM_RESTRAINT");

        Assert.Equal(["S:1814"], Index().FilterIdsInInputOrder(["S:104", "S:1814", "S:416"], filter));
    }

    [Fact]
    public void Theme_native_entry_does_not_need_fake_kind()
    {
        var filter = SpecialBrowseV2Filter.Empty.ToggleTheme("BDSM_RESTRAINT");

        Assert.True(Index().Matches("S:416", filter));
    }

    [Fact]
    public void Selecting_another_kind_replaces_kind_instead_of_creating_or_state()
    {
        var first = SpecialBrowseV2Filter.Empty.WithKind("ACTION_CONTACT");
        var second = first.WithKind("TOOL_OBJECT");

        Assert.Equal("TOOL_OBJECT", second.KindId);
        Assert.False(Index().Matches("S:104", second));
        Assert.True(Index().Matches("S:266", second));
    }

    [Fact]
    public void Toggling_body_or_theme_removes_only_that_chip()
    {
        var filter = SpecialBrowseV2Filter.Empty
            .ToggleBodySite("MOUTH_ORAL")
            .ToggleBodySite("MALE_GENITAL")
            .ToggleTheme("BDSM_RESTRAINT");

        var next = filter.ToggleBodySite("MALE_GENITAL");

        Assert.Contains("MOUTH_ORAL", next.BodySiteIds);
        Assert.DoesNotContain("MALE_GENITAL", next.BodySiteIds);
        Assert.Contains("BDSM_RESTRAINT", next.ThemeIds);
    }

    [Fact]
    public void Non_default_browse_statuses_are_excluded()
    {
        var index = Index();
        var filter = SpecialBrowseV2Filter.Empty;

        Assert.False(index.Matches("S:9991", filter));
        Assert.False(index.Matches("S:9992", filter));
        Assert.False(index.Matches("S:9993", filter));
    }

    [Fact]
    public void Search_intersection_preserves_existing_result_order()
    {
        var filter = SpecialBrowseV2Filter.Empty.ToggleBodySite("MOUTH_ORAL");

        var input = new[] { "S:1814", "S:681", "S:104", "S:266" };
        var result = Index().FilterIdsInInputOrder(input, filter);

        Assert.Equal(["S:1814", "S:681", "S:104"], result);
    }

    [Fact]
    public void Facet_counts_mean_count_after_adding_required_condition()
    {
        var index = Index();
        var current = SpecialBrowseV2Filter.Empty.ToggleBodySite("MOUTH_ORAL");

        Assert.Equal(1, index.CountWithBodySite(current, "MALE_GENITAL"));
        Assert.Equal(1, index.CountWithTheme(current, "BDSM_RESTRAINT"));
        Assert.Equal(2, index.CountWithKind(current, "ACTION_CONTACT"));
    }

    [Fact]
    public void Clear_returns_empty_filter()
    {
        var filter = SpecialBrowseV2Filter.Empty
            .WithKind("ACTION_CONTACT")
            .ToggleBodySite("MOUTH_ORAL")
            .ToggleTheme("BDSM_RESTRAINT");

        Assert.True(filter.Clear().IsEmpty);
    }

    [Fact]
    public void Prototype_tree_start_clears_query_and_previous_facets()
    {
        var vm = new Issue76BrowsePrototypeViewModel(TestCatalog(), Index());
        var mouth = vm.BodyOptions.Single(option => option.Id == "MOUTH_ORAL");
        var male = vm.BodyOptions.Single(option => option.Id == "MALE_GENITAL");
        vm.ToggleFacet.Execute(mouth);
        vm.ToggleFacet.Execute(male);
        vm.Query = "fellatio";

        vm.StartFromTree("v2:body:BUTTOCK_ANAL");

        Assert.Equal("", vm.Query);
        Assert.Equal("適用中: 尻・肛門", vm.AppliedSummary);
        Assert.Equal(["S:266"], vm.Results.Select(row => row.Entry.Id).ToArray());
    }

    [Fact]
    public void Clearing_facets_does_not_clear_search_query()
    {
        var vm = new Issue76BrowsePrototypeViewModel(TestCatalog(), Index());
        var mouth = vm.BodyOptions.Single(option => option.Id == "MOUTH_ORAL");
        vm.ToggleFacet.Execute(mouth);
        vm.Query = "fellatio";

        vm.ClearFacets.Execute(null);

        Assert.Equal("fellatio", vm.Query);
        Assert.Equal(["S:104"], vm.Results.Select(row => row.Entry.Id).ToArray());
    }

    [Fact]
    public void Prototype_loader_parses_generated_sidecar_shape_without_promoting_reference_rows()
    {
        var path = Path.GetTempFileName();
        try
        {
            File.WriteAllText(path,
                "special_id,v2_kind_id,v2_body_sites,v2_themes,v2_status\n" +
                "104,ACTION_CONTACT,MOUTH_ORAL | MALE_GENITAL,,AUTO_CANDIDATE\n" +
                "9991,TOOL_OBJECT,BUTTOCK_ANAL,,REFERENCE_ONLY_NO_DIRECT_BROWSE\n");

            var index = Issue76SpecialBrowseV2Loader.Load(path, requireFullCoverage: false);

            Assert.True(index.Matches("S:104", SpecialBrowseV2Filter.Empty.ToggleBodySite("MOUTH_ORAL")));
            Assert.False(index.Matches("S:9991", SpecialBrowseV2Filter.Empty));
        }
        finally
        {
            File.Delete(path);
        }
    }
}
