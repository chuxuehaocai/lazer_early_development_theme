"""Mouse wheel / drag over a window (companion to click.py and capture.py).

  python tools/scroll.py --process lazer_nextgen --at 760,450 --ticks -6
  python tools/scroll.py --process lazer_nextgen --drag 560,600 660,600

`--ticks` is in wheel notches: negative scrolls down (content moves up).
`--drag` presses at the first point, moves in 12 steps, releases — enough for
Flutter sliders and scrollable panes.
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import time

user32 = ctypes.WinDLL("user32", use_last_error=True)


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def windows():
    out = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(hwnd, _lparam):
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(max(length + 1, 2))
        user32.GetWindowTextW(hwnd, buf, len(buf))
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        out.append((hwnd, pid.value, buf.value, bool(user32.IsWindowVisible(hwnd))))
        return True

    user32.EnumWindows(cb, 0)
    return out


def pids_of(name):
    import subprocess
    text = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}.exe", "/FO", "CSV", "/NH"],
                          capture_output=True, text=True, encoding="mbcs", errors="replace").stdout
    pids = set()
    for line in text.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) >= 2 and parts[1].isdigit():
            pids.add(int(parts[1]))
    return pids


def find_window(process):
    pids = pids_of(process)
    cands = [w for w in windows() if w[1] in pids and w[3]]

    def area(item):
        rect = RECT()
        user32.GetWindowRect(item[0], ctypes.byref(rect))
        return max(0, rect.right - rect.left) * max(0, rect.bottom - rect.top)

    return max(cands, key=area)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--process", default="lazer_nextgen")
    ap.add_argument("--at", default="760,450")
    ap.add_argument("--ticks", type=int, default=-5)
    ap.add_argument("--drag", nargs=2, metavar=("FROM", "TO"))
    ap.add_argument("--steps", type=int, default=14)
    args = ap.parse_args()

    hwnd, _pid, title, _ = find_window(args.process)
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)

    if args.drag:
        x0, y0 = (int(v) for v in args.drag[0].split(","))
        x1, y1 = (int(v) for v in args.drag[1].split(","))
        user32.SetCursorPos(rect.left + x0, rect.top + y0)
        time.sleep(0.15)
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.1)
        for step in range(1, args.steps + 1):
            x = rect.left + int(x0 + (x1 - x0) * step / args.steps)
            y = rect.top + int(y0 + (y1 - y0) * step / args.steps)
            user32.SetCursorPos(x, y)
            time.sleep(0.02)
        time.sleep(0.1)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
        print(f"dragged ({x0},{y0}) -> ({x1},{y1}) hwnd={hwnd}")
        return

    x, y = (int(v) for v in args.at.split(","))
    user32.SetCursorPos(rect.left + x, rect.top + y)
    time.sleep(0.15)
    user32.mouse_event(0x0800, 0, 0, args.ticks * 120, 0)  # MOUSEEVENTF_WHEEL
    print(f"wheel {args.ticks} at ({x},{y}) hwnd={hwnd}")


if __name__ == "__main__":
    main()
