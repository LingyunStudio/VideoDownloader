# 项目简介-dev

VideoDownloader是一个基于`yt-dlp`的python库开发的视频下载程序。

<img src="icon/cut.png" alt="image" style="zoom:70%;" />

[yt-dlp](https://github.com/yt-dlp/yt-dlp) 是一款功能丰富的**命令行**音频/视频下载器，支持数千个网站。该项目是基于现已停用的 youtube-dlc 的 youtube-dl 的一个分支。

yt-dlp基本支持所有常见的视频网站，它是一个功能十分强大、参数十分丰富的命令行程序。本项目基于yt-dlp的python库（yt_dlp）进行开发，使用tkinter库构建了用于视频下载的GUI应用程序，免去了在命令行输入冗长的命令的过程，带给您一个轻松的下载体验。



# 开发环境

## Windows（默认）

默认使用Windows环境，我使用 pycharm+Anaconda:

- python>=3.8
- ffmpeg，用于下载后自动合并音频和视频，注意是ffmpeg的二进制可执行文件，而不是python库，记得添加到环境变量，如：`D:\ffmpeg\bin`



（1）克隆本项目

```bash
git clone git@github.com:CQUPTLei/VideoDownloader.git
```

（2）为项目新建conda虚拟环境，示例：

```bash
conda create -n videodownload  python=3.12 
```

（3）使用pip安装yt_dlp库：

```bash
conda activate videodownload
pip install yt-dlp
```



## Linux

Linux下，以Ubuntu24.04为例，使用vim编辑，python venv虚拟环境（你使用conda也可以）：

（1）克隆项目到本地

```bash
git clone git@github.com:CQUPTLei/VideoDownloader.git
```

（2）安装python venv

```bash
apt install python3.12-venv
```

（3）创建虚拟环境

```bash
python3 -m venv downloader
```

（4）激活虚拟环境

```bash
source downloader/bin/activate
```

（5）安装相关库

```bash
pip install yt-dlp
sudo apt install python3-tk
pip install prettytable
# 打包用
pip install pyinstaller
```

（6）给main.py可执行权限

```bash
sudo chmod 775 main.py
```

（7）执行(注意路径)

```bash
python3 main.py
```

> 可能的修改：如果使用了从浏览器获取cookies文件，可能需要修改路径，默认保存位置可能需要修改。

# 构建可执行程序

**Windows：**

安装pyinstaller库：

```bash
pip install pyinstaller
```

打包命令示例，注意各个路径，下面的代码是在main.py所在目录执行的：

```bash
pyinstaller -F --paths=D:\anaconda\envs\videodownload\Lib\site-packages  --python=D:\anaconda\envs\videodownload\pythonw.exe  --noconsole  --icon=icon\1.ico --name=Downloader main.py
```

**Ubuntu:**

一个简单示例：

```
pyinstaller -F --paths=/home/moon/VideoDownloader/downloader/lib/python3.12/site-packages  --python=/home/moon/VideoDownloader/downloader/bin/python312  --noconsole  --icon=icon\1.ico --name=Downloader main.py
```

**MacOS:**



# 改进方向

- [ ] 添加对视频列表的处理和下载；
- [ ] 同时进行多个下载任务；
- [ ] 支持更多的自定义参数；
- [ ] ...





# 下载参数

yt_dlp在pypi上没有专门的参考手册，github和pypi上都写得的yt-dlp命令行程序的可用参数，但你可以阅读yt_dlp的具体实现：`YoutubeDL.py`来获取可用参数和含义。

以下主要是`yt_dlp.YoutubeDL(download_opts)`方法支持的参数。

## 原文

```python
    YoutubeDL objects accept a lot of parameters. In order not to saturate
    the object constructor with arguments, it receives a dictionary of
    options instead. These options are available through the params
    attribute for the InfoExtractors to use. The YoutubeDL also
    registers itself as the downloader in charge for the InfoExtractors
    that are added to it, so this is a "mutual registration".
    
    Available options:

    username:          Username for authentication purposes.
    password:          Password for authentication purposes.
    videopassword:     Password for accessing a video.
    ap_mso:            Adobe Pass multiple-system operator identifier.
    ap_username:       Multiple-system operator account username.
    ap_password:       Multiple-system operator account password.
    usenetrc:          Use netrc for authentication instead.
    netrc_location:    Location of the netrc file. Defaults to ~/.netrc.
    netrc_cmd:         Use a shell command to get credentials
    verbose:           Print additional info to stdout.
    quiet:             Do not print messages to stdout.
    no_warnings:       Do not print out anything for warnings.
    forceprint:        A dict with keys WHEN mapped to a list of templates to
                       print to stdout. The allowed keys are video or any of the
                       items in utils.POSTPROCESS_WHEN.
                       For compatibility, a single list is also accepted
    print_to_file:     A dict with keys WHEN (same as forceprint) mapped to
                       a list of tuples with (template, filename)
    forcejson:         Force printing info_dict as JSON.
    dump_single_json:  Force printing the info_dict of the whole playlist
                       (or video) as a single JSON line.
    force_write_download_archive: Force writing download archive regardless
                       of 'skip_download' or 'simulate'.
    simulate:          Do not download the video files. If unset (or None),
                       simulate only if listsubtitles, listformats or list_thumbnails is used
    format:            Video format code. see "FORMAT SELECTION" for more details.
                       You can also pass a function. The function takes 'ctx' as
                       argument and returns the formats to download.
                       See "build_format_selector" for an implementation
    allow_unplayable_formats:   Allow unplayable formats to be extracted and downloaded.
    ignore_no_formats_error: Ignore "No video formats" error. Usefull for
                       extracting metadata even if the video is not actually
                       available for download (experimental)
    format_sort:       A list of fields by which to sort the video formats.
                       See "Sorting Formats" for more details.
    format_sort_force: Force the given format_sort. see "Sorting Formats"
                       for more details.
    prefer_free_formats: Whether to prefer video formats with free containers
                       over non-free ones of same quality.
    allow_multiple_video_streams:   Allow multiple video streams to be merged
                       into a single file
    allow_multiple_audio_streams:   Allow multiple audio streams to be merged
                       into a single file
    check_formats      Whether to test if the formats are downloadable.
                       Can be True (check all), False (check none),
                       'selected' (check selected formats),
                       or None (check only if requested by extractor)
    paths:             Dictionary of output paths. The allowed keys are 'home'
                       'temp' and the keys of OUTTMPL_TYPES (in utils/_utils.py)
    outtmpl:           Dictionary of templates for output names. Allowed keys
                       are 'default' and the keys of OUTTMPL_TYPES (in utils/_utils.py).
                       For compatibility with youtube-dl, a single string can also be used
    outtmpl_na_placeholder: Placeholder for unavailable meta fields.
    restrictfilenames: Do not allow "&" and spaces in file names
    trim_file_name:    Limit length of filename (extension excluded)
    windowsfilenames:  Force the filenames to be windows compatible
    ignoreerrors:      Do not stop on download/postprocessing errors.
                       Can be 'only_download' to ignore only download errors.
                       Default is 'only_download' for CLI, but False for API
    skip_playlist_after_errors: Number of allowed failures until the rest of
                       the playlist is skipped
    allowed_extractors:  List of regexes to match against extractor names that are allowed
    overwrites:        Overwrite all video and metadata files if True,
                       overwrite only non-video files if None
                       and don't overwrite any file if False
    playlist_items:    Specific indices of playlist to download.
    playlistrandom:    Download playlist items in random order.
    lazy_playlist:     Process playlist entries as they are received.
    matchtitle:        Download only matching titles.
    rejecttitle:       Reject downloads for matching titles.
    logger:            Log messages to a logging.Logger instance.
    logtostderr:       Print everything to stderr instead of stdout.
    consoletitle:      Display progress in console window's titlebar.
    writedescription:  Write the video description to a .description file
    writeinfojson:     Write the video description to a .info.json file
    clean_infojson:    Remove internal metadata from the infojson
    getcomments:       Extract video comments. This will not be written to disk
                       unless writeinfojson is also given
    writeannotations:  Write the video annotations to a .annotations.xml file
    writethumbnail:    Write the thumbnail image to a file
    allow_playlist_files: Whether to write playlists' description, infojson etc
                       also to disk when using the 'write*' options
    write_all_thumbnails:  Write all thumbnail formats to files
    writelink:         Write an internet shortcut file, depending on the
                       current platform (.url/.webloc/.desktop)
    writeurllink:      Write a Windows internet shortcut file (.url)
    writewebloclink:   Write a macOS internet shortcut file (.webloc)
    writedesktoplink:  Write a Linux internet shortcut file (.desktop)
    writesubtitles:    Write the video subtitles to a file
    writeautomaticsub: Write the automatically generated subtitles to a file
    listsubtitles:     Lists all available subtitles for the video
    subtitlesformat:   The format code for subtitles
    subtitleslangs:    List of languages of the subtitles to download (can be regex).
                       The list may contain "all" to refer to all the available
                       subtitles. The language can be prefixed with a "-" to
                       exclude it from the requested languages, e.g. ['all', '-live_chat']
    keepvideo:         Keep the video file after post-processing
    daterange:         A utils.DateRange object, download only if the upload_date is in the range.
    skip_download:     Skip the actual download of the video file
    cachedir:          Location of the cache files in the filesystem.
                       False to disable filesystem cache.
    noplaylist:        Download single video instead of a playlist if in doubt.
    age_limit:         An integer representing the user's age in years.
                       Unsuitable videos for the given age are skipped.
    min_views:         An integer representing the minimum view count the video
                       must have in order to not be skipped.
                       Videos without view count information are always
                       downloaded. None for no limit.
    max_views:         An integer representing the maximum view count.
                       Videos that are more popular than that are not
                       downloaded.
                       Videos without view count information are always
                       downloaded. None for no limit.
    download_archive:  A set, or the name of a file where all downloads are recorded.
                       Videos already present in the file are not downloaded again.
    break_on_existing: Stop the download process after attempting to download a
                       file that is in the archive.
    break_per_url:     Whether break_on_reject and break_on_existing
                       should act on each input URL as opposed to for the entire queue
    cookiefile:        File name or text stream from where cookies should be read and dumped to
    cookiesfrombrowser:  A tuple containing the name of the browser, the profile
                       name/path from where cookies are loaded, the name of the keyring,
                       and the container name, e.g. ('chrome', ) or
                       ('vivaldi', 'default', 'BASICTEXT') or ('firefox', 'default', None, 'Meta')
    legacyserverconnect: Explicitly allow HTTPS connection to servers that do not
                       support RFC 5746 secure renegotiation
    nocheckcertificate:  Do not verify SSL certificates
    client_certificate:  Path to client certificate file in PEM format. May include the private key
    client_certificate_key:  Path to private key file for client certificate
    client_certificate_password:  Password for client certificate private key, if encrypted.
                        If not provided and the key is encrypted, yt-dlp will ask interactively
    prefer_insecure:   Use HTTP instead of HTTPS to retrieve information.
                       (Only supported by some extractors)
    enable_file_urls:  Enable file:// URLs. This is disabled by default for security reasons.
    http_headers:      A dictionary of custom headers to be used for all requests
    proxy:             URL of the proxy server to use
    geo_verification_proxy:  URL of the proxy to use for IP address verification
                       on geo-restricted sites.
    socket_timeout:    Time to wait for unresponsive hosts, in seconds
    bidi_workaround:   Work around buggy terminals without bidirectional text
                       support, using fridibi
    debug_printtraffic:Print out sent and received HTTP traffic
    default_search:    Prepend this string if an input url is not valid.
                       'auto' for elaborate guessing
    encoding:          Use this encoding instead of the system-specified.
    extract_flat:      Whether to resolve and process url_results further
                       * False:     Always process. Default for API
                       * True:      Never process
                       * 'in_playlist': Do not process inside playlist/multi_video
                       * 'discard': Always process, but don't return the result
                                    from inside playlist/multi_video
                       * 'discard_in_playlist': Same as "discard", but only for
                                    playlists (not multi_video). Default for CLI
    wait_for_video:    If given, wait for scheduled streams to become available.
                       The value should be a tuple containing the range
                       (min_secs, max_secs) to wait between retries
    postprocessors:    A list of dictionaries, each with an entry
                       * key:  The name of the postprocessor. See
                               yt_dlp/postprocessor/__init__.py for a list.
                       * when: When to run the postprocessor. Allowed values are
                               the entries of utils.POSTPROCESS_WHEN
                               Assumed to be 'post_process' if not given
    progress_hooks:    A list of functions that get called on download
                       progress, with a dictionary with the entries
                       * status: One of "downloading", "error", or "finished".
                                 Check this first and ignore unknown values.
                       * info_dict: The extracted info_dict

                       If status is one of "downloading", or "finished", the
                       following properties may also be present:
                       * filename: The final filename (always present)
                       * tmpfilename: The filename we're currently writing to
                       * downloaded_bytes: Bytes on disk
                       * total_bytes: Size of the whole file, None if unknown
                       * total_bytes_estimate: Guess of the eventual file size,
                                               None if unavailable.
                       * elapsed: The number of seconds since download started.
                       * eta: The estimated time in seconds, None if unknown
                       * speed: The download speed in bytes/second, None if
                                unknown
                       * fragment_index: The counter of the currently
                                         downloaded video fragment.
                       * fragment_count: The number of fragments (= individual
                                         files that will be merged)

                       Progress hooks are guaranteed to be called at least once
                       (with status "finished") if the download is successful.
    postprocessor_hooks:  A list of functions that get called on postprocessing
                       progress, with a dictionary with the entries
                       * status: One of "started", "processing", or "finished".
                                 Check this first and ignore unknown values.
                       * postprocessor: Name of the postprocessor
                       * info_dict: The extracted info_dict

                       Progress hooks are guaranteed to be called at least twice
                       (with status "started" and "finished") if the processing is successful.
    merge_output_format: "/" separated list of extensions to use when merging formats.
    final_ext:         Expected final extension; used to detect when the file was
                       already downloaded and converted
    fixup:             Automatically correct known faults of the file.
                       One of:
                       - "never": do nothing
                       - "warn": only emit a warning
                       - "detect_or_warn": check whether we can do anything
                                           about it, warn otherwise (default)
    source_address:    Client-side IP address to bind to.
    impersonate:       Client to impersonate for requests.
                       An ImpersonateTarget (from yt_dlp.networking.impersonate)
    sleep_interval_requests: Number of seconds to sleep between requests
                       during extraction
    sleep_interval:    Number of seconds to sleep before each download when
                       used alone or a lower bound of a range for randomized
                       sleep before each download (minimum possible number
                       of seconds to sleep) when used along with
                       max_sleep_interval.
    max_sleep_interval:Upper bound of a range for randomized sleep before each
                       download (maximum possible number of seconds to sleep).
                       Must only be used along with sleep_interval.
                       Actual sleep time will be a random float from range
                       [sleep_interval; max_sleep_interval].
    sleep_interval_subtitles: Number of seconds to sleep before each subtitle download
    listformats:       Print an overview of available video formats and exit.
    list_thumbnails:   Print a table of all thumbnails and exit.
    match_filter:      A function that gets called for every video with the signature
                       (info_dict, *, incomplete: bool) -> Optional[str]
                       For backward compatibility with youtube-dl, the signature
                       (info_dict) -> Optional[str] is also allowed.
                       - If it returns a message, the video is ignored.
                       - If it returns None, the video is downloaded.
                       - If it returns utils.NO_DEFAULT, the user is interactively
                         asked whether to download the video.
                       - Raise utils.DownloadCancelled(msg) to abort remaining
                         downloads when a video is rejected.
                       match_filter_func in utils/_utils.py is one example for this.
    color:             A Dictionary with output stream names as keys
                       and their respective color policy as values.
                       Can also just be a single color policy,
                       in which case it applies to all outputs.
                       Valid stream names are 'stdout' and 'stderr'.
                       Valid color policies are one of 'always', 'auto', 'no_color' or 'never'.
    geo_bypass:        Bypass geographic restriction via faking X-Forwarded-For
                       HTTP header
    geo_bypass_country:
                       Two-letter ISO 3166-2 country code that will be used for
                       explicit geographic restriction bypassing via faking
                       X-Forwarded-For HTTP header
    geo_bypass_ip_block:
                       IP range in CIDR notation that will be used similarly to
                       geo_bypass_country
    external_downloader: A dictionary of protocol keys and the executable of the
                       external downloader to use for it. The allowed protocols
                       are default|http|ftp|m3u8|dash|rtsp|rtmp|mms.
                       Set the value to 'native' to use the native downloader
    compat_opts:       Compatibility options. See "Differences in default behavior".
                       The following options do not work when used through the API:
                       filename, abort-on-error, multistreams, no-live-chat,
                       format-sort, no-clean-infojson, no-playlist-metafiles,
                       no-keep-subs, no-attach-info-json, allow-unsafe-ext.
                       Refer __init__.py for their implementation
    progress_template: Dictionary of templates for progress outputs.
                       Allowed keys are 'download', 'postprocess',
                       'download-title' (console title) and 'postprocess-title'.
                       The template is mapped on a dictionary with keys 'progress' and 'info'
    retry_sleep_functions: Dictionary of functions that takes the number of attempts
                       as argument and returns the time to sleep in seconds.
                       Allowed keys are 'http', 'fragment', 'file_access'
    download_ranges:   A callback function that gets called for every video with
                       the signature (info_dict, ydl) -> Iterable[Section].
                       Only the returned sections will be downloaded.
                       Each Section is a dict with the following keys:
                       * start_time: Start time of the section in seconds
                       * end_time: End time of the section in seconds
                       * title: Section title (Optional)
                       * index: Section number (Optional)
    force_keyframes_at_cuts: Re-encode the video when downloading ranges to get precise cuts
    noprogress:        Do not print the progress bar
    live_from_start:   Whether to download livestreams videos from the start

    The following parameters are not used by YoutubeDL itself, they are used by
    the downloader (see yt_dlp/downloader/common.py):
    nopart, updatetime, buffersize, ratelimit, throttledratelimit, min_filesize,
    max_filesize, test, noresizebuffer, retries, file_access_retries, fragment_retries,
    continuedl, xattr_set_filesize, hls_use_mpegts, http_chunk_size,
    external_downloader_args, concurrent_fragment_downloads, progress_delta.

    The following options are used by the post processors:
    ffmpeg_location:   Location of the ffmpeg/avconv binary; either the path
                       to the binary or its containing directory.
    postprocessor_args: A dictionary of postprocessor/executable keys (in lower case)
                       and a list of additional command-line arguments for the
                       postprocessor/executable. The dict can also have "PP+EXE" keys
                       which are used when the given exe is used by the given PP.
                       Use 'default' as the name for arguments to passed to all PP
                       For compatibility with youtube-dl, a single list of args
                       can also be used

    The following options are used by the extractors:
    extractor_retries: Number of times to retry for known errors (default: 3)
    dynamic_mpd:       Whether to process dynamic DASH manifests (default: True)
    hls_split_discontinuity: Split HLS playlists to different formats at
                       discontinuities such as ad breaks (default: False)
    extractor_args:    A dictionary of arguments to be passed to the extractors.
                       See "EXTRACTOR ARGUMENTS" for details.
                       E.g. {'youtube': {'skip': ['dash', 'hls']}}
    mark_watched:      Mark videos watched (even with --simulate). Only for YouTube

    The following options are deprecated and may be removed in the future:

    break_on_reject:   Stop the download process when encountering a video that
                       has been filtered out.
                       - `raise DownloadCancelled(msg)` in match_filter instead
    force_generic_extractor: Force downloader to use the generic extractor
                       - Use allowed_extractors = ['generic', 'default']
    playliststart:     - Use playlist_items
                       Playlist item to start at.
    playlistend:       - Use playlist_items
                       Playlist item to end at.
    playlistreverse:   - Use playlist_items
                       Download playlist items in reverse order.
    forceurl:          - Use forceprint
                       Force printing final URL.
    forcetitle:        - Use forceprint
                       Force printing title.
    forceid:           - Use forceprint
                       Force printing ID.
    forcethumbnail:    - Use forceprint
                       Force printing thumbnail URL.
    forcedescription:  - Use forceprint
                       Force printing description.
    forcefilename:     - Use forceprint
                       Force printing final filename.
    forceduration:     - Use forceprint
                       Force printing duration.
    allsubtitles:      - Use subtitleslangs = ['all']
                       Downloads all the subtitles of the video
                       (requires writesubtitles or writeautomaticsub)
    include_ads:       - Doesn't work
                       Download ads as well
    call_home:         - Not implemented
                       Boolean, true iff we are allowed to contact the
                       yt-dlp servers for debugging.
    post_hooks:        - Register a custom postprocessor
                       A list of functions that get called as the final step
                       for each video file, after all postprocessors have been
                       called. The filename will be passed as the only argument.
    hls_prefer_native: - Use external_downloader = {'m3u8': 'native'} or {'m3u8': 'ffmpeg'}.
                       Use the native HLS downloader instead of ffmpeg/avconv
                       if True, otherwise use ffmpeg/avconv if False, otherwise
                       use downloader suggested by extractor if None.
    prefer_ffmpeg:     - avconv support is deprecated
                       If False, use avconv instead of ffmpeg if both are available,
                       otherwise prefer ffmpeg.
    youtube_include_dash_manifest: - Use extractor_args
                       If True (default), DASH manifests and related
                       data will be downloaded and processed by extractor.
                       You can reduce network I/O by disabling it if you don't
                       care about DASH. (only for youtube)
    youtube_include_hls_manifest: - Use extractor_args
                       If True (default), HLS manifests and related
                       data will be downloaded and processed by extractor.
                       You can reduce network I/O by disabling it if you don't
                       care about HLS. (only for youtube)
    no_color:          Same as `color='no_color'`
    no_overwrites:     Same as `overwrites=False`
```

## 简要翻译

阅读原文获取完整参数的完整介绍，要特别注意参数的类型，比如是元组还是字符串。

| 参数名                       | 描述                                                         |
| ---------------------------- | ------------------------------------------------------------ |
| `username`                   | 用于认证的用户名。                                           |
| `password`                   | 用于认证的密码。                                             |
| videopassword                | 访问视频的密码。                                             |
| ap_mso                       | Adobe Pass多系统运营商标识符。                               |
| ap_username                  | 多系统运营商账户用户名。                                     |
| ap_password                  | 多系统运营商账户密码。                                       |
| usenetrc                     | 使用netrc文件进行认证。                                      |
| netrc_location               | netrc文件的位置。默认为~/.netrc。                            |
| netrc_cmd                    | 使用shell命令获取凭据。                                      |
| verbose                      | 在stdout打印额外信息。                                       |
| `quiet`                      | 不在stdout打印消息。                                         |
| `no_warnings`                | 不打印警告。                                                 |
| forceprint                   | 打印到stdout的模板字典。允许的键是video或utils.POSTPROCESS_WHEN中的任何项。 |
| print_to_file                | 打印到文件的模板字典。允许的键是WHEN（与forceprint相同）。   |
| forcejson                    | 强制将info_dict作为JSON打印。                                |
| dump_single_json             | 强制将整个播放列表（或视频）的info_dict作为单个JSON行打印。  |
| force_write_download_archive | 强制写入下载存档，而不管'skip_download'或'simulate'。        |
| simulate                     | 不下载视频文件。如果未设置（或为None），则仅在使用listsubtitles、listformats或list_thumbnails时模拟。 |
| `format`                     | 视频格式代码。详见“FORMAT SELECTION”。                       |
| allow_unplayable_formats     | 允许提取和下载不可播放的格式。                               |
| ignore_no_formats_error      | 忽略“无视频格式”错误。仅用于提取元数据，即使视频实际上无法下载（实验性）。 |
| format_sort                  | 按照给定的字段列表对视频格式进行排序。详见“Sorting Formats”。 |
| format_sort_force            | 强制给定的format_sort排序。详见“Sorting Formats”。           |
| prefer_free_formats          | 是否优先选择具有免费容器的视频格式。                         |
| allow_multiple_video_streams | 允许合并多个视频流到单个文件。                               |
| allow_multiple_audio_streams | 允许合并多个音频流到单个文件。                               |
| check_formats                | 是否测试格式是否可下载。可以是True（检查全部）、False（不检查）、'selected'（检查选定的格式）、或None（仅在提取器请求时检查）。 |
| paths                        | 输出路径的字典。允许的键有'home'、'temp'和OUTTMPL_TYPES中的键（在utils/_utils.py中）。 |
| outtmpl                      | 输出名称的模板字典。允许的键有'default'和OUTTMPL_TYPES中的键（在utils/_utils.py中）。 |
| outtmpl_na_placeholder       | 不可用元字段的占位符。                                       |
| restrictfilenames            | 不允许在文件名中使用'&'和空格。                              |
| trim_file_name               | 限制文件名的长度（不包括扩展名）。                           |
| windowsfilenames             | 强制文件名为Windows兼容。                                    |
| `ignoreerrors`               | 不在下载/后处理错误时停止。可以是'only_download'仅忽略下载错误。 |
| skip_playlist_after_errors   | 允许的失败次数，直到跳过播放列表的其余部分。                 |
| allowed_extractors           | 允许的提取器名称的正则表达式列表。                           |
| overwrites                   | 如果为True，则覆盖所有视频和元数据文件；如果为None，则仅覆盖非视频文件；如果为False，则不覆盖任何文件。 |
| playlist_items               | 要下载的播放列表的特定索引。                                 |
| playlistrandom               | 随机顺序下载播放列表项。                                     |
| lazy_playlist                | 收到时即处理播放列表条目。                                   |
| matchtitle                   | 仅下载匹配的标题。                                           |
| rejecttitle                  | 拒绝下载匹配的标题。                                         |
| `logger`                     | 记录消息到logging.Logger实例。                               |
| logtostderr                  | 将所有内容打印到stderr而不是stdout。                         |
| `consoletitle`               | 在控制台窗口标题栏中显示进度。                               |
| writedescription             | 将视频描述写入.description文件。                             |
| writeinfojson                | 将视频描述写入.info.json文件。                               |
| clean_infojson               | 从infojson中删除内部元数据。                                 |
| getcomments                  | 提取视频评论。仅在同时给出writeinfojson时写入磁盘。          |
| writeannotations             | 将视频注释写入.annotations.xml文件。                         |
| writethumbnail               | 将缩略图图像写入文件。                                       |
| allow_playlist_files         | 在使用'write*'选项时，是否将播放列表的描述、infojson等写入磁盘。 |
| write_all_thumbnails         | 将所有缩略图格式写入文件。                                   |
| writelink                    | 根据当前平台写入Internet快捷方式文件（.url/.webloc/.desktop）。 |
| writeurllink                 | 写入Windows Internet快捷方式文件（.url）。                   |
| writewebloclink              | 写入macOS Internet快捷方式文件（.webloc）。                  |
| writedesktoplink             | 写入Linux Internet快捷方式文件（.desktop）。                 |
| `writesubtitles`             | 将视频字幕写入文件。                                         |
| writeautomaticsub            | 将自动生成的字幕写入文件。                                   |
| listsubtitles                | 列出所有可用字幕。                                           |
| subtitlesformat              | 字幕格式代码。                                               |
| subtitleslangs               | 要下载的字幕语言列表（可以是正则表达式）。                   |
| keepvideo                    | 在后处理后保留视频文件。                                     |
| daterange                    | 日期范围对象，仅在上传日期在范围内时下载。                   |
| skip_download                | 跳过实际的视频文件下载。如果不设置（或为None），则仅在使用listsubtitles、listformats或list_thumbnails时模拟。 |
| cachedir                     | 文件系统中缓存文件的位置。                                   |
| `noplaylist`                 | 如果不确定，下载单个视频而不是播放列表。                     |
| age_limit                    | 用户年龄的整数表示。跳过不适合给定年龄的视频。               |
| min_views                    | 视频必须具有的最低观看次数。                                 |
| max_views                    | 视频必须具有的最大观看次数。                                 |
| download_archive             | 记录所有下载的文件的集合或文件名。已经在文件中的视频不会再次下载。 |
| break_on_existing            | 尝试下载已在存档中的文件后停止下载过程。                     |
| break_per_url                | break_on_reject和break_on_existing是否应作用于每个输入URL而不是整个队列。 |
| `cookiefile`                 | 读取和转储Cookie的文件名或文本流。                           |
| `cookiesfrombrowser`         | 包含从中加载Cookie的浏览器、配置文件名称/路径、密钥环名称和容器名称的元组。 |
| legacyserverconnect          | 显式允许连接到不支持RFC 5746安全重新协商的服务器的HTTPS连接。 |
| nocheckcertificate           | 不验证SSL证书。                                              |
| client_certificate           | PEM格式客户端证书文件的路径。可以包括私钥。                  |
| client_certificate_key       | 用于客户端证书私钥文件的路径。                               |
| client_certificate_password  | 客户端证书私钥的密码，如果加密。如果未提供且                 |
| prefer_insecure             | 使用 HTTP 而不是 HTTPS 获取信息。仅某些提取器支持。          |
| enable_file_urls            | 启用 file:// URL。出于安全原因，默认禁用。                   |
| http_headers                | 自定义头部字典，用于所有请求。                               |
| `proxy`                     | 要使用的代理服务器的 URL。                                   |
| geo_verification_proxy      | 用于 IP 地址验证的代理的 URL。                               |
| socket_timeout              | 等待无响应主机的时间，单位为秒。                             |
| bidi_workaround             | 解决没有双向文本支持的错误终端问题，使用 fridibi。           |
| debug_printtraffic          | 打印发送和接收的 HTTP 流量。                                 |
| default_search              | 如果输入 URL 无效，前置的字符串。"auto" 用于详尽猜测。       |
| encoding                    | 使用此编码代替系统指定的编码。                               |
| extract_flat                | 是否进一步解析和处理 url_results。                           |
| wait_for_video              | 如果给定，等待计划的流视频可用。值应该是包含重试之间的时间范围的元组 (min_secs, max_secs)。 |
| postprocessors              | 一个字典列表，每个条目包含：                                 |
|                             | - key: 后处理器的名称。见 yt_dlp/postprocessor/__init__.py 的列表。 |
|                             | - when: 何时运行后处理器。允许的值为 utils.POSTPROCESS_WHEN 的条目。默认为 'post_process'。 |
| progress_hooks              | 一个函数列表，会在下载进度更新时调用，参数是包含状态和 info_dict 的字典。 |
| postprocessor_hooks         | 一个函数列表，会在后处理进度更新时调用，参数是包含状态、后处理器名称和 info_dict 的字典。 |
| merge_output_format         | "/" 分隔的扩展名列表，在合并格式时使用。                     |
| final_ext                   | 预期的最终扩展名；用于检测文件是否已经下载并转换。           |
| fixup                       | 自动修正已知文件错误。可能的值有："never"、"warn"、"detect_or_warn"。 |
| source_address              | 客户端绑定到的 IP 地址。                                     |
| impersonate                 | 请求中要模拟的客户端。                                       |
| sleep_interval_requests     | 抽取期间在请求之间等待的秒数。                               |
| sleep_interval              | 每次下载前的睡眠时间，或随机睡眠的最低范围。                 |
| max_sleep_interval          | 每次下载前的随机睡眠的最高范围。                             |
| sleep_interval_subtitles    | 每个字幕下载前的睡眠时间。                                   |
| sleep_interval_subtitles | 每个字幕下载前的睡眠时间。                                   |
| listformats              | 打印可用视频格式的概述并退出。                               |
| list_thumbnails          | 打印所有缩略图的表格并退出。                                 |
| match_filter             | 一个用于每个视频的函数，返回一个可选的消息或 None。如果返回消息，视频将被忽略。 |
| color                    | 输出流名称作为键的颜色策略字典。                             |
| geo_bypass               | 通过伪造 X-Forwarded-For HTTP 标头来绕过地理限制。           |
| geo_bypass_country       | 用于显式地通过伪造 X-Forwarded-For HTTP 标头绕过地理限制的两字母 ISO 3166-2 国家代码。 |
| geo_bypass_ip_block      | 以 CIDR 表示法的 IP 范围，类似于 geo_bypass_country。        |
| external_downloader      | 用于每个协议键的外部下载器的执行文件字典。                   |
| compat_opts              | 兼容性选项。查看 "Differences in default behavior"。         |
| progress_template        | 进度输出的模板字典。允许的键有 'download'、'postprocess'、'download-title' 和 'postprocess-title'。 |
| retry_sleep_functions    | 每次尝试后返回睡眠时间的函数字典。允许的键有 'http'、'fragment' 和 'file_access'。 |
| download_ranges          | 用于每个视频的回调函数，返回一个包含部分信息的可迭代对象。只有返回的部分会被下载。 |
| force_keyframes_at_cuts  | 在下载范围时重新编码视频以获取精确的切割。                   |
| `noprogress`             | 不打印进度条。                                               |
| live_from_start          | 是否从直播开始下载视频。                                     |

**下载器相关参数**

| 参数                          | 描述                            |
| ----------------------------- | ------------------------------- |
| nopart                        | 是否在下载时创建 .part 文件。   |
| updatetime                    | 更新时间。                      |
| buffersize                    | 缓冲区大小。                    |
| ratelimit                     | 速率限制。                      |
| throttledratelimit            | 节流速率限制。                  |
| min_filesize                  | 最小文件大小。                  |
| max_filesize                  | 最大文件大小。                  |
| test                          | 测试。                          |
| noresizebuffer                | 是否禁用缓冲区大小调整。        |
| `retries`                     | 下载重试次数。                  |
| `file_access_retries`         | 文件访问重试次数。              |
| `fragment_retries`            | 片段下载重试次数。              |
| `continuedl`                  | 是否继续未完成的下载。          |
| xattr_set_filesize            | 是否设置文件大小属性。          |
| hls_use_mpegts                | 是否使用 MPEG-TS 格式下载 HLS。 |
| http_chunk_size               | HTTP 下载的分块大小。           |
| external_downloader_args      | 外部下载器的参数。              |
| concurrent_fragment_downloads | 并发下载片段数。                |
| progress_delta                | 下载进度的间隔。                |

**后处理器相关参数**

| 参数               | 描述                                       |
| ------------------ | ------------------------------------------ |
| ffmpeg_location    | ffmpeg/avconv 二进制文件的位置。           |
| postprocessor_args | 后处理器或执行程序的额外命令行参数的字典。 |

**提取器相关参数**

| 参数                    | 描述                                                      |
| ----------------------- | --------------------------------------------------------- |
| `extractor_retries`     | 已知错误重试次数。                                        |
| dynamic_mpd             | 是否处理动态 DASH 清单。                                  |
| hls_split_discontinuity | 是否在 HLS 清单的不连续点（如广告中断）处拆分为不同格式。 |
| extractor_args          | 传递给提取器的参数字典。                                  |
| mark_watched            | 标记视频为已观看状态（即使使用 --simulate）。             |

**已废弃参数**

| 参数                          | 替代方案或说明                                               |
| ----------------------------- | ------------------------------------------------------------ |
| break_on_reject               | 在 `match_filter` 中遇到被过滤视频时停止下载。               |
| force_generic_extractor       | 强制使用通用提取器。                                         |
| playliststart                 | 使用 `playlist_items` 替代，指定开始下载的播放列表项。       |
| playlistend                   | 使用 `playlist_items` 替代，指定结束下载的播放列表项。       |
| playlistreverse               | 使用 `playlist_items` 替代，倒序下载播放列表项。             |
| forceurl                      | 使用 `forceprint` 替代，强制打印最终 URL。                   |
| forcetitle                    | 使用 `forceprint` 替代，强制打印标题。                       |
| forceid                       | 使用 `forceprint` 替代，强制打印视频 ID。                    |
| forcethumbnail                | 使用 `forceprint` 替代，强制打印缩略图 URL。                 |
| forcedescription              | 使用 `forceprint` 替代，强制打印视频描述。                   |
| forcefilename                 | 使用 `forceprint` 替代，强制打印最终文件名。                 |
| forceduration                 | 使用 `forceprint` 替代，强制打印视频时长。                   |
| allsubtitles                  | 使用 `subtitleslangs = ['all']` 替代，下载视频的所有字幕（需要 `writesubtitles` 或 `writeautomaticsub`）。 |
| include_ads                   | 不再起作用。                                                 |
| call_home                     | 未实现。                                                     |
| post_hooks                    | 注册自定义后处理器的函数列表。                               |
| hls_prefer_native             | 使用 `external_downloader = {'m3u8': 'native'}` 或 `{'m3u8': 'ffmpeg'}` 替代。 |
| prefer_ffmpeg                 | 如果可用，优先使用 ffmpeg 而不是 avconv。                    |
| youtube_include_dash_manifest | 使用 `extractor_args` 替代，是否下载和处理 DASH 清单及相关数据（仅适用于 YouTube）。 |
| youtube_include_hls_manifest  | 使用 `extractor_args` 替代，是否下载和处理 HLS 清单及相关数据（仅适用于 YouTube）。 |
| no_color                      | 同 `color='no_color'`。                                      |
| no_overwrites                 | 同 `overwrites=False`。                                      |