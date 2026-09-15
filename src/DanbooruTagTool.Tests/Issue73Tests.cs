using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue73Tests
{
    [Fact]
    public void DictionaryToggleAddsRemovesUndoAndReaddsCanonicalItem()
    {
        var clipboard = new MemoryClipboard();
        var vm = Fixtures.Vm(clipboard: clipboard);
        var row = Row(vm, "blue_hair");

        Assert.Equal("＋", row.AddSymbol);
        Assert.True(row.Add.CanExecute(null));
        row.Add.Execute(null);
        Assert.Equal("blue_hair", vm.English);
        Assert.Equal("✓", row.AddSymbol);
        vm.Copy.Execute(null);
        Assert.Equal(vm.English, clipboard.Value);

        row.Add.Execute(null);
        Assert.Empty(vm.Chips);
        vm.Copy.Execute(null);
        Assert.Equal("", clipboard.Value);

        vm.Undo.Execute(null);
        Assert.Equal("blue_hair", vm.English);
        row.Add.Execute(null);
        Assert.Empty(vm.Chips);
        row.Add.Execute(null);
        Assert.Equal("blue_hair", vm.English);
        vm.Copy.Execute(null);
        Assert.Equal(vm.English, clipboard.Value);
    }

    [Fact]
    public void DuplicateCanonicalToggleDoesNotGuessOrBulkDelete()
    {
        var vm = Fixtures.Vm();
        vm.Workspace.Replace("blue_hair,(blue_hair:1.2)");
        var before = vm.English;
        var row = Row(vm, "blue_hair");

        Assert.Equal(2, vm.Chips.Count(c => c.Item.Canonical == "blue_hair"));
        Assert.Equal("✓", row.AddSymbol);
        Assert.Contains("件追加済み", row.DetailAddLabel);
        Assert.False(row.Add.CanExecute(null));
        row.Add.Execute(null);
        Assert.Equal(before, vm.English);
        Assert.Equal(2, vm.Chips.Count(c => c.Item.Canonical == "blue_hair"));

        vm.InspectEntry.Execute(row);
        Assert.False(vm.SelectedEntry!.Add.CanExecute(null));
        vm.SelectedEntry.Add.Execute(null);
        Assert.Equal(before, vm.English);
    }

    [Fact]
    public void WeightedSingleCanonicalToggleDeletesExactItemAndUndoRestoresSurface()
    {
        var vm = Fixtures.Vm();
        vm.Workspace.Replace("(blue_hair:1.2)");
        var row = Row(vm, "blue_hair");

        Assert.True(row.Add.CanExecute(null));
        row.Add.Execute(null);
        Assert.Empty(vm.Chips);
        vm.Undo.Execute(null);
        Assert.Equal("(blue_hair:1.2)", vm.English);
    }

    [Fact]
    public void RawLookalikeRemainsWhenCanonicalToggleAddsAbsentCanonical()
    {
        var vm = Fixtures.Vm();
        vm.Workspace.Replace("[blue_hair]");
        var row = Row(vm, "blue_hair");

        row.Add.Execute(null);
        Assert.Equal("[blue_hair], blue_hair", vm.English);
        Assert.Contains(vm.Chips, chip => chip.Item.Kind == PromptItemKind.Raw && chip.Item.Surface == "[blue_hair]");
    }

    [Fact]
    public void RowAndTagDetailsUseTheSameToggleCommand()
    {
        var vm = Fixtures.Vm();
        var row = Row(vm, "blue_hair");

        row.Add.Execute(null);
        vm.InspectEntry.Execute(row);
        vm.SelectedEntry!.Add.Execute(null);
        Assert.Empty(vm.Chips);
        Assert.Equal("＋", row.AddSymbol);

        row.Add.Execute(null);
        Assert.Equal("blue_hair", vm.English);
    }

    [Fact]
    public void CategoryViewKeepsEnglishPromptAndOrderedSourceUnchanged()
    {
        var vm = Fixtures.Vm();
        vm.Workspace.Replace("blue_hair,raw,(smile:1.2)");
        var before = vm.English;

        vm.IsCategoryView = true;
        Assert.Equal(before, vm.English);
        Assert.NotEmpty(vm.CategoryGroups);
        vm.IsCategoryView = false;
        Assert.Equal(before, vm.English);
        Assert.Equal(new[] { "blue_hair", "raw", "(smile:1.2)" }, vm.Chips.Select(c => c.Item.Surface));
    }

    private static EntryViewModel Row(MainViewModel vm, string canonical)
    {
        vm.Query = canonical;
        vm.RefreshResults();
        return vm.Results.Single(row => row.Entry.Canonical == canonical);
    }
}
