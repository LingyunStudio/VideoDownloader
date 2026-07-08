# VideoDownloader

基于 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 的桌面视频下载器，使用 **PyQt6** 构建图形界面。支持数千个网站，可视化选择清晰度与编码、自动合并音视频、下载队列、播放列表批量下载，以及 yt-dlp 运行时在线更新（无需重新打包）。

<!-- 截图：主界面 -->
> 截图占位：主界面（左侧控制栏：链接 / 下载选项 / 格式选择；右侧：视频信息与缩略图 / 下载队列）

## 功能特性

- **可视化格式选择**：解析后列出全部可用格式，按「纯视频 / 纯音频 / 合一」三组展示，标注分辨率、编码（H.264 / AV1 / VP9 …）、码率与大小；勾选 1 视频 + 1 音频自动合并，或勾选 1 合一直接下载，★ 标记推荐项
- **容器选择**：自动 / mp4 / webm / mkv / mov
- **Cookies 支持**：从 Firefox / Chrome / Edge / Brave 浏览器读取（默认 Firefox），用于需要登录才能访问的视频
- **播放列表**：自动识别播放列表并批量下载（按最佳质量）
- **下载队列**：多任务并发，实时显示大小 / 速度 / 剩余时间，合并与转码阶段单独提示
- **yt-dlp 运行时更新**：界面内检查 GitHub 最新版并下载，重启后生效，覆盖打包内置副本
- **软件自动更新**：界面内检查 GitHub 最新版本，有新版自动下载安装包、静默安装并重启（保持原安装目录，更新时弹一次 UAC）
- **打开保存目录**：一键在资源管理器中打开当前保存目录，方便查看下载结果
- **ffmpeg 自动就绪**：打包版运行时下载 ffmpeg 到 `%APPDATA%`；开发模式经 static_ffmpeg 注入，无需手动安装
- **缩略图与元信息**：展示标题、作者、时长、播放量、点赞等
- **高清分离流**：启用 node / deno JS 运行时，YouTube 等站点可获取高分辨率分离流

## 截图

<!-- 截图：解析后格式选择 -->
> 截图占位：解析视频后，格式选择表与视频信息

<!-- 截图：下载队列 -->
> 截图占位：下载队列与进度

<!-- 截图：yt-dlp 更新 -->
> 截图占位：yt-dlp 检查更新

## 下载安装

前往 [Releases](https://github.com/LingyunStudio/VideoDownloader/releases) 下载：

- `VideoDownloader_Setup.exe`：Inno Setup 安装程序（中文界面，推荐）
- 或运行 onedir 目录中的 `VideoDownloader.exe`（便携）

> 首次运行会自动下载 ffmpeg 到 `%APPDATA%\VideoDownloader\ffmpeg`，需联网。

## 从源码运行

```bash
conda create -n videodownload python=3.12
conda activate videodownload
pip install yt-dlp PyQt6 static-ffmpeg

git clone https://github.com/LingyunStudio/VideoDownloader.git
cd VideoDownloader/pyqt6-downloader
python app.py
```

## 从源码构建

依赖 [PyInstaller](https://pyinstaller.org/) 与 [Inno Setup 6](https://jrsoftware.org/isdl/)（可选，用于生成安装包）：

```bash
pip install pyinstaller
# 在 pyqt6-downloader 目录下
powershell -ExecutionPolicy Bypass -File build.ps1
```

`build.ps1` 常用选项：

| 选项 | 作用 |
|---|---|
| `-Clean` | 先清理旧的 build / dist |
| `-SkipInstaller` | 跳过 Inno Setup，仅生成 onedir |
| `-Python <path>` | 指定 python.exe（默认 conda 环境 `videodownload`） |
| `-Iscc <path>` | 指定 ISCC.exe（默认 `D:\InnoSetup6\ISCC.exe`） |

输出：

- `dist\VideoDownloader\`：PyInstaller onedir 目录
- `dist\VideoDownloader_Setup.exe`：安装包

## 使用说明

1. 粘贴视频或播放列表链接到顶部输入框
2. 选择 Cookies 来源（默认 Firefox）与保存目录（点「打开」可在资源管理器中查看该目录）
3. 点击「解析」，等待获取视频信息与可用格式
4. 在格式表勾选目标格式（1 视频 + 1 音频自动合并，或 1 合一），可选容器
5. 点击「下载」，任务进入队列并显示进度
6. 顶部「检查更新」在线更新 yt-dlp（重启生效）；「检查软件更新」可下载并自动安装新版软件（保持原安装目录，自动重启）

输出文件名模板：`%(title).100B [%(id)s].%(ext)s`

## 技术细节

- **运行时 yt-dlp 更新**：从 GitHub releases 下载源码 tar.gz 解压到 `%APPDATA%\VideoDownloader\updates\` 并写入标记；启动时通过 `sys.meta_path` 查找器优先从用户目录加载 `yt_dlp` 及其子模块，覆盖打包内置副本。
- **软件自动更新**：检查 GitHub releases/latest 的 tag，与内置 `APP_VERSION` 比对；有新版则下载 `VideoDownloader_Setup.exe` 到 `%APPDATA%\VideoDownloader\updates\app\`，以 `ShellExecute "runas"` 静默启动安装包并退出当前进程；Inno Setup 经 `UsePreviousAppDir` 装回原目录，安装后重启。
- **ffmpeg**：开发模式用 `static_ffmpeg.add_paths()` 注入 PATH；打包后从 `%APPDATA%\VideoDownloader\ffmpeg` 加载，并传 `ffmpeg_location` 给 yt-dlp。
- **打包**：PyInstaller onedir，`VideoDownloader.spec` 收集 yt-dlp 及可选依赖（brotli / mutagen / websockets / certifi / curl_cffi / socks）；排除未使用的 Qt 大模块与 static_ffmpeg 以精简体积。

## 项目结构

```
pyqt6-downloader/
├── app.py                  # 入口
├── downloader/
│   ├── core.py             # yt-dlp 封装：元数据提取、格式解析、下载工作线程
│   ├── updater.py          # yt-dlp 运行时更新（meta_path 覆盖）
│   ├── app_updater.py      # 软件自身更新（GitHub tag 检查 + 静默安装）
│   ├── app_version.py      # 软件版本号
│   ├── ffmpeg_setup.py     # 打包版 ffmpeg 运行时下载
│   └── debug.py            # 轻量 trace 日志
├── ui/
│   ├── main_window.py      # 主窗口
│   └── style.py            # QSS 样式
├── build.ps1               # 一键构建脚本
├── installer.iss           # Inno Setup 安装包配置
├── VideoDownloader.spec    # PyInstaller 配置
├── requirements.txt        # 依赖说明
└── icon/                   # 图标资源
```

## 故障排查

- 程序启动或运行异常时，查看 `%APPDATA%\VideoDownloader\` 下的 `trace.log`（运行轨迹）与 `crash.log`（崩溃信息）。
- 缩略图无法加载：通常为网络问题，不影响下载。
- 高清格式缺失：确保已安装 [Node.js](https://nodejs.org/)（部分站点需要 JS 运行时才能拿到分离流）。

## 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — 功能强大的命令行视频下载器，本项目基于其 Python 库开发

## 许可证

参见 [LICENSE](LICENSE)
