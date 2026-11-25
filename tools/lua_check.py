"""语法检查：逐文件解析，失败时二分定位出错行。"""
import glob
import sys
from luaparser import ast


def check(path):
    src = open(path, encoding="utf-8").read()
    try:
        ast.parse(src)
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, exc


def locate(path):
    lines = open(path, encoding="utf-8").read().splitlines(keepends=True)
    lo, hi = 1, len(lines)
    # 找最小的前缀行数，使得"加入该行"后解析失败
    bad = None
    for n in range(2, len(lines) + 1):
        try:
            ast.parse("".join(lines[:n]))
        except Exception:
            bad = n
            break
    if bad is None:
        return None
    # 已在 bad 行失败：报告 bad 行及上下文
    ctx = "".join(lines[max(0, bad - 4):bad])
    return bad, ctx


def main():
    files = sys.argv[1:] or glob.glob("plugin/**/*.lua", recursive=True)
    failed = 0
    for path in files:
        ok, exc = check(path)
        if ok:
            print(f"OK   {path}")
        else:
            failed += 1
            print(f"FAIL {path}: {type(exc).__name__}: {exc}")
            hit = locate(path)
            if hit:
                line, ctx = hit
                print(f"     first failing line ~{line}")
                print("     ---context---")
                for i, text in enumerate(ctx.splitlines(), start=max(1, line - 3)):
                    print(f"     {i:>4}| {text}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
