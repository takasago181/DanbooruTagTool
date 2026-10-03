using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using DanbooruTagTool.App.ViewModels;
using Xunit;
namespace DanbooruTagTool.Tests;
public sealed class Issue234TemplateTests
{
    [Fact] public void NestedAlternativesAndWildcardProductsAreDeterministic()
    {
        var wildcards = new Dictionary<string,string[]> { ["color"] = ["red", "{blue|black}"], ["outer"] = ["__color__"] };
        var p = PromptTemplates.Preview("__outer__ {hair|eyes}", wildcards);
        Assert.Equal(6, (int)p.Count); Assert.Equal(new[] {"red hair", "red eyes", "blue hair", "blue eyes", "black hair", "black eyes"}, p.Variants);
        Assert.Equal(p.Variants, PromptTemplates.Preview(p.Source, wildcards).Variants);
    }
    [Fact] public void CountBeforeEnumerationPreventsExponentialMaterialization()
    {
        var p = PromptTemplates.Preview(string.Concat(Enumerable.Repeat("{a|b}", 100)), new Dictionary<string,string[]>(), 64);
        Assert.Equal(System.Numerics.BigInteger.Pow(2,100), p.Count); Assert.Empty(p.Variants);
        Assert.Throws<ArgumentException>(() => PromptTemplates.Preview("x", new Dictionary<string,string[]>(), 257));
    }
    [Theory] [InlineData("{2$$a|b}")] [InlineData("{0.5::a|b}")] [InlineData("{a}")] [InlineData("${a|b}")] [InlineData("{a|b")] [InlineData("__missing__")] [InlineData(@"\{a|b}")]
    public void UnsupportedSyntaxIsLossless(string source) => Assert.Equal(source, Assert.Single(PromptTemplates.Preview(source, new Dictionary<string,string[]>()).Variants));
    [Fact] public void CircularAndDeepReferencesAndOversizedOutputFailClosed()
    {
        Assert.Throws<ArgumentException>(() => PromptTemplates.Preview("__a__", new Dictionary<string,string[]> { ["a"] = ["__b__"], ["b"] = ["__a__"] }));
        var deep = Enumerable.Range(0,20).ToDictionary(i => i.ToString(), i => new[]{i == 19 ? "last" : "__" + (i+1) + "__"});
        Assert.Throws<ArgumentException>(() => PromptTemplates.Preview("__0__", deep));
        Assert.Throws<ArgumentException>(() => PromptTemplates.Preview("__a____a__", new Dictionary<string,string[]> { ["a"] = [new string('a',9000)] }));
    }
    [Fact] public async Task TemplateExperimentHandoffPinsConditionsAndUsesExistingLiteralTrialsWithoutGeneration()
    {
        using var d = new TempDirectory(); var api = new ProbeApi();
        var main = new MainViewModel(Fixtures.Catalog(),new MemoryStore(),new MemoryClipboard(),paths:new(d.Path),generationApi:api);
        main.Create.Load(new(Guid.NewGuid(),"baseline","","portrait","text",new("fixture",1,8,"Euler","Karras",4,512,640,"abc123")),"fixture");
        var vm = main.Templates!; vm.Source = "{blue|red} hair"; vm.Preview.Execute(null); await vm.ToExperiment.ExecuteAsync(null);
        Assert.Equal("portrait",main.English); Assert.Equal(0,api.Posts); Assert.True(main.Experiments!.TemplateDraftReady);
        main.Experiments.Save.Execute(null); var plan = new ExperimentStore(Path.Combine(d.Path,"UserData","experiment-lab.db")).Load(main.Experiments.SelectedExperiment!.Id);
        Assert.Equal("blue hair",plan.Trials[0].Requested.Positive); Assert.Equal("red hair",plan.Trials[1].Requested.Positive);
        Assert.All(plan.Trials,t => Assert.Equal("text",t.Requested.Negative)); ExperimentPlanner.Validate(plan); Assert.Equal(0,api.Posts);
    }
    private sealed class ProbeApi : IForgeGenerationApiClient
    {
        public int Posts;
        public Task<ForgeApiCapabilities> ProbeAsync(string url,CancellationToken ct=default) => Task.FromResult(new ForgeApiCapabilities([new("fixture","fixture","abc123")],["Euler"],["Karras"]));
        public Task<ForgeApiResult> GenerateAsync(string url,ForgeApiRequest r,string dir,CancellationToken ct=default) { Posts++; return Task.FromResult(new ForgeApiResult(false,"unexpected")); }
    }
    [Fact] public void UserOwnedTemplateAndWildcardsReopenWithoutPromptMutation()
    {
        using var d = new TempDirectory(); var store = new TemplateStore(d.Path); store.Save(new(1,"__color__",2));
        var directory = Path.Combine(d.Path,"UserData","Templates","Wildcards"); Directory.CreateDirectory(directory); File.WriteAllText(Path.Combine(directory,"color.txt"),"# comment\nred\nblue\n");
        Assert.Equal("__color__",new TemplateStore(d.Path).Load().Source); Assert.Equal(64,store.ReadWildcards("").Hashes["color"].Length);
        var main = new MainViewModel(Fixtures.Catalog(),new MemoryStore(),new MemoryClipboard(),paths:new(d.Path)); main.Workspace.Replace("smile");
        var vm = main.Templates!; Assert.Equal("smile",main.English); Assert.Empty(vm.Variants); vm.Preview.Execute(null); Assert.Equal(2,vm.Variants.Count); Assert.Equal("smile",main.English);
        vm.Selected = "blue"; vm.Materialize.Execute(null); Assert.Equal("blue",main.English); main.Workspace.Undo(); Assert.Equal("smile",main.English);
        vm.Source = "changed"; Assert.Empty(vm.Variants); Assert.False(vm.Materialize.CanExecute(null));
        vm.Save.Execute(null); Assert.Equal("changed",new TemplateStore(d.Path).Load().Source);
    }
}

