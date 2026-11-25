"""向指定窗口发送鼠标点击 / 键盘输入（本地 UI 自动化，配合 capture.py 使用）。

用法:
  python tools/click.py --process lazer_nextgen --title Lazer --at 48,640
  python tools/click.py --process lazer_nextgen --at 48,640 --double
  python tools/click.py --process lazer_nextgen --text "hello"        # 输入文本（Unicode）
  python tools/click.py --process lazer_nextgen --key 0x0D            # 发送虚拟键（回车）
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import sys
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


def find_window(process, title):
    pids = pids_of(process)
    cands = [w for w in windows() if w[1] in pids and w[3]]
    if title:
        exact = [w for w in cands if w[2].strip() == title]
        cands = exact or [w for w in cands if title in w[2]] or cands
    if not cands:
        raise SystemExit("no window")

    def area(item):
        rect = RECT()
        user32.GetWindowRect(item[0], ctypes.byref(rect))
        return max(0, rect.right - rect.left) * max(0, rect.bottom - rect.top)

    return max(cands, key=area)


def click(hwnd, x, y, double=False):
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    sx, sy = rect.left + x, rect.top + y
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    user32.SetCursorPos(int(sx), int(sy))
    time.sleep(0.1)
    for _ in range(2 if double else 1):
        user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
        time.sleep(0.03)
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
        time.sleep(0.12)
    print(f"clicked ({sx},{sy}) hwnd={hwnd}")


def send_text(hwnd, text):
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    KEYEVENTF_UNICODE = 0x0004
    for ch in text:
        for down in (True, False):
            user32.keybd_event(0, 0, 0, 0) if False else None
        # use SendInput-free path: VkKeyScan for ASCII only; Unicode via keybd_event is unreliable.
        code = user32.VkKeyScanW(ord(ch))
        if code == -1:
            print(f"skip char {ch!r}", file=sys.stderr)
            continue
        vk = code & 0xFF
        shift = (code >> 8) & 0xFF
        if shift & 1:
            user32.keybd_event(0x10, 0, 0, 0)
        user32.keybd_event(vk, 0, 0, 0)
        user32.keybd_event(vk, 0, 2, 0)
        if shift & 1:
            user32.keybd_event(0x10, 0, 2, 0)
        time.sleep(0.02)
    print(f"typed {len(text)} chars")


def send_key(hwnd, vk):
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.15)
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, 2, 0)
    print(f"key {vk}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--process", default="lazer_nextgen")
    ap.add_argument("--title", default=None)
    ap.add_argument("--at", default=None, help="窗口内坐标 x,y")
    ap.add_argument("--double", action="store_true")
    ap.add_argument("--text", default=None)
    ap.add_argument("--key", default=None, help="虚拟键码，如 0x0D")
    args = ap.parse_args()

    hwnd, pid, title, _ = find_window(args.process, args.title)
    print(f"window hwnd={hwnd} pid={pid} title={title!r}")
    if args.at:
        x, y = (int(v) for v in args.at.split(","))
        click(hwnd, x, y, args.double)
    if args.text:
        send_text(hwnd, args.text)
    if args.key:
        send_key(hwnd, int(args.key, 0))


if __name__ == "__main__":
    main()
