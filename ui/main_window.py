"""主窗口：URL 解析、信息展示、格式选择、在线预览、下载队列。

布局：左控制栏（URL/选项/格式表）+ 右内容区（预览/信息/队列）。
"""
from __future__ import annotations

import os
import sys
from typing import Optional

from PyQt6.QtCore import Qt, QUrl, QByteArray, QRect, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QColor, QLinearGradient, QPainter, QFont, QPalette
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QProgressDialog,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QStatusBar,
)

from downloader.core import (
    DownloadWorker,
    ExtractWorker,
    FormatOption,
    VideoInfo,
    build_format_from_ids,
    build_merge_output_format,
    ensure_ffmpeg,
    ffmpeg_location,
    human_eta,
    human_size,
    human_speed,
)
from downloader.ffmpeg_setup import FFmpegSetupWorker
from downloader.updater import UpdateWorker, get_current_version, get_active_source
from downloader.app_version import APP_VERSION
from downloader.app_updater import AppUpdateWorker, install_and_restart
from ui.style import QSS


def _bundled_path(*parts: str) -> str:
    """返回打包资源路径：冻结时用 sys._MEIPASS，开发时用源码根目录。"""
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    return os.path.join(base, *parts)


def _codec_label(codec: str) -> str:
    c = (codec or "").lower()
    if not c or c == "none":
        return "—"
    if c.startswith("avc1") or c.startswith("h264") or c.startswith("avc3"):
        return "H.264"
    if c.startswith("av01") or c.startswith("av1"):
        return "AV1"
    if c.startswith("vp9"):
        return "VP9"
    if c.startswith("vp8"):
        return "VP8"
    if c.startswith("mp4a"):
        return "AAC"
    if c.startswith("opus"):
        return "Opus"
    if c.startswith("vorbis"):
        return "Vorbis"
    if c.startswith("ac-3") or c.startswith("ac3"):
        return "AC-3"
    if c.startswith("ec-3"):
        return "E-AC-3"
    return c[:8].upper()


