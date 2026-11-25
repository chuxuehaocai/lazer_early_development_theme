"""Dump the running client's semantics tree through the Dart VM service.

`Failed to update ui::AXTree, error: Nodes left pending by the update: 6 7 … 16`
names node ids, so we need the mapping id -> widget. The VM service can print it
(`ext.flutter.debugDumpSemanticsTreeInTraversalOrder`) while the app runs.

Usage:
  python tools/vm_semantics.py --uri http://127.0.0.1:50876/0alkgYnbRF0=/
  python tools/vm_semantics.py --auto          # 从 shots/*.out 里找最近一次启动的 URI
"""
from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import re
import sys

import websockets

TOOLS = pathlib.Path(__file__).resolve().parent
SHOTS = TOOLS.parent / "shots"


def find_uri() -> str:
    best: tuple[float, str] | None = None
    for path in SHOTS.glob("*.out"):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"(http://127\.0\.0\.1:\d+/[^\s]+/)", text)
        if match:
            stamp = path.stat().st_mtime
            if best is None or stamp > best[0]:
                best = (stamp, match.group(1))
    if best is None:
        raise SystemExit("no VM service URI found in shots/*.out")
    return best[1]


async def main_async(uri: str) -> int:
    ws_url = uri.replace("http://", "ws://").rstrip("/") + "/ws"
    async with websockets.connect(ws_url, max_size=8 * 1024 * 1024) as ws:
        async def call(method: str, params: dict | None = None) -> dict:
            await ws.send(json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or {},
            }))
            while True:
                message = json.loads(await ws.recv())
                if message.get("id") == 1:
                    return message

        vm = await call("getVM")
        isolates = vm["result"]["isolates"]
        isolate_id = isolates[0]["id"]
        result = await call(
            "ext.flutter.debugDumpSemanticsTreeInTraversalOrder",
            {"isolateId": isolate_id},
        )
        data = result.get("result", {})
        text = data.get("data") if isinstance(data, dict) else None
        if not text:
            print(json.dumps(result, ensure_ascii=False)[:2000])
            return 1
        print(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri")
    parser.add_argument("--auto", action="store_true")
    args = parser.parse_args(argv)
    uri = args.uri or find_uri()
    print(f"# VM service {uri}", file=sys.stderr)
    return asyncio.run(main_async(uri))


if __name__ == "__main__":
    raise SystemExit(main())
