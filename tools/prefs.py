"""Set one key in the client's shared_preferences.json (UTF-8 safe).

The file is a flat JSON object of `flutter.<key>` -> value. Writing it with
PowerShell's ConvertTo-Json re-escapes CJK text and blows up on the large
`lazer_recent_tracks_v1` string, so this uses json + ensure_ascii=False.

Usage:
  python tools/prefs.py --get flutter.lazer_theme_mode
  python tools/prefs.py --set flutter.lazer_theme_mode light
  python tools/prefs.py --set flutter.lazer_corner_strength 0.0 --float
  python tools/prefs.py --dump-corner
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

PREFS = pathlib.Path(os.environ["APPDATA"]) / "dev.naominet" / "lazer_nextgen" / "shared_preferences.json"
CORNER_KEYS = (
    "flutter.lazer_corner_follows_theme",
    "flutter.lazer_corner_strength",
)


def load() -> dict:
    return json.loads(PREFS.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    PREFS.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--get")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"))
    parser.add_argument("--float", action="store_true", help="存成浮点数（滑块值）")
    parser.add_argument("--int", action="store_true", help="存成整数")
    parser.add_argument("--bool", action="store_true", help="true/false")
    parser.add_argument("--unset", action="store_true", help="删除这个键")
    parser.add_argument("--dump-corner", action="store_true")
    args = parser.parse_args(argv)

    if not PREFS.exists():
        print(f"missing {PREFS}")
        return 1

    if args.get:
        print(load().get(args.get))
        return 0

    if args.dump_corner:
        data = load()
        for key in CORNER_KEYS:
            print(f"{key} = {data.get(key)!r}")
        return 0

    if not args.set:
        parser.error("需要 --get / --set / --dump-corner")

    key, raw = args.set
    data = load()
    if args.unset:
        data.pop(key, None)
        save(data)
        print(f"unset {key}")
        return 0
    if args.bool:
        value: object = raw.lower() in ("1", "true", "yes", "on")
    elif args.int:
        value = int(raw)
    elif args.float:
        value = float(raw)
    else:
        value = raw
    data[key] = value
    save(data)
    print(f"{key} = {value!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
