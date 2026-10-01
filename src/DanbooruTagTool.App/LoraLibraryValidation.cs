using System.Buffers.Binary;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App;

/// <summary>Explicit disposable actual-runtime acceptance. No existing LoRA/UserData changes.</summary>
public static class LoraLibraryValidation
{
    public static async Task RunAsync(string outputDirectory)
    {
        var root = Path.GetFullPath(outputDirectory);
        if (Directory.Exists(root) && Directory.EnumerateFileSystemEntries(root).Any()) throw new IOException("Validation needs a new empty directory.");
        Directory.CreateDirectory(root); var models = Path.Combine(root, "Models"); Directory.CreateDirectory(models);
        var model = Path.Combine(models, "sample.safetensors"); var data = Encoding.UTF8.GetBytes("{\"__metadata__\":{\"modelspec.architecture\":\"SDXL\",\"modelspec.trigger_phrase\":\"sample_trigger\"}}");
        using (var file = File.Create(model)) { var header = new byte[8]; BinaryPrimitives.WriteUInt64LittleEndian(header, (ulong)data.Length); file.Write(header); file.Write(data); }
        var paths = new PortablePaths(root); var vm = new MainViewModel(new Catalog([]), new UserStateStore(paths.User), new ProbeClipboard(), paths: paths);
        var library = vm.LoraLibrary!; await library.AddRootAsync(models); await library.ScanAsync(); library.Selected = library.Assets.Single();
        library.Category = "Character"; library.Note = "ユーザーメモ"; library.Weight = "0.75"; library.Favorite = true; library.NegativeAdditions = "lowres"; library.Save();
        vm.Workspace.Replace("original"); library.Insert(true); Check(vm.English.Contains("<lora:sample:0.75>") && vm.English.Contains("sample_trigger"), "Prompt insertion");
        vm.Workspace.Undo(); Check(vm.English == "original", "Undo"); library.CreatePreset(); Check(vm.PresetEditor.PresetNegative == "lowres", "existing preset editor");
        var store = new LoraLibraryStore(Path.Combine(root, "UserData", "lora-library.db")); Check(store.Scan(models).Hashed == 0 && store.Query(favoriteOnly: true).Single().User.Note == "ユーザーメモ", "persist/warm scan");
        vm.WorkspaceIndex = 3; var window = new MainWindow(vm) { Width = 1200, Height = 800, Left = -30000, Top = -30000, ShowInTaskbar = false };
        window.Show(); await Task.Delay(150); window.UpdateLayout();
        var view = (FrameworkElement)window.FindName("LoraLibraryWorkspace"); Check(view.ActualWidth > 500 && view.ActualHeight > 300, "LoRA view layout");
        var bitmap = new RenderTargetBitmap((int)Math.Ceiling(view.ActualWidth), (int)Math.Ceiling(view.ActualHeight), 96, 96, PixelFormats.Pbgra32); bitmap.Render(view);
        var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap)); using (var file = File.Create(Path.Combine(root, "lora-workspace-wpf.png"))) encoder.Save(file); window.Close();
        File.Delete(model); store.Scan(models); Check(store.Query().Single() is { Available: false, User.Note: "ユーザーメモ" }, "missing notes preservation");
        File.WriteAllText(Path.Combine(root, "validation.json"), JsonSerializer.Serialize(new { Result = "PASS", Schema = LoraLibraryStore.SchemaVersion, NetworkCalls = 0, WpfRender = "lora-workspace-wpf.png", Scope = "isolated safetensors fixture, actual portable WPF/DB/workspace/preset, no generation" }));
    }
    private static void Check(bool pass, string gate) { if (!pass) throw new InvalidDataException("LoRA validation: " + gate); }
    private sealed class ProbeClipboard : IClipboardService { public string Read() => ""; public void Write(string value) { } }
}
