using System.Globalization;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.App.ViewModels;

// Shared input validation for saved preset drafts and the working Create snapshot.
// Execution capabilities and actual metadata verification remain in the #228 adapter.
internal static class GenerationRecipeInput
{
    public static bool TryBuild(string model, string seed, string steps, string sampler, string scheduler,
        string cfg, string width, string height, out GenerationRecipe? recipe, out string error)
    {
        recipe = null; error = "";
        long? s = null; int? st = null, w = null, h = null; decimal? c = null;
        if (!string.IsNullOrWhiteSpace(seed))
        {
            if (!long.TryParse(seed.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out var parsed)) { error = "Seedは整数で入力してください"; return false; }
            s = parsed;
        }
        bool Integer(string text, string label, int min, int max, out int? value)
        {
            value = null; if (string.IsNullOrWhiteSpace(text)) return true;
            if (!int.TryParse(text.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out var n) || n < min || n > max) return false;
            value = n; return true;
        }
        if (!Integer(steps, "Steps", 1, 150, out st)) { error = "Stepsは1〜150の整数で入力してください"; return false; }
        if (!string.IsNullOrWhiteSpace(cfg))
        {
            if (!decimal.TryParse(cfg.Trim(), NumberStyles.Number, CultureInfo.InvariantCulture, out var n) || n < 1 || n > 30) { error = "CFGは1〜30の数値で入力してください"; return false; }
            c = n;
        }
        if (!Integer(width, "Width", 64, 2048, out w)) { error = "Widthは64〜2048の整数で入力してください"; return false; }
        if (!Integer(height, "Height", 64, 2048, out h)) { error = "Heightは64〜2048の整数で入力してください"; return false; }
        static string? Clean(string s) => string.IsNullOrWhiteSpace(s) ? null : s.Trim();
        var r = new GenerationRecipe(Clean(model), s, st, Clean(sampler), Clean(scheduler), c, w, h);
        recipe = r.HasAny ? r : null; return true;
    }
}
