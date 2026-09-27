using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.VisualBasic.FileIO;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue132ProductionDeltaTests
{
    [Fact]
    public void BakedOverlayAddsExactlyTheAcceptedPairsAndPreservesOtherOrdinaryMetadata()
    {
        var additions = ReadAcceptedPairs();
        var catalog = CatalogWithAcceptedTargets(additions);
        var beforeIndex = new UnifiedBrowseIndex(catalog);
        var bakedEntries = Issue132RouteOverlay.Bake(catalog);
        var baked = new Catalog(bakedEntries);
        var afterIndex = new UnifiedBrowseIndex(baked);

        Assert.Equal(274, additions.Count);
        Assert.Equal(273, additions.Select(pair => pair.IdentityKey).Distinct(StringComparer.Ordinal).Count());
        Assert.Equal(274, additions.Select(pair => (pair.IdentityKey, pair.RouteId)).Distinct().Count());
        Assert.Equal(273, beforeIndex.Identities.Count);
        Assert.Equal(beforeIndex.Identities.Count, afterIndex.Identities.Count);

        var expected = additions.GroupBy(pair => pair.IdentityKey, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.Select(pair => pair.RouteId).ToHashSet(StringComparer.Ordinal), StringComparer.Ordinal);
        var changed = beforeIndex.Identities
            .Where(identity => !identity.RouteIds.SetEquals(afterIndex.Identities.Single(after => after.IdentityKey == identity.IdentityKey).RouteIds))
            .ToArray();
        Assert.Equal(273, changed.Length);
        Assert.Equal(expected.Keys.OrderBy(key => key, StringComparer.Ordinal), changed.Select(identity => identity.Representative.Canonical!).OrderBy(key => key, StringComparer.Ordinal));

        foreach (var identity in beforeIndex.Identities)
        {
            var after = Assert.Single(afterIndex.Identities, value => value.IdentityKey == identity.IdentityKey);
            var expectedRoutes = identity.RouteIds.ToHashSet(StringComparer.Ordinal);
            expectedRoutes.UnionWith(expected.GetValueOrDefault(identity.Representative.Canonical!, []));
            Assert.Equal(expectedRoutes.OrderBy(route => route, StringComparer.Ordinal), after.RouteIds.OrderBy(route => route, StringComparer.Ordinal));
            Assert.Contains("LIVING", after.RouteIds);
            Assert.Equal(identity.LocalSubrouteIds, after.LocalSubrouteIds);
            Assert.Equal(identity.BodySiteIds, after.BodySiteIds);
            Assert.Equal(identity.ThemeIds, after.ThemeIds);
            Assert.Equal(identity.SexualIntent, after.SexualIntent);
            Assert.Equal(identity.SexualIntentStatus, after.SexualIntentStatus);
        }

        foreach (var pair in additions)
        {
            var identity = Assert.Single(afterIndex.Identities, value => value.Representative.Canonical == pair.IdentityKey);
            Assert.Contains(pair.RouteId, identity.RouteIds);
        }

        var unrelatedCharacter = Assert.Single(bakedEntries, entry => entry.Id == "C:unrelated-copy");
        Assert.Equal(["EXPRESSION_GAZE"], unrelatedCharacter.UnifiedBrowseRouteIds);
    }

    [Fact]
    public void OverlayLeavesSearchOrderContentLensesAndFacetsUnchanged()
    {
        var additions = ReadAcceptedPairs();
        var entries = CatalogWithAcceptedTargets(additions).Entries.ToList();
        var first = additions[0].IdentityKey;
        var firstIntent = entries.Single(entry => entry.Canonical == first).SexualIntent;
        entries.Add(new CatalogEntry("S:body-theme-copy", first, first, "部位テスト", true, 0, [], ["部位テスト"], [], "KEEP",
            SpecialBrowseV2: new(null, ["MOUTH_ORAL"], ["BDSM_RESTRAINT"], SpecialBrowseV2Status.HumanResolved))
        {
            TagCategory = "Special",
            SexualIntent = firstIntent,
            SexualIntentStatus = SexualIntentClassificationStatus.HumanReviewed
        });

        var catalog = new Catalog(entries);
        var baked = new Catalog(Issue132RouteOverlay.Bake(catalog));
        var englishQuery = first;
        var japaneseQuery = "部位テスト";
        var mixedQuery = first.Split('_')[0] + " 部位テスト";
        foreach (var query in new[] { englishQuery, japaneseQuery, mixedQuery })
        {
            Assert.Equal(catalog.Search(query).Select(hit => (hit.Entry.Id, hit.Rank)),
                baked.Search(query).Select(hit => (hit.Entry.Id, hit.Rank)));
        }

        var before = new UnifiedBrowseIndex(catalog);
        var after = new UnifiedBrowseIndex(baked);
        foreach (var lens in new[] { ContentIntentFilter.All, ContentIntentFilter.GeneralPurpose, ContentIntentFilter.Sexual })
        {
            var neutral = UnifiedBrowseState.Neutral with { ContentIntent = lens };
            Assert.Equal(before.Browse(neutral).Select(entry => entry.Canonical).OrderBy(value => value, StringComparer.Ordinal),
                after.Browse(neutral).Select(entry => entry.Canonical).OrderBy(value => value, StringComparer.Ordinal));

            var bodyFiltered = neutral.ToggleBodySite("MOUTH_ORAL");
            bodyFiltered = bodyFiltered.ToggleTheme("BDSM_RESTRAINT");
            Assert.Equal(before.Browse(bodyFiltered).Select(entry => entry.Canonical), after.Browse(bodyFiltered).Select(entry => entry.Canonical));
        }

        var special = Assert.Single(baked.Entries, entry => entry.Id == "S:body-theme-copy");
        Assert.Equal(["MOUTH_ORAL"], special.SpecialBrowseV2!.BodySiteIds);
        Assert.Equal(["BDSM_RESTRAINT"], special.SpecialBrowseV2.ThemeIds);
    }

    [Fact]
    public void SexualLensCanReachTheAcceptedBodyActionPoseAndRelationRoutes()
    {
        var additions = ReadAcceptedPairs();
        var catalog = CatalogWithAcceptedTargets(additions);
        var before = new UnifiedBrowseIndex(catalog);
        var after = new UnifiedBrowseIndex(new Catalog(Issue132RouteOverlay.Bake(catalog)));
        foreach (var route in new[] { "BODY_SITE", "ACTION_CONTACT", "POSE_POSITION", "RELATION_ROLE" })
        {
            var identityKey = Assert.Single(additions.Where(pair => pair.RouteId == route).Select(pair => pair.IdentityKey)
                .Distinct(StringComparer.Ordinal).Take(1));
            var state = UnifiedBrowseState.Neutral with
            {
                PrimaryRouteId = route,
                ContentIntent = ContentIntentFilter.Sexual
            };
            Assert.DoesNotContain(before.Browse(state), entry => entry.Canonical == identityKey);
            Assert.Contains(after.Browse(state), entry => entry.Canonical == identityKey);
        }
    }

    [Fact]
    public void OverlayFailsIfIdentityIsMissingOrRequestedRouteAlreadyExists()
    {
        var additions = ReadAcceptedPairs();
        var complete = CatalogWithAcceptedTargets(additions).Entries.ToList();
        var first = additions[0];

        Assert.Throws<InvalidDataException>(() => Issue132RouteOverlay.Bake(new Catalog(complete.Skip(1).ToArray())));

        var existingRoute = complete.Single(entry => entry.Canonical == first.IdentityKey);
        complete[complete.IndexOf(existingRoute)] = existingRoute with { UnifiedBrowseRouteIds = [first.RouteId] };
        Assert.Throws<InvalidDataException>(() => Issue132RouteOverlay.Bake(new Catalog(complete)));
    }

    private static Catalog CatalogWithAcceptedTargets(IReadOnlyList<(string IdentityKey, string RouteId)> additions)
    {
        var identities = additions.Select(pair => pair.IdentityKey).Distinct(StringComparer.Ordinal)
            .OrderBy(identity => identity, StringComparer.Ordinal).ToArray();
        var sexualRepresentatives = additions
            .Where(pair => pair.RouteId is "BODY_SITE" or "ACTION_CONTACT" or "POSE_POSITION" or "RELATION_ROLE")
            .GroupBy(pair => pair.RouteId, StringComparer.Ordinal)
            .Select(group => group.First().IdentityKey)
            .ToHashSet(StringComparer.Ordinal);
        var entries = identities.Select((identity, index) => new CatalogEntry(
            "G:" + index, identity, identity, "タグ" + index, false, index, [], ["検索語" + index],
            [new BrowsePath("LIVING_NATURE", "生物・植物")], "KEEP",
            BrowseClassification: BrowseClassificationStatus.Proposed)
        {
            TagCategory = "General",
            SexualIntent = sexualRepresentatives.Contains(identity) ? SexualIntentClass.Sexual : (index % 3) switch
            {
                0 => SexualIntentClass.NonSexual,
                1 => SexualIntentClass.Sexual,
                _ => SexualIntentClass.Contextual
            },
            SexualIntentStatus = SexualIntentClassificationStatus.HumanReviewed
        }).ToList();
        entries.Add(new CatalogEntry("C:unrelated-copy", "unrelated_tag", "unrelated_tag", "別タグ", false, 0, [], [], [], "KEEP")
        {
            TagCategory = "Character",
            UnifiedBrowseRouteIds = ["EXPRESSION_GAZE"]
        });
        return new Catalog(entries);
    }

    private static IReadOnlyList<(string IdentityKey, string RouteId)> ReadAcceptedPairs()
    {
        var assembly = typeof(Issue132RouteOverlay).Assembly;
        var resource = Assert.Single(assembly.GetManifestResourceNames(),
            name => name.EndsWith("issue132_secondary_routes_v1.csv", StringComparison.Ordinal));
        using var stream = assembly.GetManifestResourceStream(resource)!;
        using var parser = new TextFieldParser(stream, System.Text.Encoding.UTF8)
        {
            TextFieldType = FieldType.Delimited,
            HasFieldsEnclosedInQuotes = true,
            TrimWhiteSpace = false
        };
        parser.SetDelimiters(",");
        Assert.Equal(["identity_key", "route_id"], parser.ReadFields()!.Select(value => value.TrimStart('\uFEFF')));
        var pairs = new List<(string IdentityKey, string RouteId)>();
        while (!parser.EndOfData)
        {
            var fields = parser.ReadFields()!;
            pairs.Add((fields[0], fields[1]));
        }
        return pairs;
    }
}
