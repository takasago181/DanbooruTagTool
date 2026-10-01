using System.IO;
using DanbooruTagTool.App;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue226LibraryWorkflowTests
{
    [Fact]
    public async Task RestorePresetSendAndGenerateReuseExistingAuthorities()
    {
        using var d = new LibraryFixture(); var memory = new MemoryStore(); var bridge = new RecordingBridge(); var paths = new PortablePaths(d.Path);
        var main = new MainViewModel(Fixtures.Catalog(), memory, new MemoryClipboard(), forgeBridge: bridge, paths: paths);
        var vm = main.GenerationLibrary!; main.Workspace.Replace("smile");
        Issue226LibraryFoundationTests.WritePng(Path.Combine(d.Images, "a.png"));
        await vm.AddRootAsync(d.Images); await vm.ScanAsync(); vm.Selected = Assert.Single(vm.Images);
        vm.Note = "persist"; vm.Favorite = true; vm.Rating = 4;
        var saved = new GenerationLibraryStore(paths.GenerationLibrary).Query(new(FavoriteOnly: true)).Images.Single(); Assert.Equal("persist", saved.Annotation.Note);
        await vm.SendAsync(false); Assert.Equal(ForgeBridgeAction.SendOnly, bridge.Request!.Action); Assert.Equal(vm.Positive, bridge.Request.Positive); Assert.Equal("lowres", bridge.Request.Negative); Assert.Null(bridge.Request.Recipe); Assert.Equal("smile", main.English);
        await vm.SendAsync(true); Assert.Equal(ForgeBridgeAction.SendAndGenerate, bridge.Request!.Action); Assert.Null(bridge.Request.Recipe); Assert.Equal(ForgeNegativeMode.Replace, bridge.Request.NegativeMode);
        vm.RestorePrompt.Execute(null); Assert.Equal(vm.Positive, main.English); Assert.True(main.Workspace.HasRecovery); main.Workspace.Undo(); Assert.Equal("smile", main.English);
        var editorOpened = false; main.PresetsRequested += () => editorOpened = true;
        vm.CreatePreset.Execute(null); Assert.True(editorOpened); Assert.Equal(vm.Positive, main.PresetEditor.PresetPositive); Assert.Equal("sample", main.PresetEditor.PresetModel); Assert.Equal("42", main.PresetEditor.PresetSeed); Assert.Empty(main.Presets);
        main.PresetEditor.PresetName = "image preset"; main.PresetEditor.PresetWidth = "512"; main.PresetEditor.PresetHeight = "512"; main.PresetEditor.SavePreset.Execute(null);
        Assert.False(Assert.Single(main.Presets).Recipe!.HasAutomaticSettings);
        Assert.NotNull(memory.State); Assert.Equal("smile", main.English);
        main.StartDirect.Execute(null); Assert.False(vm.RestorePrompt.CanExecute(null)); await vm.SendAsync(false); Assert.Equal(2, bridge.Count);
    }
    [Fact]
    public async Task CacheIsBoundedReconstructibleAndInvalidatesOnFileChange()
    {
        using var d = new LibraryFixture(); var store = d.Store(); var root = store.AddRoot(d.Images); var path = Path.Combine(d.Images, "a.png"); Issue226LibraryFoundationTests.WritePng(path);
        new GenerationLibraryScanner(store, new PngGenerationMetadataReader()).Scan(root); var row = store.Query(new()).Images.Single();
        var cacheDir = Path.Combine(d.Path, "Cache"); var cache = new GenerationThumbnailCache(cacheDir);
        var thumb = await cache.GetAsync(row); Assert.NotNull(thumb); Assert.True(thumb.PixelWidth <= 256 && thumb.PixelHeight <= 256); Assert.True(thumb.IsFrozen);
        var file = Assert.Single(Directory.GetFiles(cacheDir, "*.png")); var before = File.GetLastWriteTimeUtc(file);
        Assert.NotNull(await cache.GetAsync(row)); Assert.Equal(before, File.GetLastWriteTimeUtc(file));
        File.WriteAllText(file, "corrupt cache"); Assert.NotNull(await cache.GetAsync(row)); Assert.Empty(Directory.GetFiles(cacheDir, "*.tmp"));
        Assert.NotEqual(cache.Key(row), cache.Key(row with { MtimeUtcTicks = row.MtimeUtcTicks + 1 }));
        Assert.Null(await cache.GetAsync(row with { Availability = "missing" }));
        Assert.Equal("OK", store.Query(new()).Images.Single().MetadataStatus);
    }
    [Fact]
    public async Task UiPagesNeverMaterializeTheWholeLibraryAndAnnotationSelectionIsCurrent()
    {
        using var d = new LibraryFixture(); var paths = new PortablePaths(d.Path); var main = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), paths: paths);
        var vm = main.GenerationLibrary!;
        for (var i = 0; i < 65; i++) Issue226LibraryFoundationTests.WritePng(Path.Combine(d.Images, $"{i}.png"));
        await vm.AddRootAsync(d.Images); await vm.ScanAsync(); Assert.Equal(60, vm.Images.Count); Assert.True(vm.Next.CanExecute(null));
        var first = vm.Images[0]; vm.Selected = first; vm.Note = "saved"; vm.Selected = vm.Images[1]; vm.Selected = first; Assert.Equal("saved", vm.Note);
        await vm.Next.ExecuteAsync(null); Assert.Equal(5, vm.Images.Count); Assert.False(vm.Next.CanExecute(null)); await vm.Previous.ExecuteAsync(null); Assert.Equal(60, vm.Images.Count);
    }
    [Fact]
    public async Task FailedAnnotationSaveKeepsInputAndBlocksSelectionOrCloseUntilCorrected()
    {
        using var d = new LibraryFixture(); var main = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), paths: new(d.Path));
        var vm = main.GenerationLibrary!;
        Issue226LibraryFoundationTests.WritePng(Path.Combine(d.Images, "a.png")); Issue226LibraryFoundationTests.WritePng(Path.Combine(d.Images, "b.png"));
        await vm.AddRootAsync(d.Images); await vm.ScanAsync(); vm.Selected = vm.Images[0]; var original = vm.Selected;
        vm.Rating = 9; vm.Note = "retain unsaved"; Assert.False(vm.FlushAnnotation()); vm.Selected = vm.Images[1]; Assert.Same(original, vm.Selected); Assert.Equal("retain unsaved", vm.Note);
        vm.Rating = 4; Assert.True(vm.FlushAnnotation()); vm.Selected = vm.Images[1]; vm.Selected = original; Assert.Equal("retain unsaved", vm.Note);
    }
    [Theory]
    [InlineData(".jpg")]
    [InlineData(".webp")]
    public async Task MultiFormatMetadataAndThumbnailFailureAreIsolated(string extension)
    {
        using var d = new LibraryFixture(); var path = Path.Combine(d.Images, "fixture" + extension);
        Issue226LibraryFoundationTests.WriteExif(path, Issue226LibraryFoundationTests.Info);
        var store = d.Store(); var root = store.AddRoot(d.Images); var scan = new GenerationLibraryScanner(store, new ExifGenerationMetadataReader()).Scan(root);
        Assert.Equal(1, scan.Added); Assert.Equal(0, scan.Errors); var row = store.Query(new()).Images.Single(); Assert.Equal("OK", row.MetadataStatus);
        var thumbnail = await new GenerationThumbnailCache(Path.Combine(d.Path, "cache")).GetAsync(row);
        if (extension == ".jpg") Assert.NotNull(thumbnail); // WebP depends on the OS WIC codec; unsupported decoding remains safe.
        Assert.Equal("42", store.Metadata(row.Id)!.Value("Seed"));
    }
    private sealed class RecordingBridge : IForgeBridgeClient
    {
        public ForgeBridgeSendRequest? Request; public int Count;
        public Task<ForgeBridgeResult> SendAsync(string baseUrl, ForgeBridgeSendRequest request, CancellationToken cancellationToken = default)
        { Count++; Request = request; return Task.FromResult(new ForgeBridgeResult(true, "ok")); }
    }
}
