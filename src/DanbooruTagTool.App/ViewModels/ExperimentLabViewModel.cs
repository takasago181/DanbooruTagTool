using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

public sealed record ExperimentChoice(Guid Id, string Name);
public sealed record ExperimentVariant(int Index, string Label);
public sealed record ExperimentCell(ExperimentTrial Trial, ExperimentAttempt Attempt, string XLabel, string YLabel)
{
    public string? ImagePath => Attempt.Receipt?.ImagePath;
    public string Label => $"X{Trial.X + 1}: {XLabel}\nY{Trial.Y + 1}: {YLabel}\nseed {Trial.Seed} /反復{Trial.Repetition + 1} /run{Attempt.RunNumber}";
    public string Status => Attempt.Status == "Running" ? "Running /中断時は結果不明（自動再送なし）" : Attempt.Status;
    public string EvaluationLabel => $"★{Attempt.Evaluation?.Rating?.ToString() ?? "-"} /{Attempt.Evaluation?.Passed?.ToString() ?? "未評価"}" + (Attempt.Evaluation?.Winner == true ? " /Winner" : "");
}

/// <summary>Lab owns plans/attempts/evaluations; shared Create, Recipe executor and Library remain execution owners.</summary>
public sealed class ExperimentLabViewModel : Observable
{
    private readonly MainViewModel main;
    private readonly PortablePaths paths;
    private ExperimentStore? store;
    private RecipeSnapshot? baseline;
    private ExperimentPlan? plan;
    private CancellationTokenSource? cancel;
    private bool busy;
    private string name = "新しい実験", hypothesis = "", xValues = "4\n6", yValues = "8\n12", xTarget = "", yTarget = "", seeds = "1\n2";
    private ExperimentVariable xKind = ExperimentVariable.Cfg, yKind = ExperimentVariable.Steps;
    private bool useY, consent;
    private int repetitions = 1;
    private string status = "Createの条件を明示的にbaselineへ取り込んでください。起動時には通信しません。";
    public string Status { get => status; private set => Set(ref status, value); }
    public bool Busy => busy;
    public bool CanEdit => !busy && !main.Forge.RecipeBusy;
    public bool ConsentUnapplied { get => consent; set { Set(ref consent, value); Refresh(); } }
    public string Name { get => name; set { Set(ref name, value); PreviewChanged(); } }
    public string Hypothesis { get => hypothesis; set { Set(ref hypothesis, value); PreviewChanged(); } }
    public ExperimentVariable XKind { get => xKind; set { Set(ref xKind, value); PreviewChanged(); } }
    public ExperimentVariable YKind { get => yKind; set { Set(ref yKind, value); PreviewChanged(); } }
    public string XTarget { get => xTarget; set { Set(ref xTarget, value); PreviewChanged(); } }
    public string YTarget { get => yTarget; set { Set(ref yTarget, value); PreviewChanged(); } }
    public string XValues { get => xValues; set { Set(ref xValues, value); PreviewChanged(); } }
    public string YValues { get => yValues; set { Set(ref yValues, value); PreviewChanged(); } }
    public string Seeds { get => seeds; set { Set(ref seeds, value); PreviewChanged(); } }
    public int Repetitions { get => repetitions; set { Set(ref repetitions, value); PreviewChanged(); } }
    public bool UseY { get => useY; set { Set(ref useY, value); PreviewChanged(); } }
    public IReadOnlyList<ExperimentVariable> Variables { get; } = Enum.GetValues<ExperimentVariable>();
    public string BaselineSummary => baseline is null ? "baseline未取込" : $"Recipe {GenerationRecipeDerivation.Identity(baseline)}\n{baseline.Recipe.Summary}\n{GenerationLoraProvenance.Summary(baseline.Recipe.SourceParameters)}\nP: {baseline.Positive}\nN: {baseline.Negative}";
    private RegionComposerConfig? regionalComparison;
    public async Task LoadRegionalComparisonAsync(RegionComposerConfig config)
    {
        if (!CanEdit || !main.CanEditPrompt || main.PresetManagementOpen) throw new InvalidOperationException("Lab is busy.");
        RegionComposer.Validate(config);
        if (!main.Create.TryRecipe(out var recipe, out var error)) throw new ArgumentException(error);
        var ordinary = RegionComposer.Ordinary(config);
        recipe = GenerationRecipeDerivation.Strip(recipe!) with { Regional = null };
        // Prior image regional observations are preserved by the image/parent, not reused as new ordinary overrides.
        recipe = recipe with { SourceParameters = (recipe.SourceParameters ?? []).Where(p => p.Name != RegionComposer.Key && !p.Name.StartsWith("RP ", StringComparison.Ordinal)).ToArray() };
        main.Forge.BeginExperiment(); busy = true; Refresh();
        try
        {
            await main.Forge.ReadRegionalCapabilitiesAsync();
            baseline = await main.Forge.PinExperimentBaselineAsync(new(ordinary.Positive, ordinary.Negative, recipe));
            regionalComparison = config;
            Name = "Ordinary vs Region Composer"; Hypothesis = "Human assessment: attribute leakage / subject fidelity / composition";
            XKind = ExperimentVariable.RegionalMode; XTarget = ""; XValues = "Ordinary\n" + config.Layout;
            UseY = false; Repetitions = 1;
            Seeds = recipe.Seed?.ToString(CultureInfo.InvariantCulture) ?? "";
            Notify(nameof(BaselineSummary)); PreviewChanged(); Status = "同じblocks / model / LoRA / seedの比較draft。保存後、Startで2画像生成します。";
        }
        finally { busy = false; main.Forge.EndExperiment(); Refresh(); }
    }
    private ExperimentSetup Draft()
    {
        if (baseline is null) throw new ArgumentException("baselineを取り込んでください。");
        static string[] Lines(string s, bool literal = false) => s.Replace("\r\n", "\n").Split('\n').Select(v => literal ? v : v.Trim()).Where(v => !string.IsNullOrWhiteSpace(v)).ToArray();
        var explicitSeeds = Lines(Seeds).Select(v => long.TryParse(v, NumberStyles.None, CultureInfo.InvariantCulture, out var n) ? n : throw new ArgumentException("seedは1行1個の非負整数です。")).ToArray();
        return new(Name, Hypothesis, baseline, new(XKind, XTarget, Lines(XValues, XKind is ExperimentVariable.Positive or ExperimentVariable.Negative)), UseY ? new(YKind, YTarget, Lines(YValues, YKind is ExperimentVariable.Positive or ExperimentVariable.Negative)) : null, explicitSeeds, Repetitions, ConsentUnapplied, regionalComparison);
    }
    public string Preview
    {
        get { try { var p = ExperimentPlanner.Build(Draft()); return $"{p.Setup.X.Values.Count} X ×{p.Setup.Y?.Values.Count ?? 1} Y ×{p.Setup.Seeds.Count} seeds ×{p.Setup.Repetitions}反復 = {p.Trials.Count}生成（上限{ExperimentPlanner.MaxTrials}）。保存してから明示Start。"; } catch (Exception e) when (e is ArgumentException or InvalidDataException or OverflowException) { return e.Message; } }
    }
    public ObservableCollection<ExperimentChoice> Experiments { get; } = [];
    public ObservableCollection<ExperimentCell> Cells { get; } = [];
    public ObservableCollection<long> SeedChoices { get; } = [];
    public ObservableCollection<int> RunChoices { get; } = [];
    private ExperimentChoice? selectedExperiment;
    public ExperimentChoice? SelectedExperiment { get => selectedExperiment; set { if (busy) return; Set(ref selectedExperiment, value); if (value is not null) Guard(() => Open(value.Id)); } }
    private long selectedSeed;
    public long SelectedSeed { get => selectedSeed; set { Set(ref selectedSeed, value); Filter(); } }
    private int selectedRun, selectedRepetition;
    public int SelectedRun { get => selectedRun; set { Set(ref selectedRun, value); Filter(); } }
    public int SelectedRepetition { get => selectedRepetition; set { Set(ref selectedRepetition, value); Filter(); } }
    public IReadOnlyList<ExperimentVariant> RepetitionChoices => Enumerable.Range(0, plan?.Setup.Repetitions ?? 1).Select(i => new ExperimentVariant(i, $"反復{i + 1}")).ToArray();
    private ExperimentCell? selected;
    public ExperimentCell? Selected { get => selected; set { Set(ref selected, value); Rating = value?.Attempt.Evaluation?.Rating; Passed = value?.Attempt.Evaluation?.Passed; Winner = value?.Attempt.Evaluation?.Winner ?? false; Note = value?.Attempt.Evaluation?.Note ?? ""; Notify(nameof(SelectedDetails)); Refresh(); } }
    public int? Rating { get; set; }
    public bool? Passed { get; set; }
    public bool Winner { get; set; }
    public string Note { get; set; } = "";
    private ExperimentCell? compareLeft;
    public string ObservedDirection { get; set; } = "";
    public string Exceptions { get; set; } = "";
    public string SelectedDetails => Selected is not { } c ? "セルを選択してください。" :
        $"Trial {c.Trial.Id}\nAttempt/request id {c.Attempt.Id}\nLibrary image {c.Attempt.LibraryImageId}\n{c.Attempt.Receipt?.Status}\n{GenerationRecipeDerivation.Summary(c.Trial.Requested.Recipe.SourceParameters)}\nActual LoRA:\n{GenerationLoraProvenance.Summary(c.Attempt.Receipt?.Metadata?.Parameters)}\n{Comparison}\nActual PNG/receipt:\n{c.Attempt.Receipt?.Metadata?.RawInfotext}";
    private string Comparison => compareLeft?.Attempt.Receipt?.Metadata is not { } left || Selected?.Attempt.Receipt?.Metadata is not { } right ? "比較元の画像を選び「比較元にする」を押してください。" :
        $"比較: Library {compareLeft.Attempt.LibraryImageId} /seed {compareLeft.Trial.Seed} → Library {Selected.Attempt.LibraryImageId} /seed {Selected.Trial.Seed}\n" +
        string.Join("\n", GenerationMetadataDiff.Compare(left, right).Where(d => d.Field is "Positive" or "Negative" or "Model" or "Model hash" or "Seed" or "Steps" or "Sampler" or "Scheduler" or "CFG" or "Size" or "LoRA" || d.Field.StartsWith("RP ") || d.Field == RegionComposer.Key).Select(d => $"{d.Field}: {d.Left} → {d.Right} [{d.State}]"));
    public string SelectedSummary => plan is null ? "保存済み実験未選択" : $"保存済み「{plan.Setup.Name}」: {plan.Trials.Count}生成 /未実行{(attempts.Count == 0 ? plan.Trials.Count : attempts.Count(a => a.RunNumber == selectedRun && a.Status == "Pending"))}。編集の反映は新規保存で。";
    public int Columns => xFilter >= 0 ? 1 : plan?.Setup.X.Values.Count ?? 1;
    public int MatrixWidth => Columns * 190;
    public IReadOnlyList<ExperimentVariant> XVariants => new[] { new ExperimentVariant(-1, "すべて") }.Concat((plan?.Setup.X.Values ?? []).Select((v, i) => new ExperimentVariant(i, $"X{i + 1}: {v}"))).ToArray();
    public IReadOnlyList<ExperimentVariant> YVariants => new[] { new ExperimentVariant(-1, "すべて") }.Concat((plan?.Setup.Y?.Values ?? []).Select((v, i) => new ExperimentVariant(i, $"Y{i + 1}: {v}"))).ToArray();
    private int xFilter = -1, yFilter = -1;
    public int XFilter { get => xFilter; set { Set(ref xFilter, value); Notify(nameof(Columns)); Notify(nameof(MatrixWidth)); Filter(); } }
    public int YFilter { get => yFilter; set { Set(ref yFilter, value); Filter(); } }
    public AsyncRelayCommand CaptureBaseline { get; }
    public RelayCommand Save { get; }
    public RelayCommand Reload { get; }
    public RelayCommand Evaluate { get; }
    public RelayCommand SaveObservation { get; }
    public RelayCommand ExportEvidence { get; }
    public RelayCommand UseInCreate { get; }
    public RelayCommand SetCompareLeft { get; }
    public RelayCommand MarkUnknown { get; }
    public RelayCommand Cancel { get; }
    public AsyncRelayCommand Start { get; }
    public AsyncRelayCommand Rerun { get; }
    public bool UnappliedNoticeVisible => plan?.Setup.Baseline.Recipe.RequiresDerivativeConsent ?? baseline?.Recipe.RequiresDerivativeConsent ?? false;
    private bool MayStart => CanEdit && main.CanEditPrompt && plan is not null && !main.PresetManagementOpen &&
        (!plan.Setup.Baseline.Recipe.RequiresDerivativeConsent || ConsentUnapplied);
    public ExperimentLabViewModel(MainViewModel main, PortablePaths paths)
    {
        this.main = main; this.paths = paths;
        CaptureBaseline = new(async _ =>
        {
            var leased = false;
            try
            {
                if (!main.Create.TryRecipe(out var r, out var error)) throw new ArgumentException(error);
                var snapshot = GenerationRecipeDerivation.Snapshot(main.Create.Positive, main.Create.Negative, r!);
                main.Forge.BeginExperiment(); leased = true; busy = true; cancel = new(); Refresh();
                regionalComparison = null; baseline = await main.Forge.PinExperimentBaselineAsync(snapshot, cancel.Token); ConsentUnapplied = false;
                Notify(nameof(BaselineSummary)); PreviewChanged(); Status = "baselineを取込済み。Model/LoRA identityを固定しました。生成はしていません。";
            }
            catch (Exception e) when (e is IOException or InvalidDataException or ArgumentException or InvalidOperationException or System.Net.Http.HttpRequestException or OperationCanceledException or JsonException) { baseline = null; Notify(nameof(BaselineSummary)); Status = "baseline未取込: " + e.Message; }
            finally { cancel?.Dispose(); cancel = null; busy = false; if (leased) main.Forge.EndExperiment(); Refresh(); }
        }, _ => CanEdit && main.CanEditPrompt && !main.PresetManagementOpen);
        Save = new(_ => Guard(() => { var p = ExperimentPlanner.Build(Draft()); Store.Save(p); ReloadList(); SelectedExperiment = Experiments.Single(e => e.Id == p.Id); }), _ => CanEdit && baseline is not null);
        Reload = new(_ => Guard(ReloadList), _ => CanEdit);
        Start = new(_ => ExecuteAsync(false), _ => MayStart && (attempts.Count == 0 || attempts.Any(a => a.RunNumber == selectedRun && a.Status == "Pending")));
        Rerun = new(_ => ExecuteAsync(true), _ => MayStart && attempts.Count > 0 && attempts.All(a => a.Status != "Running"));
        Cancel = new(_ => cancel?.Cancel(), _ => busy);
        Evaluate = new(_ => Guard(() => { Store.Evaluate(plan!.Id, Selected!.Attempt.Id, new(Rating, Passed, Winner, Note)); ReloadAttempts(); }), _ => CanEdit && Selected is not null);
        SaveObservation = new(_ => Guard(() => { Store.SaveObservation(plan!.Id, new(ObservedDirection, Exceptions)); Status = "人の観察・例外を保存しました。知識へ昇格していません。"; }), _ => CanEdit && plan is not null);
        ExportEvidence = new(_ => Guard(() => { var dir = Path.Combine(paths.Root, "UserData", "ExperimentEvidence"); Directory.CreateDirectory(dir); var file = Path.Combine(dir, plan!.Id + "-" + Guid.NewGuid().ToString("N") + ".json"); File.WriteAllText(file, Store.Evidence(plan.Id)); Status = "全trial/attempt/評価/例外をlocal evidenceへ保存しました（#44へ送信しません）: " + file; }), _ => CanEdit && plan is not null);
        UseInCreate = new(_ => { if (Selected?.Attempt.Receipt?.Metadata is { } m) main.Create.LoadImage(m, "Experiment result"); }, _ => CanEdit && main.CanEditPrompt && Selected?.Attempt.Receipt?.Metadata is not null);
        SetCompareLeft = new(_ => { compareLeft = Selected; Notify(nameof(SelectedDetails)); }, _ => CanEdit && Selected?.Attempt.Receipt?.Metadata is not null);
        MarkUnknown = new(_ => Guard(() => { Store.MarkUnknown(Selected!.Attempt.Id); ReloadAttempts(); }), _ => CanEdit && Selected?.Attempt.Status == "Running");
        main.Forge.PropertyChanged += (_, _) => Refresh();
    }
    private ExperimentStore Store => store ??= new(Path.Combine(paths.Root, "UserData", "experiment-lab.db"));
    private IReadOnlyList<ExperimentAttempt> attempts = [];
    private void ReloadList() { Experiments.Clear(); foreach (var e in Store.List()) Experiments.Add(new(e.Id, e.Name)); }
    private void Open(Guid id)
    { plan = Store.Load(id); regionalComparison = plan.Setup.Regional; baseline = plan.Setup.Baseline; name = plan.Setup.Name; hypothesis = plan.Setup.Hypothesis; xKind = plan.Setup.X.Kind; xTarget = plan.Setup.X.Target; xValues = string.Join("\n", plan.Setup.X.Values); useY = plan.Setup.Y is not null; yKind = plan.Setup.Y?.Kind ?? ExperimentVariable.Steps; yTarget = plan.Setup.Y?.Target ?? ""; yValues = string.Join("\n", plan.Setup.Y?.Values ?? []); seeds = string.Join("\n", plan.Setup.Seeds); repetitions = plan.Setup.Repetitions; foreach (var n in new[] { nameof(BaselineSummary), nameof(Name), nameof(Hypothesis), nameof(XKind), nameof(XTarget), nameof(XValues), nameof(UseY), nameof(YKind), nameof(YTarget), nameof(YValues), nameof(Seeds), nameof(Repetitions), nameof(Preview) }) Notify(n); ConsentUnapplied = false; var observation = Store.Observation(id); ObservedDirection = observation.Direction; Exceptions = observation.Exceptions; Notify(nameof(ObservedDirection)); Notify(nameof(Exceptions)); selectedSeed = plan.Setup.Seeds[0]; selectedRepetition = 0; xFilter = yFilter = -1; SeedChoices.Clear(); foreach (var s in plan.Setup.Seeds) SeedChoices.Add(s); ReloadAttempts(); foreach (var n in new[] { nameof(SelectedSeed), nameof(RepetitionChoices), nameof(SelectedRepetition), nameof(SelectedSummary), nameof(Columns), nameof(MatrixWidth), nameof(XVariants), nameof(YVariants), nameof(XFilter), nameof(YFilter) }) Notify(n); }
    private void ReloadAttempts()
    { attempts = Store.Attempts(plan!.Id); RunChoices.Clear(); foreach (var n in attempts.Select(a => a.RunNumber).Distinct()) RunChoices.Add(n); if (!RunChoices.Contains(selectedRun)) selectedRun = RunChoices.LastOrDefault(); Notify(nameof(SelectedRun)); Notify(nameof(SelectedSummary)); Filter(); }
    private void Filter()
    {
        var oldId = selected?.Attempt.Id; Cells.Clear();
        if (plan is not null)
            foreach (var a in attempts.Where(a => a.RunNumber == selectedRun))
            {
                var t = plan.Trials.Single(t => t.Id == a.TrialId);
                if (t.Seed == selectedSeed && t.Repetition == selectedRepetition && (xFilter < 0 || t.X == xFilter) && (yFilter < 0 || t.Y == yFilter))
                    Cells.Add(new(t, a, plan.Setup.X.Values[t.X], plan.Setup.Y?.Values[t.Y] ?? "—"));
            }
        Selected = Cells.FirstOrDefault(c => c.Attempt.Id == oldId); Refresh();
    }
    public async Task ExecuteAsync(bool rerun)
    {
        if (!MayStart || plan is null) return;
        var exact = Store.Load(plan.Id); ExperimentPlanner.Validate(exact);
        if (rerun && attempts.Any(a => a.Status == "Running")) { Status = "結果不明のRunning試行を確認してください。自動再送しません。"; return; }
        var leased = false;
        try
        {
            main.Forge.BeginExperiment(); leased = true; busy = true; cancel = new(); Refresh();
            if (rerun || attempts.Count == 0) { Store.CreateRun(exact.Id); selectedRun = Store.Attempts(exact.Id).Max(a => a.RunNumber); }
            ReloadAttempts(); var queue = attempts.Where(a => a.RunNumber == selectedRun && a.Status == "Pending").ToArray();
            foreach (var a in queue)
            {
                if (cancel.IsCancellationRequested) break;
                if (!Store.Claim(a.Id)) continue; // Durable claim BEFORE any network. Never retries an ambiguous POST.
                ReloadAttempts(); var trial = exact.Trials.Single(t => t.Id == a.TrialId);
                ForgeApiResult receipt = new(false, "Trial not sent.");
                long? imageId = null;
                try
                {
                    if (a == queue[0]) Store.Capabilities(a.RunId, ExperimentPlanner.Json(new { URL = main.Forge.ForgeUrl, Capabilities = await main.Forge.ReadRecipeCapabilitiesAsync(), Client = typeof(ExperimentLabViewModel).Assembly.GetName().Version?.ToString() }));
                    receipt = await main.Forge.ExecuteExperimentTrialAsync(new(trial.Id, "Experiment " + exact.Id, "exact stored trial", trial.Requested.Positive, trial.Requested.Negative, trial.Requested.Recipe), cancel.Token, ConsentUnapplied) ?? new(false, "Executor unavailable.");
                    if (receipt.ImagePath is { } path)
                        imageId = new GenerationLibraryStore(paths.GenerationLibrary).Query(new(Text: Path.GetFileName(path), Limit: 200)).Images.Single(i => i.NormalizedPath == path).Id;
                }
                catch (Exception e) when (e is IOException or InvalidDataException or UnauthorizedAccessException or System.Net.Http.HttpRequestException or OperationCanceledException or InvalidOperationException or ArgumentException or JsonException or Microsoft.Data.Sqlite.SqliteException)
                { receipt = new(false, receipt.Status + " /Trial failed / result may be unknown; no automatic retry: " + e.Message, receipt.ImagePath, receipt.Metadata); }
                Store.Complete(a.Id, receipt, imageId); ReloadAttempts();
                Status = $"run{selectedRun}: {attempts.Count(a => a.RunNumber == selectedRun && a.Status == "Succeeded")}/{exact.Trials.Count}成功。失敗・結果不明も保持します。";
                if (!receipt.Success || imageId is null) break;
            }
        }
        catch (Exception e) when (e is IOException or InvalidDataException or InvalidOperationException or ArgumentException or Microsoft.Data.Sqlite.SqliteException) { Status = "Experiment stopped; no automatic resend: " + e.Message; }
        finally { cancel?.Dispose(); cancel = null; busy = false; if (leased) main.Forge.EndExperiment(); Refresh(); }
    }
    private void Guard(Action action)
    { try { action(); } catch (Exception e) when (e is IOException or InvalidDataException or ArgumentException or InvalidOperationException or JsonException or Microsoft.Data.Sqlite.SqliteException) { Status = e.Message; } }
    private void PreviewChanged() { Notify(nameof(Preview)); Refresh(); }
    private void Refresh()
    {
        foreach (var n in new[] { nameof(Busy), nameof(CanEdit), nameof(UnappliedNoticeVisible), nameof(Rating), nameof(Passed), nameof(Winner), nameof(Note) }) Notify(n);
        CaptureBaseline?.Refresh(); Save?.Refresh(); Reload?.Refresh(); Evaluate?.Refresh(); SaveObservation?.Refresh(); ExportEvidence?.Refresh(); Start?.Refresh(); Rerun?.Refresh(); Cancel?.Refresh(); UseInCreate?.Refresh(); SetCompareLeft?.Refresh(); MarkUnknown?.Refresh();
    }
}
