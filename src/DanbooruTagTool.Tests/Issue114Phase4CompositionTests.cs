using System.Reflection;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Threading;
using DanbooruTagTool.App;
using DanbooruTagTool.App.ViewModels;
using Xunit;

namespace DanbooruTagTool.Tests;

[CollectionDefinition("WPF composition", DisableParallelization = true)]
public sealed class WpfCompositionCollection { }

[Collection("WPF composition")]
public sealed class Issue114Phase4CompositionTests
{
    [Fact]
    public void MainWindowInjectsChildViewModelsAndSuppliesDictionaryAndPromptBindings()
    {
        Exception? failure = null;
        DictionaryWorkspaceViewModel? dictionaryVm = null;
        PromptEditorViewModel? promptVm = null;
        var dictionaryRows = 0;
        var dictionarySource = "";
        var promptEnglishBinding = "";
        var thread = new Thread(() =>
        {
            try
            {
                var vm = Fixtures.Vm();
                vm.Dictionary.Query = "hair";
                vm.Dictionary.RefreshResults();
                var app = new Application { ShutdownMode = ShutdownMode.OnExplicitShutdown };
                var window = new MainWindow(vm) { WindowState = WindowState.Normal, Width = 2560, Height = 1440, ShowInTaskbar = false };
                window.Show();
                Pump(window.Dispatcher, 150);
                window.UpdateLayout();

                var dictionaryView = GetField<FrameworkElement>(window, "DictionaryWorkspace");
                var promptView = GetField<FrameworkElement>(window, "PromptEditor");
                Assert.Same(vm.Dictionary, dictionaryView.DataContext);
                Assert.Same(vm.Prompt, promptView.DataContext);
                dictionaryVm = Assert.IsType<DictionaryWorkspaceViewModel>(dictionaryView.DataContext);
                promptVm = Assert.IsType<PromptEditorViewModel>(promptView.DataContext);

                // GitHub Windows runners expose a small virtual desktop even when the
                // Window requests WQHD. Pin the dictionary surface itself above the
                // accepted two-column threshold so this remains a composition test,
                // not a runner-screen-size test.
                dictionaryView.Width = 900;
                window.UpdateLayout();
                Pump(window.Dispatcher, 100);
                dictionaryView.UpdateLayout();

                var list = GetField<ListBox>(dictionaryView, "DictionaryList");
                dictionaryRows = list.Items.Count;
                dictionarySource = list.ItemsSource?.GetType().Name ?? "null";
                Assert.NotEmpty(vm.Dictionary.DictionaryRows);
                Assert.NotEmpty(list.Items);
                Assert.Equal(2, dictionaryVm.DictionaryColumnCount);
                Assert.Equal((dictionaryVm.Results.Count + 1) / 2, dictionaryVm.DictionaryRows.Count);
                Assert.NotNull(dictionaryVm.DictionaryRows[0].Second);
                var firstItem = list.ItemContainerGenerator.ContainerFromIndex(0) as ListBoxItem;
                Assert.NotNull(firstItem);
                var cardPresenters = FindVisualChildren<ContentPresenter>(firstItem!).Where(p => p.Content is EntryViewModel).ToArray();
                Assert.Equal(2, cardPresenters.Length);
                Assert.All(cardPresenters, presenter =>
                {
                    Assert.Equal(Visibility.Visible, presenter.Visibility);
                    Assert.True(presenter.ActualWidth > 0);
                });

                var navigationTree = GetField<TreeView>(window, "NavigationTree");
                vm.Dictionary.NavigateTo("route:HAIR_FACE");
                Pump(window.Dispatcher, 100);
                Assert.NotNull(navigationTree.SelectedItem);
                vm.Dictionary.ClearUnifiedBrowse();
                Pump(window.Dispatcher, 100);
                Assert.Null(navigationTree.SelectedItem);

                var englishPreview = GetField<TextBox>(promptView, "EnglishPreview");
                promptEnglishBinding = englishPreview.GetBindingExpression(TextBox.TextProperty)?.ParentBinding.Path.Path ?? "none";
                Assert.Equal("English", promptEnglishBinding);
                Assert.NotNull(promptVm.Chips);
                _ = promptVm.English;

                window.Close();
                app.Shutdown();
            }
            catch (Exception ex) { failure = ex; }
        });
        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        thread.Join();
        if (failure != null) throw new Xunit.Sdk.XunitException(failure.ToString());

        Assert.NotNull(dictionaryVm);
        Assert.NotNull(promptVm);
        Assert.True(dictionaryRows > 0, $"Dictionary ListBox rows={dictionaryRows}, source={dictionarySource}");
        Assert.Equal("English", promptEnglishBinding);
    }

    private static T GetField<T>(object target, string name) where T : class =>
        typeof(T) == typeof(FrameworkElement)
            ? (T)(object)(target.GetType().GetField(name, BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(target) as FrameworkElement
                ?? throw new InvalidOperationException($"Field {name} not found"))
            : (target.GetType().GetField(name, BindingFlags.Instance | BindingFlags.NonPublic)?.GetValue(target) as T
                ?? throw new InvalidOperationException($"Field {name} not found"));

    private static IEnumerable<T> FindVisualChildren<T>(DependencyObject parent) where T : DependencyObject
    {
        for (var i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
        {
            var child = VisualTreeHelper.GetChild(parent, i);
            if (child is T match) yield return match;
            foreach (var nested in FindVisualChildren<T>(child)) yield return nested;
        }
    }

    private static void Pump(Dispatcher dispatcher, int milliseconds)
    {
        var frame = new DispatcherFrame();
        var timer = new DispatcherTimer(DispatcherPriority.Background, dispatcher) { Interval = TimeSpan.FromMilliseconds(milliseconds) };
        timer.Tick += (_, _) => { timer.Stop(); frame.Continue = false; };
        timer.Start();
        Dispatcher.PushFrame(frame);
    }
}
