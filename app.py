import json
import os
import re
import tempfile
import urllib.request
import ctypes
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

import yt_dlp
from PyQt6.QtCore import QThread, Qt, QTimer, QUrl, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap, QTextCursor, QTextFormat
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QSlider,
    QSpinBox,
    QSplitter,
    QStyle,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
try:
    from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
    from PyQt6.QtMultimediaWidgets import QVideoWidget

    QT_MEDIA_AVAILABLE = True
except Exception:
    QAudioOutput = None
    QMediaPlayer = None
    QVideoWidget = None
    QT_MEDIA_AVAILABLE = False

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(APP_DIR, "downloader_settings.json")
APP_ICON_PATH = os.path.join(APP_DIR, "icon", "1.ico")
WINDOWS_APP_USER_MODEL_ID = "VideoDownloader.PyQt6"
YOUTUBE_PLAYER_CLIENT_ALLOWLIST = {
    "web",
    "web_safari",
    "web_embedded",
    "web_music",
    "web_creator",
    "mweb",
    "ios",
    "android",
    "android_vr",
    "tv",
    "tv_downgraded",
    "tv_simply",
    "default",
    "all",
}
YOUTUBE_SAFE_PLAYER_CLIENTS = ["android_vr", "ios", "tv"]
YOUTUBE_SAFE_PLAYER_CLIENTS_WITH_COOKIES = ["ios", "tv"]


if os.name == "nt":
    class _ACCENTPOLICY(ctypes.Structure):
        _fields_ = [
            ("AccentState", ctypes.c_uint),
            ("AccentFlags", ctypes.c_uint),
            ("GradientColor", ctypes.c_uint),
            ("AnimationId", ctypes.c_uint),
        ]


    class _WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
        _fields_ = [
            ("Attribute", ctypes.c_int),
            ("Data", ctypes.c_void_p),
            ("SizeOfData", ctypes.c_size_t),
        ]


def _enable_windows_glass_effect(window: QWidget) -> None:
    if os.name != "nt":
        return
    hwnd = int(window.winId())
    try:
        accent = _ACCENTPOLICY()
        accent.AccentState = 4  # ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 2
        accent.GradientColor = 0x0080FFFF
        accent.AnimationId = 0

        data = _WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.SizeOfData = ctypes.sizeof(accent)
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)

        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
    except Exception:
        return

    try:
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
            ctypes.sizeof(ctypes.c_int),
        )
    except Exception:
        pass

    try:
        DWMWA_CAPTION_COLOR = 35
        DWMWA_TEXT_COLOR = 36
        caption_color = ctypes.c_uint(0x00EEF3FA)
        text_color = ctypes.c_uint(0x0010151E)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_CAPTION_COLOR,
            ctypes.byref(caption_color),
            ctypes.sizeof(caption_color),
        )
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_TEXT_COLOR,
            ctypes.byref(text_color),
            ctypes.sizeof(text_color),
        )
    except Exception:
        pass


def _human_size(size: float | None) -> str:
    if not size:
        return "-"
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return "-"


def _human_duration(seconds: int | float | str | None) -> str:
    if seconds in (None, "", "-"):
        return "-"
    try:
        total = int(float(seconds))
    except Exception:
        return "-"
    if total <= 0:
        return "-"
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _pick_thumbnail_url(info: dict[str, Any]) -> str:
    raw = str(info.get("thumbnail") or "").strip()
    if raw:
        return raw
    thumbs = info.get("thumbnails") or []
    if isinstance(thumbs, list):
        for item in reversed(thumbs):
            if isinstance(item, dict):
                url = str(item.get("url") or "").strip()
                if url:
                    return url
    return ""


def _pick_preview_stream_url(info: dict[str, Any]) -> str:
    direct = str(info.get("url") or "").strip()
    if direct:
        return direct

    best_url = ""
    best_score = -1.0
    for fmt in (info.get("formats") or []):
        if not isinstance(fmt, dict):
            continue
        url = str(fmt.get("url") or "").strip()
        if not url:
            continue

        vcodec = str(fmt.get("vcodec") or "none")
        acodec = str(fmt.get("acodec") or "none")
        if vcodec == "none" or acodec == "none":
            continue

        ext = str(fmt.get("ext") or "").lower()
        protocol = str(fmt.get("protocol") or "").lower()
        height = int(fmt.get("height") or 0)
        tbr = float(fmt.get("tbr") or 0.0)

        score = float(height) + tbr * 0.1
        if ext == "mp4":
            score += 1500.0
        elif ext == "webm":
            score += 1100.0
        if "m3u8" in protocol:
            score += 80.0

        if score > best_score:
            best_score = score
            best_url = url

    if best_url:
        return best_url

    for fmt in (info.get("formats") or []):
        if isinstance(fmt, dict):
            url = str(fmt.get("url") or "").strip()
            if url:
                return url
    return ""


def _collect_preview_stream_candidates(formats: list[dict[str, Any]], limit: int = 24) -> list[tuple[str, str]]:
    ranked: list[tuple[float, str, str]] = []
    for fmt in formats:
        if not isinstance(fmt, dict):
            continue

        url = str(fmt.get("url") or "").strip()
        if not url:
            continue

        vcodec = str(fmt.get("vcodec") or "none").lower()
        acodec = str(fmt.get("acodec") or "none").lower()
        if vcodec == "none":
            continue

        ext = str(fmt.get("ext") or "").lower()
        if ext == "mhtml":
            continue
        protocol = str(fmt.get("protocol") or "").lower()
        fmt_id = str(fmt.get("format_id") or "").strip()
        try:
            height = int(float(fmt.get("height") or 0))
        except Exception:
            height = 0
        try:
            fps = int(float(fmt.get("fps") or 0))
        except Exception:
            fps = 0
        try:
            tbr = float(fmt.get("tbr") or 0.0)
        except Exception:
            tbr = 0.0

        has_audio = acodec != "none"

        # Prefer streams more likely to be decodable by Qt on Windows.
        score = float(height) * 2.0 + tbr * 0.05
        if has_audio:
            score += 1200.0
        else:
            score -= 260.0
        if ext == "mp4":
            score += 2500.0
        elif ext == "webm":
            score += 1800.0
        if "avc1" in vcodec or "h264" in vcodec:
            score += 800.0
        elif "vp9" in vcodec:
            score += 520.0
        elif "av01" in vcodec:
            score += 320.0
        if "mp4a" in acodec or "aac" in acodec:
            score += 500.0
        if protocol.startswith("http"):
            score += 220.0
        if "m3u8" in protocol:
            score += 140.0

        label_parts = []
        if height > 0:
            label_parts.append(f"{height}p")
        if fps > 0:
            label_parts.append(f"{fps}fps")
        label_parts.append(ext or "?")
        label_parts.append("\u542b\u97f3\u9891" if has_audio else "\u4ec5\u89c6\u9891")
        if fmt_id:
            label_parts.append(f"ID:{fmt_id}")
        label = " | ".join(label_parts)
        ranked.append((score, label, url))

    ranked.sort(key=lambda x: x[0], reverse=True)

    deduped: list[tuple[str, str]] = []
    seen_urls: set[str] = set()
    for _score, label, url in ranked:
        if url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append((label, url))
        if len(deduped) >= limit:
            break

    has_1080_or_below = False
    for label, _url in deduped:
        match = re.search(r"(\d{3,4})p", label.lower())
        if not match:
            continue
        try:
            h = int(match.group(1))
        except Exception:
            continue
        if 0 < h <= 1080:
            has_1080_or_below = True
            break
    if not has_1080_or_below:
        for _score, label, url in ranked:
            if url in seen_urls:
                continue
            match = re.search(r"(\d{3,4})p", label.lower())
            if not match:
                continue
            try:
                h = int(match.group(1))
            except Exception:
                continue
            if 0 < h <= 1080:
                deduped.append((label, url))
                break

    return deduped


def _candidate_label_height(label: str) -> int:
    match = re.search(r"(\d{3,4})p", label.lower())
    if not match:
        return 0
    try:
        return int(match.group(1))
    except Exception:
        return 0


def _candidate_has_audio(label: str) -> bool:
    return "\u542b\u97f3\u9891" in label and "\u4ec5\u89c6\u9891" not in label


def _pick_default_preview_stream_url(candidates: list[tuple[str, str]]) -> str:
    if not candidates:
        return ""

    items: list[tuple[int, int, str]] = []
    for label, url in candidates:
        h = _candidate_label_height(label)
        has_audio = 1 if _candidate_has_audio(label) else 0
        items.append((h, has_audio, url))

    at_or_below_1080_audio = [x for x in items if 0 < x[0] <= 1080 and x[1] == 1]
    if at_or_below_1080_audio:
        at_or_below_1080_audio.sort(key=lambda x: x[0], reverse=True)
        return at_or_below_1080_audio[0][2]

    at_or_below_1080 = [x for x in items if 0 < x[0] <= 1080]
    if at_or_below_1080:
        at_or_below_1080.sort(key=lambda x: x[0], reverse=True)
        return at_or_below_1080[0][2]

    above_1080_audio = [x for x in items if x[0] > 1080 and x[1] == 1]
    if above_1080_audio:
        above_1080_audio.sort(key=lambda x: x[0])
        return above_1080_audio[0][2]

    above_1080 = [x for x in items if x[0] > 1080]
    if above_1080:
        above_1080.sort(key=lambda x: x[0])
        return above_1080[0][2]

    with_audio = [x for x in items if x[1] == 1]
    if with_audio:
        return with_audio[0][2]

    return candidates[0][1]


def _is_manifest_like_audio_stream(protocol: str, url: str) -> bool:
    protocol_text = protocol.lower()
    url_text = url.lower()
    if "m3u8" in protocol_text or ".m3u8" in url_text:
        return True
    if "dash" in protocol_text or "dash" in url_text:
        return True
    if "manifest" in url_text and ("googlevideo.com" in url_text or "playlist" in url_text):
        return True
    return False


def _pick_preview_audio_stream_urls(formats: list[dict[str, Any]], limit: int = 6) -> list[str]:
    ranked: list[tuple[float, str]] = []
    for fmt in formats:
        if not isinstance(fmt, dict):
            continue
        url = str(fmt.get("url") or "").strip()
        if not url:
            continue

        acodec = str(fmt.get("acodec") or "none").lower()
        if acodec == "none":
            continue

        vcodec = str(fmt.get("vcodec") or "none").lower()
        if vcodec != "none" and acodec != "none":
            continue

        ext = str(fmt.get("ext") or "").lower()
        if ext == "mhtml":
            continue
        protocol = str(fmt.get("protocol") or "").lower()

        try:
            tbr = float(fmt.get("tbr") or 0.0)
        except Exception:
            tbr = 0.0
        try:
            asr = int(float(fmt.get("asr") or 0))
        except Exception:
            asr = 0

        is_manifest_like = _is_manifest_like_audio_stream(protocol, url)
        is_progressive_http = (
            protocol.startswith("http")
            and not is_manifest_like
            and "http_dash_segments" not in protocol
        )

        score = tbr * 1.2 + asr * 0.05
        if ext in {"m4a", "mp4"}:
            score += 900.0
        elif ext in {"webm", "opus"}:
            score += 700.0
        if "mp4a" in acodec or "aac" in acodec:
            score += 450.0
        if is_progressive_http:
            score += 1400.0
        elif protocol.startswith("http"):
            score += 420.0
        if is_manifest_like:
            score -= 1200.0
        if "mime=audio%2fmp4" in url.lower():
            score += 260.0

        ranked.append((score, url))

    ranked.sort(key=lambda x: x[0], reverse=True)
    deduped: list[str] = []
    seen_urls: set[str] = set()
    for _score, url in ranked:
        if url in seen_urls:
            continue
        seen_urls.add(url)
        deduped.append(url)
        if len(deduped) >= limit:
            break
    return deduped


def _pick_preview_audio_stream_url(formats: list[dict[str, Any]]) -> str:
    candidates = _pick_preview_audio_stream_urls(formats, limit=1)
    return candidates[0] if candidates else ""


def _to_float_percent(text: str | None) -> float:
    if not text:
        return 0.0
    match = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", "."))
    if not match:
        return 0.0
    return float(match.group(1))


def _read_json(path: str, default: dict[str, Any]) -> dict[str, Any]:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        return data if isinstance(data, dict) else default
    except Exception:
        return default


def _write_json(path: str, data: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)


def _is_cookie_db_copy_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "could not copy" in msg and "cookie database" in msg


def _is_impersonate_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "impersonate" in msg and (
        "curl_cffi" in msg or "not available" in msg or "unsupported" in msg
    )


def _is_http_403_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "403" in msg and ("forbidden" in msg or "fragment" in msg or "http error" in msg)


def _is_youtube_n_challenge_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(
        token in msg
        for token in [
            "n challenge",
            "nsig",
            "signature extraction failed",
            "challenge solver",
            "/wiki/ejs",
        ]
    )


def _is_youtube_format_unavailable_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "requested format is not available" in msg or "only images are available" in msg


def _has_downloadable_av_stream(formats: list[dict[str, Any]]) -> bool:
    for fmt in formats:
        if str(fmt.get("vcodec") or "none") != "none":
            return True
        if str(fmt.get("acodec") or "none") != "none":
            return True
    return False


