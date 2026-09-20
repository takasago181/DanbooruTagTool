using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using DanbooruTagTool.App.ViewModels;

namespace DanbooruTagTool.App.Views;

public partial class DictionaryWorkspaceView : UserControl
{
    private readonly DispatcherTimer searchTimer = new() { Interval = TimeSpan.FromMilliseconds(150) };
    private bool attached;
    private bool synchronizingScroll;

    public event Action? BrowseScrollChanged;

    public DictionaryWorkspaceView()
    {
        InitializeComponent();
        searchTimer.Tick += (_, _) => { searchTimer.Stop(); ViewModel?.RefreshResults(); };
        Loaded += (_, _) =>
        {
            if (!attached && ViewModel is { } vm)
            {
                attached = true;
                vm.ResultsRestored += RestoreScroll;
            }
            UpdateSurfaceWidth();
            QueueSurfaceWidthUpdate();
            RestoreScroll();
        };
        DataContextChanged += (_, _) =>
        {
            QueueSurfaceWidthUpdate();
        };
        Unloaded += (_, _) => searchTimer.Stop();
    }

    public void FocusSearch() => SearchBox.Focus();

    private DictionaryWorkspaceViewModel? ViewModel => DataContext as DictionaryWorkspaceViewModel;
    private void SearchChanged(object sender, TextChangedEventArgs e) { searchTimer.Stop(); searchTimer.Start(); }
    private void DictionaryListSizeChanged(object sender, SizeChangedEventArgs e)
    {
        UpdateSurfaceWidth();
    }
    private void UpdateSurfaceWidth(double? width = null)
    {
        var actualWidth = width ?? DictionaryResultSurface.ActualWidth;
        if (actualWidth <= 0) return;
        ViewModel?.SetSurfaceWidth(actualWidth - SystemParameters.VerticalScrollBarWidth - 12);
        UpdateColumnLayout();
    }
    private void QueueSurfaceWidthUpdate()
    {
        if (!IsLoaded) return;
        Dispatcher.BeginInvoke(() => UpdateSurfaceWidth(), DispatcherPriority.Loaded);
        Dispatcher.BeginInvoke(() => UpdateSurfaceWidth(), DispatcherPriority.ApplicationIdle);
    }
    private void BrowseScrolled(object sender, ScrollChangedEventArgs e)
    {
        if (ViewModel == null || synchronizingScroll) return;
        var target = ReferenceEquals(sender, DictionaryList) ? DictionaryRightList : DictionaryList;
        var targetScroll = FindChild<ScrollViewer>(target);
        if (targetScroll != null && Math.Abs(targetScroll.VerticalOffset - e.VerticalOffset) > 0.5)
        {
            synchronizingScroll = true;
            try { targetScroll.ScrollToVerticalOffset(e.VerticalOffset); }
            finally { synchronizingScroll = false; }
        }
        ViewModel.BrowseScroll = e.VerticalOffset;
        BrowseScrollChanged?.Invoke();
    }
    private void DictionaryCardMouseUp(object sender, MouseButtonEventArgs e)
    {
        if (FindAncestor<Button>(e.OriginalSource as DependencyObject) != null) return;
        var content = sender is ContentPresenter presenter ? presenter.Content : null;
        var row = ResolveCardEntry(content, e.OriginalSource as DependencyObject);
        if (row != null && ViewModel is { } vm)
        {
            vm.InspectEntry.Execute(row);
            e.Handled = true;
        }
    }
    private void DictionarySelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (sender is ListBox list && list.SelectedIndex >= 0) list.SelectedIndex = -1;
    }
    private void DictionaryPreviewKeyDown(object sender, KeyEventArgs e)
    {
        if (ViewModel is not { } vm) return;
        var action = DictionaryKeyboardNavigation.Resolve(e.Key, vm.DictionaryColumnCount);
        if (action.Kind == DictionaryKeyboardActionKind.None) return;
        if (action.Kind == DictionaryKeyboardActionKind.Move)
            vm.MoveResultSelection(action.Offset);
        else if (action.Kind == DictionaryKeyboardActionKind.Home)
            vm.SelectResultBoundary(false);
        else if (action.Kind == DictionaryKeyboardActionKind.End)
            vm.SelectResultBoundary(true);
        else if (action.Kind == DictionaryKeyboardActionKind.Inspect && vm.SelectedEntry is { } selected)
            vm.InspectEntry.Execute(selected);
        e.Handled = true;
        if (vm.SelectedEntry is not { } current) return;
        var list = vm.DictionaryFirstColumn.Contains(current) ? DictionaryList : DictionaryRightList;
        list.ScrollIntoView(current);
        Dispatcher.BeginInvoke(() => (list.ItemContainerGenerator.ContainerFromItem(current) as FrameworkElement)?.BringIntoView(), DispatcherPriority.Loaded);
    }
    private static EntryViewModel? FindEntryDataContext(DependencyObject? source)
    {
        while (source != null)
        {
            if (source is FrameworkElement { DataContext: EntryViewModel row }) return row;
            source = VisualTreeHelper.GetParent(source);
        }
        return null;
    }
    public static EntryViewModel? ResolveCardEntry(object? content, DependencyObject? source) => content as EntryViewModel ?? FindEntryDataContext(source);
    private void RestoreScroll()
    {
        if (ViewModel == null) return;
        Dispatcher.BeginInvoke(() =>
        {
            FindChild<ScrollViewer>(DictionaryList)?.ScrollToVerticalOffset(ViewModel.RestoreScroll);
            FindChild<ScrollViewer>(DictionaryRightList)?.ScrollToVerticalOffset(ViewModel.RestoreScroll);
        }, DispatcherPriority.Loaded);
    }
    private void UpdateColumnLayout()
    {
        var twoColumns = ViewModel?.DictionaryColumnCount == 2;
        DictionaryRightColumn.Width = twoColumns ? new GridLength(1, GridUnitType.Star) : new GridLength(0);
        DictionaryRightList.Visibility = twoColumns ? Visibility.Visible : Visibility.Collapsed;
    }
    private static T? FindChild<T>(DependencyObject parent) where T : DependencyObject
    {
        for (int i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
        {
            var child = VisualTreeHelper.GetChild(parent, i);
            if (child is T result) return result;
            if (FindChild<T>(child) is T nested) return nested;
        }
        return null;
    }
    private static T? FindAncestor<T>(DependencyObject? child) where T : DependencyObject
    {
        while (child != null) { if (child is T value) return value; child = VisualTreeHelper.GetParent(child); }
        return null;
    }
}
