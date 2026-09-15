namespace DanbooruTagTool.App;

public static class ForgeBridgeInstaller
{
    private static readonly (string Source, string RelativeDestination)[] Files =
    [
        (Path.Combine("ForgeBridge", "scripts", "dtt_bridge.py"), Path.Combine("scripts", "dtt_bridge.py")),
        (Path.Combine("ForgeBridge", "javascript", "dtt_bridge.js"), Path.Combine("javascript", "dtt_bridge.js"))
    ];

    public static bool TryInstall(string selectedPath, out string message)
    {
        message = "";
        if (string.IsNullOrWhiteSpace(selectedPath)) { message = "Forgeのextensionsフォルダを指定してください"; return false; }
        string selected;
        try { selected = Path.GetFullPath(selectedPath.Trim()); }
        catch (Exception) { message = "Forgeのextensionsフォルダを確認してください"; return false; }
        var extensions = Path.GetFileName(selected.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)).Equals("extensions", StringComparison.OrdinalIgnoreCase)
            ? selected
            : Path.Combine(selected, "extensions");
        if (!Directory.Exists(extensions)) { message = "Forgeのextensionsフォルダを指定してください"; return false; }

        var destination = Path.Combine(extensions, "dtt_bridge");
        try
        {
            foreach (var file in Files)
            {
                var source = Path.Combine(AppContext.BaseDirectory, file.Source);
                if (!File.Exists(source)) { message = "連携拡張の同梱ファイルが見つかりません"; return false; }
                var target = Path.Combine(destination, file.RelativeDestination);
                Directory.CreateDirectory(Path.GetDirectoryName(target)!);
                File.Copy(source, target, true);
            }
            message = "Forge連携拡張を配置しました。Forgeを再起動してください。";
            return true;
        }
        catch (UnauthorizedAccessException) { message = "Forgeフォルダへの書き込み権限がありません"; return false; }
        catch (IOException ex) { message = "Forge連携拡張を配置できません: " + ex.Message; return false; }
    }
}
