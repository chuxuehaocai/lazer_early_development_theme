"""全路由 × 全视口截图（按路由分批调 docs/dev/cdp-shot.mjs，失败自动重试一次）。

用法:
  python tools/sweep.py                # 默认 http://127.0.0.1:8080/index.html?still=1
  python tools/sweep.py --base "http://127.0.0.1:8080/index.html?ws=11581&still=1"
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

ROUTES = [
    "home",
    "likes",
    "search",
    "playlist:p1",
    "album:a1",
    "now",
    "queue",
    "settings",
    "me",
    "login",
    "design",
]
VIEWPORTS = [(1440, 900), (1024, 768), (480, 900)]


def run_batch(jobs):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(jobs, handle, ensure_ascii=False)
        path = handle.name
    try:
        result = subprocess.run(
            ["node", os.path.join("docs", "dev", "cdp-shot.mjs"), path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 99, "", "timeout"
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8080/index.html?still=1")
    parser.add_argument("--out-dir", default=os.path.join("shots", "final"))
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    failures = []
    total = 0
    for route in ROUTES:
        jobs = []
        for width, height in VIEWPORTS:
            name = f"{route.replace(':', '-')}-{width}x{height}.png"
            jobs.append(
                {
                    "url": f"{args.base}#/{route}",
                    "w": width,
                    "h": height,
                    "out": os.path.join(args.out_dir, name),
                }
            )
        for attempt in (1, 2):
            code, out, err = run_batch(jobs)
            if code == 0:
                total += len(jobs)
                print(f"OK   {route} ({'retry' if attempt > 1 else 'first'})")
                break
            if attempt == 2:
                failures.append((route, code))
                print(f"FAIL {route} code={code} out={out[-200:]} err={err[-300:]}")
    print(f"shots {total}/{len(ROUTES) * len(VIEWPORTS)}  failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
