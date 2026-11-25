"""Window geometry + clicks for the running client (companion to capture.py).

`click.py` picks the largest window of the process, which can be the floating
lyrics overlay. This one insists on an exact title and always prints the rect it
used, so a click that lands somewhere unexpected is obvious in the output.

Usage:
  python tools/ui.py --rect                      # 打印主窗口位置与大小
  python tools/ui.py --reset                     # 移到 (60,40) 并设成 1280x720
  python tools/ui.py --click 81,671              # 窗口内坐标点击（自动置前）
  python tools/ui.py --click 81,671 --double
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import subprocess
import sys
import time

user32 = ctypes.WinDLL("user32", use_last_error=True)

SW_RESTORE = 9
HWND_TOP = 0
SWP_SHOWWINDOW = 0x0040


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def pids_of(name: str) -> set[int]:
    text = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {name}.exe", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
    ).stdout
    pids: set[int] = set()
    for line in text.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) >= 2 and parts[1].isdigit():
            pids.add(int(parts[1]))
    return pids


def find(process: str, title: str):
    pids = pids_of(process)
    found: list[tuple[int, int, str]] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(hwnd, _lparam):
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(max(length + 1, 2))
        user32.GetWindowTextW(hwnd, buf, len(buf))
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids and user32.IsWindowVisible(hwnd):
            found.append((hwnd, pid.value, buf.value))
        return True

    user32.EnumWindows(cb, 0)
    for hwnd, pid, text in found:
        if text.strip() == title:
            return hwnd, pid, text
    raise SystemExit(f"no visible window titled {title!r}; saw {[t for _, _, t in found]}")


def rect_of(hwnd: int) -> RECT:
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--process", default="lazer_nextgen")
    parser.add_argument("--title", default="Lazer")
    parser.add_argument("--rect", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--click")
    parser.add_argument("--double", action="store_true")
    args = parser.parse_args(argv)

    hwnd, pid, title = find(args.process, args.title)
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.25)

    if args.reset:
        user32.SetWindowPos(hwnd, HWND_TOP, 60, 40, 1280, 760, SWP_SHOWWINDOW)
        time.sleep(0.4)

    rect = rect_of(hwnd)
    print(
        f"hwnd={hwnd} pid={pid} title={title!r} "
        f"rect=({rect.left},{rect.top})-({rect.right},{rect.bottom}) "
        f"size={rect.right - rect.left}x{rect.bottom - rect.top}"
    )

    if args.click:
        x, y = (int(v) for v in args.click.split(","))
        sx, sy = rect.left + x, rect.top + y
        user32.SetCursorPos(sx, sy)
        time.sleep(0.12)
        for _ in range(2 if args.double else 1):
            user32.mouse_event(0x0002, 0, 0, 0, 0)
            time.sleep(0.04)
            user32.mouse_event(0x0004, 0, 0, 0, 0)
            time.sleep(0.12)
        print(f"clicked window({x},{y}) -> screen({sx},{sy})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
