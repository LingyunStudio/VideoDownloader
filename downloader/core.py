"""yt-dlp 封装：元数据提取、格式解析、下载工作线程。

ffmpeg：开发模式用 static_ffmpeg 注入 PATH；打包后（只读目录）改为运行时下载到
%APPDATA%（见 downloader.ffmpeg_setup），再注入 PATH 并传 ffmpeg_location 给 yt-dlp。
"""
from __future__ import annotations

import os
import re
import sys
import threading
from dataclasses import dataclass, field
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

import yt_dlp

_ffmpeg_ready = False
_ffmpeg_location: Optional[str] = None
_ffmpeg_lock = threading.Lock()


def ensure_ffmpeg() -> bool:
    """确保 ffmpeg 可用。返回是否就绪。

    冻结模式：用 %APPDATA% 下已下载的 ffmpeg；未下载时返回 False（由 UI 触发下载）。
    开发模式：用 static_ffmpeg（conda 环境可写）。
    """
    global _ffmpeg_ready, _ffmpeg_location
    with _ffmpeg_lock:
        if _ffmpeg_ready:
            return True
        if getattr(sys, "frozen", False):
            from downloader.ffmpeg_setup import is_ready, ffmpeg_dir
            if is_ready():
                d = ffmpeg_dir()
                os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
                _ffmpeg_location = d
                _ffmpeg_ready = True
                return True
            return False
        try:
            import static_ffmpeg
            static_ffmpeg.add_paths()
            _ffmpeg_ready = True
            return True
        except Exception:
            return False


def ffmpeg_location() -> Optional[str]:
    """传给 yt-dlp 的 ffmpeg_location（目录），开发模式返回 None 走 PATH。"""
    return _ffmpeg_location


def human_size(num: float) -> str:
    if not num:
        return "?"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def human_speed(num: float) -> str:
    if not num:
        return "-"
    return human_size(num) + "/s"


