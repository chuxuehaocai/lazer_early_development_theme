"""验证插件的实时状态桥：握手 ws://127.0.0.1:<port>/lazer 并读一帧快照。

用法:
  python tools/ws_probe.py                 # 默认 11581
  python tools/ws_probe.py --port 11581 --frames 3

只用标准库（socket + base64 + struct），不依赖 websockets 包。
"""
import argparse
import base64
import json
import os
import socket
import struct
import sys


def handshake(port, path="/lazer", timeout=6):
    sock = socket.create_connection(("127.0.0.1", port), timeout=timeout)
    key = base64.b64encode(os.urandom(16)).decode()
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(request.encode("ascii"))
    buffer = b""
    while b"\r\n\r\n" not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            raise SystemExit("连接被关闭，握手失败")
        buffer += chunk
    head, rest = buffer.split(b"\r\n\r\n", 1)
    status = head.split(b"\r\n")[0].decode("latin-1")
    if "101" not in status:
        raise SystemExit(f"握手未升级: {status}")
    return sock, rest


def read_frame(sock, buffer, timeout=8):
    sock.settimeout(timeout)
    while True:
        if len(buffer) >= 2:
            first, second = buffer[0], buffer[1]
            length = second & 0x7F
            index = 2
            if length == 126:
                if len(buffer) >= 4:
                    length = struct.unpack(">H", buffer[2:4])[0]
                    index = 4
                else:
                    buffer += sock.recv(65536)
                    continue
            elif length == 127:
                if len(buffer) >= 10:
                    length = struct.unpack(">Q", buffer[2:10])[0]
                    index = 10
                else:
                    buffer += sock.recv(65536)
                    continue
            if len(buffer) >= index + length:
                payload = buffer[index:index + length]
                return payload, buffer[index + length:]
        buffer += sock.recv(65536)


def describe(payload):
    try:
        data = json.loads(payload.decode("utf-8", "replace"))
    except Exception as error:  # noqa: BLE001
        print("帧不是 JSON:", error, payload[:120])
        return
    track = data.get("track") or {}
    queue = data.get("queue") or {}
    lyrics = data.get("lyrics") or {}
    print(f"  曲目    {track.get('title')} — {track.get('artist')}")
    print(f"  进度    {data.get('positionMs')} / {data.get('durationMs')} ms · playing={data.get('playing')}")
    print(f"  队列    {queue.get('length')} 首（快照 {len(queue.get('tracks') or [])} 条）")
    print(f"  歌词    {len(lyrics.get('lines') or [])} 行")
    view = data.get("view") or {}
    print(f"  视图    {json.dumps(view, ensure_ascii=False)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=11581)
    parser.add_argument("--path", default="/lazer")
    parser.add_argument("--frames", type=int, default=1)
    args = parser.parse_args()

    try:
        sock, rest = handshake(args.port, args.path)
    except OSError as error:
        raise SystemExit(f"连不上 ws://127.0.0.1:{args.port}{args.path}：{error}")

    print(f"握手成功 ws://127.0.0.1:{args.port}{args.path}")
    try:
        for index in range(args.frames):
            payload, rest = read_frame(sock, rest)
            print(f"帧 #{index + 1}  {len(payload)} 字节")
            describe(payload)
    finally:
        sock.close()


if __name__ == "__main__":
    main()
