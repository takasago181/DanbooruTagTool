using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue79Tests
{
    [Fact]
    public void PresetCreateSaveLoadUpdateAndDeleteUseStableIds()
    {
        var store = new MemoryStore();
        var vm = Fixtures.Vm(store: store);
        vm.NewPreset.Execute(null);
        vm.PresetName = "Portrait";
        vm.PresetDescription = "Reusable set";
        vm.PresetPositive = "long_hair";
        vm.PresetNegative = "lowres, bad anatomy";
        vm.SavePreset.Execute(null);

        var saved = Assert.Single(vm.Presets);
        var id = saved.Id;
        Assert.Equal("long_hair", saved.Positive);
        Assert.Equal("lowres, bad anatomy", saved.Negative);

        var restored = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard());
        Assert.Equal(id, Assert.Single(restored.Presets).Id);
        restored.SelectedPreset = restored.Presets[0];
        restored.PresetName = "Updated portrait";
        restored.SavePreset.Execute(null);
        Assert.Equal(id, Assert.Single(restored.Presets).Id);
        Assert.Equal("Updated portrait", restored.Presets[0].Name);

        restored.DeletePreset.Execute(restored.SelectedPreset);
        Assert.Empty(restored.Presets);
        Assert.NotNull(store.State);
        Assert.Empty(store.State!.Presets!);
    }

    [Fact]
    public void PositiveCaptureUsesCanonicalInternalPromptNotOutputProfile()
    {
        var vm = Fixtures.Vm();
        vm.Workspace.Replace("long_hair, (blue_hair:1.20), raw, <lora:X:0.6>, BREAK");
        vm.OutputProfile = PromptOutputProfile.GenerationFriendly;
        vm.NewPreset.Execute(null);
        vm.CapturePresetPositive.Execute(null);

        Assert.Equal("long_hair, (blue_hair:1.20), raw, <lora:X:0.6>, BREAK", vm.PresetPositive);
        Assert.Equal("long hair, (blue hair:1.20), raw, <lora:X:0.6>, BREAK", vm.English);
    }

    [Fact]
    public void CaptureUsesCurrentInternalSurfaceBeforeCanonicalSave()
    {
        var vm = Fixtures.Vm();
        vm.Workspace.Replace("long hair, raw");
        vm.NewPreset.Execute(null);
        vm.CapturePresetPositive.Execute(null);

        Assert.Equal("long hair, raw", vm.PresetPositive);
        vm.PresetName = "Captured";
        vm.SavePreset.Execute(null);
        Assert.Equal("long_hair, raw", Assert.Single(vm.Presets).Positive);
    }

    [Fact]
    public void ManualPositiveSaveCanonicalizesRecognizedSpacedTagsOnly()
    {
        var vm = Fixtures.Vm();
        vm.NewPreset.Execute(null);
        vm.PresetName = "Mixed";
        vm.PresetPositive = "long hair, (blue hair:1.2), raw phrase";
        vm.SavePreset.Execute(null);

        Assert.Equal("long_hair, (blue_hair:1.2), raw phrase", Assert.Single(vm.Presets).Positive);
    }

    [Fact]
    public void PositiveApplyAppendsInOrderSkipsCanonicalDuplicatesAndIsOneUndo()
    {
        var vm = Fixtures.Vm();
        vm.Workspace.Replace("blue_hair, blue_hair, raw");
        var preset = new GenerationPreset(Guid.NewGuid(), "Set", "", "blue_hair, long_hair, (long_hair:1.2), raw, <lora:X:0.6>, BREAK", "");
        vm.Presets.Add(preset);

        vm.ApplyPreset.Execute(preset);

        Assert.Equal("blue_hair, blue_hair, raw, long_hair, raw, <lora:X:0.6>, BREAK", vm.Workspace.English);
        Assert.Equal("4件追加 / 2件スキップ", vm.Status);
        vm.Undo.Execute(null);
        Assert.Equal("blue_hair, blue_hair, raw", vm.Workspace.English);
    }

    [Fact]
    public void WeightedExistingCanonicalIsSkippedWithoutChangingExistingWeight()
    {
        var vm = Fixtures.Vm();
        vm.Workspace.Replace("(long_hair:1.5)");
        var preset = new GenerationPreset(Guid.NewGuid(), "Set", "", "(long_hair:1.2), blue_hair", "");

        vm.ApplyPreset.Execute(preset);

        Assert.Equal("(long_hair:1.5), blue_hair", vm.Workspace.English);
        Assert.Equal("1件追加 / 1件スキップ", vm.Status);
    }

    [Fact]
    public void NegativeRoundTripsAndCopiesOpaqueTextIncludingEmpty()
    {
        var clip = new MemoryClipboard();
        var vm = Fixtures.Vm(clipboard: clip);
        var negative = "lowres, (bad_anatomy:1.2)\r\n<lora:custom:0.7>, raw_text";
        var preset = new GenerationPreset(Guid.NewGuid(), "Opaque", "", "", negative);
        vm.Presets.Add(preset);

        vm.CopyPresetNegative.Execute(preset);
        Assert.Equal(negative, clip.Value);
        vm.Presets[0] = preset with { Negative = "" };
        vm.CopyPresetNegative.Execute(vm.Presets[0]);
        Assert.Equal("", clip.Value);
    }

    [Fact]
    public void GenerationStylePositiveIsRecognizedAndProfileSwitchDoesNotMutatePreset()
    {
        var store = new MemoryStore();
        var vm = Fixtures.Vm(store: store);
        vm.NewPreset.Execute(null);
        vm.PresetName = "Generation style";
        vm.PresetPositive = "long hair";
        vm.SavePreset.Execute(null);
        var stored = Assert.Single(vm.Presets).Positive;

        vm.OutputProfile = PromptOutputProfile.GenerationFriendly;
        vm.Workspace.Replace("long_hair");
        Assert.Equal("long hair", vm.English);
        Assert.Equal(stored, vm.Presets[0].Positive);
        vm.OutputProfile = PromptOutputProfile.Canonical;
        Assert.Equal("long_hair", vm.English);
        Assert.Equal(stored, vm.Presets[0].Positive);
    }

    [Fact]
    public void ExistingUiStateAndOutputProfileSurvivePresetPayloadExtension()
    {
        using var directory = new TempDirectory();
        var path = new PortablePaths(directory.Path).User;
        var workspace = Fixtures.Workspace();
        workspace.Replace("blue_hair");
        var ui = new UiState(OutputProfile: PromptOutputProfile.GenerationFriendly, Workspace: 1, Query: "青い");
        var preset = new GenerationPreset(Guid.NewGuid(), "Saved", "description", "blue_hair", "negative");
        new UserStateStore(path).Save(new(workspace.Snapshot(), ui, [preset]));

        var vm = new MainViewModel(Fixtures.Catalog(), new UserStateStore(path), new MemoryClipboard());

        Assert.Equal(PromptOutputProfile.GenerationFriendly, vm.OutputProfile);
        Assert.Equal(1, vm.WorkspaceIndex);
        Assert.Equal("青い", vm.Query);
        Assert.Equal(preset, Assert.Single(vm.Presets));
    }

    [Fact]
    public void GenerationStyleEscapedParenthesesAndRawRemainConservative()
    {
        var parser = new PromptParser(Fixtures.Catalog());
        var items = parser.Parse("long hair, mating \\(animal\\), arbitrary natural language");

        Assert.Equal("long_hair", items[0].Canonical);
        Assert.Equal(PromptItemKind.Raw, items[1].Kind);
        Assert.Equal(" mating \\(animal\\)", items[1].Surface);
        Assert.Equal(PromptItemKind.Raw, items[2].Kind);
    }
}
