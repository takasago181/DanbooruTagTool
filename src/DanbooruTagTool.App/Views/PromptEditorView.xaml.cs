using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using DanbooruTagTool.App.ViewModels;
using DragEventArgs = System.Windows.DragEventArgs;
using MouseEventArgs = System.Windows.Input.MouseEventArgs;
using Point = System.Windows.Point;

namespace DanbooruTagTool.App.Views;

public partial class PromptEditorView : UserControl
{
    private Point dragStart;
    private ChipViewModel? pendingChip;
    private bool deferredSelection;
    private int dropGap;

    public event Action? EditRatioChanged;
    public PromptEditorView() => InitializeComponent();
    private PromptEditorViewModel? ViewModel => DataContext as PromptEditorViewModel;
    public double EditRatio => EditorColumn.Width.Value / (EditorColumn.Width.Value + EnglishColumn.Width.Value);
    public void ApplyEditRatio(double ratio)
    {
        ratio = Math.Clamp(ratio, .3, .85);
        EditorColumn.Width = new(ratio, GridUnitType.Star); EnglishColumn.Width = new(1 - ratio, GridUnitType.Star);
    }
    public void FocusFind() => FindBox.Focus();
    public void FocusDirectEditor() { DirectEditor.Focus(); DirectEditor.SelectAll(); }
    public void BringChipIntoView(Guid id)
    {
        var index = ViewModel?.Chips.ToList().FindIndex(c => c.Id == id) ?? -1;
        if (index >= 0 && EditorItems.ItemContainerGenerator.ContainerFromIndex(index) is FrameworkElement item) item.BringIntoView();
    }
    private void SplitterChanged(object sender, System.Windows.Controls.Primitives.DragCompletedEventArgs e) => EditRatioChanged?.Invoke();
    private void FindKeyDown(object sender, KeyEventArgs e) { if (e.Key == Key.Enter && ViewModel is { } vm) { vm.FindNext(Keyboard.Modifiers.HasFlag(ModifierKeys.Shift)); e.Handled = true; } }
    private void ChipMouseDown(object sender, MouseButtonEventArgs e)
    {
        if (ViewModel is not { CanEditOrderedPrompt: true } vm || FindAncestor<Button>(e.OriginalSource as DependencyObject) != null || sender is not FrameworkElement { DataContext: ChipViewModel chip }) return;
        Keyboard.ClearFocus(); Focus(); pendingChip = chip; dragStart = e.GetPosition(EditorItems);
        bool ctrl = Keyboard.Modifiers.HasFlag(ModifierKeys.Control), shift = Keyboard.Modifiers.HasFlag(ModifierKeys.Shift);
        deferredSelection = chip.Selected && !ctrl && !shift;
        if (!deferredSelection) vm.Select(chip.Id, ctrl, shift);
        e.Handled = true;
    }
    private void ChipMouseUp(object sender, MouseButtonEventArgs e) { if (pendingChip != null && ViewModel is { } vm && deferredSelection) vm.Select(pendingChip.Id); pendingChip = null; }
    private void ChipMouseMove(object sender, MouseEventArgs e)
    {
        if (ViewModel is not { CanEditOrderedPrompt: true } vm || pendingChip == null || e.LeftButton != MouseButtonState.Pressed) return;
        var p = e.GetPosition(EditorItems);
        if (Math.Abs(p.X - dragStart.X) < SystemParameters.MinimumHorizontalDragDistance && Math.Abs(p.Y - dragStart.Y) < SystemParameters.MinimumVerticalDragDistance) return;
        var ids = vm.BeginDrag(pendingChip.Id); pendingChip = null;
        DragDrop.DoDragDrop((DependencyObject)sender, new DataObject("PromptItemIds", ids), DragDropEffects.Move); InsertionMarker.Visibility = Visibility.Collapsed;
    }
    private void EditorDragOver(object sender, DragEventArgs e)
    {
        if (ViewModel is not { CanEditOrderedPrompt: true } vm || !e.Data.GetDataPresent("PromptItemIds")) { e.Effects = DragDropEffects.None; return; }
        var pointer = e.GetPosition(EditorScroll);
        if (pointer.Y < 35) EditorScroll.ScrollToVerticalOffset(EditorScroll.VerticalOffset - 18); else if (pointer.Y > EditorScroll.ActualHeight - 35) EditorScroll.ScrollToVerticalOffset(EditorScroll.VerticalOffset + 18);
        dropGap = vm.Chips.Count; Point marker = new(4, 4); double height = 35;
        for (int i = 0; i < vm.Chips.Count; i++) if (EditorItems.ItemContainerGenerator.ContainerFromIndex(i) is FrameworkElement item)
        {
            var point = item.TranslatePoint(new(0, 0), EditorScroll); height = item.ActualHeight; marker = new(point.X + item.ActualWidth, point.Y);
            if (pointer.Y < point.Y + height && (pointer.Y < point.Y || pointer.X < point.X + item.ActualWidth / 2)) { dropGap = i; marker = point; break; }
        }
        Canvas.SetLeft(InsertionMarker, Math.Max(0, marker.X)); Canvas.SetTop(InsertionMarker, marker.Y); InsertionMarker.Height = height; InsertionMarker.Visibility = Visibility.Visible; e.Effects = DragDropEffects.Move; e.Handled = true;
    }
    private void EditorDrop(object sender, DragEventArgs e) { if (ViewModel is { } vm && e.Data.GetData("PromptItemIds") is Guid[] ids) vm.Move(ids, dropGap); InsertionMarker.Visibility = Visibility.Collapsed; e.Handled = true; }
    private void EditorDragLeave(object sender, DragEventArgs e) => InsertionMarker.Visibility = Visibility.Collapsed;
    private static T? FindAncestor<T>(DependencyObject? child) where T : DependencyObject { while (child != null) { if (child is T value) return value; child = VisualTreeHelper.GetParent(child); } return null; }
}
