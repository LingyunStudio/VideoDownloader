"""yt-dlp 运行时更新。

yt-dlp 冻结进 exe（collect_all 追踪其全部 import）。更新时从 GitHub releases 下载
官方源码 tar.gz，解压到用户数据目录，写入标记文件。启动时若标记存在，注册一个
meta_path 查找器到 sys.meta_path 最前，优先从用户目录加载 yt_dlp 及其子模块，
覆盖冻结副本——meta_path 早于 PyInstaller 的冻结导入器，故能生效。
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import re
import shutil
import sys
import tarfile
import urllib.request
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal

APP_NAME = "VideoDownloader"
TARBALL = "yt-dlp.tar.gz"
API_URL = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
RAW_VER_URL = "https://raw.githubusercontent.com/yt-dlp/yt-dlp/master/yt_dlp/version.py"
_UA = APP_NAME + "/1.0"


# ---------- 纯函数（可在 QApplication 之前调用） ----------

def data_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, APP_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _marker_file() -> str:
    return os.path.join(data_dir(), "ytdlp_update_path.txt")


def current_override_path() -> Optional[str]:
    """读取更新标记，返回当前应使用的 yt_dlp 包父目录（已校验存在）。"""
    try:
        with open(_marker_file(), encoding="utf-8") as f:
            p = f.read().strip()
    except OSError:
        return None
    if p and os.path.isdir(os.path.join(p, "yt_dlp")):
        return p
    return None


class _YtDlpOverrideFinder:
    """meta_path 查找器：从指定目录加载 yt_dlp / yt_dlp.* ，优先于冻结导入器。

    顶层包 yt_dlp 用 spec_from_file_location 直接构造，确保 __path__ 指向 override
    目录；子模块 yt_dlp.* 必须用 Python 传入的 path（父包 __path__）查找，而不是
    self._path（self._path 是「包含 yt_dlp 的目录」，在其中找不到 version 等子模块，
    会落到冻结导入器加载旧版子模块，导致版本号仍显示旧值）。
    """

    def __init__(self, path: str):
        self._path = path
        self._pkg = os.path.join(path, "yt_dlp")

    def find_spec(self, name, path=None, target=None):
        if name == "yt_dlp":
            init = os.path.join(self._pkg, "__init__.py")
            if os.path.isfile(init):
                return importlib.util.spec_from_file_location(
                    "yt_dlp", init, submodule_search_locations=[self._pkg]
                )
            return None
        if name.startswith("yt_dlp."):
            search = path or [self._pkg]
            return importlib.machinery.PathFinder.find_spec(name, search)
        return None


def apply_override_at_startup() -> Optional[str]:
    """在 import yt_dlp 之前调用：若存在更新标记，注册覆盖查找器。"""
    p = current_override_path()
    if p and not any(isinstance(f, _YtDlpOverrideFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, _YtDlpOverrideFinder(p))
    return p


def get_current_version() -> str:
    try:
        import yt_dlp
        _trace_version_once(yt_dlp)
        return yt_dlp.version.__version__
    except Exception:
        return "0"


_VERSION_TRACED = False


def _trace_version_once(mod) -> None:
    global _VERSION_TRACED
    if _VERSION_TRACED:
        return
    _VERSION_TRACED = True
    try:
        from downloader.debug import trace
        v = getattr(getattr(mod, "version", None), "__version__", "?")
        trace("yt_dlp active: v%s @ %s" % (v, getattr(mod, "__file__", "?")))
    except Exception:
        pass


def get_active_source() -> str:
    """返回当前 yt_dlp 来源描述，供 UI 显示。"""
    if current_override_path():
        return "已更新（用户目录）"
    if getattr(sys, "frozen", False):
        return "内置"
    return "系统安装"


def _parse_ver(s: str) -> tuple:
    parts = []
    for tok in re.split(r"[.\-+ ]", s or ""):
        m = re.match(r"(\d+)", tok)
        parts.append(int(m.group(1)) if m else 0)
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    return _parse_ver(latest) > _parse_ver(current)


def _fetch_latest() -> tuple[str, str]:
    """返回 (tag, tar_url)；API 失败则回退 raw version.py + 拼接 URL。"""
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": _UA, "Accept": "application/json"})
        data = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())
        tag = (data.get("tag_name") or "").strip()
        url = ""
        for a in data.get("assets", []) or []:
            if a.get("name") == TARBALL:
                url = a.get("browser_download_url") or ""
                break
        if tag and url:
            return tag, url
    except Exception:
        pass
    try:
        ver = urllib.request.urlopen(
            urllib.request.Request(RAW_VER_URL, headers={"User-Agent": _UA}), timeout=25
        ).read().decode()
        m = re.search(r"__version__\s*=\s*['\"]([^'\"]+)", ver)
        if m:
            v = m.group(1)
            return v, f"https://github.com/yt-dlp/yt-dlp/releases/download/{v}/{TARBALL}"
    except Exception:
        pass
    return "", ""


def _read_pkg_version(pkg_root: str) -> str:
    try:
        with open(os.path.join(pkg_root, "yt_dlp", "version.py"), encoding="utf-8") as f:
            m = re.search(r"__version__\s*=\s*['\"]([^'\"]+)", f.read())
            return m.group(1) if m else "?"
    except OSError:
        return "?"


# ---------- 后台工作线程 ----------

class UpdateWorker(QThread):
    """检查 / 下载更新。mode="check" 仅查询；mode="update" 下载并安装。"""

    check_done = pyqtSignal(str, str, bool, str)  # current, latest, needs_update, tar_url
    progress = pyqtSignal(int, int)               # downloaded, total（total=0 未知）
    update_done = pyqtSignal(str)                  # 新版本号
    update_failed = pyqtSignal(str)

    def __init__(self, mode: str = "check", parent=None):
        super().__init__(parent)
        self._mode = mode

    def run(self):
        if self._mode == "check":
            self._do_check()
        else:
            self._do_update()

    def _do_check(self):
        cur = get_current_version()
        tag, url = _fetch_latest()
        self.check_done.emit(cur, tag, is_newer(tag, cur) if tag else False, url)

    def _do_update(self):
        try:
            tag, url = _fetch_latest()
            if not url:
                self.update_failed.emit("无法获取下载地址，请检查网络")
                return
            upd = os.path.join(data_dir(), "updates")
            os.makedirs(upd, exist_ok=True)
            tgz = os.path.join(upd, f"yt-dlp-{tag}.tar.gz")
            self._download(url, tgz)

            ext = os.path.join(upd, f"yt-dlp-{tag}")
            if os.path.exists(ext):
                shutil.rmtree(ext, ignore_errors=True)
            with tarfile.open(tgz) as t:
                t.extractall(ext)

            pkg_root = None
            for name in os.listdir(ext):
                cand = os.path.join(ext, name)
                if os.path.isdir(os.path.join(cand, "yt_dlp")):
                    pkg_root = cand
                    break
            if not pkg_root:
                self.update_failed.emit("解压后未找到 yt_dlp 包")
                return

            new_ver = _read_pkg_version(pkg_root)
            with open(_marker_file(), "w", encoding="utf-8") as f:
                f.write(pkg_root)
            self.update_done.emit(new_ver)
        except Exception as e:
            self.update_failed.emit(f"{type(e).__name__}: {e}")

    def _download(self, url: str, dest: str):
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as out:
            total = int(resp.headers.get("Content-Length") or 0)
            dl = 0
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out.write(chunk)
                dl += len(chunk)
                self.progress.emit(dl, total)