def _opts_has_cookie_source(opts: dict[str, Any]) -> bool:
    return bool(opts.get("cookiesfrombrowser") or opts.get("cookiefile"))


def _drop_cookie_source(opts: dict[str, Any]) -> dict[str, Any]:
    next_opts = dict(opts)
    next_opts.pop("cookiesfrombrowser", None)
    next_opts.pop("cookiefile", None)
    return next_opts


def _youtube_safe_clients_for_opts(opts: dict[str, Any]) -> list[str]:
    if _opts_has_cookie_source(opts):
        return list(YOUTUBE_SAFE_PLAYER_CLIENTS_WITH_COOKIES)
    return list(YOUTUBE_SAFE_PLAYER_CLIENTS)


def _youtube_safe_clients_text(opts: dict[str, Any]) -> str:
    return ",".join(_youtube_safe_clients_for_opts(opts))


def _apply_youtube_safe_profile(opts: dict[str, Any]) -> None:
    extractor_args = dict(opts.get("extractor_args") or {})
    youtube_args = dict(extractor_args.get("youtube") or {})
    youtube_args["player_client"] = _youtube_safe_clients_for_opts(opts)
    extractor_args["youtube"] = youtube_args
    opts["extractor_args"] = extractor_args


def _should_enable_youtube_safe_profile(url: str, exc: Exception) -> bool:
    if not _is_youtube_url(url):
        return False
    return (
        _is_http_403_error(exc)
        or _is_youtube_n_challenge_error(exc)
        or _is_youtube_format_unavailable_error(exc)
    )


def _youtube_safe_profile_reason(exc: Exception) -> str:
    if _is_http_403_error(exc):
        return "YouTube 403"
    if _is_youtube_n_challenge_error(exc):
        return "YouTube n challenge"
    if _is_youtube_format_unavailable_error(exc):
        return "YouTube \u683c\u5f0f\u4e0d\u53ef\u7528"
    return "YouTube \u5f02\u5e38"


def _is_proxy_connect_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "proxyerror" in msg or "unable to connect to proxy" in msg


def _is_youtube_url(url: str) -> bool:
    lower = url.lower()
    return "youtube.com/" in lower or "youtu.be/" in lower


def _parse_youtube_player_clients(raw: str) -> tuple[list[str], list[str]]:
    clients: list[str] = []
    invalid: list[str] = []
    for token in [x.strip() for x in raw.split(",") if x.strip()]:
        base = token[1:] if token.startswith("-") else token
        if base in YOUTUBE_PLAYER_CLIENT_ALLOWLIST:
            clients.append(token)
        else:
            invalid.append(token)
    return clients, invalid


def _apply_cookie_source(opts: dict[str, Any], cookie_browser: str, cookie_file: str) -> None:
    if cookie_file and os.path.isfile(cookie_file):
        opts["cookiefile"] = cookie_file
        return
    if cookie_browser != "none":
        opts["cookiesfrombrowser"] = (cookie_browser,)


def _apply_anti_bot_source(opts: dict[str, Any], impersonate_client: str, youtube_player_client: str) -> None:
    if impersonate_client:
        opts["impersonate"] = impersonate_client

    clients, _invalid = _parse_youtube_player_clients(youtube_player_client)
    if clients:
        extractor_args = dict(opts.get("extractor_args") or {})
        youtube_args = dict(extractor_args.get("youtube") or {})
        youtube_args["player_client"] = clients
        extractor_args["youtube"] = youtube_args
        opts["extractor_args"] = extractor_args


def _run_with_runtime_fallback(
    opts: dict[str, Any],
    execute: Callable[[dict[str, Any]], Any],
    emit_log: Callable[[str], None],
    on_cookie_fallback: Callable[[], None] | None = None,
    on_impersonate_fallback: Callable[[], None] | None = None,
    on_proxy_fallback: Callable[[], None] | None = None,
) -> Any:
    current_opts = dict(opts)
    while True:
        try:
            return execute(current_opts)
        except DownloadCancelled:
            raise
        except Exception as exc:
            if _is_cookie_db_copy_error(exc) and "cookiesfrombrowser" in current_opts:
                if on_cookie_fallback:
                    on_cookie_fallback()
                emit_log(
                    "\u6d4f\u89c8\u5668 Cookie \u88ab\u5360\u7528\uff0c\u5df2\u81ea\u52a8\u6539\u4e3a\u4e0d\u4f7f\u7528\u6d4f\u89c8\u5668 Cookie \u91cd\u8bd5\uff1b"
                    "\u82e5\u9700\u8981\u767b\u5f55\u6001\uff0c\u8bf7\u914d\u7f6e cookies.txt"
                )
                next_opts = dict(current_opts)
                next_opts.pop("cookiesfrombrowser", None)
                current_opts = next_opts
                continue

            if _is_impersonate_error(exc) and "impersonate" in current_opts:
                if on_impersonate_fallback:
                    on_impersonate_fallback()
                emit_log(
                    "\u6d4f\u89c8\u5668\u6a21\u62df\uff08impersonate\uff09\u4e0d\u53ef\u7528\uff0c\u5df2\u81ea\u52a8\u5173\u95ed\u6a21\u62df\u91cd\u8bd5\u3002"
                    "\u82e5\u8981\u542f\u7528\u6a21\u62df\uff0c\u8bf7\u786e\u4fdd\u5b89\u88c5 curl_cffi\u3002"
                )
                next_opts = dict(current_opts)
                next_opts.pop("impersonate", None)
                current_opts = next_opts
                continue

            if _is_proxy_connect_error(exc) and current_opts.get("proxy"):
                if on_proxy_fallback:
                    on_proxy_fallback()
                emit_log("\u4ee3\u7406\u8fde\u63a5\u5931\u8d25\uff0c\u5df2\u81ea\u52a8\u5207\u6362\u4e3a\u76f4\u8fde\u91cd\u8bd5")
                next_opts = dict(current_opts)
                next_opts.pop("proxy", None)
                current_opts = next_opts
                continue

            raise


class DownloadCancelled(Exception):
    pass


class QtYdlLogger:
    def __init__(self, emit_log, should_abort: Callable[[], bool] | None = None):
        self._emit_log = emit_log
        self._should_abort = should_abort

    def _check_abort(self) -> None:
        if self._should_abort and self._should_abort():
            raise DownloadCancelled("\u7528\u6237\u5df2\u505c\u6b62\u4efb\u52a1")

    def debug(self, msg: str) -> None:
        self._check_abort()
        if msg.startswith("[debug] "):
            return
        self._emit_log(msg)

    def info(self, msg: str) -> None:
        self._check_abort()
        self._emit_log(msg)

    def warning(self, msg: str) -> None:
        self._check_abort()
        self._emit_log(f"[WARN] {msg}")

    def error(self, msg: str) -> None:
        self._check_abort()
        self._emit_log(f"[ERROR] {msg}")


class FetchInfoThread(QThread):
    log = pyqtSignal(str)
    info_ready = pyqtSignal(dict, list)
    failed = pyqtSignal(str)

    def __init__(
        self,
        url: str,
        cookie_browser: str,
        cookie_file: str,
        impersonate_client: str,
        youtube_player_client: str,
    ):
        super().__init__()
        self.url = url
        self.cookie_browser = cookie_browser
        self.cookie_file = cookie_file
        self.impersonate_client = impersonate_client
        self.youtube_player_client = youtube_player_client

    def run(self) -> None:
        try:
            self.log.emit("\u6b63\u5728\u89e3\u6790\u89c6\u9891\u4fe1\u606f...")
            opts: dict[str, Any] = {
                "quiet": True,
                "no_warnings": True,
                "logger": QtYdlLogger(self.log.emit),
            }
            _apply_cookie_source(opts, self.cookie_browser, self.cookie_file)
            _apply_anti_bot_source(opts, self.impersonate_client, self.youtube_player_client)

            def _do_extract(run_opts: dict[str, Any]) -> dict[str, Any]:
                with yt_dlp.YoutubeDL(run_opts) as ydl:
                    return ydl.extract_info(self.url, download=False)

            def _extract_with_safe_profile(base_opts: dict[str, Any], trigger_exc: Exception) -> dict[str, Any]:
                safe_opts = dict(base_opts)
                _apply_youtube_safe_profile(safe_opts)
                self.log.emit(
                    f"\u89e3\u6790\u89e6\u53d1{_youtube_safe_profile_reason(trigger_exc)}\uff0c"
                    f"\u5df2\u5207\u6362\u7a33\u5b9a\u6a21\u5f0f\u91cd\u8bd5\uff1aplayer_client={_youtube_safe_clients_text(safe_opts)}"
                )
                try:
                    return _run_with_runtime_fallback(safe_opts, _do_extract, self.log.emit)
                except Exception as safe_exc:
                    if _should_enable_youtube_safe_profile(self.url, safe_exc) and _opts_has_cookie_source(safe_opts):
                        no_cookie_opts = _drop_cookie_source(safe_opts)
                        _apply_youtube_safe_profile(no_cookie_opts)
                        self.log.emit(
                            "\u7a33\u5b9a\u6a21\u5f0f\u4ecd\u89e3\u6790\u5931\u8d25\uff0c"
                            f"\u5df2\u81ea\u52a8\u7981\u7528 Cookies \u518d\u8bd5\uff1aplayer_client={_youtube_safe_clients_text(no_cookie_opts)}"
                        )
                        return _run_with_runtime_fallback(no_cookie_opts, _do_extract, self.log.emit)
                    raise

            safe_retry_done = False
            try:
                info = _run_with_runtime_fallback(opts, _do_extract, self.log.emit)
            except Exception as exc:
                if _should_enable_youtube_safe_profile(self.url, exc):
                    safe_retry_done = True
                    info = _extract_with_safe_profile(opts, exc)
                else:
                    raise

            if _is_youtube_url(self.url):
                formats = info.get("formats") or []
                if not _has_downloadable_av_stream(formats) and not safe_retry_done:
                    retry_info = _extract_with_safe_profile(
                        opts, RuntimeError("Only images are available for download")
                    )
                    if _has_downloadable_av_stream(retry_info.get("formats") or []):
                        info = retry_info

            if info.get("_type") == "playlist":
                entries = [e for e in (info.get("entries") or []) if e]
                if not entries:
                    raise RuntimeError("\u64ad\u653e\u5217\u8868\u6ca1\u6709\u53ef\u4e0b\u8f7d\u6761\u76ee")
                info = entries[0]
                self.log.emit("\u68c0\u6d4b\u5230\u64ad\u653e\u5217\u8868\uff0c\u5c55\u793a\u7b2c\u4e00\u6761")

            compact = {
                "title": info.get("title") or "-",
                "uploader": info.get("uploader") or "-",
                "duration": info.get("duration"),
                "view_count": info.get("view_count"),
                "webpage_url": info.get("webpage_url") or self.url,
                "thumbnail_url": _pick_thumbnail_url(info),
                "preview_stream_url": _pick_preview_stream_url(info),
            }
            self.info_ready.emit(compact, info.get("formats") or [])
        except Exception as exc:
            self.failed.emit(str(exc))


@dataclass
class DownloadConfig:
    urls: list[str]
    output_dir: str
    output_template: str
    mode: str
    custom_format: str
    audio_codec: str
    video_container: str
    cookie_browser: str
    cookie_file: str
    impersonate_client: str
    youtube_player_client: str
    proxy: str
    ffmpeg_location: str
    allow_playlist: bool
    max_task_retries: int
    force_stable_for_youtube_custom: bool


