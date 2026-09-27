using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using System.Text.Json;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue201ScenarioFactAttribute : FactAttribute
{
    public Issue201ScenarioFactAttribute()
    {
        if (string.IsNullOrWhiteSpace(Environment.GetEnvironmentVariable("DTT_ISSUE201_SCENARIO_CATALOG")))
            Skip = "Requires an isolated production-size Issue #201 catalog path.";
    }
}

public sealed class Issue201PracticalScenarioTests(ITestOutputHelper output)
{
    [Issue201ScenarioFact]
    public void ProductionCatalogSupportsIntentFirstDiscoveryScenarios()
    {
        var catalogPath = Environment.GetEnvironmentVariable("DTT_ISSUE201_SCENARIO_CATALOG")!;
        var catalog = CatalogDatabase.Open(catalogPath);
        var query = RuntimeCatalogIndex.Create(catalog);
        var index = new UnifiedBrowseIndex(query, SpecialBrowseV2Overlay.FromCatalog(catalog));

        var scenarios = new[]
        {
            new Scenario("sexual / breast / pose", "胸", Sexual with { BodySiteIds = Set("BREAST_NIPPLE"), PrimaryRouteId = "POSE_POSITION" }, ["sideways_perpendicular_paizuri"]),
            new Scenario("sexual / buttock / oral contact", "肛門 舐める", Sexual with { BodySiteIds = Set("BUTTOCK_ANAL"), PrimaryRouteId = "ACTION_CONTACT" }, ["anilingus", "ass-to-mouth"]),
            new Scenario("sexual / mouth / action", "口", Sexual with { BodySiteIds = Set("MOUTH_ORAL"), PrimaryRouteId = "ACTION_CONTACT" }, ["fellatio", "cunnilingus"]),
            new Scenario("sexual / female genital / pose", "女性器", Sexual with { BodySiteIds = Set("FEMALE_GENITAL"), PrimaryRouteId = "POSE_POSITION" }, ["presenting_own_pussy"]),
            new Scenario("sexual / male genital / action", "男性器", Sexual with { BodySiteIds = Set("MALE_GENITAL"), PrimaryRouteId = "ACTION_CONTACT" }, ["fellatio", "handjob"]),
            new Scenario("sexual / restraint / action", "拘束", Sexual with { ThemeIds = Set("BDSM_RESTRAINT"), PrimaryRouteId = "ACTION_CONTACT" }, ["bondage", "bound_arms"]),
            new Scenario("sexual / pregnancy or lactation", "授乳", Sexual with { ThemeIds = Set("REPRO_PREGNANCY_LACTATION") }, ["breastfeeding", "self_milking"]),
            new Scenario("sexual / clothing and pattern", "縞模様の下着", Sexual with { PrimaryRouteId = "CLOTHING_EXPOSURE" }, ["striped_underwear"]),
            new Scenario("sexual / nonhuman and body", "触手", Sexual with { PrimaryRouteId = "NONHUMAN_TRANSFORM" }, ["tentacle_sex"]),
            new Scenario("sexual / composition and camera", "胸元 構図", Sexual with { PrimaryRouteId = "COMPOSITION_CAMERA" }, ["breast_focus", "pov_breasts"]),
            new Scenario("general-purpose contextual clothing", "縞模様の下着", GeneralPurpose with { PrimaryRouteId = "CLOTHING_EXPOSURE" }, ["striped_underwear"]),
            new Scenario("general-purpose contextual action", "手を置く", GeneralPurpose with { PrimaryRouteId = "ACTION_CONTACT", LocalSubrouteId = "ACTION_CONTACT/INTERACTION" }, ["hand_on_another's_head"]),
        };

        var report = new List<object>();
        foreach (var scenario in scenarios)
        {
            var browse = index.Browse(scenario.State);
            var search = index.FilterSearchHits(query.Search(scenario.Query), scenario.State);
            var browseNames = browse.Select(item => item.Canonical).Where(name => name is not null).ToHashSet(StringComparer.Ordinal);
            var searchNames = search.Select(hit => hit.Entry.Canonical).Where(name => name is not null).ToHashSet(StringComparer.Ordinal);
            var expectedFound = scenario.Expected.Where(name => browseNames.Contains(name) || searchNames.Contains(name)).ToArray();
            Assert.Equal(scenario.Expected.Order(StringComparer.Ordinal), expectedFound.Order(StringComparer.Ordinal));
            output.WriteLine($"{scenario.Name}: browse={browse.Count}, search={search.Count}, expected={string.Join(",", expectedFound)}");
            output.WriteLine("browse examples: " + string.Join("; ", browse.Take(12).Select(item => $"{item.Japanese ?? item.Canonical} [{item.Canonical}]")));
            output.WriteLine("query examples: " + string.Join("; ", search.Take(8).Select(hit => $"{hit.Entry.Japanese ?? hit.Entry.Canonical} [{hit.Entry.Canonical}]")));
            report.Add(new
            {
                scenario.Name,
                scenario.Query,
                Filters = new
                {
                    scenario.State.ContentIntent,
                    scenario.State.PrimaryRouteId,
                    scenario.State.LocalSubrouteId,
                    BodySiteIds = scenario.State.BodySiteIds.Order(StringComparer.Ordinal),
                    ThemeIds = scenario.State.ThemeIds.Order(StringComparer.Ordinal),
                    scenario.State.DeepOnly
                },
                BrowseCount = browse.Count,
                SearchCount = search.Count,
                ExpectedTags = scenario.Expected,
                ExpectedFound = expectedFound,
                BrowseExamples = browse.Take(12).Select(item => new { item.Canonical, item.Japanese, item.EffectiveCategory }),
                SearchExamples = search.Take(8).Select(hit => new { hit.Entry.Canonical, hit.Entry.Japanese, hit.Entry.EffectiveCategory })
            });
        }
        foreach (var searchText in new[] { "縞模様の下着", "striped_underwear", "striped_underwear 縞模様の下着" })
        {
            var found = index.FilterSearchHits(query.Search(searchText), Sexual with { PrimaryRouteId = "CLOTHING_EXPOSURE" })
                .Any(hit => hit.Entry.Canonical == "striped_underwear");
            output.WriteLine($"search [{searchText}] => striped_underwear: {found}");
            Assert.True(found, $"Expected the pattern tag from Japanese/English/mixed search: {searchText}");
        }
        if (Environment.GetEnvironmentVariable("DTT_ISSUE201_SCENARIO_REPORT") is { Length: > 0 } reportPath)
            File.WriteAllText(reportPath, JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
    }

    private static UnifiedBrowseState Sexual => UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual };
    private static UnifiedBrowseState GeneralPurpose => UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.GeneralPurpose };

    private static IReadOnlySet<string> Set(string value) => new HashSet<string>([value], StringComparer.Ordinal);

    private sealed record Scenario(string Name, string Query, UnifiedBrowseState State, string[] Expected);
}
