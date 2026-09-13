using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using DanbooruTagTool.App.ViewModels;

namespace DanbooruTagTool.Tests;
internal static class Fixtures
{
    public static readonly BrowsePath HairPath = new("APPEARANCE", "容姿", "HAIR", "髪");
    public static CatalogEntry Entry(string canonical, string japanese, long usage = 10, string[]? aliases = null, bool special = false, string fit = "KEEP") =>
        new((special ? "S:" : "G:") + canonical, canonical, canonical, japanese, special, usage, aliases ?? [], [], special ? [HairPath] : [], fit);
    public static Catalog Catalog() => new([
        Entry("blue_hair", "青い髪", 100, ["azure_locks"], true), Entry("red_hair", "赤い髪", 500),
        Entry("long_hair", "長い髪", 1000), Entry("anal", "アナル", 100, ["anal_sex"]),
        Entry("anal_focus", "肛門に焦点", 90), Entry("piano", "ピアノ", 10000000), Entry("analog_clock", "アナログ時計", 1000000),
        Entry("smile", "笑顔", 5000), Entry("forbidden", "除外", 999, fit: "OUT_OF_SCOPE_PRODUCT"),
        new("S:semantic", null, "semantic concept", "意味だけの入口", true, null, [], [], [HairPath])]);
    public static PromptWorkspace Workspace() => new(new(Catalog()));
    public static MainViewModel Vm(MemoryStore? store = null, MemoryClipboard? clipboard = null) => new(Catalog(), store ?? new(), clipboard ?? new());
}
internal sealed class MemoryStore : IUserStateStore
{
    public UserState? State;
    public UserState? Load() => State;
    public void Save(UserState state) => State = state;
}
internal sealed class MemoryClipboard : IClipboardService
{
    public string Value = "";
    public string Read() => Value;
    public void Write(string text) => Value = text;
}
internal sealed class TempDirectory : IDisposable
{
    public string Path { get; } = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "DanbooruTagToolTests", Guid.NewGuid().ToString());
    public TempDirectory() => Directory.CreateDirectory(Path);
    public void Dispose() => Directory.Delete(Path, true);
}
