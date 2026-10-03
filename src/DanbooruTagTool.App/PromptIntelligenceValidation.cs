using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App;

/// <summary>Actual executable acceptance with isolated UserData; no generation or network.</summary>
public static class PromptIntelligenceValidation
{
    public static async Task RunAsync(string outputDirectory)
    {
        var root = Path.GetFullPath(outputDirectory);
        if (Directory.Exists(root) && Directory.EnumerateFileSystemEntries(root).Any()) throw new IOException("Validation requires a new empty directory.");
        Directory.CreateDirectory(root); var paths = new PortablePaths(root);
        var catalog = new Catalog([new CatalogEntry("G:blue_hair", "blue_hair", "blue_hair", "青い髪", false, 1, ["azure_locks"], [], [], "KEEP")]);
        var bridge = new ProbeBridge(); var store = new UserStateStore(paths.User); var vm = new MainViewModel(catalog, store, new ProbeClipboard(), forgeBridge: bridge, paths: paths);
        vm.Workspace.Replace("azure_locks BREAK (blue_hair:1.2), raw"); vm.NegativeWorkspace.Replace("blue_hair, lowres");
        Check(vm.Intelligence.Warnings.Any(w => w.Code == "conflict") && vm.Intelligence.Warnings.Any(w => w.Code == "duplicate"), "canonical warnings");
        var positive = vm.English; var negative = vm.Negative.English;
        vm.Negative.StartDirect.Execute(null); vm.Negative.DirectText = "lowres AND <lora:detail:0.75>"; vm.Negative.ApplyDirect.Execute(null);
        vm.Negative.Undo.Execute(null); Check(vm.Negative.English == negative && vm.English == positive, "independent Undo"); vm.Negative.Redo.Execute(null);
        await vm.Forge.SendWorkspacePair.ExecuteAsync(null); Check(bridge.Last is { NegativeMode: ForgeNegativeMode.Replace } && bridge.Last.Negative == vm.Negative.English, "explicit pair send");
        var preset = new GenerationPreset(Guid.NewGuid(), "fixture", "", "positive", "blue_hair, lowres"); vm.PresetEditor.ApplyPresetNegative.Execute(preset);
        var restored = new MainViewModel(catalog, new UserStateStore(paths.User), new ProbeClipboard(), paths: paths);
        Check(restored.Negative.English == preset.Negative && restored.English == positive, "versioned persistence");
        foreach (var width in new[] { 900, 1400 })
        {
            vm.WorkspaceIndex = 1; vm.Intelligence.ActiveSide = 1;
            var window = new MainWindow(vm) { Width = width, Height = width == 900 ? 600 : 900, WindowState = WindowState.Normal, Left = -30000, Top = -30000, ShowInTaskbar = false };
            window.Show(); await Task.Delay(150); window.UpdateLayout();
            var sides = (TabControl)window.FindName("PromptSides"); Check(sides.SelectedIndex == 1, "Negative tab binding");
            var editor = (FrameworkElement)window.FindName("NegativeEditor"); Check(editor.IsVisible && editor.ActualWidth > 500 && editor.ActualHeight > 150, "Negative layout");
            var bitmap = new RenderTargetBitmap((int)Math.Ceiling(window.ActualWidth), (int)Math.Ceiling(window.ActualHeight), 96, 96, PixelFormats.Pbgra32); bitmap.Render(window);
            var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap)); using (var file = File.Create(Path.Combine(root, $"negative-wpf-{width}.png"))) encoder.Save(file);
            vm.Create.Load(new(Guid.NewGuid(), "hash fixture", "", positive, negative,
                new("sample", 42, 20, "Euler", "Karras", 5, 512, 768, "abcdef1234")), "画像fixture");
            vm.CreatePageIndex = 2; window.UpdateLayout();
            var hashInput = Descendants(window).OfType<TextBox>().Single(e => System.Windows.Automation.AutomationProperties.GetName(e) == "現在Model hash");
            Check(hashInput.IsVisible && hashInput.IsEnabled && hashInput.Text == "abcdef1234" && hashInput.ActualWidth > 100, "editable Model hash binding/layout");
            var conditions = new RenderTargetBitmap((int)Math.Ceiling(window.ActualWidth), (int)Math.Ceiling(window.ActualHeight), 96, 96, PixelFormats.Pbgra32); conditions.Render(window);
            var conditionsEncoder = new PngBitmapEncoder(); conditionsEncoder.Frames.Add(BitmapFrame.Create(conditions)); using (var file = File.Create(Path.Combine(root, $"recipe-hash-wpf-{width}.png"))) conditionsEncoder.Save(file);
            vm.CreatePageIndex = 0; window.Close();
        }
        File.WriteAllText(Path.Combine(root, "validation.json"), JsonSerializer.Serialize(new { Result = "PASS", Schema = UserStateStore.SchemaVersion, NetworkCalls = 0, GenerationRequests = 0, BridgeMockRequests = 1, Widths = new[] { 900, 1400 }, Scope = "actual executable WPF / isolated versioned UserData / Positive-Negative / Undo / preset / explicit send" }));
    }
    private static void Check(bool pass, string gate) { if (!pass) throw new InvalidDataException("Prompt intelligence validation: " + gate); }
    private static IEnumerable<DependencyObject> Descendants(DependencyObject parent)
    {
        for (var i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
        { var child = VisualTreeHelper.GetChild(parent, i); yield return child; foreach (var descendant in Descendants(child)) yield return descendant; }
    }
    private sealed class ProbeClipboard : IClipboardService { public string Read() => ""; public void Write(string value) { } }
    private sealed class ProbeBridge : IForgeBridgeClient { public ForgeBridgeSendRequest? Last; public Task<ForgeBridgeResult> SendAsync(string url, ForgeBridgeSendRequest request, CancellationToken ct = default) { Last = request; return Task.FromResult(new ForgeBridgeResult(true, "probe")); } }
}
