using System.IO;
using System.Diagnostics;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;
// Opt in explicitly with DTT_PRODUCTION_CATALOG; CI never manufactures production data.
public sealed class ProductionFactAttribute : FactAttribute
{
    public ProductionFactAttribute() { if (Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG") == null) Skip = "Production catalog is local/protected; set DTT_PRODUCTION_CATALOG explicitly."; }
}
public class ProductionTests(ITestOutputHelper output)
{
    [ProductionFact] public void ProductionCatalogCoverageEligibilitySearchAndSourceIntegrity()
    {
        var path=Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!; var watch=Stopwatch.StartNew();
        var catalog=CatalogDatabase.Open(path); output.WriteLine($"Catalog open {watch.ElapsedMilliseconds} ms");
        Assert.Equal(30629,catalog.Entries.Count(e=>!e.IsSpecial)); Assert.Equal(2983,catalog.Entries.Count(e=>e.IsSpecial));
        Assert.Equal(28226,catalog.Entries.Count(e=>!e.IsSpecial && e.BrowseClassification==BrowseClassificationStatus.Proposed));
        Assert.Equal(2403,catalog.Entries.Count(e=>!e.IsSpecial && e.BrowseClassification==BrowseClassificationStatus.Unresolved));
        var special=catalog.Entries.Where(e=>e.IsSpecial).ToArray();
        Assert.Equal(1813,special.Count(e=>e.CanBrowse)); Assert.Equal(12,special.Count(e=>!e.CanSearch));
        output.WriteLine($"Special paths: {special.Count(e=>e.Paths.Length>0)} classified / {special.Count(e=>e.Paths.Length==0)} explicitly unresolved");
        var search=new SearchEngine(catalog);
        foreach (var q in new[]{"blue_hair","青い髪","anal","a","s","hair","blue hair","青い hair","anal_sex","blu","lue","blie hair"})
        {
            watch.Restart(); var hits=search.Search(q); Assert.NotEmpty(hits);
            output.WriteLine($"{q}: {watch.Elapsed.TotalMilliseconds:F2} ms; hits={hits.Count}; " + string.Join(" | ",hits.Take(5).Select(h=>$"{h.Entry.English} [{h.Rank}]")));
            if(q=="anal") { Assert.Equal("anal",hits[0].Entry.Canonical); Assert.DoesNotContain(hits,h=>h.Entry.Canonical=="piano" || h.Entry.Canonical?.StartsWith("analog",StringComparison.Ordinal)==true); }
        }
        var sourceRoot=Environment.GetEnvironmentVariable("DTT_SOURCE_ROOT"); var authorityRoot=Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT");
        if(sourceRoot!=null && authorityRoot!=null)
        {
            using var report=JsonDocument.Parse(File.ReadAllText(Path.Combine(Path.GetDirectoryName(path)!,"import-report.json")));
            foreach(var p in report.RootElement.GetProperty("Sources").EnumerateObject())
            { var root=AcceptedAssetImporter.ProtectedInputs.Contains(p.Name)?sourceRoot:authorityRoot; Assert.Equal(p.Value.GetString(),AcceptedAssetImporter.Hash(Path.Combine(root,p.Name))); }
        }
    }
    [ProductionFact] public void ProductionPromptParserEightyItemBenchmark()
    {
        var catalog=CatalogDatabase.Open(Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!);
        var parser=new PromptParser(catalog);
        var normal=catalog.Entries.Where(e=>e.CanSearch && e.Canonical is not null).OrderBy(e=>e.Id,StringComparer.Ordinal).Take(76).Select(e=>e.Canonical!).ToArray();
        Assert.Equal(76,normal.Length);
        var prompt=string.Join(",",normal.Append($"({normal[0]}:1.1)").Append("<lora:benchmark_style:0.8>").Append("BREAK").Append("custom_trigger"));
        Assert.Equal(80,parser.Parse(prompt).Length);
        var times=new List<double>();
        for(var i=0;i<5;i++)
        {
            var watch=Stopwatch.StartNew(); var items=parser.Parse(prompt); watch.Stop();
            Assert.Equal(80,items.Length); times.Add(watch.Elapsed.TotalMilliseconds);
        }
        times.Sort();
        output.WriteLine($"PromptParser.Parse 80 items: min={times[0]:F2} ms; median={times[2]:F2} ms; max={times[^1]:F2} ms");
    }

    [ProductionFact] public void ProductionGeneralBrowseAddSearchUndoCopyAndRestart()
    {
        var catalog=CatalogDatabase.Open(Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!);
        var provider=GeneralBrowseProvider.FromCatalog(catalog);
        Assert.False(provider.IsPending);
        Assert.Equal(28226,catalog.Entries.Count(e=>!e.IsSpecial && e.BrowseClassification==BrowseClassificationStatus.Proposed));
        Assert.Equal(28220,provider.Browse("").Count);
        Assert.Equal(6,catalog.Entries.Count(e=>!e.IsSpecial && e.BrowseClassification==BrowseClassificationStatus.Proposed && !e.CanBrowse));
        Assert.DoesNotContain(provider.Browse(""),e=>e.BrowseClassification!=BrowseClassificationStatus.Proposed);
        using var temp=new TempDirectory();
        var store=new UserStateStore(Path.Combine(temp.Path,"UserData","user.db"));
        var clipboard=new MemoryClipboard();
        var vm=new MainViewModel(catalog,store,clipboard,provider);
        var sample=catalog.Entries.First(e=>!e.IsSpecial && e.BrowseClassification==BrowseClassificationStatus.Proposed && e.CanBrowse && e.Paths.Length>0 && e.Paths[0].SubgenreId.Length>0 && !catalog.Entries.Any(s=>s.IsSpecial && s.Canonical==e.Canonical && s.CanSearch));
        var category=vm.Navigation.Single(n=>n.Key=="general").Children.Single(n=>n.Key=="general:"+sample.Paths[0].GenreId+">");
        Assert.Contains(category.Children,n=>n.Key=="general:"+sample.Paths[0].Key);
        vm.NavigateTo("general");
        vm.NavigateTo(category.Key);
        vm.NavigateTo("general:"+sample.Paths[0].Key);
        vm.Back.Execute(null);
        Assert.Equal(category.Key,vm.BrowseKey);
        vm.NavigateTo("general:"+sample.Paths[0].Key);
        Assert.Contains(vm.Results,r=>r.Entry.Canonical==sample.Canonical);

        vm.Query=sample.Japanese!; vm.RefreshResults();
        Assert.Contains(vm.Results,r=>r.Entry.Canonical==sample.Canonical);
        vm.Results.Single(r=>r.Entry.Canonical==sample.Canonical).Add.Execute(null);
        Assert.Contains(vm.Chips,c=>c.Item.Canonical==sample.Canonical);
        vm.OpenEditor.Execute(null);
        vm.Copy.Execute(null);
        Assert.Equal(vm.English,clipboard.Value);
        vm.Undo.Execute(null); Assert.DoesNotContain(vm.Chips,c=>c.Item.Canonical==sample.Canonical);
        vm.Redo.Execute(null); Assert.Contains(vm.Chips,c=>c.Item.Canonical==sample.Canonical);

        var restarted=new MainViewModel(catalog,store,new MemoryClipboard(),provider);
        Assert.Equal(1,restarted.WorkspaceIndex);
        Assert.Equal(vm.English,restarted.English);
        Assert.Contains(restarted.Chips,c=>c.Item.Canonical==sample.Canonical);
        output.WriteLine($"General path {sample.Paths[0].Label}; Japanese query {sample.Japanese}; canonical add/undo/redo/copy and SQLite restart restore PASS");
    }
}
