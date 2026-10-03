using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using DanbooruTagTool.App.ViewModels;
using Xunit;
namespace DanbooruTagTool.Tests;
public sealed class Issue236PersonalRuleTests
{
    [Fact] public void HashScopeIsStableUnderRenameAndNeverFallsBackToSameName()
    {
        var key=new PersonalModelKey("same","abc");Assert.True(key.Matches(new("renamed","ABC")));Assert.False(key.Matches(new("same","different")));Assert.False(key.Matches(new("same","")));Assert.True(new PersonalModelKey("same").Matches(new("SAME")));Assert.True(new PersonalModelKey().Matches(new("any")));
    }
    [Fact] public void AliasAndWeightBlacklistUsesExistingCanonicalResolution()
    {
        var evaluator=new PersonalRuleEvaluator(Fixtures.Catalog());var p=Fixtures.Workspace();p.Replace("(blue_hair:1.2), raw_token");var rules=new PersonalRules(1,[],[new(Guid.NewGuid(),"azure_locks",PersonalSeverity.BlockAdd,new()),new(Guid.NewGuid(),"raw token",PersonalSeverity.Warn,new())]);
        Assert.Single(evaluator.Matching(rules,new(),p.Items[0]));Assert.Single(evaluator.Matching(rules,new(),p.Items[1]));Assert.Equal(2,evaluator.Warnings(rules,new(),p,Fixtures.Workspace()).Length);Assert.Equal("(blue_hair:1.2), raw_token",p.English);
    }
    [Fact] public void HideWarnBlockArePersonalAndAllExplicitAppendPathsRespectBlockWithoutDeletingRaw()
    {
        using var d=new TempDirectory();var main=new MainViewModel(Fixtures.Catalog(),new MemoryStore(),new MemoryClipboard(),paths:new(d.Path));var vm=main.PersonalRules!;
        main.Workspace.Replace("azure_locks, raw_token");vm.Token="azure_locks";vm.Severity=PersonalSeverity.BlockAdd;vm.AddRule.Execute(null);
        Assert.Equal("azure_locks, raw_token",main.English);Assert.Contains(main.Intelligence.Warnings,w=>w.Code=="personal-BlockAdd");main.Workspace.DirectEdit("existing raw");
        Assert.False(main.Workspace.Add(Fixtures.Catalog().Resolve("blue_hair")!));Assert.Equal(0,main.Workspace.AppendText("(blue_hair:1.2)").Added);Assert.Contains("block-add",main.Status);
        vm.Token="smile";vm.Severity=PersonalSeverity.Hide;vm.AddRule.Execute(null);main.Query="smile";main.RefreshResults();Assert.DoesNotContain(main.Results,r=>r.Entry.Canonical=="smile");Assert.NotNull(Fixtures.Catalog().Resolve("smile"));
        vm.Token="raw_token";vm.Severity=PersonalSeverity.Warn;vm.AddRule.Execute(null);main.Workspace.AppendText("raw_token");Assert.Contains(main.Intelligence.Warnings,w=>w.Code=="personal-Warn");Assert.Contains("raw_token",main.English);
        var reopened=new MainViewModel(Fixtures.Catalog(),new MemoryStore(),new MemoryClipboard(),paths:new(d.Path));Assert.False(reopened.Workspace.Add(Fixtures.Catalog().Resolve("blue_hair")!));
    }
    [Fact] public void ModelHintsAndScopedBlacklistPersistAndOnlyApplyOnExplicitAction()
    {
        using var d=new TempDirectory();var state=new MemoryStore();var main=new MainViewModel(Fixtures.Catalog(),state,new MemoryClipboard(),paths:new(d.Path));main.Workspace.Replace("original");main.Create.Model="test";main.Create.ModelHash="abc";var vm=main.PersonalRules!;vm.CaptureModel.Execute(null);vm.Trigger="trigger";vm.Positive="blue_hair";vm.Negative="lowres";vm.Warning="personal caution";vm.AddHint.Execute(null);
        vm.Token="smile";vm.Severity=PersonalSeverity.BlockAdd;vm.AddRule.Execute(null);Assert.Equal("original",main.English);Assert.Contains(main.Intelligence.Warnings,w=>w.Code=="personal-hint");
        vm.SelectedHint=Assert.Single(vm.Hints);vm.ApplyPositive.Execute(null);Assert.Contains("trigger",main.English);vm.ApplyNegative.Execute(null);Assert.Contains("lowres",main.Negative.English);
        main.Create.ModelHash="different";Assert.Empty(vm.Hints);Assert.True(main.Workspace.Add(Fixtures.Catalog().Resolve("smile")!));var text=main.English;main.Create.ModelHash="abc";Assert.Equal(text,main.English);
        var reopened=new MainViewModel(Fixtures.Catalog(),state,new MemoryClipboard(),paths:new(d.Path));reopened.Create.Model="renamed";reopened.Create.ModelHash="abc";Assert.Single(reopened.PersonalRules!.Hints);Assert.Equal(text,reopened.English);Assert.False(reopened.NegativeWorkspace.Add(Fixtures.Catalog().Resolve("smile")!));Assert.Equal(2,new PersonalRuleStore(d.Path).Load().Hints.Count+new PersonalRuleStore(d.Path).Load().Exclusions.Count);
    }
    [Fact] public void InvalidRuleFilePreservesRawStateAndBlocksAppendUntilRepaired()
    {
        using var d=new TempDirectory();var path=Path.Combine(d.Path,"UserData","PersonalRules","rules.json");Directory.CreateDirectory(Path.GetDirectoryName(path)!);File.WriteAllText(path,"{\"Version\":1,\"Hints\":[null],\"Exclusions\":[]}");var before=File.ReadAllBytes(path);
        var state=new MemoryStore();var initial=Fixtures.Vm(state,new MemoryClipboard());initial.Workspace.Replace("kept raw");var main=new MainViewModel(Fixtures.Catalog(),state,new MemoryClipboard(),paths:new(d.Path));Assert.Equal("kept raw",main.English);Assert.Equal(0,main.Workspace.AppendText("smile").Added);Assert.Equal(before,File.ReadAllBytes(path));
        File.WriteAllText(path,"{\"Version\":1,\"Hints\":[],\"Exclusions\":[]}");main.PersonalRules!.Reload.Execute(null);Assert.Equal(1,main.Workspace.AppendText("smile").Added);
    }
    [Fact] public void FutureVersionIsNeverOverwritten()
    {
        using var d=new TempDirectory();var path=Path.Combine(d.Path,"UserData","PersonalRules","rules.json");Directory.CreateDirectory(Path.GetDirectoryName(path)!);File.WriteAllText(path,"{\"Version\":99,\"Hints\":[],\"Exclusions\":[]}");var bytes=File.ReadAllBytes(path);Assert.Throws<InvalidDataException>(()=>new PersonalRuleStore(d.Path).Save(PersonalRules.Empty));Assert.Equal(bytes,File.ReadAllBytes(path));
    }
}
