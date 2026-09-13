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
                var output = Path.GetFullPath(e.Args[3]);
                foreach (var root in e.Args.Skip(1).Take(2))
                    if (output.StartsWith(Path.GetFullPath(Path.Combine(root, "data")) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
                        throw new ArgumentException("Catalog output must not be inside source data.");
                var result = AcceptedAssetImporter.Read(e.Args[1], e.Args[2]);
                CatalogDatabase.Build(Path.Combine(output, "catalog.db"), result.Entries, JsonSerializer.Serialize(result.SourceHashes));
                File.WriteAllText(Path.Combine(output, "import-report.json"), JsonSerializer.Serialize(new { Total = result.Entries.Length, General = result.Entries.Count(x => !x.IsSpecial), Special = result.Entries.Count(x => x.IsSpecial), GeneralTaxonomy = "PENDING / not imported", Sources = result.SourceHashes }, new JsonSerializerOptions { WriteIndented = true }));
                Shutdown(0); return;
            }
            var paths = new PortablePaths(AppContext.BaseDirectory);
            ICatalog catalog; string? warning = null;
            try { catalog = CatalogDatabase.Open(paths.Catalog); }
            catch (FileNotFoundException ex) { catalog = new Catalog([]); warning = ex.Message; }
            var vm = new MainViewModel(catalog, new UserStateStore(paths.User), new ClipboardService());
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
