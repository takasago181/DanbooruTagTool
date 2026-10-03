using System.IO;
using System.Windows;
using Application = System.Windows.Application;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App;
public partial class App : Application
{
    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        try
        {
            if (e.Args.FirstOrDefault() == "--build-catalog")
                throw new NotSupportedException("Catalog compilation moved to DanbooruTagTool.Maintenance: compile <manifest.json> <new-empty-output>.");
            if (e.Args.FirstOrDefault() == "--validate-image-tags")
            {
                if (e.Args.Length != 3) throw new ArgumentException("--validate-image-tags <spec.json> <fresh-output>");
                ShutdownMode = ShutdownMode.OnExplicitShutdown;
                await ImageTagAnalysisValidation.RunAsync(e.Args[1],e.Args[2]); Shutdown(0); return;
            }
            if (e.Args.FirstOrDefault() == "--validate-prompt-intelligence")
            {
                if (e.Args.Length != 2) throw new ArgumentException("--validate-prompt-intelligence <new-empty-output-directory>");
                ShutdownMode = ShutdownMode.OnExplicitShutdown;
                await PromptIntelligenceValidation.RunAsync(e.Args[1]); Shutdown(0); return;
            }
            if (e.Args.FirstOrDefault() == "--validate-forge-workflow")
            {
                if (e.Args.Length != 3) throw new ArgumentException("--validate-forge-workflow <spec.json> <new-output>");
                ShutdownMode = ShutdownMode.OnExplicitShutdown;
                await ForgeWorkflowValidation.RunAsync(e.Args[1], e.Args[2]); Shutdown(0); return;
            }
            if (e.Args.FirstOrDefault() is "--validate-regions" or "--validate-regions-production")
            {
                if (e.Args.Length != 3) throw new ArgumentException("--validate-regions <spec.json> <new-output>");
                ShutdownMode = ShutdownMode.OnExplicitShutdown;
                await RegionComposerValidation.RunAsync(e.Args[1], e.Args[2], e.Args[0] == "--validate-regions-production"); Shutdown(0); return;
            }
            if (e.Args.FirstOrDefault() == "--validate-experiments")
            {
                if (e.Args.Length != 3) throw new ArgumentException("--validate-experiments <spec.json> <new-output>");
                ShutdownMode = ShutdownMode.OnExplicitShutdown;
                await ExperimentLabValidation.RunAsync(e.Args[1], e.Args[2]); Shutdown(0); return;
            }
            if (e.Args.FirstOrDefault() == "--validate-experiments-ui")
            {
                if (e.Args.Length != 4) throw new ArgumentException("--validate-experiments-ui <spec.json> <prior-isolated-evidence> <new-output>");
                ShutdownMode = ShutdownMode.OnExplicitShutdown;
                await ExperimentLabValidation.RenderExistingAsync(e.Args[1], e.Args[2], e.Args[3]); Shutdown(0); return;
            }
            if (e.Args.FirstOrDefault() == "--validate-lora")
            {
                if (e.Args.Length != 2) throw new ArgumentException("--validate-lora <new-empty-output-directory>");
                ShutdownMode = ShutdownMode.OnExplicitShutdown;
                await LoraLibraryValidation.RunAsync(e.Args[1]); Shutdown(0); return;
            }
            if (e.Args.FirstOrDefault() == "--validate-library")
            {
                if (e.Args.Length != 2) throw new ArgumentException("--validate-library <new-empty-output-directory>");
                ShutdownMode = ShutdownMode.OnExplicitShutdown;
                await GenerationLibraryValidation.RunAsync(e.Args[1]);
                Shutdown(0); return;
            }
            var paths = new PortablePaths(AppContext.BaseDirectory);
            ICatalog catalog; string? warning = null;
            try { catalog = CatalogDatabase.Open(paths.Catalog); }
            catch (FileNotFoundException ex) { catalog = new Catalog([]); warning = ex.Message; }
            SpecialBrowseV2Index? specialBrowse = null;
            if (warning == null)
            {
                try { specialBrowse = SpecialBrowseCatalogReader.FromCatalog(catalog); }
                catch (InvalidDataException ex) { warning = ex.Message; }
            }
            var vm = new MainViewModel(catalog, new UserStateStore(paths.User), new ClipboardService(), GeneralBrowseProvider.FromCatalog(catalog), specialBrowse: specialBrowse, paths: paths);
            if (warning != null) vm.Status = warning;
            var window = new MainWindow(vm); MainWindow = window; window.Show();
        }
        catch (Exception ex)
        {
            if (e.Args.Length > 0) File.WriteAllText(Path.Combine(AppContext.BaseDirectory, "catalog-build-error.txt"), ex.ToString());
            else MessageBox.Show(ex.Message, "DanbooruTagTool 起動エラー", MessageBoxButton.OK, MessageBoxImage.Error);
            Shutdown(1);
        }
    }
}
public sealed class ClipboardService : IClipboardService
{
    public string Read() => Clipboard.ContainsText() ? Clipboard.GetText() : "";
    public void Write(string text) { if (text.Length == 0) Clipboard.Clear(); else Clipboard.SetText(text); }
}
