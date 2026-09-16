using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue114Phase2ViewModelTests
{
    [Fact]
    public void WorkspaceIndexChangePersistsTheNewWorkspaceExactlyOnce()
    {
        var store = new CountingStore();
        var vm = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard());
        var before = store.SaveCount;

        vm.WorkspaceIndex = 1;

        Assert.Equal(before + 1, store.SaveCount);
        Assert.Equal(1, store.State!.Ui.Workspace);
        vm.WorkspaceIndex = 1;
        Assert.Equal(before + 1, store.SaveCount);

        vm.StartDirect.Execute(null);
        var duringDirectEdit = store.SaveCount;
        vm.WorkspaceIndex = 0;
        Assert.Equal(1, vm.WorkspaceIndex);
        Assert.Equal(duringDirectEdit, store.SaveCount);
    }

    [Fact]
    public void MainShellComposesFeatureOwnersAndSharesCoreWorkspace()
    {
        var vm = Fixtures.Vm();

        Assert.Same(vm.Workspace, vm.Prompt.Workspace);
        Assert.NotNull(vm.Dictionary);
        Assert.NotNull(vm.PresetEditor);
        Assert.NotNull(vm.Forge);
        Assert.NotNull(vm.UserState);
        Assert.Equal(vm.Results.Select(row => row.Entry.Id), vm.Dictionary.Results.Select(row => row.Entry.Id));
    }

    [Fact]
    public void DictionaryAddFlowsThroughPromptOwnerAndPromptDeleteRefreshesDictionaryState()
    {
        var vm = Fixtures.Vm();
        var row = vm.Dictionary.Results.First(entry => entry.Entry.Canonical == "blue_hair");

        row.Add.Execute(null);
        Assert.Single(vm.Prompt.Chips);
        Assert.Equal("blue_hair", vm.Prompt.Chips[0].Item.Canonical);
        Assert.Equal("✓", row.AddSymbol);

        vm.Prompt.DeleteOne.Execute(vm.Prompt.Chips[0]);
        Assert.Empty(vm.Prompt.Chips);
        Assert.Equal("＋", row.AddSymbol);
    }

    [Fact]
    public void DictionaryBrowseAndPromptPresentationRemainOwnedByTheirChildren()
    {
        var vm = Fixtures.Vm();
        vm.Dictionary.NavigateTo("special:APPEARANCE>HAIR");
        var ids = vm.Dictionary.Results.Select(row => row.Entry.Id).ToArray();
        vm.Prompt.Workspace.Replace("blue_hair,smile");

        Assert.Equal(ids, vm.Dictionary.Results.Select(row => row.Entry.Id));
        Assert.Equal("blue_hair,smile", vm.Prompt.English);
        Assert.Equal("blue_hair,smile", vm.English);
    }

    [Fact]
    public void SplitStateSnapshotRestoresDictionaryPromptPresetAndForgeState()
    {
        var store = new MemoryStore();
        var first = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard());
        first.Dictionary.NavigateTo("special:APPEARANCE>HAIR");
        first.Prompt.OutputProfile = PromptOutputProfile.GenerationFriendly;
        first.Forge.ForgeUrl = "http://127.0.0.1:7861";
        first.Persist();

        var restored = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard());
        Assert.Equal("special:APPEARANCE>HAIR", restored.Dictionary.BrowseKey);
        Assert.Equal(PromptOutputProfile.GenerationFriendly, restored.Prompt.OutputProfile);
        Assert.Equal("http://127.0.0.1:7861", restored.Forge.ForgeUrl);
    }

    private sealed class CountingStore : IUserStateStore
    {
        public UserState? State { get; private set; }
        public int SaveCount { get; private set; }
        public UserState? Load() => State;
        public void Save(UserState state) { State = state; SaveCount++; }
    }
}