class ProgressBar(QProgressBar):
    """自绘进度条：圆角渐变填充 + 居中百分比文字，支持不确定模式（忙时滚动）。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setFixedHeight(22)
        self._busy = False
        self._busy_offset = 0
        self._state = ""  # "" / "done" / "error"

    def set_busy(self, busy: bool):
        if busy == self._busy:
            return
        self._busy = busy
        if busy:
            self.setRange(0, 0)
        else:
            self.setRange(0, 100)
        self.update()

    def set_state(self, state: str):
        self._state = state
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        w, h = rect.width(), rect.height()
        r = h // 2

        # 背景槽
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#e8ecf4"))
        p.drawRoundedRect(rect, r, r)

        if self._busy:
            # 不确定模式：一段渐变条循环滑动
            self._busy_offset = (self._busy_offset + 6) % (w + 60)
            seg_w = min(80, w)
            x = self._busy_offset - 60
            grad = QLinearGradient(x, 0, x + seg_w, 0)
            c = QColor("#1aa260") if self._state == "done" else (
                QColor("#e23e5b") if self._state == "error" else QColor("#3b6ef6"))
            g0, g1 = QColor(c), QColor(c)
            g0.setAlpha(0); g1.setAlpha(220)
            grad.setColorAt(0.0, g0)
            grad.setColorAt(0.5, g1)
            grad.setColorAt(1.0, g0)
            p.setBrush(grad)
            p.drawRoundedRect(rect.intersected(QRect(x, 0, seg_w, h)), r, r)
            p.setPen(QColor("#6b7280"))
            p.setFont(QFont("Microsoft YaHei UI", 8))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "下载中…")
            return

        # 确定模式：渐变填充
        lo, hi = self.minimum(), self.maximum()
        frac = (self.value() - lo) / (hi - lo) if hi > lo else 0.0
        frac = max(0.0, min(1.0, frac))
        fill_w = int(w * frac)
        if fill_w > 0:
            if self._state == "done":
                c0, c1 = QColor("#22c55e"), QColor("#1aa260")
            elif self._state == "error":
                c0, c1 = QColor("#ef4d6a"), QColor("#e23e5b")
            else:
                c0, c1 = QColor("#5b8bff"), QColor("#3b6ef6")
            grad = QLinearGradient(0, 0, fill_w, 0)
            grad.setColorAt(0.0, c0)
            grad.setColorAt(1.0, c1)
            p.setBrush(grad)
            p.drawRoundedRect(QRect(rect.left(), rect.top(), max(fill_w, h), h), r, r)

        # 完成/错误态：纯色满条，不画百分比（状态文字在下方 size_label 显示）
        if self._state in ("done", "error"):
            return

        # 居中百分比文字：颜色随填充区切换
        pct = int(frac * 100)
        p.setFont(QFont("Microsoft YaHei UI", 8, QFont.Weight.Bold))
        text = f"{pct}%"
        tw = p.fontMetrics().horizontalAdvance(text)
        tx = rect.left() + (w - tw) // 2
        # 文字若落在填充区上用白字，否则深字
        in_fill = (tx + tw // 2) < (rect.left() + fill_w) if fill_w > 0 else False
        p.setPen(QColor("#ffffff") if in_fill else QColor("#374151"))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)


class DownloadCard(QFrame):
    """下载队列中的单个条目：标题 + 进度条 + 状态 + 取消。"""

    def __init__(self, title: str, worker: DownloadWorker, parent=None, on_removed=None):
        super().__init__(parent)
        self.worker = worker
        self._on_removed_cb = on_removed
        self.setObjectName("Card")
        self.setMinimumHeight(96)
        self.setMaximumHeight(96)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetaVal")
        self.title_label.setStyleSheet("font-weight:600;color:#1f2330;font-size:13px;")
        self.title_label.setWordWrap(False)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("Danger")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self._on_cancel)
        top.addWidget(self.title_label, 1)
        top.addWidget(self.cancel_btn, 0)
        layout.addLayout(top)

        bot = QVBoxLayout()
        bot.setSpacing(0)
        self.progress = ProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        bot.addWidget(self.progress)
        bot.addSpacing(10)

        # 状态行：下载量  |  实时速度  |  剩余时间，清晰分列
        stat = QHBoxLayout()
        stat.setSpacing(12)
        self.size_label = QLabel("等待中…")
        self.size_label.setObjectName("Subtitle")
        self.size_label.setFixedHeight(16)
        self.speed_label = QLabel("")
        self.speed_label.setObjectName("Subtitle")
        self.speed_label.setStyleSheet("color:#3b6ef6;font-weight:600;")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_label.setFixedHeight(16)
        self.eta_label = QLabel("")
        self.eta_label.setObjectName("Subtitle")
        self.eta_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.eta_label.setFixedHeight(16)
        stat.addWidget(self.size_label, 1)
        stat.addWidget(self.speed_label, 1)
        stat.addWidget(self.eta_label, 1)
        bot.addLayout(stat)
        layout.addLayout(bot)

        # 不确定模式下的滚动动画
        self._busy_timer = QTimer(self)
        self._busy_timer.setInterval(60)
        self._busy_timer.timeout.connect(self.progress.update)

        worker.progress.connect(self._on_progress)
        worker.finished_ok.connect(self._on_done)
        worker.failed.connect(self._on_fail)

    def _set_busy(self, busy: bool):
        self.progress.set_busy(busy)
        if busy:
            self._busy_timer.start()
        else:
            self._busy_timer.stop()

    def _on_progress(self, d: dict):
        if d.get("status") == "finished":
            self._set_busy(False)
            self.progress.set_state("")
            self.size_label.setText("后期处理中（合并/转码）…")
            self.speed_label.setText("")
            self.eta_label.setText("")
            return
        downloaded = d.get("downloaded", 0)
        total = d.get("total", 0)
        speed = d.get("speed", 0)
        eta = d.get("eta")
        if total > 0:
            self._set_busy(False)
            pct = int(downloaded * 100 / total)
            self.progress.setValue(pct)
            self.size_label.setText(f"{human_size(downloaded)} / {human_size(total)}")
        else:
            self._set_busy(True)
            self.size_label.setText(f"已下载 {human_size(downloaded)}")
        self.speed_label.setText(human_speed(speed))
        self.eta_label.setText(f"剩余 {human_eta(eta)}" if eta else "")

    def _on_done(self, _title: str):
        self._set_busy(False)
        self.progress.setValue(100)
        self.progress.set_state("done")
        self.size_label.setText("已完成")
        self.speed_label.setText("")
        self.eta_label.setText("")
        self.cancel_btn.setText("完成")
        self.cancel_btn.setEnabled(False)

    def _on_fail(self, msg: str):
        self._set_busy(False)
        self.progress.set_state("error")
        self.speed_label.setText("")
        self.eta_label.setText("")
        short = msg if len(msg) < 80 else msg[:77] + "…"
        self.size_label.setText("失败: " + short)
        self.size_label.setToolTip(msg)
        self.cancel_btn.setText("移除")
        self.cancel_btn.setEnabled(True)
        try:
            self.cancel_btn.clicked.disconnect()
        except Exception:
            pass
        self.cancel_btn.clicked.connect(self._remove_self)

    def _on_cancel(self):
        self.worker.cancel()
        self.cancel_btn.setEnabled(False)
        self.size_label.setText("正在取消…")

    def _remove_self(self):
        self.setParent(None)
        self.deleteLater()
        if self._on_removed_cb:
            self._on_removed_cb()


class _ThumbWorker(QThread):
    """用 Python urllib 拉取缩略图，避免 frozen 环境 QtNetwork/SSL 崩溃。"""
    data_ready = pyqtSignal(bytes)
    failed = pyqtSignal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self._url = url

    def run(self):
        import urllib.request
        from downloader.debug import trace
        trace("thumb worker start")
        try:
            req = urllib.request.Request(
                self._url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            trace("thumb worker got %d bytes" % len(data))
            self.data_ready.emit(data)
        except Exception as e:
            trace("thumb worker failed: %s" % e)
            self.failed.emit(str(e))


class ThumbnailLoader(QLabel):
    """从 URL 异步加载缩略图（urllib 线程，非 QtNetwork）。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(230, 130)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("Card")
        self.setText("无封面")
        self.setStyleSheet("color:#b3b9c8;font-size:12px;background-color:#eef1f7;border-radius:12px;")
        self._worker: Optional[_ThumbWorker] = None

    def load(self, url: str):
        from downloader.debug import trace
        trace("thumb.load: " + (url[:60] if url else "(empty)"))
        self.clear()
        if not url:
            self.setText("无封面")
            return
        self.setText("加载封面…")
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(2000)
        self._worker = _ThumbWorker(url, self)
        self._worker.data_ready.connect(self._on_data)
        self._worker.failed.connect(lambda _m: self._on_fail())
        self._worker.start()

    def _on_data(self, data: bytes):
        from downloader.debug import trace
        trace("thumb _on_data %d bytes" % len(data))
        try:
            pix = QPixmap()
            if pix.loadFromData(data):
                self.setPixmap(
                    pix.scaled(
                        self.size(),
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                trace("thumb set OK")
            else:
                self.setText("无封面")
                trace("thumb loadFromData failed")
        except Exception:
            import traceback
            trace("thumb CRASH: " + traceback.format_exc())
            self.setText("无封面")

    def _on_fail(self):
        from downloader.debug import trace
        trace("thumb _on_fail")
        self.setText("无封面")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoDownloader")
        self.resize(1280, 800)
        self.setMinimumSize(1000, 660)

        self._extract_worker: Optional[ExtractWorker] = None
        self._current_info: Optional[VideoInfo] = None

        self._build_ui()
        self._set_default_output_dir()

        # 心跳：每 3 秒写 trace，app 崩溃时心跳停止，便于定位死亡时刻
        from downloader.debug import trace
        from PyQt6.QtCore import QTimer
        self._hb = QTimer(self)
        self._hb.timeout.connect(lambda: trace("heartbeat"))
        self._hb.start(3000)
        trace("MainWindow constructed")

    # ---------- UI 构建 ----------
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("Root")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.addWidget(self._build_left())
        splitter.addWidget(self._build_right())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([400, 880])
        self.left_panel.setMinimumWidth(340)
        self.left_panel.setMaximumWidth(520)
        root.addWidget(splitter, 1)

        sb = QStatusBar()
        self.setStatusBar(sb)
        self.statusBar().showMessage("就绪")

    # ---- 左控制栏 ----
    def _build_left(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("Root")
        self.left_panel = wrap
        outer = QVBoxLayout(wrap)
        outer.setContentsMargins(14, 14, 8, 14)
        outer.setSpacing(12)

        # URL 输入
        url_card = QFrame()
        url_card.setObjectName("Card")
        ul = QVBoxLayout(url_card)
        ul.setContentsMargins(14, 12, 14, 12)
        ul.setSpacing(8)
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("粘贴视频或播放列表链接…")
        self.url_edit.returnPressed.connect(self.extract)
        ul.addWidget(self.url_edit)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.parse_btn = QPushButton("解析")
        self.parse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.parse_btn.clicked.connect(self.extract)
        self.download_btn = QPushButton("下载")
        self.download_btn.setObjectName("Secondary")
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.start_download)
        btn_row.addWidget(self.parse_btn)
        btn_row.addWidget(self.download_btn)
        ul.addLayout(btn_row)
        outer.addWidget(url_card)

        # 下载选项卡
        outer.addWidget(self._build_options_card())

        # yt-dlp 更新条
        outer.addWidget(self._build_update_bar())

        # 下载队列（占满左栏剩余空间）
        outer.addWidget(self._build_queue(), 1)

        return wrap

    def _build_update_bar(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        # 第一行：yt-dlp 版本 + 检查更新
        r1 = QHBoxLayout()
        r1.setSpacing(8)
        info = QLabel(f"yt-dlp  v{get_current_version()}  ·  {get_active_source()}")
        info.setObjectName("Subtitle")
        info.setToolTip("点击「检查更新」从 GitHub 获取最新 yt-dlp；更新后需重启生效")
        self.ytdlp_ver_label = info
        r1.addWidget(info, 1)
        self.update_btn = QPushButton("检查更新")
        self.update_btn.setObjectName("Secondary")
        self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_btn.clicked.connect(self._check_ytdlp_update)
        r1.addWidget(self.update_btn)
        layout.addLayout(r1)

        # 第二行：软件版本 + 检查软件更新
        r2 = QHBoxLayout()
        r2.setSpacing(8)
        app_info = QLabel(f"软件  v{APP_VERSION}")
        app_info.setObjectName("Subtitle")
        app_info.setToolTip("点击「检查软件更新」从 GitHub 获取最新版本并自动升级（安装目录保持原位置）")
        self.app_ver_label = app_info
        r2.addWidget(app_info, 1)
        self.app_update_btn = QPushButton("检查软件更新")
        self.app_update_btn.setObjectName("Secondary")
        self.app_update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.app_update_btn.clicked.connect(self._check_app_update)
        r2.addWidget(self.app_update_btn)
        layout.addLayout(r2)
        return card

    def _build_options_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        header = QLabel("下载选项")
        header.setObjectName("Section")
        layout.addWidget(header)

        # 容器
        r1 = QHBoxLayout()
        r1.setSpacing(8)
        cl = QLabel("容器"); cl.setObjectName("MetaKey"); cl.setMinimumWidth(40)
        r1.addWidget(cl)
        self.container_combo = QComboBox()
        self.container_combo.addItems(["自动", "mp4", "webm", "mkv", "mov"])
        r1.addWidget(self.container_combo, 1)
        layout.addLayout(r1)

        # cookies
        r2 = QHBoxLayout()
        r2.setSpacing(8)
        kl = QLabel("Cookies"); kl.setObjectName("MetaKey"); kl.setMinimumWidth(40)
        r2.addWidget(kl)
        self.cookies_combo = QComboBox()
        self.cookies_combo.addItem("不使用", "")
        self.cookies_combo.addItem("Firefox", "firefox")
        self.cookies_combo.addItem("Chrome", "chrome")
        self.cookies_combo.addItem("Edge", "edge")
        self.cookies_combo.addItem("Brave", "brave")
        self.cookies_combo.setCurrentIndex(1)
        r2.addWidget(self.cookies_combo, 1)
        layout.addLayout(r2)

        # 保存目录
        r3 = QVBoxLayout()
        r3.setSpacing(4)
        sl = QLabel("保存到"); sl.setObjectName("MetaKey")
        r3.addWidget(sl)
        dir_row = QHBoxLayout()
        dir_row.setSpacing(6)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("选择输出目录…")
        browse_btn = QPushButton("浏览")
        browse_btn.setObjectName("Secondary")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse_output)
        open_btn = QPushButton("打开")
        open_btn.setObjectName("Secondary")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.clicked.connect(self._open_output_dir)
        dir_row.addWidget(self.output_edit, 1)
        dir_row.addWidget(browse_btn)
        dir_row.addWidget(open_btn)
        r3.addLayout(dir_row)
        layout.addLayout(r3)

        return card

    def _build_format_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        head = QHBoxLayout()
        head.setSpacing(10)
        header = QLabel("格式选择")
        header.setObjectName("Section")
        head.addWidget(header)
        head.addStretch()
        legend = QLabel("选 1 视频 + 1 音频自动合并，或选 1 合一直接下载 · 三组互斥 · ★ 推荐")
        legend.setObjectName("Hint")
        head.addWidget(legend)
        layout.addLayout(head)

        self.fmt_summary = QLabel("解析后在此显示可用格式")
        self.fmt_summary.setObjectName("MetaVal")
        self.fmt_summary.setStyleSheet("color:#6b7280;font-size:12px;padding:2px 2px;")
        layout.addWidget(self.fmt_summary)

        self.fmt_table = QTableWidget(0, 4)
        self.fmt_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.fmt_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.fmt_table.setAlternatingRowColors(True)
        self.fmt_table.verticalHeader().setVisible(False)
        self.fmt_table.verticalHeader().setDefaultSectionSize(32)
        self.fmt_table.setHorizontalHeaderLabels(
            ["✓", "分辨率", "编码", "码率 / 大小"]
        )
        hh = self.fmt_table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.fmt_table.setColumnWidth(0, 38)
        self.fmt_table.setColumnWidth(1, 150)
        self.fmt_table.setColumnWidth(2, 170)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        hh.setStretchLastSection(True)
        self.fmt_table.itemChanged.connect(self._on_format_item_changed)
        layout.addWidget(self.fmt_table, 1)

        self.fmt_empty_label = QLabel("解析视频后在此显示可用格式")
        self.fmt_empty_label.setObjectName("QueueEmpty")
        self.fmt_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fmt_empty_label.setVisible(False)
        layout.addWidget(self.fmt_empty_label)

        self._fmt_by_id: dict[str, FormatOption] = {}
        return card

    # ---- 右内容区 ----
    def _build_right(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("Root")
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(8, 14, 14, 14)
        layout.setSpacing(12)

        # 上：视频信息卡（固定高度，紧凑横向）
        layout.addWidget(self._build_info_card(), 0)

        # 下：格式选择表（占满剩余空间，主操作区）
        layout.addWidget(self._build_format_card(), 1)
        return wrap

    def _build_info_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        il = QVBoxLayout(card)
        il.setContentsMargins(16, 14, 16, 14)
        il.setSpacing(8)

        head = QHBoxLayout()
        head.setSpacing(14)
        self.thumb = ThumbnailLoader()
        head.addWidget(self.thumb)

        meta_col = QVBoxLayout()
        meta_col.setSpacing(4)
        self.title_label = QLabel("等待解析…")
        self.title_label.setObjectName("Title")
        self.title_label.setWordWrap(True)
        self.subtitle_label = QLabel("输入链接并点击「解析」获取视频信息")
        self.subtitle_label.setObjectName("Subtitle")
        self.subtitle_label.setWordWrap(True)
        meta_col.addWidget(self.title_label)
        meta_col.addWidget(self.subtitle_label)
        meta_col.addSpacing(4)

        self.meta_grid = QGridLayout()
        self.meta_grid.setHorizontalSpacing(14)
        self.meta_grid.setVerticalSpacing(4)
        self._meta_labels: dict[str, QLabel] = {}
        for i, key in enumerate(["时长", "观看", "点赞", "上传", "来源", "ID"]):
            kl = QLabel(key); kl.setObjectName("MetaKey")
            vl = QLabel("-"); vl.setObjectName("MetaVal")
            self.meta_grid.addWidget(kl, i // 3, (i % 3) * 2)
            self.meta_grid.addWidget(vl, i // 3, (i % 3) * 2 + 1)
            self._meta_labels[key] = vl
        meta_col.addLayout(self.meta_grid)
        head.addLayout(meta_col, 1)
        il.addLayout(head)
        return card

    def _build_queue(self) -> QWidget:
        wrap = QWidget()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        head = QHBoxLayout()
        sec = QLabel("下载队列"); sec.setObjectName("Section")
        head.addWidget(sec)
        head.addStretch()
        self.queue_count_label = QLabel("0 项")
        self.queue_count_label.setObjectName("Hint")
        head.addWidget(self.queue_count_label)
        layout.addLayout(head)

        self.queue_scroll = QScrollArea()
        self.queue_scroll.setWidgetResizable(True)
        inner = QWidget()
        self.queue_layout = QVBoxLayout(inner)
        self.queue_layout.setContentsMargins(0, 0, 6, 0)
        self.queue_layout.setSpacing(8)
        self.queue_empty_label = QLabel("暂无下载任务，解析视频后点击「下载」加入队列")
        self.queue_empty_label.setObjectName("QueueEmpty")
        self.queue_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.queue_empty_label.setMinimumHeight(50)
        self.queue_layout.addWidget(self.queue_empty_label)
        self.queue_layout.addStretch()
        self.queue_scroll.setWidget(inner)
        layout.addWidget(self.queue_scroll)
        return wrap

    # ---------- 行为 ----------
    def _set_default_output_dir(self):
        default = r"F:\download"
        try:
            os.makedirs(default, exist_ok=True)
        except Exception:
            from PyQt6.QtCore import QStandardPaths
            default = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DownloadLocation
            ) or os.path.expanduser("~")
        self.output_edit.setText(default)

    def _browse_output(self):
        d = QFileDialog.getExistingDirectory(self, "选择保存目录", self.output_edit.text() or "")
        if d:
            self.output_edit.setText(d)

    def _open_output_dir(self):
        d = self.output_edit.text().strip()
        if not d or not os.path.isdir(d):
            QMessageBox.information(self, "打开目录", "保存目录不存在，请先选择。")
            return
        try:
            os.startfile(d)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", str(e))

    def _cookies_source(self) -> str:
        return self.cookies_combo.currentData() or ""

    # ---------- 解析 ----------
    def extract(self):
        from downloader.debug import trace
        trace("extract() called")
        url = self.url_edit.text().strip()
        if not url:
            self.statusBar().showMessage("请输入链接")
            return
        if self._extract_worker and self._extract_worker.isRunning():
            self.statusBar().showMessage("正在解析中，请稍候…")
            return

        ensure_ffmpeg()
        self.parse_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.statusBar().showMessage("解析中…")
        self.title_label.setText("解析中…")
        self.subtitle_label.setText(url)

        self._extract_worker = ExtractWorker(url, self._cookies_source(), self)
        self._extract_worker.finished.connect(self._on_extracted)
        self._extract_worker.error.connect(self._on_extract_error)
        self._extract_worker.start()
        trace("ExtractWorker started")

    def _on_extracted(self, info: VideoInfo):
        from downloader.debug import trace
        trace("_on_extracted entered")
        try:
            self._on_extracted_impl(info)
            trace("_on_extracted done OK")
        except Exception:
            import traceback
            msg = "".join(traceback.format_exc())
            self._write_crash("EXTRACT CALLBACK\n" + msg)
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    0, "解析完成时出错，详见 crash.log：\n\n" + msg[:800],
                    "VideoDownloader", 0x10)
            except Exception:
                pass

    def _write_crash(self, msg):
        try:
            import os
            base = os.environ.get("APPDATA") or os.path.expanduser("~")
            p = os.path.join(base, "VideoDownloader", "crash.log")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(msg)
        except Exception:
            pass

    def _on_extracted_impl(self, info: VideoInfo):
        self.parse_btn.setEnabled(True)
        self._current_info = info

        self.title_label.setText(info.title)
        if info.is_playlist:
            self.subtitle_label.setText(
                f"播放列表 · 共 {info.playlist_count} 个条目 · {info.extractor}"
            )
        else:
            self.subtitle_label.setText(
                f"作者：{info.uploader or '-'}  ·  来源：{info.extractor or '-'}"
            )

        self._set_meta("时长", info.duration_str)
        self._set_meta("观看", info.view_str)
        self._set_meta("点赞", info.like_str)
        self._set_meta("上传", info.upload_date or "-")
        self._set_meta("来源", info.extractor or "-")
        self._set_meta("ID", info.video_id or "-")

        self.thumb.load(info.thumbnail)

        self._populate_format_table()

        self.download_btn.setEnabled(True)
        self.statusBar().showMessage(
            f"解析完成，可用格式 {len(info.formats)} 个" if not info.is_playlist
            else f"播放列表共 {info.playlist_count} 个视频，将批量下载"
        )

    def _on_extract_error(self, msg: str):
        from downloader.debug import trace
        trace("_on_extract_error: " + msg)
        self.parse_btn.setEnabled(True)
        self.download_btn.setEnabled(False)
        self.title_label.setText("解析失败")
        self.subtitle_label.setText(msg)
        self.statusBar().showMessage("解析失败")
        QMessageBox.warning(self, "解析失败", msg)

    def _set_meta(self, key: str, value: str):
        if key in self._meta_labels:
            self._meta_labels[key].setText(value)

    def _populate_format_table(self):
        info = self._current_info
        self.fmt_table.blockSignals(True)
        self.fmt_table.setRowCount(0)
        self._fmt_by_id = {}
        if not info or info.is_playlist:
            self.fmt_empty_label.setText("播放列表无单视频格式，将按最佳质量下载")
            self.fmt_empty_label.setVisible(True)
            self.fmt_summary.setText("播放列表：按最佳质量下载")
            self.fmt_table.blockSignals(False)
            return

        # 过滤掉非媒体格式（storyboard 等：既无视频又无音频）
        media_fmts = [f for f in info.formats if f.kind != "其它"]
        if not media_fmts:
            self.fmt_empty_label.setText("无可用媒体格式")
            self.fmt_empty_label.setVisible(True)
            self.fmt_summary.setText("无可用媒体格式")
            self.fmt_table.blockSignals(False)
            return
        self.fmt_empty_label.setVisible(False)

        # 分组：视频流在前（分辨率降序、码率降序），音频流次之（码率降序），合一流垫底
        videos = sorted(
            [f for f in media_fmts if f.kind == "视频"],
            key=lambda f: (-(f.height or 0), -(f.tbr or 0)),
        )
        audios = sorted(
            [f for f in media_fmts if f.kind == "音频"],
            key=lambda f: -(f.tbr or 0),
        )
        mixed = sorted(
            [f for f in media_fmts if f.kind == "音视频"],
            key=lambda f: (-(f.height or 0), -(f.tbr or 0)),
        )
        groups = [("视频流", videos), ("音频流", audios), ("合一流", mixed)]

        # 默认勾选：最佳纯视频 + 最佳纯音频；无分离流则最佳合一
        default_ids: set[str] = set()
        if videos and audios:
            default_ids = {videos[0].format_id, audios[0].format_id}
        elif mixed:
            default_ids = {mixed[0].format_id}

        kind_color = {"视频": "#3b6ef6", "音频": "#1aa260", "音视频": "#8b5cf6"}

        total_rows = sum(len(g[1]) for g in groups) + sum(1 for g in groups if g[1])
        self.fmt_table.setRowCount(total_rows)
        r = 0
        for group_name, fmts_in_group in groups:
            if not fmts_in_group:
                continue
            # 分组标题行：跨 4 列
            self._set_group_header_row(r, f"{group_name}  ·  {len(fmts_in_group)} 项")
            r += 1
            for f in fmts_in_group:
                self._fmt_by_id[f.format_id] = f
                recommended = f.format_id in default_ids

                chk = QTableWidgetItem()
                chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                chk.setCheckState(
                    Qt.CheckState.Checked if recommended else Qt.CheckState.Unchecked
                )
                chk.setData(Qt.ItemDataRole.UserRole, f.format_id)
                self.fmt_table.setItem(r, 0, chk)

                # 分辨率：推荐项加 ★ 前缀；高帧率(>30)追加 · Nfps
                res = f.resolution
                try:
                    fps_val = float(f.fps) if f.fps else 0
                except (TypeError, ValueError):
                    fps_val = 0
                if fps_val > 30:
                    res = f"{res} · {int(fps_val)}fps"
                res_item = QTableWidgetItem(("★ " if recommended else "   ") + res)
                res_item.setForeground(QColor(kind_color.get(f.kind, "#9aa1b1")))
                if recommended:
                    fnt = res_item.font()
                    fnt.setBold(True)
                    res_item.setFont(fnt)
                self.fmt_table.setItem(r, 1, res_item)

                # 编码：人话化
                if f.kind == "音频":
                    codec = _codec_label(f.acodec)
                elif f.kind == "视频":
                    codec = _codec_label(f.vcodec)
                else:
                    codec = f"{_codec_label(f.vcodec)} / {_codec_label(f.acodec)}"
                self.fmt_table.setItem(r, 2, QTableWidgetItem(codec))

                size = f.filesize_str or (f"{int(f.tbr)}k" if f.tbr else "—")
                self.fmt_table.setItem(r, 3, QTableWidgetItem(size))
                r += 1
        self.fmt_table.blockSignals(False)
        self._update_format_summary()
        from downloader.debug import trace
        trace("populate done, rows=%d selected=%s" % (self.fmt_table.rowCount(), self._selected_format_ids()))

    def _set_group_header_row(self, row: int, text: str):
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        fnt = item.font()
        fnt.setBold(True)
        item.setFont(fnt)
        item.setForeground(QColor("#6b7280"))
        item.setBackground(QColor("#eef1f7"))
        self.fmt_table.setItem(row, 0, item)
        self.fmt_table.setSpan(row, 0, 1, 4)
        self.fmt_table.setRowHeight(row, 26)

    def _selected_format_ids(self) -> list[str]:
        ids = []
        for r in range(self.fmt_table.rowCount()):
            item = self.fmt_table.item(r, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                fid = item.data(Qt.ItemDataRole.UserRole)
                if fid:
                    ids.append(str(fid))
        return ids

    def _on_format_item_changed(self, item):
        row = self.fmt_table.row(item)
        fid = item.data(Qt.ItemDataRole.UserRole)
        # 分组标题行无 format_id，忽略
        if not fid:
            return
        # 仅在「勾选」时执行互斥；取消勾选不动其他行
        if item.checkState() != Qt.CheckState.Checked:
            self._update_format_summary()
            return
        f = self._fmt_by_id.get(str(fid))
        if not f:
            return
        kind = f.kind
        self.fmt_table.blockSignals(True)
        for r in range(self.fmt_table.rowCount()):
            if r == row:
                continue
            it = self.fmt_table.item(r, 0)
            if not it or it.checkState() != Qt.CheckState.Checked:
                continue
            rid = it.data(Qt.ItemDataRole.UserRole)
            if not rid:
                continue  # 标题行
            rf = self._fmt_by_id.get(str(rid))
            if not rf:
                continue
            # 合一流与分离流互斥
            if kind == "音视频" or rf.kind == "音视频":
                it.setCheckState(Qt.CheckState.Unchecked)
            # 同类型至多一条：勾视频流取消其他视频流，勾音频流取消其他音频流
            elif rf.kind == kind:
                it.setCheckState(Qt.CheckState.Unchecked)
        self.fmt_table.blockSignals(False)
        self._update_format_summary()

    def _update_format_summary(self):
        ids = self._selected_format_ids()
        if not ids:
            self.fmt_summary.setText("未勾选任何格式，将按默认最佳质量下载")
            return
        parts = []
        for fid in ids:
            f = self._fmt_by_id.get(fid)
            if not f:
                continue
            if f.kind == "视频":
                parts.append(f"{f.resolution} 视频")
            elif f.kind == "音频":
                parts.append(f"{f.ext} 音频")
            else:
                parts.append(f"{f.resolution} 合一")
        merge = "  →  合并输出" if len(ids) > 1 else ""
        self.fmt_summary.setText("已选 " + "  +  ".join(parts) + merge)

    # ---------- 下载 ----------
    def _build_ydl_opts(self) -> dict:
        info = self._current_info
        out_dir = self.output_edit.text().strip() or os.path.expanduser("~")
        os.makedirs(out_dir, exist_ok=True)

        if info and info.is_playlist:
            fmt_str = "bv*+ba/b"
        else:
            fmt_str = build_format_from_ids(self._selected_format_ids())

        container = self.container_combo.currentText()
        opts = {
            "format": fmt_str,
            "outtmpl": {"default": os.path.join(out_dir, "%(title).100B [%(id)s].%(ext)s")},
            "concurrent_fragment_downloads": 4,
            "ignoreerrors": True,
        }
        merge = build_merge_output_format(container if container != "自动" else "")
        if merge:
            opts["merge_output_format"] = merge
        return opts

    def start_download(self):
        info = self._current_info
        if not info:
            self.statusBar().showMessage("请先解析视频")
            return
        out_dir = self.output_edit.text().strip()
        if not out_dir:
            QMessageBox.warning(self, "缺少目录", "请先选择保存目录")
            return

        if not self._ensure_ffmpeg_ready():
            return

        opts = self._build_ydl_opts()
        title = info.title
        if info.is_playlist:
            title = f"[列表 {info.playlist_count} 项] {title}"

        worker = DownloadWorker(
            info.webpage_url or self.url_edit.text().strip(),
            opts, title, self._cookies_source(), self,
        )
        card = DownloadCard(title, worker, on_removed=self._refresh_queue_count)
        self.queue_layout.insertWidget(self.queue_layout.count() - 1, card)
        self._refresh_queue_count()
        worker.start()
        self.statusBar().showMessage(f"已加入下载队列：{title}")

    def _refresh_queue_count(self):
        count = 0
        for i in range(self.queue_layout.count()):
            item = self.queue_layout.itemAt(i)
            if item and isinstance(item.widget(), DownloadCard):
                count += 1
        self.queue_count_label.setText(f"{count} 项")
        self.queue_empty_label.setVisible(count == 0)

    # ---------- yt-dlp 更新 ----------
    def _ensure_ffmpeg_ready(self) -> bool:
        """下载需要 ffmpeg 合并音视频。冻结模式下若未就绪，弹窗引导下载。"""
        if ensure_ffmpeg():
            return True
        reply = QMessageBox.question(
            self, "需要 ffmpeg",
            "合并视频+音频流需要 ffmpeg（约 90MB，仅首次）。\n是否现在下载到用户目录？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return False

        prog = QProgressDialog("正在下载 ffmpeg…", "取消", 0, 100, self)
        prog.setWindowTitle("ffmpeg 安装")
        prog.setMinimumDuration(0)
        prog.setAutoClose(False)
        prog.setModal(True)
        prog.setValue(0)

        worker = FFmpegSetupWorker(self)
        loop = __import__("PyQt6.QtCore", fromlist=["QEventLoop"]).QEventLoop(self)

        def on_progress(dl, total):
            if total > 0:
                prog.setRange(0, 100)
                prog.setValue(int(dl * 100 / total))
            else:
                prog.setRange(0, 0)

        def on_done():
            prog.close()
            loop.quit()

        def on_fail(msg):
            prog.close()
            loop.quit()
            QMessageBox.warning(self, "ffmpeg 下载失败", msg)

        worker.progress.connect(on_progress)
        worker.done.connect(on_done)
        worker.failed.connect(on_fail)
        prog.canceled.connect(worker.terminate)
        worker.start()
        loop.exec()
        return ensure_ffmpeg()

    def _check_ytdlp_update(self):
        if hasattr(self, "_upd_worker") and self._upd_worker and self._upd_worker.isRunning():
            return
        self.update_btn.setEnabled(False)
        self.update_btn.setText("检查中…")
        self.ytdlp_ver_label.setText(
            f"yt-dlp  v{get_current_version()}  ·  正在检查更新…"
        )
        self._upd_worker = UpdateWorker("check", self)
        self._upd_worker.check_done.connect(self._on_check_done)
        self._upd_worker.start()

    def _on_check_done(self, current: str, latest: str, needs: bool, tar_url: str):
        self.update_btn.setEnabled(True)
        if not latest:
            self.update_btn.setText("检查更新")
            self.ytdlp_ver_label.setText(f"yt-dlp  v{current}  ·  检查失败，请稍后重试")
            return
        if not needs:
            self.update_btn.setText("检查更新")
            self.ytdlp_ver_label.setText(f"yt-dlp  v{current}  ·  已是最新")
            return
        self.ytdlp_ver_label.setText(f"yt-dlp  v{current} → 可更新到 v{latest}")
        reply = QMessageBox.question(
            self, "发现新版本",
            f"当前 yt-dlp：v{current}\n最新版本：v{latest}\n\n是否下载并更新？\n（更新完成后需重启软件生效）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._do_ytdlp_update(tar_url)

    def _do_ytdlp_update(self, _tar_url: str):
        self.update_btn.setEnabled(False)
        self.update_btn.setText("更新中…")
        self._upd_worker = UpdateWorker("update", self)
        self._upd_worker.progress.connect(self._on_upd_progress)
        self._upd_worker.update_done.connect(self._on_upd_done)
        self._upd_worker.update_failed.connect(self._on_upd_failed)
        self._upd_worker.start()

    def _on_upd_progress(self, downloaded: int, total: int):
        if total > 0:
            pct = int(downloaded * 100 / total)
            self.ytdlp_ver_label.setText(
                f"下载更新中…  {human_size(downloaded)}/{human_size(total)}  {pct}%"
            )
        else:
            self.ytdlp_ver_label.setText(f"下载更新中…  {human_size(downloaded)}")

    def _on_upd_done(self, new_ver: str):
        self.update_btn.setEnabled(True)
        self.update_btn.setText("检查更新")
        self.ytdlp_ver_label.setText(f"yt-dlp 已更新到 v{new_ver}  ·  重启后生效")
        QMessageBox.information(
            self, "更新完成",
            f"yt-dlp 已更新到 v{new_ver}。\n请重启软件使新版本生效。",
        )

    def _on_upd_failed(self, msg: str):
        self.update_btn.setEnabled(True)
        self.update_btn.setText("检查更新")
        self.ytdlp_ver_label.setText(f"yt-dlp  v{get_current_version()}  ·  更新失败")
        QMessageBox.warning(self, "更新失败", msg)

    # ---------- 软件自身更新 ----------
    def _check_app_update(self):
        if getattr(self, "_app_upd_worker", None) and self._app_upd_worker.isRunning():
            return
        self.app_update_btn.setEnabled(False)
        self.app_update_btn.setText("检查中…")
        self.app_ver_label.setText(f"软件  v{APP_VERSION}  ·  正在检查更新…")
        self._app_upd_worker = AppUpdateWorker("check", self)
        self._app_upd_worker.check_done.connect(self._on_app_check_done)
        self._app_upd_worker.start()

    def _on_app_check_done(self, current: str, latest: str, needs: bool, setup_url: str):
        self.app_update_btn.setEnabled(True)
        self.app_update_btn.setText("检查软件更新")
        if not latest:
            self.app_ver_label.setText(f"软件  v{current}  ·  检查失败，请稍后重试")
            return
        if not needs:
            self.app_ver_label.setText(f"软件  v{current}  ·  已是最新")
            return
        self.app_ver_label.setText(f"软件  v{current} -> 可更新到 v{latest}")
        reply = QMessageBox.question(
            self, "发现新版本",
            f"当前软件：v{current}\n最新版本：v{latest}\n\n是否下载并自动安装？\n"
            "（将弹出 UAC 确认，安装完成后自动重启；安装目录保持原位置）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._do_app_update()

    def _do_app_update(self):
        self.app_update_btn.setEnabled(False)
        self.app_update_btn.setText("更新中…")
        self._app_upd_worker = AppUpdateWorker("update", self)
        self._app_upd_worker.progress.connect(self._on_app_upd_progress)
        self._app_upd_worker.done.connect(self._on_app_upd_done)
        self._app_upd_worker.failed.connect(self._on_app_upd_failed)
        self._app_upd_worker.start()

    def _on_app_upd_progress(self, downloaded: int, total: int):
        if total > 0:
            pct = int(downloaded * 100 / total)
            self.app_ver_label.setText(
                f"下载更新中…  {human_size(downloaded)}/{human_size(total)}  {pct}%"
            )
        else:
            self.app_ver_label.setText(f"下载更新中…  {human_size(downloaded)}")

    def _on_app_upd_done(self, installer_path: str):
        self.app_ver_label.setText("下载完成，正在启动安装程序…")
        QMessageBox.information(
            self, "即将安装更新",
            "更新已下载完成。\n点击确定后将弹出 UAC 确认，软件将关闭并自动安装新版本、重启。",
        )
        try:
            install_and_restart(installer_path)
        except Exception as e:
            self.app_update_btn.setEnabled(True)
            self.app_update_btn.setText("检查软件更新")
            self.app_ver_label.setText(f"软件  v{APP_VERSION}  ·  启动安装失败")
            QMessageBox.warning(self, "更新失败", str(e))

    def _on_app_upd_failed(self, msg: str):
        self.app_update_btn.setEnabled(True)
        self.app_update_btn.setText("检查软件更新")
        self.app_ver_label.setText(f"软件  v{APP_VERSION}  ·  更新失败")
        QMessageBox.warning(self, "更新失败", msg)

    def closeEvent(self, event):
        from downloader.debug import trace
        trace("closeEvent fired")
        running = 0
        for i in range(self.queue_layout.count()):
            item = self.queue_layout.itemAt(i)
            if item and isinstance(item.widget(), DownloadCard):
                if item.widget().worker.isRunning():
                    running += 1
        if running:
            reply = QMessageBox.question(
                self, "确认退出",
                f"有 {running} 个下载仍在进行，确定退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        self._shutdown_workers()
        event.accept()
        # setQuitOnLastWindowClosed(False) 时关窗不会退出事件循环，需显式 quit，
        # 否则进程残留（心跳定时器关窗后仍持续即证）
        QApplication.instance().quit()

    def _shutdown_workers(self):
        from downloader.debug import trace
        try:
            self._hb.stop()
        except Exception:
            pass
        workers = []
        for attr in ("_extract_worker", "_upd_worker", "_app_upd_worker"):
            w = getattr(self, attr, None)
            if w is not None:
                workers.append(w)
        thumb_loader = getattr(self, "thumb", None)
        if thumb_loader is not None and getattr(thumb_loader, "_worker", None) is not None:
            workers.append(thumb_loader._worker)
        for i in range(self.queue_layout.count()):
            item = self.queue_layout.itemAt(i)
            if item and isinstance(item.widget(), DownloadCard):
                workers.append(item.widget().worker)
        for w in workers:
            try:
                if hasattr(w, "cancel"):
                    w.cancel()
            except Exception:
                pass
            try:
                w.wait(1500)
            except Exception:
                pass
            if w.isRunning():
                try:
                    w.terminate()
                    w.wait(1000)
                except Exception:
                    pass
        trace("workers shut down")


def run():
    import sys
    import atexit
    from downloader.debug import trace
    ensure_ffmpeg()
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    app.setApplicationName("VideoDownloader")
    app.setWindowIcon(QIcon(_bundled_path("icon", "1.ico")))
    app.setQuitOnLastWindowClosed(False)  # 防止意外退出事件循环

    def _on_about_to_quit():
        trace("aboutToQuit —— 事件循环即将退出（正常退出路径）")

    app.aboutToQuit.connect(_on_about_to_quit)
    atexit.register(lambda: trace("atexit —— Python 进程正常退出"))

    win = MainWindow()
    win.show()
    trace("window shown, entering event loop")
    # --selftest URL: 自动解析指定链接，用于诊断打包后解析路径是否崩溃
    if len(sys.argv) >= 3 and sys.argv[1] == "--selftest":
        from PyQt6.QtCore import QTimer
        url = sys.argv[2]
        QTimer.singleShot(800, lambda: (win.url_edit.setText(url), win.extract()))
        # 解析完成或出错后 25s 自动退出，便于脚本捕获
        QTimer.singleShot(25000, app.quit)
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
