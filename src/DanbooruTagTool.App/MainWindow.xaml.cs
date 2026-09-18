using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using DanbooruTagTool.App.ViewModels;
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
    public MainWindow(MainViewModel vm)
    {
        this.vm = vm; InitializeComponent(); DataContext = vm;
        vm.PresetsRequested += OpenPresetDialog;
        vm.ForgeSettingsRequested += OpenForgeSettingsDialog;
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
                Dispatcher.BeginInvoke(PromptEditor.FocusDirectEditor, DispatcherPriority.Input);
            }
            if (e.PropertyName == nameof(vm.BrowseKey)) Dispatcher.BeginInvoke(SyncNavigationSelection, DispatcherPriority.Loaded);
        };
        vm.ScrollToChip += PromptEditor.BringChipIntoView;
        DictionaryWorkspace.BrowseScrollChanged += QueueUiSave;
        PromptEditor.EditRatioChanged += SaveGeometry;
        SizeChanged += (_, _) => QueueUiSave(); LocationChanged += (_, _) => QueueUiSave();
        Closing += (_, _) => { SaveGeometry(); feedbackTimer.Stop(); uiTimer.Stop(); if (presetDialog != null) presetDialog.Close(); if (forgeSettingsDialog != null) forgeSettingsDialog.Close(); };
        Loaded += (_, _) => { vm.UpdateChipLanguage(); SyncNavigationSelection(); };
    }
    private static bool IsLegacyNavWidth(double width) => Math.Abs(width - 210) < 0.5 || Math.Abs(width - 230) < 0.5;
    private static bool IsLegacyPromptWidth(double width) => Math.Abs(width - 230) < 0.5 || Math.Abs(width - 260) < 0.5 || Math.Abs(width - 280) < 0.5 || Math.Abs(width - 300) < 0.5 || Math.Abs(width - 340) < 0.5;
    private void QueueUiSave() { if (!IsLoaded) return; uiTimer.Stop(); uiTimer.Start(); }
    private void SaveGeometry()
    {
        var rect = WindowState == WindowState.Normal ? new Rect(Left, Top, ActualWidth, ActualHeight) : RestoreBounds;
        var ratio = PromptEditor.EditRatio;
        vm.SaveUi(vm.Ui with { Width = rect.Width, Height = rect.Height, Left = rect.Left, Top = rect.Top,
            NavWidth = vm.WorkspaceIndex == 0 ? NavColumn.ActualWidth : vm.Ui.NavWidth,
            PromptWidth = vm.WorkspaceIndex == 0 ? PromptColumn.ActualWidth : vm.Ui.PromptWidth,
            EditRatio = ratio });
    }
    private void NavigationChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
    {
        if (syncingNavigation || e.NewValue is not NavigationNode node) return;
        vm.Navigate.Execute(node);
    }
    private void SyncNavigationSelection()
    {
        if (!IsLoaded) return;
        var path = new List<NavigationNode>();
        if (!TryFindNavigationPath(vm.Navigation, vm.BrowseKey, path)) return;
        syncingNavigation = true;
        try
        {
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
        if (ctrl && e.Key == Key.F) { if (vm.WorkspaceIndex == 1) PromptEditor.FocusFind(); else DictionaryWorkspace.FocusSearch(); e.Handled = true; return; }
        if (Keyboard.FocusedElement is TextBox) return;
        if (ctrl && e.Key == Key.Z) vm.Undo.Execute(null);
        else if (ctrl && e.Key == Key.Y) vm.Redo.Execute(null);
        else if (vm.WorkspaceIndex == 1 && ctrl && e.Key == Key.A) vm.SelectAll();
        else if (vm.WorkspaceIndex == 1 && e.Key == Key.Escape) vm.ClearSelection();
        else if (vm.WorkspaceIndex == 1 && e.Key == Key.Delete) vm.Delete.Execute(null);
        else return;
        e.Handled = true;
    }
    private void OpenPresetDialog()
    {
        if (presetDialog is { IsVisible: true }) { presetDialog.Activate(); return; }
        presetDialog = new GenerationPresetDialog(vm) { Owner = this };
        presetDialog.Closed += (_, _) => presetDialog = null;
        presetDialog.Show();
    }
    private void OpenForgeSettingsDialog()
    {
        if (forgeSettingsDialog is { IsVisible: true }) { forgeSettingsDialog.Activate(); return; }
        forgeSettingsDialog = new ForgeSettingsDialog(vm) { Owner = this };
        forgeSettingsDialog.Closed += (_, _) => forgeSettingsDialog = null;
        forgeSettingsDialog.Show();
    }
}
