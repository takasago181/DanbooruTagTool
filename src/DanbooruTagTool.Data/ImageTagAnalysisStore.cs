using System.Diagnostics;
using System.Text.Json;
using DanbooruTagTool.Core;
namespace DanbooruTagTool.Data;
public sealed class ImageTagAnalysisStore(string root)
{
    private string DirectoryPath => Path.Combine(root,"UserData","ImageTagAnalysis");
    public TaggerProfile? LoadProfile()
    { var p=Path.Combine(DirectoryPath,"profile.json"); var profile = File.Exists(p) ? JsonSerializer.Deserialize<TaggerProfile>(File.ReadAllText(p)) : null; if (profile is not null && profile.Version != 1) throw new InvalidDataException("未対応tagger profile version。"); return profile; }
    public void SaveProfile(TaggerProfile profile) { _ = LoadProfile(); Save("profile.json",profile); }
    public void SaveResult(TagAnalysis result) => Save(result.ImageSha256 + "-" + Guid.NewGuid().ToString("N") + ".json",result);
    public TagAnalysis? Latest(string imageSha256) => Directory.Exists(DirectoryPath) ? Directory.GetFiles(DirectoryPath,imageSha256 + "-*.json").Select(p => JsonSerializer.Deserialize<TagAnalysis>(File.ReadAllText(p))).Where(r => r is { Version:1 }).OrderByDescending(r => r!.AnalyzedUtc).FirstOrDefault() : null;
    private void Save<T>(string name,T value)
    {
        Directory.CreateDirectory(DirectoryPath); var path=Path.Combine(DirectoryPath,name); var temp=path+".tmp";
        try { File.WriteAllText(temp,JsonSerializer.Serialize(value)); if(File.Exists(path)) File.Replace(temp,path,path+".bak"); else File.Move(temp,path); }
        finally { if(File.Exists(temp)) File.Delete(temp); }
    }
    public static async Task<TaggerProfile> DiscoverMoatAsync(string forgeRoot)
    {
        var extension=Path.Combine(forgeRoot,"extensions","stable-diffusion-webui-wd14-tagger");
        var manifest=Path.Combine(forgeRoot,"models","interrogators","model.json");
        using var json=JsonDocument.Parse(await File.ReadAllTextAsync(manifest));
        var entry=json.RootElement.EnumerateArray().Single(e => e.GetProperty("name").GetString()=="WD14 moat tagger v2");
        var model=entry.GetProperty("model_path").GetString()!; var tags=entry.GetProperty("tags_path").GetString()!;
        var revision=Path.GetFileName(Path.GetDirectoryName(model))!;
        var start=new ProcessStartInfo("git") { RedirectStandardOutput=true,RedirectStandardError=true,UseShellExecute=false,CreateNoWindow=true };
        start.ArgumentList.Add("-C"); start.ArgumentList.Add(extension); start.ArgumentList.Add("rev-parse"); start.ArgumentList.Add("HEAD");
        using var process=Process.Start(start) ?? throw new IOException("git起動不可。"); var commit=(await process.StandardOutput.ReadToEndAsync()).Trim(); await process.WaitForExitAsync();
        if(process.ExitCode!=0 || commit.Length!=40) throw new IOException("tagger実装version取得不可。");
        return new("wd-v1-4-moat-tagger.v2","WD14 moat tagger v2","https://huggingface.co/SmilingWolf/wd-v1-4-moat-tagger-v2",revision,model,await LocalTaggerClient.HashAsync(model),tags,await LocalTaggerClient.HashAsync(tags),manifest,"https://github.com/hirorohi03/stable-diffusion-webui-wd14-tagger",commit,"Implementation: README public domain except borrowed parts; model: Apache-2.0");
    }
}
