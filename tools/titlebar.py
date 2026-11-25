"""Point the running client at the classic title bar (or back to inline).

`lazer_title_bar_style` 存在 shared_preferences 里，值是 `inline` / `classic`。
改完要重启客户端才生效 —— 这个脚本只写偏好，不重启进程。

  python tools/titlebar.py --style classic
  python tools/titlebar.py --show
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

PREFS = (
    pathlib.Path(os.environ["APPDATA"])
    / "dev.naominet"
    / "lazer_nextgen"
    / "shared_preferences.json"
)
KEY = "flutter.lazer_title_bar_style"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", choices=("inline", "classic"))
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args(argv)

    data = json.loads(PREFS.read_text(encoding="utf-8"))
    if args.style:
        data[KEY] = args.style
        PREFS.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"{KEY} = {args.style}")
        return 0
    print(f"{KEY} = {data.get(KEY)!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
