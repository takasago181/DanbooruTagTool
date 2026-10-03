using System;
using System.Buffers.Binary;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App;

/// <summary>Explicit isolated acceptance hook for the actual portable executable. Never runs on normal startup.</summary>
public static class GenerationLibraryValidation
{
    public static async Task RunAsync(string outputDirectory)
    {
        var root = Path.GetFullPath(outputDirectory);
        if (Directory.Exists(root) && Directory.EnumerateFileSystemEntries(root).Any()) throw new IOException("Validation output must be a new empty directory; existing user data is protected.");
        Directory.CreateDirectory(root);
        var paths = new PortablePaths(root); var imageDir = Path.Combine(root, "Images"); Directory.CreateDirectory(imageDir);
        var imagePath = Path.Combine(imageDir, "fixture.png");
        const string info = "1girl, blue_hair, <lora:detail:0.75>\nNegative prompt: lowres\nSteps: 20, Sampler: Euler a, Schedule type: Karras, CFG scale: 5, Seed: 42, Size: 512x768, Model: sample, Model hash: abc, Extra: preserve";
        WriteFixture(imagePath, info);
        var bridge = new ProbeBridge(); var vm = new MainViewModel(new Catalog([]), new UserStateStore(paths.User), new ProbeClipboard(), forgeBridge: bridge, paths: paths);
        var library = vm.GenerationLibrary!;
        vm.Workspace.Replace("smile");
        await library.AddRootAsync(imageDir); await library.ScanAsync(); library.Selected = library.Images.Single();
        library.Favorite = true; library.Rating = 4; library.Note = "offline annotation 日本語";
        var store = new GenerationLibraryStore(paths.GenerationLibrary);
        Check(store.Query(new(FavoriteOnly: true, Seed: 42)).Total == 1, "SQL filters / annotation");
        Check(library.Selected.Thumbnail is { PixelWidth: <= 256, PixelHeight: <= 256 }, "bounded thumbnail");
        library.RestorePrompt.Execute(null); Check(vm.English == library.Positive, "Prompt restore"); vm.Workspace.Undo(); Check(vm.English == "smile", "Undo");
        library.CreatePreset.Execute(null); Check(vm.PresetEditor.PresetSeed == "42" && vm.Presets.Count == 0, "existing preset editor");
        await library.SendAsync(false); await library.SendAsync(true); Check(bridge.Count == 2 && bridge.Last is { Recipe: null } last && last.Positive == library.Positive, "existing Forge adapter / no recipe");
        var scanner = new GenerationLibraryScanner(store, GenerationMetadataReaders.CreateDefault());
        var warm = scanner.Scan(store.Roots().Single()); Check(warm.Unchanged == 1, "warm scan");
        library.SetCompareLeft.Execute(null); library.Compare.Execute(null); Check(library.Differences.All(d => d.State == "same"), "metadata diff");
        var fts = store.SupportsFts5();
        vm.WorkspaceIndex = 2;
        var window = new MainWindow(vm) { Width = 1400, Height = 900, Left = -30000, Top = -30000, ShowInTaskbar = false };
        window.Show(); await Task.Delay(150); window.UpdateLayout();
        var bitmap = new RenderTargetBitmap((int)Math.Ceiling(window.ActualWidth), (int)Math.Ceiling(window.ActualHeight), 96, 96, PixelFormats.Pbgra32); bitmap.Render(window);
        var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap));
        using (var output = File.Create(Path.Combine(root, "library-wpf.png"))) encoder.Save(output);
        var view = (FrameworkElement)window.FindName("GenerationLibraryWorkspace");
        var libraryBitmap = new RenderTargetBitmap((int)Math.Ceiling(view.ActualWidth), (int)Math.Ceiling(view.ActualHeight), 96, 96, PixelFormats.Pbgra32); libraryBitmap.Render(view);
        var libraryEncoder = new PngBitmapEncoder(); libraryEncoder.Frames.Add(BitmapFrame.Create(libraryBitmap));
        using (var output = File.Create(Path.Combine(root, "library-workspace-wpf.png"))) libraryEncoder.Save(output);
        window.Close();
        File.Delete(imagePath); var missing = scanner.Scan(store.Roots().Single()); Check(missing.Missing == 1 && store.Query(new(FavoriteOnly: true)).Images.Single().Annotation.Note.Contains("日本語"), "missing / user-owned preservation");
        store.Backup(Path.Combine(root, "library-backup.db"));
        File.WriteAllText(Path.Combine(root, "validation.json"), JsonSerializer.Serialize(new
        {
            Result = "PASS", Fts5Available = fts, NetworkCalls = 0, Framework = System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,
            Schema = GenerationLibraryStore.SchemaVersion, Warm = warm, Missing = missing, ForgeMockRequests = bridge.Count,
            WpfRender = "library-wpf.png", Scope = "isolated fixture / actual runtime; no production data writes; Forge rendering not invoked"
        }, new JsonSerializerOptions { WriteIndented = true }));
    }
    private static void Check(bool valid, string gate) { if (!valid) throw new InvalidDataException("Library validation failed: " + gate); }
    private static void WriteFixture(string path, string infotext)
    {
        var pixels = new byte[512 * 768 * 3];
        for (var i = 0; i < pixels.Length; i += 3) { pixels[i] = 170; pixels[i + 1] = 195; pixels[i + 2] = 225; }
        var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(BitmapSource.Create(512, 768, 96, 96, PixelFormats.Rgb24, null, pixels, 512 * 3)));
        using var buffer = new MemoryStream(); encoder.Save(buffer); var png = buffer.ToArray();
        using var s = File.Create(path); s.Write(png.AsSpan(0, png.Length - 12));
        var text = Encoding.Latin1.GetBytes("parameters\0" + infotext); var typeAndText = "tEXt"u8.ToArray().Concat(text).ToArray();
        Span<byte> length = stackalloc byte[4]; BinaryPrimitives.WriteInt32BigEndian(length, text.Length); s.Write(length); s.Write(typeAndText);
        uint crc = 0xffffffff;
        foreach (var b in typeAndText) { crc ^= b; for (var j = 0; j < 8; j++) crc = (crc >> 1) ^ ((crc & 1) == 0 ? 0u : 0xedb88320u); }
        BinaryPrimitives.WriteUInt32BigEndian(length, ~crc); s.Write(length); s.Write(png.AsSpan(png.Length - 12));
    }
    private sealed class ProbeClipboard : IClipboardService { public string Read() => ""; public void Write(string text) { } }
    private sealed class ProbeBridge : IForgeBridgeClient
    {
        public int Count; public ForgeBridgeSendRequest? Last;
        public Task<ForgeBridgeResult> SendAsync(string baseUrl, ForgeBridgeSendRequest request, CancellationToken cancellationToken = default)
        { Count++; Last = request; return Task.FromResult(new ForgeBridgeResult(true, "isolated bridge probe")); }
    }
}
