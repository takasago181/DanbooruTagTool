using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using DanbooruTagTool.App.ViewModels;
using Microsoft.Win32;
using KeyEventArgs = System.Windows.Input.KeyEventArgs;

namespace DanbooruTagTool.App;

// View-only behavior: focus, pointer geometry, insertion feedback and window sizing.
// All Prompt mutations and selection rules are delegated to the ViewModel/Core.
public partial class MainWindow : Window
{
    private readonly MainViewModel vm;
    private readonly DispatcherTimer feedbackTimer = new() { Interval = TimeSpan.FromSeconds(2) };
    private readonly DispatcherTimer uiTimer = new() { Interval = TimeSpan.FromMilliseconds(400) };
    private bool syncingNavigation;
    private GenerationPresetDialog? presetDialog;
    private ForgeSettingsDialog? forgeSettingsDialog;
    private GenerationImportDialog? generationImportDialog;
    public MainWindow(MainViewModel vm)
    {
        this.vm = vm; InitializeComponent(); DataContext = vm;
        vm.PresetsRequested += OpenPresetDialog;
        vm.ForgeSettingsRequested += OpenForgeSettingsDialog;
        vm.GenerationImportRequested += OpenGenerationImportDialog;
        var defaultHeight = Math.Abs(vm.Ui.Height - 820) < 0.5 ? 720 : vm.Ui.Height;
        Width = Math.Max(MinWidth, vm.Ui.Width); Height = Math.Max(MinHeight, defaultHeight);
        Left = Math.Clamp(vm.Ui.Left, SystemParameters.VirtualScreenLeft, SystemParameters.VirtualScreenLeft + SystemParameters.VirtualScreenWidth - 100);
        Top = Math.Clamp(vm.Ui.Top, SystemParameters.VirtualScreenTop, SystemParameters.VirtualScreenTop + SystemParameters.VirtualScreenHeight - 100);
        var navWidth = IsLegacyNavWidth(vm.Ui.NavWidth) ? 300 : vm.Ui.NavWidth;
        var promptWidth = IsLegacyPromptWidth(vm.Ui.PromptWidth) ? 400 : vm.Ui.PromptWidth;
        NavColumn.Width = new(Math.Max(240, navWidth)); PromptColumn.Width = new(Math.Max(360, promptWidth));
        // Hidden editor geometry used to persist zero, then clamp it to 25%.
        // Repair that collapsed state and migrate the old 70:30 default to 75:25.
        var ratio = vm.Ui.EditRatio <= .251 || Math.Abs(vm.Ui.EditRatio - .7) < .001 ? .75 : Math.Clamp(vm.Ui.EditRatio, .3, .85);
        PromptEditor.ApplyEditRatio(ratio);
        NegativeEditor.ApplyEditRatio(ratio);
        vm.Negative.ScrollToChip += NegativeEditor.BringChipIntoView;
        vm.Negative.PropertyChanged += (_, e) => { if (e.PropertyName == nameof(vm.Negative.DirectEditing) && vm.Negative.DirectEditing) Dispatcher.BeginInvoke(NegativeEditor.FocusDirectEditor, DispatcherPriority.Input); };
        feedbackTimer.Tick += (_, _) => { feedbackTimer.Stop(); if (vm.Status == "✓ コピーしました") vm.Status = ""; };
        uiTimer.Tick += (_, _) => { uiTimer.Stop(); SaveGeometry(); };
        vm.PropertyChanged += (_, e) =>
        {
            if (e.PropertyName == nameof(vm.Status) && vm.Status == "✓ コピーしました")
            {
                feedbackTimer.Stop();
                feedbackTimer.Start();
            }
            if (e.PropertyName == nameof(vm.DirectEditing) && vm.DirectEditing)
            {
                if (vm.Prompt.DirectEditing) Dispatcher.BeginInvoke(PromptEditor.FocusDirectEditor, DispatcherPriority.Input);
            }
            if (e.PropertyName == nameof(vm.BrowseKey)) Dispatcher.BeginInvoke(SyncNavigationSelection, DispatcherPriority.Loaded);
        };
        vm.ScrollToChip += PromptEditor.BringChipIntoView;
        DictionaryWorkspace.BrowseScrollChanged += QueueUiSave;
        PromptEditor.EditRatioChanged += SaveGeometry;
        NegativeEditor.EditRatioChanged += SaveGeometry;
        SizeChanged += (_, _) => { UpdateResponsiveLayout(); QueueUiSave(); }; LocationChanged += (_, _) => QueueUiSave();
        Closing += (_, e) => { if (vm.Experiments?.Busy == true) { vm.Experiments.Cancel.Execute(null); vm.Status = "実験を中止中です。trial記録の完了までお待ちください。"; e.Cancel = true; return; } if (vm.GenerationLibrary?.FlushAnnotation() == false) { e.Cancel = true; return; } vm.GenerationLibrary?.CancelPendingScan(); SaveGeometry(); feedbackTimer.Stop(); uiTimer.Stop(); if (presetDialog != null) presetDialog.Close(); if (forgeSettingsDialog != null) forgeSettingsDialog.Close(); if (generationImportDialog != null) generationImportDialog.Close(); };
        Loaded += (_, _) => { vm.UpdateChipLanguage(); UpdateResponsiveLayout(); SyncNavigationSelection(); };
    }
    private static bool IsLegacyNavWidth(double width) => Math.Abs(width - 210) < 0.5 || Math.Abs(width - 230) < 0.5;
    private static bool IsLegacyPromptWidth(double width) => Math.Abs(width - 230) < 0.5 || Math.Abs(width - 260) < 0.5 || Math.Abs(width - 280) < 0.5 || Math.Abs(width - 300) < 0.5 || Math.Abs(width - 340) < 0.5;
    private void QueueUiSave() { if (!IsLoaded) return; uiTimer.Stop(); uiTimer.Start(); }
    private void SaveGeometry()
    {
        var rect = WindowState == WindowState.Normal ? new Rect(Left, Top, ActualWidth, ActualHeight) : RestoreBounds;
        var activeEditor = vm.Intelligence.ActiveSide == 1 ? NegativeEditor : PromptEditor;
        var ratio = activeEditor.IsVisible && activeEditor.EditRatio > .251 ? activeEditor.EditRatio : vm.Ui.EditRatio;
        vm.SaveUi(vm.Ui with { Width = rect.Width, Height = rect.Height, Left = rect.Left, Top = rect.Top,
            NavWidth = vm.WorkspaceIndex == 0 && ActualWidth >= 1400 ? NavColumn.ActualWidth : vm.Ui.NavWidth,
            PromptWidth = vm.WorkspaceIndex == 0 && ActualWidth >= 1400 ? PromptColumn.ActualWidth : vm.Ui.PromptWidth,
            EditRatio = ratio });
    }
    private void NavigationChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
    {
        if (syncingNavigation || e.NewValue is not NavigationNode node) return;
        if (node.Key.StartsWith("group:", StringComparison.Ordinal))
        {
            syncingNavigation = true;
            try
            {
                if (NavigationTree.ItemContainerGenerator.ContainerFromItem(node) is TreeViewItem item)
                {
                    item.IsExpanded = true;
                    item.IsSelected = false;
                }
            }
            finally { syncingNavigation = false; }
            Dispatcher.BeginInvoke(SyncNavigationSelection, DispatcherPriority.Loaded);
            return;
        }
        vm.Navigate.Execute(node);
    }
    private void SyncNavigationSelection()
    {
        if (!IsLoaded) return;
        var path = new List<NavigationNode>();
        syncingNavigation = true;
        try
        {
            if (!TryFindNavigationPath(vm.Navigation, vm.BrowseKey, path))
            {
                ClearNavigationSelection(NavigationTree);
                return;
            }

            ItemsControl owner = NavigationTree;
            TreeViewItem? item = null;
            for (int i = 0; i < path.Count; i++)
            {
                item = owner.ItemContainerGenerator.ContainerFromItem(path[i]) as TreeViewItem;
                if (item == null) { owner.UpdateLayout(); item = owner.ItemContainerGenerator.ContainerFromItem(path[i]) as TreeViewItem; }
                if (item == null) return;
                if (i < path.Count - 1) { item.IsExpanded = true; item.UpdateLayout(); owner = item; }
            }
            if (item == null) return;
            item.IsSelected = true;
            item.BringIntoView();
        }
        finally { syncingNavigation = false; }
    }

