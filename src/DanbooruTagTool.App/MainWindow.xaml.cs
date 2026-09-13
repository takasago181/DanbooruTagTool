using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using DanbooruTagTool.App.ViewModels;

namespace DanbooruTagTool.App;

// View-only behavior: focus, pointer geometry, insertion feedback and window sizing.
// All Prompt mutations and selection rules are delegated to the ViewModel/Core.
public partial class MainWindow : Window
{
    private readonly MainViewModel vm;
    private readonly DispatcherTimer searchTimer = new() { Interval = TimeSpan.FromMilliseconds(150) };
    private readonly DispatcherTimer feedbackTimer = new() { Interval = TimeSpan.FromSeconds(2) };
    private readonly DispatcherTimer uiTimer = new() { Interval = TimeSpan.FromMilliseconds(400) };
    private Point dragStart;
    private ChipViewModel? pendingChip;
    private bool deferredSelection;
    private int dropGap;
    public MainWindow(MainViewModel vm)
    {
        this.vm = vm; InitializeComponent(); DataContext = vm;
        var defaultHeight = Math.Abs(vm.Ui.Height - 820) < 0.5 ? 720 : vm.Ui.Height;
        Width = Math.Max(MinWidth, vm.Ui.Width); Height = Math.Max(MinHeight, defaultHeight);
        Left = Math.Clamp(vm.Ui.Left, SystemParameters.VirtualScreenLeft, SystemParameters.VirtualScreenLeft + SystemParameters.VirtualScreenWidth - 100);
        Top = Math.Clamp(vm.Ui.Top, SystemParameters.VirtualScreenTop, SystemParameters.VirtualScreenTop + SystemParameters.VirtualScreenHeight - 100);
        var navWidth = Math.Abs(vm.Ui.NavWidth - 210) < 0.5 ? 230 : vm.Ui.NavWidth;
        // Values written by the previous layout were 300 (old XAML default) or
        // 340 (the persisted UiState default). Migrate only those legacy
        // defaults; a wider splitter value is an explicit user choice.
        var promptWidth = IsLegacyPromptWidth(vm.Ui.PromptWidth) ? 230 : vm.Ui.PromptWidth;
        NavColumn.Width = new(Math.Max(180, navWidth)); PromptColumn.Width = new(Math.Max(200, promptWidth));
        EditorColumn.Width = new(Math.Clamp(vm.Ui.EditRatio, .25, .85), GridUnitType.Star); EnglishColumn.Width = new(1 - Math.Clamp(vm.Ui.EditRatio, .25, .85), GridUnitType.Star);
        searchTimer.Tick += (_, _) => { searchTimer.Stop(); vm.RefreshResults(); };
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
                Dispatcher.BeginInvoke(() => { DirectEditor.Focus(); DirectEditor.SelectAll(); }, DispatcherPriority.Input);
            }
        };
        vm.ResultsRestored += () => Dispatcher.BeginInvoke(() => FindChild<ScrollViewer>(DictionaryList)?.ScrollToVerticalOffset(vm.RestoreScroll), DispatcherPriority.Loaded);
        vm.ScrollToChip += id => { var index = vm.Chips.ToList().FindIndex(c => c.Id == id); if (index >= 0 && EditorItems.ItemContainerGenerator.ContainerFromIndex(index) is FrameworkElement item) item.BringIntoView(); };
        SizeChanged += (_, _) => QueueUiSave(); LocationChanged += (_, _) => QueueUiSave();
        Closing += (_, _) => { SaveGeometry(); searchTimer.Stop(); feedbackTimer.Stop(); uiTimer.Stop(); };
        Loaded += (_, _) => { vm.UpdateChipLanguage(); FindChild<ScrollViewer>(DictionaryList)?.ScrollToVerticalOffset(vm.RestoreScroll); };
    }
    private static bool IsLegacyPromptWidth(double width) => Math.Abs(width - 300) < 0.5 || Math.Abs(width - 340) < 0.5;
    private void QueueUiSave() { if (!IsLoaded) return; uiTimer.Stop(); uiTimer.Start(); }
    private void SaveGeometry()
    {
        var rect = WindowState == WindowState.Normal ? new Rect(Left, Top, ActualWidth, ActualHeight) : RestoreBounds;
        vm.SaveUi(vm.Ui with { Width = rect.Width, Height = rect.Height, Left = rect.Left, Top = rect.Top, NavWidth = NavColumn.ActualWidth, PromptWidth = PromptColumn.ActualWidth, EditRatio = EditorColumn.ActualWidth / Math.Max(1, EditorColumn.ActualWidth + EnglishColumn.ActualWidth) });
    }
    private void SearchChanged(object sender, TextChangedEventArgs e) { if (DataContext == null) return; searchTimer.Stop(); searchTimer.Start(); }
    private void NavigationChanged(object sender, RoutedPropertyChangedEventArgs<object> e) { if (e.NewValue is NavigationNode node) vm.Navigate.Execute(node); }
    private void WorkspaceChanged(object sender, SelectionChangedEventArgs e) { if (DataContext != null && e.Source == Workspaces) vm.UpdateChipLanguage(); }
    private void SplitterChanged(object sender, System.Windows.Controls.Primitives.DragCompletedEventArgs e) => SaveGeometry();
    private void BrowseScrolled(object sender, ScrollChangedEventArgs e) { if (DataContext != null) { vm.BrowseScroll = e.VerticalOffset; QueueUiSave(); } }
    private void FindKeyDown(object sender, KeyEventArgs e) { if (e.Key == Key.Enter) { vm.FindNext(Keyboard.Modifiers.HasFlag(ModifierKeys.Shift)); e.Handled = true; } }
    private void WindowKeyDown(object sender, KeyEventArgs e)
    {
        bool ctrl = Keyboard.Modifiers.HasFlag(ModifierKeys.Control);
        if (ctrl && e.Key == Key.F) { if (vm.WorkspaceIndex == 1) FindBox.Focus(); else SearchBox.Focus(); e.Handled = true; return; }
        if (Keyboard.FocusedElement is TextBox) return;
        if (ctrl && e.Key == Key.Z) vm.Undo.Execute(null);
        else if (ctrl && e.Key == Key.Y) vm.Redo.Execute(null);
        else if (vm.WorkspaceIndex == 1 && ctrl && e.Key == Key.A) vm.SelectAll();
        else if (vm.WorkspaceIndex == 1 && e.Key == Key.Escape) vm.ClearSelection();
        else if (vm.WorkspaceIndex == 1 && e.Key == Key.Delete) vm.Delete.Execute(null);
        else return;
        e.Handled = true;
    }
    private void ChipMouseDown(object sender, MouseButtonEventArgs e)
    {
        if (FindAncestor<Button>(e.OriginalSource as DependencyObject) != null) return;
        if (sender is not FrameworkElement { DataContext: ChipViewModel chip }) return;
        Keyboard.ClearFocus(); Focus(); pendingChip = chip; dragStart = e.GetPosition(EditorItems);
        bool ctrl = Keyboard.Modifiers.HasFlag(ModifierKeys.Control), shift = Keyboard.Modifiers.HasFlag(ModifierKeys.Shift);
        deferredSelection = chip.Selected && !ctrl && !shift;
        if (!deferredSelection) vm.Select(chip.Id, ctrl, shift);
        e.Handled = true;
    }
    private void ChipMouseUp(object sender, MouseButtonEventArgs e)
    { if (pendingChip != null && deferredSelection) vm.Select(pendingChip.Id); pendingChip = null; }
    private void ChipMouseMove(object sender, MouseEventArgs e)
    {
        if (pendingChip == null || e.LeftButton != MouseButtonState.Pressed) return;
        var p = e.GetPosition(EditorItems);
        if (Math.Abs(p.X - dragStart.X) < SystemParameters.MinimumHorizontalDragDistance && Math.Abs(p.Y - dragStart.Y) < SystemParameters.MinimumVerticalDragDistance) return;
        var ids = vm.BeginDrag(pendingChip.Id); pendingChip = null;
        DragDrop.DoDragDrop((DependencyObject)sender, new DataObject("PromptItemIds", ids), DragDropEffects.Move);
        InsertionMarker.Visibility = Visibility.Collapsed;
    }
    private void EditorDragOver(object sender, DragEventArgs e)
    {
        if (!e.Data.GetDataPresent("PromptItemIds")) { e.Effects = DragDropEffects.None; return; }
        var pointer = e.GetPosition(EditorScroll);
        if (pointer.Y < 35) EditorScroll.ScrollToVerticalOffset(EditorScroll.VerticalOffset - 18);
        else if (pointer.Y > EditorScroll.ActualHeight - 35) EditorScroll.ScrollToVerticalOffset(EditorScroll.VerticalOffset + 18);
        dropGap = vm.Chips.Count; Point marker = new(4, 4); double height = 35;
        for (int i = 0; i < vm.Chips.Count; i++)
        {
            if (EditorItems.ItemContainerGenerator.ContainerFromIndex(i) is not FrameworkElement item) continue;
            var point = item.TranslatePoint(new(0, 0), EditorScroll); height = item.ActualHeight;
            marker = new(point.X + item.ActualWidth, point.Y);
            if (pointer.Y < point.Y + height && (pointer.Y < point.Y || pointer.X < point.X + item.ActualWidth / 2)) { dropGap = i; marker = point; break; }
        }
        Canvas.SetLeft(InsertionMarker, Math.Max(0, marker.X)); Canvas.SetTop(InsertionMarker, marker.Y); InsertionMarker.Height = height; InsertionMarker.Visibility = Visibility.Visible;
        e.Effects = DragDropEffects.Move; e.Handled = true;
    }
    private void EditorDrop(object sender, DragEventArgs e) { if (e.Data.GetData("PromptItemIds") is Guid[] ids) vm.Move(ids, dropGap); InsertionMarker.Visibility = Visibility.Collapsed; e.Handled = true; }
    private void EditorDragLeave(object sender, DragEventArgs e) => InsertionMarker.Visibility = Visibility.Collapsed;
    private static T? FindChild<T>(DependencyObject parent) where T : DependencyObject
    { for (int i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++) { var child = VisualTreeHelper.GetChild(parent, i); if (child is T result) return result; if (FindChild<T>(child) is T nested) return nested; } return null; }
    private static T? FindAncestor<T>(DependencyObject? child) where T : DependencyObject
    { while (child != null) { if (child is T value) return value; child = VisualTreeHelper.GetParent(child); } return null; }
}
