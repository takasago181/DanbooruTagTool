using System.IO;
using System.Text.Json;
using System.Windows;
using Application = System.Windows.Application;
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
                if (e.Args.Length != 4 && e.Args.Length != 6)
                    throw new ArgumentException("--build-catalog <protected-source-root> <authority-root> <output-directory> [--profile full|ordinary]");
                if (e.Args.Length == 6 && !string.Equals(e.Args[4], "--profile", StringComparison.OrdinalIgnoreCase))
                    throw new ArgumentException("--build-catalog <protected-source-root> <authority-root> <output-directory> [--profile full|ordinary]");
                var profile = e.Args.Length == 6 ? CatalogBuildProfiles.Parse(e.Args[5]) : CatalogBuildProfile.Full;
                var output = CatalogOutputGuard.Validate(e.Args[3], e.Args[1], e.Args[2]);
                var result = AcceptedAssetImporter.Read(e.Args[1], e.Args[2], profile);
                var specialBrowseEntries = SpecialBrowseV2Overlay.Bake(new Catalog(result.Entries));
                var unifiedBrowseEntries = UnifiedBrowseOverlay.Bake(new Catalog(specialBrowseEntries), e.Args[2]);
                var bakedEntries = Issue118SexualIntentOverlay.Bake(new Catalog(unifiedBrowseEntries), e.Args[2], result.SourceHashes);
                CatalogDatabase.Build(Path.Combine(output, "catalog.db"), bakedEntries, JsonSerializer.Serialize(result.SourceHashes));
                File.WriteAllText(Path.Combine(output, "import-report.json"), JsonSerializer.Serialize(new
                {
                    Profile = profile.Name(),
                    Total = result.Entries.Length,
                    General = result.Entries.Count(x => x.EffectiveCategory == "General"),
                    Special = result.Entries.Count(x => x.EffectiveCategory == "Special"),
                    Character = result.Entries.Count(x => x.EffectiveCategory == "Character"),
                    Copyright = result.Entries.Count(x => x.EffectiveCategory == "Copyright"),
                    Artist = result.Entries.Count(x => x.EffectiveCategory == "Artist"),
                    GeneralTaxonomy = new
                    {
                        Proposed = result.Entries.Count(x => !x.IsSpecial && x.BrowseClassification == BrowseClassificationStatus.Proposed),
                        Unresolved = result.Entries.Count(x => !x.IsSpecial && x.BrowseClassification == BrowseClassificationStatus.Unresolved),
                        EligibleForBrowse = result.Entries.Count(x => !x.IsSpecial && x.BrowseClassification == BrowseClassificationStatus.Proposed && x.CanBrowse)
                    },
                    SexualIntent = new
                    {
                        Identities = Issue118SexualIntentOverlay.IdentityCount,
                        Sexual = Issue118SexualIntentOverlay.SexualCount,
                        Contextual = Issue118SexualIntentOverlay.ContextualCount,
                        NonSexual = Issue118SexualIntentOverlay.NonSexualCount,
                        Unclassified = Issue118SexualIntentOverlay.UnclassifiedCount,
                        BackingRows = bakedEntries.Count(x => x.EffectiveCategory is "General" or "Special")
                    },
                    Sources = result.SourceHashes
                }, new JsonSerializerOptions { WriteIndented = true }));
                Shutdown(0); return;
            }
            var paths = new PortablePaths(AppContext.BaseDirectory);
            ICatalog catalog; string? warning = null;
            try { catalog = CatalogDatabase.Open(paths.Catalog); }
            catch (FileNotFoundException ex) { catalog = new Catalog([]); warning = ex.Message; }
            SpecialBrowseV2Index? specialBrowse = null;
            if (warning == null)
            {
                try { specialBrowse = SpecialBrowseV2Overlay.FromCatalog(catalog); }
                catch (InvalidDataException ex) { warning = ex.Message; }
            }
            var vm = new MainViewModel(catalog, new UserStateStore(paths.User), new ClipboardService(), GeneralBrowseProvider.FromCatalog(catalog), specialBrowse: specialBrowse);
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
