using System;
using System.Collections.Generic;
using System.Linq;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue97SpecialAuditTests
{
    [ProductionFact]
    public void ExpandedSpecialCatalogHasCompleteQualityAndBrowseV2Coverage()
    {
        var path = Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!;
        var catalog = CatalogDatabase.Open(path);
        var special = catalog.Entries
            .Where(entry => entry.IsSpecial)
            .OrderBy(entry => ParseSpecialId(entry.Id))
            .ToArray();

        Assert.Equal(AcceptedAssetImporter.ProductionSpecialCount, special.Length);
        var specialIds = special.Select(entry => ParseSpecialId(entry.Id)).ToArray();
        Assert.Equal(specialIds.Length, specialIds.Distinct().Count());
        Assert.All(specialIds, id => Assert.InRange(id, 1, AcceptedAssetImporter.ExpandedSpecialCount));
        Assert.Equal(AcceptedAssetImporter.ExpandedSpecialCount, specialIds.Max());

        Assert.All(special, entry => Assert.False(string.IsNullOrWhiteSpace(entry.Japanese)));
        Assert.All(special, entry => Assert.NotEmpty(entry.JapaneseSearch));
        Assert.All(special, entry => Assert.False(string.IsNullOrWhiteSpace(entry.ProductFit)));
        Assert.All(special, entry => Assert.NotNull(entry.SpecialBrowseV2));

        Assert.Equal(2718, special.Count(entry => entry.SpecialBrowseV2!.Status == SpecialBrowseV2Status.AutoCandidate));
        Assert.Equal(315, special.Count(entry => entry.SpecialBrowseV2!.Status == SpecialBrowseV2Status.HumanResolved));
        Assert.Equal(21, special.Count(entry => entry.SpecialBrowseV2!.Status == SpecialBrowseV2Status.ReferenceOnlyNoDirectBrowse));
        Assert.Equal(5, special.Count(entry => entry.SpecialBrowseV2!.Status == SpecialBrowseV2Status.DeferProductFitReview));
        Assert.Equal(0, special.Count(entry => entry.SpecialBrowseV2!.Status == SpecialBrowseV2Status.OutOfScopeNoBrowse));

        foreach (var entry in special)
        {
            var browse = entry.SpecialBrowseV2!;
            var hasRoute = browse.KindId is not null || browse.BodySiteIds.Length > 0 || browse.ThemeIds.Length > 0;
            if (browse.Status is SpecialBrowseV2Status.AutoCandidate or SpecialBrowseV2Status.HumanResolved)
                Assert.True(hasRoute, $"Browsable Special has no v2 route: {entry.Id}");
            else
                Assert.False(hasRoute, $"Non-browse Special still has a v2 route: {entry.Id}");
        }

        var promoted = special.Where(entry => ParseSpecialId(entry.Id) > AcceptedAssetImporter.BaseSpecialCount).ToArray();
        Assert.Equal(
            AcceptedAssetImporter.ExpandedSpecialCount - AcceptedAssetImporter.BaseSpecialCount,
            promoted.Length);
        Assert.Equal(
            Enumerable.Range(
                AcceptedAssetImporter.BaseSpecialCount + 1,
                AcceptedAssetImporter.ExpandedSpecialCount - AcceptedAssetImporter.BaseSpecialCount),
            promoted.Select(entry => ParseSpecialId(entry.Id)));
        Assert.All(promoted, entry => Assert.Equal(SpecialBrowseV2Status.HumanResolved, entry.SpecialBrowseV2!.Status));

        var baseSurfaces = special
            .Where(entry => ParseSpecialId(entry.Id) <= AcceptedAssetImporter.BaseSpecialCount)
            .SelectMany(Surfaces)
            .ToHashSet(StringComparer.Ordinal);
        var promotedSurfaces = new HashSet<string>(StringComparer.Ordinal);
        foreach (var entry in promoted)
        {
            foreach (var surface in Surfaces(entry).Distinct(StringComparer.Ordinal))
            {
                Assert.DoesNotContain(surface, baseSurfaces);
                Assert.True(promotedSurfaces.Add(surface), $"Promoted Special surface collision: {surface}");
            }
        }
    }

    private static int ParseSpecialId(string value)
    {
        Assert.StartsWith("S:", value, StringComparison.Ordinal);
        return int.Parse(value.AsSpan(2), System.Globalization.CultureInfo.InvariantCulture);
    }

    private static IEnumerable<string> Surfaces(CatalogEntry entry)
    {
        if (!string.IsNullOrWhiteSpace(entry.English)) yield return entry.English;
        if (!string.IsNullOrWhiteSpace(entry.Canonical)) yield return entry.Canonical!;
        foreach (var alias in entry.Aliases)
            if (!string.IsNullOrWhiteSpace(alias)) yield return alias;
    }
}
