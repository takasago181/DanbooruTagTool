using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;
public class DataAndViewModelTests
{
    [Fact] public void CatalogIsReadOnlyAndSeparatedFromUserDb()
    {
        using var d=new TempDirectory(); var paths=new PortablePaths(d.Path); var entries=Fixtures.Catalog().Entries;
        CatalogDatabase.Build(paths.Catalog,entries,"isolated fixture"); var hash=AcceptedAssetImporter.Hash(paths.Catalog);
        Assert.Equal(entries.Count,CatalogDatabase.Open(paths.Catalog).Entries.Count);
        var w=Fixtures.Workspace(); w.Replace("a,b"); new UserStateStore(paths.User).Save(new(w.Snapshot(),new()));
        Assert.Equal(hash,AcceptedAssetImporter.Hash(paths.Catalog)); Assert.NotEqual(paths.Catalog,paths.User);
        Assert.Throws<IOException>(()=>CatalogDatabase.Build(paths.Catalog,entries,"overwrite"));
        Assert.Throws<ArgumentException>(()=>new UserStateStore(paths.Catalog));
    }
    [Fact] public void RestartRestoresItemsRecoveryAndUiState()
    {
        using var d=new TempDirectory(); var path=new PortablePaths(d.Path).User; var w=Fixtures.Workspace(); w.Replace("old"); w.Replace("blue hair,blue_hair,<lora:X:0.6>");
        var ui=new UiState(1,"special:APPEARANCE>HAIR", "青い", "S:blue_hair",42,190,420,.67,1234,777,12,34,true);
        new UserStateStore(path).Save(new(w.Snapshot(),ui)); var saved=new UserStateStore(path).Load()!;
        var restored=Fixtures.Workspace(); restored.Restore(saved.Prompt); Assert.Equal(w.English,restored.English); Assert.Equal(w.Items.Select(i=>i.Id),restored.Items.Select(i=>i.Id)); Assert.Equal(ui,saved.Ui); restored.Recover(); Assert.Equal("old",restored.English);
    }
    [Fact] public void UserDataCanMoveWithPortableFolder()
    { using var a=new TempDirectory(); using var b=new TempDirectory(); var w=Fixtures.Workspace(); w.Replace("portable, raw"); var pa=new PortablePaths(a.Path); var pb=new PortablePaths(b.Path); new UserStateStore(pa.User).Save(new(w.Snapshot(),new())); Directory.CreateDirectory(Path.GetDirectoryName(pb.User)!); File.Copy(pa.User,pb.User); Assert.Equal(w.English,PromptParser.Serialize(new UserStateStore(pb.User).Load()!.Prompt.Items)); }
    [Fact] public void NoOptionalHugeIndexNeededForStartup()
    { using var d=new TempDirectory(); var p=new PortablePaths(d.Path); CatalogDatabase.Build(p.Catalog,Fixtures.Catalog().Entries,"fixture"); var vm=new App.ViewModels.MainViewModel(CatalogDatabase.Open(p.Catalog),new UserStateStore(p.User),new MemoryClipboard()); Assert.NotEmpty(vm.Results); Assert.False(Directory.Exists(Path.Combine(d.Path,"data/runtime_index"))); }
    [Fact] public void GeneralPendingAndFutureSidecarContract()
    { var pending=new PendingGeneralBrowseProvider(); Assert.True(pending.IsPending); Assert.Empty(pending.Paths); Assert.Empty(pending.Browse("anything")); var provider=new GeneralBrowseProvider(Fixtures.Catalog(),new Dictionary<string,BrowsePath[]> { ["red_hair"]=[Fixtures.HairPath] }); Assert.False(provider.IsPending); Assert.Equal("red_hair",Assert.Single(provider.Browse(Fixtures.HairPath.Key)).Canonical); }
    [Fact] public void SpecialGenreSubgenreBrowseAndRelatedUseSamePaths()
    { var vm=Fixtures.Vm(); vm.NavigateTo("special:APPEARANCE>HAIR"); Assert.All(vm.Results,r=>Assert.True(r.Entry.IsSpecial && r.Entry.Paths.Contains(Fixtures.HairPath))); Assert.Equal("blue_hair",vm.Results[0].Entry.Canonical); vm.SelectedEntry=vm.Results[0]; Assert.Contains(vm.Related,r=>r.Entry.Id=="S:semantic"); }
    [Fact] public void VmClipboardEqualsVisibleWorkspaceAndPreview()
    { var clip=new MemoryClipboard { Value="blue hair, raw,blue_hair" }; var vm=Fixtures.Vm(clipboard:clip); vm.Import.Execute(null); vm.Copy.Execute(null); Assert.Equal(PromptParser.Serialize(vm.Chips.Select(c=>c.Item)),vm.English); Assert.Equal(vm.English,clip.Value); Assert.Equal("✓ コピーしました",vm.Status); }
    [Fact] public void VmToggleStateUpdatesImmediately()
    { var vm=Fixtures.Vm(); var row=vm.Results.First(r=>r.Entry.Canonical=="blue_hair"); row.Add.Execute(null); Assert.Equal("✓ 追加済み（クリックで取消）",row.AddLabel); Assert.True(row.Add.CanExecute(null)); Assert.Single(vm.Chips); row.Add.Execute(null); Assert.Empty(vm.Chips); }
    [Fact] public void SingleCtrlShiftVisibleMultiSelectAndClear()
    { var vm=Fixtures.Vm(); vm.Workspace.Replace("a,b,c,d,e"); vm.Select(vm.Chips[1].Id); vm.Select(vm.Chips[3].Id,ctrl:true); Assert.Equal(2,vm.Chips.Count(c=>c.Selected)); vm.Select(vm.Chips[4].Id,shift:true); Assert.Equal(new[]{false,false,false,true,true},vm.Chips.Select(c=>c.Selected)); vm.MultiSelect=true; vm.Select(vm.Chips[0].Id); Assert.Equal(3,vm.Chips.Count(c=>c.Selected)); vm.SelectAll(); Assert.All(vm.Chips,c=>Assert.True(c.Selected)); vm.ClearSelection(); Assert.All(vm.Chips,c=>Assert.False(c.Selected)); }
    [Fact] public void SelectedDragMovesSelectionUnselectedDragReplacesSelection()
    { var vm=Fixtures.Vm(); vm.Workspace.Replace("a,b,c,d,e"); vm.Select(vm.Chips[1].Id); vm.Select(vm.Chips[3].Id,true); var ids=vm.BeginDrag(vm.Chips[1].Id); Assert.Equal(2,ids.Length); vm.Move(ids,5); Assert.Equal("a,c,e,b,d",vm.English); var single=vm.BeginDrag(vm.Chips[0].Id); Assert.Single(single); Assert.Single(vm.Chips,c=>c.Selected); }
    [Fact] public void PromptFindHighlightsWithoutFilteringOrReordering()
    { var vm=Fixtures.Vm(); vm.Workspace.Replace("blue_hair,raw,smile"); var ids=vm.Chips.Select(c=>c.Id).ToArray(); Guid? scroll=null; vm.ScrollToChip+=id=>scroll=id; vm.Find="青い"; Assert.Equal(ids,vm.Chips.Select(c=>c.Id)); Assert.Single(vm.Chips,c=>c.Match); Assert.Equal(ids[0],scroll); }
    [Fact] public void DirectEscapeHatchAndUndoUseCore()
    { var vm=Fixtures.Vm(); vm.Workspace.Replace("smile"); vm.StartDirect.Execute(null); vm.DirectText="[a:b:0.4],blue_hair"; vm.ApplyDirect.Execute(null); Assert.Equal(PromptItemKind.Raw,vm.Chips[0].Item.Kind); vm.Undo.Execute(null); Assert.Equal("smile",vm.English); }
    [Fact] public void QueryClearReturnsToBrowseSelectionAndScroll()
    { var vm=Fixtures.Vm(); vm.NavigateTo("special:APPEARANCE>HAIR"); vm.SelectedEntry=vm.Results[0]; vm.BrowseScroll=35; var id=vm.SelectedEntry.Entry.Id; vm.Query="red"; vm.RefreshResults(); vm.ClearQuery.Execute(null); Assert.Equal(id,vm.SelectedEntry?.Entry.Id); Assert.Equal(35,vm.RestoreScroll); Assert.Equal("容姿 > 髪",vm.BrowseLabel); }
    [Fact] public void CsvReaderPreservesQuotedCommasAndNewlines()
    { using var d=new TempDirectory(); var p=Path.Combine(d.Path,"fixture.csv"); File.WriteAllText(p,"tag,description\r\nblue_hair,\"long, Japanese\r\nlabel\"\r\n"); var rows=AcceptedAssetImporter.Csv(p); Assert.Equal("long, Japanese\r\nlabel",Assert.Single(rows)["description"]); }
    [Fact] public void MissingProductionInputFailsWithoutGeneratingFakeData()
    { using var d=new TempDirectory(); Assert.Throws<FileNotFoundException>(()=>AcceptedAssetImporter.Read(d.Path,d.Path)); Assert.Empty(Directory.GetFiles(d.Path)); }
}
