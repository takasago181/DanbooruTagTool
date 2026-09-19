using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class CatalogBuildProfileTests
{
    [Theory]
    [InlineData("full", CatalogBuildProfile.Full)]
    [InlineData("FULL", CatalogBuildProfile.Full)]
    [InlineData("ordinary", CatalogBuildProfile.Ordinary)]
    [InlineData(" Ordinary ", CatalogBuildProfile.Ordinary)]
    public void ParsesExplicitProfiles(string value, CatalogBuildProfile expected)
        => Assert.Equal(expected, CatalogBuildProfiles.Parse(value));

    [Fact]
    public void RejectsUnknownProfiles()
        => Assert.Throws<ArgumentException>(() => CatalogBuildProfiles.Parse("catalog70"));

    [Fact]
    public void ExistingReadOverloadRemainsFullProfile()
        => Assert.Equal("full", CatalogBuildProfile.Full.Name());
}
