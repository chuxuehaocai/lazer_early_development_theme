#!/usr/bin/env python3
"""Validate that plugin/ can actually be packaged and installed.

Checks (all from the docs, 包结构 / 体积与文件限制 / 路径规则):
  * whitelist        manifest.json, *.lua, .json .md .txt .html .css .js .svg, root LICENSE
  * path safety      no \\, drive letter, leading /, `.`/`..` segments, trailing dot or
                     space, < > " | ? *, control characters, > 200 chars, case-fold dups
  * budgets          <= 256 files, <= 2 MB per file, <= 8 MB total, <= 16 MB as ZIP
  * manifest         present at the package root and parseable
  * frontend         every css/js/svg referenced by index.html exists in the package
  * extras           asset files nobody references, `<use href="x.svg#...">`,
                     symlinks, empty files

Usage:
  python tools\\check_package.py [--plugin-dir plugin] [--frontend-dir DIR ...]
                                 [--strict] [--json] [--require]

Exit code 1 means at least one error. A missing plugin directory prints SKIP and
exits 0 unless --require is passed.
"""

from __future__ import annotations

import argparse
import io
import json
import pathlib
import re
import sys
import zipfile
from html.parser import HTMLParser

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import plugin_rules as R  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent

ASSET_EXTENSIONS = {".css", ".js", ".svg", ".html"}
IGNORED_SCHEMES = ("http://", "https://", "data:", "mailto:", "tel:", "javascript:", "blob:", "about:")


