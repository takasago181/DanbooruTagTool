using System.Reflection;
using System.Windows;
using System.Windows.Controls;
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
                var app = new Application { ShutdownMode = ShutdownMode.OnExplicitShutdown };
                var window = new MainWindow(vm) { WindowState = WindowState.Normal, Width = 1920, Height = 820, ShowInTaskbar = false };
                window.Show();
                Pump(window.Dispatcher, 150);
                window.UpdateLayout();

                var dictionaryView = GetField<FrameworkElement>(window, "DictionaryWorkspace");
                var promptView = GetField<FrameworkElement>(window, "PromptEditor");
                Assert.Same(vm.Dictionary, dictionaryView.DataContext);
                Assert.Same(vm.Prompt, promptView.DataContext);
                dictionaryVm = Assert.IsType<DictionaryWorkspaceViewModel>(dictionaryView.DataContext);
                promptVm = Assert.IsType<PromptEditorViewModel>(promptView.DataContext);

                var list = GetField<ListBox>(dictionaryView, "DictionaryList");
                dictionaryRows = list.Items.Count;
                dictionarySource = list.ItemsSource?.GetType().Name ?? "null";
                Assert.NotEmpty(vm.Dictionary.DictionaryRows);
                Assert.NotEmpty(list.Items);
                Assert.Equal(2, dictionaryVm.DictionaryColumnCount);
                Assert.Equal((dictionaryVm.Results.Count + 1) / 2, dictionaryVm.DictionaryRows.Count);

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

    private static void Pump(Dispatcher dispatcher, int milliseconds)
    {
        var frame = new DispatcherFrame();
        var timer = new DispatcherTimer(DispatcherPriority.Background, dispatcher) { Interval = TimeSpan.FromMilliseconds(milliseconds) };
        timer.Tick += (_, _) => { timer.Stop(); frame.Continue = false; };
        timer.Start();
        Dispatcher.PushFrame(frame);
    }
}
