#!/usr/bin/env python3
"""Validate plugin/manifest.json against the Lazer Lua plugin rules (schema 1).

Rules come from docs/lua-plugins.md and the site manifest page:
  id           ^[a-z][a-z0-9_.-]{2,79}$
  name         non-empty, <= 100 characters
  version      semantic version (-prerelease allowed, build metadata noted)
  apiVersion   must be the number 1 (a missing key means 0 -> rejected)
  provider     ^[a-z][a-z0-9_-]{1,39}$, not the reserved word `local`
  entry        safe relative path, ends with .lua, present inside the package
  capabilities known names (case and -/_ insensitive)
  permissions  network/socket/websocket <= 32, socketServer/websocketServer <= 16,
               storage/filesystem booleans, data <= 5 known scopes,
               hosts are bare hostnames with an optional port, `*.` wildcards must
               land on a registrable domain (public suffix table is built in)

Usage:
  python tools\\check_manifest.py [--manifest plugin\\manifest.json]
                                  [--plugin-dir plugin] [--strict] [--json] [--require]

Exit code 1 means at least one error. A missing manifest prints SKIP and exits 0
unless --require is passed.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import plugin_rules as R  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent

KNOWN_TOP_LEVEL = {
    "id", "name", "version", "description", "author", "entry", "apiVersion",
    "provider", "capabilities", "auth", "permissions", "minAppVersion",
    "homepage", "license", "repo", "tags", "icon", "platforms",
}


def load_manifest(path: pathlib.Path, findings: R.Findings) -> dict | None:
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        findings.error("manifest", f"无法读取 {path}：{exc}")
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        findings.error(
            "manifest",
            f"JSON 解析失败：第 {exc.lineno} 行第 {exc.colno} 列 {exc.msg}",
        )
        return None
    if not isinstance(data, dict):
        findings.error("manifest", f"顶层必须是 JSON 对象，当前是 {type(data).__name__}")
        return None
    return data


def check_top_level(data: dict, findings: R.Findings) -> None:
    unknown = sorted(set(data) - KNOWN_TOP_LEVEL)
    for key in unknown:
        findings.warn("schema", f"未知字段 {key!r}（客户端会忽略；确认不是拼写错误）")


def check_id(data: dict, findings: R.Findings) -> None:
    value = data.get("id")
    if not isinstance(value, str):
        findings.error("id", f"id 必须是非空字符串，当前 {value!r}")
        return
    if not R.ID_RE.match(value):
        findings.error(
            "id",
            f"id {value!r} 不符合 ^[a-z][a-z0-9_.-]{{2,79}}$（小写字母开头、3–80 位、"
            "只允许 a-z 0-9 _ . -）",
        )
        return
    findings.checks += 1
    if "." not in value:
        findings.note("id", f"id {value!r} 没有域名点号；建议用反写域名，例如 community.example.music")


def check_name(data: dict, findings: R.Findings) -> None:
    value = data.get("name")
    if not isinstance(value, str) or not value.strip():
        findings.error("name", f"name 必须是非空字符串，当前 {value!r}")
        return
    findings.expect(
        len(value) <= R.NAME_MAX,
        "name",
        f"name 长度 {len(value)} 超过 {R.NAME_MAX} 字符",
    )


def check_version(data: dict, findings: R.Findings) -> None:
    value = data.get("version")
    if not isinstance(value, str):
        findings.error("version", f"version 必须是字符串，当前 {value!r}")
        return
    match = R.VERSION_RE.match(value)
    if not match:
        findings.error(
            "version",
            f"version {value!r} 不是语义化版本（期望 MAJOR.MINOR.PATCH[-prerelease]）",
        )
        return
    findings.checks += 1
    if match.group(5) is not None:  # +build metadata
        findings.warn(
            "version",
            f"version {value!r} 带构建元数据，市场清单的 version 校验不接受 +build，"
            "上架前请去掉",
        )
    if match.group(4) is not None:  # prerelease
        findings.note("version", f"version {value!r} 是预发布版本")
    if not R.VERSION_MARKET_RE.match(value):
        findings.note("version", f"市场清单要求 version 完全一致，当前值需原样写进 plugins.json")


def check_api_version(data: dict, findings: R.Findings) -> None:
    if "apiVersion" not in data:
        findings.error("apiVersion", "缺少 apiVersion；遗漏时客户端按 0 处理并拒绝安装，必须显式写 1")
        return
    value = data["apiVersion"]
    if isinstance(value, bool) or not isinstance(value, int):
        findings.error("apiVersion", f"apiVersion 必须是数字 1，当前 {value!r}")
        return
    findings.expect(
        value == R.API_VERSION,
        "apiVersion",
        f"apiVersion 只接受 {R.API_VERSION}，当前 {value}",
    )


def check_provider(data: dict, findings: R.Findings) -> None:
    value = data.get("provider")
    if value is None:
        findings.error("provider", "缺少 provider（清单唯一来源，运行时放进 args.platform）")
        return
    if not isinstance(value, str):
        findings.error("provider", f"provider 必须是字符串，当前 {value!r}")
        return
    if value in R.RESERVED_PROVIDERS:
        findings.error("provider", f"provider {value!r} 是保留字，不能使用")
        return
    findings.expect(
        bool(R.PROVIDER_RE.match(value)),
        "provider",
        f"provider {value!r} 不符合 ^[a-z][a-z0-9_-]{{1,39}}$（小写字母开头、2–40 位）",
    )


def check_entry(data: dict, plugin_dir: pathlib.Path | None, findings: R.Findings) -> None:
    value = data.get("entry", "main.lua")
    if "entry" not in data:
        findings.note("entry", "未写 entry，按默认 main.lua 处理")
    if not isinstance(value, str):
        findings.error("entry", f"entry 必须是字符串，当前 {value!r}")
        return
    problems = R.path_problems(value)
    for problem in problems:
        findings.error("entry", f"entry {value!r}：{problem}")
    if problems:
        return
    if not value.lower().endswith(".lua"):
        findings.error("entry", f"entry {value!r} 必须以 .lua 结尾")
        return
    findings.checks += 1
    if plugin_dir is None or not plugin_dir.is_dir():
        findings.note("entry", f"未找到插件目录，跳过 entry 存在性检查（{value}）")
        return
    target = plugin_dir / value
    if not target.is_file():
        findings.error("entry", f"entry {value!r} 在插件目录里不存在（{target}）")
        return
    try:
        size = target.stat().st_size
    except OSError as exc:
        findings.warn("entry", f"无法读取 entry 大小：{exc}")
        return
    findings.expect(
        size <= R.MAX_FILE_BYTES,
        "entry",
        f"entry {value!r} 大小 {size} 字节超过单文件上限 {R.MAX_FILE_BYTES}",
    )
    if size == 0:
        findings.warn("entry", f"entry {value!r} 是空文件")


def check_text_field(data: dict, key: str, limit: int, findings: R.Findings) -> None:
    if key not in data:
        return
    value = data[key]
    if not isinstance(value, str):
        findings.error(key, f"{key} 必须是字符串，当前 {type(value).__name__}")
        return
    findings.checks += 1
    if len(value) > limit:
        findings.warn(key, f"{key} 长度 {len(value)} 超过建议的 {limit} 字符")


def check_capabilities(data: dict, strict: bool, findings: R.Findings) -> None:
    if "capabilities" not in data:
        findings.note("capabilities", "未声明 capabilities；首页模块和菜单入口都不会出现")
        return
    value = data["capabilities"]
    if not isinstance(value, list):
        findings.error("capabilities", f"capabilities 必须是数组，当前 {type(value).__name__}")
        return
    seen: dict[str, str] = {}
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            findings.error("capabilities", f"capabilities[{index}] 必须是非空字符串，当前 {item!r}")
            continue
        findings.checks += 1
        canonical = R.capability_canonical(item)
        if canonical is None:
            extra = ""
            if item in R.CAPABILITY_NOTES:
                extra = f"；{R.CAPABILITY_NOTES[item]}"
            else:
                trap = R.CAPABILITY_TRAPS.get(item)
                if trap:
                    extra = f"；{item!r} 是操作名，能力名应写 {trap!r}；未知能力不会出现入口"
                else:
                    extra = "；未知能力不会出现入口"
            message = (
                f"capabilities[{index}]={item!r} 不是客户端认识的能力名"
                f"（可选：{', '.join(sorted(R.CAPABILITIES))}）{extra}"
            )
            if strict:
                findings.error("capabilities", message)
            else:
                findings.warn("capabilities", message + "；未知能力不会出现入口")
            continue
        key = R.normalize_name(canonical)
        if key in seen:
            findings.warn(
                "capabilities",
                f"capabilities 重复：{seen[key]!r} 与 {item!r} 等价（大小写与 -/_ 不敏感）",
            )
        else:
            seen[key] = item


def check_auth(data: dict, strict: bool, findings: R.Findings) -> None:
    if "auth" not in data:
        return
    value = data["auth"]
    if not isinstance(value, list):
        findings.error("auth", f"auth 必须是数组，当前 {type(value).__name__}")
        return
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str):
            findings.error("auth", f"auth[{index}] 必须是字符串，当前 {item!r}")
            continue
        findings.checks += 1
        if item not in R.AUTH_MODES:
            findings.error(
                "auth",
                f"auth[{index}]={item!r} 不合法（只允许 {', '.join(sorted(R.AUTH_MODES))}）",
            )
        if item in seen:
            findings.warn("auth", f"auth 重复：{item!r}")
        seen.add(item)


def check_permissions(data: dict, strict: bool, findings: R.Findings) -> None:
    if "permissions" not in data:
        findings.note("permissions", "未声明 permissions；所有宿主能力都不会生效")
        return
    value = data["permissions"]
    if not isinstance(value, dict):
        findings.error("permissions", f"permissions 必须是对象，当前 {type(value).__name__}")
        return

    for raw_key in value:
        key = R.PERMISSION_ALIASES.get(raw_key, raw_key)
        if key not in R.PERMISSION_SPECS:
            message = (
                f"permissions.{raw_key} 不是已知的权限键"
                f"（{', '.join(sorted(R.PERMISSION_SPECS))}；filesystem 别名 files/file）"
            )
            if strict:
                findings.error("permissions", message)
            else:
                findings.warn("permissions", message + "；该键不会生效")
        elif raw_key in R.PERMISSION_ALIASES:
            findings.note("permissions", f"permissions.{raw_key} 是 {key} 的别名，建议直接写 {key}")

    for key, spec in R.PERMISSION_SPECS.items():
        if key not in value:
            continue
        kind, limit, purpose = spec
        entry = value[key]
        rule = f"permissions.{key}"

        if kind == "flag":
            if not isinstance(entry, bool):
                findings.error(rule, f"{rule} 必须是布尔值 true/false，当前 {entry!r}（{purpose}）")
            else:
                findings.checks += 1
            continue

        if not isinstance(entry, list):
            findings.error(rule, f"{rule} 必须是字符串数组，当前 {type(entry).__name__}（{purpose}）")
            continue
        if limit is not None:
            findings.expect(
                len(entry) <= limit,
                rule,
                f"{rule} 最多 {limit} 条，当前 {len(entry)} 条",
            )
        seen: dict[str, str] = {}
        for index, item in enumerate(entry):
            if not isinstance(item, str) or not item.strip():
                findings.error(rule, f"{rule}[{index}] 必须是非空字符串，当前 {item!r}")
                continue
            findings.checks += 1
            lowered = item.strip().lower()
            if lowered in seen and seen[lowered] != item:
                findings.warn(rule, f"{rule} 含重复条目 {item!r}（大小写不同但等价）")
            elif item in seen:
                findings.warn(rule, f"{rule} 含重复条目 {item!r}")
            else:
                seen[lowered] = item

            if kind == "data":
                if item not in R.DATA_SCOPES:
                    findings.error(
                        rule,
                        f"{rule}[{index}]={item!r} 不是合法的数据权限"
                        f"（只允许 {', '.join(sorted(R.DATA_SCOPES))}）",
                    )
                continue

            host, port, error = R.split_host_port(item)
            if error:
                findings.error(rule, f"{rule}[{index}]={item!r}：{error}")
                continue
            if kind == "hosts":
                for problem in R.validate_dns_host(host, allow_wildcard=True):
                    findings.error(rule, f"{rule}[{index}]={item!r}：{problem}")
                if port is not None:
                    problem = R.validate_port(port, allow_zero=False)
                    if problem:
                        findings.error(rule, f"{rule}[{index}]={item!r}：{problem}")
                    elif int(port) == 443:
                        findings.note(rule, f"{rule}[{index}]={item!r} 显式写了 443，与不写端口等价")
            else:  # endpoints
                if port is None:
                    findings.error(rule, f"{rule}[{index}]={item!r} 必须是 host:port 形式")
                    continue
                for problem in R.validate_listen_host(host):
                    findings.error(rule, f"{rule}[{index}]={item!r}：{problem}")
                problem = R.validate_port(port, allow_zero=True)
                if problem:
                    findings.error(rule, f"{rule}[{index}]={item!r}：{problem}")

        if kind == "hosts" and not entry and key == "socket":
            findings.note("socket", "permissions.socket 为空时连接目标回退到 network")


def check_min_app_version(data: dict, findings: R.Findings) -> None:
    if "minAppVersion" not in data:
        return
    value = data["minAppVersion"]
    if not isinstance(value, str) or not R.VERSION_RE.match(value):
        findings.error("minAppVersion", f"minAppVersion {value!r} 不是语义化版本")
    else:
        findings.checks += 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate plugin/manifest.json.")
    parser.add_argument("--manifest", default=None, help="manifest 路径（默认 plugin\\manifest.json）")
    parser.add_argument("--plugin-dir", default=None, help="插件目录（默认 plugin）")
    parser.add_argument("--strict", action="store_true", help="把 warn 级问题也当错误")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    parser.add_argument("--require", action="store_true", help="缺少 manifest 时视为失败")
    args = parser.parse_args(argv)

    plugin_dir = pathlib.Path(args.plugin_dir) if args.plugin_dir else REPO / "plugin"
    manifest = pathlib.Path(args.manifest) if args.manifest else plugin_dir / "manifest.json"

    findings = R.Findings("check_manifest")

    if not manifest.is_file():
        print(f"SKIP manifest 不存在：{manifest}")
        print("     （插件目录还没建好时这是正常的，先写 plugin/manifest.json）")
        if args.require:
            return 1
        return 0

    print(f"manifest  {manifest}")
    data = load_manifest(manifest, findings)
    if data is not None:
        check_top_level(data, findings)
        check_id(data, findings)
        check_name(data, findings)
        check_version(data, findings)
        check_api_version(data, findings)
        check_provider(data, findings)
        check_entry(data, plugin_dir, findings)
        check_text_field(data, "description", 300, findings)
        check_text_field(data, "author", 100, findings)
        check_capabilities(data, args.strict, findings)
        check_auth(data, args.strict, findings)
        check_permissions(data, args.strict, findings)
        check_min_app_version(data, findings)

    if args.strict:
        for rule, message in list(findings.warnings):
            findings.error(rule, message)
        findings.warnings.clear()

    findings.emit()
    print(findings.summary())

    if args.json:
        payload = findings.as_dict()
        payload["manifest"] = str(manifest)
        payload["ok"] = findings.ok
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if findings.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
