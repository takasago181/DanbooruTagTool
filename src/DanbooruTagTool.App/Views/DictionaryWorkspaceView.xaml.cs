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
            RestoreScroll();
        };
        Unloaded += (_, _) => searchTimer.Stop();
    }

    public void FocusSearch() => SearchBox.Focus();

    private DictionaryWorkspaceViewModel? ViewModel => DataContext as DictionaryWorkspaceViewModel;
    private void SearchChanged(object sender, TextChangedEventArgs e) { searchTimer.Stop(); searchTimer.Start(); }
    private void DictionaryListSizeChanged(object sender, SizeChangedEventArgs e)
    {
        var available = e.NewSize.Width - SystemParameters.VerticalScrollBarWidth - 12;
        ViewModel?.SetSurfaceWidth(available);
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
        if (sender is FrameworkElement { DataContext: EntryViewModel row } && ViewModel is { } vm)
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
        int? offset = e.Key switch
        {
            Key.Left when vm.DictionaryColumnCount == 2 => -1,
            Key.Right when vm.DictionaryColumnCount == 2 => 1,
            Key.Up => -vm.DictionaryColumnCount,
            Key.Down => vm.DictionaryColumnCount,
            Key.PageUp => -10 * vm.DictionaryColumnCount,
            Key.PageDown => 10 * vm.DictionaryColumnCount,
            _ => null
        };
        if (offset.HasValue) vm.MoveResultSelection(offset.Value);
        else if (e.Key == Key.Home) vm.SelectResultBoundary(false);
        else if (e.Key == Key.End) vm.SelectResultBoundary(true);
        else if (e.Key == Key.Enter && vm.SelectedEntry is { } selected) vm.InspectEntry.Execute(selected);
        else return;
        e.Handled = true;
        if (vm.SelectedEntry is not { } current) return;
        var row = vm.DictionaryRows.FirstOrDefault(candidate => ReferenceEquals(candidate.First, current) || ReferenceEquals(candidate.Second, current));
        if (row == null) return;
        DictionaryList.ScrollIntoView(row);
        Dispatcher.BeginInvoke(() => (DictionaryList.ItemContainerGenerator.ContainerFromItem(row) as FrameworkElement)?.BringIntoView(), DispatcherPriority.Loaded);
    }
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