    private static void ClearNavigationSelection(ItemsControl owner)
    {
        owner.UpdateLayout();
        foreach (var data in owner.Items)
        {
            if (owner.ItemContainerGenerator.ContainerFromItem(data) is not TreeViewItem item) continue;
            if (item.IsSelected) item.IsSelected = false;
            if (item.HasItems)
            {
                item.IsExpanded = true;
                ClearNavigationSelection(item);
            }
        }
    }
    private static bool TryFindNavigationPath(IReadOnlyList<NavigationNode> nodes, string key, List<NavigationNode> path)
    {
        foreach (var node in nodes)
        {
            path.Add(node);
            if (node.Key == key || TryFindNavigationPath(node.Children, key, path)) return true;
            path.RemoveAt(path.Count - 1);
        }
        return false;
    }
    private void WorkspaceChanged(object sender, SelectionChangedEventArgs e) { if (DataContext != null && e.Source == Workspaces) vm.UpdateChipLanguage(); }
    private void SplitterChanged(object sender, System.Windows.Controls.Primitives.DragCompletedEventArgs e) => SaveGeometry();
    private void FindKeyDown(object sender, KeyEventArgs e) { if (e.Key == Key.Enter) { vm.FindNext(Keyboard.Modifiers.HasFlag(ModifierKeys.Shift)); e.Handled = true; } }
    private void WindowKeyDown(object sender, KeyEventArgs e)
    {
        if (vm.DirectEditing) return;
        bool ctrl = Keyboard.Modifiers.HasFlag(ModifierKeys.Control);
        if (vm.WorkspaceIndex == 1 && vm.CreatePageIndex == 1)
        {
            if (ctrl && e.Key == Key.F) NegativeEditor.FocusFind();
            else if (Keyboard.FocusedElement is TextBox) return;
            else if (ctrl && e.Key == Key.Z) vm.Negative.Undo.Execute(null);
            else if (ctrl && e.Key == Key.Y) vm.Negative.Redo.Execute(null);
            else if (ctrl && e.Key == Key.A) vm.Negative.SelectAll();
            else if (e.Key == Key.Delete) vm.Negative.Delete.Execute(null);
            else if (e.Key == Key.Escape) vm.Negative.ClearSelection(); else return;
            e.Handled = true; return;
        }
        if (ctrl && e.Key == Key.F) { if (vm.WorkspaceIndex == 2) GenerationLibraryWorkspace.FocusSearch(); else if (vm.WorkspaceIndex == 3) LoraLibraryWorkspace.FocusSearch(); else if (vm.WorkspaceIndex == 1 && vm.CreatePageIndex == 0) PromptEditor.FocusFind(); else if (vm.WorkspaceIndex == 0) DictionaryWorkspace.FocusSearch(); else return; e.Handled = true; return; }
        if (Keyboard.FocusedElement is TextBox || vm.WorkspaceIndex > 1 || vm.WorkspaceIndex == 1 && vm.CreatePageIndex > 1) return;
        if (ctrl && e.Key == Key.Z) vm.Undo.Execute(null);
        else if (ctrl && e.Key == Key.Y) vm.Redo.Execute(null);
        else if (vm.WorkspaceIndex == 1 && ctrl && e.Key == Key.A) vm.SelectAll();
        else if (vm.WorkspaceIndex == 1 && e.Key == Key.Escape) vm.ClearSelection();
        else if (vm.WorkspaceIndex == 1 && e.Key == Key.Delete) vm.Delete.Execute(null);
        else return;
        e.Handled = true;
    }
    private void CreateMoreClick(object sender, RoutedEventArgs e)
    {
        if (sender is Button { ContextMenu: { } menu } button) { menu.DataContext = vm; menu.PlacementTarget = button; menu.IsOpen = true; }
    }
    private void GeneratorOutputClick(object sender, RoutedEventArgs e) => vm.OutputProfile = DanbooruTagTool.Core.PromptOutputProfile.GenerationFriendly;
    private void CanonicalOutputClick(object sender, RoutedEventArgs e) => vm.OutputProfile = DanbooruTagTool.Core.PromptOutputProfile.Canonical;
    private void ResetLayoutClick(object sender, RoutedEventArgs e)
    {
        vm.SaveUi(vm.Ui with { NavWidth = 300, PromptWidth = 400, EditRatio = .75 });
        PromptEditor.ApplyEditRatio(.75); NegativeEditor.ApplyEditRatio(.75); UpdateResponsiveLayout();
        vm.Status = "ペイン幅と編集比率を初期値へ戻しました。Prompt・Preset・Libraryは変更していません。";
    }
    private void UpdateResponsiveLayout()
    {
        if (NavColumn is null || PromptColumn is null) return;
        // Keep a useful centre result surface on smaller windows; preserve saved wide widths.
        NavColumn.MinWidth = 170; PromptColumn.MinWidth = 210;
        if (ActualWidth < 1400)
        { NavColumn.Width = new(ActualWidth < 1050 ? 170 : 240); PromptColumn.Width = new(ActualWidth < 1050 ? 230 : 300); }
        else { NavColumn.Width = new(Math.Clamp(vm.Ui.NavWidth, 240, ActualWidth * .3)); PromptColumn.Width = new(Math.Clamp(vm.Ui.PromptWidth, 300, ActualWidth * .35)); }
        Resources["NavigationLabelWidth"] = Math.Clamp(NavColumn.Width.Value - 80, 60, 270);
    }
    private void ImportGenerationPngClick(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFileDialog
        {
            Title = "Forgeで生成したPNGを選択",
            Filter = "PNG画像 (*.png)|*.png",
            CheckFileExists = true,
            Multiselect = false
        };
        if (dialog.ShowDialog(this) == true) vm.ImportGenerationPng(dialog.FileName);
    }
    private async void TokenCountClick(object sender, RoutedEventArgs e) => await vm.Intelligence.CountAsync();

