using System.IO;
using System.Text.Json;
using System.Windows;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App;
public partial class App : Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        // This text-only portable app favors predictable rendering across GPU/remote-desktop drivers.
        System.Windows.Media.RenderOptions.ProcessRenderMode = System.Windows.Interop.RenderMode.SoftwareOnly;
        try
        {
            if (e.Args.FirstOrDefault() == "--build-catalog")
            {
                if (e.Args.Length != 4) throw new ArgumentException("--build-catalog <protected-source-root> <authority-root> <output-directory>");
                var output = CatalogOutputGuard.Validate(e.Args[3], e.Args[1], e.Args[2]);
                var result = AcceptedAssetImporter.Read(e.Args[1], e.Args[2]);
                CatalogDatabase.Build(Path.Combine(output, "catalog.db"), result.Entries, JsonSerializer.Serialize(result.SourceHashes));
                File.WriteAllText(Path.Combine(output, "import-report.json"), JsonSerializer.Serialize(new
                {
                    Total = result.Entries.Length,
                    General = result.Entries.Count(x => !x.IsSpecial),
                    Special = result.Entries.Count(x => x.IsSpecial),
                    GeneralTaxonomy = new
                    {
                        Proposed = result.Entries.Count(x => !x.IsSpecial && x.BrowseClassification == BrowseClassificationStatus.Proposed),
                        Unresolved = result.Entries.Count(x => !x.IsSpecial && x.BrowseClassification == BrowseClassificationStatus.Unresolved),
                        EligibleForBrowse = result.Entries.Count(x => !x.IsSpecial && x.BrowseClassification == BrowseClassificationStatus.Proposed && x.CanBrowse)
                    },
                    Sources = result.SourceHashes
                }, new JsonSerializerOptions { WriteIndented = true }));
                Shutdown(0); return;
            }

            var paths = new PortablePaths(AppContext.BaseDirectory);
            ICatalog catalog; string? warning = null;
            try { catalog = CatalogDatabase.Open(paths.Catalog); }
            catch (FileNotFoundException ex) { catalog = new Catalog([]); warning = ex.Message; }

            if (e.Args.FirstOrDefault() == "--issue76-v2-prototype")
            {
                if (e.Args.Length != 2) throw new ArgumentException("--issue76-v2-prototype <issue76_v2_candidate_mapping_v0_8.csv>");
                if (warning != null) throw new FileNotFoundException(warning, paths.Catalog);
                var index = Issue76SpecialBrowseV2Loader.Load(e.Args[1]);
                var prototype = new Issue76BrowsePrototypeViewModel(catalog, index);
                var prototypeWindow = new Issue76BrowsePrototypeWindow(prototype);
                MainWindow = prototypeWindow;
                prototypeWindow.Show();
                return;
            }

            var vm = new MainViewModel(catalog, new UserStateStore(paths.User), new ClipboardService(), GeneralBrowseProvider.FromCatalog(catalog));
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
