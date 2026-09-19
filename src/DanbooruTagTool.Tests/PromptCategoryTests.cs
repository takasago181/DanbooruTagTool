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
        var specialAction = new BrowsePath("SPECIAL_ACTION", "関係・行為", "CONTACT", "接触");
        var catalog = new Catalog([
            new("G:blue_hair", "blue_hair", "blue_hair", "青い髪", false, 10, [], [], [hair], BrowseClassification: BrowseClassificationStatus.Proposed),
            new("G:smile", "smile", "smile", "笑顔", false, 10, [], [], [expression], BrowseClassification: BrowseClassificationStatus.Proposed),
            new("S:special", "special_tag", "special_tag", "特別タグ", true, 10, [], [], [specialAction]),
            new("S:pathless", "pathless_special", "pathless_special", "分類なしSpecial", true, 10, [], [], []),
        ]);
        var items = new PromptParser(catalog).Parse("blue_hair,smile,blue_hair,special_tag,pathless_special,<lora:Rella:0.6>,BREAK,unknown");

        var groups = PromptCategoryProjection.Build(catalog, items);

        Assert.Equal(new[] { "髪・顔", "表情・感情", "◆ 関係・行為", PromptCategoryProjection.SpecialLabel, PromptCategoryProjection.OtherLabel }, groups.Select(g => g.Label));
        Assert.Equal(new[] { 0, 2 }, groups[0].Items.Select(i => i.OriginalIndex));
        Assert.Equal(2, groups[0].Count);
        Assert.Equal("青い髪", groups[0].Items[0].Japanese);
        Assert.Equal("blue_hair", groups[0].Items[0].English);
        Assert.Equal(new[] { 1 }, groups[1].Items.Select(i => i.OriginalIndex));
        Assert.Equal(new[] { 3 }, groups[2].Items.Select(i => i.OriginalIndex));
        Assert.Equal(new[] { 4 }, groups[3].Items.Select(i => i.OriginalIndex));
        Assert.Equal(new[] { 5, 6, 7 }, groups[4].Items.Select(i => i.OriginalIndex));
        Assert.Equal("<lora:Rella:0.6>", groups[4].Items[0].English);
        Assert.Equal("unknown ?", groups[4].Items[2].Japanese);
    }

    [Fact]
    public void SpecialGroupsUseExistingTopLevelTaxonomyWithoutChangingPromptOrder()
    {
        var action = new BrowsePath("ACTION", "関係・行為", "A", "行為A");
        var camera = new BrowsePath("CAMERA", "構図・視点", "C", "視点");
        var catalog = new Catalog([
            new("S:first", "first_special", "first_special", "最初", true, 1, [], [], [action]),
            new("S:second", "second_special", "second_special", "二番目", true, 1, [], [], [camera]),
            new("S:third", "third_special", "third_special", "三番目", true, 1, [], [], [action]),
        ]);
        var items = new PromptParser(catalog).Parse("first_special,second_special,third_special");

        var groups = PromptCategoryProjection.Build(catalog, items);

        Assert.Equal(new[] { "◆ 関係・行為", "◆ 構図・視点" }, groups.Select(group => group.Label));
        Assert.Equal(new[] { 0, 2 }, groups[0].Items.Select(item => item.OriginalIndex));
        Assert.Equal(new[] { 1 }, groups[1].Items.Select(item => item.OriginalIndex));
        Assert.Equal("first_special, second_special, third_special", string.Join(", ", items.Select(item => item.Surface.Trim())));
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

    [Fact]
    public void PromptHeaderPresentationKeepsTheSameControlsAvailableAcrossViews()
    {
        var vm = Fixtures.Vm().Prompt;

        Assert.Equal("日本語表示のPromptを並べ替え・削除できます。見えている順序がそのままコピーされます。", vm.ViewHint);
        Assert.Equal("0件", vm.EditorCount);
        Assert.True(vm.CanEditOrderedPrompt);

        vm.IsCategoryView = true;

        Assert.Equal("Promptをカテゴリ別に読みやすく表示します。元の並び順・内容は変わりません。", vm.ViewHint);
        Assert.False(vm.CanEditOrderedPrompt);
        Assert.Equal("0件", vm.EditorCount);
    }
}
