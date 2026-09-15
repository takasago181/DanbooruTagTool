using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue77Tests
{
    private static Catalog ProfileCatalog() => new([.. Fixtures.Catalog().Entries,
        Fixtures.Entry("mating_(animal)", "動物の交尾", 20)]);

    [Fact]
    public void GenerationProfileNormalizesRecognizedCoresOnly()
    {
        var parser = new PromptParser(ProfileCatalog());
        var source = "blue_hair, (long_hair:1.2), mating_(animal), <lora:Rella:0.6>, BREAK, raw phrase";
        var items = parser.Parse(source);

        Assert.Equal(source, PromptParser.Serialize(items));
        Assert.Equal("blue hair, (long hair:1.2), mating \\(animal\\), <lora:Rella:0.6>, BREAK, raw phrase",
            PromptOutputFormatter.Serialize(items, PromptOutputProfile.GenerationFriendly));
    }

    [Fact]
    public void CanonicalProfileIsByteForByteCurrentSerialization()
    {
        var parser = new PromptParser(ProfileCatalog());
        var source = "  blue_hair , (long_hair:1.20), mating_(animal), raw phrase";
        var items = parser.Parse(source);

        Assert.Equal(source, PromptOutputFormatter.Serialize(items, PromptOutputProfile.Canonical));
    }

    [Fact]
    public void SwitchingProfileDoesNotChangePromptIdentityOrOrder()
    {
        var vm = new MainViewModel(ProfileCatalog(), new MemoryStore(), new MemoryClipboard());
        vm.Workspace.Replace("blue_hair, blue_hair,raw");
        var ids = vm.Workspace.Items.Select(item => item.Id).ToArray();
        var surfaces = vm.Workspace.Items.Select(item => item.Surface).ToArray();

        vm.OutputProfile = PromptOutputProfile.GenerationFriendly;

        Assert.Equal(ids, vm.Workspace.Items.Select(item => item.Id));
        Assert.Equal(surfaces, vm.Workspace.Items.Select(item => item.Surface));
        Assert.Equal("blue hair, blue hair,raw", vm.English);
    }

    [Fact]
    public void PreviewEqualsOneClickCopyForEachProfile()
    {
        var clipboard = new MemoryClipboard();
        var vm = new MainViewModel(ProfileCatalog(), new MemoryStore(), clipboard);
        vm.Workspace.Replace("blue_hair, (long_hair:1.2), raw");

        foreach (var profile in new[] { PromptOutputProfile.Canonical, PromptOutputProfile.GenerationFriendly })
        {
            vm.OutputProfile = profile;
            vm.Copy.Execute(null);
            Assert.Equal(vm.English, clipboard.Value);
        }
    }

    [Fact]
    public void ProfilePersistsThroughExistingUserStateStore()
    {
        var store = new MemoryStore();
        var first = new MainViewModel(ProfileCatalog(), store, new MemoryClipboard());
        first.OutputProfile = PromptOutputProfile.GenerationFriendly;

        var second = new MainViewModel(ProfileCatalog(), store, new MemoryClipboard());

        Assert.Equal(PromptOutputProfile.GenerationFriendly, second.OutputProfile);
        Assert.Equal("生成向け", second.OutputProfiles.Single(option => option.Value == second.OutputProfile).Label);
    }

    [Fact]
    public void ImportAcceptsCanonicalSpacedAndEscapedGenerationTokens()
    {
        var parser = new PromptParser(ProfileCatalog());

        var canonical = Assert.Single(parser.Parse("blue_hair"));
        var spaced = Assert.Single(parser.Parse("blue hair"));
        var escaped = Assert.Single(parser.Parse("mating \\(animal\\)"));

        Assert.Equal("blue_hair", canonical.Canonical);
        Assert.Equal("blue_hair", spaced.Canonical);
        Assert.Equal("mating_(animal)", escaped.Canonical);
        Assert.Equal("mating \\(animal\\)", escaped.Surface);
    }

    [Fact]
    public void WeightedGenerationImportPreservesWeightAndRawSurfaces()
    {
        var parser = new PromptParser(ProfileCatalog());
        var items = parser.Parse("(long hair:1.20), <lora:Rella:0.6>, BREAK, unknown phrase");

        Assert.Equal(PromptItemKind.Weighted, items[0].Kind);
        Assert.Equal("long_hair", items[0].Canonical);
        Assert.Equal(1.20m, items[0].Weight);
        Assert.Equal("(long hair:1.20)", items[0].Surface);
        Assert.Equal(PromptItemKind.Lora, items[1].Kind);
        Assert.Equal(PromptItemKind.Control, items[2].Kind);
        Assert.Equal(PromptItemKind.Raw, items[3].Kind);
        Assert.Equal(" unknown phrase", items[3].Surface);
    }

    [Fact]
    public void NonMatchingNaturalTextAndAmbiguousRecognitionRemainRaw()
    {
        var ambiguous = new Catalog([
            Fixtures.Entry("first_identity", "一", special: true) with { English = "same phrase" },
            Fixtures.Entry("second_identity", "二", special: true) with { English = "same phrase" }
        ]);
        var parser = new PromptParser(ambiguous);

        var items = parser.Parse("same phrase, a natural language sentence");

        Assert.All(items, item => Assert.Equal(PromptItemKind.Raw, item.Kind));
        Assert.Equal("same phrase, a natural language sentence", PromptParser.Serialize(items));
    }

    [Fact]
    public void DirectEnglishEditAcceptsBothStylesConservatively()
    {
        var vm = new MainViewModel(ProfileCatalog(), new MemoryStore(), new MemoryClipboard());
        vm.Workspace.Replace("raw");

        vm.StartDirect.Execute(null);
        vm.DirectText = "blue hair, mating \\(animal\\), <lora:Rella:0.6>, BREAK, untouched words";
        vm.ApplyDirect.Execute(null);

        Assert.Equal(new[] { "blue_hair", "mating_(animal)", null, null, null },
            vm.Workspace.Items.Select(item => item.Canonical));
        Assert.Equal("blue hair, mating \\(animal\\), <lora:Rella:0.6>, BREAK, untouched words", vm.English);
    }
}