class DownloadThread(QThread):
    log = pyqtSignal(str)
    progress = pyqtSignal(int, float, str, str)
    task_state = pyqtSignal(int, str, str)
    task_finished = pyqtSignal(dict)
    all_done = pyqtSignal(int, int)

    def __init__(self, config: DownloadConfig):
        super().__init__()
        self.config = config
        self._stop_requested = False
        self._current_task_index = -1
        self._skip_browser_cookies = False
        self._disable_cookie_file = False
        self._disable_impersonate = False
        self._use_youtube_safe_profile = False
        self._disable_proxy = False

    def stop(self) -> None:
        self._stop_requested = True

    def _build_opts(self) -> dict[str, Any]:
        opts: dict[str, Any] = {
            "paths": {"home": self.config.output_dir},
            "outtmpl": self.config.output_template,
            "noplaylist": not self.config.allow_playlist,
            "continuedl": True,
            "retries": 10,
            "fragment_retries": 10,
            "extractor_retries": 5,
            "file_access_retries": 5,
            "ignoreerrors": False,
            "no_warnings": True,
            "logger": QtYdlLogger(self.log.emit, lambda: self._stop_requested),
            "progress_hooks": [self._progress_hook],
        }

        if self.config.proxy and not self._disable_proxy:
            opts["proxy"] = self.config.proxy
        cookie_browser = "none" if self._skip_browser_cookies else self.config.cookie_browser
        cookie_file = "" if self._disable_cookie_file else self.config.cookie_file
        impersonate_client = "" if self._disable_impersonate else self.config.impersonate_client
        _apply_cookie_source(opts, cookie_browser, cookie_file)
        _apply_anti_bot_source(opts, impersonate_client, self.config.youtube_player_client)

        if self._use_youtube_safe_profile:
            # Stable fallback for YouTube anti-bot / format availability issues.
            _apply_youtube_safe_profile(opts)

        if self.config.ffmpeg_location:
            opts["ffmpeg_location"] = self.config.ffmpeg_location

        if self.config.mode == "video":
            opts["format"] = "bv*+ba/b"
            opts["merge_output_format"] = self.config.video_container
        elif self.config.mode == "audio":
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.config.audio_codec,
                    "preferredquality": "0",
                }
            ]
        else:
            if self.config.force_stable_for_youtube_custom:
                self.log.emit(
                    "\u68c0\u6d4b\u5230\u6240\u9009\u81ea\u5b9a\u4e49\u683c\u5f0f\u4e3a YouTube \u5206\u7247\u6d41\uff0c"
                    "\u5df2\u81ea\u52a8\u5207\u6362\u4e3a\u7a33\u5b9a\u4e0b\u8f7d\u6a21\u5f0f\uff08bv*+ba/b\uff09"
                )
                opts["format"] = "bv*+ba/b"
                opts["merge_output_format"] = self.config.video_container
                self._use_youtube_safe_profile = True
            else:
                opts["format"] = self.config.custom_format or "bv*+ba/b"

        if self._use_youtube_safe_profile and self.config.mode == "custom":
            opts["format"] = "bv*+ba/b"

        return opts

    def _download_once(self, url: str, opts: dict[str, Any]) -> int:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.download([url])

    def _download_with_runtime_fallback(self, url: str) -> int:
        def _run_download(run_opts: dict[str, Any]) -> int:
            return _run_with_runtime_fallback(
                run_opts,
                lambda x: self._download_once(url, x),
                self.log.emit,
                on_cookie_fallback=lambda: setattr(self, "_skip_browser_cookies", True),
                on_impersonate_fallback=lambda: setattr(self, "_disable_impersonate", True),
                on_proxy_fallback=lambda: setattr(self, "_disable_proxy", True),
            )

        opts = self._build_opts()
        try:
            return _run_download(opts)
        except Exception as exc:
            if _should_enable_youtube_safe_profile(url, exc) and not self._use_youtube_safe_profile:
                self._use_youtube_safe_profile = True
                safe_opts = self._build_opts()
                self.log.emit(
                    f"\u68c0\u6d4b\u5230{_youtube_safe_profile_reason(exc)}\uff0c"
                    "\u5df2\u5207\u6362\u7a33\u5b9a\u6a21\u5f0f\u91cd\u8bd5\uff1a"
                    f"player_client={_youtube_safe_clients_text(safe_opts)}\uff0c\u5e76\u5ffd\u7565\u9ad8\u98ce\u9669\u81ea\u5b9a\u4e49\u683c\u5f0f ID"
                )
                try:
                    return _run_download(safe_opts)
                except Exception as safe_exc:
                    if _should_enable_youtube_safe_profile(url, safe_exc) and _opts_has_cookie_source(safe_opts):
                        self._skip_browser_cookies = True
                        self._disable_cookie_file = True
                        no_cookie_opts = self._build_opts()
                        self.log.emit(
                            "\u7a33\u5b9a\u6a21\u5f0f\u4ecd\u4e0b\u8f7d\u5931\u8d25\uff0c"
                            f"\u5df2\u81ea\u52a8\u7981\u7528 Cookies \u518d\u8bd5\uff1aplayer_client={_youtube_safe_clients_text(no_cookie_opts)}"
                        )
                        return _run_download(no_cookie_opts)
                    raise
            raise

    def _progress_hook(self, data: dict[str, Any]) -> None:
        if self._stop_requested:
            raise DownloadCancelled("\u7528\u6237\u5df2\u505c\u6b62\u4efb\u52a1")

        status = data.get("status")
        if status == "downloading":
            percent = _to_float_percent(data.get("_percent_str"))
            speed = (data.get("_speed_str") or "").strip()
            eta = (data.get("_eta_str") or "").strip()
            self.progress.emit(self._current_task_index, percent, speed, eta)
        elif status == "finished":
            self.progress.emit(self._current_task_index, 100.0, "\u540e\u5904\u7406\u4e2d", "-")

    def run(self) -> None:
        ok_count = 0
        total = len(self.config.urls)
        max_attempts = self.config.max_task_retries + 1

        for idx, url in enumerate(self.config.urls):
            if self._stop_requested:
                self.task_state.emit(idx, "\u5df2\u53d6\u6d88", "\u961f\u5217\u5df2\u505c\u6b62")
                break

            self._current_task_index = idx
            success = False
            cancelled = False
            last_error = ""
            used_attempts = 0

            for attempt in range(1, max_attempts + 1):
                if self._stop_requested:
                    cancelled = True
                    break

                used_attempts = attempt
                self.task_state.emit(idx, "\u4e0b\u8f7d\u4e2d", f"\u7b2c {attempt}/{max_attempts} \u6b21")
                self.progress.emit(idx, 0.0, "-", "-")

                try:
                    code = self._download_with_runtime_fallback(url)
                    if code == 0:
                        success = True
                        break
                    last_error = f"yt-dlp return code: {code}"
                except DownloadCancelled as exc:
                    cancelled = True
                    last_error = str(exc)
                    break
                except Exception as exc:
                    last_error = str(exc)

                if attempt < max_attempts:
                    self.task_state.emit(idx, "\u91cd\u8bd5\u4e2d", f"\u5931\u8d25\uff0c\u51c6\u5907\u91cd\u8bd5\uff1a{last_error[:70]}")
                    self.log.emit(f"retry task {idx + 1}: {last_error}")

            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if success:
                ok_count += 1
                self.task_state.emit(idx, "\u5b8c\u6210", "\u4e0b\u8f7d\u6210\u529f")
                self.task_finished.emit({
                    "time": ts,
                    "url": url,
                    "mode": self.config.mode,
                    "success": True,
                    "message": "\u4e0b\u8f7d\u6210\u529f",
                    "output_dir": self.config.output_dir,
                    "attempts": used_attempts,
                })
            elif cancelled:
                self.task_state.emit(idx, "\u5df2\u53d6\u6d88", last_error or "\u7528\u6237\u505c\u6b62")
                self.task_finished.emit({
                    "time": ts,
                    "url": url,
                    "mode": self.config.mode,
                    "success": False,
                    "message": last_error or "\u7528\u6237\u505c\u6b62",
                    "output_dir": self.config.output_dir,
                    "attempts": used_attempts,
                })
                break
            else:
                self.task_state.emit(idx, "\u5931\u8d25", last_error[:120] if last_error else "\u672a\u77e5\u9519\u8bef")
                self.task_finished.emit({
                    "time": ts,
                    "url": url,
                    "mode": self.config.mode,
                    "success": False,
                    "message": last_error or "\u672a\u77e5\u9519\u8bef",
                    "output_dir": self.config.output_dir,
                    "attempts": used_attempts,
                })

        self.all_done.emit(ok_count, total)


