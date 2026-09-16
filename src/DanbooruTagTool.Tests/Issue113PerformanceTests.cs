using System.Diagnostics;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue113PerformanceTests(ITestOutputHelper output)
{
    [Fact]
    public void OneColumnProjectionFlattensExactlyToResults()
    {
        var vm = Fixtures.Vm();
        vm.Query = "hair";
        vm.RefreshResults();

        var rows = DictionaryResultProjection.Project(vm.Results, 1);

        Assert.Equal(vm.Results, DictionaryResultProjection.Flatten(rows));
        Assert.All(rows, row => Assert.Null(row.Second));
    }

    [Fact]
    public void TwoColumnProjectionFlattensExactlyAndKeepsOddLastEntry()
    {
        var vm = Fixtures.Vm();
        vm.Query = "hair";
        vm.RefreshResults();

        var rows = DictionaryResultProjection.Project(vm.Results, 2);

        Assert.Equal(vm.Results, DictionaryResultProjection.Flatten(rows));
        Assert.Equal(vm.Results.Count / 2 + vm.Results.Count % 2, rows.Count);
        Assert.Equal(vm.Results[^1], rows[^1].Second ?? rows[^1].First);
    }

    [Fact]
    public void SwitchingDictionaryColumnsPreservesResultsOrderAndSelectedEntryIdentity()
    {
        var vm = Fixtures.Vm();
        vm.Query = "hair";
        vm.RefreshResults();
        var selected = vm.Results[1];
        var resultIds = vm.Results.Select(row => row.Entry.Id).ToArray();
        vm.SelectedEntry = selected;

        vm.SetDictionarySurfaceWidth(1400);
        Assert.Equal(2, vm.DictionaryColumnCount);
        Assert.Same(selected, vm.SelectedEntry);
        Assert.Equal(resultIds, DictionaryResultProjection.Flatten(vm.DictionaryRows).Select(row => row.Entry.Id));
        Assert.True(selected.IsSelected);

        vm.SetDictionarySurfaceWidth(600);
        Assert.Equal(1, vm.DictionaryColumnCount);
        Assert.Same(selected, vm.SelectedEntry);
        Assert.Equal(resultIds, DictionaryResultProjection.Flatten(vm.DictionaryRows).Select(row => row.Entry.Id));
        Assert.True(selected.IsSelected);
    }

    [Fact]
    public void PromptCanonicalCountChangesRefreshOnlyAffectedRowsAndRemainDuplicateSafe()
    {
        var vm = Fixtures.Vm();
        vm.Query = "hair";
        vm.RefreshResults();
        var affected = vm.Results.Single(row => row.Entry.Canonical == "blue_hair");
        var unrelated = vm.Results.Single(row => row.Entry.Canonical == "red_hair");
        var unrelatedNotifications = 0;
        unrelated.PropertyChanged += (_, _) => unrelatedNotifications++;

        vm.Workspace.Replace("blue_hair");
        Assert.Equal("✓", affected.AddSymbol);
        Assert.Equal(0, unrelatedNotifications);

        vm.Workspace.Replace("");
        Assert.Equal("＋", affected.AddSymbol);

        vm.Workspace.Replace("blue_hair,blue_hair");
        Assert.Equal("✓", affected.AddSymbol);
        Assert.Contains("2件追加済み", affected.DetailAddLabel);
        Assert.False(affected.Add.CanExecute(null));
    }

    [Fact]
    public void GeneralBrowsePathsAreCachedWithoutChangingContentOrOrder()
    {
        var first = new BrowsePath("first", "First", "a", "A");
        var second = new BrowsePath("first", "First", "b", "B");
        var third = new BrowsePath("second", "Second", "", "");
        var provider = new GeneralBrowseProvider(Fixtures.Catalog(), new Dictionary<string, BrowsePath[]>
        {
            ["blue_hair"] = [first, second],
            ["red_hair"] = [first, third]
        });

        Assert.Equal(new[] { first, second, third }, provider.Paths);
        Assert.Same(provider.Paths, provider.Paths);
    }

    [Fact]
    public void QuerySetterDoesNotPersistUntilExplicitUiSave()
    {
        var store = new MemoryStore();
        var vm = Fixtures.Vm(store);

        vm.Query = "blue_hair";
        Assert.Null(store.State);

        vm.Persist();
        Assert.Equal("blue_hair", store.State?.Ui.Query);
    }

    [Fact]
    public void LargeProjectionRemainsFlatAndCreatesRowsOnlyForDisplay()
    {
        var workspace = Fixtures.Workspace();
        var entries = Enumerable.Range(0, 126_427)
            .Select(i => new EntryViewModel(
                new CatalogEntry($"G:{i}", $"tag_{i}", $"tag_{i}", $"タグ{i}", false, i, [], [], []),
                workspace, _ => { }))
            .ToArray();

        var watch = Stopwatch.StartNew();
        var rows = DictionaryResultProjection.Project(entries, 2);
        watch.Stop();

        Assert.Equal(63_214, rows.Count);
        Assert.Equal(entries, DictionaryResultProjection.Flatten(rows));
        output.WriteLine($"Synthetic 126,427 results -> {rows.Count:N0} display rows in {watch.Elapsed.TotalMilliseconds:F2} ms; no card/container creation occurs in the projection.");
    }
}
