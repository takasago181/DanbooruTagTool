using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public class UxRefinementTests(ITestOutputHelper output)
{
    private const string Mixed = "blue_hair,blue_hair, (smile:1.2),<lora:sample:0.7>,BREAK,[a:b:0.4],custom_trigger";

    [Theory]
    [InlineData("")]
    [InlineData(" \r\n\t")]
    public void EmptyClipboardPreservesPromptIdsRecoveryAndHistory(string empty)
    {
        var clip = new MemoryClipboard { Value = empty }; var vm = Fixtures.Vm(clipboard: clip);
        vm.Workspace.Replace("previous"); vm.Workspace.Replace(Mixed);
        var ids = vm.Chips.Select(c => c.Id).ToArray(); var recovery = vm.Workspace.Snapshot().Recovery;
        vm.Import.Execute(null);
        Assert.Equal(Mixed, vm.English); Assert.Equal(ids, vm.Chips.Select(c => c.Id));
        Assert.Equal(recovery, vm.Workspace.Snapshot().Recovery);
        Assert.Equal("クリップボードにPrompt文字列がありません", vm.Status);
        vm.Undo.Execute(null); Assert.Equal("previous", vm.English);
    }

    [Fact]
    public void DirectEditBlocksCommandsAndPointerEntrypointsUntilCancel()
    {
        var clip = new MemoryClipboard { Value = "smile" }; var vm = Fixtures.Vm(clipboard: clip);
        vm.Workspace.Replace(Mixed); vm.Workspace.Replace("temporary"); vm.Undo.Execute(null);
        vm.Select(vm.Chips[0].Id); var ids = vm.Chips.Select(c => c.Id).ToArray();
        var row = vm.Results.First(r => r.Entry.Canonical == "blue_hair");
        vm.StartDirect.Execute(null); vm.DirectText = "stale draft";
        foreach (var command in new[] { vm.Copy, vm.Import, vm.New, vm.Recover, vm.Undo, vm.Redo, vm.Delete, vm.DeleteOne, vm.ApplyWeight, vm.OpenEditor, vm.Navigate, vm.Back, vm.Inspect, vm.InspectEntry, vm.StartDirect })
        { Assert.False(command.CanExecute(null)); command.Execute(vm.Chips[0]); }
        Assert.False(row.Add.CanExecute(null)); row.Add.Execute(null);
        vm.Add(Fixtures.Entry("red_hair", "赤い髪")); vm.Move([ids[0]], ids.Length);
        Assert.Empty(vm.BeginDrag(ids[0])); vm.WorkspaceIndex = 0;
        Assert.Equal(1, vm.WorkspaceIndex); Assert.Equal(Mixed, vm.English);
        Assert.Equal(ids, vm.Chips.Select(c => c.Id)); Assert.Equal("smile", clip.Value);
        Assert.True(vm.ApplyDirect.CanExecute(null)); Assert.True(vm.CancelDirect.CanExecute(null));
        vm.CancelDirect.Execute(null); Assert.False(vm.DirectEditing); Assert.Equal(Mixed, vm.English);
        Assert.True(vm.Redo.CanExecute(null)); vm.Redo.Execute(null); Assert.Equal("temporary", vm.English);
    }

    [Fact]
    public void DirectApplyReparsesRawAndIsOneUndoStepWithVisibleCopy()
    {
        var clip = new MemoryClipboard(); var vm = Fixtures.Vm(clipboard: clip);
        vm.Workspace.Replace("smile"); vm.StartDirect.Execute(null); vm.DirectText = Mixed;
        vm.ApplyDirect.Execute(null); Assert.Equal(Mixed, vm.English);
        vm.Copy.Execute(null); Assert.Equal(PromptParser.Serialize(vm.Chips.Select(c => c.Item)), clip.Value);
        Assert.Equal(2, vm.Chips.Count(c => c.Item.Canonical == "blue_hair"));
        vm.Undo.Execute(null); Assert.Equal("smile", vm.English);
        vm.Redo.Execute(null); Assert.Equal(Mixed, vm.English);
    }

    [Fact]
    public void ExplicitInspectRevealsDetailsButRefreshAndPromptChangesDoNot()
    {
        var vm = Fixtures.Vm(); var row = vm.Results.First(r => r.Entry.Canonical == "blue_hair");
        vm.DetailsTabIndex = 1; vm.SelectedEntry = row; vm.RefreshResults();
        vm.Add(row.Entry); Assert.Equal(1, vm.DetailsTabIndex);
        vm.InspectEntry.Execute(row); Assert.Equal(0, vm.DetailsTabIndex);
        var related = vm.Related.Single(); vm.DetailsTabIndex = 1;
        vm.InspectEntry.Execute(related); Assert.Equal(related, vm.SelectedEntry); Assert.Equal(0, vm.DetailsTabIndex);
        vm.DetailsTabIndex = 1; vm.Inspect.Execute(vm.Chips[0]); Assert.Equal(0, vm.DetailsTabIndex);
        Assert.Equal(row.Entry.Id, vm.SelectedEntry!.Entry.Id);
        vm.DetailsTabIndex = 1; vm.Query = "red"; vm.RefreshResults(); vm.ClearQuery.Execute(null);
        Assert.Equal(1, vm.DetailsTabIndex);
    }

    [Fact]
    public void SortStateReturnsToPreviousBrowseSortAfterSearch()
    {
        var vm = Fixtures.Vm(); vm.SortIndex = 1; vm.Query = "blue";
        Assert.True(vm.IsSearching); Assert.False(vm.CanBrowseSort);
        vm.RefreshResults(); vm.ClearQuery.Execute(null);
        Assert.False(vm.IsSearching); Assert.True(vm.CanBrowseSort); Assert.Equal(1, vm.SortIndex);
    }

    [Fact]
    public void PromptFindShowsMatchPositionAndBrowseBackTracksAvailability()
    {
        var vm = Fixtures.Vm();
        Assert.False(vm.Back.CanExecute(null)); Assert.False(vm.CanGoBack);
        vm.NavigateTo("special:APPEARANCE>HAIR");
        Assert.Equal("special:APPEARANCE>HAIR", vm.BrowseKey); Assert.True(vm.Back.CanExecute(null));
        vm.Back.Execute(null);
        Assert.Equal("special", vm.BrowseKey); Assert.False(vm.Back.CanExecute(null));

        vm.Workspace.Replace("blue_hair,red_hair,blue_eye");
        vm.Find = "hair";
        Assert.Equal("2件一致 · 1/2", vm.FindMatchSummary);
        Assert.True(vm.FindPrevious.CanExecute(null)); Assert.True(vm.FindNextCommand.CanExecute(null));
        vm.FindNextCommand.Execute(null); Assert.Equal("2件一致 · 2/2", vm.FindMatchSummary);
        vm.FindPrevious.Execute(null); Assert.Equal("2件一致 · 1/2", vm.FindMatchSummary);
        vm.Find = "no_such_tag"; Assert.Equal("0件一致", vm.FindMatchSummary);
        Assert.False(vm.FindPrevious.CanExecute(null)); Assert.False(vm.FindNextCommand.CanExecute(null));
    }

    [Fact]
    public void ItemDeleteAndUndoRetainDuplicatesRawSurfaceAndOrder()
    {
        var vm = Fixtures.Vm(); vm.Workspace.Replace(Mixed); var ids = vm.Chips.Select(c => c.Id).ToArray();
        var row = vm.Results.First(r => r.Entry.Canonical == "blue_hair");
        Assert.Equal("✓", row.AddSymbol); Assert.Equal("✓ 追加済み", row.DetailAddLabel);
        foreach (var id in ids)
        {
            vm.DeleteOne.Execute(vm.Chips.Single(c => c.Id == id));
            Assert.Equal(ids.Where(i => i != id), vm.Chips.Select(c => c.Id));
            vm.Undo.Execute(null); Assert.Equal(ids, vm.Chips.Select(c => c.Id)); Assert.Equal(Mixed, vm.English);
        }
        vm.DeleteOne.Execute(vm.Chips[0]); Assert.Equal("✓", row.AddSymbol);
        vm.DeleteOne.Execute(vm.Chips[0]); Assert.Equal("＋", row.AddSymbol); Assert.Equal("＋ Promptへ追加", row.DetailAddLabel);
        Assert.Equal("参照", vm.Results.Single(r => r.Entry.Canonical == null).AddSymbol);
    }

    [Fact]
    public void DetailOmitsOnlyExactRepeatedMetadataAndRetainsRealDescription()
    {
        var entry = Fixtures.Entry("blue_hair", "青い髪", 100) with { Description = "青い髪（blue_hair）【100件】\n固有の説明。" };
        Assert.Equal("固有の説明。", new EntryViewModel(entry, Fixtures.Workspace(), _ => {}).Description);
        entry = entry with { Description = "別の書式の説明【100件】" };
        Assert.Equal(entry.Description, new EntryViewModel(entry, Fixtures.Workspace(), _ => {}).Description);
    }

    [ProductionFact]
    public void ProductionSexBrowseIdentitiesAreDistinctAndSearchIsCanonicalUnique()
    {
        var catalog = CatalogDatabase.Open(Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!);
        var identities = catalog.Entries.Where(e => e.Canonical == "sex").ToArray();
        Assert.Equal(4, identities.Length); Assert.Equal(4, identities.Select(e => e.Id).Distinct().Count());
        output.WriteLine(string.Join(" | ", identities.Select(e => $"{e.Id}: {e.English} -> {e.Canonical}")));
        var vm = new MainViewModel(catalog, new MemoryStore(), new MemoryClipboard());
        Assert.Equal(3, vm.Results.Count(r => r.Entry.Canonical == "sex"));
        foreach (var q in new[] { "sex", "fuck", "fucking", "性行為", "blue_hair" })
        {
            vm.Query = q; vm.RefreshResults();
            var canonical = vm.Results.Where(r => r.Entry.Canonical != null).Select(r => r.Entry.Canonical).ToArray();
            Assert.Equal(canonical.Length, canonical.Distinct().Count());
            output.WriteLine($"{q}: {vm.Results.Count} visible rows; duplicate canonical groups = 0");
        }
    }
}
