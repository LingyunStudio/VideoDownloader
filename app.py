"""VideoDownloader 入口。

运行：
    conda activate videodownload
    python app.py
"""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _crash_log_location():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "VideoDownloader", "crash.log")


def _write_crash(msg):
    try:
        p = _crash_log_location()
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(msg)
    except Exception:
        pass


# 包裹整个启动（含 import）：任何异常都写 crash.log 并弹窗，避免 GUI 模式静默闪退。
try:
    from downloader.debug import trace, trace_reset
    trace_reset()
    trace("app start, frozen=%s" % getattr(sys, "frozen", False))
    from downloader.updater import apply_override_at_startup
    apply_override_at_startup()
    trace("override applied")


    def _excepthook(exc_type, exc_value, exc_tb):
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        _write_crash("UNHANDLED (excepthook)\n" + msg)
        trace("EXCEPTHOOK: " + msg)
        try:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "程序出错", msg[-2000:])
        except Exception:
            pass


    sys.excepthook = _excepthook

    from ui.main_window import run
    trace("imports done")
except Exception:
    msg = "".join(traceback.format_exception(*sys.exc_info()))
    _write_crash("STARTUP CRASH\n" + msg)
    try:
        from downloader.debug import trace
        trace("STARTUP CRASH: " + msg)
    except Exception:
        pass
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "启动失败，详见 crash.log：\n\n" + msg[:800],
                                         "VideoDownloader", 0x10)
    except Exception:
        pass
    raise


if __name__ == "__main__":
    run()
