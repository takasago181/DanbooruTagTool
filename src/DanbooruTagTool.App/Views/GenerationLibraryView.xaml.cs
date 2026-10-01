using System;
using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using DanbooruTagTool.App.ViewModels;
using Microsoft.Win32;

namespace DanbooruTagTool.App.Views;
public partial class GenerationLibraryView : UserControl
{
    public GenerationLibraryView() => InitializeComponent();
    private GenerationLibraryViewModel? Vm => DataContext as GenerationLibraryViewModel;
    private async void OnLoaded(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.InitializeAsync(); }
    private async void AddRootClick(object sender, RoutedEventArgs e)
    {
        if (Vm is not { Busy: false } vm) return;
        var dialog = new OpenFolderDialog { Title = "生成画像フォルダーを選択（再帰スキャン）" };
        if (dialog.ShowDialog() == true) await vm.AddRootAsync(dialog.FolderName);
    }
    private async void DisableRootClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.SetSelectedRootEnabledAsync(false); }
    private async void EnableRootClick(object sender, RoutedEventArgs e) { if (Vm is { } vm) await vm.SetSelectedRootEnabledAsync(true); }
    private void BackupClick(object sender, RoutedEventArgs e)
    {
        if (Vm is not { Busy: false } vm) return;
        var dialog = new SaveFileDialog { Title = "Library DBバックアップ", Filter = "SQLite DB|*.db", FileName = "generation-library-backup.db" };
        if (dialog.ShowDialog() == true) vm.Backup(dialog.FileName);
    }
    private void OpenImageClick(object sender, RoutedEventArgs e)
    { if (Vm is { } vm && File.Exists(vm.SelectedPath)) Launch(new ProcessStartInfo(vm.SelectedPath) { UseShellExecute = true }); }
    private void RevealClick(object sender, RoutedEventArgs e)
    {
        if (Vm is not { } vm || !File.Exists(vm.SelectedPath)) return;
        Launch(new ProcessStartInfo("explorer.exe", "/select,\"" + vm.SelectedPath + "\"") { UseShellExecute = true });
    }
    private static void Launch(ProcessStartInfo start)
    {
        try { Process.Start(start); }
        catch (Exception e) when (e is System.ComponentModel.Win32Exception or InvalidOperationException) { MessageBox.Show(e.Message, "画像を開けません"); }
    }
    public void FocusSearch() => SearchBox.Focus();
}
