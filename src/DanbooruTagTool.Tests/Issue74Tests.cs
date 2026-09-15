using DanbooruTagTool.App.ViewModels;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue74Tests
{
    [Fact]
    public void DictionaryCardsUseTwoColumnsOnlyWhenTheResultSurfaceIsWideEnough()
    {
        Assert.Equal(376, DictionaryLayoutMetrics.CardWidth(760));
        Assert.Equal(759, DictionaryLayoutMetrics.CardWidth(759));
        Assert.Equal(DictionaryLayoutMetrics.MinimumCardWidth, DictionaryLayoutMetrics.CardWidth(240));
    }

    [Fact]
    public void WqhdVisualLayoutDoesNotChangeResultSequenceOrPromptOutput()
    {
        var vm = Fixtures.Vm();
        vm.Query = "";
        vm.RefreshResults();
        var resultIds = vm.Results.Select(row => row.Entry.Id).ToArray();
        vm.Workspace.Replace("blue_hair,raw,(smile:1.2)");
        var before = vm.English;

        vm.IsCategoryView = true;
        vm.DictionaryCardWidth = DictionaryLayoutMetrics.CardWidth(1400);

        Assert.Equal(resultIds, vm.Results.Select(row => row.Entry.Id));
        Assert.Equal(before, vm.English);
        Assert.True(vm.DictionaryCardWidth < 1400);
        Assert.NotEmpty(vm.CategoryGroups);
    }
}
