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

        Assert.Empty(after.Single(e => e.Canonical == "ace_attorney").JapaneseSearch);
        Assert.Empty(after.Single(e => e.Canonical == "kuroshitsuji").JapaneseSearch);

        var artistBefore = before.Single(e => e.EffectiveCategory == "Artist");
        var artistAfter = after.Single(e => e.Id == artistBefore.Id);
        Assert.Equal(artistBefore, artistAfter);
        Assert.All(after, e =>
        {
            Assert.Null(e.FormalHomeCopyright);
            Assert.Null(e.ReviewedBrowseHome);
        });
    }

    [Fact]
    public void ProjectionIsPinnedToReviewedArtifact()
    {
        var root = FindRepoRoot();
        var projectionPath = Path.Combine(root, Issue179QualityOverlay.RelativePath);
        Assert.Equal(Issue179QualityOverlay.ExpectedSha256, AcceptedAssetImporter.Hash(projectionPath));
        Assert.Equal(1180, AcceptedAssetImporter.Csv(projectionPath).Count);
    }

    private static string FindRepoRoot()
    {
        DirectoryInfo? dir = new(AppContext.BaseDirectory);
        while (dir != null && !File.Exists(Path.Combine(dir.FullName, "AGENTS.md"))) dir = dir.Parent;
        return dir?.FullName ?? throw new DirectoryNotFoundException("Repository root not found");
    }
}
