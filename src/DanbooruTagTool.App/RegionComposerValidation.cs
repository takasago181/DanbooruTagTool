using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
namespace DanbooruTagTool.App;

/// <summary>Opt-in installed-executable gate; fresh isolated UserData, three controlled requests, no real Library mutations.</summary>
public static class RegionComposerValidation
{
    public static async Task RunAsync(string specPath,string output,bool productionSmoke=false)
    {
        var spec=JsonSerializer.Deserialize<ForgeWorkflowSpec>(File.ReadAllText(specPath))!;
        var root=Path.GetFullPath(output);
        if(Directory.Exists(root) || root.StartsWith(Path.GetFullPath(AppContext.BaseDirectory).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase)) throw new IOException("Fresh output outside runtime required.");
        Directory.CreateDirectory(Path.Combine(root,"UserData"));
        var paths=new PortablePaths(root); using var wire=new Wire(root); var api=new ForgeGenerationApiClient(new HttpClient(wire){Timeout=Timeout.InfiniteTimeSpan});
        var catalog=CatalogDatabase.Open(spec.CatalogPath ?? new PortablePaths(AppContext.BaseDirectory).Catalog);
        MainViewModel NewVM()=>new(catalog,new UserStateStore(paths.User),new NullClipboard(),paths:paths,generationApi:api);
        var vm=NewVM(); var window=new MainWindow(vm){Left=-30000,Top=-30000,ShowInTaskbar=false,Width=1200,Height=900}; window.Show();
        try
        {
            await vm.Create.RefreshCapabilities.ExecuteAsync(null); vm.Create.SelectedForgeModel=vm.Create.ForgeModels.Single(m=>m.Hash==spec.ModelHash); vm.Create.ApplyForgeModel.Execute(null);
            vm.Create.Seed=spec.Seed.ToString(); vm.Create.Steps="12";vm.Create.Cfg="5";vm.Create.Sampler="Euler";vm.Create.Scheduler="Normal";vm.Create.Width="768";vm.Create.Height="512";
            var regions=vm.Regions!;regions.Common="two women, full body, outdoors, <lora:"+spec.LoraName+":0.35>";regions.SubjectA="1girl, (red hair:1.2), red dress";regions.SubjectB="1girl, blue hair, blue dress";regions.CommonNegative="low quality";regions.NegativeA="bad hands";regions.NegativeB="text";regions.Ratios="2,1";
            await regions.Detect.ExecuteAsync(null);Check(regions.Status.Contains(RegionComposer.Commit),regions.Status);
            regions.Name="isolated regional preset";regions.Save.Execute(null);Check(regions.Presets.Count==1,regions.Status);
            var reopened=NewVM();reopened.Regions!.SelectedPreset=reopened.Regions.Presets.Single();reopened.Regions.Load.Execute(null);Check(reopened.Regions.Config==regions.Config,"composer preset round-trip");
            var config=regions.Config;
            await regions.Generate.ExecuteAsync(null); Check(wire.Posts==1 && regions.Status.Contains("実画像metadata"),regions.Status);
            if(productionSmoke)
            {
                regions.Layout=RegionLayout.Vertical; await regions.Generate.ExecuteAsync(null); Check(wire.Posts==2 && regions.Status.Contains("実画像metadata"),regions.Status);
                var productionLibrary=new GenerationLibraryStore(paths.GenerationLibrary);var images=productionLibrary.Query(new(Limit:10)).Images;
                Check(images.Count==2,"production Library links");
                var metadata=images.Select(i=>productionLibrary.Metadata(i.Id)!).ToArray();
                foreach(var m in metadata) {var regional=RegionComposer.Read(m.Parameters)!;RegionComposer.Verify(regional.Config,m);Check(regional.Extension.Commit==RegionComposer.Commit,"production extension identity");}
                vm.Create.LoadImage(metadata.First(),"production isolated regional");Check(regions.RestoredRegional is not null && !vm.Create.CanGenerate,"production restore guard");
                File.WriteAllText(Path.Combine(root,"result.json"),ExperimentPlanner.Json(new{Result="PASS",Runtime=Environment.ProcessPath,Posts=wire.Posts,Metadata=metadata,LibraryRestore="PASS",RecipeRestore="PASS",PresetRestore="PASS",Extension=await api.ProbeRegionalAsync(vm.Forge.ForgeUrl)}));return;
            }
            vm.WorkspaceIndex=1;vm.CreatePageIndex=5;await Render(window,Path.Combine(root,"composer-1200.png"));window.Width=900;window.Height=750;await Render(window,Path.Combine(root,"composer-900.png"));
            await regions.Compare.ExecuteAsync(null);var lab=vm.Experiments!;Check(lab.XKind==ExperimentVariable.RegionalMode,regions.Status);
            lab.XValues="Ordinary\nHorizontal\nVertical";lab.Save.Execute(null);Check(lab.SelectedExperiment is not null,lab.Status);
            var id=lab.SelectedExperiment!.Id;await lab.Start.ExecuteAsync(null);
            var store=new ExperimentStore(Path.Combine(root,"UserData","experiment-lab.db"));var plan=store.Load(id);var attempts=store.Attempts(id);
            Check(attempts.Count==3 && attempts.All(a=>a.Status=="Succeeded" && a.LibraryImageId is not null),lab.Status+" / "+string.Join(" / ",attempts.Select(a=>a.Receipt?.Status)));
            Check(wire.Posts==4,"one direct + three controlled generation requests");
            var library=new GenerationLibraryStore(paths.GenerationLibrary);
            foreach(var a in attempts)
            {
                var trial=plan.Trials.Single(t=>t.Id==a.TrialId);var metadata=library.Metadata(a.LibraryImageId!.Value)!;
                Check(metadata.Value("Seed")==spec.Seed.ToString() && metadata.Value("Model hash")==spec.ModelHash,"fixed seed/model");
                Check(GenerationLoraProvenance.Expected(metadata.Parameters).Single().FileSha256==spec.LoraFileSha256,"fixed LoRA full-file identity");
                var r=GenerationRecipe.FromMetadata(metadata);Check(r.Regional==trial.Requested.Recipe.Regional,"Library regional config");
                if(r.Regional is { } c) { RegionComposer.Verify(c,metadata);Check(RegionComposer.Read(metadata.Parameters)!.Extension.Commit==RegionComposer.Commit,"installed extension provenance"); }
                Check(JsonSerializer.Serialize(GenerationRecipeDerivation.Read(metadata.Parameters))==JsonSerializer.Serialize(GenerationRecipeDerivation.Read(trial.Requested.Recipe.SourceParameters)),"exact trial derivation");
            }
            var horizontal=attempts.Single(a=>plan.Trials.Single(t=>t.Id==a.TrialId).X==1);var image=library.Metadata(horizontal.LibraryImageId!.Value)!;
            vm.Create.LoadImage(image,"regional Library");Check(regions.RestoredRegional==config && vm.CreatePageIndex==5 && !vm.Create.CanGenerate,"Library → composer restore / ordinary guard");
            Check(vm.Create.TryRecipe(out var restored,out _) && restored!.Regional==config,"Recipe restore");
            var actualRecipe=GenerationRecipe.FromMetadata(image);Check(!actualRecipe.UnappliedParameters.Any(p=>p.Name.StartsWith("RP ")||p.Name==RegionComposer.Key),"verified regional fields applied");
            var fresh=NewVM();fresh.Experiments!.Reload.Execute(null);fresh.Experiments.SelectedExperiment=fresh.Experiments.Experiments.Single(e=>e.Id==id);Check(fresh.Experiments.Cells.Count==3,"Lab exact reopen");
            fresh.Experiments.Selected=fresh.Experiments.Cells.First();fresh.Experiments.Rating=3;fresh.Experiments.Passed=null;fresh.Experiments.Note="pipeline verified; leakage judgment remains user-owned";fresh.Experiments.Evaluate.Execute(null);
            Check(store.Attempts(id).Single(a=>a.Id==fresh.Experiments.Selected.Attempt.Id).Evaluation?.Note.Contains("user-owned")==true,"human evaluation persistence");
            vm.CreatePageIndex=4;window.Width=1400;window.Height=900;await Render(window,Path.Combine(root,"comparison.png"));
            var left=attempts.Single(a=>plan.Trials.Single(t=>t.Id==a.TrialId).X==0).Receipt!.Metadata!;
            var differences=GenerationMetadataDiff.Compare(left,image);Check(differences.Any(d=>d.Field==RegionComposer.Key)&&differences.Where(d=>d.Field is "Seed" or "Model hash" or "Steps" or "Sampler" or "Scheduler" or "CFG" or "Size" or "LoRA").All(d=>d.State=="same"),"same conditions / config diff");
            File.WriteAllText(Path.Combine(root,"result.json"),ExperimentPlanner.Json(new{Result="PASS",Runtime=Environment.ProcessPath,Posts=wire.Posts,Capability=await api.ProbeRegionalAsync(vm.Forge.ForgeUrl),Config=config,Plan=plan,Attempts=store.Attempts(id),Diff=differences,LibraryRestore="PASS",RecipeRestore="PASS",PresetRestore="PASS",OrdinaryGuard="PASS",Leakage="Human evaluation; no automatic improvement claim"}));
        }
        finally {window.Close();}
    }
    private static async Task Render(MainWindow window,string path)
    {await window.Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ContextIdle);window.UpdateLayout();var bitmap=new RenderTargetBitmap((int)window.ActualWidth,(int)window.ActualHeight,96,96,PixelFormats.Pbgra32);bitmap.Render(window);var encoder=new PngBitmapEncoder();encoder.Frames.Add(BitmapFrame.Create(bitmap));using var file=File.Create(path);encoder.Save(file);}
    private static void Check(bool pass,string gate){if(!pass)throw new InvalidDataException("Regional E2E: "+gate);}
    private sealed class NullClipboard:IClipboardService { public string Read()=>"";public void Write(string value){} }
    private sealed class Wire(string root):DelegatingHandler(new HttpClientHandler{UseProxy=false,AllowAutoRedirect=false})
    {public int Posts;protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken ct){if(request.Method==HttpMethod.Post)await File.WriteAllTextAsync(Path.Combine(root,$"sent-{++Posts}.json"),await request.Content!.ReadAsStringAsync(ct),ct);return await base.SendAsync(request,ct);}}
}

