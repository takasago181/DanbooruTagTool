using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.App.Views;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
namespace DanbooruTagTool.App;
public sealed record PracticalFeatureSpec(string ForgeRoot,string ModelHash,long Seed=234235236,string ForgeUrl="http://127.0.0.1:7860");
/// <summary>Opt-in acceptance for the three personal features; fresh isolated state, existing real Forge/tagger.</summary>
public static class PracticalFeatureValidation
{
    public static async Task RunAsync(string specPath,string output,bool production)
    {
        var spec=JsonSerializer.Deserialize<PracticalFeatureSpec>(File.ReadAllText(specPath)) ?? throw new InvalidDataException("spec missing");
        var root=Path.GetFullPath(output);if(Directory.Exists(root)||root.StartsWith(Path.GetFullPath(AppContext.BaseDirectory),StringComparison.OrdinalIgnoreCase))throw new IOException("fresh isolated output required");Directory.CreateDirectory(root);
        var paths=new PortablePaths(root);var catalog=CatalogDatabase.Open(Path.Combine(AppContext.BaseDirectory,"Data","catalog.db"));var main=new MainViewModel(catalog,new UserStateStore(paths.User),new NullClipboard(),paths:paths);main.Forge.ForgeUrl=spec.ForgeUrl;
        var window=new MainWindow(main){Width=1400,Height=900,Left=-30000,Top=-30000,ShowInTaskbar=false};window.Show();
        try
        {
            await main.Create.RefreshCapabilities.ExecuteAsync(null); main.Create.SelectedForgeModel=main.Create.ForgeModels.Single(m=>m.Hash==spec.ModelHash);main.Create.ApplyForgeModel.Execute(null);
            main.Create.Seed=spec.Seed.ToString();main.Create.Steps="4";main.Create.Cfg="4";main.Create.Sampler="Euler";main.Create.Scheduler="Karras";main.Create.Width="512";main.Create.Height="512";
            main.Workspace.Replace("original raw");main.NegativeWorkspace.Replace("text, watermark");var personal=main.PersonalRules!;personal.CaptureModel.Execute(null);personal.Trigger="still life";personal.Warning="personal scoped diagnostic";personal.Note="isolated acceptance";personal.AddHint.Execute(null);Check(main.English=="original raw","hint auto mutation");personal.SelectedHint=personal.Hints.Single();personal.ApplyPositive.Execute(null);Check(main.English.Contains("still life"),"explicit hint");
            personal.Global=true;personal.Token="forbidden_raw";personal.Severity=PersonalSeverity.BlockAdd;personal.AddRule.Execute(null);Check(main.Workspace.AppendText("forbidden_raw").Added==0,"block-add");main.Workspace.DirectEdit("forbidden_raw");Check(main.Intelligence.Warnings.Any(w=>w.Code=="personal-BlockAdd"),"existing raw warning");Check(main.English=="forbidden_raw","raw preservation");
            personal.Token="smile";personal.Severity=PersonalSeverity.Hide;personal.AddRule.Execute(null);main.Query="smile";main.RefreshResults();Check(main.Results.All(r=>r.Entry.Canonical!="smile"),"personal hide");personal.Token="teapot";personal.Severity=PersonalSeverity.Warn;personal.AddRule.Execute(null);
            var template=main.Templates!;template.Source="a {blue|red} and white porcelain teapot, on a wooden table";template.Cap=2;template.Preview.Execute(null);Check(template.Variants.Count==2,"bounded count");template.Save.Execute(null);template.Selected=template.Variants[0];template.Materialize.Execute(null);Check(main.English==template.Selected,"materialization");Check(main.Intelligence.Warnings.Any(w=>w.Code=="personal-hint"),"model hint diagnostic");
            await template.ToExperiment.ExecuteAsync(null);var lab=main.Experiments!;Check(lab.TemplateDraftReady,"experiment draft: "+lab.Status);lab.Seeds=spec.Seed.ToString();lab.Save.Execute(null);Check(lab.SelectedExperiment is not null,"experiment save: "+lab.Status);
            if(production)await main.Create.GenerateAsync();else {await lab.Start.ExecuteAsync(null);Check(lab.Cells.Count==2 && lab.Cells.All(c=>c.Attempt.Status=="Succeeded"),"template trials: "+lab.Status);}
            var library=main.GenerationLibrary!;await library.Refresh.ExecuteAsync(null);Check(library.Images.Count==(production?1:2),"real generation Library: "+main.Forge.RecipeStatus);library.Selected=library.Images.First();
            var analysis=main.ImageTagAnalysis!;analysis.ForgeRoot=spec.ForgeRoot;await analysis.Setup.ExecuteAsync(null);var promptBefore=main.English;await analysis.Analyze.ExecuteAsync(null);Check(main.English==promptBefore && analysis.Rows.Any(r=>r.Value.Confidence is not null),"real WD14: "+analysis.Status);
            var row=analysis.Rows.First(r=>r.Value.Confidence is not null && !main.Workspace.Contains(r.Value.Tag));row.Selected=true;analysis.AddSelected.Execute(null);Check(main.English!=promptBefore,"explicit analyzed tag add");main.Workspace.Undo();Check(main.English==promptBefore,"analysis Undo");analysis.Threshold=.8;Check(analysis.Rows.Where(r=>r.Value.Confidence is not null).All(r=>r.Value.Confidence>=.8),"threshold");analysis.Filter=row.Value.Tag;Check(analysis.Rows.All(r=>r.Value.Tag.Contains(row.Value.Tag)),"filter");analysis.Filter="";analysis.Threshold=.35;
            library.LoadInCreate.Execute(null);Check(main.Create.TryRecipe(out var restored,out _) && restored!.ModelHash==spec.ModelHash,"Recipe restore");main.Create.SaveName="isolated practical recipe";main.Create.Save.Execute(null);
            var reopened=new MainViewModel(catalog,new UserStateStore(paths.User),new NullClipboard(),paths:paths);reopened.Create.Load(reopened.Presets.Single(),"restart");Check(reopened.Create.ModelHash==spec.ModelHash && reopened.PersonalRules!.Hints.Count==1,"rules/recipe restart");Check(new TemplateStore(root).Load().Source==template.Source,"template restart");Check(reopened.Workspace.AppendText("forbidden_raw").Added==0,"block restart");
            var result=new ImageTagAnalysisStore(root).Latest(await LocalTaggerClient.HashAsync(library.SelectedPath))!;Check(result.Tags.Count>0,"analysis evidence restart");
            Render(new TemplateView{DataContext=template},root,"templates.png",850,700);Render(new ImageTagAnalysisView{DataContext=analysis},root,"image-tags.png",1100,760);Render(new PersonalRulesView{DataContext=personal},root,"personal-rules.png",950,750);
            File.WriteAllText(Path.Combine(root,"result.json"),JsonSerializer.Serialize(new{Pass=true,Runtime=Environment.ProcessPath,Production=production,GenerationPosts=production?1:2,TemplateVariants=2,TagCount=result.Tags.Count,SelectedTag=row.Value.Tag,Model=result.Model,UserSchema=UserStateStore.SchemaVersion,LibrarySchema=GenerationLibraryStore.SchemaVersion,UserData="fresh isolated only",CatalogMutation=false,RecipeRestart=true,PersonalRulesRestart=true},new JsonSerializerOptions{WriteIndented=true}));
        }
        finally{window.Close();}
    }
    private static void Check(bool pass,string gate){if(!pass)throw new InvalidDataException("Practical acceptance: "+gate);}
    private static void Render(FrameworkElement view,string root,string filename,int width,int height){view.Measure(new(width,height));view.Arrange(new Rect(0,0,width,height));view.UpdateLayout();var bitmap=new RenderTargetBitmap(width,height,96,96,PixelFormats.Pbgra32);bitmap.Render(view);var encoder=new PngBitmapEncoder();encoder.Frames.Add(BitmapFrame.Create(bitmap));using var stream=File.Create(Path.Combine(root,filename));encoder.Save(stream);}
    private sealed class NullClipboard:IClipboardService{public string Read()=>"";public void Write(string text){}}
}
