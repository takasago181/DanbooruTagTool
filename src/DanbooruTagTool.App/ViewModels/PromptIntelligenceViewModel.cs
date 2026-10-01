using System.Collections.ObjectModel;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.App.ViewModels;

public sealed class PromptIntelligenceViewModel(PromptWorkspace positive, PromptWorkspace negative, Func<string> forgeUrl, IForgeTokenCounter? counter = null, Func<string>? positiveText = null, Func<string>? negativeText = null) : Observable
{
    private readonly IForgeTokenCounter counter = counter ?? new ForgeTokenCounter();
    private string tokenStatus = "Token count未取得。モデル/tokenizer不明のローカル推定はしません。BREAK/ANDは構文境界のみ表示します。";
    private bool busy; private int revision, activeSide;
    public ObservableCollection<PromptWarning> Warnings { get; } = [];
    public ObservableCollection<PromptBoundary> Boundaries { get; } = [];
    public string TokenStatus { get => tokenStatus; private set => Set(ref tokenStatus, value); }
    public int Steps { get; set; } = 20;
    public int ActiveSide { get => activeSide; set => Set(ref activeSide, value); }
    public bool Busy { get => busy; private set => Set(ref busy, value); }
    public void Refresh()
    {
        revision++; Warnings.Clear(); foreach (var w in PromptDiagnostics.Warnings(positive, negative)) Warnings.Add(w);
        Boundaries.Clear(); foreach (var b in PromptDiagnostics.Boundaries(positive, "Positive").Concat(PromptDiagnostics.Boundaries(negative, "Negative"))) Boundaries.Add(b);
        TokenStatus = "Prompt変更後のtoken count未取得。BREAK/ANDは構文境界です。モデル依存chunkはForge照会後に表示します。";
    }
    public async Task CountAsync()
    {
        if (Busy) return; Busy = true; var version = revision; var url = forgeUrl(); var steps = Steps;
        try
        {
            var p = await counter.CountAsync(url, positiveText?.Invoke() ?? positive.English, false, steps); var n = await counter.CountAsync(url, negativeText?.Invoke() ?? negative.English, true, steps);
            if (version != revision || url != forgeUrl() || steps != Steps) { TokenStatus = "照会中にPrompt/URL/Stepsが変わりました。件数を採用せず再照会してください。"; return; }
            if (p.Available && n.Available && (p.Model != n.Model || p.ModelHash != n.ModelHash || p.Engine != n.Engine || p.Tokenizer != n.Tokenizer)) { TokenStatus = "照会中のモデル/tokenizer変更。両側の件数を採用しません。"; return; }
            TokenStatus = Describe("Positive", p) + "\n" + Describe("Negative", n);
        }
        finally { Busy = false; }
    }
    private static string Describe(string side, ForgeTokenCount r) => !r.Available ? side + ": 取得不可 — " + r.Status : $"{side}: {r.Count}/{r.Capacity} tokens · " + (r.Chunks is { } chunks ? $"{chunks} chunks × {r.ChunkLength} · " : "chunk contract未公開 · ") + $"{r.Model} [{r.ModelHash}] / {r.Engine} / {r.Tokenizer} / {r.Status}";
}
