using System.IO;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue118StagingFactAttribute : FactAttribute
{
    public Issue118StagingFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("DTT_ISSUE118_STAGING_CATALOG") == null)
            Skip = "Issue #118 staging catalog validation is opt-in.";
    }
}

public sealed class Issue118OrdinaryStagingValidationTests(ITestOutputHelper output)
{
    [Issue118StagingFact]
    public void StagedOrdinaryCatalogMatchesV2AuthorityAndRuntimeContracts()
    {
        var catalogPath = Environment.GetEnvironmentVariable("DTT_ISSUE118_STAGING_CATALOG")!;
        var sourceRoot = Environment.GetEnvironmentVariable("DTT_SOURCE_ROOT")!;
        var authorityRoot = Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT")!;
        var catalog = CatalogDatabase.Open(catalogPath);
        Assert.Equal(30_629, catalog.Entries.Count(entry => entry.EffectiveCategory == "General"));
        Assert.Equal(3_059, catalog.Entries.Count(entry => entry.EffectiveCategory == "Special"));
        Assert.Equal(33_688, catalog.Entries.Count);
        Assert.DoesNotContain(catalog.Entries, entry => entry.EffectiveCategory is "Character" or "Copyright" or "Artist");

        var authority = AcceptedAssetImporter.Csv(Path.Combine(authorityRoot, Issue118SexualIntentV2Overlay.RelativePath))
            .ToDictionary(row => row["identity_key"], StringComparer.Ordinal);
        var ordinary = catalog.Entries.Where(entry => entry.EffectiveCategory is "General" or "Special").ToArray();
        var groups = ordinary.GroupBy(Issue118SexualIntentV2Overlay.SourceIdentity, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal);
        Assert.Equal(Issue118SexualIntentV2Overlay.IdentityCount, groups.Count);
        Assert.Equal(authority.Keys.OrderBy(key => key, StringComparer.Ordinal), groups.Keys.OrderBy(key => key, StringComparer.Ordinal));

        foreach (var (identity, backing) in groups)
        {
            var row = authority[identity];
            Assert.Equal(row["is_general"], backing.Any(entry => entry.EffectiveCategory == "General") ? "YES" : "NO");
            Assert.Equal(row["is_special"], backing.Any(entry => entry.EffectiveCategory == "Special") ? "YES" : "NO");
            Assert.All(backing, entry =>
            {
                Assert.Equal(row["sexual_intent"], Intent(entry.SexualIntent));
                Assert.Equal(row["review_status"], Status(entry.SexualIntentStatus));
                Assert.Equal(row["rule_id"], entry.SexualIntentSource);
                Assert.Equal(row["evidence"], entry.SexualIntentEvidence);
            });
        }

        var runtime = RuntimeCatalogIndex.Create(catalog);
        var unified = new UnifiedBrowseIndex(runtime);
        Assert.Equal(Issue118SexualIntentV2Overlay.IdentityCount, unified.Identities.Count);
        Assert.Equal(19, UnifiedBrowseTaxonomy.Routes.Length);
        Assert.Equal(unified.Identities.Count, unified.Identities.Count(identity => identity.SexualIntent is not null || identity.SexualIntentStatus == SexualIntentClassificationStatus.Unclassified));

        var all = unified.Identities.ToArray();
        var generalPurpose = all.Where(identity => identity.SexualIntent is SexualIntentClass.NonSexual or SexualIntentClass.Contextual).ToArray();
        var sexual = all.Where(identity => identity.SexualIntent is SexualIntentClass.Sexual or SexualIntentClass.Contextual).ToArray();
        var unclassified = all.Where(identity => identity.SexualIntent is null).ToArray();
        Assert.Equal(31_003, all.Length);
        Assert.Equal(29_493, generalPurpose.Length);
        Assert.Equal(3_292, sexual.Length);
        Assert.Equal(4, unclassified.Length);
        Assert.All(unclassified, identity => Assert.Equal(ContentIntentFilter.All, FilterFor(identity, generalPurpose, sexual)));
        Assert.DoesNotContain(unclassified, identity => generalPurpose.Contains(identity) || sexual.Contains(identity));

        var overlap = all.Single(identity => identity.BackingEntries.Any(entry => entry.EffectiveCategory == "General" && entry.Canonical == "covered_nipples") &&
            identity.BackingEntries.Any(entry => entry.EffectiveCategory == "Special" && entry.English == "covered nipples"));
        Assert.Equal(UnifiedBrowseIndex.IdentityKey(overlap.BackingEntries[0]), UnifiedBrowseIndex.IdentityKey(overlap.BackingEntries[1]));

        var noSafe = new[] { "naked socks", "naked randoseru", "sexual euphemism", "lolicon", "vacuum fellatio", "uterine prolapse" }
            .Select(surface => catalog.Entries.Single(entry => entry.IsSpecial && entry.English == surface)).ToArray();
        Assert.All(noSafe, entry =>
        {
            Assert.Null(entry.Canonical);
            Assert.Equal(Issue118SexualIntentV2Overlay.NormalizeIdentity(entry.English), entry.PromptToken);
            Assert.True(entry.CanAdd);
        });
        var socks = catalog.Entries.Single(entry => entry.EffectiveCategory == "General" && entry.Canonical == "socks");
        Assert.NotEqual(UnifiedBrowseIndex.IdentityKey(socks), UnifiedBrowseIndex.IdentityKey(noSafe[0]));

        var workspace = new PromptWorkspace(new PromptParser(catalog));
        Assert.True(workspace.Add(noSafe[0]));
        Assert.False(workspace.Add(noSafe[0]));
        Assert.Equal(noSafe[0].PromptToken, workspace.Items.Single().Canonical);
        Assert.Equal(noSafe[0].PromptToken, new PromptParser(catalog).Parse(workspace.English).Single().Canonical);

        var search = new SearchEngine(catalog);
        var anal = search.Search("anal");
        Assert.Equal("anal", anal[0].Entry.Canonical);
        Assert.DoesNotContain(anal, hit => hit.Entry.Canonical == "piano" || hit.Entry.Canonical?.StartsWith("analog", StringComparison.Ordinal) == true);
        Assert.Contains(search.Search("naked socks"), hit => hit.Entry.English == "naked socks");

        var generalProvider = GeneralBrowseProvider.FromCatalog(catalog);
        Assert.DoesNotContain(generalProvider.Browse(""), entry => entry.BrowseClassification == BrowseClassificationStatus.Unresolved);
        Assert.All(catalog.Entries.Where(entry => entry.SpecialBrowseV2?.Status == SpecialBrowseV2Status.ReferenceOnlyNoDirectBrowse),
            entry => Assert.False(entry.CanBrowse));

        output.WriteLine($"staged_catalog={catalogPath}");
        output.WriteLine($"runtime_identities={all.Length}; all={all.Length}; general_purpose={generalPurpose.Length}; sexual={sexual.Length}; unclassified={unclassified.Length}");
    }

    private static string Intent(SexualIntentClass? intent) => intent switch
    {
        null => "",
        SexualIntentClass.Sexual => "SEXUAL",
        SexualIntentClass.Contextual => "CONTEXTUAL",
        SexualIntentClass.NonSexual => "NON_SEXUAL",
        _ => throw new ArgumentOutOfRangeException(nameof(intent))
    };

    private static string Status(SexualIntentClassificationStatus status) => status switch
    {
        SexualIntentClassificationStatus.AutoHighConfidence => "AUTO_HIGH_CONF",
        SexualIntentClassificationStatus.HumanReviewed => "HUMAN_REVIEWED",
        SexualIntentClassificationStatus.Unclassified => "UNCLASSIFIED",
        _ => throw new ArgumentOutOfRangeException(nameof(status))
    };

    private static ContentIntentFilter FilterFor(UnifiedBrowseIdentity identity, IReadOnlyList<UnifiedBrowseIdentity> generalPurpose, IReadOnlyList<UnifiedBrowseIdentity> sexual)
        => generalPurpose.Contains(identity) ? ContentIntentFilter.GeneralPurpose : sexual.Contains(identity) ? ContentIntentFilter.Sexual : ContentIntentFilter.All;
}
