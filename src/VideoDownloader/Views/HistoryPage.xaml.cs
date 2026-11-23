using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VideoDownloader.Models;
using VideoDownloader.ViewModels;

namespace VideoDownloader.Views;

public sealed partial class HistoryPage : Page
{
    public HistoryViewModel ViewModel => App.CurrentApp.HistoryViewModel;

    public HistoryPage()
    {
        InitializeComponent();
    }

    private void OpenFile_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement { Tag: HistoryEntry entry })
            ViewModel.OpenFileLocationCommand.Execute(entry);
    }

    private void Redownload_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement { Tag: HistoryEntry entry })
            ViewModel.RedownloadCommand.Execute(entry);
    }

    private void OpenWeb_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement { Tag: HistoryEntry entry })
            ViewModel.OpenWebPageCommand.Execute(entry);
    }

    private void Delete_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement { Tag: HistoryEntry entry })
            ViewModel.DeleteEntryCommand.Execute(entry);
    }
}
