using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Media.Imaging;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.Data.Sqlite;

namespace DanbooruTagTool.App.ViewModels;

public sealed class LibraryImageCard(LibraryImage image) : Observable
{
    public LibraryImage Image { get; private set; } = image;
    public void UpdateAnnotation(ImageAnnotation value) { Image = Image with { Annotation = value }; Notify(nameof(Image)); }
    public string Filename => Path.GetFileName(Image.RelativePath);
    public string Status => $"{Image.Availability} / {Image.MetadataStatus}";
    private BitmapSource? thumbnail;
    public BitmapSource? Thumbnail { get => thumbnail; set => Set(ref thumbnail, value); }
}

public sealed class GenerationLibraryViewModel : Observable
{
    private readonly PortablePaths paths;
    private readonly PromptWorkspace workspace;
    private readonly Action<GenerationMetadataSnapshot> createPreset;
    private readonly ForgeViewModel forge;
    private readonly Func<bool> canMutate;
    private readonly GenerationThumbnailCache thumbnails;
    private GenerationLibraryStore? store;
    private CancellationTokenSource? cancellation;
    private bool busy, loaded, changingAnnotation, annotationPending;
    private int offset;
    private long total;
    private string status = "フォルダーを追加してスキャンしてください。画像は元の場所に保持されます。";
    private LibraryImageCard? selected;
    private GenerationMetadataSnapshot? metadata, compareLeft;
    private LibraryRoot? selectedRoot;
    private bool favorite;
    private int? rating;
    private string note = "";
    public ObservableCollection<LibraryRoot> Roots { get; } = [];
    public ObservableCollection<LibraryImageCard> Images { get; } = [];
    public ObservableCollection<MetadataDifference> Differences { get; } = [];
    public string Text { get; set; } = "";
    public string PositiveFilter { get; set; } = "";
    public string NegativeFilter { get; set; } = "";
    public string ModelFilter { get; set; } = "";
    public string SeedFilter { get; set; } = "";
    public string SamplerFilter { get; set; } = "";
    public string SchedulerFilter { get; set; } = "";
    public string CfgMinFilter { get; set; } = "";
    public string CfgMaxFilter { get; set; } = "";
    public string WidthFilter { get; set; } = "";
    public string HeightFilter { get; set; } = "";
    public string LoraFilter { get; set; } = "";
    public string NoteFilter { get; set; } = "";
    public bool FavoriteFilter { get; set; }
    public string RatingFilter { get; set; } = "";
    public int MetadataFilter { get; set; }
    public int SortIndex { get; set; }
    public LibraryRoot? SelectedRoot { get => selectedRoot; set => Set(ref selectedRoot, value); }
    public bool Busy { get => busy; private set { Set(ref busy, value); Notify(nameof(CanAnnotate)); RefreshCommands(); } }
    public string Status { get => status; private set => Set(ref status, value); }
    public string PageSummary => $"{total:N0}件 · {offset + (Images.Count == 0 ? 0 : 1)}–{offset + Images.Count}（60件/ページ）";
    public LibraryImageCard? Selected
    {
        get => selected;
        set
        {
            if (selected != value && annotationPending && !PersistAnnotation()) { Notify(nameof(Selected)); return; }
            if (!Set(ref selected, value)) return;
            try { metadata = value is null ? null : store?.Metadata(value.Image.Id); }
            catch (Exception e) when (StorageError(e)) { metadata = null; Status = e.Message; }
            changingAnnotation = true;
            Favorite = value?.Image.Annotation.Favorite ?? false; Rating = value?.Image.Annotation.Rating; Note = value?.Image.Annotation.Note ?? "";
            changingAnnotation = false;
            Notify(nameof(Positive)); Notify(nameof(Negative)); Notify(nameof(RawInfotext)); Notify(nameof(SelectedPath)); Notify(nameof(HasSelection)); Notify(nameof(CanAnnotate)); Notify(nameof(Preview)); Notify(nameof(CompareRightSource)); Notify(nameof(RestorationWarning));
            Notify(nameof(LoraProvenance)); Notify(nameof(DerivationSummary)); RefreshCommands();
        }
    }
    public bool HasSelection => Selected is not null;
    public bool CanAnnotate => HasSelection && !Busy;
    public BitmapSource? Preview => Selected?.Thumbnail;
    public string SelectedPath => Selected?.Image.NormalizedPath ?? "";
    public string Positive => metadata?.Positive ?? "";
    public string Negative => metadata?.Negative ?? "";
    public string RawInfotext => metadata?.RawInfotext ?? "生成metadataなし。画像の評価・メモは保存できます。";
    public string DerivationSummary => GenerationRecipeDerivation.Summary(metadata?.Parameters);
    public string LoraProvenance => metadata is null ? "" : GenerationLoraProvenance.Summary(metadata.Parameters);
    public string RestorationWarning => metadata is null ? "" : GenerationRecipe.FromMetadata(metadata) is { RequiresDerivativeConsent: true } r
        ? "元画像の未適用条件: " + string.Join(" / ", r.UnappliedParameters.Select(p => p.Name)) + "。「作成で使う」で確認してください。"
        : "保存metadataの対応条件のみ復元します。画像の完全一致は保証できません。";
    public bool Favorite { get => favorite; set { if (Set(ref favorite, value)) PersistAnnotation(); } }
    public int? Rating { get => rating; set { if (Set(ref rating, value)) PersistAnnotation(); } }
    public string Note { get => note; set { if (Set(ref note, value)) PersistAnnotation(); } }
    public AsyncRelayCommand Refresh { get; }
    public AsyncRelayCommand Scan { get; }
    public AsyncRelayCommand Previous { get; }
    public AsyncRelayCommand Next { get; }
    public RelayCommand AllRoots { get; }
    public RelayCommand RestorePrompt { get; }
    public Action<GenerationMetadataSnapshot, string>? UseInCreate { get; set; }
    public RelayCommand LoadInCreate { get; }
    private string compareLeftFilename = "";
    public bool HasCompareLeft => compareLeft is not null;
    public string CompareLeftSource => "左: " + (compareLeftFilename.Length == 0 ? "未選択" : compareLeftFilename);
    public string CompareRightSource => "右: " + (Selected?.Filename ?? "未選択");
    public PromptWorkspace? NegativeWorkspace { get; set; }
    public RelayCommand RestoreNegative { get; }
    public RelayCommand CreatePreset { get; }
    public AsyncRelayCommand Send { get; }
    public AsyncRelayCommand Generate { get; }
    public AsyncRelayCommand GenerateRecipe { get; }
    public string RecipeStatus => forge.RecipeStatus;
    public RelayCommand SetCompareLeft { get; }
    public RelayCommand Compare { get; }
    public RelayCommand CancelScan { get; }
    public GenerationLibraryViewModel(PortablePaths paths, PromptWorkspace workspace,
        Action<GenerationMetadataSnapshot> createPreset, ForgeViewModel forge, Func<bool> canMutate)
    {
        this.paths = paths; this.workspace = workspace; this.createPreset = createPreset; this.forge = forge; this.canMutate = canMutate;
        thumbnails = new(paths.GenerationThumbnails);
        Refresh = new(_ => LoadPageAsync(reset: true), _ => !Busy);
        Scan = new(_ => ScanAsync(), _ => !Busy && Roots.Any(r => r.Enabled));
        Previous = new(_ => LoadPageAsync(delta: -60), _ => !Busy && offset > 0);
        Next = new(_ => LoadPageAsync(delta: 60), _ => !Busy && offset + Images.Count < total);
        AllRoots = new(_ => SelectedRoot = null, _ => !Busy);
        LoadInCreate = new(_ => { if (metadata is not null) UseInCreate?.Invoke(metadata, Selected?.Filename ?? "画像"); }, _ => !Busy && canMutate() && metadata is not null && UseInCreate is not null);
        RestorePrompt = new(_ => { if (metadata is not null && canMutate()) { workspace.Replace(metadata.Positive); Status = "Positive Promptを復元しました。Undo / 回復で戻せます。"; } }, _ => !Busy && canMutate() && metadata is not null);
        RestoreNegative = new(_ => { if (metadata is not null && canMutate()) { NegativeWorkspace?.Replace(metadata.Negative); Status = "Negativeを置換しました。NegativeのUndo/回復で戻せます。"; } }, _ => !Busy && canMutate() && metadata is not null && NegativeWorkspace is not null);
        CreatePreset = new(_ => { if (metadata is not null && canMutate()) createPreset(metadata); }, _ => !Busy && canMutate() && metadata is not null);
        Send = new(_ => SendAsync(false), _ => !Busy && canMutate() && metadata is not null);
        Generate = new(_ => SendAsync(true), _ => !Busy && canMutate() && metadata is not null);
        GenerateRecipe = new(async _ =>
        {
            if (metadata is null) return;
            try
            {
                var preset = new GenerationPreset(Guid.NewGuid(), "image recipe", "", metadata.Positive, metadata.Negative, GenerationRecipeDerivation.FromImage(metadata, Selected?.Filename ?? "画像", GenerationMetadataReaders.ReadSnapshot));
                await forge.GenerateRecipeAsync(preset);
            }
            catch (Exception e) when (StorageError(e) || e is GenerationMetadataException) { Status = "派生元画像を確認できません: " + e.Message; }
        }, _ => !Busy && canMutate() && metadata is not null);
        forge.PropertyChanged += (_, e) => { if (e.PropertyName == nameof(forge.RecipeStatus)) Notify(nameof(RecipeStatus)); };
        SetCompareLeft = new(_ => { compareLeft = metadata; compareLeftFilename = Selected?.Filename ?? "画像"; Notify(nameof(CompareLeftSource)); Notify(nameof(HasCompareLeft)); Differences.Clear(); Status = "比較する左画像を保持しました。右画像を選択して比較してください。"; Compare?.Refresh(); }, _ => metadata is not null);
        Compare = new(_ => { if (compareLeft is null || metadata is null) return; Differences.Clear(); foreach (var row in GenerationMetadataDiff.Compare(compareLeft, metadata)) Differences.Add(row); }, _ => compareLeft is not null && metadata is not null);
        CancelScan = new(_ => cancellation?.Cancel(), _ => Busy);
    }
    public async Task InitializeAsync()
    {
        if (loaded || Busy) return;
        await LoadPageAsync();
    }
    private void EnsureStore()
    {
        store ??= new(paths.GenerationLibrary);
        Roots.Clear(); foreach (var root in store.Roots()) Roots.Add(root);
        loaded = true;
    }
    public async Task AddRootAsync(string path)
    {
        if (Busy) return;
        try { EnsureStore(); store!.AddRoot(path); EnsureStore(); Status = "フォルダーを登録しました。「スキャン」で画像を登録します。"; }
        catch (Exception e) when (StorageError(e) || e is ArgumentException) { Status = "登録できません: " + e.Message; }
        RefreshCommands(); await LoadPageAsync(reset: true);
    }
    public async Task SetSelectedRootEnabledAsync(bool enabled)
    {
        if (Busy || SelectedRoot is null) return;
        try { store?.SetRootEnabled(SelectedRoot.Id, enabled); SelectedRoot = null; EnsureStore(); }
        catch (Exception e) when (StorageError(e)) { Status = e.Message; }
        RefreshCommands(); await Task.CompletedTask;
    }
    public async Task ScanAsync()
    {
        if (Busy || (annotationPending && !PersistAnnotation())) return;
        Busy = true; cancellation = new();
        try
        {
            EnsureStore(); var roots = SelectedRoot is null ? Roots.Where(r => r.Enabled).ToArray() : [SelectedRoot];
            var scanner = new GenerationLibraryScanner(store!, GenerationMetadataReaders.CreateDefault());
            var results = await Task.Run(() => roots.Select(r => scanner.Scan(r, cancellation.Token)).ToArray());
            Status = $"追加 {results.Sum(r => r.Added)} / 更新 {results.Sum(r => r.Refreshed)} / 変更なし {results.Sum(r => r.Unchanged)} / missing {results.Sum(r => r.Missing)} / エラー {results.Sum(r => r.Errors)}" + (results.All(r => r.Complete) ? "" : " · 未完了のフォルダーがあります。接続・読取権限を確認してください。");
        }
        catch (OperationCanceledException) { Status = "スキャンを中止しました。未完了フォルダーのDB変更は取り消しました。"; }
        catch (Exception e) when (StorageError(e)) { Status = "スキャンできません: " + e.Message; }
        finally { Busy = false; cancellation.Dispose(); cancellation = null; }
        await LoadPageAsync(reset: true);
    }
    public async Task LoadPageAsync(bool reset = false, int delta = 0)
    {
        if (Busy || (annotationPending && !PersistAnnotation())) return;
        Busy = true;
        try
        {
            EnsureStore(); var target = reset ? 0 : Math.Max(0, offset + delta); var query = BuildQuery(target);
            var page = await Task.Run(() => store!.Query(query)); offset = target; total = page.Total;
            Selected = null; Images.Clear(); foreach (var image in page.Images) Images.Add(new(image)); Notify(nameof(PageSummary));
            // Only one bounded page is queued. Two cache workers; no full-size grid decode.
            await Task.WhenAll(Images.Select(async card => { card.Thumbnail = await thumbnails.GetAsync(card.Image); if (Selected == card) Notify(nameof(Preview)); Notify(nameof(CompareRightSource)); }));
        }
        catch (Exception e) when (StorageError(e) || e is FormatException or OverflowException) { Status = "表示できません: " + e.Message; }
        finally { Busy = false; }
    }
    private LibraryQuery BuildQuery(int target)
    {
        long? Long(string s) => string.IsNullOrWhiteSpace(s) ? null : long.Parse(s, CultureInfo.InvariantCulture);
        int? Int(string s) => string.IsNullOrWhiteSpace(s) ? null : int.Parse(s, CultureInfo.InvariantCulture);
        decimal? Decimal(string s) => string.IsNullOrWhiteSpace(s) ? null : decimal.Parse(s, CultureInfo.InvariantCulture);
        return new(Text, SelectedRoot?.Id, PositiveFilter, NegativeFilter, ModelFilter, Long(SeedFilter), SamplerFilter, SchedulerFilter,
            Decimal(CfgMinFilter), Decimal(CfgMaxFilter), Int(WidthFilter), Int(HeightFilter), LoraFilter, FavoriteFilter, Int(RatingFilter), NoteFilter,
            MetadataFilter == 0 ? null : MetadataFilter == 1, (LibrarySort)SortIndex, target);
    }
    private bool PersistAnnotation()
    {
        if (changingAnnotation || Selected is null || store is null) return true;
        try { var value = new ImageAnnotation(Favorite, Rating, Note); store.SaveAnnotation(Selected.Image.Id, value); Selected.UpdateAnnotation(value); annotationPending = false; Status = "評価・メモを保存しました。"; return true; }
        catch (Exception e) when (StorageError(e) || e is ArgumentOutOfRangeException) { annotationPending = true; Status = "評価・メモを保存できません。入力を保持しています。値・保存先を確認して再編集してください: " + e.Message; return false; }
    }
    public async Task SendAsync(bool generate)
    {
        if (metadata is null || !canMutate()) return;
        // A transient existing preset is an adapter, not another persisted model or Prompt state.
        var preset = new GenerationPreset(Guid.NewGuid(), "image", "", metadata.Positive, metadata.Negative);
        if (generate) await forge.GenerateImageAsync(preset, CancellationToken.None);
        else await forge.SendImageAsync(preset, CancellationToken.None);
    }
    public void Backup(string destination)
    {
        try { EnsureStore(); store!.Backup(destination); Status = "Library DBをバックアップしました（フォルダー設定・評価・メモを含みます）。"; }
        catch (Exception e) when (StorageError(e) || e is ArgumentException) { Status = "バックアップできません: " + e.Message; }
    }
    public bool FlushAnnotation() => !annotationPending || PersistAnnotation();
    public async Task IndexRecipeResultAsync(string imagePath)
    {
        var resultStore = new GenerationLibraryStore(paths.GenerationLibrary);
        var root = resultStore.AddRoot(Path.GetDirectoryName(imagePath)!);
        var scan = await Task.Run(() => new GenerationLibraryScanner(resultStore, new PngGenerationMetadataReader()).Scan(root));
        if (!scan.Complete || scan.Errors != 0) throw new InvalidDataException("生成PNGのLibraryスキャンに失敗しました。");
        await LoadPageAsync(reset: true);
    }
    public void CancelPendingScan() => cancellation?.Cancel();
    private static bool StorageError(Exception e) => e is IOException or UnauthorizedAccessException or SqliteException or InvalidDataException;
    public void RefreshCommands()
    {
        Refresh?.Refresh(); Scan?.Refresh(); Previous?.Refresh(); Next?.Refresh(); AllRoots?.Refresh(); LoadInCreate?.Refresh(); RestorePrompt?.Refresh(); RestoreNegative?.Refresh(); CreatePreset?.Refresh();
        Send?.Refresh(); Generate?.Refresh(); GenerateRecipe?.Refresh(); SetCompareLeft?.Refresh(); Compare?.Refresh(); CancelScan?.Refresh();
    }
}
