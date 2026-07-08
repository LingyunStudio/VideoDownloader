"""ffmpeg 运行时管理。

打包后程序装在 Program Files（只读），不能用 static_ffmpeg 默认的「下载到包目录」。
改为：首次需要 ffmpeg 时，下载到 %APPDATA%\\VideoDownloader\\ffmpeg\\（可写），
并加入 PATH / 传给 yt-dlp 的 ffmpeg_location。

开发模式（未冻结）仍走 static_ffmpeg（conda 环境可写）。
"""
from __future__ import annotations

import os
import sys
import zipfile
import urllib.request
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

APP_NAME = "VideoDownloader"
# 复用 static_ffmpeg 的托管二进制（已知可用）
_PLATFORM_URL = {
    "win32": "https://github.com/zackees/ffmpeg_bins/raw/main/v8.0/win32.zip",
}
_UA = APP_NAME + "/1.0"


def ffmpeg_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, APP_NAME, "ffmpeg")
    os.makedirs(d, exist_ok=True)
    return d


def _platform_key() -> str:
    if sys.platform.startswith("win"):
        return "win32"
    if sys.platform == "darwin":
        return "darwin"
    return "linux"


def ffmpeg_url() -> str:
    return _PLATFORM_URL[_platform_key()]


def is_ready() -> bool:
    return os.path.isfile(os.path.join(ffmpeg_dir(), "ffmpeg.exe")) or os.path.isfile(
        os.path.join(ffmpeg_dir(), "ffmpeg")
    )


def ffmpeg_exe() -> Optional[str]:
    for name in ("ffmpeg.exe", "ffmpeg"):
        p = os.path.join(ffmpeg_dir(), name)
        if os.path.isfile(p):
            return p
    return None


class FFmpegSetupWorker(QThread):
    """下载并解压 ffmpeg 到用户数据目录。"""

    progress = pyqtSignal(int, int)  # downloaded, total
    done = pyqtSignal()
    failed = pyqtSignal(str)

    def run(self):
        try:
            import tempfile, shutil

            url = ffmpeg_url()
            tmp = tempfile.mkdtemp(prefix="vdl_ff_")
            zip_path = os.path.join(tmp, "ffmpeg.zip")
            self._download(url, zip_path)

            with zipfile.ZipFile(zip_path) as z:
                z.extractall(tmp)

            # 找到 ffmpeg / ffprobe 可执行文件（可能在子目录）
            targets = {}
            for root, _dirs, files in os.walk(tmp):
                for fn in files:
                    low = fn.lower()
                    if low in ("ffmpeg.exe", "ffmpeg") and "ffmpeg" not in targets:
                        targets["ffmpeg"] = os.path.join(root, fn)
                    elif low in ("ffprobe.exe", "ffprobe") and "ffprobe" not in targets:
                        targets["ffprobe"] = os.path.join(root, fn)

            if "ffmpeg" not in targets:
                self.failed.emit("解压后未找到 ffmpeg 可执行文件")
                return

            dest = ffmpeg_dir()
            for key, src in targets.items():
                dst = os.path.join(dest, os.path.basename(src))
                if os.path.abspath(src) != os.path.abspath(dst):
                    shutil.copy2(src, dst)

            shutil.rmtree(tmp, ignore_errors=True)
            self.done.emit()
        except Exception as e:
            self.failed.emit(f"{type(e).__name__}: {e}")

    def _download(self, url: str, dest: str):
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=300) as resp, open(dest, "wb") as out:
            total = int(resp.headers.get("Content-Length") or 0)
            dl = 0
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out.write(chunk)
                dl += len(chunk)
                self.progress.emit(dl, total)
