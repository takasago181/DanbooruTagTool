using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.App;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using System.Reflection;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

[Collection("WPF composition")]
public sealed class Issue204UnifiedRefreshTests
{
    private sealed class MemoryStore(UserState? initial = null) : IUserStateStore
    {
        public UserState? State { get; private set; } = initial;
        public UserState? Load() => State;
        public void Save(UserState state) => State = state;
    }

    private sealed class Clipboard : IClipboardService
    {
        public string Read() => "";
        public void Write(string text) { }
    }

    private static CatalogEntry Entry(string id, string canonical, string route, params string[] bodies) =>
        new(id, canonical, canonical, canonical, false, 100, [], [], [],
            BrowseClassification: BrowseClassificationStatus.Proposed)
        {
            UnifiedBrowseRouteIds = [route],
            UnifiedBrowseFacets = new(bodies, []),
            SexualIntent = SexualIntentClass.NonSexual
        };

    private static Catalog FixtureCatalog()
    {
        CatalogEntry General(string id, string canonical, string local, string[] bodies, string[] themes, SexualIntentClass intent)
            => Entry(id, canonical, "BODY_SITE", bodies) with
            {
                Paths = [new("BODY_PART", "身体", local, local == "BREAST" ? "胸" : local == "MOUTH" ? "口" : "全身")],
                UnifiedBrowseRouteIds = ["BODY_SITE", "ACTION_CONTACT", "COMPOSITION_CAMERA"],
                UnifiedBrowseFacets = new(bodies, themes),
                SexualIntent = intent
            };

        var entries = new List<CatalogEntry>
        {
            General("g1", "breast_tag", "BREAST", ["BREAST_NIPPLE", "MOUTH_ORAL"], ["BDSM_RESTRAINT", "REPRO_PREGNANCY_LACTATION"], SexualIntentClass.Sexual),
            General("g2", "mouth_tag", "MOUTH", ["MOUTH_ORAL"], ["BDSM_RESTRAINT"], SexualIntentClass.Contextual),
            General("g3", "anal_tag", "ANAL", ["BUTTOCK_ANAL"], ["REPRO_PREGNANCY_LACTATION"], SexualIntentClass.NonSexual),
            General("g4", "style_tag", "STYLE", [], [], SexualIntentClass.NonSexual) with { UnifiedBrowseRouteIds = ["STYLE_PROCESSING"], Paths = [] }
        };
        entries.AddRange(new[]
        {
            Special("s1", "deep_tag", ["BREAST_NIPPLE", "MOUTH_ORAL"], ["BDSM_RESTRAINT"]),
            Special("s2", "deep_breast", ["BREAST_NIPPLE"], []),
            Special("s3", "deep_mouth", ["MOUTH_ORAL"], [])
        });
        return new(entries);
    }

    private static CatalogEntry Special(string id, string canonical, string[] bodies, string[] themes)
        => new(id, canonical, canonical, canonical, true, 50, [], [], [],
            SpecialBrowseV2: new("BODY_STATE", bodies, themes, SpecialBrowseV2Status.HumanResolved))
        {
            UnifiedBrowseRouteIds = ["BODY_SITE", "ACTION_CONTACT", "COMPOSITION_CAMERA"],
            SexualIntent = SexualIntentClass.Sexual
        };

    private static DictionaryWorkspaceViewModel Workspace(Catalog? catalog = null, Action? persist = null)
    {
        catalog ??= FixtureCatalog();
        return new(catalog, new PromptWorkspace(new PromptParser(catalog)), new PendingGeneralBrowseProvider(), persist ?? (() => { }), () => true);
    }

    private static string[] Snapshot(DictionaryWorkspaceViewModel vm)
        => vm.Results.Select(row => row.Entry.Canonical!).Order(StringComparer.Ordinal).ToArray();

