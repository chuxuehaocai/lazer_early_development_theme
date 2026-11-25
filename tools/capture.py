"""抓取指定进程主窗口的截图（Windows 真值对照用）。

用法: python tools/capture.py --process lazer_nextgen --out shots/ref-home.png
实现: EnumWindows 找窗口 → PrintWindow(PW_RENDERFULLCONTENT) 抓位图 → Pillow 存 PNG。
PrintWindow 对 Flutter(D3D/ANGLE) 窗口通常有效；若得到全黑，再加 --foreground 先置前
并用 BitBlt 抓屏幕。
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import sys

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("需要 Pillow: python -m pip install pillow", file=sys.stderr)
    raise SystemExit(2)

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

PW_RENDERFULLCONTENT = 0x00000002
SRCCOPY = 0x00CC0020


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


def process_pids(name):
    import subprocess
    text = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}.exe", "/FO", "CSV", "/NH"],
                          capture_output=True, text=True, encoding="mbcs", errors="replace").stdout
    pids = set()
    for line in text.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) >= 2 and parts[1].isdigit():
            pids.add(int(parts[1]))
    if not pids:
        pids = {int(p) for p in os.popen(f'tasklist /FI "IMAGENAME eq {name}.exe" /FO CSV /NH').read().split('","')[1:2] if p.isdigit()}
    return pids


def capture(hwnd, out, foreground=False):
    if foreground:
        user32.ShowWindow(hwnd, 9)
        user32.SetForegroundWindow(hwnd)
        ctypes.windll.kernel32.Sleep(500)
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    if w <= 0 or h <= 0:
        raise SystemExit(f"bad rect {w}x{h}")
    hdc = user32.GetWindowDC(hwnd)
    mem = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(mem, bmp)

    ok = user32.PrintWindow(hwnd, mem, PW_RENDERFULLCONTENT)
    payload = None
    if ok:
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32),
                        ("biHeight", ctypes.c_int32), ("biPlanes", ctypes.c_uint16),
                        ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                        ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32),
                        ("biYPelsPerMeter", ctypes.c_int32), ("biClrUsed", ctypes.c_uint32),
                        ("biClrImportant", ctypes.c_uint32)]

        bi = BITMAPINFOHEADER()
        bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bi.biWidth = w
        bi.biHeight = -h  # top-down
        bi.biPlanes = 1
        bi.biBitCount = 32
        bi.biCompression = 0
        buf = ctypes.create_string_buffer(w * h * 4)
        got = gdi32.GetDIBits(mem, bmp, 0, h, buf, ctypes.byref(bi), 0)
        if got:
            payload = Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1).convert("RGB")
    if payload is None or payload.getbbox() is None:
        # 回退：直接从屏幕抓窗口区域
        if not foreground:
            user32.ShowWindow(hwnd, 9)
            user32.SetForegroundWindow(hwnd)
            ctypes.windll.kernel32.Sleep(600)
        screen = user32.GetDC(0)
        mem2 = gdi32.CreateCompatibleDC(screen)
        bmp2 = gdi32.CreateCompatibleBitmap(screen, w, h)
        gdi32.SelectObject(mem2, bmp2)
        gdi32.BitBlt(mem2, 0, 0, w, h, screen, rect.left, rect.top, SRCCOPY)
        class BIH(ctypes.Structure):
            _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32),
                        ("biHeight", ctypes.c_int32), ("biPlanes", ctypes.c_uint16),
                        ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                        ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32),
                        ("biYPelsPerMeter", ctypes.c_int32), ("biClrUsed", ctypes.c_uint32),
                        ("biClrImportant", ctypes.c_uint32)]
        bi2 = BIH()
        bi2.biSize = ctypes.sizeof(BIH)
        bi2.biWidth, bi2.biHeight = w, -h
        bi2.biPlanes, bi2.biBitCount, bi2.biCompression = 1, 32, 0
        buf2 = ctypes.create_string_buffer(w * h * 4)
        gdi32.GetDIBits(mem2, bmp2, 0, h, buf2, ctypes.byref(bi2), 0)
        payload = Image.frombuffer("RGBA", (w, h), buf2, "raw", "BGRA", 0, 1).convert("RGB")
        gdi32.DeleteObject(bmp2)
        gdi32.DeleteDC(mem2)
        user32.ReleaseDC(0, screen)
        source = "screen"
    else:
        source = "printwindow"
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mem)
    user32.ReleaseDC(hwnd, hdc)

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    payload.save(out)
    colors = payload.getcolors(maxcolors=1 << 20) or []
    print(f"saved {out} {w}x{h} source={source} distinct={len(colors)}")
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--process", default="lazer_nextgen")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default=None)
    ap.add_argument("--foreground", action="store_true")
    args = ap.parse_args()

    pids = process_pids(args.process)
    if not pids:
        raise SystemExit(f"no process named {args.process}")
    cands = [w for w in windows() if w[1] in pids and w[3]]
    if args.title:
        exact = [w for w in cands if w[2].strip() == args.title]
        cands = exact or [w for w in cands if args.title in w[2]] or cands
    if not cands:
        raise SystemExit("no visible window for process")

    def area(item):
        rect = RECT()
        user32.GetWindowRect(item[0], ctypes.byref(rect))
        return max(0, rect.right - rect.left) * max(0, rect.bottom - rect.top)

    hwnd, pid, title, _ = max(cands, key=area)
    print(f"window hwnd={hwnd} pid={pid} title={title!r}")
    capture(hwnd, args.out, foreground=args.foreground)


if __name__ == "__main__":
    main()
