using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
namespace DanbooruTagTool.App;
public sealed record ImageTagValidationSpec(string ForgeRoot,string ImagePath,string ForgeUrl="http://127.0.0.1:7860");
public static class ImageTagAnalysisValidation
{
    public static async Task RunAsync(string specPath,string output)
    {
        var spec=JsonSerializer.Deserialize<ImageTagValidationSpec>(File.ReadAllText(specPath)) ?? throw new InvalidDataException("spec missing");
        var root=Path.GetFullPath(output); if(Directory.Exists(root) || root.StartsWith(Path.GetFullPath(AppContext.BaseDirectory),StringComparison.OrdinalIgnoreCase)) throw new IOException("fresh isolated output required");
        Directory.CreateDirectory(root); var paths=new PortablePaths(root);
        var catalog=CatalogDatabase.Open(Path.Combine(AppContext.BaseDirectory,"Data","catalog.db"));
        var main=new MainViewModel(catalog,new UserStateStore(paths.User),new NullClipboard(),paths:paths); main.Forge.ForgeUrl=spec.ForgeUrl;
        var library=main.GenerationLibrary!; await library.AddRootAsync(Path.GetDirectoryName(spec.ImagePath)!); await library.ScanAsync(); library.Selected=library.Images.Single(i=>i.Image.NormalizedPath.Equals(Path.GetFullPath(spec.ImagePath),StringComparison.OrdinalIgnoreCase));
        main.Workspace.Replace("diagnostic_original"); var vm=main.ImageTagAnalysis!; vm.ForgeRoot=spec.ForgeRoot; await vm.Setup.ExecuteAsync(null); await vm.Analyze.ExecuteAsync(null);
        if(main.English!="diagnostic_original" || !vm.Rows.Any(r=>r.Value.Confidence is not null)) throw new InvalidDataException("real analysis failed: "+vm.Status);
        var selected=vm.Rows.First(r=>r.Value.Confidence is not null); selected.Selected=true; vm.AddSelected.Execute(null);
        if(!main.Workspace.Items.Any(i=>(i.Canonical ?? i.Surface.Trim()).Replace(' ','_')==selected.Value.Tag)) throw new InvalidDataException("explicit add failed");
        main.Workspace.Undo(); var restored=new MainViewModel(catalog,new UserStateStore(paths.User),new NullClipboard(),paths:paths); if(restored.English!="diagnostic_original") throw new InvalidDataException("prompt restart mismatch");
        var model=new ImageTagAnalysisStore(root).LoadProfile()!; var result=new ImageTagAnalysisStore(root).Latest(await LocalTaggerClient.HashAsync(spec.ImagePath))!;
        await vm.Reopen.ExecuteAsync(null); if(result.Tags.Count==0 || result.Model!=model) throw new InvalidDataException("persistence mismatch");
        var window=new MainWindow(main){Width=1400,Height=900,Left=-30000,Top=-30000,ShowInTaskbar=false}; window.Show(); main.WorkspaceIndex=2;
        try { window.UpdateLayout(); Expand(window); window.UpdateLayout(); var bitmap=new RenderTargetBitmap((int)window.ActualWidth,(int)window.ActualHeight,96,96,PixelFormats.Pbgra32); bitmap.Render(window); var encoder=new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap)); using var stream=File.Create(Path.Combine(root,"library-analysis.png")); encoder.Save(stream); }
        finally {window.Close();}
        File.WriteAllText(Path.Combine(root,"result.json"),JsonSerializer.Serialize(new {Pass=true,Tags=result.Tags.Count,AboveThreshold=result.Tags.Count(t=>t.Confidence>=.35),SelectedTag=selected.Value.Tag,Model=model,PromptMutation="explicit selected add + undo only",CatalogMutation=false,SchemaMigration=false}));
    }
    private static void Expand(DependencyObject parent) { for(var i=0;i<VisualTreeHelper.GetChildrenCount(parent);i++){var child=VisualTreeHelper.GetChild(parent,i); if(child is Expander e && e.Header?.ToString()=="ローカル画像→tag診断") e.IsExpanded=true; Expand(child);} }
    private sealed class NullClipboard:IClipboardService {public string Read()=>"";public void Write(string text){} }
}
