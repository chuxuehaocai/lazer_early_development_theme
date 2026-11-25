#!/usr/bin/env python3
"""Run the whole toolchain against this repository in one shot.

Stages (stop-on-failure is off: you see every stage's verdict):
  1. manifest check_manifest.py          plugin/manifest.json 逐字段
  2. package  check_package.py           plugin/ 可打包性
  3. lua      check_lua.py               plugin/**/*.lua AST + 静态检查
  4. zip      build_zip.py               产出 build/<id>-<version>.zip 与 SHA-256

纯主题插件：没有静态前端、没有本地服务、没有页面与设置项，因此也没有
icons / corner / shots 三个阶段。

Usage:
  python tools\\verify.py             # 只校验 + 打包
  python tools\\verify.py --json      # 末尾打印机器可读汇总
Exit code 1 when any stage fails.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

TOOLS = pathlib.Path(__file__).resolve().parent
REPO = TOOLS.parent
PY = sys.executable


def stage(title: str, args: list[str]) -> tuple[str, int, str]:
    print(f"\n=== {title} " + "=" * max(0, 66 - len(title)))
    runner = ["node", *args] if args and args[0].endswith(".js") else [PY, *args]
    label = "node" if runner[0] == "node" else "python"
    process = subprocess.run(runner, cwd=str(REPO))
    return title, process.returncode, f"{label} {' '.join(args)}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run every plugin check.")
    parser.add_argument("--json", action="store_true", help="打印 JSON 汇总")
    args = parser.parse_args(argv)

    plan = [
        ("manifest", [str(TOOLS / "check_manifest.py")]),
        ("package", [str(TOOLS / "check_package.py")]),
        ("lua", [str(TOOLS / "check_lua.py")]),
        ("zip", [str(TOOLS / "build_zip.py")]),
    ]

    results = [stage(title, cmd) for title, cmd in plan]

    print("\n=== summary " + "=" * 55)
    for title, code, label in results:
        mark = "PASS" if code == 0 else "FAIL"
        print(f"  {mark}  {title:<9} exit={code}  {label}")
    failed = [title for title, code, _ in results if code != 0]
    if failed:
        print(f"\n{len(results) - len(failed)}/{len(results)} 个阶段通过  ->  FAIL {', '.join(failed)}")
    else:
        print(f"\n{len(results)}/{len(results)} 个阶段通过  ->  PASS")
    if args.json:
        print(json.dumps(
            [{"stage": t, "exit": c, "command": l} for t, c, l in results],
            ensure_ascii=False,
        ))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
