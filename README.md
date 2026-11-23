# VideoDownloader (WinUI 3)

基于 **C# · .NET 8 · WinUI 3（Windows App SDK）** 构建的原生 Windows 11 视频下载器，后端集成高速版 `yt-dlp` 与 `ffmpeg`，支持数千个视频网站。

## 核心特性

- **原生 Windows 11 Fluent 体验**：支持 Mica / Mica Alt / Acrylic 窗口材质、浅色 / 深色 / 跟随系统主题实时切换、自定义无边框标题栏与高 DPI 缩放。
- **解析与可视化格式选择**：
  - 支持单视频解析与播放列表自动识别。
  - 提供「最佳画质」「1080p 均衡」「仅音频提取（MP3/M4A/FLAC/Opus/WAV）」「自定义格式」四大模式。
  - 自定义模式按「纯视频流 / 纯音频流 / 音视频合一」分组展示分辨率、帧率、编码（H.264 / H.265 / AV1 / VP9 / AAC / Opus）、码率、大小与 `★ 推荐` 标记；支持 1 视频 + 1 音频自动合并。
  - 支持剪贴板一键粘贴、多行链接直接批量加入下载队列。
- **高级下载能力**：
  - 封装容器选择（auto / mp4 / mkv / webm / mov）。
  - 浏览器 Cookies 读取（Firefox / Chrome / Edge / Brave）及本地 `.txt` Cookies 文件导入。
  - 字幕下载与嵌入、封面缩略图嵌入、视频元数据写入、时间片段裁剪（如 `00:01:00-00:02:30`）、自定义代理、Node / Deno JS 运行时高清分离流支持。
- **并发下载队列**：可配置最大并发数，实时展示单任务进度 / 速度 / 剩余时间与全局总速度；支持取消、重试、定位已下载文件。
- **下载历史记录**：本地持久化归档已完成任务，支持搜索过滤、一键定位文件、打开原网页与一键重新下载。
- **零重启在线更新**：
  - 首次运行自动下载并管理高速非单文件版 `yt-dlp_win.zip` 与 `ffmpeg` 到 `%APPDATA%\VideoDownloader\`。
  - 设置页支持一键检查并在线更新 `yt-dlp`（下一次任务立即生效，无需重启软件）以及软件自身静默升级。

## 性能与内存优化

- **Workstation GC + 源生成 JSON + 编译期 `x:Bind`**：全程零反射绑定与序列化，降低内存占用与 GC 停顿。
- **缩略图低内存解码**：限定 `DecodePixelWidth = 320`，避免 4K 原图解码占用数十 MB 显存/内存。
- **进度节流**：下载进度按 ~10 FPS 节流合并推向 UI 线程，显著降低下载时的 CPU 与分配开销。
- **Windows Job Object 进程树托管**：所有 `yt-dlp` / `ffmpeg` 子进程绑定至 Job Object，取消任务或主程序退出时瞬时清理整棵进程树，杜绝孤儿进程残留。
- **高速非单文件 `yt-dlp`**：优先下载 `yt-dlp_win.zip`，避免单文件版每次运行解压带来的 1 秒以上冷启动延迟。

## 构建与打包

依赖：**.NET 8 SDK**（Windows 10/11 x64）与 **Inno Setup 6**（可选，用于生成安装包）。

```powershell
# 开发调试构建
dotnet build src\VideoDownloader\VideoDownloader.csproj -c Debug -p:Platform=x64

# 一键发布 Release 并生成安装包
powershell -ExecutionPolicy Bypass -File build.ps1

# 仅生成便携发布目录（跳过安装包）
powershell -ExecutionPolicy Bypass -File build.ps1 -SkipInstaller
```

## 项目结构

```text
VideoDownloader_Project/
├── VideoDownloader.sln
├── build.ps1                   # 一键发布与打包脚本
├── installer.iss               # Inno Setup 安装包配置
├── icon/                       # 原始图标资源（1.ico, dlp.png 等）
└── src/VideoDownloader/
    ├── App.xaml / .cs          # 应用入口与轻量无反射依赖管理
    ├── MainWindow.xaml / .cs   # Mica 窗口壳、自定义标题栏与页面缓存导航
    ├── Models/                 # 数据模型与 System.Text.Json 源生成上下文
    ├── Helpers/                # Job Object、格式化工具、窗口与文件选择器、日志
    ├── Services/               # yt-dlp / 队列 / 工具管理 / 设置 / 历史 / 自更新服务
    ├── ViewModels/             # MVVM 视图模型（CommunityToolkit.Mvvm）
    ├── Converters/             # 轻量值转换器
    └── Views/                  # Home / Downloads / History / Settings 页面
```
