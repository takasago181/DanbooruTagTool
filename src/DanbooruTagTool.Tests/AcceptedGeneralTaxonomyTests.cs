using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class AcceptedGeneralTaxonomyTests
{
    [Fact]
    public void AcceptedSidecarBuildsReachableGeneralBrowsePathsAndKeepsUnresolvedOut()
    {
        var authority = Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT") ?? FindRepositoryRoot();
        var imported = AcceptedGeneralTaxonomyImporter.Read(authority);

        Assert.Equal(30_629, imported.Assignments.Count);
        Assert.Equal(28_226, imported.ProposedCount);
        Assert.Equal(2_403, imported.UnresolvedCount);
        Assert.Equal(AcceptedGeneralTaxonomyImporter.AcceptedTaxonomySha256, imported.SourceHashes[AcceptedGeneralTaxonomyImporter.TaxonomyRelativePath]);
        Assert.Equal(AcceptedGeneralTaxonomyImporter.AcceptedSidecarSha256, imported.SourceHashes[AcceptedGeneralTaxonomyImporter.SidecarRelativePath]);

        var catalogEntries = imported.Assignments.Select(pair => new CatalogEntry(
            "G:" + pair.Key, pair.Key, pair.Key, "日本語 " + pair.Key, false, 17,
            [], [], pair.Value.Paths, BrowseClassification: pair.Value.Status)).ToArray();
        var provider = Assert.IsType<GeneralBrowseProvider>(GeneralBrowseProvider.FromCatalog(new Catalog(catalogEntries)));

        Assert.False(provider.IsPending);
        Assert.Equal(28_226, provider.Browse("").Count);
        var unresolved = imported.Assignments.First(pair => pair.Value.Status == BrowseClassificationStatus.Unresolved);
        Assert.Empty(unresolved.Value.Paths);
        Assert.DoesNotContain(provider.Browse(""), entry => entry.Canonical == unresolved.Key);

        var withSecondary = imported.Assignments.First(pair => pair.Value.Status == BrowseClassificationStatus.Proposed && pair.Value.Paths.Length > 1);
        var browseEntry = catalogEntries.Single(entry => entry.Canonical == withSecondary.Key);
        Assert.Equal(2, browseEntry.Paths.Length);
        foreach (var path in browseEntry.Paths)
        {
            Assert.Contains(provider.Browse(path.Key), entry => entry.Canonical == withSecondary.Key);
            Assert.Contains(provider.Browse(path.GenreId + ">"), entry => entry.Canonical == withSecondary.Key);
        }
        Assert.Equal(BrowseClassificationStatus.Proposed, browseEntry.BrowseClassification);
    }

    private static string FindRepositoryRoot()
    {
        for (var directory = new DirectoryInfo(AppContext.BaseDirectory); directory != null; directory = directory.Parent)
            if (File.Exists(Path.Combine(directory.FullName, AcceptedGeneralTaxonomyImporter.TaxonomyRelativePath)))
                return directory.FullName;
        throw new DirectoryNotFoundException("Could not locate the checked-in Issue #64 production candidate assets.");
    }
}
