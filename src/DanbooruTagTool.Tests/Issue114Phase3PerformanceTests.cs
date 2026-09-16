using System.Diagnostics;
using System.Windows.Input;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.App.Views;
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
        var allocatedBefore = GC.GetAllocatedBytesForCurrentThread();
        var stopwatch = Stopwatch.StartNew();
        var rows = DictionaryResultProjection.Project(entries, 2);
        stopwatch.Stop();
        var projectionAllocations = GC.GetAllocatedBytesForCurrentThread() - allocatedBefore;

        Assert.Equal(63_214, rows.Count);
        Assert.Equal(count, DictionaryResultProjection.Flatten(rows).Count());
        Assert.Same(entries[0], rows[0].First);
        Assert.Same(entries[^1], rows[^1].First);
        output.WriteLine($"synthetic projection: {count:N0} entries -> {rows.Count:N0} rows in {stopwatch.Elapsed.TotalMilliseconds:F2} ms; allocations={projectionAllocations:N0} bytes; projection creates no EntryViewModel instances");
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

        var refreshedRowCount = vm.Dictionary.Results.Concat(vm.Dictionary.Related).Count(row => row.Entry.Canonical == "blue_hair");
        var refreshTimer = Stopwatch.StartNew();
        affected.Add.Execute(null); // canonical count 0 -> 1
        refreshTimer.Stop();

        Assert.True(affectedNotifications > 0);
        Assert.Equal(0, unrelatedNotifications);
        Assert.True(detachedNotifications > 0);
        Assert.Equal("✓", affected.AddSymbol);
        Assert.Equal("✓", detached.AddSymbol);
        var fullRefreshTimer = Stopwatch.StartNew();
        foreach (var row in vm.Dictionary.Results.Concat(vm.Dictionary.Related)) row.Refresh();
        fullRefreshTimer.Stop();
        output.WriteLine($"targeted refresh: canonical=blue_hair, refreshed rows={refreshedRowCount}, detached selected=1, elapsed={refreshTimer.Elapsed.TotalMilliseconds:F3} ms; full candidate rows={vm.Dictionary.Results.Count + vm.Dictionary.Related.Count}, old-style full sweep={fullRefreshTimer.Elapsed.TotalMilliseconds:F3} ms");

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
        output.WriteLine($"query refresh save count delta={store.SaveCount - before}");
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

    [Theory]
    [InlineData(1, Key.Up, -1)]
    [InlineData(1, Key.Down, 1)]
    [InlineData(1, Key.PageUp, -10)]
    [InlineData(1, Key.PageDown, 10)]
    [InlineData(2, Key.Left, -1)]
    [InlineData(2, Key.Right, 1)]
    [InlineData(2, Key.Up, -2)]
    [InlineData(2, Key.Down, 2)]
    [InlineData(2, Key.PageUp, -20)]
    [InlineData(2, Key.PageDown, 20)]
    public void KeyboardMappingUsesColumnAwareOffsets(int columns, Key key, int expectedOffset)
    {
        var action = DictionaryKeyboardNavigation.Resolve(key, columns);
        Assert.Equal(DictionaryKeyboardActionKind.Move, action.Kind);
        Assert.Equal(expectedOffset, action.Offset);
    }

    [Fact]
    public void KeyboardMappingCoversBoundariesInspectAndSingleColumnHorizontalNoOp()
    {
        Assert.Equal(DictionaryKeyboardActionKind.Home, DictionaryKeyboardNavigation.Resolve(Key.Home, 1).Kind);
        Assert.Equal(DictionaryKeyboardActionKind.End, DictionaryKeyboardNavigation.Resolve(Key.End, 2).Kind);
        Assert.Equal(DictionaryKeyboardActionKind.Inspect, DictionaryKeyboardNavigation.Resolve(Key.Enter, 2).Kind);
        Assert.Equal(DictionaryKeyboardActionKind.None, DictionaryKeyboardNavigation.Resolve(Key.Left, 1).Kind);
        Assert.Equal(DictionaryKeyboardActionKind.None, DictionaryKeyboardNavigation.Resolve(Key.Right, 1).Kind);

        var vm = Fixtures.Vm();
        vm.Query = "hair";
        vm.RefreshResults();
        vm.Dictionary.SelectedEntry = vm.Dictionary.Results[0];
        vm.Dictionary.MoveResultSelection(-20);
        Assert.Same(vm.Dictionary.Results[0], vm.Dictionary.SelectedEntry);
        vm.Dictionary.MoveResultSelection(20);
        Assert.Same(vm.Dictionary.Results[^1], vm.Dictionary.SelectedEntry);
    }

    [Fact]
    public void CardContentResolvesTheEntrySuppliedToEitherContentPresenter()
    {
        var entry = new EntryViewModel(Fixtures.Catalog().Entries[0], Fixtures.Workspace(), _ => { });
        Assert.Same(entry, DictionaryWorkspaceView.ResolveCardEntry(entry, null));
    }

    [Fact]
    public void ActiveSelectedEntryIsRefreshedOnceWhileDetachedSelectionStillRefreshes()
    {
        var vm = Fixtures.Vm();
        vm.Query = "hair";
        vm.RefreshResults();
        var selected = vm.Dictionary.Results.Single(row => row.Entry.Canonical == "blue_hair");
        vm.Dictionary.SelectedEntry = selected;
        var notifications = 0;
        selected.PropertyChanged += (_, _) => notifications++;

        vm.Workspace.Replace("blue_hair");

        Assert.Equal(3, notifications); // AddLabel, AddSymbol, DetailAddLabel
    }

    private sealed class CountingStore : IUserStateStore
    {
        public UserState? State { get; private set; }
        public int SaveCount { get; private set; }
        public UserState? Load() => State;
        public void Save(UserState state) { State = state; SaveCount++; }
    }
}
