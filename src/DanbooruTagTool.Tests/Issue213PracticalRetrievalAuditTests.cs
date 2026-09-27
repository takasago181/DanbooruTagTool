using System.IO;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue213PracticalRetrievalAuditTests(ITestOutputHelper output)
{
    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNameCaseInsensitive = true, WriteIndented = true };

    [Fact]
    public void EvaluateIssue213ScenariosAgainstProductionSearchAndBrowse()
    {
        var catalogPath = Environment.GetEnvironmentVariable("DTT_ISSUE213_CATALOG")
            ?? throw new InvalidOperationException("Set DTT_ISSUE213_CATALOG to the read-only production catalog.db path.");
        var scenarioPath = Environment.GetEnvironmentVariable("DTT_ISSUE213_SCENARIOS")
            ?? throw new InvalidOperationException("Set DTT_ISSUE213_SCENARIOS to scenarios.json.");
        var reportPath = Environment.GetEnvironmentVariable("DTT_ISSUE213_REPORT")
            ?? throw new InvalidOperationException("Set DTT_ISSUE213_REPORT to an output path.");

        var catalog = Assert.IsAssignableFrom<IRuntimeCatalogQuery>(CatalogDatabase.Open(catalogPath));
        var browse = new UnifiedBrowseIndex(catalog);
        var scenarios = JsonSerializer.Deserialize<Scenario[]>(File.ReadAllText(scenarioPath), JsonOptions)!;
        Assert.True(scenarios.Length >= 180);
        Assert.True(scenarios.Count(scenario => scenario.Sexual) >= 100);
        Assert.Equal(scenarios.Length, scenarios.Select(scenario => scenario.Id).Distinct(StringComparer.Ordinal).Count());

        var rows = scenarios.Select(scenario => Evaluate(scenario, catalog, browse)).ToArray();
        var smokeScenarios = scenarios.Where(scenario => scenario.Sexual).GroupBy(scenario => scenario.ScenarioClass, StringComparer.Ordinal)
            .Select(group => group.First()).Concat(scenarios.Where(scenario => !scenario.Sexual).Where(scenario =>
                scenario.ScenarioClass is "clothing" or "color_pattern" or "pose" or "composition" or "object" or "scene" or "living"))
            .Take(17).ToArray();
        var viewModelSmoke = smokeScenarios.Select(scenario => ValidateViewModel(scenario, catalog, browse)).ToArray();
        var themeAndViewModel = ValidateThemeAndViewModel(catalog);
        var summary = new
        {
            CatalogPath = Path.GetFullPath(catalogPath),
            CatalogEntries = catalog.Entries.Count,
            ViewModelSmoke = new { Count = viewModelSmoke.Length, Passed = viewModelSmoke.Count(row => row.Passed), Cases = viewModelSmoke },
            ThemeAndViewModel = themeAndViewModel,
            Scenarios = rows,
            Overall = Summarize(rows),
            Sexual = Summarize(rows.Where(row => row.Sexual).ToArray()),
            General = Summarize(rows.Where(row => !row.Sexual).ToArray()),
            ConstraintProbes = ConstraintProbes(browse),
            BySexualFamily = rows.Where(row => row.Sexual).GroupBy(row => row.ScenarioClass, StringComparer.Ordinal)
                .OrderBy(group => group.Key, StringComparer.Ordinal)
                .Select(group => new { Family = group.Key, Count = group.Count(), Summary = Summarize(group.ToArray()) }).ToArray(),
            ByTargetCatalogCategory = rows.GroupBy(row => row.TargetCatalogCategory, StringComparer.Ordinal)
                .OrderBy(group => group.Key, StringComparer.Ordinal)
                .Select(group => new { Category = group.Key, Count = group.Count(), Summary = Summarize(group.ToArray()) }).ToArray(),
            TopIssues = rows.Where(row => row.Status is "BURIED" or "NOISY" or "MISLEADING" or "DEAD_END")
                .SelectMany(row => row.RootCauses.Select(cause => new { Row = row, Cause = cause }))
                .GroupBy(item => new { item.Cause, item.Row.ScenarioClass, item.Row.Sexual })
                .Select(group => new
                {
                    RootCause = group.Key.Cause,
                    Family = group.Key.ScenarioClass,
                    Sexual = group.Key.Sexual,
                    Frequency = group.Count(),
                    ScenarioIds = group.Select(item => item.Row.Id).Order(StringComparer.Ordinal).ToArray(),
                    ExampleTargets = group.SelectMany(item => item.Row.Expected).Distinct(StringComparer.Ordinal).Take(5).ToArray()
                })
                .OrderByDescending(item => item.Frequency).ThenBy(item => item.RootCause, StringComparer.Ordinal)
                .Take(20).ToArray()
        };

        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(reportPath))!);
        File.WriteAllText(reportPath, JsonSerializer.Serialize(summary, JsonOptions));
        output.WriteLine($"catalog={catalog.Entries.Count}; scenarios={rows.Length}; sexual={rows.Count(row => row.Sexual)}");
        output.WriteLine($"DictionaryWorkspaceViewModel smoke={viewModelSmoke.Count(row => row.Passed)}/{viewModelSmoke.Length}");
        output.WriteLine(JsonSerializer.Serialize(new { summary.Overall, summary.Sexual, summary.General, summary.BySexualFamily, summary.TopIssues }, JsonOptions));
        output.WriteLine($"report={Path.GetFullPath(reportPath)}");
    }

    private static ViewModelSmokeRow ValidateViewModel(Scenario scenario, IRuntimeCatalogQuery catalog, UnifiedBrowseIndex index)
    {
        var vm = new DictionaryWorkspaceViewModel(catalog, new PromptWorkspace(new PromptParser(catalog)),
            new PendingGeneralBrowseProvider(), () => { }, () => true);
        vm.Query = scenario.Query;
        vm.RefreshResults();
        var search = vm.Results.Select(row => row.Entry.Canonical ?? row.Entry.Id).ToArray();
        vm.Query = "";
        vm.RefreshResults();
        if (scenario.ContentIntent != "All") vm.SetContentIntent(ParseContent(scenario.ContentIntent));
        if (scenario.Route.Length > 0) vm.SetPrimaryRoute(scenario.Route);
        if (scenario.Local.Length > 0) vm.SetLocalSubroute(scenario.Local);
        if (scenario.BodySite.Length > 0) vm.ToggleBodySite(scenario.BodySite);
        if (scenario.Theme.Length > 0) vm.ToggleTheme(scenario.Theme);
        if (scenario.DeepOnly) vm.ToggleDeepOnly();
        var browseOnly = vm.Results.Select(row => row.Entry.Canonical ?? row.Entry.Id).ToArray();
        vm.Query = scenario.Query;
        vm.RefreshResults();
        var combined = vm.Results.Select(row => row.Entry.Canonical ?? row.Entry.Id).ToArray();

        var expectedSearch = catalog.Search(scenario.Query).Where(hit => hit.Entry.EffectiveCategory != "Artist")
            .Select(hit => hit.Entry.Canonical ?? hit.Entry.Id).ToArray();
        var state = State(scenario);
        var expectedBrowse = index.Browse(state).OrderByDescending(entry => entry.Usage)
            .Select(entry => entry.Canonical ?? entry.Id).ToArray();
        var expectedCombined = index.FilterSearchHits(catalog.Search(scenario.Query), state)
            .Select(hit => hit.Entry.Canonical ?? hit.Entry.Id).ToArray();
        var passed = search.SequenceEqual(expectedSearch, StringComparer.Ordinal)
            && browseOnly.SequenceEqual(expectedBrowse, StringComparer.Ordinal)
            && combined.SequenceEqual(expectedCombined, StringComparer.Ordinal);
        return new(scenario.Id, passed, search.Length, browseOnly.Length, combined.Length);
    }

    private static object ValidateThemeAndViewModel(IRuntimeCatalogQuery catalog)
    {
        var vm = new DictionaryWorkspaceViewModel(catalog, new PromptWorkspace(new PromptParser(catalog)),
            new PendingGeneralBrowseProvider(), () => { }, () => true);
        vm.SetContentIntent(ContentIntentFilter.Sexual);
        vm.ToggleTheme("BDSM_RESTRAINT");
        var oneThemeCount = vm.Results.Count;
        var oneTheme = vm.ThemeIds.Order(StringComparer.Ordinal).ToArray();
        vm.ToggleTheme("REPRO_PREGNANCY_LACTATION");
        return new
        {
            OneThemeCount = oneThemeCount,
            OneThemeSelection = oneTheme,
            AfterSecondThemeCount = vm.Results.Count,
            AfterSecondThemeSelection = vm.ThemeIds.Order(StringComparer.Ordinal).ToArray(),
            SecondThemeRetainedFirst = vm.ThemeIds.Contains("BDSM_RESTRAINT")
        };
    }

    private static EvaluationRow Evaluate(Scenario scenario, IRuntimeCatalogQuery catalog, UnifiedBrowseIndex browse)
    {
        var state = State(scenario);
        var searchHits = catalog.Search(scenario.Query);
        var searchOnly = searchHits.Where(hit => hit.Entry.EffectiveCategory != "Artist").Select(hit => hit.Entry).ToArray();
        var browseOnly = browse.Browse(state).OrderByDescending(entry => entry.Usage).ToArray();
        var combinedHits = browse.FilterSearchHits(searchHits, state);
        var combined = combinedHits.Select(hit => hit.Entry).ToArray();
        var targets = scenario.Expected.Concat(scenario.AcceptableAlternatives).Distinct(StringComparer.Ordinal).ToArray();
        var searchRank = BestRank(searchOnly, targets);
        var browseRank = BestRank(browseOnly, targets);
        var combinedRank = BestRank(combined, targets);
        var bodyOnly = scenario.BodySite.Length == 0 ? [] : browse.Browse(UnifiedBrowseState.Neutral with
        {
            BodySiteIds = new HashSet<string>([scenario.BodySite], StringComparer.Ordinal),
            ContentIntent = ParseContent(scenario.ContentIntent)
        }).OrderByDescending(entry => entry.Usage).ToArray();
        var routeOnlyState = UnifiedBrowseState.Neutral with { ContentIntent = ParseContent(scenario.ContentIntent) };
        if (scenario.Route.Length > 0) routeOnlyState = routeOnlyState.WithPrimary(scenario.Route);
        var routeOnly = browse.Browse(routeOnlyState).OrderByDescending(entry => entry.Usage).ToArray();
        var broadIntent = browse.Browse(state with { ContentIntent = ContentIntentFilter.All }).OrderByDescending(entry => entry.Usage).ToArray();
        var deepOff = scenario.DeepOnly ? browse.Browse(state with { DeepOnly = false }).OrderByDescending(entry => entry.Usage).ToArray() : [];
        var bodyOnlyRank = scenario.BodySite.Length == 0 ? null : BestRank(bodyOnly, targets);
        var routeOnlyRank = scenario.Route.Length == 0 ? null : BestRank(routeOnly, targets);
        var broadIntentRank = BestRank(broadIntent, targets);
        var canonicalEntry = scenario.Expected.Select(catalog.Resolve).FirstOrDefault(entry => entry is not null);
        var japaneseLabel = canonicalEntry?.Japanese ?? "";
        var targetCategory = canonicalEntry?.EffectiveCategory ?? "MISSING";
        var labelRank = japaneseLabel.Length == 0 ? null : BestRank(catalog.Search(japaneseLabel)
            .Where(hit => hit.Entry.EffectiveCategory != "Artist").Select(hit => hit.Entry).ToArray(), targets);
        var paths = new[]
        {
            new RetrievalPath("A_SEARCH_ONLY", searchOnly, searchRank, 1, 1),
            new RetrievalPath("B_BROWSE_ONLY", browseOnly, browseRank, FilterSteps(scenario), FilterSteps(scenario)),
            new RetrievalPath("C_SEARCH_AND_BROWSE", combined, combinedRank, 1 + FilterSteps(scenario), FilterSteps(scenario))
        }.Where(path => path.Rank is not null).OrderBy(path => path.Cost).ThenBy(path => path.Rank).ThenBy(path => path.Mode, StringComparer.Ordinal).ToArray();
        var bestPath = paths.FirstOrDefault();
        var accepted = targets.ToHashSet(StringComparer.Ordinal);
        var bestResults = bestPath?.Results ?? combined;
        var distractors = bestResults.Take(20).Where(entry => entry.Canonical is null || !accepted.Contains(entry.Canonical))
            .Select(entry => new { Canonical = entry.Canonical ?? entry.Id, entry.Japanese, entry.Usage }).ToArray();
        var causes = RootCauses(scenario, catalog, browse, searchOnly, browseOnly, combined, searchRank, labelRank, browseRank, combinedRank);
        var bestCost = bestPath?.Cost ?? 1 + FilterSteps(scenario);
        var filterMisleads = bestPath is null && browseRank is null
            && (bodyOnlyRank is not null || routeOnlyRank is not null || broadIntentRank is not null);
        var status = filterMisleads ? "MISLEADING" : Status(bestPath?.Results.Count ?? combined.Length, bestPath?.Rank, distractors.Length, bestCost);
        return new(
            scenario.Id, scenario.ScenarioClass, scenario.Sexual, scenario.Intent, scenario.Query,
            scenario.Expected, scenario.AcceptableAlternatives, scenario.Route, scenario.Local,
            scenario.BodySite, scenario.Theme, scenario.ContentIntent, scenario.DeepOnly, targetCategory,
            bodyOnly.Length, bodyOnlyRank,
            routeOnly.Length, routeOnlyRank,
            broadIntent.Length, broadIntentRank,
            deepOff.Length, scenario.DeepOnly ? BestRank(deepOff, targets) : null,
            searchOnly.Length, searchRank, searchRank is > 0 and <= 5, searchRank is > 0 and <= 10, searchRank is > 0 and <= 20,
            browseOnly.Length, browseRank, browseRank is > 0 and <= 5, browseRank is > 0 and <= 10, browseRank is > 0 and <= 20,
            japaneseLabel, labelRank,
            combined.Length, combinedRank, combinedRank is > 0 and <= 5, combinedRank is > 0 and <= 10, combinedRank is > 0 and <= 20,
            bestPath?.Mode ?? "NONE", bestPath?.Results.Count ?? combined.Length, bestPath?.Rank,
            bestPath?.Rank is > 0 and <= 5, bestPath?.Rank is > 0 and <= 10, bestPath?.Rank is > 0 and <= 20,
            bestPath is not null, bestCost, bestPath?.KnowledgeSteps ?? FilterSteps(scenario), 1 + FilterSteps(scenario), bestPath is null,
            distractors.Length, distractors, causes, status);
    }

    private static UnifiedBrowseState State(Scenario scenario)
    {
        var state = UnifiedBrowseState.Neutral with { ContentIntent = ParseContent(scenario.ContentIntent) };
        if (scenario.Route.Length > 0) state = state.WithPrimary(scenario.Route);
        if (scenario.Local.Length > 0) state = state.WithLocal(scenario.Local);
        if (scenario.BodySite.Length > 0) state = state.ToggleBodySite(scenario.BodySite);
        if (scenario.Theme.Length > 0) state = state.ToggleTheme(scenario.Theme);
        if (scenario.DeepOnly) state = state with { DeepOnly = true };
        return state;
    }

    private static object[] ConstraintProbes(UnifiedBrowseIndex browse)
    {
        var sexual = UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual };
        var twoThemes = new HashSet<string>(["BDSM_RESTRAINT", "REPRO_PREGNANCY_LACTATION"], StringComparer.Ordinal);
        var cases = new (string Name, UnifiedBrowseState State)[]
        {
            ("sexual-neutral", sexual),
            ("sexual-deep-only", sexual with { DeepOnly = true }),
            ("sexual-body-breast", sexual.ToggleBodySite("BREAST_NIPPLE")),
            ("sexual-action-and-breast", sexual.WithPrimary("ACTION_CONTACT").ToggleBodySite("BREAST_NIPPLE")),
            ("sexual-body-mouth", sexual.ToggleBodySite("MOUTH_ORAL")),
            ("sexual-action-and-mouth", sexual.WithPrimary("ACTION_CONTACT").ToggleBodySite("MOUTH_ORAL")),
            ("sexual-theme-bdsm", sexual.ToggleTheme("BDSM_RESTRAINT")),
            ("sexual-theme-reproduction", sexual.ToggleTheme("REPRO_PREGNANCY_LACTATION")),
            ("sexual-theme-AND-bdsm-reproduction", sexual with { ThemeIds = twoThemes }),
            ("sexual-breast-and-theme-AND", sexual with { BodySiteIds = new HashSet<string>(["BREAST_NIPPLE"], StringComparer.Ordinal), ThemeIds = twoThemes }),
            ("general-purpose-breast", (UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.GeneralPurpose }).ToggleBodySite("BREAST_NIPPLE")),
            ("all-breast", UnifiedBrowseState.Neutral.ToggleBodySite("BREAST_NIPPLE"))
        };
        return cases.Select(item =>
        {
            var results = browse.Browse(item.State).OrderByDescending(entry => entry.Usage).ToArray();
            return (object)new
            {
                item.Name,
                item.State.PrimaryRouteId,
                BodySiteIds = item.State.BodySiteIds.Order(StringComparer.Ordinal).ToArray(),
                ThemeIds = item.State.ThemeIds.Order(StringComparer.Ordinal).ToArray(),
                item.State.DeepOnly,
                item.State.ContentIntent,
                ResultCount = results.Length,
                Top10 = results.Take(10).Select(entry => new { entry.Canonical, entry.Japanese, entry.EffectiveCategory, entry.Usage }).ToArray()
            };
        }).ToArray();
    }

    private static ContentIntentFilter ParseContent(string content) => content switch
    {
        "Sexual" => ContentIntentFilter.Sexual,
        "GeneralPurpose" => ContentIntentFilter.GeneralPurpose,
        _ => ContentIntentFilter.All
    };

    private static int FilterSteps(Scenario scenario) =>
        (scenario.Route.Length > 0 ? 1 : 0) + (scenario.Local.Length > 0 ? 1 : 0) +
        (scenario.BodySite.Length > 0 ? 1 : 0) + (scenario.Theme.Length > 0 ? 1 : 0) +
        (scenario.ContentIntent != "All" ? 1 : 0) + (scenario.DeepOnly ? 1 : 0);

    private static int? BestRank(IReadOnlyList<CatalogEntry> entries, IReadOnlyList<string> targets)
    {
        var accepted = targets.ToHashSet(StringComparer.Ordinal);
        for (var i = 0; i < entries.Count; i++)
            if (entries[i].Canonical is { } canonical && accepted.Contains(canonical)) return i + 1;
        return null;
    }

    private static string Status(int count, int? rank, int noise, int cost)
    {
        if (count == 0) return "DEAD_END";
        if (rank is null) return "DEAD_END";
        if (rank > 20) return "BURIED";
        if (rank <= 20 && count > 100 && noise >= 15) return "NOISY";
        if (rank <= 5 && cost <= 5) return "GOOD";
        return "DISCOVERABLE";
    }

    private static string[] RootCauses(Scenario scenario, IRuntimeCatalogQuery catalog, UnifiedBrowseIndex browse,
        IReadOnlyList<CatalogEntry> search, IReadOnlyList<CatalogEntry> browseResults,
        IReadOnlyList<CatalogEntry> combined, int? searchRank, int? labelRank, int? browseRank, int? combinedRank)
    {
        var causes = new HashSet<string>(StringComparer.Ordinal);
        var expectedEntries = scenario.Expected.Concat(scenario.AcceptableAlternatives).Distinct(StringComparer.Ordinal)
            .Select(catalog.Resolve).Where(entry => entry is not null).Cast<CatalogEntry>().ToArray();
        if (searchRank is null)
            causes.Add(labelRank is not null ? "SEARCH_SYNONYM" : expectedEntries.Any(entry => !string.IsNullOrWhiteSpace(entry.Japanese)) ? "SEARCH_SYNONYM" : "LABEL_DESCRIPTION");
        else if (searchRank > 20)
        {
            var target = scenario.Expected.FirstOrDefault();
            var hit = target is null ? null : catalog.Search(scenario.Query).FirstOrDefault(item => item.Entry.Canonical == target);
            causes.Add(hit is not null && catalog.Search(scenario.Query).Count(item => item.Rank == hit.Rank) > 20 ? "USAGE_SORT" : "SEARCH_RANKING");
        }

        if (browseRank is null)
        {
            foreach (var target in expectedEntries)
            {
                var identity = browse.Get(target);
                if (identity is null || !identity.BrowseableDiscovery) { causes.Add("UI_ONLY"); continue; }
                if (scenario.Route.Length > 0 && !identity.RouteIds.Contains(scenario.Route)) causes.Add("ROUTE");
                if (scenario.Local.Length > 0 && !identity.LocalSubrouteIds.Contains(scenario.Local)) causes.Add("LOCAL_REFINEMENT");
                if (scenario.BodySite.Length > 0 && !identity.BodySiteIds.Contains(scenario.BodySite)) causes.Add("BODY_FACET");
                if (scenario.Theme.Length > 0 && !identity.ThemeIds.Contains(scenario.Theme)) causes.Add("THEME_FACET");
                if (scenario.DeepOnly && !identity.DeepDiscovery) causes.Add("INTERACTION");
                var expectedIntent = ParseContent(scenario.ContentIntent);
                if (expectedIntent == ContentIntentFilter.Sexual && identity.SexualIntent is not (SexualIntentClass.Sexual or SexualIntentClass.Contextual) ||
                    expectedIntent == ContentIntentFilter.GeneralPurpose && identity.SexualIntent is SexualIntentClass.Sexual)
                    causes.Add("CONTENT_INTENT");
            }
        }
        else if (browseRank > 20)
            causes.Add("USAGE_SORT");
        if (combinedRank is null && searchRank is not null) causes.Add("INTERACTION");
        if (causes.Count == 0) causes.Add("NO_CHANGE");
        return causes.Order(StringComparer.Ordinal).ToArray();
    }

    private static object Summarize(IReadOnlyList<EvaluationRow> rows)
    {
        var statuses = new[] { "GOOD", "DISCOVERABLE", "BURIED", "NOISY", "MISLEADING", "DEAD_END" }
            .ToDictionary(status => status, status => rows.Count(row => row.Status == status), StringComparer.Ordinal);
        var found = rows.Where(row => row.TargetFound).ToArray();
        return new
        {
            Total = rows.Count,
            Sexual = rows.Count(row => row.Sexual),
            General = rows.Count(row => !row.Sexual),
            Statuses = statuses,
            MedianInteractionCost = Median(rows.Select(row => row.InteractionCost)),
            MedianClassificationKnowledgeSteps = Median(rows.Select(row => row.ClassificationKnowledgeSteps)),
            Top5Rate = Percent(rows.Count(row => row.Top5), rows.Count),
            Top10Rate = Percent(rows.Count(row => row.Top10), rows.Count),
            Top20Rate = Percent(rows.Count(row => row.Top20), rows.Count),
            TargetFoundRate = Percent(found.Length, rows.Count),
            SearchOnlyTop5Rate = Percent(rows.Count(row => row.SearchOnlyTop5), rows.Count),
            BrowseOnlyTop5Rate = Percent(rows.Count(row => row.BrowseOnlyTop5), rows.Count),
            CombinedTop5Rate = Percent(rows.Count(row => row.CombinedTop5), rows.Count),
            SearchOnlyTargetFoundRate = Percent(rows.Count(row => row.SearchOnlyBestRank is not null), rows.Count),
            BrowseOnlyTargetFoundRate = Percent(rows.Count(row => row.BrowseOnlyBestRank is not null), rows.Count),
            CombinedTargetFoundRate = Percent(rows.Count(row => row.CombinedBestRank is not null), rows.Count),
            ComplexCount = rows.Count(row => row.Sexual && row.Route.Length > 0 && (row.BodySite.Length > 0 || row.Theme.Length > 0))
        };
    }

    private static double? Median(IEnumerable<int> source)
    {
        var values = source.Order().ToArray();
        if (values.Length == 0) return null;
        return values.Length % 2 == 1 ? values[values.Length / 2] : (values[values.Length / 2 - 1] + values[values.Length / 2]) / 2.0;
    }

    private static double Percent(int numerator, int denominator) => denominator == 0 ? 0 : Math.Round(100.0 * numerator / denominator, 2);

    private sealed record Scenario(
        string Id, string ScenarioClass, bool Sexual, string Intent, string Query,
        string[] Expected, string[] AcceptableAlternatives, string Route, string Local,
        string BodySite, string Theme, string ContentIntent, bool DeepOnly);

    private sealed record RetrievalPath(string Mode, IReadOnlyList<CatalogEntry> Results, int? Rank, int Cost, int KnowledgeSteps);

    private sealed record ViewModelSmokeRow(string ScenarioId, bool Passed, int SearchCount, int BrowseCount, int CombinedCount);

    private sealed record EvaluationRow(
        string Id, string ScenarioClass, bool Sexual, string Intent, string Query,
        string[] Expected, string[] AcceptableAlternatives, string Route, string Local,
        string BodySite, string Theme, string ContentIntent, bool DeepOnly,
        string TargetCatalogCategory, int BodySiteOnlyResultCount, int? BodySiteOnlyBestRank,
        int RouteOnlyResultCount, int? RouteOnlyBestRank, int AllIntentBrowseResultCount, int? AllIntentBrowseBestRank,
        int DeepOnlyOffResultCount, int? DeepOnlyOffBestRank,
        int SearchOnlyResultCount, int? SearchOnlyBestRank, bool SearchOnlyTop5, bool SearchOnlyTop10, bool SearchOnlyTop20,
        int BrowseOnlyResultCount, int? BrowseOnlyBestRank, bool BrowseOnlyTop5, bool BrowseOnlyTop10, bool BrowseOnlyTop20,
        string JapaneseLabel, int? JapaneseLabelSearchRank,
        int ResultCount, int? CombinedBestRank, bool CombinedTop5, bool CombinedTop10, bool CombinedTop20,
        string BestMode, int BestModeResultCount, int? BestRank, bool Top5, bool Top10, bool Top20, bool TargetFound,
        int InteractionCost, int ClassificationKnowledgeSteps, int CombinedInteractionCost, bool DeadEnd,
        int NonTargetRowsInTop20, object[] ConfusingSimilarTags, string[] RootCauses, string Status);
}
