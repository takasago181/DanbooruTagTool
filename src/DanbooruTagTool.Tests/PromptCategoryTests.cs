using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using Xunit;

namespace DanbooruTagTool.Tests;

public class PromptCategoryTests
{
    [Fact]
    public void ProjectionUsesAcceptedPathsAndPreservesRelativeOrder()
    {
        var hair = new BrowsePath("HAIR", "髪・顔", "HAIR", "髪");
        var expression = new BrowsePath("EXPRESSION", "表情・感情", "SMILE", "笑顔");
        var catalog = new Catalog([
            new("G:blue_hair", "blue_hair", "blue_hair", "青い髪", false, 10, [], [], [hair], BrowseClassification: BrowseClassificationStatus.Proposed),
            new("G:smile", "smile", "smile", "笑顔", false, 10, [], [], [expression], BrowseClassification: BrowseClassificationStatus.Proposed),
            new("S:special", "special_tag", "special_tag", "特別タグ", true, 10, [], [], [hair]),
        ]);
        var items = new PromptParser(catalog).Parse("blue_hair,smile,blue_hair,special_tag,<lora:Rella:0.6>,BREAK,unknown");

        var groups = PromptCategoryProjection.Build(catalog, items);

        Assert.Equal(new[] { "髪・顔", "表情・感情", PromptCategoryProjection.SpecialLabel, PromptCategoryProjection.OtherLabel }, groups.Select(g => g.Label));
        Assert.Equal(new[] { 0, 2 }, groups[0].Items.Select(i => i.OriginalIndex));
        Assert.Equal(2, groups[0].Count);
        Assert.Equal("青い髪", groups[0].Items[0].Japanese);
        Assert.Equal("blue_hair", groups[0].Items[0].English);
        Assert.Equal(new[] { 1 }, groups[1].Items.Select(i => i.OriginalIndex));
        Assert.Equal(new[] { 3 }, groups[2].Items.Select(i => i.OriginalIndex));
        Assert.Equal(new[] { 4, 5, 6 }, groups[3].Items.Select(i => i.OriginalIndex));
        Assert.Equal("<lora:Rella:0.6>", groups[3].Items[0].English);
        Assert.Equal("unknown ?", groups[3].Items[2].Japanese);
    }

    [Fact]
    public void CategoryToggleIsReadOnlyAndOrderedEditingReturnsUnchanged()
    {
        var clipboard = new MemoryClipboard();
        var vm = Fixtures.Vm(clipboard: clipboard);
        vm.Workspace.Replace("blue_hair, blue_hair,(blue_hair:1.2),BREAK,custom_trigger");
        var before = vm.English;
        var beforeIds = vm.Chips.Select(chip => chip.Id).ToArray();

        vm.IsCategoryView = true;
        vm.SelectAll();
        vm.Move([beforeIds[0]], vm.Chips.Count);
        vm.Delete.Execute(null);
        vm.Copy.Execute(null);

        Assert.False(vm.IsOrderedView);
        Assert.Equal(before, vm.English);
        Assert.Equal(before, clipboard.Value);
        Assert.Equal(beforeIds, vm.Chips.Select(chip => chip.Id));
        Assert.Equal(5, vm.CategoryGroups.Sum(group => group.Count));
        Assert.Contains(vm.CategoryGroups.SelectMany(group => group.Items), item => item.Item.Kind == PromptItemKind.Raw);

        vm.IsOrderedView = true;
        vm.Select(vm.Chips[0].Id);
        Assert.True(vm.Delete.CanExecute(null));
        Assert.Equal(before, vm.English);
    }
}
