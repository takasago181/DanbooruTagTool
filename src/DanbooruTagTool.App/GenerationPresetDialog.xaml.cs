using System.Windows;
using DanbooruTagTool.App.ViewModels;

namespace DanbooruTagTool.App;

public partial class GenerationPresetDialog : Window
{
    public GenerationPresetDialog(MainViewModel vm)
    {
        InitializeComponent();
        DataContext = vm;
    }

    private void DeletePresetClick(object sender, RoutedEventArgs e)
    {
        if (DataContext is not MainViewModel vm || vm.SelectedPreset == null) return;
        var answer = MessageBox.Show(this, $"「{vm.SelectedPreset.Name}」を削除しますか？", "生成プリセットの削除", MessageBoxButton.YesNo, MessageBoxImage.Warning);
        if (answer == MessageBoxResult.Yes) vm.DeletePreset.Execute(vm.SelectedPreset);
    }
}
