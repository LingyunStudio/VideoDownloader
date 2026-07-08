"""软件自身更新：检查 GitHub release tag，下载新安装包并静默安装。

检查 https://api.github.com/repos/LingyunStudio/VideoDownloader/releases/latest，
比对 tag 与 app_version.APP_VERSION。有新版则下载 VideoDownloader_Setup.exe 到
%APPDATA%/VideoDownloader/updates/app/，调用 install_and_restart 用 ShellExecute
"runas" 触发 UAC 静默安装（不传 /DIR=，由 Inno UsePreviousAppDir 装回原目录）。
"""
from __future__ import annotations

import json
import os
import urllib.request

from PyQt6.QtCore import QThread, pyqtSignal

from downloader.app_version import APP_VERSION
from downloader.updater import data_dir, is_newer

API_URL = "https://api.github.com/repos/LingyunStudio/VideoDownloader/releases/latest"
ASSET_NAME = "VideoDownloader_Setup.exe"
_UA = "VideoDownloader/2.1"


def _strip_v(tag: str) -> str:
    return tag[1:] if tag and tag[0] in ("v", "V") else tag


def _fetch_latest() -> tuple[str, str]:
    """返回 (tag, setup_url)；网络失败返回 ("", "")。"""
    try:
        req = urllib.request.Request(
            API_URL, headers={"User-Agent": _UA, "Accept": "application/json"}
        )
        data = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())
        tag = (data.get("tag_name") or "").strip()
        url = ""
        for a in data.get("assets", []) or []:
            if a.get("name") == ASSET_NAME:
                url = a.get("browser_download_url") or ""
                break
        return tag, url
    except Exception:
        return "", ""


class AppUpdateWorker(QThread):
    """检查/下载软件更新。mode="check" 仅查询；mode="update" 下载安装包。"""

    check_done = pyqtSignal(str, str, bool, str)  # current, latest, needs_update, setup_url
    progress = pyqtSignal(int, int)               # downloaded, total
    done = pyqtSignal(str)                        # installer path
    failed = pyqtSignal(str)

    def __init__(self, mode: str = "check", parent=None):
        super().__init__(parent)
        self._mode = mode

    def run(self):
        if self._mode == "check":
            self._do_check()
        else:
            self._do_update()

    def _do_check(self):
        cur = APP_VERSION
        tag, url = _fetch_latest()
        latest = _strip_v(tag)
        needs = is_newer(latest, cur) if latest else False
        self.check_done.emit(cur, latest, needs, url)

    def _do_update(self):
        try:
            tag, url = _fetch_latest()
            if not url:
                self.failed.emit("无法获取下载地址，请检查网络或确认 Release 已上传安装包")
                return
            upd = os.path.join(data_dir(), "updates", "app")
            os.makedirs(upd, exist_ok=True)
            dest = os.path.join(upd, ASSET_NAME)
            self._download(url, dest)
            self.done.emit(dest)
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


def install_and_restart(installer_path: str) -> None:
    """以管理员权限静默启动安装包并退出当前进程（让安装包接管升级+重启）。"""
    import ctypes
    import sys
    from PyQt6.QtWidgets import QApplication

    params = "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART"
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", installer_path, params, None, 0)
    if rc <= 32:
        raise RuntimeError("启动安装包失败（用户取消 UAC 或其它错误）")
    app = QApplication.instance()
    if app is not None:
        app.quit()
    else:
        sys.exit(0)