class ReferenceParser(HTMLParser):
    """Collect href/src attributes and flag external-sprite references."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str, int]] = []  # (tag, value, lineno)
        self.uses: list[tuple[str, int]] = []      # <use href=...> values
        self.scripts: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        for attribute in ("href", "src"):
            value = attributes.get(attribute)
            if value:
                self.refs.append((tag, value, self.getpos()[0]))
                if tag == "use" or attribute == "href" and tag == "use":
                    self.uses.append((value, self.getpos()[0]))
        if tag == "script" and attributes.get("src"):
            self.scripts.append(attributes["src"])


def is_external(value: str) -> bool:
    text = value.strip()
    if not text:
        return True
    lowered = text.lower()
    if lowered.startswith(IGNORED_SCHEMES) or lowered.startswith("//"):
        return True
    if lowered.startswith("#"):
        return True
    return False


def resolve_reference(source: pathlib.Path, value: str, root: pathlib.Path) -> tuple[pathlib.Path | None, str]:
    """Resolve an HTML reference to a path inside the package root."""
    clean = value.strip().split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return None, "空引用"
    if clean.startswith("/"):
        return None, "以 / 开头的绝对路径在包里不会命中（提示：用相对路径）"
    target = (source.parent / clean).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None, f"解析到包外（{target}）"
    return target, ""


def check_frontend_files(
    root: pathlib.Path,
    findings: R.Findings,
    referenced: set[pathlib.Path],
    label: str,
) -> None:
    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        findings.note("frontend", f"{label} 里没有 .html，跳过资源引用检查")
        return
    for html_file in html_files:
        rel = html_file.relative_to(root).as_posix()
        try:
            text = html_file.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            findings.error("frontend", f"无法读取 {rel}：{exc}")
            continue
        parser = ReferenceParser()
        try:
            parser.feed(text)
        except Exception as exc:  # html.parser is forgiving, but stay safe
            findings.warn("frontend", f"{rel} 解析失败：{exc}")
            continue
        for tag, value, line in parser.refs:
            if is_external(value):
                continue
            target, problem = resolve_reference(html_file, value, root)
            findings.checks += 1
            if target is None:
                findings.error("frontend", f"{rel}:{line} <{tag}> {value!r} 无效：{problem}")
                continue
            referenced.add(target.resolve())
            if not target.is_file():
                findings.error(
                    "frontend",
                    f"{rel}:{line} <{tag}> 引用了 {value!r}，但包里没有 "
                    f"{target.relative_to(root.resolve()).as_posix()}",
                )
        for value, line in parser.uses:
            if "svg#" in value or value.lower().endswith(".svg"):
                findings.warn(
                    "frontend",
                    f"{rel}:{line} <use href={value!r}> 引用外部 svg；file:// 下会被拦，"
                    "应把 symbol 内联进页面（js/icons.js 注入）",
                )


def report_orphans(root: pathlib.Path, referenced: set[pathlib.Path], findings: R.Findings) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in ASSET_EXTENSIONS:
            continue
        if path.suffix.lower() == ".html":
            continue
        if path.resolve() not in referenced:
            findings.note(
                "frontend",
                f"未被任何 html 引用的资源：{path.relative_to(root).as_posix()}",
            )


ICON_REF_RE = re.compile(r'#(i-[a-z0-9]+(?:-[a-z0-9]+)*)')
# Symbols are only trusted from the runtime injector: the packaged frontend uses
# <use href="#id"> against js/icons.js, and a second copy of the sprite would be
# a divergent source of truth.
ICON_JS_IDS_RE = re.compile(r'"(i-[a-z0-9-]+)"')


def check_icon_refs(root: pathlib.Path, findings: R.Findings) -> None:
    """`<use href="#i-home">` must point at a symbol js/icons.js actually injects."""
    js_path = root / "js" / "icons.js"
    if not js_path.is_file():
        findings.note("icons", "没有 js/icons.js，跳过图标引用检查")
        return
    defined = set(ICON_JS_IDS_RE.findall(js_path.read_text(encoding="utf-8", errors="replace")))
    if not defined:
        findings.note("icons", "js/icons.js 里没有 i-* symbol id，跳过图标引用检查")
        return

    used: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".html", ".js", ".css"):
            continue
        if path == js_path:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in ICON_REF_RE.finditer(text):
            used.setdefault(match.group(1), path.relative_to(root).as_posix())

    missing = sorted(set(used) - defined)
    for icon_id in missing:
        findings.error(
            "icons",
            f"{used[icon_id]} 引用了 #{icon_id}，但 js/icons.js 没有注入这个 symbol"
            f"（共 {len(defined)} 个）",
        )
    findings.checks += 1
    if used and not missing:
        findings.note("icons", f"图标引用 {len(used)} 个，全部在 js/icons.js 里")


def check_temp_files(files: list[tuple[str, pathlib.Path, int]], findings: R.Findings) -> None:
    """Underscore-prefixed files are scratch pads; they must not ship."""
    for rel, _path, _size in files:
        name = rel.rsplit("/", 1)[-1]
        if not name.startswith("_"):
            continue
        findings.error(
            "tempfile",
            f"{rel} 是下划线开头的临时/调试文件，不应进入发布包；"
            "开发期调试文件请放到 frontend 目录之外",
        )


def estimate_zip(files: list[tuple[str, pathlib.Path, int]]) -> int:
    """Measure the deterministic ZIP that build_zip.py would write."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel, path, _size in files:
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            try:
                zf.writestr(info, path.read_bytes())
            except OSError:
                pass
    return len(buffer.getvalue())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate that plugin/ is packageable.")
    parser.add_argument("--plugin-dir", default=None, help="插件目录（默认 plugin）")
    parser.add_argument(
        "--frontend-dir",
        action="append",
        default=None,
        help="额外的静态前端目录（可重复）；默认同时检查插件内的 html 与仓库根的 frontend/",
    )
    parser.add_argument("--strict", action="store_true", help="把 warn 级问题也当错误")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    parser.add_argument("--require", action="store_true", help="缺少插件目录时视为失败")
    args = parser.parse_args(argv)

    plugin_dir = pathlib.Path(args.plugin_dir) if args.plugin_dir else REPO / "plugin"
    findings = R.Findings("check_package")

    if not plugin_dir.is_dir():
        print(f"SKIP 插件目录不存在：{plugin_dir}")
        if args.require:
            return 1
        return 0

    print(f"package  {plugin_dir}")
    files, ignored = R.collect_files(plugin_dir)
    for rel in ignored:
        findings.note("package", f"打包杂物已忽略：{rel}")

    if not files:
        print(f"SKIP 插件目录是空的：{plugin_dir}")
        if args.require:
            return 1
        return 0

    lowered: dict[str, str] = {}
    total = 0
    empty: list[str] = []
    symlinks: list[str] = []

    for rel, path, size in files:
        rule = "path"
        problems = R.path_problems(rel)
        for problem in problems:
            findings.error(rule, f"{rel}：{problem}")
        findings.checks += 1

        allowed, reason = R.file_type_allowed(rel)
        if not allowed:
            findings.error("type", f"{rel}：{reason}")

        total += size
        if size > R.MAX_FILE_BYTES:
            findings.error(
                "size",
                f"{rel} 大小 {size} 字节超过单文件上限 {R.MAX_FILE_BYTES}（2 MB）",
            )
        if size == 0:
            empty.append(rel)
        if path.is_symlink():
            symlinks.append(rel)

        key = rel.lower()
        if key in lowered and lowered[key] != rel:
            findings.error(
                "path",
                f"路径按小写去重冲突：{lowered[key]!r} 与 {rel!r}（客户端只保留一个）",
            )
        else:
            lowered.setdefault(key, rel)

    findings.expect(
        len(files) <= R.MAX_FILES,
        "count",
        f"文件数 {len(files)} 超过上限 {R.MAX_FILES}",
    )
    findings.expect(
        total <= R.MAX_TOTAL_BYTES,
        "total",
        f"解压后总量 {total} 字节超过上限 {R.MAX_TOTAL_BYTES}（8 MB）",
    )
    for rel in empty:
        findings.warn("size", f"{rel} 是空文件")
    for rel in symlinks:
        findings.error("path", f"{rel} 是符号链接；沙箱禁止符号链接")

    manifest = plugin_dir / "manifest.json"
    if not manifest.is_file():
        findings.error("manifest", "ZIP 根目录缺少 manifest.json（entry 也必须在包里）")
    else:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8-sig"))
            entry = data.get("entry", "main.lua") if isinstance(data, dict) else "main.lua"
            if isinstance(entry, str) and not (plugin_dir / entry).is_file():
                findings.error("manifest", f"manifest 的 entry {entry!r} 不在包里")
        except (json.JSONDecodeError, OSError) as exc:
            findings.error("manifest", f"manifest.json 读取/解析失败：{exc}")

    # --- frontend asset references -------------------------------------------
    referenced: set[pathlib.Path] = set()
    if (plugin_dir / "frontend").is_dir():
        check_frontend_files(plugin_dir, findings, referenced, "plugin/frontend")
    else:
        if any(p.suffix.lower() == ".html" for _rel, p, _s in files):
            check_frontend_files(plugin_dir, findings, referenced, "plugin")
        else:
            findings.note("frontend", "包里没有 html；随包前端可能还没写")
    extra_dirs = args.frontend_dir
    if extra_dirs is None:
        extra_dirs = []
        repo_frontend = REPO / "frontend"
        if repo_frontend.is_dir() and (repo_frontend / "index.html").is_file():
            extra_dirs.append(str(repo_frontend))
    for extra in extra_dirs:
        extra_root = pathlib.Path(extra)
        if not extra_root.is_dir():
            findings.note("frontend", f"额外前端目录不存在：{extra_root}")
            continue
        if extra_root.resolve() == (plugin_dir / "frontend").resolve():
            continue
        check_frontend_files(extra_root, findings, referenced, str(extra_root))

    if (plugin_dir / "frontend").is_dir():
        report_orphans(plugin_dir / "frontend", referenced, findings)
        check_icon_refs(plugin_dir / "frontend", findings)

    for rel, _path, _size in files:
        if rel.lower().endswith(".html") and rel.rsplit("/", 1)[-1].lower() != "index.html":
            findings.note("package", f"包内额外的 html：{rel}（会随 ZIP 发布，确认不是调试页）")
    check_temp_files(files, findings)

    # --- zip budget ----------------------------------------------------------
    zip_size = estimate_zip(files)
    findings.expect(
        zip_size <= R.MAX_ZIP_BYTES,
        "zip",
        f"打包后 ZIP 大小 {zip_size} 字节超过上限 {R.MAX_ZIP_BYTES}（16 MB）",
    )

    findings.emit()
    print(
        f"files {len(files)}  total {total} B ({total / 1024:.1f} KB)  "
        f"zip {zip_size} B ({zip_size / 1024:.1f} KB)"
    )
    print(findings.summary())

    if args.json:
        payload = findings.as_dict()
        payload.update(
            {
                "pluginDir": str(plugin_dir),
                "files": len(files),
                "totalBytes": total,
                "zipBytes": zip_size,
            }
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if findings.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