    public sealed class ProductionSmoke(ITestOutputHelper output)
    {
        [ProductionFact]
        public void Production_view_model_refreshes_route_sexual_body_deep_removals_without_persisted_user_data()
        {
            var path = Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!;
            var catalog = CatalogDatabase.Open(path);
            var query = RuntimeCatalogIndex.Create(catalog);
            var state = UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual };
            var index = new UnifiedBrowseIndex(query, SpecialBrowseV2Overlay.FromCatalog(catalog));
            var bodyIds = SpecialBrowseV2Taxonomy.BodySites.Select(facet => facet.Id).ToArray();
            (string Route, string First, string Second, int Pair, int One, int Deep)? pair = null;
            foreach (var route in UnifiedBrowseTaxonomy.Routes.Select(item => item.Id))
            {
                foreach (var first in bodyIds)
                {
                    foreach (var second in bodyIds.Where(id => id != first))
                    {
                        var routed = state with { PrimaryRouteId = route };
                        var combined = routed.ToggleBodySite(first).ToggleBodySite(second);
                        var pairCount = index.Count(combined with { DeepOnly = true });
                        var oneCount = index.Count((routed.ToggleBodySite(second)) with { DeepOnly = true });
                        var deepCount = index.Count(routed with { DeepOnly = true });
                        if (pairCount > 0 && pairCount < oneCount && oneCount < deepCount)
                        {
                            pair = (route, first, second, pairCount, oneCount, deepCount);
                            break;
                        }
                    }
                    if (pair is not null) break;
                }
                if (pair is not null) break;
            }
            Assert.NotNull(pair);
            var chosen = pair.Value;
            output.WriteLine($"{chosen.Route}/Sexual body AND pair {chosen.First}+{chosen.Second}: {chosen.Pair} -> {chosen.One} -> {chosen.Deep}");