def human_eta(eta: float) -> str:
    if eta is None:
        return "?"
    eta = int(eta)
    h, rem = divmod(eta, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def human_duration(sec: float) -> str:
    if not sec:
        return "?"
    return human_eta(sec)


@dataclass
class FormatOption:
    format_id: str
    ext: str = ""
    height: Optional[int] = None
    width: Optional[int] = None
    fps: Optional[float] = None
    vcodec: str = ""
    acodec: str = ""
    tbr: Optional[float] = None
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    note: str = ""
    has_video: bool = False
    has_audio: bool = False

    @property
    def resolution(self) -> str:
        if self.height and self.width:
            return f"{self.width}×{self.height}"
        if self.height:
            return f"{self.height}p"
        if self.width:
            return f"{self.width}×?"
        return "-"

    @property
    def kind(self) -> str:
        if self.has_video and self.has_audio:
            return "音视频"
        if self.has_video:
            return "视频"
        if self.has_audio:
            return "音频"
        return "其它"

    @property
    def filesize_str(self) -> str:
        sz = self.filesize or self.filesize_approx
        return human_size(sz) if sz else ""

    @property
    def label(self) -> str:
        parts = [self.resolution]
        if self.ext:
            parts.append(self.ext)
        if self.fps:
            parts.append(f"{int(self.fps)}fps")
        if self.tbr:
            parts.append(f"{int(self.tbr)}k")
        if self.note:
            parts.append(self.note)
        return " | ".join(parts)


@dataclass
class VideoInfo:
    title: str = ""
    uploader: str = ""
    duration: float = 0
    thumbnail: str = ""
    webpage_url: str = ""
    extractor: str = ""
    video_id: str = ""
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    upload_date: str = ""
    description: str = ""
    is_playlist: bool = False
    playlist_count: int = 0
    entries: list = field(default_factory=list)
    formats: list = field(default_factory=list)
    best_format_id: str = ""

    @property
    def duration_str(self) -> str:
        return human_duration(self.duration)

    @property
    def view_str(self) -> str:
        return f"{self.view_count:,}" if self.view_count else "-"

    @property
    def like_str(self) -> str:
        return f"{self.like_count:,}" if self.like_count else "-"


def parse_info(raw: dict) -> VideoInfo:
    """把 yt-dlp 的 info dict 转成 VideoInfo。"""
    info = VideoInfo(
        title=raw.get("title") or raw.get("id") or "(未知标题)",
        uploader=raw.get("uploader") or raw.get("channel") or "",
        duration=raw.get("duration") or 0,
        thumbnail=raw.get("thumbnail") or "",
        webpage_url=raw.get("webpage_url") or raw.get("original_url") or "",
        extractor=raw.get("extractor_key") or raw.get("extractor") or "",
        video_id=raw.get("id") or "",
        view_count=raw.get("view_count"),
        like_count=raw.get("like_count"),
        upload_date=raw.get("upload_date") or "",
        description=raw.get("description") or "",
    )

    entries = raw.get("entries")
    if entries is not None:
        info.is_playlist = True
        info.playlist_count = len(entries)
        return info

    fmts = []
    for f in raw.get("formats", []) or []:
        vcodec = f.get("vcodec") or ""
        acodec = f.get("acodec") or ""
        fmt = FormatOption(
            format_id=str(f.get("format_id") or ""),
            ext=f.get("ext") or "",
            height=f.get("height"),
            width=f.get("width"),
            fps=f.get("fps"),
            vcodec=vcodec,
            acodec=acodec,
            tbr=f.get("tbr") or f.get("abr") or f.get("vbr"),
            filesize=f.get("filesize"),
            filesize_approx=f.get("filesize_approx"),
            note=f.get("format_note") or "",
            has_video=vcodec != "none" and vcodec != "",
            has_audio=acodec != "none" and acodec != "",
        )
        fmts.append(fmt)
    info.formats = fmts
    info.best_format_id = str(raw.get("format_id") or "")
    return info


def distinct_heights(info: VideoInfo) -> list[int]:
    heights = sorted(
        {f.height for f in info.formats if f.has_video and f.height},
        reverse=True,
    )
    return heights


def build_format_string(
    quality: str,
    container: str,
    audio_only: bool,
    audio_format: str,
) -> tuple[str, list[dict]]:
    """根据 UI 选择构建 yt-dlp 的 format 字符串与 postprocessors。"""
    postprocessors = []

    if audio_only:
        fmt = "ba/b"
        if audio_format and audio_format != "best":
            fmt = f"ba[ext={audio_format}]/ba/b"
            postprocessors.append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": "0",
                }
            )
        return fmt, postprocessors

    if quality == "best" or not quality:
        fmt = "bv*+ba/b"
    else:
        h = quality
        fmt = (
            f"bv*[height<={h}]+ba/bv*[height<={h}]/b[height<={h}]/b"
        )

    return fmt, postprocessors


def build_format_from_ids(ids: list[str]) -> str:
    """根据用户勾选的 format_id 列表构建 yt-dlp format 字符串。

    多个 id 用 + 合并（需 ffmpeg）。空列表回退到最佳音视频。
    """
    ids = [i for i in ids if i]
    if not ids:
        return "bv*+ba/b"
    if len(ids) == 1:
        return ids[0]
    return "+".join(ids)


def build_merge_output_format(container: str) -> str:
    if container in ("mp4", "webm", "mkv", "mov", "avi", "flv"):
        return container
    return ""


class _CaptureLogger:
    """收集 yt-dlp 日志，便于把错误回传给 UI。"""

    def __init__(self):
        self.messages: list[str] = []

    def debug(self, msg):
        self.messages.append(str(msg))

    def info(self, msg):
        self.messages.append(str(msg))

    def warning(self, msg):
        self.messages.append("WARNING: " + str(msg))

    def error(self, msg):
        self.messages.append("ERROR: " + str(msg))


