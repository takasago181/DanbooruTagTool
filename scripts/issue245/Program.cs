using System.Buffers.Binary;
using System.IO;
using System.Reflection;
using System.Text;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Documents;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using DanbooruTagTool.App;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

// Development-only baseline audit. References unchanged product assemblies;
// never runs through normal App startup and never sends a Forge request.
internal static class Program
{
    private static string output = "";
    private static readonly List<object> renders = [];
    [STAThread]
    public static int Main(string[] args)
    {
        if (args.Length != 2) throw new ArgumentException("UiAudit <new-empty-output> <read-only-catalog>");
        output = Path.GetFullPath(args[0]);
        if (!Path.GetFileName(output).StartsWith(".staging-issue245-audit-", StringComparison.Ordinal)
            || Path.GetFullPath(args[1]).StartsWith(output + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)
            || (Directory.Exists(output) && Directory.EnumerateFileSystemEntries(output).Any()))
            throw new IOException("Use a new .staging-issue245-audit-* directory outside the catalog location.");
        Directory.CreateDirectory(output);
        var app = new App { ShutdownMode = ShutdownMode.OnExplicitShutdown };
        app.InitializeComponent();
        SynchronizationContext.SetSynchronizationContext(new DispatcherSynchronizationContext());
        var exitCode = 0;
        Dispatcher.CurrentDispatcher.BeginInvoke(async () =>
        {
            try { await Audit(args[1]); }
            catch (Exception e) { File.WriteAllText(Path.Combine(output, "error.txt"), e.ToString()); exitCode = 1; }
            finally { app.Shutdown(exitCode); Dispatcher.CurrentDispatcher.BeginInvokeShutdown(DispatcherPriority.Background); }
        });
        Dispatcher.Run();
        return exitCode;
    }
    private static async Task Audit(string catalogPath)
    {
        var catalog = CatalogDatabase.Open(catalogPath); // Existing production catalog opened read-only.
        var paths = new PortablePaths(output);
        var vm = new MainViewModel(catalog, new UserStateStore(paths.User), new AuditClipboard(), GeneralBrowseProvider.FromCatalog(catalog), specialBrowse: SpecialBrowseV2Overlay.FromCatalog(catalog), paths: paths);
        vm.Query = "blue_hair";
        vm.Workspace.Replace("1girl, blue_hair, smile, (looking_at_viewer:1.2), BREAK, <lora:sample:0.75>, raw example");
        vm.NegativeWorkspace.Replace("lowres, blurry, blue_hair");
        var images = Path.Combine(output, "Images"); Directory.CreateDirectory(images);
        var image = Path.Combine(images, "fixture.png");
        // Existing runtime validation fixture, rather than a new image codec/parser.
        typeof(GenerationLibraryValidation).GetMethod("WriteFixture", BindingFlags.NonPublic | BindingFlags.Static)!.Invoke(null,
            [image, "1girl, blue_hair, smile\nNegative prompt: lowres\nSteps: 20, Sampler: Euler a, Schedule type: Karras, CFG scale: 5, Seed: 42, Size: 512x768, Model: sample, Model hash: abc"]);
        await vm.GenerationLibrary!.AddRootAsync(images); await vm.GenerationLibrary.ScanAsync();
        vm.GenerationLibrary.Selected = vm.GenerationLibrary.Images.Single();
        var models = Path.Combine(output, "Models"); Directory.CreateDirectory(models);
        var metadata = Encoding.UTF8.GetBytes("{\"__metadata__\":{\"modelspec.architecture\":\"SDXL\",\"modelspec.trigger_phrase\":\"sample_trigger\"}}");
        using (var file = File.Create(Path.Combine(models, "sample.safetensors")))
        { var header = new byte[8]; BinaryPrimitives.WriteUInt64LittleEndian(header, (ulong)metadata.Length); file.Write(header); file.Write(metadata); }
        await vm.LoraLibrary!.AddRootAsync(models); await vm.LoraLibrary.ScanAsync(); vm.LoraLibrary.Selected = vm.LoraLibrary.Assets.Single();
        vm.LoraLibrary.Note = "Audit fixture / 日本語メモ";
        foreach (var size in new[] { (900, 600), (1280, 720), (1600, 900), (2560, 1440) })
        {
            var w = new MainWindow(vm) { Width = size.Item1, Height = size.Item2, WindowState = WindowState.Normal,
                Left = -30000, Top = -30000, ShowInTaskbar = false };
            w.Show(); w.Left = 0; w.Top = 0; w.Width = size.Item1; w.Height = size.Item2; await Task.Delay(200);
            foreach (var page in new[] { (0, 0, "dictionary"), (1, 0, "positive"), (1, 1, "negative"), (2, 0, "images"), (3, 0, "lora") })
            {
                vm.WorkspaceIndex = page.Item1; vm.Intelligence.ActiveSide = page.Item2;
                await Task.Delay(100); w.UpdateLayout();
                Capture(w, $"{page.Item3}-{size.Item1}x{size.Item2}", size.Item1, size.Item2);
            }
            w.Close();
        }
        vm.PresetEditor.BeginNewPreset(); vm.PresetEditor.CapturePresetPositive.Execute(null); vm.PresetEditor.CapturePresetNegative.Execute(null);
        var owner = new MainWindow(vm) { Width = 1280, Height = 720, WindowState = WindowState.Normal, Left = -30000, Top = -30000, ShowInTaskbar = false };
        owner.Show(); owner.Left = 0; owner.Top = 0; owner.Width = 1280; owner.Height = 720;
        foreach (var dialog in new Window[] { new GenerationPresetDialog(vm), new ForgeSettingsDialog(vm) })
        { var desiredWidth = dialog.Width; var desiredHeight = dialog.Height; dialog.Owner = owner; dialog.ShowInTaskbar = false; dialog.Show(); dialog.Left = 0; dialog.Top = 0; dialog.Width = desiredWidth; dialog.Height = desiredHeight; await Task.Delay(150); Capture(dialog, dialog.GetType().Name, (int)desiredWidth, (int)desiredHeight); dialog.Close(); }
        vm.GenerationImport.Load(ForgePngGenerationMetadata.Read(image));
        var import = new GenerationImportDialog(vm) { Owner = owner, ShowInTaskbar = false };
        import.Show(); await Task.Delay(150); Capture(import, "GenerationImportDialog", 920, 780); import.Close(); owner.Close();
        File.WriteAllText(Path.Combine(output, "renders.json"), JsonSerializer.Serialize(new { SourceBaseline = "a96dcd10d77e85d629e0169669ea26028f88c835", Mode = "Detached WPF client viewport / RenderTargetBitmap / 96 DPI; synthetic owned assets; read-only real catalog", Limitations = "No native pixel or pointer acceptance. Ancestor Window command bindings may be unavailable during detached capture; source inventory is authoritative for command semantics. Scroll descendants outside their viewport are not header overflow.", Screen = new { SystemParameters.PrimaryScreenWidth, SystemParameters.PrimaryScreenHeight, SystemParameters.VirtualScreenWidth, SystemParameters.VirtualScreenHeight }, NetworkCalls = 0, GenerationRequests = 0, Renders = renders }, new JsonSerializerOptions { WriteIndented = true }));
    }
    private static void Capture(Window window, string name, int width, int height)
    {
        window.UpdateLayout();
        // Capture a deliberately arranged client viewport, not a claim about native window pixels.
        var content = (FrameworkElement)window.Content;
        window.Content = null;
        var root = new Border { Child = content, DataContext = window.DataContext, Width = width, Height = height, Background = new SolidColorBrush(Color.FromRgb(244, 247, 250)) };
        TextElement.SetFontFamily(root, window.FontFamily); TextElement.SetFontSize(root, window.FontSize);
        TextElement.SetFontWeight(root, window.FontWeight); TextElement.SetForeground(root, window.Foreground);
        root.UseLayoutRounding = window.UseLayoutRounding; root.SnapsToDevicePixels = window.SnapsToDevicePixels;
        TextOptions.SetTextFormattingMode(root, TextOptions.GetTextFormattingMode(window));
        TextOptions.SetTextRenderingMode(root, TextOptions.GetTextRenderingMode(window));
        root.Resources.MergedDictionaries.Add(window.Resources);
        root.Measure(new Size(width, height)); root.Arrange(new Rect(0, 0, width, height)); root.UpdateLayout();
        if (Math.Abs(root.ActualWidth - width) > .5 || Math.Abs(root.ActualHeight - height) > .5) throw new InvalidDataException("Viewport arrangement failed");
        var bitmap = new RenderTargetBitmap(width, height, 96, 96, PixelFormats.Pbgra32); bitmap.Render(root);
        var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap));
        using (var f = File.Create(Path.Combine(output, name + ".png"))) encoder.Save(f);
        var tree = new List<object>(); Walk(root, root, tree);
        File.WriteAllText(Path.Combine(output, name + ".json"), "[\n" + string.Join(",\n", tree.Select(row => JsonSerializer.Serialize(row))) + "\n]\n");
        renders.Add(new { Name = name, Width = width, Height = height, NativeWidth = window.ActualWidth, NativeHeight = window.ActualHeight, WindowState = window.WindowState.ToString(), Controls = tree.Count });
        root.Child = null;
        window.Content = content;
    }
    private static void Walk(DependencyObject node, FrameworkElement root, List<object> tree)
    {
        if (node is FrameworkElement hidden && hidden.Visibility != Visibility.Visible) return;
        if (node is FrameworkElement e && e.ActualWidth > 0 && e.ActualHeight > 0
            && (e is ButtonBase or TextBox or ComboBox or TabControl or TabItem or GridSplitter or ScrollViewer or Expander || e.Name.Length > 0))
        {
            var p = e.TranslatePoint(new Point(), root);
            tree.Add(new { Type = e.GetType().Name, e.Name, Label = e is ContentControl c ? c.Content?.ToString() : e is HeaderedContentControl h ? h.Header?.ToString() : "", X = p.X, Y = p.Y, Width = e.ActualWidth, Height = e.ActualHeight, e.IsEnabled, RightOverflow = p.X + e.ActualWidth > root.ActualWidth + .5, BottomOverflow = p.Y + e.ActualHeight > root.ActualHeight + .5, Command = e is Button b ? b.Command?.GetType().Name : null });
        }
        for (var i = 0; i < VisualTreeHelper.GetChildrenCount(node); i++) Walk(VisualTreeHelper.GetChild(node, i), root, tree);
    }
    private sealed class AuditClipboard : IClipboardService { public string Read() => ""; public void Write(string value) { } }
}
