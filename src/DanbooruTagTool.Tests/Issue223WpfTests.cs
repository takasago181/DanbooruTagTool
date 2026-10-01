using System.IO;
using System.Reflection;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using DanbooruTagTool.App;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

[Collection("WPF composition")]
public sealed class Issue223WpfTests
{
    [Theory]
    [InlineData(1200)]
    [InlineData(1500)]
    public void RealWpfGroupButtonsBindWrapFilterAndReturn(int width)
    {
        Exception? failure = null;
        var thread = new Thread(() =>
        {
            MainWindow? window = null;
            try
            {
                var root = new DirectoryInfo(AppContext.BaseDirectory);
                while (root is not null && !File.Exists(Path.Combine(root.FullName, Issue223BrowseGroupImporter.GroupsPath))) root = root.Parent;
                Assert.NotNull(root);
                var entries = Issue70CatalogOverlayImporter.Read(Path.Combine(root!.FullName, Issue70CatalogOverlayImporter.RelativePath));
                entries = Issue216BrowseHomeImporter.Apply(Path.Combine(root.FullName, Issue216BrowseHomeImporter.RelativePath), entries);
                entries = Issue223BrowseGroupImporter.Apply(Path.Combine(root.FullName, Issue223BrowseGroupImporter.GroupsPath),
                    Path.Combine(root.FullName, Issue223BrowseGroupImporter.MembersPath), entries);
                var catalog = new Catalog(entries);
                var vm = new MainViewModel(catalog, new MemoryStore(), new MemoryClipboard());
                window = new MainWindow(vm) { Width = width, Height = 900, WindowState = WindowState.Normal, ShowInTaskbar = false };
                window.Show();
                vm.Dictionary.OpenRelated(catalog.Resolve("fire_emblem")!);
                Pump(window.Dispatcher);
                window.UpdateLayout();
                var view = (FrameworkElement)window.GetType().GetField("DictionaryWorkspace", BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(window)!;
                var buttons = Children<Button>(view).Where(b => b.DataContext is DictionaryWorkspaceViewModel.GroupOption).ToArray();
                Assert.Equal(17, buttons.Length); // 16 reviewed groups + unclassified
                Assert.Empty(vm.Results);
                Assert.False(vm.Dictionary.ShowUnifiedRefinement);
                Assert.DoesNotContain(Children<TextBlock>(view), t => t.IsVisible && t.Text == "左からカテゴリを選ぶか、タグ名を検索してください。");
                foreach (var button in buttons)
                {
                    var label = Assert.IsType<TextBlock>(button.Content);
                    Assert.Equal(TextWrapping.Wrap, label.TextWrapping);
                    Assert.Equal(TextTrimming.None, label.TextTrimming);
                    Assert.Equal(((DictionaryWorkspaceViewModel.GroupOption)button.DataContext).Label, label.Text);
                    Assert.True(button.ActualHeight >= label.ActualHeight);
                    Assert.True(button.ActualWidth <= view.ActualWidth);
                }
                Render(view, width, "groups");
                var chosen = buttons.First(b => ((DictionaryWorkspaceViewModel.GroupOption)b.DataContext).Id == "fire_emblem:_three_houses");
                Assert.True(chosen.Command!.CanExecute(chosen.CommandParameter));
                chosen.Command.Execute(chosen.CommandParameter);
                Pump(window.Dispatcher);
                Assert.Equal(catalog.BrowseHomeCharacters("fire_emblem", "fire_emblem:_three_houses").Count, vm.Results.Count);
                Assert.All(vm.Results, r => Assert.Equal("fire_emblem:_three_houses", r.Entry.BrowseGroup!.Id));
                Assert.True(Children<ListBox>(view).First(l => l.Name == "DictionaryList").ActualHeight > 80);
                Render(view, width, "characters");
                var back = Children<Button>(view).First(b => b.Content as string == "グループ一覧に戻る");
                back.Command!.Execute(back.CommandParameter);
                Pump(window.Dispatcher);
                Assert.Empty(vm.Results);
                Assert.Null(vm.Dictionary.SelectedBrowseGroupId);
                vm.Dictionary.ClearRelatedBrowse();
                Pump(window.Dispatcher);
                Assert.False(vm.Dictionary.ShowBrowseGroups);
            }
            catch (Exception ex) { failure = ex; }
            finally { window?.Close(); }
        });
        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        thread.Join();
        if (failure is not null) throw new Xunit.Sdk.XunitException(failure.ToString());
    }
    private static IEnumerable<T> Children<T>(DependencyObject parent) where T : DependencyObject
    {
        for (var i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
        {
            var child = VisualTreeHelper.GetChild(parent, i);
            if (child is T match) yield return match;
            foreach (var nested in Children<T>(child)) yield return nested;
        }
    }
    private static void Pump(Dispatcher dispatcher)
    {
        var frame = new DispatcherFrame();
        var timer = new DispatcherTimer(DispatcherPriority.Background, dispatcher) { Interval = TimeSpan.FromMilliseconds(75) };
        timer.Tick += (_, _) => { timer.Stop(); frame.Continue = false; };
        timer.Start(); Dispatcher.PushFrame(frame);
    }
    private static void Render(FrameworkElement view, int width, string state)
    {
        if (Environment.GetEnvironmentVariable("DTT_ISSUE223_RENDER_DIR") is not { Length: > 0 } directory) return;
        Directory.CreateDirectory(directory);
        var bitmap = new RenderTargetBitmap((int)Math.Ceiling(view.ActualWidth), (int)Math.Ceiling(view.ActualHeight), 96, 96, PixelFormats.Pbgra32);
        var drawing = new DrawingVisual();
        using (var context = drawing.RenderOpen())
            context.DrawRectangle(new VisualBrush(view), null, new Rect(0, 0, view.ActualWidth, view.ActualHeight));
        bitmap.Render(drawing);
        var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap));
        using var stream = File.Create(Path.Combine(directory, $"browse-{width}-{state}.png")); encoder.Save(stream);
    }
}
