using System.Windows;
using Forms = System.Windows.Forms;
using DanbooruTagTool.App.ViewModels;

namespace DanbooruTagTool.App;

public partial class ForgeSettingsDialog : Window
{
    public ForgeSettingsDialog(MainViewModel vm)
    {
        InitializeComponent();
        DataContext = vm;
    }

    private void ChooseFolderClick(object sender, RoutedEventArgs e)
    {
        if (DataContext is not MainViewModel vm) return;
        using var dialog = new Forms.FolderBrowserDialog { Description = "Forge本体またはextensionsフォルダを選択してください", UseDescriptionForTitle = true, SelectedPath = vm.ForgeExtensionPath };
        if (dialog.ShowDialog() == Forms.DialogResult.OK) vm.ForgeExtensionPath = dialog.SelectedPath;
    }

    private void InstallClick(object sender, RoutedEventArgs e)
    {
        if (DataContext is not MainViewModel vm) return;
        if (ForgeBridgeInstaller.TryInstall(vm.ForgeExtensionPath, out var message)) vm.SaveForgeSettings.Execute(null);
        vm.Status = message;
    }

    private void CloseClick(object sender, RoutedEventArgs e) => Close();
}
