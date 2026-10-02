using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Threading;
using DanbooruTagTool.App;
using DanbooruTagTool.App.Views;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

[Collection("WPF composition")]
public sealed class Issue245WpfTests
{
    [Theory]
    [InlineData(900, 560)] [InlineData(1280, 720)] [InlineData(1600, 900)] [InlineData(2560, 1440)]
    public void NativeGroupResultsRemainReachableAndCreateLibraryShareOwners(int width, int height)
    {
        Exception? failure = null;
        var thread = new Thread(() =>
        {
            MainWindow? w = null;
            try
            {
                var root = new DirectoryInfo(AppContext.BaseDirectory);
                while (root is not null && !File.Exists(Path.Combine(root.FullName, Issue223BrowseGroupImporter.GroupsPath))) root = root.Parent;
                Assert.NotNull(root);
                var entries = Issue70CatalogOverlayImporter.Read(Path.Combine(root!.FullName, Issue70CatalogOverlayImporter.RelativePath));
                entries = Issue216BrowseHomeImporter.Apply(Path.Combine(root.FullName, Issue216BrowseHomeImporter.RelativePath), entries);
                entries = Issue223BrowseGroupImporter.Apply(Path.Combine(root.FullName, Issue223BrowseGroupImporter.GroupsPath), Path.Combine(root.FullName, Issue223BrowseGroupImporter.MembersPath), entries);
                var catalog = new Catalog(entries);
                using var d = new TempDirectory();
                var vm = new MainViewModel(catalog, new MemoryStore(), new MemoryClipboard(), paths: new(d.Path));
                w = new MainWindow(vm) { Width = width, Height = height, WindowState = WindowState.Normal, ShowInTaskbar = false };
                w.Show(); vm.Dictionary.OpenRelated(catalog.Resolve("fire_emblem")!); Pump(w);
                Assert.Equal(17, vm.Dictionary.BrowseGroupOptions.Count);
                var dictionary = (FrameworkElement)w.FindName("DictionaryWorkspace");
                var chosen = Children<Button>(dictionary).Single(b => b.DataContext is DictionaryWorkspaceViewModel.GroupOption g && g.Id == "fire_emblem:_three_houses");
                chosen.Command!.Execute(chosen.CommandParameter); Pump(w);
                var list = Children<ListBox>(dictionary).Single(l => l.Name == "DictionaryList");
                Assert.True(list.ActualHeight > 80, $"requested={width}x{height}; actual={w.ActualWidth}x{w.ActualHeight}; list={list.ActualHeight}");
                Assert.Equal(45, vm.Results.Count); Assert.False(vm.Dictionary.ShowBrowseGroupCandidates);
                Assert.True(list.ActualWidth > 250);
                vm.Dictionary.BackToBrowseGroups(); Pump(w);
                Assert.True(vm.Dictionary.ShowBrowseGroupCandidates); Assert.Empty(vm.Results);
                var header = (FrameworkElement)w.FindName("GlobalHeader");
                foreach (var button in Children<Button>(header))
                { var pos = button.TranslatePoint(new Point(), header); Assert.True(pos.X >= 0 && pos.X + button.ActualWidth <= header.ActualWidth + 1); }
                var tabs = (TabControl)w.FindName("Workspaces");
                Assert.Equal(new[] { "作成", "タグ探索", "ライブラリ" }, tabs.Items.Cast<TabItem>().Select(t => t.Header));
                vm.ShellWorkspaceIndex = 0; vm.CreatePageIndex = 0; Pump(w);
                var positiveEditor = (FrameworkElement)w.FindName("PromptEditor");
                Assert.True(Children<ScrollViewer>(positiveEditor).Single(s => s.Name == "EditorScroll").ActualHeight > 40, $"Current Positive chips must remain reachable: editor={positiveEditor.ActualHeight}; chips={Children<ScrollViewer>(positiveEditor).Single(s => s.Name == "EditorScroll").ActualHeight}; window={w.ActualHeight}");
                Assert.True(Children<TextBox>(positiveEditor).Single(s => s.Name == "EnglishPreview").ActualHeight > 20, "Current output preview must remain reachable.");
                Assert.Contains(Children<Button>(positiveEditor), b => b.Content as string == "Positiveをコピー");
                vm.CreatePageIndex = 1; Pump(w);
                Assert.Contains(Children<Button>((FrameworkElement)w.FindName("NegativeEditor")), b => b.Content as string == "NegativeをRaw編集");
                vm.CreatePageIndex = 3; Pump(w);
                Assert.Same(vm.LoraLibrary, Children<LoraQuickUseView>(w).Single().DataContext);
                vm.ShellWorkspaceIndex = 2; vm.LibrarySubtypeIndex = 1; Pump(w);
                Assert.Same(vm.LoraLibrary, ((FrameworkElement)w.FindName("LoraLibraryWorkspace")).DataContext);
            }
            catch (Exception e) { failure = e; }
            finally { w?.Close(); }
        });
        thread.SetApartmentState(ApartmentState.STA); thread.Start(); thread.Join();
        if (failure is not null) throw new Xunit.Sdk.XunitException(failure.ToString());
    }
    private static void Pump(Window w)
    {
        var frame = new DispatcherFrame(); var timer = new DispatcherTimer(DispatcherPriority.Background, w.Dispatcher) { Interval = TimeSpan.FromMilliseconds(100) };
        timer.Tick += (_, _) => { timer.Stop(); frame.Continue = false; }; timer.Start(); Dispatcher.PushFrame(frame); w.UpdateLayout();
    }
    private static IEnumerable<T> Children<T>(DependencyObject root) where T : DependencyObject
    {
        for (var i = 0; i < VisualTreeHelper.GetChildrenCount(root); i++)
        { var child = VisualTreeHelper.GetChild(root, i); if (child is T t) yield return t; foreach (var d in Children<T>(child)) yield return d; }
    }
}
