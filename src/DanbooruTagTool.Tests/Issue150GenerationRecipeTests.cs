using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue150GenerationRecipeTests
{
    [Fact]
    public void LegacyPresetJsonWithoutRecipeStillLoads()
    {
        var id = Guid.NewGuid();
        var json = $$"""{"Id":"{{id}}","Name":"legacy","Description":"","Positive":"blue_hair","Negative":"lowres"}""";

        var preset = JsonSerializer.Deserialize<GenerationPreset>(json)!;

        Assert.Equal("legacy", preset.Name);
        Assert.Null(preset.Recipe);
        Assert.False(preset.HasRecipe);
    }

    [Fact]
    public void RecipePersistsThroughUserStateStore()
    {
        using var directory = new TempDirectory();
        var path = new PortablePaths(directory.Path).User;
        var workspace = Fixtures.Workspace();
        var recipe = new GenerationRecipe("waiIllustriousSDXL_v170", 16521, 8, "Euler a", "Automatic", 5m, 1024, 1024);
        var preset = new GenerationPreset(Guid.NewGuid(), "recipe", "test", "blue_hair", "lowres", recipe);

        new UserStateStore(path).Save(new(workspace.Snapshot(), new(), [preset]));
        var restored = Assert.Single(new UserStateStore(path).Load()!.Presets!);

        Assert.True(restored.HasRecipe);
        Assert.Equal(recipe, restored.Recipe);
        Assert.Contains("8 steps", restored.RecipeSummary);
        Assert.Contains("1024×1024", restored.RecipeSummary);
    }

    [Fact]
    public void AllGenerationRecipeFieldsAreReferenceOnly()
    {
        var recipe = new GenerationRecipe(
            Model: "manual-model",
            Seed: 42,
            Steps: 20,
            Sampler: "Euler a",
            Scheduler: "Karras",
            Cfg: 5m,
            Width: 832,
            Height: 1216);
        var preset = new GenerationPreset(Guid.NewGuid(), "reference recipe", "", "blue_hair", "lowres", recipe);

        Assert.True(recipe.HasAny);
        Assert.False(recipe.HasAutomaticSettings);
        Assert.True(preset.HasRecipe);
    }

    [Fact]
    public void PngSnapshotPrefillsRecipeWithoutAutoSaving()
    {
        var store = new MemoryStore();
        var vm = Fixtures.Vm(store);
        var snapshot = ForgePngGenerationMetadata.Parse(
            "sample.png",
            "blue_hair, smile\nNegative prompt: lowres\nSteps: 8, Sampler: Euler a, Schedule type: Automatic, CFG scale: 5, Seed: 16521, Size: 1024x1024, Model: waiIllustriousSDXL_v170");

        vm.GenerationImport.Load(snapshot);
        vm.GenerationImport.CreatePreset.Execute(null);

        Assert.Empty(vm.Presets);
        Assert.Equal("blue_hair, smile", vm.PresetPositive);
        Assert.Equal("lowres", vm.PresetNegative);
        Assert.Equal("waiIllustriousSDXL_v170", vm.PresetModel);
        Assert.Equal("16521", vm.PresetSeed);
        Assert.Equal("8", vm.PresetSteps);
        Assert.Equal("Euler a", vm.PresetSampler);
        Assert.Equal("Automatic", vm.PresetScheduler);
        Assert.Equal("5", vm.PresetCfg);
        Assert.Equal("1024", vm.PresetWidth);
        Assert.Equal("1024", vm.PresetHeight);
        Assert.Null(store.State);
    }

    [Fact]
    public void SavingPrefilledRecipePersistsOnlyAfterExplicitSave()
    {
        var store = new MemoryStore();
        var vm = Fixtures.Vm(store);
        vm.NewPreset.Execute(null);
        vm.PresetName = "my recipe";
        vm.PresetPositive = "blue_hair";
        vm.PresetNegative = "lowres";
        vm.PresetSeed = "42";
        vm.PresetSteps = "25";
        vm.PresetSampler = "Euler a";
        vm.PresetScheduler = "Karras";
        vm.PresetCfg = "5.5";
        vm.PresetWidth = "832";
        vm.PresetHeight = "1216";

        vm.SavePreset.Execute(null);

        var preset = Assert.Single(vm.Presets);
        Assert.NotNull(preset.Recipe);
        Assert.Equal(42, preset.Recipe!.Seed);
        Assert.Equal(25, preset.Recipe.Steps);
        Assert.Equal(5.5m, preset.Recipe.Cfg);
        Assert.NotNull(store.State);
        Assert.Equal(preset, Assert.Single(store.State!.Presets!));
    }

    [Fact]
    public void EmptyRecipeFieldsPreservePromptOnlyPreset()
    {
        var vm = Fixtures.Vm();
        vm.NewPreset.Execute(null);
        vm.PresetName = "prompt only";
        vm.PresetPositive = "blue_hair";
        vm.PresetNegative = "lowres";

        vm.SavePreset.Execute(null);

        var preset = Assert.Single(vm.Presets);
        Assert.Null(preset.Recipe);
        Assert.False(preset.HasRecipe);
    }

    [Fact]
    public void InvalidRecipeNumberDoesNotSave()
    {
        var vm = Fixtures.Vm();
        vm.NewPreset.Execute(null);
        vm.PresetName = "bad";
        vm.PresetPositive = "blue_hair";
        vm.PresetSteps = "999";

        vm.SavePreset.Execute(null);

        Assert.Empty(vm.Presets);
        Assert.Contains("Steps", vm.Status);
    }


}
