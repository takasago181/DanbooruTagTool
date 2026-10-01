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
    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        try
        {
            if (e.Args.FirstOrDefault() == "--validate-library")
            {
                if (e.Args.Length != 2) throw new ArgumentException("--validate-library <new-empty-output-directory>");
                ShutdownMode = ShutdownMode.OnExplicitShutdown;
                await GenerationLibraryValidation.RunAsync(e.Args[1]);
                Shutdown(0); return;
            }
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
                var issue132Entries = Issue132RouteOverlay.Bake(new Catalog(unifiedBrowseEntries));
                var issue118Entries = Issue118SexualIntentV2Overlay.Bake(new Catalog(issue132Entries), e.Args[2], result.SourceHashes);
                var bakedEntries = Issue199GeneralFacetOverlay.Bake(new Catalog(issue118Entries));
                result.SourceHashes[Issue199GeneralFacetOverlay.RelativePath] = Issue199GeneralFacetOverlay.ExpectedSha256;
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
                        Identities = Issue118SexualIntentV2Overlay.IdentityCount,
                        Sexual = Issue118SexualIntentV2Overlay.SexualCount,
                        Contextual = Issue118SexualIntentV2Overlay.ContextualCount,
                        NonSexual = Issue118SexualIntentV2Overlay.NonSexualCount,
                        Unclassified = Issue118SexualIntentV2Overlay.UnclassifiedCount,
                        BackingRows = bakedEntries.Count(x => x.EffectiveCategory is "General" or "Special")
                    },
                    UnifiedGeneralFacets = new
                    {
                        Identities = Issue199GeneralFacetOverlay.IdentityCount,
                        Assignments = Issue199GeneralFacetOverlay.AssignmentCount,
                        BodyAssignments = Issue199GeneralFacetOverlay.BodyAssignmentCount,
                        ThemeAssignments = Issue199GeneralFacetOverlay.ThemeAssignmentCount
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
