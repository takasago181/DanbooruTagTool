using System.Text.Json;

namespace DanbooruTagTool.Data;

/// <summary>Atomic local JSON replacement. Domain owners validate before calling;
/// this helper supplies no schema, semantic authority, or recovery policy.</summary>
internal static class AtomicJsonFile
{
    public static void Write<T>(string path, T value, JsonSerializerOptions? options = null)
    {
        var json = JsonSerializer.Serialize(value, options);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        var temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            File.WriteAllText(temporary, json);
            if (File.Exists(path)) File.Replace(temporary, path, path + ".bak");
            else File.Move(temporary, path);
        }
        finally
        {
            if (File.Exists(temporary)) File.Delete(temporary);
        }
    }
}
