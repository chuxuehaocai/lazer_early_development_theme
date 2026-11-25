"""Locate the failing line inside the assembled Lua chunk.

The host concatenates every plugin module into one chunk:
    module_loaders["<name>"] = function()
    <module source>
    end
so a Lua error position like `:1174` refers to that synthetic chunk. This
script rebuilds the same chunk and prints the line at that index.
"""
import io
import json
import os
import sys

PLUGIN = r"E:\projects\lazer_early_development_theme\plugin"
STORAGE = os.path.join(
    os.environ["APPDATA"],
    "dev.naominet",
    "lazer_nextgen",
    "lua_plugin_data",
    "community.naominet.parchment-field-notes",
    "storage.json",
)


def chunk():
    lines = ["local function page_edit(operation, spec)", "end"]
    # The host walks modules in sorted order and wraps each one.
    names = []
    for root, _dirs, files in os.walk(PLUGIN):
        for name in files:
            if name.endswith(".lua"):
                rel = os.path.relpath(os.path.join(root, name), PLUGIN)
                rel = rel.replace("\\", "/")
                if rel != "main.lua":
                    names.append(rel)
    for rel in sorted(names):
        with io.open(os.path.join(PLUGIN, rel), "r", encoding="utf-8") as handle:
            body = handle.read().splitlines()
        lines.append('module_loaders["%s"] = function()' % rel)
        lines.extend(body)
        lines.append("end")
    with io.open(os.path.join(PLUGIN, "main.lua"), "r", encoding="utf-8") as handle:
        lines.extend(handle.read().splitlines())
    return lines


def main():
    lines = chunk()
    print("chunk lines:", len(lines))
    if len(sys.argv) > 1:
        want = int(sys.argv[1])
    else:
        want = 1174
        try:
            with io.open(STORAGE, "r", encoding="utf-8") as handle:
                err = json.load(handle).get("lastError") or ""
            tail = err.rsplit(":", 1)[-1]
            digits = "".join(ch for ch in err[err.rfind("]") - 8 :] if ch.isdigit())
            if digits:
                want = int(digits)
        except Exception:
            pass
    lo = max(0, want - 6)
    for index in range(lo, min(len(lines), want + 3)):
        mark = ">>" if index + 1 == want else "  "
        print("%s %5d: %s" % (mark, index + 1, lines[index]))


if __name__ == "__main__":
    main()
