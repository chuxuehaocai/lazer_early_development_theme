#!/usr/bin/env python3
"""Parse every plugin/**/*.lua with luaparser and run the conservative static checks.

Per file:
  * AST parses (luaparser, installed via pip) - a syntax error is a hard failure
  * every `host.<name>` must be a documented host API (the list below is copied
    from docs/lua-plugins.md, host 接口表 + 工具函数 + 页面编辑 + 权限/资料接口),
    and the check is scope aware: a file that defines `local function load()` is
    not reported for calling it
  * dynamic loading is rejected: io.*, os.*, load, loadstring, dofile, loadfile,
    and require() with anything but a string literal; a literal require must
    resolve to a .lua file inside the package (`lib.tokens` -> lib/tokens.lua)
  * string concatenation inside an inner loop (nesting >= 2) is reported as a
    warning - the host runs every call on one serial VM with a time budget

Usage:
  python tools\\check_lua.py [--plugin-dir plugin] [--strict] [--json] [--require]
                             [--quiet]

Exit code 1 means a parse failure or an error-level finding. A missing plugin
directory prints SKIP and exits 0 unless --require is passed.
"""

from __future__ import annotations

import argparse
import difflib
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

try:
    from luaparser import ast as lua_ast
    from luaparser import astnodes
    HAVE_LUAPARSER = True
except ImportError:  # pragma: no cover - reported, never fatal
    HAVE_LUAPARSER = False
    lua_ast = None
    astnodes = None

# Everything Lua can call on `host`, straight from the docs.
ALLOWED_HOST: dict[str, str] = {
    # 网络 / 连接
    "http": "HTTPS 请求，需 permissions.network",
    "http_json": "HTTPS 请求并解析 JSON",
    "socket": "TCP 连接，需 permissions.socket",
    "socket_server": "TCP 监听，需 permissions.socketServer",
    "websocket": "WebSocket 连接，需 permissions.websocket",
    "websocket_server": "WebSocket 监听，需 permissions.websocketServer",
    # 编解码 / 工具
    "crypto": "md5/sha1/sha256/hmac/base64/xor/zlib/krc_decode/aes/rsa_modpow",
    "json_encode": "JSON 编码",
    "json_decode": "JSON 解码",
    "url_encode": "URL 百分号编码",
    "url_decode": "URL 百分号解码",
    "cookie_compact": "规范化 Cookie 头",
    "cookie_field": "读取 Cookie 字段",
    "cookie_merge": "合并 Set-Cookie",
    "random_hex": "随机十六进制串",
    "now": "Unix 毫秒时间",
    "sleep": "异步挂起 0-60s",
    "log": "写宿主诊断日志",
    "timer": "周期回调，100-60000ms，最多 4 个",
    # 持久化
    "storage_get": "读取插件键值存储",
    "storage_set": "写入插件键值存储",
    "storage_keys": "枚举键",
    "storage_clear": "清空键值存储",
    # 文件沙箱
    "file": "沙箱文件读写，需 permissions.filesystem",
    "files": "批量文件操作",
    # 包内资源
    "resource": "读取包内文本资源",
    "read_resource": "读取包内文本资源",
    "resource_keys": "枚举包内资源",
    # 自省
    "info": "插件与宿主信息",
    "plugin_info": "插件与宿主信息",
    "permissions": "已声明/已获准的数据权限",
    "request_permission": "请求一个数据权限",
    # 界面
    "add_setting": "注册设置项",
    "add_page": "注册插件页面",
    "page": "读取页面描述",
    "pages": "列出页面概要",
    "update_page": "改写页面布局",
    "set_page_elements": "整体替换控件",
    "add_page_element": "新增控件",
    "update_page_element": "局部改写控件",
    "remove_page_element": "删除控件",
    "move_page_element": "调整控件顺序",
    "add_player_menu_item": "注册正在播放菜单项",
    # 播放器
    "player_control": "播放控制",
    "player_state": "播放状态",
    "player_status": "播放状态",
    "player_queue": "队列",
    "player_track": "当前歌曲",
    "player_lyrics": "当前歌词",
    "player_recent": "最近播放（需 history）",
    # 资料库 / 账号 / 原生
    "library": "资料库读取（需 library）",
    "search": "本地音乐搜索（需 library）",
    "user": "账号资料与统计（需 profile/history）",
    "native": "受限原生能力",
}

