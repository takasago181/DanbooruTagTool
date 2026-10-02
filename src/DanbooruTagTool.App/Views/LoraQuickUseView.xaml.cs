using System.Windows;
using System.Windows.Controls;
using DanbooruTagTool.App.ViewModels;
namespace DanbooruTagTool.App.Views;
public partial class LoraQuickUseView : UserControl
{
    public LoraQuickUseView() => InitializeComponent();
    private LoraLibraryViewModel? Vm => DataContext as LoraLibraryViewModel;
    private async void OnLoaded(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.InitializeAsync(); }
    private async void SearchClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.RefreshAsync(); }
    private async void PreviousClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.RefreshAsync(-100); }
    private async void NextClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.RefreshAsync(100); }
    private void InsertClick(object sender, RoutedEventArgs e) => Vm?.Insert(false);
    private void RecipeClick(object sender, RoutedEventArgs e) => Vm?.Insert(true);
    private void AppendNegativeClick(object sender, RoutedEventArgs e) => Vm?.AppendNegative();
}
