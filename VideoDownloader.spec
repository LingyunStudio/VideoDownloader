# -*- mode: python ; coding: utf-8 -*-
"""VideoDownloader PyInstaller spec.

要点（精简体积）：
- yt_dlp 不冻结：作为源码随程序分发（dist/VideoDownloader/yt-dlp-bundled/），
  启动时由 downloader.updater 插入 sys.path，可被运行时下载的更新覆盖。
- 排除未使用的大型 Qt 模块（WebEngine / Qt3D / Multimedia / Quick / Qml …）。
- 仅 collect yt-dlp 的可选依赖（brotli/mutagen/websockets/certifi/curl_cffi/socks）
  与 static_ffmpeg。
"""
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []

# yt_dlp：冻结进包（collect_all 自动追踪其全部 import，含 glob 等 stdlib，
# 避免「No module named glob」）。运行时更新通过 downloader.updater 的
# meta_path 查找器优先从用户目录加载，覆盖冻结副本。
# static_ffmpeg 不打包——ffmpeg 运行时下载到 %APPDATA%，避免 ~198MB 体积。
for pkg in ("yt_dlp", "brotli", "mutagen", "websockets", "certifi", "curl_cffi", "socks"):
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

# icon 资源打进包，供 UI 内品牌 logo 等加载
datas += [("icon", "icon")]

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    excludes=[
        "static_ffmpeg",  # 运行时下载 ffmpeg 到 %APPDATA%，不打包
        # PyQt6 未使用的大模块
        "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineQuick",
        "PyQt6.QtWebChannel", "PyQt6.QtWebEngineProcess",
        "PyQt6.QtQml", "PyQt6.QtQuick", "PyQt6.QtQuick3D", "PyQt6.QtQuickWidgets",
        "PyQt6.QtQuickControls2", "PyQt6.QtQmlModels", "PyQt6.QtQmlWorkerScript",
        "PyQt6.Qt3DCore", "PyQt6.Qt3DRender", "PyQt6.Qt3DInput",
        "PyQt6.Qt3DLogic", "PyQt6.Qt3DAnimation", "PyQt6.Qt3DExtras",
        "PyQt6.QtMultimedia", "PyQt6.QtMultimediaWidgets",
        "PyQt6.QtCharts", "PyQt6.QtDataVisualization", "PyQt6.QtDataVisualizationQml",
        "PyQt6.QtPdf", "PyQt6.QtPdfWidgets",
        "PyQt6.QtBluetooth", "PyQt6.QtSensors", "PyQt6.QtSerialPort",
        "PyQt6.QtPositioning", "PyQt6.QtLocation", "PyQt6.QtNfc",
        "PyQt6.QtSql", "PyQt6.QtTest", "PyQt6.QtDesigner", "PyQt6.QtHelp",
        "PyQt6.QtRemoteObjects", "PyQt6.QtScxml", "PyQt6.QtWebSockets",
        "PyQt6.QtSpeech",
        # QtNetwork：缩略图改用 Python urllib 后不再需要，排除以消除 frozen 下
        # QtNetwork/SSL C 层段错误崩溃面。
        "PyQt6.QtNetwork",
        # 标准库中无用的大块
        "tkinter", "unittest", "pydoc_data", "test",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VideoDownloader",
    console=False,
    icon="icon/1.ico",
    uac_admin=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="VideoDownloader",
)
