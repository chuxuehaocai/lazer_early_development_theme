"""Multiply every hard-coded `BorderRadius.circular(x)` by the global corner
strength provider (`AppleShape.scaleOf(context)`), and add the import.

Usage:
  python tools/sweep_radii.py --dry
  python tools/sweep_radii.py
"""
import io
import os
import sys

LIB = r"E:\projects\lazer_nextgen\lib"
TARGET = os.path.join(LIB, "theme", "shape_scale.dart")
SKIP_DIRS = {"tv"}
SKIP_FILES = {"image_export.dart"}
NEEDLE = "BorderRadius.circular("


def import_line(path):
    rel = os.path.relpath(TARGET, os.path.dirname(path)).replace("\\", "/")
    return "import '%s';" % rel


def add_import(text, path):
    line = import_line(path)
    if line in text:
        return text
    lines = text.splitlines()
    last = -1
    for index, value in enumerate(lines):
        if value.startswith("import "):
            last = index
    if last < 0:
        return line + "\n" + text
    lines.insert(last + 1, line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def rewrite(text):
    out = []
    index = 0
    count = 0
    while True:
        found = text.find(NEEDLE, index)
        if found < 0:
            out.append(text[index:])
            break
        start = found + len(NEEDLE)
        depth = 1
        cursor = start
        while cursor < len(text) and depth > 0:
            char = text[cursor]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            cursor += 1
        if depth != 0:
            out.append(text[index:])
            break
        arg = text[start : cursor - 1]
        out.append(text[index:start])
        if "AppleShape.scaleOf" in arg:
            out.append(arg + ")")
        else:
            out.append("%s * AppleShape.scaleOf(context))" % arg.strip())
            count += 1
        index = cursor
    return "".join(out), count


def main():
    dry = "--dry" in sys.argv
    total_files = 0
    total_sites = 0
    skipped = []
    for root, dirs, files in os.walk(LIB):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(".dart") or name in SKIP_FILES:
                continue
            path = os.path.join(root, name)
            text = io.open(path, encoding="utf-8").read()
            if NEEDLE not in text:
                continue
            updated, count = rewrite(text)
            if count == 0:
                continue
            if not dry:
                updated = add_import(updated, path)
                io.open(path, "w", encoding="utf-8", newline="\n").write(updated)
            total_files += 1
            total_sites += count
            print("%-52s %3d" % (os.path.relpath(path, LIB), count))
    print("files", total_files, "sites", total_sites, "dry" if dry else "written")


if __name__ == "__main__":
    main()
