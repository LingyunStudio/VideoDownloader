using System.Collections.ObjectModel;
using System.Diagnostics;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VideoDownloader.Helpers;
using VideoDownloader.Models;
using VideoDownloader.Services;

namespace VideoDownloader.ViewModels;

public sealed partial class HomeViewModel : ObservableObject
{
    private readonly YtDlpService _ytDlp;
    private readonly DownloadQueueService _queue;
    private readonly SettingsService _settings;
    private readonly ToolManagerService _tools;
    private readonly CookieManagerService _cookies;
    private CancellationTokenSource? _parseCts;

    public HomeViewModel(
        YtDlpService ytDlp,
        DownloadQueueService queue,
        SettingsService settings,
        ToolManagerService tools,
        CookieManagerService cookies)
    {
        _ytDlp = ytDlp;
        _queue = queue;
        _settings = settings;
        _tools = tools;
        _cookies = cookies;

        var s = _settings.Current;
        OutputDirectory = s.OutputDirectory;
        SelectedContainer = s.DefaultContainer;
        DownloadSubtitles = s.AutoDownloadSubtitles;
        SubtitleLangs = s.DefaultSubtitleLangs;
        EmbedThumbnail = s.AutoEmbedThumbnail;
        EmbedMetadata = s.AutoEmbedMetadata;
        EmbedChapters = s.AutoEmbedChapters;
        ConcurrentFragments = s.ConcurrentFragments;
        UseAria2Acceleration = s.UseAria2Acceleration;
        Aria2Connections = s.Aria2Connections;
        RateLimit = s.RateLimit;
        Impersonate = s.Impersonate;
        ForceIpv4 = s.ForceIpv4;
        UseArchive = s.UseDownloadArchive;
        NoMtime = s.NoMtime;
        SponsorBlockMode = s.SponsorBlockMode;
        ExtraArguments = s.DefaultExtraArguments;

        LoadCookieSources(s.CookiesSource);
    }

    public event Action? NavigateToDownloadsRequested;