if QT_MEDIA_AVAILABLE:
    class PreviewPlayerDialog(QDialog):
        def __init__(
            self,
            parent: QWidget,
            title: str,
            stream_url: str,
            page_url: str,
            stream_candidates: list[tuple[str, str]] | None = None,
            fallback_audio_url: str = "",
            fallback_audio_urls: list[str] | None = None,
        ) -> None:
            super().__init__(parent)
            self._page_url = page_url
            self._fallback_audio_url = fallback_audio_url.strip()
            self._fallback_audio_urls: list[str] = []
            for candidate_audio_url in list(fallback_audio_urls or []):
                clean_audio_url = str(candidate_audio_url or "").strip()
                if clean_audio_url and clean_audio_url not in self._fallback_audio_urls:
                    self._fallback_audio_urls.append(clean_audio_url)
            if self._fallback_audio_url and self._fallback_audio_url not in self._fallback_audio_urls:
                self._fallback_audio_urls.insert(0, self._fallback_audio_url)
            if self._fallback_audio_urls:
                self._fallback_audio_url = self._fallback_audio_urls[0]
            self._slider_dragging = False
            self._current_stream_url = ""
            self._current_quality_label = ""
            self._current_stream_has_audio = False
            self._using_external_audio = False
            self._muted = False
            self._current_label_has_audio_hint = False
            self._failed_stream_urls: set[str] = set()
            self._video_sink = None
            self._audio_local_retry_attempted = False
            self._cached_audio_file = ""
            self._current_audio_candidate_index = -1
            self._active_external_audio_url = ""
            self.setWindowTitle(f"\u89c6\u9891\u9884\u89c8 - {title}")
            self.resize(980, 620)

            root = QVBoxLayout(self)
            root.setContentsMargins(8, 8, 8, 8)
            root.setSpacing(8)

            self.video_widget = QVideoWidget(self)
            self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            self.video_widget.mousePressEvent = self._on_video_clicked
            try:
                sink = self.video_widget.videoSink()
            except Exception:
                sink = None
            if sink is not None:
                self._video_sink = sink
                sink.videoSizeChanged.connect(self._on_video_size_changed)
            root.addWidget(self.video_widget, 1)

            timeline = QHBoxLayout()
            self.current_time_label = QLabel("00:00")
            self.seek_slider = QSlider(Qt.Orientation.Horizontal)
            self.seek_slider.setRange(0, 0)
            self.total_time_label = QLabel("00:00")
            timeline.addWidget(self.current_time_label)
            timeline.addWidget(self.seek_slider, 1)
            timeline.addWidget(self.total_time_label)
            root.addLayout(timeline)

            controls = QHBoxLayout()
            self.back_btn = QPushButton("-10s")
            self.forward_btn = QPushButton("+10s")
            self.mute_btn = QPushButton("\u9759\u97f3")
            self.volume_slider = QSlider(Qt.Orientation.Horizontal)
            self.volume_slider.setRange(0, 100)
            self.volume_slider.setValue(85)
            self.quality_combo = QComboBox()
            self.rate_combo = QComboBox()
            self.rate_combo.addItems(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"])
            self.rate_combo.setCurrentText("1.0x")
            self.fullscreen_btn = QPushButton("\u5168\u5c4f")
            self.back_btn.clicked.connect(lambda: self._seek_relative(-10_000))
            self.forward_btn.clicked.connect(lambda: self._seek_relative(10_000))
            self.mute_btn.clicked.connect(self._toggle_mute)
            self.volume_slider.valueChanged.connect(self._on_volume_changed)
            self.quality_combo.currentIndexChanged.connect(self._on_quality_changed)
            self.rate_combo.currentTextChanged.connect(self._on_rate_changed)
            self.fullscreen_btn.clicked.connect(self._toggle_fullscreen)
            self.open_page_btn = QPushButton("\u5728\u6d4f\u89c8\u5668\u6253\u5f00")
            self.open_page_btn.clicked.connect(self._open_page)
            controls.addWidget(self.back_btn)
            controls.addWidget(self.forward_btn)
            controls.addWidget(self.mute_btn)
            controls.addWidget(QLabel("\u97f3\u91cf"))
            controls.addWidget(self.volume_slider)
            controls.addWidget(QLabel("\u6e05\u6670\u5ea6"))
            controls.addWidget(self.quality_combo)
            controls.addWidget(QLabel("\u500d\u901f"))
            controls.addWidget(self.rate_combo)
            controls.addWidget(self.fullscreen_btn)
            controls.addStretch(1)
            controls.addWidget(self.open_page_btn)
            root.addLayout(controls)

            self.status_label = QLabel("\u6b63\u5728\u52a0\u8f7d...")
            root.addWidget(self.status_label)

            self.player = QMediaPlayer(self)
            self.video_audio = QAudioOutput(self)
            self.video_audio.setVolume(0.85)
            self.player.setAudioOutput(self.video_audio)
            self.player.setVideoOutput(self.video_widget)

            self.audio_player = QMediaPlayer(self)
            self.audio = QAudioOutput(self)
            self.audio.setVolume(0.85)
            self.audio_player.setAudioOutput(self.audio)

            self.player.playbackStateChanged.connect(self._on_playback_state_changed)
            self.player.positionChanged.connect(self._on_position_changed)
            self.player.durationChanged.connect(self._on_duration_changed)
            self.player.mediaStatusChanged.connect(self._on_media_status_changed)
            self.player.errorOccurred.connect(self._on_player_error)
            self.audio_player.errorOccurred.connect(self._on_audio_player_error)
            self.audio_player.mediaStatusChanged.connect(self._on_audio_media_status_changed)

            self.seek_slider.sliderPressed.connect(self._on_seek_pressed)
            self.seek_slider.sliderReleased.connect(self._on_seek_released)
            self.seek_slider.sliderMoved.connect(self._on_seek_moved)

            candidates = list(stream_candidates or [])
            if stream_url and all(url != stream_url for _label, url in candidates):
                candidates.insert(0, ("\u63a8\u8350", stream_url))
            if not candidates and stream_url:
                candidates = [("\u9ed8\u8ba4", stream_url)]
            self.quality_combo.blockSignals(True)
            self.quality_combo.clear()
            for label, url in candidates:
                self.quality_combo.addItem(label, url)
            preferred_idx = self._pick_default_quality_index()
            if preferred_idx >= 0:
                self.quality_combo.setCurrentIndex(preferred_idx)
            elif stream_url:
                selected_idx = self.quality_combo.findData(stream_url)
                if selected_idx >= 0:
                    self.quality_combo.setCurrentIndex(selected_idx)
            self.quality_combo.setEnabled(self.quality_combo.count() > 1)
            self.quality_combo.blockSignals(False)
            if self.quality_combo.count() > 0:
                self._load_stream(
                    str(self.quality_combo.currentData() or ""),
                    self.quality_combo.currentText(),
                )
            elif stream_url:
                self._load_stream(stream_url, "\u9ed8\u8ba4")

        @staticmethod
        def _format_ms(ms: int) -> str:
            if ms <= 0:
                return "00:00"
            secs = ms // 1000
            h = secs // 3600
            m = (secs % 3600) // 60
            s = secs % 60
            if h > 0:
                return f"{h:02d}:{m:02d}:{s:02d}"
            return f"{m:02d}:{s:02d}"

        def _toggle_playback(self) -> None:
            if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.player.pause()
                if self._using_external_audio:
                    self.audio_player.pause()
            else:
                self.player.play()
                if self._using_external_audio:
                    self.audio_player.play()

        def _on_video_clicked(self, event) -> None:  # type: ignore[override]
            if hasattr(event, "button") and event.button() == Qt.MouseButton.LeftButton:
                self._toggle_playback()
                event.accept()
                return
            if hasattr(event, "ignore"):
                event.ignore()

        def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
            if state == QMediaPlayer.PlaybackState.PlayingState:
                if self._using_external_audio and self.audio_player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                    self.audio_player.play()
                self.status_label.setText(
                    "\u64ad\u653e\u4e2d\uff08\u70b9\u51fb\u753b\u9762\u53ef\u6682\u505c\uff09" + self._quality_tip()
                )
            elif state == QMediaPlayer.PlaybackState.PausedState:
                if self._using_external_audio and self.audio_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                    self.audio_player.pause()
                self.status_label.setText(
                    "\u5df2\u6682\u505c\uff08\u70b9\u51fb\u753b\u9762\u53ef\u7ee7\u7eed\uff09" + self._quality_tip()
                )

        def _on_position_changed(self, pos: int) -> None:
            if not self._slider_dragging:
                self.seek_slider.setValue(pos)
            self._sync_audio_position(pos)
            self.current_time_label.setText(self._format_ms(pos))

        def _on_duration_changed(self, duration: int) -> None:
            self.seek_slider.setRange(0, max(0, duration))
            self.total_time_label.setText(self._format_ms(duration))

        def _on_seek_pressed(self) -> None:
            self._slider_dragging = True

        def _on_seek_released(self) -> None:
            self._slider_dragging = False
            target = self.seek_slider.value()
            self.player.setPosition(target)
            if self._using_external_audio:
                self.audio_player.setPosition(target)

        def _on_seek_moved(self, value: int) -> None:
            self.current_time_label.setText(self._format_ms(value))

        def _seek_relative(self, delta_ms: int) -> None:
            target = max(0, self.player.position() + delta_ms)
            duration = self.player.duration()
            if duration > 0:
                target = min(target, duration)
            self.player.setPosition(target)
            if self._using_external_audio:
                self.audio_player.setPosition(target)

        def _on_volume_changed(self, value: int) -> None:
            vol = max(0.0, min(1.0, value / 100.0))
            self.video_audio.setVolume(vol)
            self.audio.setVolume(vol)

        def _toggle_mute(self) -> None:
            muted = not self._muted
            self._muted = muted
            self.video_audio.setMuted(muted or self._using_external_audio)
            self.audio.setMuted(muted)
            self.mute_btn.setText("\u53d6\u6d88\u9759\u97f3" if muted else "\u9759\u97f3")

        def _on_rate_changed(self, text: str) -> None:
            try:
                rate = float(text.replace("x", "").strip())
            except Exception:
                rate = 1.0
            self.player.setPlaybackRate(rate)
            if self._using_external_audio:
                self.audio_player.setPlaybackRate(rate)

        def _on_quality_changed(self, _index: int) -> None:
            next_url = str(self.quality_combo.currentData() or "").strip()
            if not next_url or next_url == self._current_stream_url:
                return
            self._load_stream(next_url, self.quality_combo.currentText())

        def _try_start_external_audio(self, start_index: int = 0) -> bool:
            if not self._fallback_audio_urls:
                return False
            safe_start = max(0, start_index)
            for idx in range(safe_start, len(self._fallback_audio_urls)):
                audio_url = str(self._fallback_audio_urls[idx] or "").strip()
                if not audio_url:
                    continue
                self._current_audio_candidate_index = idx
                self._active_external_audio_url = audio_url
                self._fallback_audio_url = audio_url
                self._audio_local_retry_attempted = False
                self.audio_player.stop()
                self.audio_player.setSource(QUrl(audio_url))
                self.audio_player.setPlaybackRate(self.player.playbackRate())
                self.audio_player.play()
                self._using_external_audio = True
                QTimer.singleShot(2200, self._check_external_audio_health)
                return True
            self._current_audio_candidate_index = -1
            self._active_external_audio_url = ""
            return False

        def _load_stream(self, url: str, label: str = "") -> None:
            next_url = url.strip()
            if not next_url:
                return
            self._current_stream_url = next_url
            self._current_quality_label = label or self._current_quality_label
            self._current_label_has_audio_hint = ("\u542b\u97f3\u9891" in self._current_quality_label) or ("\u4ec5\u89c6\u9891" in self._current_quality_label)
            self._current_stream_has_audio = _candidate_has_audio(self._current_quality_label)
            self._using_external_audio = False
            self._current_audio_candidate_index = -1
            self._active_external_audio_url = ""
            self.player.stop()
            self.player.setSource(QUrl(next_url))

            if self._current_stream_has_audio:
                self.video_audio.setMuted(self._muted)
                self.audio_player.stop()
            else:
                self.video_audio.setMuted(True)
                if self._fallback_audio_urls and self._try_start_external_audio(0):
                    pass
                else:
                    self.audio_player.stop()
                    audio_idx = self._find_audio_capable_quality_index()
                    if audio_idx >= 0 and audio_idx != self.quality_combo.currentIndex():
                        self.quality_combo.setCurrentIndex(audio_idx)
                        return
                    # Keep the main-stream audio path available in case label metadata is inaccurate.
                    self.video_audio.setMuted(self._muted)

            self.player.play()
            if self._using_external_audio:
                self.audio_player.setPosition(self.player.position())
            self.status_label.setText("\u6b63\u5728\u52a0\u8f7d..." + self._quality_tip())

        def _quality_tip(self) -> str:
            if self._current_stream_has_audio:
                return ""
            if self._using_external_audio:
                return "\uff08\u5f53\u524d\u4e3a\u5206\u79bb\u89c6\u9891\uff0c\u5df2\u81ea\u52a8\u52a0\u8f7d\u97f3\u9891\uff09"
            return "\uff08\u5f53\u524d\u4e3a\u4ec5\u89c6\u9891\uff0c\u4e14\u672a\u627e\u5230\u53ef\u7528\u97f3\u9891\uff09"

        def _sync_audio_position(self, pos: int) -> None:
            if not self._using_external_audio:
                return
            diff = abs(self.audio_player.position() - pos)
            if diff > 650:
                self.audio_player.setPosition(pos)

        def _check_external_audio_health(self) -> None:
            if not self._using_external_audio:
                return
            if self.player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                return
            if self.player.position() < 1000:
                QTimer.singleShot(1200, self._check_external_audio_health)
                return
            audio_stuck = (
                self.audio_player.playbackState() != QMediaPlayer.PlaybackState.PlayingState
                or self.audio_player.position() <= 0
            )
            if audio_stuck:
                self._on_audio_player_error()

        def _pick_default_quality_index(self) -> int:
            if self.quality_combo.count() <= 0:
                return -1
            candidates: list[tuple[str, str]] = []
            for i in range(self.quality_combo.count()):
                label = self.quality_combo.itemText(i)
                url = str(self.quality_combo.itemData(i) or "").strip()
                if url:
                    candidates.append((label, url))
            chosen_url = _pick_default_preview_stream_url(candidates)
            if not chosen_url:
                return 0
            idx = self.quality_combo.findData(chosen_url)
            return idx if idx >= 0 else 0

        def _find_audio_capable_quality_index(self) -> int:
            if self.quality_combo.count() <= 0:
                return -1
            best_idx = -1
            best_bucket = 99
            best_height = -1
            for i in range(self.quality_combo.count()):
                label = self.quality_combo.itemText(i)
                if not _candidate_has_audio(label):
                    continue
                h = _candidate_label_height(label)
                if 0 < h <= 1080:
                    bucket = 0
                elif h > 1080:
                    bucket = 1
                else:
                    bucket = 2
                if bucket < best_bucket:
                    best_bucket = bucket
                    best_height = h
                    best_idx = i
                    continue
                if bucket == best_bucket and h > best_height:
                    best_height = h
                    best_idx = i
            return best_idx

        def _on_video_size_changed(self, size: QSize | None = None) -> None:
            try:
                if size is None or size.width() <= 0 or size.height() <= 0:
                    if self._video_sink is not None:
                        size = self._video_sink.videoSize()
            except Exception:
                return
            if size is None:
                return
            if size.width() <= 0 or size.height() <= 0:
                return
            self._fit_dialog_to_video(size)

        def _fit_dialog_to_video(self, size: QSize) -> None:
            ratio = float(size.width()) / float(size.height())
            if ratio <= 0:
                return

            screen = self.screen() or QApplication.primaryScreen()
            if not screen:
                return
            available = screen.availableGeometry()
            max_w = min(available.width(), max(760, int(available.width() * 0.9)))
            max_h = min(available.height(), max(560, int(available.height() * 0.9)))

            chrome_h = max(180, self.height() - max(1, self.video_widget.height()))
            available_video_h = max(240, max_h - chrome_h)

            # Fit the video area into available bounds using the real aspect ratio.
            if max_w / ratio <= available_video_h:
                target_video_w = max_w
                target_video_h = int(target_video_w / ratio)
            else:
                target_video_h = available_video_h
                target_video_w = int(target_video_h * ratio)

            target_w = max(460, min(target_video_w, max_w))
            target_h = max(420, min(target_video_h + chrome_h, max_h))

            if abs(self.width() - target_w) < 6 and abs(self.height() - target_h) < 6:
                return
            self.resize(target_w, target_h)
            frame = self.frameGeometry()
            frame.moveCenter(available.center())
            self.move(frame.topLeft())

        def _toggle_fullscreen(self) -> None:
            self.video_widget.setFullScreen(not self.video_widget.isFullScreen())
            self.fullscreen_btn.setText("\u9000\u51fa\u5168\u5c4f" if self.video_widget.isFullScreen() else "\u5168\u5c4f")

        def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
            mapping = {
                QMediaPlayer.MediaStatus.LoadingMedia: "\u6b63\u5728\u52a0\u8f7d...",
                QMediaPlayer.MediaStatus.BufferingMedia: "\u6b63\u5728\u7f13\u51b2...",
                QMediaPlayer.MediaStatus.BufferedMedia: "\u5df2\u5c31\u7eea",
                QMediaPlayer.MediaStatus.EndOfMedia: "\u5df2\u64ad\u653e\u5b8c\u6bd5",
                QMediaPlayer.MediaStatus.InvalidMedia: "\u5a92\u4f53\u65e0\u6548\u6216\u4e0d\u53ef\u64ad\u653e",
            }
            self.status_label.setText(mapping.get(status, self.status_label.text()) + self._quality_tip())
            if status == QMediaPlayer.MediaStatus.InvalidMedia:
                self._try_switch_to_next_stream("\u5f53\u524d\u6e05\u6670\u5ea6\u4e0d\u53ef\u64ad\u653e")

        def _on_player_error(self, *_args) -> None:
            self._try_switch_to_next_stream("\u64ad\u653e\u51fa\u9519\uff0c\u6b63\u5728\u5c1d\u8bd5\u5176\u4ed6\u6e05\u6670\u5ea6")

        def _on_audio_player_error(self, *_args) -> None:
            if not self._using_external_audio:
                return
            failed_audio_url = str(self._active_external_audio_url or self._fallback_audio_url or "").strip()
            current_audio_idx = self._current_audio_candidate_index
            self.audio_player.stop()
            self._using_external_audio = False
            next_audio_idx = current_audio_idx + 1
            if next_audio_idx >= 0 and self._try_start_external_audio(next_audio_idx):
                self.status_label.setText("\u5f53\u524d\u97f3\u8f68\u52a0\u8f7d\u5931\u8d25\uff0c\u5df2\u81ea\u52a8\u5c1d\u8bd5\u5907\u7528\u97f3\u8f68")
                return
            if (
                not self._audio_local_retry_attempted
                and failed_audio_url.startswith("http")
            ):
                self._audio_local_retry_attempted = True
                local_audio = self._cache_external_audio_to_temp(failed_audio_url)
                if local_audio:
                    self._cached_audio_file = local_audio
                    self._current_audio_candidate_index = len(self._fallback_audio_urls)
                    self._active_external_audio_url = local_audio
                    self._fallback_audio_url = local_audio
                    self.audio_player.setSource(QUrl(local_audio))
                    self.audio_player.setPlaybackRate(self.player.playbackRate())
                    self.audio_player.play()
                    self._using_external_audio = True
                    QTimer.singleShot(2200, self._check_external_audio_health)
                    self.status_label.setText("\u8fdc\u7a0b\u97f3\u9891\u53d7\u9650\uff0c\u5df2\u5207\u6362\u672c\u5730\u7f13\u5b58\u97f3\u9891\u91cd\u8bd5")
                    return
            self.status_label.setText("\u97f3\u9891\u52a0\u8f7d\u5931\u8d25\uff0c\u5df2\u5c1d\u8bd5\u5207\u6362\u5230\u542b\u97f3\u9891\u6e05\u6670\u5ea6")
            audio_idx = self._find_audio_capable_quality_index()
            if audio_idx >= 0 and audio_idx != self.quality_combo.currentIndex():
                self.quality_combo.setCurrentIndex(audio_idx)
                return
            self.video_audio.setMuted(self._muted)

        def _on_audio_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
            if status == QMediaPlayer.MediaStatus.InvalidMedia:
                self._on_audio_player_error()

        def _cache_external_audio_to_temp(self, source_url: str = "") -> str:
            target_url = str(source_url or self._fallback_audio_url or "").strip()
            if not target_url or not target_url.startswith("http"):
                return ""
            suffix = ".m4a"
            lower = target_url.lower()
            if ".webm" in lower:
                suffix = ".webm"
            elif ".mp3" in lower:
                suffix = ".mp3"
            try:
                req = urllib.request.Request(
                    target_url,
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Referer": self._page_url,
                    },
                )
                with urllib.request.urlopen(req, timeout=18) as resp:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        while True:
                            chunk = resp.read(262144)
                            if not chunk:
                                break
                            tmp.write(chunk)
                        return tmp.name
            except Exception:
                return ""

        def _try_switch_to_next_stream(self, reason: str) -> None:
            current = self._current_stream_url.strip()
            if not current:
                return
            self._failed_stream_urls.add(current)
            start = self.quality_combo.currentIndex()
            if start < 0:
                start = 0
            for i in range(start + 1, self.quality_combo.count()):
                candidate_url = str(self.quality_combo.itemData(i) or "").strip()
                if not candidate_url or candidate_url in self._failed_stream_urls:
                    continue
                self.status_label.setText(f"{reason}\uff0c\u5df2\u81ea\u52a8\u5207\u6362\u5230\uff1a{self.quality_combo.itemText(i)}")
                self.quality_combo.setCurrentIndex(i)
                return

        def _open_page(self) -> None:
            if self._page_url:
                os.startfile(self._page_url)

        def closeEvent(self, event) -> None:  # type: ignore[override]
            try:
                self.video_widget.setFullScreen(False)
                self.player.stop()
                self.audio_player.stop()
                if self._cached_audio_file:
                    try:
                        os.remove(self._cached_audio_file)
                    except Exception:
                        pass
            finally:
                super().closeEvent(event)


class VideoDownloaderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fetch_thread: FetchInfoThread | None = None
        self.download_thread: DownloadThread | None = None

        self.all_formats: list[dict[str, Any]] = []
        self.filtered_formats: list[dict[str, Any]] = []
        self.queue_urls: list[str] = []
        self.finished_tasks = 0
        self._thumbnail_source: QPixmap | None = None
        self._current_video_url = ""
        self._preview_stream_url = ""
        self._preview_stream_candidates: list[tuple[str, str]] = []
        self._preview_audio_stream_url = ""
        self._preview_audio_stream_urls: list[str] = []
        self._preview_dialog = None
        self._glass_effect_applied = False
        self._startup_centered = False
        self._selected_video_format_id = ""
        self._selected_audio_format_id = ""
        self._selected_muxed_format_id = ""

        self.setWindowTitle("\u89c6\u9891\u4e0b\u8f7d\u5668 - PyQt6 \u91cd\u6784\u7248")
        window_icon = QIcon(APP_ICON_PATH)
        if not window_icon.isNull():
            self.setWindowIcon(window_icon)
        self.resize(1600, 960)
        self.setMinimumSize(1280, 820)
        self.setFont(QFont("Microsoft YaHei UI", 10))
        if os.name == "nt":
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._init_ui()
        self._apply_style()
        self._load_settings()

    def _init_ui(self) -> None:
        root = QWidget(self)
        root.setObjectName("RootSurface")
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        config_box = QGroupBox("\u4efb\u52a1\u914d\u7f6e")
        config_box.setMinimumHeight(330)
        config_outer_layout = QVBoxLayout(config_box)
        config_outer_layout.setSpacing(8)

        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("\u6bcf\u884c\u4e00\u4e2a\u89c6\u9891\u94fe\u63a5\uff0c\u53ef\u6279\u91cf\u4e0b\u8f7d")
        self.url_input.setMinimumHeight(72)
        self.url_input.setMaximumHeight(120)
        self.url_input.cursorPositionChanged.connect(self._update_url_active_line_highlight)
        self.url_input.textChanged.connect(self._update_url_active_line_highlight)

        self.output_path = QLineEdit(os.path.join(os.getcwd(), "downloads"))
        self.path_btn = QPushButton("\u9009\u62e9\u76ee\u5f55")
        self.path_btn.clicked.connect(self._pick_output_path)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.output_path)
        path_layout.addWidget(self.path_btn)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("\u6700\u4f73\u89c6\u9891+\u97f3\u9891", "video")
        self.mode_combo.addItem("\u4ec5\u97f3\u9891", "audio")
        self.mode_combo.addItem("\u81ea\u5b9a\u4e49\u683c\u5f0f", "custom")
        self.mode_combo.currentIndexChanged.connect(self._update_mode_state)

        self.custom_format = QLineEdit()
        self.custom_format.setPlaceholderText("\u4f8b\uff1a137+140 \u6216 bv*+ba/b")
        self.audio_codec = QComboBox()
        self.audio_codec.addItems(["mp3", "m4a", "opus"])
        self.video_container = QComboBox()
        self.video_container.addItems(["mp4", "mkv", "webm"])
        self.output_template = QLineEdit("%(title)s [%(id)s].%(ext)s")

        self.cookie_browser = QComboBox()
        self.cookie_browser.addItem("\u4e0d\u4f7f\u7528\u6d4f\u89c8\u5668 Cookies", "none")
        self.cookie_browser.addItem("Chrome", "chrome")
        self.cookie_browser.addItem("Edge", "edge")
        self.cookie_browser.addItem("Firefox", "firefox")
        self.cookie_browser.addItem("Brave", "brave")
        self.cookie_file_input = QLineEdit()
        self.cookie_file_input.setPlaceholderText("\u53ef\u9009\uff1acookies.txt\uff08Netscape \u683c\u5f0f\uff09")
        self.cookie_file_btn = QPushButton("\u9009\u62e9\u6587\u4ef6")
        self.cookie_file_btn.clicked.connect(self._pick_cookie_file)
        cookie_file_layout = QHBoxLayout()
        cookie_file_layout.addWidget(self.cookie_file_input)
        cookie_file_layout.addWidget(self.cookie_file_btn)
        self.impersonate_combo = QComboBox()
        self.impersonate_combo.addItem("\u4e0d\u542f\u7528", "")
        self.impersonate_combo.addItem("chrome", "chrome")
        self.impersonate_combo.addItem("edge", "edge")
        self.impersonate_combo.addItem("safari", "safari")
        self.youtube_player_client_input = QLineEdit()
        self.youtube_player_client_input.setPlaceholderText(
            "\u53ef\u9009\uff1aandroid_vr,web_safari\uff08\u7528\u9017\u53f7\u5206\u9694\uff09"
        )

        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("\u4f8b\u5982\uff1ahttp://127.0.0.1:7890")

        self.ffmpeg_location = QLineEdit()
        self.ffmpeg_location.setPlaceholderText("\u53ef\u9009\uff1affmpeg \u4e8c\u8fdb\u5236\u76ee\u5f55")
        self.ffmpeg_btn = QPushButton("\u9009\u62e9")
        self.ffmpeg_btn.clicked.connect(self._pick_ffmpeg_path)

        ffmpeg_layout = QHBoxLayout()
        ffmpeg_layout.addWidget(self.ffmpeg_location)
        ffmpeg_layout.addWidget(self.ffmpeg_btn)

        self.playlist_checkbox = QCheckBox("\u5141\u8bb8\u4e0b\u8f7d\u64ad\u653e\u5217\u8868")
        self.task_retry_spin = QSpinBox()
        self.task_retry_spin.setRange(0, 5)
        self.task_retry_spin.setValue(1)
        self.task_retry_spin.setSuffix(" \u6b21")

        basic_tab = QWidget()
        basic_layout = QGridLayout(basic_tab)
        basic_layout.setHorizontalSpacing(10)
        basic_layout.setVerticalSpacing(8)
        basic_layout.setColumnStretch(1, 2)
        basic_layout.setColumnStretch(3, 2)
        basic_layout.setRowMinimumHeight(0, 92)
        basic_layout.setRowMinimumHeight(1, 36)

        basic_layout.addWidget(QLabel("\u94fe\u63a5\u5217\u8868"), 0, 0)
        basic_layout.addWidget(self.url_input, 0, 1, 1, 3)
        basic_layout.addWidget(QLabel("\u4fdd\u5b58\u76ee\u5f55"), 1, 0)
        basic_layout.addLayout(path_layout, 1, 1, 1, 3)
        basic_layout.addWidget(QLabel("\u4e0b\u8f7d\u6a21\u5f0f"), 2, 0)
        basic_layout.addWidget(self.mode_combo, 2, 1)
        basic_layout.addWidget(QLabel("\u81ea\u5b9a\u4e49\u683c\u5f0f"), 2, 2)
        basic_layout.addWidget(self.custom_format, 2, 3)
        basic_layout.addWidget(QLabel("\u97f3\u9891\u7f16\u7801"), 3, 0)
        basic_layout.addWidget(self.audio_codec, 3, 1)
        basic_layout.addWidget(QLabel("\u89c6\u9891\u5c01\u88c5"), 3, 2)
        basic_layout.addWidget(self.video_container, 3, 3)
        basic_layout.addWidget(QLabel("\u547d\u540d\u6a21\u677f"), 4, 0)
        basic_layout.addWidget(self.output_template, 4, 1, 1, 3)
        basic_layout.addWidget(QLabel("\u5931\u8d25\u91cd\u8bd5"), 5, 0)
        basic_layout.addWidget(self.task_retry_spin, 5, 1)
        basic_layout.addWidget(self.playlist_checkbox, 5, 2, 1, 2)

        network_tab = QWidget()
        network_layout = QGridLayout(network_tab)
        network_layout.setHorizontalSpacing(10)
        network_layout.setVerticalSpacing(8)
        network_layout.setColumnStretch(1, 2)
        network_layout.setColumnStretch(3, 2)

        network_layout.addWidget(QLabel("Cookies"), 0, 0)
        network_layout.addWidget(self.cookie_browser, 0, 1)
        network_layout.addWidget(QLabel("\u6a21\u62df\u5ba2\u6237\u7aef"), 0, 2)
        network_layout.addWidget(self.impersonate_combo, 0, 3)
        network_layout.addWidget(QLabel("Cookies\u6587\u4ef6"), 1, 0)
        network_layout.addLayout(cookie_file_layout, 1, 1, 1, 3)
        network_layout.addWidget(QLabel("\u4ee3\u7406"), 2, 0)
        network_layout.addWidget(self.proxy_input, 2, 1)
        network_layout.addWidget(QLabel("FFmpeg"), 2, 2)
        network_layout.addLayout(ffmpeg_layout, 2, 3)
        network_layout.addWidget(QLabel("YT player_client"), 3, 0)
        network_layout.addWidget(self.youtube_player_client_input, 3, 1, 1, 3)

        config_tabs = QTabWidget()
        config_tabs.addTab(basic_tab, "\u57fa\u7840\u8bbe\u7f6e")
        config_tabs.addTab(network_tab, "\u9ad8\u7ea7\u7f51\u7edc")
        config_outer_layout.addWidget(config_tabs)

        self.fetch_btn = QPushButton("\u89e3\u6790\u89c6\u9891\u4fe1\u606f")
        self.start_btn = QPushButton("\u5f00\u59cb\u4e0b\u8f7d")
        self.stop_btn = QPushButton("\u505c\u6b62\u4efb\u52a1")
        self.open_dir_btn = QPushButton("\u6253\u5f00\u4e0b\u8f7d\u76ee\u5f55")
        self.stop_btn.setEnabled(False)

        self.fetch_btn.clicked.connect(self._fetch_info)
        self.start_btn.clicked.connect(self._start_download)
        self.stop_btn.clicked.connect(self._stop_download)
        self.open_dir_btn.clicked.connect(self._open_download_folder)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(self.fetch_btn)
        actions.addWidget(self.start_btn)
        actions.addWidget(self.stop_btn)
        actions.addWidget(self.open_dir_btn)
        config_outer_layout.addLayout(actions)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)
        left_layout.addWidget(config_box)

        info_box = QGroupBox("\u89c6\u9891\u4fe1\u606f")
        info_outer_layout = QHBoxLayout(info_box)
        info_outer_layout.setSpacing(10)
        info_left = QWidget()
        info_layout = QFormLayout(info_left)
        info_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.title_label = QLabel("-")
        self.uploader_label = QLabel("-")
        self.duration_label = QLabel("-")
        self.views_label = QLabel("-")
        self.link_label = QTextEdit("-")
        self.link_label.setReadOnly(True)
        self.link_label.setObjectName("InfoInlineLink")
        self.link_label.setMaximumHeight(52)
        self.link_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.link_label.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.title_label.setWordWrap(True)
        self.uploader_label.setWordWrap(True)
        info_layout.addRow("\u6807\u9898", self.title_label)
        info_layout.addRow("\u4f5c\u8005", self.uploader_label)
        info_layout.addRow("\u65f6\u957f", self.duration_label)
        info_layout.addRow("\u64ad\u653e\u91cf", self.views_label)
        info_layout.addRow("\u94fe\u63a5", self.link_label)

        thumb_panel = QWidget()
        thumb_layout = QVBoxLayout(thumb_panel)
        thumb_layout.setContentsMargins(0, 0, 0, 0)
        thumb_layout.setSpacing(0)
        self.thumbnail_label = QLabel("")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setMinimumSize(230, 130)
        self.thumbnail_label.setMaximumWidth(320)
        self.thumbnail_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumbnail_label.mousePressEvent = self._on_thumbnail_clicked
        self.thumbnail_play_btn = QPushButton(self.thumbnail_label)
        self.thumbnail_play_btn.setObjectName("ThumbPlayOverlay")
        self.thumbnail_play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.thumbnail_play_btn.setIconSize(QSize(28, 28))
        self.thumbnail_play_btn.setFixedSize(56, 56)
        self.thumbnail_play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumbnail_play_btn.clicked.connect(self._on_thumbnail_clicked)
        self.thumbnail_play_btn.hide()
        thumb_layout.addWidget(self.thumbnail_label, 1)
        info_outer_layout.addWidget(info_left, 1)
        info_outer_layout.addWidget(thumb_panel, 1)
        info_box.setMaximumHeight(240)
        left_layout.addWidget(info_box)

        filter_box = QGroupBox("\u683c\u5f0f\u7b5b\u9009")
        filter_layout = QGridLayout(filter_box)
        filter_layout.setHorizontalSpacing(10)
        filter_layout.setVerticalSpacing(6)
        filter_layout.setColumnStretch(1, 1)
        filter_layout.setColumnStretch(3, 1)
        filter_layout.setColumnStretch(4, 1)
        self.ext_filter = QComboBox()
        self.ext_filter.addItems(["\u5168\u90e8\u6269\u5c55\u540d", "mp4", "webm", "m4a", "mp3", "mov", "flv"])
        self.vcodec_filter = QComboBox()
        self.vcodec_filter.addItems(["\u5168\u90e8\u7f16\u7801", "avc1/h264", "vp9", "av01", "hevc/h265", "\u4ec5\u65e0\u89c6\u9891"])
        self.audio_only_filter = QCheckBox("\u4ec5\u97f3\u9891\u6d41")
        self.apply_filter_btn = QPushButton("\u5e94\u7528\u7b5b\u9009")
        self.reset_filter_btn = QPushButton("\u91cd\u7f6e")
        self.apply_filter_btn.clicked.connect(self._apply_format_filter)
        self.reset_filter_btn.clicked.connect(self._reset_format_filter)

        filter_layout.addWidget(QLabel("\u6269\u5c55\u540d"), 0, 0)
        filter_layout.addWidget(self.ext_filter, 0, 1)
        filter_layout.addWidget(QLabel("\u89c6\u9891\u7f16\u7801"), 0, 2)
        filter_layout.addWidget(self.vcodec_filter, 0, 3)
        filter_layout.addWidget(self.audio_only_filter, 1, 0, 1, 2)
        filter_layout.addWidget(self.apply_filter_btn, 1, 3)
        filter_layout.addWidget(self.reset_filter_btn, 1, 4)
        left_layout.addWidget(filter_box)
        self.format_table = QTableWidget(0, 8)
        self.format_table.setHorizontalHeaderLabels([
            "\u683c\u5f0fID", "\u6269\u5c55\u540d", "\u5206\u8fa8\u7387", "FPS", "\u5927\u5c0f", "\u89c6\u9891\u7f16\u7801", "\u97f3\u9891\u7f16\u7801", "\u5907\u6ce8"
        ])
        self.format_table.setAlternatingRowColors(True)
        self.format_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.format_table.cellDoubleClicked.connect(self._pick_format_from_table)
        self.format_table.setWordWrap(False)
        self.format_table.verticalHeader().setDefaultSectionSize(24)
        fmt_header = self.format_table.horizontalHeader()
        fmt_header.setMinimumSectionSize(60)
        fmt_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        fmt_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        fmt_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        fmt_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        fmt_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        fmt_header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        fmt_header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        fmt_header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        format_box = QGroupBox("\u53ef\u7528\u683c\u5f0f\uff08\u53cc\u51fb\u683c\u5f0fID\u53ef\u56de\u586b\u5230\u81ea\u5b9a\u4e49\u683c\u5f0f\uff09")
        format_layout = QVBoxLayout(format_box)
        format_layout.addWidget(self.format_table)
        format_box.setMinimumHeight(260)
        left_layout.addWidget(format_box, 1)

        self.queue_table = QTableWidget(0, 5)
        self.queue_table.setHorizontalHeaderLabels(["\u5e8f\u53f7", "URL", "\u72b6\u6001", "\u8fdb\u5ea6", "\u7ed3\u679c"])
        self.queue_table.setAlternatingRowColors(True)
        self.queue_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.queue_table.setWordWrap(False)
        self.queue_table.verticalHeader().setDefaultSectionSize(24)
        self.queue_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.queue_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.queue_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.queue_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.queue_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.queue_table.setColumnWidth(2, 120)
        self.queue_table.setColumnWidth(3, 90)

        queue_box = QGroupBox("\u4efb\u52a1\u961f\u5217")
        queue_layout = QVBoxLayout(queue_box)
        queue_layout.addWidget(self.queue_table)
        queue_box.setMinimumHeight(220)

        main_splitter.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)

        runtime_box = QGroupBox("\u8fd0\u884c\u72b6\u6001")
        runtime_layout = QVBoxLayout(runtime_box)
        self.task_status = QLabel("\u5c31\u7eea")
        self.current_progress = QProgressBar()
        self.current_progress.setRange(0, 100)
        self.total_progress = QProgressBar()
        self.total_progress.setRange(0, 100)
        self.progress_detail = QLabel("Speed: - | ETA: -")
        runtime_layout.addWidget(self.task_status)
        runtime_layout.addWidget(QLabel("\u5f53\u524d\u4efb\u52a1\u8fdb\u5ea6"))
        runtime_layout.addWidget(self.current_progress)
        runtime_layout.addWidget(QLabel("\u961f\u5217\u603b\u4f53\u8fdb\u5ea6"))
        runtime_layout.addWidget(self.total_progress)
        runtime_layout.addWidget(self.progress_detail)
        runtime_box.setMinimumHeight(170)
        runtime_box.setMaximumHeight(210)
        right_layout.addWidget(runtime_box)

        log_box = QGroupBox("\u5b9e\u65f6\u65e5\u5fd7")
        log_layout = QVBoxLayout(log_box)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.log_output.customContextMenuRequested.connect(self._show_log_context_menu)
        log_layout.addWidget(self.log_output)
        log_box.setMinimumHeight(260)

        right_content_splitter = QSplitter(Qt.Orientation.Vertical)
        right_content_splitter.setChildrenCollapsible(False)
        right_content_splitter.addWidget(queue_box)
        right_content_splitter.addWidget(log_box)
        right_content_splitter.setStretchFactor(0, 2)
        right_content_splitter.setStretchFactor(1, 3)
        right_content_splitter.setSizes([300, 430])
        right_layout.addWidget(right_content_splitter, 1)

        main_splitter.addWidget(right_panel)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([860, 780])
        root_layout.addWidget(main_splitter, 1)

        self._update_mode_state()
        self._sync_thumbnail_overlay()
        self._update_url_active_line_highlight()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background: transparent; }
            QWidget#RootSurface {
                background: rgba(245, 248, 255, 78);
                border-radius: 12px;
            }
            #TitleHeader { font-size: 24px; font-weight: 700; color: #1f2a44; }
            #SubHeader { color: #5b6480; }
            QGroupBox {
                border: 1px solid #d7ddea;
                border-radius: 10px;
                margin-top: 12px;
                background: rgba(255, 255, 255, 122);
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #2c3858;
            }
            QSplitter::handle {
                background: transparent;
                border: none;
            }
            QSplitter::handle:hover {
                background: transparent;
            }
            QSplitter::handle:pressed {
                background: transparent;
            }
            QTabWidget::pane {
                border: 1px solid #d7ddea;
                border-radius: 8px;
                background: rgba(255, 255, 255, 102);
                top: -1px;
            }
            QTabBar::tab {
                background: rgba(233, 238, 251, 180);
                color: #2c3858;
                padding: 6px 14px;
                border: 1px solid #d1d9ee;
                border-bottom: 0;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: rgba(255, 255, 255, 215);
                font-weight: 600;
            }
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(67, 169, 123, 198),
                    stop: 1 rgba(94, 198, 149, 188)
                );
                color: #f7faff;
                border: 1px solid rgba(255, 255, 255, 128);
                border-radius: 7px;
                min-height: 30px;
                padding: 0 12px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(78, 184, 134, 210),
                    stop: 1 rgba(111, 211, 161, 200)
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(54, 141, 102, 212),
                    stop: 1 rgba(73, 172, 125, 204)
                );
            }
            QPushButton:disabled {
                background: rgba(154, 166, 196, 150);
                color: rgba(245, 248, 255, 170);
                border: 1px solid rgba(255, 255, 255, 90);
            }
            QLineEdit, QTextEdit, QComboBox, QTableWidget, QSpinBox {
                border: 1px solid #cbd4e8;
                border-radius: 7px;
                background: rgba(252, 253, 255, 148);
            }
            QProgressBar {
                border: 1px solid #cbd4e8;
                border-radius: 6px;
                text-align: center;
                background: rgba(252, 253, 255, 120);
            }
            QProgressBar::chunk { background-color: #2cbf6d; border-radius: 6px; }
            QTextEdit#InfoInlineLink {
                border: 0;
                background: transparent;
                padding: 0;
                color: #2b3550;
            }
            QPushButton#ThumbPlayOverlay {
                background: rgba(10, 20, 40, 130);
                border: 1px solid rgba(255, 255, 255, 120);
                border-radius: 28px;
                padding: 0;
            }
            QPushButton#ThumbPlayOverlay:hover {
                background: rgba(10, 20, 40, 180);
            }
            """
        )

    def _append_log(self, text: str) -> None:
        now = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{now}] {text}")

    def _show_log_context_menu(self, pos) -> None:
        menu = self.log_output.createStandardContextMenu()
        menu.addSeparator()
        clear_action = menu.addAction("\u6e05\u9664\u65e5\u5fd7")
        clear_action.setEnabled(bool(self.log_output.toPlainText().strip()))
        clear_action.triggered.connect(self.log_output.clear)
        menu.exec(self.log_output.viewport().mapToGlobal(pos))

    def _update_url_active_line_highlight(self) -> None:
        cursor = self.url_input.textCursor()
        line_text = cursor.block().text().strip()
        if not line_text:
            self.url_input.setExtraSelections([])
            return

        selection = QTextEdit.ExtraSelection()
        line_cursor = QTextCursor(cursor)
        line_cursor.clearSelection()
        selection.cursor = line_cursor
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.format.setBackground(QColor(31, 102, 255, 30))
        self.url_input.setExtraSelections([selection])

    def _set_thumbnail_placeholder(self, text: str = "") -> None:
        self._thumbnail_source = None
        self.thumbnail_label.clear()
        self.thumbnail_label.setText(text)
        self._sync_thumbnail_overlay()

    def _position_thumbnail_play_button(self) -> None:
        btn = self.thumbnail_play_btn
        host = self.thumbnail_label
        x = max(0, (host.width() - btn.width()) // 2)
        y = max(0, (host.height() - btn.height()) // 2)
        btn.move(x, y)

    def _sync_thumbnail_overlay(self) -> None:
        can_click = bool(self._current_video_url and self._thumbnail_source is not None)
        self.thumbnail_play_btn.setVisible(can_click)
        self.thumbnail_label.setToolTip("" if not can_click else "\u70b9\u51fb\u5c01\u9762\u64ad\u653e")
        self.thumbnail_label.setCursor(
            Qt.CursorShape.PointingHandCursor if can_click else Qt.CursorShape.ArrowCursor
        )
        self._position_thumbnail_play_button()

    def _render_thumbnail(self) -> None:
        if not self._thumbnail_source:
            return
        target = self.thumbnail_label.size()
        if target.width() <= 2 or target.height() <= 2:
            return
        scaled = self._thumbnail_source.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.thumbnail_label.setPixmap(scaled)
        self._position_thumbnail_play_button()

    def _set_thumbnail_from_url(self, url: str) -> None:
        clean = url.strip()
        if not clean:
            self._set_thumbnail_placeholder()
            return
        try:
            req = urllib.request.Request(clean, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
            pix = QPixmap()
            if not pix.loadFromData(data):
                self._set_thumbnail_placeholder()
                return
            self._thumbnail_source = pix
            self.thumbnail_label.setText("")
            self._render_thumbnail()
            self._sync_thumbnail_overlay()
        except Exception:
            self._set_thumbnail_placeholder()

    def _on_thumbnail_clicked(self, event) -> None:  # type: ignore[override]
        if hasattr(event, "button") and event.button() != Qt.MouseButton.LeftButton:
            return
        if not self.thumbnail_play_btn.isVisible():
            return
        if not self._current_video_url:
            return

        stream_url = self._preview_stream_url or ""
        if not QT_MEDIA_AVAILABLE or not stream_url:
            os.startfile(self._current_video_url)
            return

        try:
            candidates = list(self._preview_stream_candidates)
            if stream_url and all(url != stream_url for _label, url in candidates):
                candidates.insert(0, ("\u63a8\u8350", stream_url))
            dlg = PreviewPlayerDialog(
                self,
                str(self.title_label.text() or "\u89c6\u9891"),
                stream_url,
                self._current_video_url,
                candidates,
                self._preview_audio_stream_url,
                self._preview_audio_stream_urls,
            )
            self._preview_dialog = dlg
            dlg.show()
            dlg.raise_()
            dlg.activateWindow()
        except Exception as exc:
            QMessageBox.warning(self, "\u9884\u89c8\u5931\u8d25", str(exc))

    def _pick_output_path(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "\u9009\u62e9\u4e0b\u8f7d\u76ee\u5f55")
        if folder:
            self.output_path.setText(folder)

    def _pick_ffmpeg_path(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "\u9009\u62e9 ffmpeg \u76ee\u5f55")
        if folder:
            self.ffmpeg_location.setText(folder)

    def _pick_cookie_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "\u9009\u62e9 cookies \u6587\u4ef6",
            "",
            "Cookie Files (*.txt *.cookies);;All Files (*.*)",
        )
        if file_path:
            self.cookie_file_input.setText(file_path)

    def _open_download_folder(self) -> None:
        path = self.output_path.text().strip()
        if not path:
            QMessageBox.information(self, "\u63d0\u793a", "\u8bf7\u5148\u8bbe\u7f6e\u4e0b\u8f7d\u76ee\u5f55")
            return
        os.makedirs(path, exist_ok=True)
        os.startfile(path)

    def _update_mode_state(self) -> None:
        mode = self.mode_combo.currentData()
        self.audio_codec.setEnabled(mode == "audio")
        self.video_container.setEnabled(mode == "video")
        self.custom_format.setEnabled(mode == "custom")

    def _read_urls(self) -> list[str]:
        return [x.strip() for x in self.url_input.toPlainText().splitlines() if x.strip()]

    def _get_active_url(self) -> str:
        active = self.url_input.textCursor().block().text().strip()
        if active:
            return active
        urls = self._read_urls()
        return urls[0] if urls else ""

    def _normalize_network_fields(self) -> str:
        player_raw = self.youtube_player_client_input.text().strip()
        proxy_raw = self.proxy_input.text().strip()

        if player_raw and "://" in player_raw and not proxy_raw:
            self.proxy_input.setText(player_raw)
            self.youtube_player_client_input.setText("")
            self._append_log(
                "\u68c0\u6d4b\u5230 YT player_client \u586b\u5165\u4e86\u4ee3\u7406\u5730\u5740\uff0c\u5df2\u81ea\u52a8\u79fb\u5230\u201c\u4ee3\u7406\u201d\u8f93\u5165\u6846"
            )
            player_raw = ""

        clients, invalid = _parse_youtube_player_clients(player_raw)
        if invalid:
            self._append_log(
                "\u68c0\u6d4b\u5230\u65e0\u6548 YT player_client \u53c2\u6570\uff0c\u5df2\u5ffd\u7565\uff1a"
                + ", ".join(invalid[:3])
            )
            normalized = ",".join(clients)
            self.youtube_player_client_input.setText(normalized)
            return normalized
        return ",".join(clients) if clients else player_raw

    def _fetch_info(self) -> None:
        urls = self._read_urls()
        if not urls:
            QMessageBox.warning(self, "\u7f3a\u5c11\u8f93\u5165", "\u8bf7\u81f3\u5c11\u8f93\u5165\u4e00\u4e2a\u94fe\u63a5")
            return
        target_url = self._get_active_url()
        if not target_url:
            QMessageBox.warning(self, "\u7f3a\u5c11\u8f93\u5165", "\u8bf7\u5148\u9009\u4e2d\u6216\u8f93\u5165\u6709\u6548\u94fe\u63a5")
            return
        if self.fetch_thread and self.fetch_thread.isRunning():
            QMessageBox.information(self, "\u8bf7\u7a0d\u5019", "\u6b63\u5728\u89e3\u6790\u4e0a\u4e00\u4e2a\u94fe\u63a5")
            return

        self.fetch_btn.setEnabled(False)
        self.format_table.setRowCount(0)
        self._selected_video_format_id = ""
        self._selected_audio_format_id = ""
        self._selected_muxed_format_id = ""
        self._current_video_url = target_url
        self._preview_stream_url = ""
        self._preview_stream_candidates = []
        self._preview_audio_stream_url = ""
        self._preview_audio_stream_urls = []
        self._sync_thumbnail_overlay()
        self._set_thumbnail_placeholder()
        self._append_log(f"\u5f00\u59cb\u89e3\u6790\u4fe1\u606f\uff1a{target_url}")
        player_clients = self._normalize_network_fields()

        self.fetch_thread = FetchInfoThread(
            target_url,
            str(self.cookie_browser.currentData()),
            self.cookie_file_input.text().strip(),
            str(self.impersonate_combo.currentData() or ""),
            player_clients,
        )
        self.fetch_thread.log.connect(self._append_log)
        self.fetch_thread.info_ready.connect(self._on_info_ready)
        self.fetch_thread.failed.connect(self._on_fetch_failed)
        self.fetch_thread.finished.connect(lambda: self.fetch_btn.setEnabled(True))
        self.fetch_thread.start()

    def _on_info_ready(self, info: dict, formats: list[dict]) -> None:
        page_url = str(info.get("webpage_url") or self._current_video_url or "")
        self.title_label.setText(str(info.get("title") or "-"))
        self.uploader_label.setText(str(info.get("uploader") or "-"))
        self.duration_label.setText(_human_duration(info.get("duration")))
        self.views_label.setText(str(info.get("view_count") or "-"))
        self.link_label.setPlainText(page_url)
        self.link_label.setToolTip(page_url)
        self._current_video_url = page_url
        self._preview_stream_candidates = _collect_preview_stream_candidates(formats)
        self._preview_audio_stream_urls = _pick_preview_audio_stream_urls(formats)
        self._preview_audio_stream_url = self._preview_audio_stream_urls[0] if self._preview_audio_stream_urls else ""
        self._preview_stream_url = _pick_default_preview_stream_url(self._preview_stream_candidates)
        if not self._preview_stream_url:
            self._preview_stream_url = str(info.get("preview_stream_url") or "").strip()
        if self._preview_stream_url and all(
            url != self._preview_stream_url for _label, url in self._preview_stream_candidates
        ):
            self._preview_stream_candidates.insert(0, ("\u63a8\u8350", self._preview_stream_url))
        if not self._preview_stream_url:
            self._preview_stream_url = _pick_preview_stream_url({"formats": formats})
            if self._preview_stream_url:
                self._preview_stream_candidates = [("\u9ed8\u8ba4", self._preview_stream_url)]
        self._sync_thumbnail_overlay()
        self._set_thumbnail_from_url(str(info.get("thumbnail_url") or ""))
        self._selected_video_format_id = ""
        self._selected_audio_format_id = ""
        self._selected_muxed_format_id = ""
        self.all_formats = [f for f in formats if self._is_downloadable_av_format(f)]
        self._apply_format_filter()
        self._append_log(
            f"\u89e3\u6790\u5b8c\u6210\uff0c\u5171 {len(self.all_formats)} \u4e2a\u97f3/\u89c6\u9891\u683c\u5f0f\uff08\u5df2\u8fc7\u6ee4 {len(formats) - len(self.all_formats)} \u4e2a\u975e\u97f3/\u89c6\u9891\u683c\u5f0f\uff09"
        )

    def _on_fetch_failed(self, err: str) -> None:
        self._selected_video_format_id = ""
        self._selected_audio_format_id = ""
        self._selected_muxed_format_id = ""
        self._preview_stream_url = ""
        self._preview_stream_candidates = []
        self._preview_audio_stream_url = ""
        self._preview_audio_stream_urls = []
        self._sync_thumbnail_overlay()
        self._set_thumbnail_placeholder()
        self._append_log(f"\u89e3\u6790\u5931\u8d25\uff1a{err}")
        QMessageBox.critical(self, "\u89e3\u6790\u5931\u8d25", err)

    @staticmethod
    def _format_has_video(fmt: dict[str, Any]) -> bool:
        return str(fmt.get("vcodec") or "none").lower() != "none"

    @staticmethod
    def _format_has_audio(fmt: dict[str, Any]) -> bool:
        return str(fmt.get("acodec") or "none").lower() != "none"

    def _is_downloadable_av_format(self, fmt: dict[str, Any]) -> bool:
        ext = str(fmt.get("ext") or "").strip().lower()
        if not ext or ext == "mhtml":
            return False
        has_video = self._format_has_video(fmt)
        has_audio = self._format_has_audio(fmt)
        if not has_video and not has_audio:
            return False
        if not str(fmt.get("format_id") or "").strip():
            return False
        return True

    def _format_stream_kind(self, fmt: dict[str, Any]) -> str:
        has_video = self._format_has_video(fmt)
        has_audio = self._format_has_audio(fmt)
        if has_video and has_audio:
            return "muxed"
        if has_video:
            return "video"
        if has_audio:
            return "audio"
        return "other"

    def _build_custom_format_from_selection(self) -> str:
        if self._selected_muxed_format_id:
            return f"{self._selected_muxed_format_id}/bv*+ba/b"
        if self._selected_video_format_id and self._selected_audio_format_id:
            return f"{self._selected_video_format_id}+{self._selected_audio_format_id}/bv*+ba/b"
        if self._selected_video_format_id:
            return f"{self._selected_video_format_id}+ba/b"
        if self._selected_audio_format_id:
            return f"bv*+{self._selected_audio_format_id}/b"
        return "bv*+ba/b"

    def _format_passes_filter(self, fmt: dict[str, Any]) -> bool:
        ext_selected = self.ext_filter.currentText()
        vcodec_selected = self.vcodec_filter.currentText()
        ext = str(fmt.get("ext") or "")
        vcodec = str(fmt.get("vcodec") or "")

        if ext_selected != "\u5168\u90e8\u6269\u5c55\u540d" and ext != ext_selected:
            return False
        if self.audio_only_filter.isChecked() and vcodec != "none":
            return False
        if vcodec_selected == "avc1/h264" and not (vcodec.startswith("avc1") or "h264" in vcodec):
            return False
        if vcodec_selected == "vp9" and not vcodec.startswith("vp9"):
            return False
        if vcodec_selected == "av01" and not vcodec.startswith("av01"):
            return False
        if vcodec_selected == "hevc/h265" and not ("hev" in vcodec or "h265" in vcodec):
            return False
        if vcodec_selected == "\u4ec5\u65e0\u89c6\u9891" and vcodec != "none":
            return False
        return True

    def _apply_format_filter(self) -> None:
        if not self.all_formats:
            self.format_table.setRowCount(0)
            return
        self.filtered_formats = [f for f in self.all_formats if self._format_passes_filter(f)]
        self._fill_format_table(self.filtered_formats)

    def _reset_format_filter(self) -> None:
        self.ext_filter.setCurrentIndex(0)
        self.vcodec_filter.setCurrentIndex(0)
        self.audio_only_filter.setChecked(False)
        self._apply_format_filter()

    def _fill_format_table(self, formats: list[dict[str, Any]]) -> None:
        rows = min(len(formats), 400)
        self.format_table.setRowCount(rows)
        for row in range(rows):
            fmt = formats[row]
            kind = self._format_stream_kind(fmt)
            if kind == "video":
                stream_note = "\u89c6\u9891"
            elif kind == "audio":
                stream_note = "\u97f3\u9891"
            elif kind == "muxed":
                stream_note = "\u97f3+\u89c6"
            else:
                stream_note = "-"
            cells = [
                str(fmt.get("format_id", "-")),
                str(fmt.get("ext", "-")),
                str(fmt.get("resolution", fmt.get("format_note", "-"))),
                str(fmt.get("fps", "-")),
                _human_size(fmt.get("filesize") or fmt.get("filesize_approx")),
                str(fmt.get("vcodec", "-")),
                str(fmt.get("acodec", "-")),
                f"{stream_note} | {str(fmt.get('format_note', '-'))}",
            ]
            for col, value in enumerate(cells):
                item = QTableWidgetItem(value)
                if col in (0, 3):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.format_table.setItem(row, col, item)

    def _pick_format_from_table(self, row: int, _column: int) -> None:
        if row < 0 or row >= len(self.filtered_formats):
            return
        fmt = self.filtered_formats[row]
        fmt_id = str(fmt.get("format_id") or "").strip()
        if not fmt_id:
            return
        kind = self._format_stream_kind(fmt)
        if kind == "video":
            self._selected_video_format_id = fmt_id
            self._selected_muxed_format_id = ""
            msg = f"\u5df2\u9009\u62e9\u89c6\u9891\u683c\u5f0f\uff1a{fmt_id}\uff0c\u97f3\u9891\u5c06\u81ea\u52a8\u4f7f\u7528\u6700\u4f73\u6216\u5df2\u9009\u683c\u5f0f"
        elif kind == "audio":
            self._selected_audio_format_id = fmt_id
            self._selected_muxed_format_id = ""
            msg = f"\u5df2\u9009\u62e9\u97f3\u9891\u683c\u5f0f\uff1a{fmt_id}\uff0c\u89c6\u9891\u5c06\u81ea\u52a8\u4f7f\u7528\u6700\u4f73\u6216\u5df2\u9009\u683c\u5f0f"
        elif kind == "muxed":
            self._selected_video_format_id = ""
            self._selected_audio_format_id = ""
            self._selected_muxed_format_id = fmt_id
            msg = f"\u5df2\u9009\u62e9\u97f3\u89c6\u4e00\u4f53\u683c\u5f0f\uff1a{fmt_id}"
        else:
            return

        custom_expr = self._build_custom_format_from_selection()
        self._set_combo_by_data(self.mode_combo, "custom")
        self.custom_format.setText(custom_expr)
        self._append_log(f"{msg}\uff0c\u81ea\u5b9a\u4e49\u683c\u5f0f\uff1a{custom_expr}")

    def _init_queue_table(self, urls: list[str]) -> None:
        self.queue_urls = urls
        self.queue_table.setRowCount(len(urls))
        for idx, url in enumerate(urls):
            values = [str(idx + 1), url, "\u7b49\u5f85\u4e2d", "0%", "-"]
            for col, val in enumerate(values):
                self.queue_table.setItem(idx, col, QTableWidgetItem(val))

    def _update_queue_row(self, idx: int, status: str | None = None, progress: str | None = None, result: str | None = None) -> None:
        if idx < 0 or idx >= self.queue_table.rowCount():
            return
        if status is not None:
            self.queue_table.setItem(idx, 2, QTableWidgetItem(status))
        if progress is not None:
            self.queue_table.setItem(idx, 3, QTableWidgetItem(progress))
        if result is not None:
            self.queue_table.setItem(idx, 4, QTableWidgetItem(result))

    def _build_download_config(self) -> DownloadConfig | None:
        urls = self._read_urls()
        if not urls:
            QMessageBox.warning(self, "\u7f3a\u5c11\u8f93\u5165", "\u8bf7\u81f3\u5c11\u8f93\u5165\u4e00\u4e2a\u94fe\u63a5")
            return None
        output_dir = self.output_path.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "\u7f3a\u5c11\u76ee\u5f55", "\u8bf7\u5148\u8bbe\u7f6e\u4e0b\u8f7d\u76ee\u5f55")
            return None
        os.makedirs(output_dir, exist_ok=True)
        player_clients = self._normalize_network_fields()
        mode = str(self.mode_combo.currentData())
        custom_format = self.custom_format.text().strip()
        force_stable = self._should_force_stable_youtube_custom(urls, mode, custom_format)
        return DownloadConfig(
            urls=urls,
            output_dir=output_dir,
            output_template=self.output_template.text().strip() or "%(title)s.%(ext)s",
            mode=mode,
            custom_format=custom_format,
            audio_codec=self.audio_codec.currentText(),
            video_container=self.video_container.currentText(),
            cookie_browser=str(self.cookie_browser.currentData()),
            cookie_file=self.cookie_file_input.text().strip(),
            impersonate_client=str(self.impersonate_combo.currentData() or ""),
            youtube_player_client=player_clients,
            proxy=self.proxy_input.text().strip(),
            ffmpeg_location=self.ffmpeg_location.text().strip(),
            allow_playlist=self.playlist_checkbox.isChecked(),
            max_task_retries=self.task_retry_spin.value(),
            force_stable_for_youtube_custom=force_stable,
        )

    def _should_force_stable_youtube_custom(self, urls: list[str], mode: str, custom_format: str) -> bool:
        if mode != "custom" or not custom_format or not urls:
            return False
        if not _is_youtube_url(urls[0]):
            return False
        if any(x in custom_format for x in ["+", "/", "[", "]", ",", ":"]):
            return False
        if custom_format.isdigit():
            self._append_log(
                f"\u68c0\u6d4b\u5230 YouTube \u5355\u4e00\u683c\u5f0fID\uff1a{custom_format}\uff0c"
                "\u4e3a\u907f\u514d HLS/DASH \u5206\u7247 403\uff0c\u5df2\u81ea\u52a8\u5207\u6362\u7a33\u5b9a\u6a21\u5f0f\uff08bv*+ba/b\uff09"
            )
            return True

        target = None
        for fmt in self.all_formats:
            if str(fmt.get("format_id") or "") == custom_format:
                target = fmt
                break
        if not target:
            return False

        protocol = str(target.get("protocol") or "").lower()
        note = str(target.get("format_note") or "").lower()
        is_fragmented = bool(target.get("fragments")) or "m3u8" in protocol or "dash" in protocol or "hls" in note
        if is_fragmented:
            self._append_log(
                f"\u68c0\u6d4b\u5230\u6240\u9009\u683c\u5f0f {custom_format} \u4e3a\u5206\u7247\u6d41\uff08{protocol or 'unknown'}\uff09\uff0c"
                "\u5df2\u542f\u7528\u7a33\u5b9a\u6a21\u5f0f\u907f\u514d 403"
            )
        return is_fragmented

    def _start_download(self) -> None:
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.information(self, "\u8bf7\u7a0d\u5019", "\u5df2\u6709\u4e0b\u8f7d\u4efb\u52a1\u5728\u8fd0\u884c")
            return
        cfg = self._build_download_config()
        if not cfg:
            return

        self._save_settings()
        self._init_queue_table(cfg.urls)
        self.finished_tasks = 0
        self.current_progress.setValue(0)
        self.total_progress.setValue(0)
        self.task_status.setText("\u51c6\u5907\u4e0b\u8f7d\u961f\u5217")

        self.download_thread = DownloadThread(cfg)
        self.download_thread.log.connect(self._append_log)
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.task_state.connect(self._on_task_state)
        self.download_thread.task_finished.connect(self._on_task_finished)
        self.download_thread.all_done.connect(self._on_all_done)
        self.download_thread.finished.connect(self._on_download_finished)

        self.fetch_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self._append_log("\u4e0b\u8f7d\u4efb\u52a1\u5df2\u542f\u52a8")
        self.download_thread.start()

    def _stop_download(self) -> None:
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.requestInterruption()
            self._append_log("\u5df2\u8bf7\u6c42\u505c\u6b62")
            self.task_status.setText("\u6b63\u5728\u505c\u6b62\u4efb\u52a1...")
            self.stop_btn.setEnabled(False)

    def _on_progress(self, idx: int, percent: float, speed: str, eta: str) -> None:
        p = max(0, min(100, int(percent)))
        self.current_progress.setValue(p)
        self.progress_detail.setText(f"Speed: {speed or '-'} | ETA: {eta or '-'}")
        if idx >= 0:
            self._update_queue_row(idx, progress=f"{p}%")

    def _on_task_state(self, idx: int, status: str, result: str) -> None:
        self._update_queue_row(idx, status=status, result=result)
        if idx < len(self.queue_urls):
            self.task_status.setText(f"\u4efb\u52a1 {idx + 1}/{len(self.queue_urls)}\uff1a{status}")

    def _on_task_finished(self, record: dict) -> None:
        self.finished_tasks += 1
        total = max(1, len(self.queue_urls))
        self.total_progress.setValue(int(self.finished_tasks * 100 / total))

    def _on_all_done(self, ok_count: int, total: int) -> None:
        self.task_status.setText(f"\u961f\u5217\u5b8c\u6210\uff1a\u6210\u529f {ok_count}/{total}")
        if total > 0:
            self.total_progress.setValue(100)

    def _on_download_finished(self) -> None:
        self.fetch_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _set_combo_by_data(self, combo: QComboBox, value: str) -> None:
        for i in range(combo.count()):
            if str(combo.itemData(i)) == value:
                combo.setCurrentIndex(i)
                return

    def _set_combo_by_text(self, combo: QComboBox, text: str) -> None:
        idx = combo.findText(text)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _collect_settings(self) -> dict[str, Any]:
        return {
            "output_path": self.output_path.text().strip(),
            "mode": str(self.mode_combo.currentData()),
            "custom_format": self.custom_format.text().strip(),
            "audio_codec": self.audio_codec.currentText(),
            "video_container": self.video_container.currentText(),
            "output_template": self.output_template.text().strip(),
            "cookie_browser": str(self.cookie_browser.currentData()),
            "cookie_file": self.cookie_file_input.text().strip(),
            "impersonate_client": str(self.impersonate_combo.currentData() or ""),
            "youtube_player_client": self.youtube_player_client_input.text().strip(),
            "proxy": self.proxy_input.text().strip(),
            "ffmpeg_location": self.ffmpeg_location.text().strip(),
            "allow_playlist": self.playlist_checkbox.isChecked(),
            "task_retry": self.task_retry_spin.value(),
            "url_text": self.url_input.toPlainText(),
            "ext_filter": self.ext_filter.currentText(),
            "vcodec_filter": self.vcodec_filter.currentText(),
            "audio_only_filter": self.audio_only_filter.isChecked(),
        }

    def _save_settings(self) -> None:
        _write_json(SETTINGS_FILE, self._collect_settings())

    def _load_settings(self) -> None:
        s = _read_json(SETTINGS_FILE, {})
        if not s:
            return
        self.output_path.setText(s.get("output_path") or self.output_path.text())
        self._set_combo_by_data(self.mode_combo, str(s.get("mode") or "video"))
        self.custom_format.setText(str(s.get("custom_format") or ""))
        self._set_combo_by_text(self.audio_codec, str(s.get("audio_codec") or "mp3"))
        self._set_combo_by_text(self.video_container, str(s.get("video_container") or "mp4"))
        self.output_template.setText(s.get("output_template") or self.output_template.text())
        self._set_combo_by_data(self.cookie_browser, str(s.get("cookie_browser") or "none"))
        self.cookie_file_input.setText(str(s.get("cookie_file") or ""))
        self._set_combo_by_data(self.impersonate_combo, str(s.get("impersonate_client") or ""))
        self.youtube_player_client_input.setText(str(s.get("youtube_player_client") or ""))
        self.proxy_input.setText(str(s.get("proxy") or ""))
        self.ffmpeg_location.setText(str(s.get("ffmpeg_location") or ""))
        self.playlist_checkbox.setChecked(bool(s.get("allow_playlist", False)))
        self.task_retry_spin.setValue(int(s.get("task_retry", 1)))
        self.url_input.setPlainText(str(s.get("url_text") or ""))
        self._set_combo_by_text(self.ext_filter, str(s.get("ext_filter") or "\u5168\u90e8\u6269\u5c55\u540d"))
        self._set_combo_by_text(self.vcodec_filter, str(s.get("vcodec_filter") or "\u5168\u90e8\u7f16\u7801"))
        self.audio_only_filter.setChecked(bool(s.get("audio_only_filter", False)))
        self._normalize_network_fields()
        self._update_mode_state()

    def _center_on_screen(self) -> None:
        screen = self.screen() or QApplication.primaryScreen()
        if not screen:
            return
        rect = screen.availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(rect.center())
        self.move(frame.topLeft())

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._render_thumbnail()
        self._position_thumbnail_play_button()

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        if not self._startup_centered:
            self._center_on_screen()
            self._startup_centered = True
        if os.name == "nt" and not self._glass_effect_applied:
            _enable_windows_glass_effect(self)
            self._glass_effect_applied = True

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._save_settings()
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(2500)
        if self.fetch_thread and self.fetch_thread.isRunning():
            self.fetch_thread.wait(1200)
        super().closeEvent(event)


def run_app() -> None:
    if os.name == "nt":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WINDOWS_APP_USER_MODEL_ID)
        except Exception:
            pass

    app = QApplication.instance() or QApplication([])
    app_icon = QIcon(APP_ICON_PATH)
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    window = VideoDownloaderWindow()
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)

    window.show()
    app.exec()