            var store = new MemoryStore(); // disposable in-memory UserState, never the installed UserData database.
            var app = new MainViewModel(catalog, store, new Clipboard());
            app.Dictionary.SetPrimaryRoute(chosen.Route);
            app.Dictionary.SetContentIntent(ContentIntentFilter.Sexual);
            var chosenState = state with { PrimaryRouteId = chosen.Route };
            var initial = app.Dictionary.Results.Count;
            Assert.Equal(index.Count(chosenState), initial);
            app.Dictionary.ToggleBodySite(chosen.First);
            app.Dictionary.ToggleBodySite(chosen.Second);
            app.Dictionary.ToggleDeepOnly();
            Assert.Equal(chosen.Pair, app.Dictionary.Results.Count);
            app.Dictionary.RemoveUnifiedCondition("body:" + chosen.First);
            Assert.Equal(chosen.One, app.Dictionary.Results.Count);
            app.Dictionary.RemoveUnifiedCondition("body:" + chosen.Second);
            Assert.Equal(chosen.Deep, app.Dictionary.Results.Count);
            app.Dictionary.ToggleDeepOnly();
            Assert.Equal(initial, app.Dictionary.Results.Count);
            app.Dictionary.RemoveUnifiedCondition("content-intent");
            Assert.Equal(index.Count(chosenState with { ContentIntent = ContentIntentFilter.All }), app.Dictionary.Results.Count);
            output.WriteLine($"production ViewModel smoke: {initial} -> {chosen.Pair} -> {chosen.One} -> {chosen.Deep} -> DeepOnly OFF -> Sexual All; in-memory state only");
        }
    }

    [Fact]
    public void State_notifications_observe_results_for_the_same_applied_state()
    {
        var catalog = new Catalog([
            Entry("g1", "one", "BODY_SITE", "BREAST_NIPPLE"),
            Entry("g2", "two", "BODY_SITE", "BUTTOCK_ANAL")
        ]);
        var workspace = new PromptWorkspace(new PromptParser(catalog));
        var vm = new DictionaryWorkspaceViewModel(catalog, workspace, new PendingGeneralBrowseProvider(), () => { }, () => true);
        vm.RefreshResults();
        var staleSnapshotObserved = false;
        var stateNotificationCount = 0;
        vm.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName == nameof(vm.PrimaryRouteId) && vm.PrimaryRouteId == "BODY_SITE")
            {
                stateNotificationCount++;
                if (stateNotificationCount == 1)
                    staleSnapshotObserved = vm.ResultSummary != "2件" || vm.Results.Count != 2;
            }
        };

        vm.SetPrimaryRoute("BODY_SITE");

        Assert.False(staleSnapshotObserved, "Unified state was announced before ResultSummary and result cards reflected it.");
        Assert.Equal(1, stateNotificationCount);
        Assert.Equal("2件", vm.ResultSummary);
    }

    [Fact]
    public void Primary_local_body_theme_content_and_deep_conditions_restore_the_exact_prior_result_set()
    {
        var primary = Workspace();
        primary.SetContentIntent(ContentIntentFilter.GeneralPurpose);
        var primaryA = Snapshot(primary);
        Assert.NotEmpty(primaryA);
        primary.SetPrimaryRoute("BODY_SITE");
        Assert.NotEqual(primaryA, Snapshot(primary));
        primary.RemoveUnifiedCondition("route");
        Assert.Equal(primaryA, Snapshot(primary));

        var local = Workspace();
        local.SetPrimaryRoute("BODY_SITE");
        var localA = Snapshot(local);
        local.SetLocalSubroute("BODY_PART/BREAST");
        Assert.Single(local.Results);
        Assert.Contains("分類: 身体・部位", local.ActiveUnifiedConditions.Select(condition => condition.Label));
        Assert.Contains("小分類: 胸", local.ActiveUnifiedConditions.Select(condition => condition.Label));
        local.RemoveUnifiedCondition("local");
        Assert.Equal(localA, Snapshot(local));

        var routeRemoval = Workspace();
        routeRemoval.SetPrimaryRoute("BODY_SITE");
        routeRemoval.SetLocalSubroute("BODY_PART/BREAST");
        var localOnlyResults = Snapshot(routeRemoval);
        routeRemoval.RemoveUnifiedCondition("route");
        Assert.Null(routeRemoval.PrimaryRouteId);
        Assert.Equal("BODY_PART/BREAST", routeRemoval.LocalSubrouteId);
        Assert.Contains("小分類: 胸", routeRemoval.ActiveUnifiedConditions.Select(condition => condition.Label));
        Assert.Equal(localOnlyResults, Snapshot(routeRemoval));

        var body = Workspace();
        body.SetPrimaryRoute("BODY_SITE");
        var bodyA = Snapshot(body);
        body.ToggleBodySite("BREAST_NIPPLE");
        Assert.Equal(3, body.Results.Count);
        body.RemoveUnifiedCondition("body:BREAST_NIPPLE");
        Assert.Equal(bodyA, Snapshot(body));

        var theme = Workspace();
        theme.SetPrimaryRoute("BODY_SITE");
        var themeA = Snapshot(theme);
        theme.ToggleTheme("REPRO_PREGNANCY_LACTATION");
        Assert.Equal(2, theme.Results.Count);
        theme.RemoveUnifiedCondition("theme:REPRO_PREGNANCY_LACTATION");
        Assert.Equal(themeA, Snapshot(theme));

        var content = Workspace();
        content.SetPrimaryRoute("BODY_SITE");
        var contentA = Snapshot(content);
        content.SetContentIntent(ContentIntentFilter.Sexual);
        Assert.NotEqual(contentA, Snapshot(content));
        content.RemoveUnifiedCondition("content-intent");
        Assert.Equal(contentA, Snapshot(content));

        var deep = Workspace();
        deep.SetPrimaryRoute("BODY_SITE");
        var deepA = Snapshot(deep);
        deep.ToggleDeepOnly();
        Assert.Equal(["deep_breast", "deep_mouth", "deep_tag"], Snapshot(deep));
        deep.RemoveUnifiedCondition("deep-only");
        Assert.Equal(deepA, Snapshot(deep));
    }

    [Fact]
    public void Multiple_body_and_theme_facets_keep_and_semantics_and_individual_removal_restores_prior_results()
    {
        var body = Workspace();
        body.SetPrimaryRoute("BODY_SITE");
        body.ToggleBodySite("BREAST_NIPPLE");
        var bodyA = Snapshot(body);
        Assert.Equal(["breast_tag", "deep_breast", "deep_tag"], bodyA);
        body.ToggleBodySite("MOUTH_ORAL");
        Assert.Equal(["breast_tag", "deep_tag"], Snapshot(body)); // both must match.
        Assert.Contains("すべて満たす", body.ActiveUnifiedConditionSummary);
        body.RemoveUnifiedCondition("body:MOUTH_ORAL");
        Assert.Equal(bodyA, Snapshot(body));

        var theme = Workspace();
        theme.SetPrimaryRoute("BODY_SITE");
        theme.ToggleTheme("BDSM_RESTRAINT");
        var themeA = Snapshot(theme);
        Assert.Equal(["breast_tag", "deep_tag", "mouth_tag"], themeA);
        theme.ToggleTheme("REPRO_PREGNANCY_LACTATION");
        Assert.Equal(["breast_tag"], Snapshot(theme));
        Assert.Contains("すべて満たす", theme.ActiveUnifiedConditionSummary);
        theme.RemoveUnifiedCondition("theme:REPRO_PREGNANCY_LACTATION");
        Assert.Equal(themeA, Snapshot(theme));
    }

    [Fact]
    public void Search_and_browse_facet_removal_refreshes_cards_summary_and_facet_options_synchronously()
    {
        var vm = Workspace();
        vm.SetPrimaryRoute("ACTION_CONTACT");
        vm.Query = "tag";
        vm.RefreshResults();
        var stateA = Snapshot(vm);
        var summaryA = vm.ResultSummary;
        var bodyOption = Assert.Single(vm.BodyOptions, option => option.Id == "BREAST_NIPPLE");
        var countA = bodyOption.Count;

        vm.ToggleBodySite("BREAST_NIPPLE");
        Assert.NotEqual(stateA, Snapshot(vm));
        vm.RemoveUnifiedCondition("body:BREAST_NIPPLE");
        Assert.Equal(stateA, Snapshot(vm));
        Assert.Equal(summaryA, vm.ResultSummary);
        Assert.False(bodyOption.Selected);
        Assert.Equal(countA, bodyOption.Count);

        var browse = Workspace();
        browse.SetPrimaryRoute("BODY_SITE");
        var browseA = Snapshot(browse);
        browse.ToggleTheme("BDSM_RESTRAINT");
        Assert.NotEqual(browseA, Snapshot(browse));
        browse.ToggleTheme("BDSM_RESTRAINT");
        Assert.Equal(browseA, Snapshot(browse));
    }

    [Fact]
    public void Undo_clear_all_summary_labels_and_ui_state_save_restore_are_consistent()
    {
        var persistCount = 0;
        var vm = Workspace(persist: () => persistCount++);
        vm.SetPrimaryRoute("BODY_SITE");
        vm.ToggleBodySite("BREAST_NIPPLE");
        vm.ToggleTheme("BDSM_RESTRAINT");
        vm.SetContentIntent(ContentIntentFilter.Sexual);
        vm.ToggleDeepOnly();
        Assert.Contains("分類: 身体・部位", vm.ActiveUnifiedConditions.Select(condition => condition.Label));
        Assert.Contains("部位: 乳房・乳首", vm.ActiveUnifiedConditions.Select(condition => condition.Label));
        Assert.Contains("テーマ: 拘束・BDSM", vm.ActiveUnifiedConditions.Select(condition => condition.Label));
        Assert.Contains("内容: 性的", vm.ActiveUnifiedConditions.Select(condition => condition.Label));
        Assert.Contains("深掘りのみ", vm.ActiveUnifiedConditions.Select(condition => condition.Label));
        Assert.True(persistCount >= 5);

        var beforeUndo = Snapshot(vm);
        vm.UndoUnifiedBrowse();
        Assert.False(vm.DeepOnly);
        Assert.NotEqual(beforeUndo, Snapshot(vm));

        var store = new MemoryStore();
        var catalog = FixtureCatalog();
        var app = new MainViewModel(catalog, store, new Clipboard());
        app.Dictionary.SetPrimaryRoute("BODY_SITE");
        app.Dictionary.ToggleBodySite("BREAST_NIPPLE");
        app.Dictionary.ToggleTheme("BDSM_RESTRAINT");
        app.Dictionary.SetContentIntent(ContentIntentFilter.Sexual);
        app.Dictionary.ToggleDeepOnly();
        app.Persist();
        var saved = Assert.IsType<UserState>(store.State).Ui;
        var restored = new MainViewModel(catalog, store, new Clipboard());
        Assert.Equal(saved.BrowsePrimaryRoute, restored.Dictionary.PrimaryRouteId);
        Assert.Equal(saved.BrowseBodySites, restored.Dictionary.BodySiteIds.Order(StringComparer.Ordinal));
        Assert.Equal(saved.BrowseThemes, restored.Dictionary.ThemeIds.Order(StringComparer.Ordinal));
        Assert.Equal(ContentIntentFilter.Sexual, restored.Dictionary.ContentIntent);
        Assert.True(restored.Dictionary.DeepOnly);
        Assert.Equal(vm.ActiveUnifiedConditions.Count, vm.ActiveUnifiedConditions.DistinctBy(c => c.Id).Count());

        restored.Dictionary.ClearUnifiedBrowse();
        Assert.True(restored.Dictionary.IsNeutralTags);
        Assert.Empty(restored.Dictionary.ActiveUnifiedConditions);
        Assert.Empty(restored.Dictionary.Results);
    }

    [Fact]
    public void Wpf_controls_run_the_complete_body_deep_removal_flow_and_search_facet_round_trip()
    {
        Exception? failure = null;
        var thread = new Thread(() =>
        {
            try
            {
                var catalog = FixtureCatalog();
                var vm = new MainViewModel(catalog, new MemoryStore(), new Clipboard());
                var window = new MainWindow(vm) { WindowState = WindowState.Normal, Width = 1500, Height = 950, ShowInTaskbar = false };
                window.Show();
                Pump(window.Dispatcher, 100);
                var view = (FrameworkElement)(window.GetType().GetField("DictionaryWorkspace", BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(window)
                    ?? throw new InvalidOperationException("DictionaryWorkspace view was not created."));
                view.Width = 1100;
                window.UpdateLayout();
                Pump(window.Dispatcher, 100);

                vm.Dictionary.SetPrimaryRoute("COMPOSITION_CAMERA");
                InvokeCommand(view, "性的");
                InvokeCommand(view, "乳房・乳首");
                InvokeCommand(view, "口・口内");
                InvokeCommand(view, "◆ 深掘りのみ");
                Pump(window.Dispatcher, 30);
                Assert.Single(vm.Dictionary.Results);
                AssertUiResults(view, vm);

                InvokeCommand(view, "乳房・乳首");
                Pump(window.Dispatcher, 30);
                Assert.Equal(2, vm.Dictionary.Results.Count);
                AssertUiResults(view, vm);
                InvokeCommand(view, "口・口内");
                Pump(window.Dispatcher, 30);
                Assert.Equal(3, vm.Dictionary.Results.Count);
                AssertUiResults(view, vm);

                InvokeCommand(view, "◆ 深掘りのみ");
                Assert.Equal(5, vm.Dictionary.Results.Count);
                InvokeCommand(view, "すべて", "All", vm.Dictionary.SetContentIntentCommand);
                Assert.Equal(6, vm.Dictionary.Results.Count);

                var search = GetField<TextBox>(view, "SearchBox");
                search.Text = "tag";
                Pump(window.Dispatcher, 250);
                var searchA = vm.Dictionary.Results.Count;
                InvokeCommand(view, "乳房・乳首");
                Assert.True(vm.Dictionary.Results.Count < searchA);
                AssertUiResults(view, vm);
                InvokeCommand(view, "乳房・乳首");
                Assert.Equal(searchA, vm.Dictionary.Results.Count);
                AssertUiResults(view, vm);

                window.Close();
            }
            catch (Exception ex) { failure = ex; }
        });
        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        thread.Join();
        if (failure != null) throw new Xunit.Sdk.XunitException(failure.ToString());
    }

    [Fact]
    public void Wpf_content_intent_selection_stays_exclusive_and_refinement_rows_keep_fixed_positions()
    {
        Exception? failure = null;
        var thread = new Thread(() =>
        {
            try
            {
                var vm = new MainViewModel(FixtureCatalog(), new MemoryStore(), new Clipboard());
                var window = new MainWindow(vm) { WindowState = WindowState.Normal, Width = 1500, Height = 950, ShowInTaskbar = false };
                window.Show();
                Pump(window.Dispatcher, 50);
                var view = (FrameworkElement)(window.GetType().GetField("DictionaryWorkspace", BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(window)
                    ?? throw new InvalidOperationException("DictionaryWorkspace view was not created."));
                view.Width = 1100;
                window.UpdateLayout();
                vm.Dictionary.SetPrimaryRoute("BODY_SITE");
                Pump(window.Dispatcher, 30);

                ClickContentOption(view, "一般向け");
                AssertContentSelection(view, vm, ContentIntentFilter.GeneralPurpose);

                ClickContentOption(view, "一般向け");
                AssertContentSelection(view, vm, ContentIntentFilter.GeneralPurpose);

                ClickContentOption(view, "性的");
                AssertContentSelection(view, vm, ContentIntentFilter.Sexual);
                ClickContentOption(view, "性的");
                AssertContentSelection(view, vm, ContentIntentFilter.Sexual);

                ClickContentOption(view, "一般向け");
                AssertContentSelection(view, vm, ContentIntentFilter.GeneralPurpose);
                ClickContentOption(view, "性的");
                AssertContentSelection(view, vm, ContentIntentFilter.Sexual);
                ClickContentOption(view, "すべて");
                AssertContentSelection(view, vm, ContentIntentFilter.All);

                ClickContentOption(view, "一般向け");
                AssertContentSelection(view, vm, ContentIntentFilter.GeneralPurpose);
                ClickContentOption(view, "すべて");
                AssertContentSelection(view, vm, ContentIntentFilter.All);

                window.Close();
            }
            catch (Exception ex) { failure = ex; }
        });
        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        thread.Join();
        if (failure != null) throw new Xunit.Sdk.XunitException(failure.ToString());
    }

    [Fact]
    public void Wpf_refinement_rows_do_not_move_when_active_filters_change()
    {
        Exception? failure = null;
        var thread = new Thread(() =>
        {
            try
            {
                var vm = new MainViewModel(FixtureCatalog(), new MemoryStore(), new Clipboard());
                var window = new MainWindow(vm) { WindowState = WindowState.Normal, Width = 1500, Height = 950, ShowInTaskbar = false };
                window.Show();
                Pump(window.Dispatcher, 50);
                var view = (FrameworkElement)(window.GetType().GetField("DictionaryWorkspace", BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(window)
                    ?? throw new InvalidOperationException("DictionaryWorkspace view was not created."));
                view.Width = 1100;
                window.UpdateLayout();
                vm.Dictionary.SetPrimaryRoute("BODY_SITE");
                Pump(window.Dispatcher, 30);
                var rowPositions = RefinementRowPositions(view);

                ClickContentOption(view, "性的");
                InvokeCommand(view, "乳房・乳首");
                InvokeCommand(view, "口・口内");
                InvokeCommand(view, "拘束・BDSM");
                InvokeCommand(view, "◆ 深掘りのみ");
                Pump(window.Dispatcher, 30);

                Assert.DoesNotContain(FindVisualChildren<TextBlock>(view), text => text.Text == "現在の絞り込み条件");
                AssertRefinementRowsStable(rowPositions, RefinementRowPositions(view));
                AssertUiResults(view, vm);

                InvokeCommand(view, "口・口内");
                InvokeCommand(view, "拘束・BDSM");
                InvokeCommand(view, "◆ 深掘りのみ");
                Pump(window.Dispatcher, 30);
                AssertRefinementRowsStable(rowPositions, RefinementRowPositions(view));

                window.Close();
            }
            catch (Exception ex) { failure = ex; }
        });
        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        thread.Join();
        if (failure != null) throw new Xunit.Sdk.XunitException(failure.ToString());
    }

    [Fact]
    public void Wpf_body_and_theme_chips_keep_their_slots_when_filter_counts_change()
    {
        Exception? failure = null;
        var thread = new Thread(() =>
        {
            try
            {
                var vm = new MainViewModel(FixtureCatalog(), new MemoryStore(), new Clipboard());
                var window = new MainWindow(vm) { WindowState = WindowState.Normal, Width = 1200, Height = 900, ShowInTaskbar = false };
                window.Show();
                Pump(window.Dispatcher, 50);
                var view = (FrameworkElement)(window.GetType().GetField("DictionaryWorkspace", BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(window)
                    ?? throw new InvalidOperationException("DictionaryWorkspace view was not created."));
                view.Width = 650;
                window.UpdateLayout();
                vm.Dictionary.SetPrimaryRoute("BODY_SITE");
                Pump(window.Dispatcher, 30);

                var bodySlots = FacetChipSlots(view, BrowseFacetKind.BodySite);
                var themeSlots = FacetChipSlots(view, BrowseFacetKind.Theme);
                Assert.Equal(SpecialBrowseV2Taxonomy.BodySites.Length, bodySlots.Count);
                Assert.Equal(SpecialBrowseV2Taxonomy.Themes.Length, themeSlots.Count);
                var breastChip = FacetChip(view, BrowseFacetKind.BodySite, "BREAST_NIPPLE");
                var initialFill = FacetChipFill(breastChip);

                ClickContentOption(view, "性的");
                InvokeCommand(view, "乳房・乳首");
                InvokeCommand(view, "拘束・BDSM");
                InvokeCommand(view, "◆ 深掘りのみ");
                Pump(window.Dispatcher, 30);

                AssertFacetChipSlotsStable(bodySlots, FacetChipSlots(view, BrowseFacetKind.BodySite));
                AssertFacetChipSlotsStable(themeSlots, FacetChipSlots(view, BrowseFacetKind.Theme));
                Assert.Equal(Colors.White, initialFill);
                Assert.Equal(Color.FromRgb(0x2B, 0x72, 0xB9), FacetChipFill(breastChip));

                InvokeCommand(view, "◆ 深掘りのみ");
                InvokeCommand(view, "拘束・BDSM");
                InvokeCommand(view, "乳房・乳首");
                AssertFacetChipSlotsStable(bodySlots, FacetChipSlots(view, BrowseFacetKind.BodySite));
                AssertFacetChipSlotsStable(themeSlots, FacetChipSlots(view, BrowseFacetKind.Theme));
                window.Close();
            }
            catch (Exception ex) { failure = ex; }
        });
        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        thread.Join();
        if (failure != null) throw new Xunit.Sdk.XunitException(failure.ToString());
    }

    private static void ClickContentOption(FrameworkElement root, string label)
    {
        var target = FindVisualChildren<ButtonBase>(root).FirstOrDefault(button =>
            button.Content?.ToString() == label && button.Command is not null &&
            root.DataContext is DictionaryWorkspaceViewModel dictionary &&
            ReferenceEquals(button.Command, dictionary.SetContentIntentCommand));
        Assert.NotNull(target);
        ClickButtonBase(target!);
        root.UpdateLayout();
        Pump(root.Dispatcher, 25);
    }

    private static void AssertContentSelection(FrameworkElement root, MainViewModel vm, ContentIntentFilter expected)
    {
        var dictionary = vm.Dictionary;
        Assert.Equal(expected, dictionary.ContentIntent);
        Assert.Equal(expected == ContentIntentFilter.All, dictionary.IsContentAll);
        Assert.Equal(expected == ContentIntentFilter.GeneralPurpose, dictionary.IsContentGeneralPurpose);
        Assert.Equal(expected == ContentIntentFilter.Sexual, dictionary.IsContentSexual);
        var buttons = FindVisualChildren<ToggleButton>(root)
            .Where(button => button.CommandParameter is string value &&
                (value == "All" || value == "GeneralPurpose" || value == "Sexual") &&
                ReferenceEquals(button.Command, dictionary.SetContentIntentCommand))
            .ToArray();
        Assert.Equal(3, buttons.Length);
        var selected = Assert.Single(buttons, button => button.IsChecked == true);
        Assert.Equal(expected switch
        {
            ContentIntentFilter.All => "すべて",
            ContentIntentFilter.GeneralPurpose => "一般向け",
            ContentIntentFilter.Sexual => "性的",
            _ => throw new ArgumentOutOfRangeException(nameof(expected))
        }, selected.Content?.ToString());
        AssertUiResults(root, vm);
    }

    private static double[] RefinementRowPositions(FrameworkElement root)
    {
        var labels = new[] { "分類", "部位", "テーマ", "内容" };
        return labels.Select(label =>
        {
            var text = FindVisualChildren<TextBlock>(root).FirstOrDefault(candidate => candidate.Text == label);
            Assert.NotNull(text);
            return text!.TransformToAncestor(root).Transform(new Point(0, 0)).Y;
        }).ToArray();
    }

    private static Dictionary<string, Rect> FacetChipSlots(FrameworkElement root, BrowseFacetKind kind)
    {
        var buttons = FindVisualChildren<Button>(root)
            .Where(button => button.DataContext is BrowseFacetOptionViewModel option && option.Kind == kind)
            .ToArray();
        Assert.All(buttons, button => Assert.True(button.IsVisible, $"Facet chip {((BrowseFacetOptionViewModel)button.DataContext).Id} was hidden."));
        return buttons.ToDictionary(
            button => ((BrowseFacetOptionViewModel)button.DataContext).Id,
            button => new Rect(button.TransformToAncestor(root).Transform(new Point(0, 0)), new Size(button.ActualWidth, button.ActualHeight)),
            StringComparer.Ordinal);
    }

    private static Button FacetChip(FrameworkElement root, BrowseFacetKind kind, string id)
        => FindVisualChildren<Button>(root).Single(button =>
            button.DataContext is BrowseFacetOptionViewModel option && option.Kind == kind && option.Id == id);

    private static Color FacetChipFill(Button button)
        => Assert.IsType<SolidColorBrush>(FindVisualChildren<Border>(button).First().Background).Color;

    private static void AssertFacetChipSlotsStable(IReadOnlyDictionary<string, Rect> expected, IReadOnlyDictionary<string, Rect> actual)
    {
        Assert.Equal(expected.Keys.Order(StringComparer.Ordinal), actual.Keys.Order(StringComparer.Ordinal));
        foreach (var (id, before) in expected)
        {
            var after = actual[id];
            Assert.True(Math.Abs(before.X - after.X) < 1 && Math.Abs(before.Y - after.Y) < 1,
                $"Facet chip {id} moved from ({before.X}, {before.Y}) to ({after.X}, {after.Y}) DIPs.");
            Assert.True(Math.Abs(before.Width - after.Width) < 1 && Math.Abs(before.Height - after.Height) < 1,
                $"Facet chip {id} changed size from {before.Size} to {after.Size}.");
        }
    }

    private static void AssertRefinementRowsStable(IReadOnlyList<double> expected, IReadOnlyList<double> actual)
    {
        Assert.Equal(expected.Count, actual.Count);
        for (var index = 0; index < expected.Count; index++)
            Assert.True(Math.Abs(expected[index] - actual[index]) < 1, $"Refinement row {index} moved from {expected[index]} to {actual[index]} DIPs.");
    }

    private static void InvokeCommand(FrameworkElement root, string content, string? parameterContains = null, ICommand? expectedCommand = null)
    {
        var target = FindVisualChildren<ButtonBase>(root).FirstOrDefault(button =>
            button.Content?.ToString() == content && button.Command is not null &&
            (parameterContains is null || button.CommandParameter?.ToString()?.Contains(parameterContains, StringComparison.OrdinalIgnoreCase) == true) &&
            (expectedCommand is null || ReferenceEquals(button.Command, expectedCommand)));
        Assert.NotNull(target);
        Assert.True(target!.Command!.CanExecute(target.CommandParameter));
        ClickButtonBase(target);
        root.UpdateLayout();
    }

    private static void ClickButtonBase(ButtonBase target)
    {
        var onClick = typeof(ButtonBase).GetMethod("OnClick", BindingFlags.Instance | BindingFlags.NonPublic)
            ?? throw new InvalidOperationException("WPF ButtonBase.OnClick was not found.");
        onClick.Invoke(target, null);
    }

    private static void AssertUiResults(FrameworkElement root, MainViewModel vm)
    {
        var first = GetField<ListBox>(root, "DictionaryList");
        var second = GetField<ListBox>(root, "DictionaryRightList");
        Assert.Equal(vm.Dictionary.Results.Count, first.Items.Count + second.Items.Count);
        var summary = FindVisualChildren<TextBlock>(root).Single(text =>
            text.GetBindingExpression(TextBlock.TextProperty)?.ParentBinding.Path.Path == "ResultSummary");
        Assert.Equal(vm.Dictionary.ResultSummary, summary.Text);
    }

    private static T GetField<T>(object target, string name) where T : class
        => target.GetType().GetField(name, BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(target) as T
            ?? throw new InvalidOperationException($"Field {name} was not found.");

    private static IEnumerable<T> FindVisualChildren<T>(DependencyObject parent) where T : DependencyObject
    {
        for (var index = 0; index < VisualTreeHelper.GetChildrenCount(parent); index++)
        {
            var child = VisualTreeHelper.GetChild(parent, index);
            if (child is T match) yield return match;
            foreach (var nested in FindVisualChildren<T>(child)) yield return nested;
        }
    }

    private static void Pump(Dispatcher dispatcher, int milliseconds)
    {
        var frame = new DispatcherFrame();
        var timer = new DispatcherTimer(DispatcherPriority.Background, dispatcher) { Interval = TimeSpan.FromMilliseconds(milliseconds) };
        timer.Tick += (_, _) => { timer.Stop(); frame.Continue = false; };
        timer.Start();
        Dispatcher.PushFrame(frame);
    }
}