    public ObservableCollection<CookieSourceChoice> CookieSources { get; } = [];

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(ParseCommand))]
    [NotifyCanExecuteChangedFor(nameof(PrimaryDownloadCommand))]
    [NotifyPropertyChangedFor(nameof(HasUrlInput))]
    [NotifyPropertyChangedFor(nameof(ShowMixedListHint))]
    [NotifyPropertyChangedFor(nameof(PrimaryDownloadButtonText))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _urlInput = string.Empty;

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(ParseCommand))]
    [NotifyCanExecuteChangedFor(nameof(PrimaryDownloadCommand))]
    private bool _isParsing;

    [ObservableProperty]
    private string _statusMessage = string.Empty;

    [ObservableProperty]
    private bool _isErrorBannerOpen;

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    [ObservableProperty]
    private bool _isAuthRelatedError;

    [ObservableProperty]
    private bool _isInfoBannerOpen;

    [ObservableProperty]
    private string _infoMessage = string.Empty;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(HasVideoInfo))]
    [NotifyPropertyChangedFor(nameof(IsSingleVideo))]
    [NotifyPropertyChangedFor(nameof(IsPlaylistInfo))]
    [NotifyPropertyChangedFor(nameof(PlaylistNoticeText))]
    [NotifyPropertyChangedFor(nameof(PrimaryDownloadButtonText))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    [NotifyCanExecuteChangedFor(nameof(PrimaryDownloadCommand))]
    private VideoInfo? _currentVideo;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(PlaylistModeShortLabel))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private int _playlistModeIndex;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsCustomMode))]
    [NotifyPropertyChangedFor(nameof(IsAudioPreset))]
    [NotifyPropertyChangedFor(nameof(IsPreset0))]
    [NotifyPropertyChangedFor(nameof(IsPreset1))]
    [NotifyPropertyChangedFor(nameof(IsPreset2))]
    [NotifyPropertyChangedFor(nameof(IsPreset3))]
    [NotifyPropertyChangedFor(nameof(IsPreset4))]
    [NotifyPropertyChangedFor(nameof(SelectionSummaryText))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private int _selectedPresetIndex;

    [ObservableProperty]
    private int _selectedFormatTabIndex;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(ShortOutputDirectory))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _outputDirectory = string.Empty;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _selectedContainer = "auto";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _remuxVideo;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(SelectionSummaryText))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _selectedAudioFormat = "mp3";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CookieStatusHint))]
    [NotifyPropertyChangedFor(nameof(CookieChipLabel))]
    [NotifyPropertyChangedFor(nameof(IsCookieAuthenticated))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private CookieSourceChoice? _selectedCookieSource;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(SelectionSummaryText))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _playlistItems = string.Empty;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _playlistReverse;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _useArchive;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _noMtime;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _downloadSubtitles;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _downloadAutoSubtitles;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _subtitleLangs = "zh-Hans,zh-CN,zh,en.*";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _embedSubtitles = true;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _convertSubtitles = "none";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _embedThumbnail;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _writeThumbnail;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _embedMetadata = true;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _embedChapters = true;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _splitChapters;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _sponsorBlockMode = "off";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _sponsorBlockCategories = "default";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _sectionRange = string.Empty;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _forceKeyframesAtCuts;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _liveFromStart;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private double _concurrentFragments = 8;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _useAria2Acceleration = true;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private double _aria2Connections = 16;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _rateLimit = string.Empty;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _impersonate = "none";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private bool _forceIpv4;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _videoPassword = string.Empty;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private string _extraArguments = string.Empty;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(SelectionSummaryText))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private FormatOption? _selectedVideoFormat;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(SelectionSummaryText))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private FormatOption? _selectedAudioFormatOption;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(SelectionSummaryText))]
    [NotifyPropertyChangedFor(nameof(CommandPreview))]
    private FormatOption? _selectedCombinedFormat;

    public ObservableCollection<FormatOption> VideoFormats { get; } = [];
    public ObservableCollection<FormatOption> AudioFormats { get; } = [];
    public ObservableCollection<FormatOption> CombinedFormats { get; } = [];
    public ObservableCollection<PlaylistEntryItem> PlaylistEntries { get; } = [];

    public bool HasUrlInput => !string.IsNullOrWhiteSpace(UrlInput);
    public bool HasVideoInfo => CurrentVideo is not null;
    public bool IsSingleVideo => CurrentVideo is { IsPlaylist: false };
    public bool IsPlaylistInfo => CurrentVideo is { IsPlaylist: true };
    public bool IsCustomMode => SelectedPresetIndex == 4;
    public bool IsAudioPreset => SelectedPresetIndex == 3;
    public bool IsPreset0 => SelectedPresetIndex == 0;
    public bool IsPreset1 => SelectedPresetIndex == 1;
    public bool IsPreset2 => SelectedPresetIndex == 2;
    public bool IsPreset3 => SelectedPresetIndex == 3;
    public bool IsPreset4 => SelectedPresetIndex == 4;
    public bool ShowMixedListHint => YtDlpService.UrlContainsVideoAndList(UrlInput);

    public string PlaylistModeShortLabel => PlaylistModeIndex switch
    {
        1 => "仅当前视频",
        2 => "整个播放列表",
        _ => "列表：自动智能"
    };

    public string ShortOutputDirectory
    {
        get
        {
            if (string.IsNullOrWhiteSpace(OutputDirectory))
                return "选择保存目录";
            return OutputDirectory.Length <= 28
                ? OutputDirectory
                : "…\\" + Path.GetFileName(OutputDirectory.TrimEnd('\\', '/'));
        }
    }

    public bool IsCookieAuthenticated
    {
        get
        {
            var key = SelectedCookieSource?.Key ?? CookieManagerService.NoneSourceKey;
            if (key.Equals(CookieManagerService.NoneSourceKey, StringComparison.OrdinalIgnoreCase))
                return false;
            if (key.Equals(CookieManagerService.BuiltinSourceKey, StringComparison.OrdinalIgnoreCase))
                return _cookies.InspectBuiltinCookies().TotalCookies > 0;
            if (File.Exists(key))
                return _cookies.InspectCookieFile(key).TotalCookies > 0;
            return true;
        }
    }

    public string CookieChipLabel
    {
        get
        {
            var key = SelectedCookieSource?.Key ?? CookieManagerService.NoneSourceKey;
            if (key.Equals(CookieManagerService.BuiltinSourceKey, StringComparison.OrdinalIgnoreCase))
            {
                var info = _cookies.InspectBuiltinCookies();
                if (!info.Exists || info.TotalCookies == 0)
                    return "Cookies：未登录";
                if (info.HasYouTubeAuth && info.HasBilibiliAuth)
                    return "已登录 · YT / B站";
                if (info.HasYouTubeAuth)
                    return "已登录 · YouTube";
                if (info.HasBilibiliAuth)
                    return "已登录 · Bilibili";
                return $"内置登录 · {info.TotalCookies} 条";
            }
            if (key.Equals(CookieManagerService.NoneSourceKey, StringComparison.OrdinalIgnoreCase))
                return "Cookies：不使用";
            if (File.Exists(key))
                return $"Cookies：{Path.GetFileName(key)}";
            return $"Cookies：{key}";
        }
    }

    [RelayCommand]
    private void SelectPreset(string? indexText)
    {
        if (int.TryParse(indexText, out int idx) && idx is >= 0 and <= 4)
            SelectedPresetIndex = idx;
    }

    [RelayCommand]
    private void SetPlaylistMode(string? indexText)
    {
        if (int.TryParse(indexText, out int idx) && idx is >= 0 and <= 2)
            PlaylistModeIndex = idx;
    }

    public PlaylistParseMode CurrentPlaylistMode => PlaylistModeIndex switch
    {
        1 => PlaylistParseMode.SingleVideoOnly,
        2 => PlaylistParseMode.FullPlaylist,
        _ => PlaylistParseMode.Auto
    };

    public string PrimaryDownloadButtonText
    {
        get
        {
            if (CurrentVideo is not null)
                return CurrentVideo.IsPlaylist ? "下载播放列表" : "开始下载";

            var urls = ExtractUrls(UrlInput);
            if (urls.Count > 1)
                return $"批量直接下载 ({urls.Count})";

            return "按预设直接下载";
        }
    }

    public string CookieStatusHint
    {
        get
        {
            var key = SelectedCookieSource?.Key ?? CookieManagerService.NoneSourceKey;
            if (key.Equals(CookieManagerService.BuiltinSourceKey, StringComparison.OrdinalIgnoreCase))
                return _cookies.InspectBuiltinCookies().StatusSummary;

            if (key.Equals(CookieManagerService.NoneSourceKey, StringComparison.OrdinalIgnoreCase))
                return "未启用登录态（遇到 YouTube 人机验证或会员视频时可点击「网页登录」）";

            if (key.StartsWith("edge", StringComparison.OrdinalIgnoreCase) ||
                key.StartsWith("chrome", StringComparison.OrdinalIgnoreCase))
                return "提示：Windows 新版 Chrome/Edge 已启用系统加密锁库，若失败请点击「网页登录」";

            if (key.StartsWith("firefox", StringComparison.OrdinalIgnoreCase))
                return "将读取本机 Firefox Cookies（请确认已在 Firefox 内登录目标网站）";

            if (File.Exists(key))
            {
                var info = _cookies.InspectCookieFile(key);
                return $"外部文件：{Path.GetFileName(key)} · {info.StatusSummary}";
            }

            return SelectedCookieSource?.Description ?? string.Empty;
        }
    }

    public string PlaylistNoticeText => CurrentVideo is { IsPlaylist: true }
        ? $"播放列表共 {CurrentVideo.PlaylistCount} 个条目。可通过「播放列表范围」指定子集（如 1-5,8），留空默认下载全部。"
        : string.Empty;

    public string SelectionSummaryText
    {
        get
        {
            if (CurrentVideo is { IsPlaylist: true })
            {
                var range = string.IsNullOrWhiteSpace(PlaylistItems) ? "全部条目" : $"范围 {PlaylistItems}";
                return $"播放列表批量下载（{CurrentVideo.PlaylistCount} 项 · {range}）";
            }

            return SelectedPresetIndex switch
            {
                0 => "最佳画质自动合并（推荐）",
                1 => "高兼容 MP4（优先 H.264 + AAC，适合剪辑与移动端）",
                2 => "1080p 高清均衡",
                3 => $"仅提取音频（{SelectedAudioFormat.ToUpperInvariant()} 最高音质）",
                4 => BuildCustomSummary(),
                _ => "最佳画质"
            };
        }
    }

    public string CommandPreview
    {
        get
        {
            var url = ExtractUrls(UrlInput).FirstOrDefault() ?? "<URL>";
            var req = BuildRequest(url, CurrentVideo?.Title ?? "", CurrentVideo?.Thumbnail ?? "", CurrentVideo?.Extractor ?? "", forDirectUrl: CurrentVideo is null);
            return _ytDlp.BuildCommandPreview(req);
        }
    }

    public string GetSuggestedLoginUrl()
    {
        var url = ExtractUrls(UrlInput).FirstOrDefault();
        if (!string.IsNullOrEmpty(url))
        {
            if (url.Contains("bilibili.com", StringComparison.OrdinalIgnoreCase))
                return "https://www.bilibili.com/";
            if (url.Contains("x.com", StringComparison.OrdinalIgnoreCase) || url.Contains("twitter.com", StringComparison.OrdinalIgnoreCase))
                return "https://x.com/login";
            if (url.Contains("douyin.com", StringComparison.OrdinalIgnoreCase))
                return "https://www.douyin.com/";
            if (url.Contains("tiktok.com", StringComparison.OrdinalIgnoreCase))
                return "https://www.tiktok.com/";
            if (url.Contains("youtube.com", StringComparison.OrdinalIgnoreCase) || url.Contains("youtu.be", StringComparison.OrdinalIgnoreCase))
                return "https://www.youtube.com/";
            if (Uri.TryCreate(url, UriKind.Absolute, out var uri))
                return $"{uri.Scheme}://{uri.Host}/";
        }
        return "https://www.youtube.com/";
    }

    private void LoadCookieSources(string savedKey)
    {
        CookieSources.Clear();
        foreach (var item in _cookies.DiscoverAvailableSources())
            CookieSources.Add(item);

        if (!string.IsNullOrWhiteSpace(savedKey) && File.Exists(savedKey))
        {
            var fileChoice = new CookieSourceChoice(savedKey, $"本地文件：{Path.GetFileName(savedKey)}", savedKey);
            CookieSources.Add(fileChoice);
            SelectedCookieSource = fileChoice;
            return;
        }

        var match = CookieSources.FirstOrDefault(c => c.Key.Equals(savedKey, StringComparison.OrdinalIgnoreCase));
        SelectedCookieSource = match ?? CookieSources.First(c => c.Key == CookieManagerService.BuiltinSourceKey);
    }

    public void OnBuiltinCookiesExtracted(CookieFileInspection inspection)
    {
        var builtinChoice = CookieSources.FirstOrDefault(c => c.Key == CookieManagerService.BuiltinSourceKey);
        if (builtinChoice is not null)
            SelectedCookieSource = builtinChoice;

        OnPropertyChanged(nameof(CookieStatusHint));
        OnPropertyChanged(nameof(CookieChipLabel));
        OnPropertyChanged(nameof(IsCookieAuthenticated));
        OnPropertyChanged(nameof(CommandPreview));
        IsErrorBannerOpen = false;
        IsAuthRelatedError = false;
        ShowInfo($"内置 Cookies 提取成功：{inspection.StatusSummary}");

        if (ParseCommand.CanExecute(null))
            _ = ParseAsync();
    }

    public void ImportExternalCookieFile(string filePath)
    {
        if (string.IsNullOrWhiteSpace(filePath) || !File.Exists(filePath))
            return;

        var existing = CookieSources.FirstOrDefault(c => c.Key.Equals(filePath, StringComparison.OrdinalIgnoreCase));
        if (existing is null)
        {
            existing = new CookieSourceChoice(filePath, $"本地文件：{Path.GetFileName(filePath)}", filePath);
            CookieSources.Add(existing);
        }

        SelectedCookieSource = existing;
        var info = _cookies.InspectCookieFile(filePath);
        if (info.TotalCookies == 0)
            ShowError("所选文件未检测到有效的 Netscape Cookies 行，请确认导出格式正确。", authError: true);
        else
            ShowInfo($"已加载 Cookies 文件（{info.TotalCookies} 条记录）。");
    }

    private string ResolveActiveCookiesForYtDlp() =>
        _cookies.ResolveForYtDlp(SelectedCookieSource?.Key);

    private string BuildCustomSummary()
    {
        if (SelectedCombinedFormat is not null)
        {
            var f = SelectedCombinedFormat;
            return $"合一流：{f.ResolutionText} {f.ExtUpper} ({f.SizeText})";
        }

        if (SelectedVideoFormat is not null && SelectedAudioFormatOption is not null)
        {
            long est = SelectedVideoFormat.EffectiveSize + SelectedAudioFormatOption.EffectiveSize;
            var sizeStr = est > 0 ? $" · 约 {FormatHelpers.HumanSize(est)}" : string.Empty;
            return $"合并：{SelectedVideoFormat.ResolutionText} ({SelectedVideoFormat.CodecDisplay}) + {SelectedAudioFormatOption.CodecDisplay}{sizeStr}";
        }

        if (SelectedVideoFormat is not null)
            return $"仅视频：{SelectedVideoFormat.ResolutionText} {SelectedVideoFormat.ExtUpper} ({SelectedVideoFormat.SizeText})";

        if (SelectedAudioFormatOption is not null)
            return $"仅音频：{SelectedAudioFormatOption.CodecDisplay} {SelectedAudioFormatOption.BitrateText} ({SelectedAudioFormatOption.SizeText})";

        return "未勾选具体格式（将使用最佳画质）";
    }

    partial void OnOutputDirectoryChanged(string value)
    {
        if (!string.IsNullOrWhiteSpace(value))
        {
            _settings.Current.OutputDirectory = value;
            _settings.Save();
        }
    }

    partial void OnSelectedCookieSourceChanged(CookieSourceChoice? value)
    {
        if (value is not null)
        {
            _settings.Current.CookiesSource = value.Key;
            _settings.Save();
        }
    }

    partial void OnSelectedContainerChanged(string value)
    {
        _settings.Current.DefaultContainer = value;
        _settings.Save();
    }

    public void SelectFormat(FormatOption option)
    {
        if (option.Group == FormatGroup.Combined)
        {
            ClearSelection(VideoFormats);
            ClearSelection(AudioFormats);
            SelectedVideoFormat = null;
            SelectedAudioFormatOption = null;

            bool toggleOff = SelectedCombinedFormat == option;
            ClearSelection(CombinedFormats);
            if (!toggleOff)
            {
                option.IsSelected = true;
                SelectedCombinedFormat = option;
            }
            else
            {
                SelectedCombinedFormat = null;
            }
        }
        else if (option.Group == FormatGroup.VideoOnly)
        {
            ClearSelection(CombinedFormats);
            SelectedCombinedFormat = null;

            bool toggleOff = SelectedVideoFormat == option;
            ClearSelection(VideoFormats);
            if (!toggleOff)
            {
                option.IsSelected = true;
                SelectedVideoFormat = option;
            }
            else
            {
                SelectedVideoFormat = null;
            }
        }
        else
        {
            ClearSelection(CombinedFormats);
            SelectedCombinedFormat = null;

            bool toggleOff = SelectedAudioFormatOption == option;
            ClearSelection(AudioFormats);
            if (!toggleOff)
            {
                option.IsSelected = true;
                SelectedAudioFormatOption = option;
            }
            else
            {
                SelectedAudioFormatOption = null;
            }
        }

        SelectedPresetIndex = 4;
        OnPropertyChanged(nameof(SelectionSummaryText));
        OnPropertyChanged(nameof(CommandPreview));
    }

    private static void ClearSelection(ObservableCollection<FormatOption> list)
    {
        foreach (var item in list)
            item.IsSelected = false;
    }

    [RelayCommand]
    private async Task ParseSingleVideoAsync()
    {
        PlaylistModeIndex = 1;
        if (ParseCommand.CanExecute(null))
            await ParseAsync();
    }

    [RelayCommand]
    private async Task ParseFullPlaylistAsync()
    {
        PlaylistModeIndex = 2;
        if (ParseCommand.CanExecute(null))
            await ParseAsync();
    }

    private bool CanParse() => !IsParsing && !string.IsNullOrWhiteSpace(UrlInput);

    [RelayCommand(CanExecute = nameof(CanParse))]
    public async Task ParseAsync()
    {
        IsErrorBannerOpen = false;
        IsInfoBannerOpen = false;
        IsAuthRelatedError = false;

        var urls = ExtractUrls(UrlInput);
        if (urls.Count == 0)
        {
            ShowError("请输入有效的 http:// 或 https:// 视频或播放列表链接。");
            return;
        }

        if (!_tools.IsYtDlpReady)
        {
            ShowError("yt-dlp 引擎尚未就绪，请等待顶部自动下载完成或前往「设置」页安装。");
            return;
        }

        _parseCts?.Cancel();
        _parseCts?.Dispose();
        _parseCts = new CancellationTokenSource();

        IsParsing = true;
        StatusMessage = "正在解析视频信息、可用字幕与高清流…";

        try
        {
            var info = await _ytDlp.ExtractInfoAsync(
                urls[0],
                CurrentPlaylistMode,
                ResolveActiveCookiesForYtDlp(),
                _settings.Current.ProxyUrl,
                Impersonate,
                ForceIpv4,
                _settings.Current.EnableJsRuntimes,
                VideoPassword,
                ExtraArguments,
                _parseCts.Token);

            CurrentVideo = info;
            PopulateVideoInfo(info);
            StatusMessage = info.IsPlaylist
                ? $"解析完成：播放列表共 {info.PlaylistCount} 项"
                : $"解析完成：找到 {info.Formats.Count} 个可用格式";
        }
        catch (OperationCanceledException)
        {
            StatusMessage = "已取消解析";
        }
        catch (Exception ex)
        {
            AppLogger.Error("Parse failed", ex);
            bool authRelated = ex.Message.Contains("Cookies", StringComparison.OrdinalIgnoreCase) ||
                               ex.Message.Contains("人机验证", StringComparison.OrdinalIgnoreCase) ||
                               ex.Message.Contains("登录", StringComparison.OrdinalIgnoreCase) ||
                               ex.Message.Contains("私有", StringComparison.OrdinalIgnoreCase) ||
                               ex.Message.Contains("Sign in", StringComparison.OrdinalIgnoreCase);
            ShowError(ex.Message, authRelated);
            StatusMessage = string.Empty;
        }
        finally
        {
            IsParsing = false;
        }
    }

    [RelayCommand]
    private void CancelParse() => _parseCts?.Cancel();

    private bool CanPrimaryDownload() => !IsParsing && (CurrentVideo is not null || ExtractUrls(UrlInput).Count > 0);

    [RelayCommand(CanExecute = nameof(CanPrimaryDownload))]
    private void PrimaryDownload()
    {
        IsErrorBannerOpen = false;
        if (!_tools.IsYtDlpReady)
        {
            ShowError("yt-dlp 引擎尚未就绪，请稍候。");
            return;
        }

        if (CurrentVideo is not null)
        {
            var url = string.IsNullOrWhiteSpace(CurrentVideo.WebpageUrl)
                ? ExtractUrls(UrlInput).FirstOrDefault() ?? UrlInput.Trim()
                : CurrentVideo.WebpageUrl;

            var req = BuildRequest(url, CurrentVideo.Title, CurrentVideo.Thumbnail, CurrentVideo.Extractor, forDirectUrl: false);
            _queue.Enqueue(req);
            ShowInfo($"已开始下载：{CurrentVideo.Title}");
            NavigateToDownloadsRequested?.Invoke();
            return;
        }

        var urls = ExtractUrls(UrlInput);
        if (urls.Count == 0)
        {
            ShowError("请输入有效的链接。");
            return;
        }

        foreach (var url in urls)
            _queue.Enqueue(BuildRequest(url, url, string.Empty, string.Empty, forDirectUrl: true));

        ShowInfo(urls.Count == 1 ? "已按当前预设加入下载队列。" : $"已将 {urls.Count} 个链接加入下载队列。");
        NavigateToDownloadsRequested?.Invoke();
    }

    [RelayCommand]
    private void OpenOutputDirectory()
    {
        try
        {
            Directory.CreateDirectory(OutputDirectory);
            Process.Start(new ProcessStartInfo("explorer.exe", OutputDirectory) { UseShellExecute = true });
        }
        catch (Exception ex)
        {
            ShowError($"无法打开目录：{ex.Message}");
        }
    }

    [RelayCommand]
    private void ClearUrl()
    {
        UrlInput = string.Empty;
        CurrentVideo = null;
        VideoFormats.Clear();
        AudioFormats.Clear();
        CombinedFormats.Clear();
        PlaylistEntries.Clear();
        SelectedVideoFormat = null;
        SelectedAudioFormatOption = null;
        SelectedCombinedFormat = null;
        StatusMessage = string.Empty;
        IsErrorBannerOpen = false;
        IsInfoBannerOpen = false;
        IsAuthRelatedError = false;
    }

    private DownloadRequest BuildRequest(string url, string title, string thumbnail, string extractor, bool forDirectUrl)
    {
        var (fmtSpec, fmtSort, audioOnly, containerOverride, summary) = BuildFormatSpecForCurrentSelection(forDirectUrl);

        var effectivePlaylistMode = CurrentVideo is { IsPlaylist: true } && CurrentPlaylistMode == PlaylistParseMode.Auto
            ? PlaylistParseMode.FullPlaylist
            : CurrentPlaylistMode;

        return new DownloadRequest
        {
            Url = url,
            Title = title,
            ThumbnailUrl = thumbnail,
            Extractor = extractor,
            OutputDirectory = OutputDirectory,
            OutputTemplate = _settings.Current.OutputTemplate,
            UseArchive = UseArchive,
            NoMtime = NoMtime,
            FormatSpec = fmtSpec,
            FormatSort = fmtSort,
            FormatSummary = summary,
            Container = string.IsNullOrEmpty(containerOverride) ? SelectedContainer : containerOverride,
            RemuxVideo = RemuxVideo,
            AudioOnly = audioOnly,
            AudioFormat = SelectedAudioFormat,
            PlaylistMode = effectivePlaylistMode,
            PlaylistItems = PlaylistItems,
            PlaylistReverse = PlaylistReverse,
            DownloadSubtitles = DownloadSubtitles,
            DownloadAutoSubtitles = DownloadAutoSubtitles,
            SubtitleLangs = SubtitleLangs,
            EmbedSubtitles = EmbedSubtitles,
            ConvertSubtitles = ConvertSubtitles,
            EmbedThumbnail = EmbedThumbnail,
            WriteThumbnail = WriteThumbnail,
            EmbedMetadata = EmbedMetadata,
            EmbedChapters = EmbedChapters,
            SplitChapters = SplitChapters,
            SponsorBlockMode = SponsorBlockMode,
            SponsorBlockCategories = SponsorBlockCategories,
            SectionRange = SectionRange,
            ForceKeyframesAtCuts = ForceKeyframesAtCuts,
            LiveFromStart = LiveFromStart,
            ConcurrentFragments = double.IsNaN(ConcurrentFragments) ? 8 : Math.Clamp((int)Math.Round(ConcurrentFragments), 1, 16),
            UseAria2Acceleration = UseAria2Acceleration,
            Aria2Connections = double.IsNaN(Aria2Connections) ? 16 : Math.Clamp((int)Math.Round(Aria2Connections), 1, 16),
            RateLimit = RateLimit,
            CookiesSource = ResolveActiveCookiesForYtDlp(),
            ProxyUrl = _settings.Current.ProxyUrl,
            Impersonate = Impersonate,
            ForceIpv4 = ForceIpv4,
            EnableJsRuntimes = _settings.Current.EnableJsRuntimes,
            VideoPassword = VideoPassword,
            ExtraArguments = ExtraArguments
        };
    }

    private (string FormatSpec, string FormatSort, bool AudioOnly, string ContainerOverride, string Summary) BuildFormatSpecForCurrentSelection(bool forDirectUrl)
    {
        if (SelectedPresetIndex == 0)
            return ("bv*+ba/b", string.Empty, false, string.Empty, "最佳画质");

        if (SelectedPresetIndex == 1)
            return ("bv*+ba/b", "ext:mp4:m4a,vcodec:h264,acodec:aac", false, "mp4", "兼容 MP4 (H.264)");

        if (SelectedPresetIndex == 2)
            return ("bv*[height<=1080]+ba/b[height<=1080]/b", string.Empty, false, string.Empty, "1080p 均衡");

        if (SelectedPresetIndex == 3)
            return ("ba/b", string.Empty, true, string.Empty, $"音频 {SelectedAudioFormat.ToUpperInvariant()}");

        if (forDirectUrl)
            return ("bv*+ba/b", string.Empty, false, string.Empty, "最佳画质");

        if (SelectedCombinedFormat is not null)
            return (SelectedCombinedFormat.FormatId, string.Empty, false, string.Empty, $"{SelectedCombinedFormat.ResolutionText} {SelectedCombinedFormat.ExtUpper}");

        if (SelectedVideoFormat is not null && SelectedAudioFormatOption is not null)
            return ($"{SelectedVideoFormat.FormatId}+{SelectedAudioFormatOption.FormatId}", string.Empty, false, string.Empty,
                $"{SelectedVideoFormat.ResolutionText} + {SelectedAudioFormatOption.CodecDisplay}");

        if (SelectedVideoFormat is not null)
            return (SelectedVideoFormat.FormatId, string.Empty, false, string.Empty, $"仅视频 {SelectedVideoFormat.ResolutionText}");

        if (SelectedAudioFormatOption is not null)
            return (SelectedAudioFormatOption.FormatId, string.Empty, false, string.Empty, $"仅音频 {SelectedAudioFormatOption.CodecDisplay}");

        return ("bv*+ba/b", string.Empty, false, string.Empty, "最佳画质");
    }

    private void PopulateVideoInfo(VideoInfo info)
    {
        VideoFormats.Clear();
        AudioFormats.Clear();
        CombinedFormats.Clear();
        PlaylistEntries.Clear();
        SelectedVideoFormat = null;
        SelectedAudioFormatOption = null;
        SelectedCombinedFormat = null;

        if (info.IsPlaylist)
        {
            foreach (var entry in info.PlaylistEntries)
                PlaylistEntries.Add(entry);
            OnPropertyChanged(nameof(SelectionSummaryText));
            OnPropertyChanged(nameof(CommandPreview));
            return;
        }

        foreach (var v in info.Formats
                     .Where(f => f.Group == FormatGroup.VideoOnly)
                     .OrderByDescending(f => f.Height ?? 0)
                     .ThenByDescending(f => f.Fps ?? 0)
                     .ThenByDescending(f => f.Tbr ?? 0))
            VideoFormats.Add(v);

        foreach (var a in info.Formats
                     .Where(f => f.Group == FormatGroup.AudioOnly)
                     .OrderByDescending(f => f.Tbr ?? 0))
            AudioFormats.Add(a);

        foreach (var c in info.Formats
                     .Where(f => f.Group == FormatGroup.Combined)
                     .OrderByDescending(f => f.Height ?? 0)
                     .ThenByDescending(f => f.Tbr ?? 0))
            CombinedFormats.Add(c);

        var recVideo = VideoFormats.FirstOrDefault(v => v.IsRecommended) ?? VideoFormats.FirstOrDefault();
        var recAudio = AudioFormats.FirstOrDefault(a => a.IsRecommended) ?? AudioFormats.FirstOrDefault();
        if (recVideo is not null)
        {
            recVideo.IsSelected = true;
            SelectedVideoFormat = recVideo;
        }
        if (recAudio is not null)
        {
            recAudio.IsSelected = true;
            SelectedAudioFormatOption = recAudio;
        }
        else if (recVideo is null && CombinedFormats.Count > 0)
        {
            var recComb = CombinedFormats.FirstOrDefault(c => c.IsRecommended) ?? CombinedFormats[0];
            recComb.IsSelected = true;
            SelectedCombinedFormat = recComb;
            SelectedFormatTabIndex = 2;
        }

        OnPropertyChanged(nameof(SelectionSummaryText));
        OnPropertyChanged(nameof(CommandPreview));
    }

    private static List<string> ExtractUrls(string raw)
    {
        return raw.Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Where(l => l.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
                        l.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();
    }

    private void ShowError(string message, bool authError = false)
    {
        ErrorMessage = message;
        IsAuthRelatedError = authError;
        IsErrorBannerOpen = true;
    }

    private void ShowInfo(string message)
    {
        InfoMessage = message;
        IsInfoBannerOpen = true;
    }
}