    private void WindowDragOver(object sender, DragEventArgs e)
    {
        // Let file drops reach WindowDrop so invalid selections receive feedback.
        e.Effects = e.Data.GetDataPresent(DataFormats.FileDrop) ? DragDropEffects.Copy : DragDropEffects.None;
        e.Handled = true;
    }

    private void WindowDrop(object sender, DragEventArgs e)
    {
        if (!e.Data.GetDataPresent(DataFormats.FileDrop) || e.Data.GetData(DataFormats.FileDrop) is not string[] files || files.Length != 1)
            vm.Status = "生成PNGを1ファイルだけドロップしてください";
        else if (!Path.GetExtension(files[0]).Equals(".png", StringComparison.OrdinalIgnoreCase))
            vm.Status = "生成情報の読込はPNGファイルに対応しています";
        else
            vm.ImportGenerationPng(files[0]);
        e.Handled = true;
    }

    private void OpenGenerationImportDialog()
    {
        if (generationImportDialog is { IsVisible: true })
        {
            generationImportDialog.Activate();
            return;
        }
        generationImportDialog = new GenerationImportDialog(vm) { Owner = this };
        generationImportDialog.Closed += (_, _) => generationImportDialog = null;
        generationImportDialog.Show();
    }

    private void OpenPresetDialog()
    {
        if (presetDialog is { IsVisible: true }) { presetDialog.Activate(); return; }
        presetDialog = new GenerationPresetDialog(vm) { Owner = this };
        presetDialog.Closed += (_, _) => presetDialog = null;
        vm.PresetManagementOpen = true;
        try { presetDialog.ShowDialog(); }
        finally { vm.PresetManagementOpen = false; }

    }
    private void OpenForgeSettingsDialog()
    {
        if (forgeSettingsDialog is { IsVisible: true }) { forgeSettingsDialog.Activate(); return; }
        forgeSettingsDialog = new ForgeSettingsDialog(vm) { Owner = this };
        forgeSettingsDialog.Closed += (_, _) => forgeSettingsDialog = null;
        forgeSettingsDialog.Show();
    }
}
