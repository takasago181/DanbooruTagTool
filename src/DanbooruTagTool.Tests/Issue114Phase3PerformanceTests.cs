using System.Diagnostics;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue114Phase3PerformanceTests(ITestOutputHelper output)
{
    [Fact]
    public void ProjectionPreservesFlatOrderForOneAndTwoColumnsAndOddTail()
    {
        var workspace = Fixtures.Workspace();
        var entries = Fixtures.Catalog().Entries.Select(entry => new EntryViewModel(entry, workspace, _ => { })).ToArray();

        var oneColumn = DictionaryResultProjection.Project(entries, 1);
        var oddEntries = entries[..^1];
        var twoColumns = DictionaryResultProjection.Project(oddEntries, 2);

        Assert.Equal(entries.Select(row => row.Entry.Id), DictionaryResultProjection.Flatten(oneColumn).Select(row => row.Entry.Id));
        Assert.Equal(oddEntries.Select(row => row.Entry.Id), DictionaryResultProjection.Flatten(twoColumns).Select(row => row.Entry.Id));
        Assert.Equal(oddEntries.Length, DictionaryResultProjection.Flatten(twoColumns).Count());
        Assert.Null(twoColumns[^1].Second);
        Assert.Same(oddEntries[^1], DictionaryResultProjection.Flatten(twoColumns).Last());
    }

    [Fact]
    public void SyntheticProductionSizedProjectionDoesNotCreateAdditionalCardInstances()
    {
        const int count = 126_427;
        var workspace = Fixtures.Workspace();
        var entries = Enumerable.Range(0, count)
            .Select(index => new EntryViewModel(Fixtures.Entry("synthetic_" + index, "合成" + index), workspace, _ => { }))
            .ToArray();
        var stopwatch = Stopwatch.StartNew();
        var rows = DictionaryResultProjection.Project(entries, 2);
        stopwatch.Stop();

        Assert.Equal(63_214, rows.Count);
        Assert.Equal(count, DictionaryResultProjection.Flatten(rows).Count());
        Assert.Same(entries[0], rows[0].First);
        Assert.Same(entries[^1], rows[^1].First);
        output.WriteLine($"synthetic projection: {count:N0} entries -> {rows.Count:N0} rows in {stopwatch.Elapsed.TotalMilliseconds:F2} ms; projection creates no EntryViewModel instances");
    }

    [Fact]
    public void ColumnChangesPreserveFlatResultsAndSelectedEntryIdentity()
    {
        var vm = Fixtures.Vm();
        vm.Query = "hair";
        vm.RefreshResults();
        var selected = vm.Dictionary.Results[2];
        vm.Dictionary.SelectedEntry = selected;
        var ids = vm.Dictionary.Results.Select(row => row.Entry.Id).ToArray();

        vm.Dictionary.SetSurfaceWidth(1_000);
        Assert.Equal(2, vm.Dictionary.DictionaryColumnCount);
        Assert.Same(selected, vm.Dictionary.SelectedEntry);
        Assert.Equal(ids, DictionaryResultProjection.Flatten(vm.Dictionary.DictionaryRows).Select(row => row.Entry.Id));

        vm.Dictionary.SetSurfaceWidth(500);
        Assert.Equal(1, vm.Dictionary.DictionaryColumnCount);
        Assert.Same(selected, vm.Dictionary.SelectedEntry);
        Assert.Equal(ids, DictionaryResultProjection.Flatten(vm.Dictionary.DictionaryRows).Select(row => row.Entry.Id));
    }

    [Fact]
    public void PromptRefreshTouchesOnlyChangedCanonicalAndDetachedSelection()
    {
        var vm = Fixtures.Vm();
        vm.Query = "hair";
        vm.RefreshResults();
        var affected = vm.Dictionary.Results.Single(row => row.Entry.Canonical == "blue_hair");
        var unrelated = vm.Dictionary.Results.Single(row => row.Entry.Canonical == "red_hair");
        var detached = new EntryViewModel(affected.Entry, vm.Workspace, vm.Add);
        vm.Dictionary.SelectedEntry = detached;
        var affectedNotifications = 0;
        var unrelatedNotifications = 0;
        var detachedNotifications = 0;
        affected.PropertyChanged += (_, _) => affectedNotifications++;
        unrelated.PropertyChanged += (_, _) => unrelatedNotifications++;
        detached.PropertyChanged += (_, _) => detachedNotifications++;

        affected.Add.Execute(null); // canonical count 0 -> 1

        Assert.True(affectedNotifications > 0);
        Assert.Equal(0, unrelatedNotifications);
        Assert.True(detachedNotifications > 0);
        Assert.Equal("✓", affected.AddSymbol);
        Assert.Equal("✓", detached.AddSymbol);

        vm.Workspace.Replace("blue_hair,blue_hair"); // 1 -> 2
        Assert.Contains("2件", affected.DetailAddLabel);
        vm.Workspace.Replace(""); // 2 -> 0
        Assert.Equal("＋", affected.AddSymbol);
    }

    [Fact]
    public void QueryRefreshDoesNotPersistUntilExplicitDurableSave()
    {
        var store = new CountingStore();
        var vm = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard());
        var before = store.SaveCount;

        vm.Query = "blue";
        vm.RefreshResults();

        Assert.Equal(before, store.SaveCount);
        vm.Persist();
        Assert.Equal(before + 1, store.SaveCount);
        Assert.Equal("blue", store.State!.Ui.Query);
    }

    [Fact]
    public void DictionaryNavigationUsesFlatResultOffsets()
    {
        var vm = Fixtures.Vm();
        vm.Query = "hair";
        vm.RefreshResults();
        vm.Dictionary.SetSurfaceWidth(1_000);
        vm.Dictionary.SelectedEntry = vm.Dictionary.Results[0];

        vm.Dictionary.MoveResultSelection(2);
        Assert.Same(vm.Dictionary.Results[2], vm.Dictionary.SelectedEntry);
        vm.Dictionary.MoveResultSelection(-1);
        Assert.Same(vm.Dictionary.Results[1], vm.Dictionary.SelectedEntry);
        vm.Dictionary.SelectResultBoundary(true);
        Assert.Same(vm.Dictionary.Results[^1], vm.Dictionary.SelectedEntry);
        vm.Dictionary.SelectResultBoundary(false);
        Assert.Same(vm.Dictionary.Results[0], vm.Dictionary.SelectedEntry);
    }

    private sealed class CountingStore : IUserStateStore
    {
        public UserState? State { get; private set; }
        public int SaveCount { get; private set; }
        public UserState? Load() => State;
        public void Save(UserState state) { State = state; SaveCount++; }
    }
}