FORBIDDEN_GLOBALS = {
    "load": "宿主沙箱不提供 load",
    "loadstring": "宿主沙箱不提供 loadstring",
    "dofile": "宿主沙箱不提供文件系统",
    "loadfile": "宿主沙箱不提供文件系统",
}
FORBIDDEN_NAMESPACES = {
    "io": "宿主沙箱不提供 io",
    "os": "宿主沙箱不提供 os（时间用 host.now，等待用 host.sleep）",
}

LOOP_NODES = {"Fornum", "Forin", "While", "Repeat"}
SCOPE_NODES = {"Chunk", "Block"}
FUNCTION_NODES = {"Function", "LocalFunction", "AnonymousFunction", "Method"}


def as_list(value) -> list:
    """luaparser sometimes stores a single node where a list is expected."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def node_children(node):
    """Generic child iteration; luaparser nodes keep their fields in __dict__."""
    for value in vars(node).values():
        if isinstance(value, astnodes.Node):
            yield value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, astnodes.Node):
                    yield item


def string_value(node) -> str | None:
    """Decode a luaparser String literal (b'...' bytes) to text."""
    if isinstance(node, astnodes.String):
        raw = node.s
        if isinstance(raw, bytes):
            for encoding in ("utf-8", "latin-1"):
                try:
                    return raw.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return raw.decode("utf-8", "replace")
        return str(raw)
    return None


def name_value(node) -> str | None:
    """Name, or a constant string key (`host["http"]`)."""
    if isinstance(node, astnodes.Name):
        return node.id
    return string_value(node)


def param_names(node) -> set[str]:
    names: set[str] = set()
    for argument in as_list(getattr(node, "args", None)):
        target = getattr(argument, "name", None)
        if isinstance(target, astnodes.Name):
            names.add(target.id)
    return names


def resolve_module(plugin_dir: pathlib.Path, module: str) -> pathlib.Path | None:
    """`lib.tokens` / `lib/tokens` / `lib/tokens.lua` -> the file inside the package."""
    for candidate in (
        plugin_dir / f"{module.replace('.', '/')}.lua",
        plugin_dir / f"{module}.lua",
    ):
        try:
            candidate.resolve().relative_to(plugin_dir.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    return None


class FileChecker:
    """Scope-aware walker: reports host/io/os/require/concat problems for one file."""

    def __init__(self, plugin_dir: pathlib.Path, rel: str, findings: R.Findings):
        self.plugin_dir = plugin_dir
        self.rel = rel
        self.findings = findings
        self.nodes = 0
        self.host_aliases: set[str] = set()
        self.concat_lines: dict[int, int] = {}
        self.shadowed_host_reported = False

    # -- helpers ---------------------------------------------------------
    def where(self, node) -> str:
        return f"{self.rel}:{getattr(node, 'line', 0) or 0}"

    def is_global(self, name: str, scope: set[str]) -> bool:
        return name not in scope

    # -- traversal -------------------------------------------------------
    def run(self, tree) -> None:
        self.host_aliases = self.collect_host_aliases(tree)
        self.visit(tree, set(), 0)
        for line, count in sorted(self.concat_lines.items()):
            self.findings.warn(
                "perf",
                f"{self.rel}:{line} 内层循环里有字符串拼接（{count} 处 ..）：宿主是单线程"
                "串行 VM，建议先拼到 table 再 table.concat",
            )

    def collect_host_aliases(self, tree) -> set[str]:
        aliases: set[str] = set()
        stack = [tree]
        while stack:
            node = stack.pop()
            if type(node).__name__ in ("LocalAssign", "Assign"):
                targets = as_list(getattr(node, "targets", None))
                values = as_list(getattr(node, "values", None))
                if (len(values) == 1 and isinstance(values[0], astnodes.Name)
                        and values[0].id == "host"):
                    aliases.update(t.id for t in targets if isinstance(t, astnodes.Name))
            stack.extend(node_children(node))
        return aliases

    def visit(self, node, scope: set[str], loop_depth: int) -> None:
        if node is None or not isinstance(node, astnodes.Node):
            # Fornum.step and a few fields may hold raw ints/strings.
            return
        kind = type(node).__name__

        if kind in LOOP_NODES:
            loop_depth += 1

        # --- declarations that change the visible scope -------------------
        if kind == "LocalAssign":
            for value in as_list(getattr(node, "values", None)):
                self.visit(value, scope, loop_depth)
            for target in as_list(getattr(node, "targets", None)):
                if isinstance(target, astnodes.Name):
                    scope.add(target.id)
            return

        if kind == "LocalFunction":
            name = getattr(node, "name", None)
            if isinstance(name, astnodes.Name):
                scope.add(name.id)
            inner = set(scope) | param_names(node)
            self.visit(getattr(node, "body", None), inner, loop_depth)
            return

        if kind in SCOPE_NODES:
            inner = set(scope)
            for statement in as_list(getattr(node, "body", None)):
                self.visit(statement, inner, loop_depth)
            return

        if kind in ("Function", "AnonymousFunction", "Method"):
            inner = set(scope) | param_names(node)
            self.visit(getattr(node, "body", None), inner, loop_depth)
            return

        if kind == "Fornum":
            for field in ("start", "stop", "step"):
                self.visit(getattr(node, field, None), scope, loop_depth)
            inner = set(scope)
            target = getattr(node, "target", None)
            if isinstance(target, astnodes.Name):
                inner.add(target.id)
            self.visit(getattr(node, "body", None), inner, loop_depth)
            return

        if kind == "Forin":
            for value in as_list(getattr(node, "iter", None)):
                self.visit(value, scope, loop_depth)
            inner = set(scope)
            for target in as_list(getattr(node, "targets", None)):
                if isinstance(target, astnodes.Name):
                    inner.add(target.id)
            self.visit(getattr(node, "body", None), inner, loop_depth)
            return

        self.nodes += 1
        self.inspect(node, scope, loop_depth)
        for child in node_children(node):
            self.visit(child, scope, loop_depth)

    # -- checks ----------------------------------------------------------
    def inspect(self, node, scope: set[str], loop_depth: int) -> None:
        findings = self.findings

        if isinstance(node, astnodes.Index) and isinstance(node.value, astnodes.Name):
            owner = node.value.id
            api = name_value(node.idx)

            if owner == "host" and not self.is_global("host", scope):
                if not self.shadowed_host_reported:
                    self.shadowed_host_reported = True
                    findings.note("host", f"{self.where(node)} host 被局部变量遮蔽，跳过 host 校验")
            elif owner == "host" or owner in self.host_aliases:
                if api is None:
                    findings.warn("host", f"{self.where(node)} host[...] 用了动态键，无法静态校验")
                elif api not in ALLOWED_HOST:
                    suggestion = difflib.get_close_matches(api, ALLOWED_HOST, n=1)
                    hint = f"，是不是 {suggestion[0]!r}？" if suggestion else ""
                    findings.error(
                        "host",
                        f"{self.where(node)} host.{api} 不在允许的 host 接口清单里{hint}",
                    )
                else:
                    findings.checks += 1

            if owner in FORBIDDEN_NAMESPACES and self.is_global(owner, scope):
                findings.error(
                    "sandbox",
                    f"{self.where(node)} 使用了 {owner}.{api or '?'}："
                    f"{FORBIDDEN_NAMESPACES[owner]}",
                )

        if isinstance(node, astnodes.Concat) and loop_depth >= 2:
            line = getattr(node, "line", 0) or 0
            self.concat_lines[line] = self.concat_lines.get(line, 0) + 1

        if not isinstance(node, astnodes.Call):
            return

        func = node.func
        callee = None
        if isinstance(func, astnodes.Name):
            callee = func.id
        elif isinstance(func, astnodes.Index) and isinstance(func.value, astnodes.Name):
            owner = func.value.id
            if owner in FORBIDDEN_NAMESPACES and self.is_global(owner, scope):
                findings.error(
                    "sandbox",
                    f"{self.where(node)} 调用了 {owner}.{name_value(func.idx) or '?'}()："
                    f"{FORBIDDEN_NAMESPACES[owner]}",
                )

        if callee is None or not self.is_global(callee, scope):
            return
        if callee in FORBIDDEN_GLOBALS:
            findings.error(
                "sandbox",
                f"{self.where(node)} 调用了 {callee}()：{FORBIDDEN_GLOBALS[callee]}",
            )
            return
        if callee in FORBIDDEN_NAMESPACES:
            findings.error(
                "sandbox",
                f"{self.where(node)} 调用了 {callee}()：{FORBIDDEN_NAMESPACES[callee]}",
            )
            return
        if callee != "require":
            return

        args = as_list(getattr(node, "args", None))
        if len(args) != 1:
            findings.error(
                "require",
                f"{self.where(node)} require() 需要且只接受一个字符串字面量参数",
            )
            return
        module = string_value(args[0])
        if module is None:
            findings.error(
                "require",
                f"{self.where(node)} require() 的参数不是字符串字面量；宿主只加载包内静态模块",
            )
            return
        findings.checks += 1
        if resolve_module(self.plugin_dir, module) is None:
            findings.warn(
                "require",
                f"{self.where(node)} require({module!r}) 在包里找不到对应 .lua"
                "（按 module.name → module/name.lua 解析）",
            )


def check_file(
    plugin_dir: pathlib.Path,
    path: pathlib.Path,
    findings: R.Findings,
    *,
    quiet: bool,
) -> tuple[bool, int, int]:
    rel = path.relative_to(plugin_dir).as_posix()
    before_errors = len(findings.errors)
    before_warnings = len(findings.warnings)

    try:
        source = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        findings.error("lua", f"{rel}: 无法读取：{exc}")
        return False, 0, 0
    if "\x00" in source:
        findings.error("lua", f"{rel}: 文件含 NUL 字节，不是文本 Lua 源码")
        return False, 0, 0

    line_count = source.count("\n") + 1
    try:
        tree = lua_ast.parse(source)
    except Exception as exc:  # luaparser raises antlr / SyntaxException variants
        message = " ".join(str(exc).split())
        findings.error("syntax", f"{rel}: AST 解析失败：{message[:400]}")
        return False, line_count, 0

    findings.checks += 1
    checker = FileChecker(plugin_dir, rel, findings)
    checker.run(tree)

    new_errors = len(findings.errors) - before_errors
    new_warnings = len(findings.warnings) - before_warnings
    if not quiet:
        status = "OK  " if new_errors == 0 else "ERR "
        extra = f"  ({new_errors} error, {new_warnings} warn)" if (new_errors or new_warnings) else ""
        print(f"  {status} {rel:<28} {line_count:>5} 行 {checker.nodes:>6} 节点{extra}")
    return True, line_count, checker.nodes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse and statically check plugin/**/*.lua.")
    parser.add_argument("--plugin-dir", default=None, help="插件目录（默认 plugin）")
    parser.add_argument("--strict", action="store_true", help="把 warn 级问题也当错误")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    parser.add_argument("--require", action="store_true", help="缺少插件目录 / 没有 lua 时视为失败")
    parser.add_argument("--quiet", action="store_true", help="只打印问题，不打印每个文件的状态")
    args = parser.parse_args(argv)

    plugin_dir = pathlib.Path(args.plugin_dir) if args.plugin_dir else REPO / "plugin"
    findings = R.Findings("check_lua")

    if not plugin_dir.is_dir():
        print(f"SKIP 插件目录不存在：{plugin_dir}")
        if args.require:
            return 1
        return 0

    if not HAVE_LUAPARSER:
        print("SKIP luaparser 未安装：python -m pip install luaparser")
        return 1 if args.require else 0

    lua_files = sorted(plugin_dir.rglob("*.lua"), key=lambda p: p.as_posix().lower())
    if not lua_files:
        print(f"SKIP {plugin_dir} 下没有 .lua 文件")
        return 1 if args.require else 0

    print(f"lua      {plugin_dir}  ({len(lua_files)} 个文件)")
    failed: list[str] = []
    total_lines = 0
    total_nodes = 0
    for path in lua_files:
        ok, lines, nodes = check_file(plugin_dir, path, findings, quiet=args.quiet)
        total_lines += lines
        total_nodes += nodes
        if not ok:
            failed.append(path.relative_to(plugin_dir).as_posix())

    if args.strict:
        for rule, message in list(findings.warnings):
            findings.error(rule, message)
        findings.warnings.clear()

    findings.emit()
    print(
        f"files {len(lua_files)}  parsed {len(lua_files) - len(failed)}  "
        f"lines {total_lines}  nodes {total_nodes}"
    )
    print(findings.summary())

    if args.json:
        payload = findings.as_dict()
        payload.update(
            {
                "pluginDir": str(plugin_dir),
                "files": [p.relative_to(plugin_dir).as_posix() for p in lua_files],
                "parseFailures": failed,
                "hostApiCount": len(ALLOWED_HOST),
            }
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if findings.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
