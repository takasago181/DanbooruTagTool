using System.IO;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using Xunit;
namespace DanbooruTagTool.Tests;
public class Issue256CapabilitySelectionTests
{
    [Fact]
    public async Task ProbeNeverChangesCurrentRecipeAndExplicitSelectionPinsNameAndHash()
    {
        var api = new Probe(); var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), generationApi: api);
        vm.Create.Model = "original"; vm.Create.ModelHash = "abc"; vm.Workspace.Replace("raw prompt");
        await vm.Create.RefreshCapabilities.ExecuteAsync(null);
        Assert.Equal("original", vm.Create.Model); Assert.Equal("abc", vm.Create.ModelHash); Assert.Equal("raw prompt", vm.English);
        vm.Create.SelectedForgeModel = vm.Create.ForgeModels.Single(); Assert.Equal("abc", vm.Create.ModelHash);
        vm.Create.ApplyForgeModel.Execute(null); Assert.Equal("selected [def]", vm.Create.Model); Assert.Equal("def", vm.Create.ModelHash);
        Assert.Equal(new[] { "Euler" }, vm.Create.ForgeSamplers); Assert.Equal(0, api.Posts);
        vm.PresetManagementOpen = true; Assert.False(vm.Create.ApplyForgeModel.CanExecute(null));
    }
    [Fact]
    public async Task FailedRefreshRetainsValuesAndCannotApplyStaleSelection()
    {
        var api = new Probe(); var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), generationApi: api);
        await vm.Create.RefreshCapabilities.ExecuteAsync(null); vm.Create.SelectedForgeModel = vm.Create.ForgeModels.Single(); vm.Create.Model = "current";
        api.Fail = true; await vm.Create.RefreshCapabilities.ExecuteAsync(null);
        Assert.Equal("current", vm.Create.Model); Assert.False(vm.Create.ApplyForgeModel.CanExecute(null)); Assert.Contains("取得できません", vm.Create.CapabilityStatus); Assert.Equal(0, api.Posts);
    }
    private sealed class Probe : IForgeGenerationApiClient
    {
        public bool Fail; public int Posts;
        public Task<ForgeApiCapabilities> ProbeAsync(string url, CancellationToken ct = default) => Fail ? Task.FromException<ForgeApiCapabilities>(new InvalidDataException("fixture")) : Task.FromResult(new ForgeApiCapabilities([new("selected [def]", "selected", "def")], ["Euler"], ["Karras"]));
        public Task<ForgeApiResult> GenerateAsync(string url, ForgeApiRequest r, string dir, CancellationToken ct = default) { Posts++; return Task.FromResult(new ForgeApiResult(false, "not called")); }
    }
}
