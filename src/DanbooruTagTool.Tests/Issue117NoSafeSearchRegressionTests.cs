using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue117PortableCatalogFactAttribute : FactAttribute
{
    public Issue117PortableCatalogFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("DTT_ISSUE117_PORTABLE_CATALOG") == null)
            Skip = "Issue #117 portable catalog regression validation is opt-in.";
    }
}

public sealed class Issue117NoSafeSearchRegressionTests(ITestOutputHelper output)
{
    [Issue117PortableCatalogFact]
    public void NoSafeSpecialSurvivesEveryRuntimeSearchBoundary()
    {
        var path = Environment.GetEnvironmentVariable("DTT_ISSUE117_PORTABLE_CATALOG");
        Assert.False(string.IsNullOrWhiteSpace(path), "Set DTT_ISSUE117_PORTABLE_CATALOG to the portable catalog under investigation.");

        var catalog = CatalogDatabase.Open(path!);
        var runtime = Assert.IsAssignableFrom<IRuntimeCatalogQuery>(catalog);
        var special = catalog.Entries.SingleOrDefault(entry => entry.Id == "S:2531");
        Assert.NotNull(special);
        var general = Assert.Single(catalog.Entries, entry => !entry.IsSpecial && entry.Canonical == "socks");

        output.WriteLine($"special: id={special.Id}; english={special.English}; canonical={special.Canonical ?? "<null>"}; prompt={special.PromptToken ?? "<null>"}; effective={special.EffectivePromptToken ?? "<null>"}; product_fit={special.ProductFit}; can_search={special.CanSearch}; can_add={special.CanAdd}; sexual_intent={special.SexualIntent?.ToString() ?? "<null>"}; status={special.SexualIntentStatus}");
        output.WriteLine($"general: id={general.Id}; english={general.English}; canonical={general.Canonical ?? "<null>"}; aliases=[{string.Join("|", general.Aliases)}]; japanese_search=[{string.Join("|", general.JapaneseSearch)}]");

        Assert.Equal("S:2531", special.Id);
        Assert.Equal("naked socks", special.English);
        Assert.Null(special.Canonical);
        Assert.Equal("naked_socks", special.PromptToken);
        Assert.Equal("naked_socks", special.EffectivePromptToken);
        Assert.True(special.CanSearch);
        Assert.True(special.CanAdd);

        var resolveSurface = runtime.Resolve("naked socks");
        var resolveToken = runtime.Resolve("naked_socks");
        output.WriteLine($"resolve naked socks={resolveSurface?.Id ?? "<null>"}; naked_socks={resolveToken?.Id ?? "<null>"}");
        Assert.Equal(special.Id, resolveSurface?.Id);
        Assert.Equal(special.Id, resolveToken?.Id);

        var hits = runtime.Search("naked socks");
        WriteHits("raw", hits);
        Assert.Contains(hits, hit => hit.Entry.Id == special.Id);

        var unified = new UnifiedBrowseIndex(runtime);
        var state = UnifiedBrowseState.Neutral;
        var filtered = unified.FilterSearchHits(hits, state);
        output.WriteLine($"filtered ids=[{string.Join(",", filtered.Select(hit => hit.Entry.Id))}]");
        Assert.Contains(filtered, hit => hit.Entry.Id == special.Id);

        var workspace = new PromptWorkspace(new PromptParser(runtime));
        var viewModel = new DictionaryWorkspaceViewModel(
            runtime,
            workspace,
            GeneralBrowseProvider.FromCatalog(runtime),
            () => { },
            () => true);
        viewModel.Restore(new UiState(BrowseScope: "Tags", ContentIntent: "ALL"));
        viewModel.Query = "naked socks";
        viewModel.RefreshResults();
        output.WriteLine($"viewmodel ids=[{string.Join(",", viewModel.Results.Select(row => row.Entry.Id))}]");
        Assert.Contains(viewModel.Results, row => row.Entry.Id == special.Id);
        Assert.Equal("naked socks", viewModel.Results.Single(row => row.Entry.Id == special.Id).English);
    }

    private void WriteHits(string layer, IEnumerable<SearchHit> hits)
    {
        foreach (var hit in hits)
        {
            var entry = hit.Entry;
            output.WriteLine($"{layer}: rank={hit.Rank}; id={entry.Id}; english={entry.English}; canonical={entry.Canonical ?? "<null>"}; prompt={entry.PromptToken ?? "<null>"}; effective={entry.EffectivePromptToken ?? "<null>"}; special={entry.IsSpecial}");
        }
    }
}
