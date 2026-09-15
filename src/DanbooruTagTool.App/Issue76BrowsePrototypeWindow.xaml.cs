using System.Windows;
using System.Windows.Controls;
using DanbooruTagTool.App.ViewModels;

namespace DanbooruTagTool.App;

public partial class Issue76BrowsePrototypeWindow : Window
{
    private readonly Issue76BrowsePrototypeViewModel viewModel;

    public Issue76BrowsePrototypeWindow(Issue76BrowsePrototypeViewModel viewModel)
    {
        InitializeComponent();
        this.viewModel = viewModel;
        DataContext = viewModel;
    }

    private void NavigationChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
    {
        if (e.NewValue is NavigationNode node && node.Children.Count == 0)
            viewModel.StartFromTree(node.Key);
    }
}