class ExtractWorker(QThread):
    """在工作线程中提取视频信息。"""

    finished = pyqtSignal(VideoInfo)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, url: str, cookies_source: str = "", parent=None):
        super().__init__(parent)
        self._url = url
        self._cookies_source = cookies_source
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        from downloader.debug import trace
        trace("ExtractWorker.run start, url=%s cookies=%s" % (self._url, self._cookies_source))
        ensure_ffmpeg()
        trace("ffmpeg ensured")
        logger = _CaptureLogger()
        opts = {
            "logger": logger,
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": False,
            "ignoreerrors": True,
            # 启用 node JS 运行时，YouTube 才会返回高清分离流（video-only / audio-only），
            # 否则只能拿到低分辨率的合一 progressive 流。
            "js_runtimes": {"node": {}, "deno": {}},
        }
        _apply_cookies(opts, self._cookies_source)
        try:
            trace("calling extract_info")
            with yt_dlp.YoutubeDL(opts) as ydl:
                raw = ydl.extract_info(self._url, download=False)
            trace("extract_info returned, raw is None=%s" % (raw is None))
            if self._cancelled:
                return
            if not raw:
                self.error.emit("未能提取到任何信息")
                return
            info = parse_info(ydl.sanitize_info(raw) if isinstance(raw, dict) else raw)
            trace("parse_info done, formats=%d" % len(info.formats))
            self.finished.emit(info)
            trace("finished emitted")
        except yt_dlp.utils.DownloadError as e:
            trace("DownloadError: %s" % e)
            if self._cancelled:
                return
            self.error.emit(str(e))
        except Exception as e:
            trace("Exception: %s: %s" % (type(e).__name__, e))
            if self._cancelled:
                return
            self.error.emit(f"{type(e).__name__}: {e}")


class DownloadCancelled(Exception):
    pass


def _apply_cookies(opts: dict, source: str) -> None:
    """把 cookies 来源写入 ydl_opts。

    source 为空则不处理；为浏览器名（chrome/firefox/edge/brave...）时用
    cookiesfrombrowser；以 .txt 结尾视为 Netscape cookies 文件路径。
    """
    if not source:
        return
    src = source.strip()
    if not src:
        return
    lower = src.lower()
    browsers = {"chrome", "firefox", "edge", "brave", "chromium", "opera", "vivaldi", "whale", "safari"}
    if lower in browsers:
        opts["cookiesfrombrowser"] = (lower,)
    elif lower.endswith(".txt") and os.path.isfile(src):
        opts["cookiefile"] = src


class DownloadWorker(QThread):
    """在工作线程中执行下载，通过信号上报进度。"""

    progress = pyqtSignal(dict)
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, url: str, ydl_opts: dict, title: str = "", cookies_source: str = "", parent=None):
        super().__init__(parent)
        self._url = url
        self._opts = ydl_opts
        self._title = title
        self._cookies_source = cookies_source
        self._cancelled = False
        self._ydl: Optional[yt_dlp.YoutubeDL] = None

    def cancel(self):
        self._cancelled = True

    def _hook(self, d):
        if self._cancelled:
            raise DownloadCancelled()
        if d.get("status") == "downloading":
            self.progress.emit(
                {
                    "status": "downloading",
                    "downloaded": d.get("downloaded_bytes") or 0,
                    "total": d.get("total_bytes")
                    or d.get("total_bytes_estimate")
                    or 0,
                    "speed": d.get("speed") or 0,
                    "eta": d.get("eta"),
                    "fragment": d.get("fragment_index"),
                    "fragment_count": d.get("fragment_count"),
                    "filename": d.get("filename") or "",
                }
            )
        elif d.get("status") == "finished":
            self.progress.emit(
                {
                    "status": "finished",
                    "filename": d.get("filename") or "",
                }
            )

    def run(self):
        ensure_ffmpeg()
        logger = _CaptureLogger()
        opts = dict(self._opts)
        opts.setdefault("logger", logger)
        opts.setdefault("quiet", True)
        opts.setdefault("no_warnings", True)
        opts.setdefault("ignoreerrors", True)
        opts.setdefault("retries", 5)
        opts.setdefault("js_runtimes", {"node": {}, "deno": {}})
        _loc = ffmpeg_location()
        if _loc:
            opts.setdefault("ffmpeg_location", _loc)
        opts["progress_hooks"] = [self._hook]
        _apply_cookies(opts, self._cookies_source)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                self._ydl = ydl
                ydl.download([self._url])
            if self._cancelled:
                self.failed.emit("已取消")
                return
            self.finished_ok.emit(self._title or self._url)
        except DownloadCancelled:
            self.failed.emit("已取消")
        except yt_dlp.utils.DownloadError as e:
            if self._cancelled:
                self.failed.emit("已取消")
                return
            tail = "\n".join(m for m in logger.messages if m.startswith("ERROR"))[-400:]
            self.failed.emit(tail or str(e))
        except Exception as e:
            if self._cancelled:
                self.failed.emit("已取消")
                return
            self.failed.emit(f"{type(e).__name__}: {e}")
