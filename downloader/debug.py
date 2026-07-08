"""轻量追踪日志：写入 %APPDATA%\\VideoDownloader\\trace.log，用于诊断 frozen（无 console）模式下的崩溃位置。"""
from __future__ import annotations

import os
import time

_LOG = None


def _path() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "VideoDownloader", "trace.log")


def trace(msg: str) -> None:
    try:
        p = _path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        line = f"{time.strftime('%H:%M:%S')}  {msg}\n"
        with open(p, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def trace_reset() -> None:
    try:
        p = _path()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write("=== trace reset ===\n")
    except Exception:
        pass
