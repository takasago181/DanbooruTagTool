using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue179QualityOverlayTests
{
    [Fact]
    public void ReviewedProjectionAppliesOnlyExpectedIssue70Rows()
    {
        var root = FindRepoRoot();
        var issue70Path = Path.Combine(root, Issue70CatalogOverlayImporter.RelativePath);
        var projectionPath = Path.Combine(root, Issue179QualityOverlay.RelativePath);

        var before = Issue70CatalogOverlayImporter.Read(issue70Path);
        var after = Issue179QualityOverlay.Apply(projectionPath, issue70Path, before);

        Assert.Equal(before.Length, after.Length);
        Assert.Equal(Issue179QualityOverlay.ExpectedRows,
            before.Zip(after).Count(pair =>
                pair.First.Japanese != pair.Second.Japanese ||
                !pair.First.JapaneseSearch.SequenceEqual(pair.Second.JapaneseSearch)));

        var miku = after.Single(e => e.Canonical == "hatsune_miku");
        Assert.Equal("初音ミク", miku.Japanese);
        Assert.Equal(["初音ミク", "ミク"], miku.JapaneseSearch);

        var jupiter = after.Single(e => e.Canonical == "super_sailor_jupiter");
        Assert.Equal("スーパーセーラージュピター", jupiter.Japanese);
        Assert.Equal(["スーパーセーラージュピター"], jupiter.JapaneseSearch);

        var jahy = after.Single(e => e.Canonical == "jahy");
        Assert.Equal("ジャヒー様", jahy.Japanese);
        Assert.Equal(["ジャヒー", "ジャヒー様"], jahy.JapaneseSearch);

        var ritsuka = after.Single(e =>
            e.Canonical == "fujimaru_ritsuka_(female)_(decisive_battle_chaldea_uniform)");
        Assert.Equal("藤丸立香（女性）（決戦用カルデア制服）", ritsuka.Japanese);

        Assert.Equal("矢倉蓬咲", after.Single(e => e.Canonical == "yakura_yomogi").Japanese);
        Assert.Equal("四宮寧月", after.Single(e => e.Canonical == "shinomiya_shizuku").Japanese);
        Assert.Equal("須賀蕾叶", after.Single(e => e.Canonical == "suga_raika").Japanese);
        Assert.Equal("馬橋心玖", after.Single(e => e.Canonical == "mahashi_miku").Japanese);

        // The shared surface is an identity for Azur Lane, but only a surname for Mari.
        Assert.Contains("イラストリアス", after.Single(e => e.Canonical == "illustrious_(azur_lane)").JapaneseSearch);
        Assert.DoesNotContain("イラストリアス", after.Single(e => e.Canonical == "makinami_mari_illustrious").JapaneseSearch);
        Assert.Contains("真希波・マリ・イラストリアス", after.Single(e => e.Canonical == "makinami_mari_illustrious").JapaneseSearch);
        Assert.DoesNotContain("エンイラ(アズールレーン)", after.Single(e => e.Canonical == "enterprise_(azur_lane)").JapaneseSearch);

        Assert.Empty(after.Single(e => e.Canonical == "ace_attorney").JapaneseSearch);
        Assert.Empty(after.Single(e => e.Canonical == "kuroshitsuji").JapaneseSearch);

        var artistBefore = before.First(e => e.EffectiveCategory == "Artist");
        var artistAfter = after.Single(e => e.Id == artistBefore.Id);
        Assert.Equal(artistBefore, artistAfter);
        Assert.All(after, e =>
        {
            Assert.Null(e.FormalHomeCopyright);
            Assert.Null(e.ReviewedBrowseHome);
        });
    }


    [Fact]
    public void OverlayComposesWithBrowseHomeWithoutChangingAuthorityCounts()
    {
        var root = FindRepoRoot();
        var issue70Path = Path.Combine(root, Issue70CatalogOverlayImporter.RelativePath);
        var projectionPath = Path.Combine(root, Issue179QualityOverlay.RelativePath);
        var homePath = Path.Combine(root, Issue216BrowseHomeImporter.RelativePath);

        var issue70 = Issue70CatalogOverlayImporter.Read(issue70Path);
        var quality = Issue179QualityOverlay.Apply(projectionPath, issue70Path, issue70);
        var combined = Issue216BrowseHomeImporter.Apply(homePath, quality);

        Assert.Equal(issue70.Length, combined.Length);
        Assert.Equal(35278, combined.Count(e => e.EffectiveCategory == "Character"));
        Assert.Equal(7616, combined.Count(e => e.EffectiveCategory == "Copyright"));
        Assert.Equal(48313, combined.Count(e => e.EffectiveCategory == "Artist"));
        Assert.Equal(25533, combined.Count(e => e.FormalHomeCopyright is not null));
        Assert.Equal(7409, combined.Count(e => e.ReviewedBrowseHome is not null));
        Assert.Equal(2336, combined.Count(e =>
            e.EffectiveCategory == "Character" && e.EffectiveBrowseHome is null));

        var fallback = combined.Single(e => e.Canonical == "yuzuki_yukari");
        Assert.Equal("voiceroid", fallback.EffectiveBrowseHome);
        Assert.Equal("REVIEWED_BROWSE_FALLBACK", fallback.BrowseHomeSource);
    }

    [Fact]
    public void ProjectionIsPinnedToReviewedArtifact()
    {
        var root = FindRepoRoot();
        var projectionPath = Path.Combine(root, Issue179QualityOverlay.RelativePath);
        Assert.Equal(Issue179QualityOverlay.ExpectedSha256, AcceptedAssetImporter.Hash(projectionPath));
        Assert.Equal(Issue179QualityOverlay.ExpectedRows, AcceptedAssetImporter.Csv(projectionPath).Count);
    }

    private static string FindRepoRoot()
    {
        DirectoryInfo? dir = new(AppContext.BaseDirectory);
        while (dir != null && !File.Exists(Path.Combine(dir.FullName, "AGENTS.md"))) dir = dir.Parent;
        return dir?.FullName ?? throw new DirectoryNotFoundException("Repository root not found");
    }
}
