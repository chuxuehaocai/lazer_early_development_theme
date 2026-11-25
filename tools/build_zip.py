#!/usr/bin/env python3
"""Pack plugin/ into build/<id>-<version>.zip the way the client expects.

The package layout rules (docs: 包结构 / 体积与文件限制 / 路径规则):
  * every file is added individually, paths use forward slashes
  * no parent directory inside the archive - manifest.json sits at the root
  * root LICENSE is included, __MACOSX/ .DS_Store Thumbs.db are dropped
  * only whitelisted types are packed; anything else fails the build
  * output name is <id>-<version>.zip

The archive is deterministic: entries sorted, timestamps pinned to 1980-01-01,
permissions 0644, deflate level 9 - rebuilding identical sources yields the same
SHA-256.

The output file follows the manifest: `build/<manifest.id>.zip`. The marketplace
requires the file name, the listing entry and the manifest id to agree, so the
manifest is the default source; `--id X` overrides it when you need a different
name on purpose.

Usage:
  python tools\\build_zip.py [--plugin-dir plugin] [--build-dir build]
                             [--id X] [--version X.Y.Z]
                             [--force] [--json] [--require] [--list]

Exit code 1 on a packaging error (bad file type, oversized package, missing
manifest). A missing plugin directory prints SKIP and exits 0 unless --require.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import zipfile

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import plugin_rules as R  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent

# `--id` overrides the file name; the default follows manifest.json because the
# marketplace compares the file name, the listing id and the manifest id.
DEFAULT_ID = None
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def read_manifest(plugin_dir: pathlib.Path, findings: R.Findings) -> dict | None:
    manifest = plugin_dir / "manifest.json"
    if not manifest.is_file():
        findings.error("manifest", f"缺少 {manifest}（ZIP 根目录必须有 manifest.json）")
        return None
    try:
        data = json.loads(manifest.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        findings.error("manifest", f"manifest.json 解析失败：第 {exc.lineno} 行 {exc.msg}")
        return None
    except OSError as exc:
        findings.error("manifest", f"无法读取 manifest.json：{exc}")
        return None
    if not isinstance(data, dict):
        findings.error("manifest", "manifest.json 顶层必须是对象")
        return None
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the plugin ZIP from plugin/.")
    parser.add_argument("--plugin-dir", default=None, help="插件目录（默认 plugin）")
    parser.add_argument("--build-dir", default=None, help="输出目录（默认 build）")
    parser.add_argument(
        "--id",
        default=DEFAULT_ID,
        help="文件名里的插件 id（默认跟随 manifest.json 的 id；manifest 表示显式跟随清单）",
    )
    parser.add_argument("--version", default=None, help="覆盖版本号（默认取清单 version）")
    parser.add_argument("--force", action="store_true", help="忽略白名单问题，照样打包")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    parser.add_argument("--require", action="store_true", help="缺少插件目录时视为失败")
    parser.add_argument("--list", dest="list_entries", action="store_true", help="列出包内条目")
    args = parser.parse_args(argv)

    plugin_dir = pathlib.Path(args.plugin_dir) if args.plugin_dir else REPO / "plugin"
    build_dir = pathlib.Path(args.build_dir) if args.build_dir else REPO / "build"

    if not plugin_dir.is_dir():
        print(f"SKIP 插件目录不存在：{plugin_dir}")
        if args.require:
            return 1
        return 0

    findings = R.Findings("build_zip")
    manifest = read_manifest(plugin_dir, findings)
    if manifest is None or not findings.ok:
        findings.emit()
        print(findings.summary())
        return 1

    version = args.version or manifest.get("version")
    if not isinstance(version, str) or not R.VERSION_RE.match(version):
        findings.error("version", f"版本号无效：{version!r}（清单 version 必须是语义化版本）")
    manifest_id = manifest.get("id")

    if args.id in (None, "manifest"):
        stem = manifest_id
        if not isinstance(stem, str) or not R.ID_RE.match(stem):
            findings.error(
                "id",
                f"manifest id {stem!r} 不合法，无法作为文件名；用 --id 指定",
            )
            stem = "plugin"
    else:
        stem = args.id
        if manifest_id and manifest_id != stem:
            findings.warn(
                "name",
                f"文件名用 {stem!r}，清单 id 是 {manifest_id!r}；市场要求两者一致"
                "（默认已跟随清单，确认这次是故意的）",
            )

    files, ignored = R.collect_files(plugin_dir)
    for rel in ignored:
        findings.note("package", f"打包杂物已忽略：{rel}")
    if not files:
        print(f"SKIP 插件目录是空的：{plugin_dir}")
        return 1 if args.require else 0

    packable: list[tuple[str, pathlib.Path, int]] = []
    total = 0
    for rel, path, size in files:
        problems = R.path_problems(rel)
        for problem in problems:
            findings.error("path", f"{rel}：{problem}")
        allowed, reason = R.file_type_allowed(rel)
        if not allowed:
            findings.error("type", f"{rel}：{reason}")
        if size > R.MAX_FILE_BYTES:
            findings.error("size", f"{rel} 大小 {size} 超过单文件上限 {R.MAX_FILE_BYTES}")
        total += size
        if not problems and (allowed or args.force):
            packable.append((rel, path, size))

    findings.expect(len(files) <= R.MAX_FILES, "count", f"文件数 {len(files)} 超过 {R.MAX_FILES}")
    findings.expect(
        total <= R.MAX_TOTAL_BYTES,
        "total",
        f"解压后总量 {total} 字节超过 {R.MAX_TOTAL_BYTES}",
    )
    if (plugin_dir / "manifest.json").resolve() not in {p.resolve() for _r, p, _s in packable}:
        findings.error("manifest", "manifest.json 没有被加入包（必须在根目录）")

    if not findings.ok:
        findings.emit()
        print(findings.summary())
        print("FAIL 没有写出 ZIP；修好上面的问题后重试（--force 可跳过白名单）")
        return 1

    build_dir.mkdir(parents=True, exist_ok=True)
    target = build_dir / f"{stem}-{version}.zip"
    buffer_hash = hashlib.sha256()

    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel, path, _size in sorted(packable, key=lambda item: item[0].lower()):
            data = path.read_bytes()
            info = zipfile.ZipInfo(rel, date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.create_system = 0
            archive.writestr(info, data)

    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    size = target.stat().st_size

    findings.expect(
        size <= R.MAX_ZIP_BYTES,
        "zip",
        f"ZIP 大小 {size} 字节超过上限 {R.MAX_ZIP_BYTES}（16 MB）",
    )

    findings.emit()
    print(f"WROTE {target}")
    print(f"  files   {len(packable)}  (+{len(ignored)} ignored)")
    print(f"  unpacked {total} B ({total / 1024:.1f} KB)")
    print(f"  zip     {size} B ({size / 1024:.1f} KB)")
    print(f"  sha256  {digest}")
    print(
        f"  summary id={stem}  version={version}  files={len(packable)}  "
        f"zip={size}B  sha256={digest}"
    )
    if args.list_entries:
        for rel, _path, entry_size in sorted(packable, key=lambda item: item[0].lower()):
            print(f"    {entry_size:>8}  {rel}")
    print(findings.summary())

    if args.json:
        payload = findings.as_dict()
        payload.update(
            {
                "path": str(target),
                "bytes": size,
                "files": len(packable),
                "unpackedBytes": total,
                "sha256": digest,
                "version": version,
                "id": stem,
            }
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if findings.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
