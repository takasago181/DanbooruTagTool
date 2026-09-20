using System.Windows;
using DanbooruTagTool.App.ViewModels;

namespace DanbooruTagTool.App;

public partial class GenerationImportDialog : Window
{
    public GenerationImportDialog(MainViewModel vm)
    {
        InitializeComponent();
        DataContext = vm.GenerationImport;
    }

    private void CloseClick(object sender, RoutedEventArgs e) => Close();
}
