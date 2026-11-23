using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VideoDownloader.Models;
using VideoDownloader.ViewModels;

namespace VideoDownloader.Views;

public sealed partial class DownloadsPage : Page
{
    public DownloadsViewModel ViewModel => App.CurrentApp.DownloadsViewModel;

    public DownloadsPage()
    {
        InitializeComponent();
    }

    private void Cancel_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement { Tag: DownloadTaskItem item })
            ViewModel.CancelTaskCommand.Execute(item);
    }

    private void Retry_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement { Tag: DownloadTaskItem item })
            ViewModel.RetryTaskCommand.Execute(item);
    }

    private void Remove_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement { Tag: DownloadTaskItem item })
            ViewModel.RemoveTaskCommand.Execute(item);
    }

    private void OpenFile_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement { Tag: DownloadTaskItem item })
            ViewModel.OpenFileLocationCommand.Execute(item);
    }

    private async void ViewLog_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not FrameworkElement { Tag: DownloadTaskItem item })
            return;

        var content = new ScrollViewer
        {
            MaxHeight = 420,
            Content = new StackPanel
            {
                Spacing = 10,
                Children =
                {
                    new TextBlock { Text = "执行命令：", FontWeight = Microsoft.UI.Text.FontWeights.SemiBold },
                    new TextBlock
                    {
                        Text = string.IsNullOrEmpty(item.CommandPreview) ? "(无)" : item.CommandPreview,
                        FontFamily = new Microsoft.UI.Xaml.Media.FontFamily("Consolas"),
                        FontSize = 12,
                        TextWrapping = TextWrapping.Wrap,
                        IsTextSelectionEnabled = true
                    },
                    new TextBlock { Text = "最近输出日志：", FontWeight = Microsoft.UI.Text.FontWeights.SemiBold },
                    new TextBlock
                    {
                        Text = string.IsNullOrEmpty(item.LogSummary)
                            ? (string.IsNullOrEmpty(item.ErrorMessage) ? "(尚无输出日志)" : item.ErrorMessage)
                            : item.LogSummary,
                        FontFamily = new Microsoft.UI.Xaml.Media.FontFamily("Consolas"),
                        FontSize = 12,
                        TextWrapping = TextWrapping.Wrap,
                        IsTextSelectionEnabled = true
                    }
                }
            }
        };

        var dialog = new ContentDialog
        {
            Title = item.Title,
            Content = content,
            CloseButtonText = "关闭",
            XamlRoot = XamlRoot
        };
        await dialog.ShowAsync();
    }
}
