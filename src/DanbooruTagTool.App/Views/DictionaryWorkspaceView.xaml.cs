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
        UpdateSurfaceWidth(e.NewSize.Width);
    }
    private void UpdateSurfaceWidth(double? width = null)
    {
        var actualWidth = width ?? DictionaryList.ActualWidth;
        if (actualWidth <= 0) return;
        ViewModel?.SetSurfaceWidth(actualWidth - SystemParameters.VerticalScrollBarWidth - 12);
    }
    private void QueueSurfaceWidthUpdate()
    {
        if (!IsLoaded) return;
        Dispatcher.BeginInvoke(() => UpdateSurfaceWidth(), DispatcherPriority.Loaded);
        Dispatcher.BeginInvoke(() => UpdateSurfaceWidth(), DispatcherPriority.ApplicationIdle);
    }
    private void BrowseScrolled(object sender, ScrollChangedEventArgs e)
    {
        if (ViewModel == null) return;
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
        if (DictionaryList.SelectedIndex >= 0) DictionaryList.SelectedIndex = -1;
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
        var row = vm.DictionaryRows.FirstOrDefault(candidate => ReferenceEquals(candidate.First, current) || ReferenceEquals(candidate.Second, current));
        if (row == null) return;
        DictionaryList.ScrollIntoView(row);
        Dispatcher.BeginInvoke(() => (DictionaryList.ItemContainerGenerator.ContainerFromItem(row) as FrameworkElement)?.BringIntoView(), DispatcherPriority.Loaded);
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
        Dispatcher.BeginInvoke(() => FindChild<ScrollViewer>(DictionaryList)?.ScrollToVerticalOffset(ViewModel.RestoreScroll), DispatcherPriority.Loaded);
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
