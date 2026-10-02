using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using DanbooruTagTool.App.ViewModels;
using Microsoft.Win32;

namespace DanbooruTagTool.App.Views;
public partial class LoraLibraryView : UserControl
{
    public LoraLibraryView() => InitializeComponent();
    public void FocusSearch() => SearchBox.Focus();
    private LoraLibraryViewModel? Vm => DataContext as LoraLibraryViewModel;
    private async void OnLoaded(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.InitializeAsync(); }
    private async void AddRootClick(object sender, RoutedEventArgs e) { var d = new OpenFolderDialog { Title = "local LoRA root（再帰scan、ファイルを書き換えません）" }; if (Vm is { CanEdit: true } vm && d.ShowDialog() == true) await vm.AddRootAsync(d.FolderName); }
    private async void ScanClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.ScanAsync(); }
    private async void VerifyClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.ScanAsync(true); }
    private async void SearchClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.RefreshAsync(); }
    private async void PreviousClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.RefreshAsync(-100); }
    private async void NextClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.RefreshAsync(100); }
    private void SaveClick(object sender, RoutedEventArgs e) => Vm?.Save();
    private void InsertClick(object sender, RoutedEventArgs e) => Vm?.Insert(false);
    private void RecipeClick(object sender, RoutedEventArgs e) => Vm?.Insert(true);
    private void CopyNegativeClick(object sender, RoutedEventArgs e) => Vm?.CopyNegative();
    private void AppendNegativeClick(object sender, RoutedEventArgs e) => Vm?.AppendNegative();
    private void CopyTriggersClick(object sender, RoutedEventArgs e) => Vm?.CopyTriggers();
    private void AddTriggerClick(object sender, RoutedEventArgs e) => Vm?.AddTrigger();
    private void PresetClick(object sender, RoutedEventArgs e) => Vm?.CreatePreset();
}
