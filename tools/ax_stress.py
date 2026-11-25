"""Force Flutter to build its semantics tree, then stress it.

Flutter's Windows embedder turns semantics on when it receives
WM_GETOBJECT / OBJID_CLIENT with the UIA root object id. Once an AT client
holds a reference, every navigation reshapes the tree — which is exactly when
`accessibility_bridge.cc(114) Failed to update ui::AXTree` floods.

Usage:
  python tools/ax_stress.py --seconds 40
  python tools/ax_stress.py --seconds 40 --navigate     (also click the sidebar)
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import subprocess
import sys
import time

user32 = ctypes.WinDLL("user32", use_last_error=True)

WM_GETOBJECT = 0x003D
OBJID_CLIENT = 0xFFFFFFFC
UiaRootObjectId = -25


def pids(name):
    text = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {name}.exe", "/FO", "CSV", "/NH"],
        capture_output=True, text=True, encoding="mbcs", errors="replace",
    ).stdout
    out = set()
    for line in text.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) >= 2 and parts[1].isdigit():
            out.add(int(parts[1]))
    return out


def find_window(proc):
    target = pids(proc)
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(hwnd, _l):
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in target and user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(max(length + 1, 2))
            user32.GetWindowTextW(hwnd, buf, len(buf))
            found.append((hwnd, buf.value))
        return True

    user32.EnumWindows(cb, 0)
    return found


def stim(hwnd):
    """The call Flutter listens for to enable its accessibility bridge."""
    user32.SendMessageW(hwnd, WM_GETOBJECT, ctypes.c_void_p(0),
                        ctypes.c_void_p(OBJID_CLIENT))
    # UIA root: what UI Automation clients actually ask for.
    user32.SendMessageW(hwnd, WM_GETOBJECT, ctypes.c_void_p(0),
                        ctypes.c_void_p(UiaRootObjectId))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--process", default="lazer_nextgen")
    ap.add_argument("--seconds", type=int, default=40)
    ap.add_argument("--navigate", action="store_true")
    args = ap.parse_args()

    windows = [w for w in find_window(args.process) if w[1].strip() == "Lazer"]
    if not windows:
        windows = find_window(args.process)
    if not windows:
        print("no window", file=sys.stderr)
        return 2
    hwnd, title = windows[0]
    print(f"window {hwnd} {title!r}")

    for _ in range(3):
        stim(hwnd)
        time.sleep(.3)

    clicks = ["48,162", "48,208", "48,254", "48,124"]
    deadline = time.time() + args.seconds
    index = 0
    while time.time() < deadline:
        stim(hwnd)
        if args.navigate:
            x, y = (int(v) for v in clicks[index % len(clicks)].split(","))
            subprocess.run(
                ["python", "tools/click.py", "--process", args.process,
                 "--title", "Lazer", "--at", f"{x},{y}"],
                capture_output=True, cwd="E:\\projects\\lazer_early_development_theme",
            )
            index += 1
        time.sleep(1.2)
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
