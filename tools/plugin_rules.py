#!/usr/bin/env python3
"""Shared manifest / package rules for the Lazer Lua plugin toolchain.

Single source of truth for the numbers the client enforces, so check_manifest.py,
check_package.py and build_zip.py cannot drift apart:

  docs  E:\\projects\\lazer_nextgen\\docs\\lua-plugins.md
  site  E:\\projects\\lazer_web\\docs\\index.html  (清单字段 / 权限清单 / 包结构)
  code  E:\\projects\\lazer_web\\scripts\\check-plugins.mjs  (market side id/version)

Nothing here touches the filesystem; the checks live in the individual tools.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------- manifest ----

ID_RE = re.compile(r"^[a-z][a-z0-9_.-]{2,79}$")
PROVIDER_RE = re.compile(r"^[a-z][a-z0-9_-]{1,39}$")
# SemVer 2.0.0 core, optional pre-release / build metadata. The marketplace
# listing regex is stricter (no build metadata); see VERSION_MARKET_RE.
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
                        r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
                        r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
                        r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$")
VERSION_MARKET_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")

NAME_MAX = 100
API_VERSION = 1
RESERVED_PROVIDERS = {"local"}

# Capability names the client understands (docs: 能力对照表 + player_events +
# exportCookie). Comparison ignores case and -/_ separators.
CAPABILITIES = {
    "search",
    "browseAlbums",
    "savedAlbums",
    "playlists",
    "editPlaylists",
    "favorites",
    "lyrics",
    "scrobble",
    "recommendations",
    "comments",
    "listenTogether",
    "radio",
    "charts",
    "homeFeed",
    "player_events",
    "exportCookie",
}
# Operations that authors sometimes mistake for capabilities: the client ignores
# unknown names but the entry never appears, so they are worth reporting.
CAPABILITY_TRAPS = {
    "album": "browseAlbums",
    "albums": "browseAlbums",
    "albumSongs": "browseAlbums",
    "artistSongs": "browseAlbums",
    "artistAlbums": "browseAlbums",
    "artist": "browseAlbums",
    "playlist": "playlists",
    "playlistSongs": "playlists",
    "home_feed": "homeFeed",
    "saved_albums": "savedAlbums",
    "listen_together": "listenTogether",
    "player_event": "player_events",
    "playerEvents": "player_events",
    "favorite": "favorites",
    "scrobbles": "scrobble",
    "stream": "search",
    "song": "search",
}
# Names that are not capabilities at all, with the reason (reported verbatim).
CAPABILITY_NOTES = {
    "theme": "主题不写进 capabilities：在 describe 里返回 theme=true，客户端会另外调用 theme 操作；"
             "这个名字会被客户端忽略（不影响启动）",
}

AUTH_MODES = {"qr", "sms", "password", "cookie", "exportCookie"}
DATA_SCOPES = {"library", "profile", "history", "native_audio", "native_control"}

# permissions.<key> -> (kind, max entries / None, description)
# kind: hosts | endpoints | data | flag
PERMISSION_SPECS: dict[str, tuple[str, int | None, str]] = {
    "network": ("hosts", 32, "host.http / host.http_json 的目标主机"),
    "socket": ("hosts", 32, "TCP 连接目标；为空时回退 network"),
    "socketServer": ("endpoints", 16, "TCP 监听地址 host:port"),
    "websocket": ("hosts", 32, "WebSocket 连接目标"),
    "websocketServer": ("endpoints", 16, "WebSocket 监听地址 host:port"),
    "storage": ("flag", None, "键值存储 host.storage_*"),
    "filesystem": ("flag", None, "文件沙箱 host.file / host.files"),
    "data": ("data", 5, "本地资料权限"),
}
# Documented aliases: filesystem is also accepted as files / file.
PERMISSION_ALIASES = {"files": "filesystem", "file": "filesystem"}

# ----------------------------------------------------------------- package ----

MAX_FILES = 256
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
MAX_ZIP_BYTES = 16 * 1024 * 1024
MAX_PATH_CHARS = 200
MAX_PATH_DEPTH = 12

TEXT_EXTENSIONS = {".lua", ".json", ".md", ".txt", ".html", ".css", ".js", ".svg"}
ROOT_ONLY_NAMES = {"license"}
IGNORED_NAMES = {"__MACOSX", ".DS_Store", "Thumbs.db", ".ds_store", "thumbs.db"}
IGNORED_NAME_SET = {name.lower() for name in IGNORED_NAMES}

BAD_PATH_CHARS = set('<>"|?*')
CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")

# ---------------------------------------------------------------- host rules ---

# The client ships "a small public suffix table" so that `*.co.uk` is rejected
# while `*.example.co.uk` is accepted. This mirrors that shape.
PUBLIC_SUFFIXES = {
    # united kingdom
    "ac.uk", "co.uk", "gov.uk", "ltd.uk", "me.uk", "net.uk", "nhs.uk", "org.uk",
    "plc.uk", "police.uk", "sch.uk",
    # china / hong kong / taiwan
    "ac.cn", "com.cn", "edu.cn", "gov.cn", "net.cn", "org.cn",
    "com.hk", "edu.hk", "gov.hk", "idv.hk", "net.hk", "org.hk",
    "com.tw", "edu.tw", "gov.tw", "idv.tw", "net.tw", "org.tw",
    # japan / korea
    "ac.jp", "ad.jp", "co.jp", "ed.jp", "go.jp", "gr.jp", "lg.jp", "ne.jp", "or.jp",
    "ac.kr", "co.kr", "go.kr", "mil.kr", "ne.kr", "or.kr", "pe.kr", "re.kr",
    # south-east asia
    "com.sg", "edu.sg", "gov.sg", "net.sg", "org.sg",
    "ac.id", "co.id", "go.id", "mil.id", "or.id", "sch.id", "web.id",
    "com.my", "edu.my", "gov.my", "net.my", "org.my",
    "com.ph", "edu.ph", "gov.ph", "net.ph", "org.ph",
    "ac.th", "co.th", "go.th", "in.th", "net.th", "or.th",
    "com.vn", "edu.vn", "gov.vn", "net.vn", "org.vn",
    # oceania
    "asn.au", "com.au", "edu.au", "gov.au", "id.au", "net.au", "org.au",
    "ac.nz", "co.nz", "geek.nz", "govt.nz", "net.nz", "org.nz", "school.nz",
    # americas
    "art.br", "blog.br", "com.br", "edu.br", "gov.br", "net.br", "org.br",
    "com.ar", "edu.ar", "gob.ar", "net.ar", "org.ar",
    "com.mx", "edu.mx", "gob.mx", "net.mx", "org.mx",
    "com.co", "edu.co", "gov.co", "net.co", "org.co",
    "com.ec", "com.pe", "com.ve", "com.uy",
    # india / middle east / africa
    "ac.in", "co.in", "edu.in", "firm.in", "gen.in", "gov.in", "ind.in", "net.in",
    "org.in", "res.in",
    "ac.il", "co.il", "gov.il", "muni.il", "net.il", "org.il",
    "com.ae", "com.sa", "com.eg", "com.tr", "edu.tr", "gov.tr", "net.tr", "org.tr",
    "ac.ke", "co.ke", "go.ke", "ne.ke", "or.ke",
    "co.za", "gov.za", "net.za", "org.za", "web.za",
    "com.ng", "edu.ng", "gov.ng", "net.ng", "org.ng",
    # europe
    "com.pl", "net.pl", "org.pl",
    "com.ua", "edu.ua", "gov.ua", "net.ua", "org.ua",
    "com.ru", "net.ru", "org.ru",
    "com.gr", "edu.gr", "gov.gr", "net.gr", "org.gr",
}

# Single-label TLDs worth naming in error messages (the wildcard rule itself only
# needs "two labels minimum").
COMMON_TLDS = {
    "com", "net", "org", "edu", "gov", "mil", "int", "info", "biz", "name", "pro",
    "mobi", "asia", "xyz", "top", "site", "online", "store", "tech", "shop", "app",
    "dev", "cloud", "space", "website", "live", "life", "world", "zone", "page",
    "link", "click", "fun", "media", "network", "digital", "studio", "design",
    "codes", "art", "blog", "wiki", "group", "team", "club", "icu", "vip", "work",
    "cn", "uk", "jp", "kr", "tw", "hk", "sg", "au", "nz", "in", "id", "my", "ph",
    "th", "vn", "br", "ar", "mx", "co", "pe", "cl", "za", "ng", "ke", "eg", "sa",
    "ae", "tr", "il", "pl", "ua", "ru", "gr", "de", "fr", "it", "es", "nl", "be",
    "ch", "at", "se", "no", "fi", "dk", "ie", "pt", "cz", "sk", "hu", "ro", "bg",
    "us", "ca", "io", "me", "tv", "cc", "ws", "fm", "ai", "sh", "gg", "to", "ly",
    "gl", "ink", "one", "run", "lol", "gay", "page",
}

LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def normalize_name(value: str) -> str:
    """Capability comparison ignores case and -/_ separators."""
    return re.sub(r"[-_\s]", "", value).lower()


CANONICAL_CAPABILITIES = {normalize_name(name): name for name in CAPABILITIES}


def capability_canonical(value: str) -> str | None:
    return CANONICAL_CAPABILITIES.get(normalize_name(value))


# -------------------------------------------------------------------- paths ---


def path_problems(rel: str) -> list[str]:
    """Return human readable reasons why a package-relative path is unsafe."""
    problems: list[str] = []
    if not rel:
        return ["路径为空"]
    if len(rel) > MAX_PATH_CHARS:
        problems.append(f"路径长度 {len(rel)} 超过 {MAX_PATH_CHARS} 字符")
    if "\\" in rel:
        problems.append("路径含反斜杠 \\（包内一律使用正斜杠）")
    if WINDOWS_DRIVE_RE.match(rel):
        problems.append("路径以盘符开头")
    if rel.startswith("/"):
        problems.append("路径以 / 开头")
    if CONTROL_CHAR_RE.search(rel):
        problems.append("路径含控制字符")
    bad = sorted({ch for ch in rel if ch in BAD_PATH_CHARS})
    if bad:
        problems.append("路径含非法字符 " + " ".join(bad))
    segments = rel.split("/")
    if len(segments) > MAX_PATH_DEPTH:
        problems.append(f"目录层级 {len(segments)} 超过 {MAX_PATH_DEPTH}")
    for segment in segments:
        if segment in ("",):
            problems.append("路径含空目录段（// 或结尾 /）")
        elif segment in (".", ".."):
            problems.append(f"路径含 {segment} 段")
        elif segment.endswith(".") or segment.endswith(" "):
            problems.append(f"路径段 {segment!r} 以点或空格结尾")
    return problems


def is_ignored(rel: str) -> bool:
    """Packaging droppings the client ignores anyway (__MACOSX/, .DS_Store, Thumbs.db)."""
    for segment in rel.split("/"):
        if segment.lower() in IGNORED_NAME_SET:
            return True
    return False


def file_type_allowed(rel: str) -> tuple[bool, str]:
    """Whitelist from the docs: manifest.json, *.lua, text assets, root LICENSE."""
    name = rel.rsplit("/", 1)[-1]
    lowered = name.lower()
    suffix = "." + lowered.rsplit(".", 1)[-1] if "." in lowered else ""
    depth = rel.count("/")

    if lowered in ("__macosx",):
        return False, "打包杂物 __MACOSX"
    if lowered == "manifest.json":
        return (depth == 0), "manifest.json 必须在 ZIP 根目录"
    if lowered == "license":
        return (depth == 0), "LICENSE 只能在包根目录"
    if suffix in TEXT_EXTENSIONS:
        return True, ""
    return False, f"扩展名 {suffix or '(无)'} 不在白名单（manifest.json / *.lua / .json .md .txt .html .css .js .svg / 根 LICENSE）"


# -------------------------------------------------------------------- hosts ----


def split_host_port(entry: str) -> tuple[str, str | None, str | None]:
    """Split `host`, `host:port`, `[v6]:port` -> (host, port or None, error or None)."""
    text = entry.strip()
    if not text:
        return "", None, "条目为空"
    if "://" in text:
        return "", None, "不能带协议前缀（只写主机名，请求必须是 HTTPS）"
    if "/" in text:
        return "", None, "不能带路径"
    if "@" in text:
        return "", None, "不能带用户名或密码"
    if any(ch.isspace() for ch in text):
        return "", None, "不能含空白字符"
    if text.startswith("["):
        end = text.find("]")
        if end < 0:
            return "", None, "IPv6 地址缺少 ]"
        host = text[: end + 1]
        rest = text[end + 1 :]
        if rest == "":
            return host, None, None
        if not rest.startswith(":"):
            return "", None, "地址后缀只能是 :端口"
        return host, rest[1:], None
    if text.count(":") > 1:
        return "", None, "IPv6 地址需要写成 [::1]:端口"
    if ":" in text:
        host, _, port = text.rpartition(":")
        return host, port, None
    return text, None, None


def validate_port(port: str, *, allow_zero: bool) -> str | None:
    if not port.isdigit():
        return f"端口 {port!r} 不是数字"
    value = int(port)
    if value > 65535:
        return f"端口 {value} 超出 0–65535"
    if value == 0 and not allow_zero:
        return "端口 0 只用于监听地址（系统分配临时端口）"
    if value == 0:
        return None
    if value < 1:
        return f"端口 {value} 无效"
    return None


def validate_dns_host(host: str, *, allow_wildcard: bool) -> list[str]:
    """Validate a hostname (optionally `*.` prefixed) used in permissions.network."""
    problems: list[str] = []
    if host != host.lower():
        problems.append("主机名含大写字母；匹配是精确的，请写小写")
    lowered = host.lower()

    wildcard = lowered.startswith("*.")
    if "*" in lowered and not wildcard:
        problems.append("只支持 *. 前缀通配，不支持中间或后缀通配")
        return problems

    body = lowered[2:] if wildcard else lowered
    if not body:
        problems.append("通配符后面缺少域名")
        return problems
    if body.startswith("["):
        # A bracketed IPv6 literal is a legal host; it just never matches a wildcard.
        import ipaddress

        try:
            ipaddress.IPv6Address(body[1:-1] if body.endswith("]") else body[1:])
        except ValueError:
            problems.append("IPv6 字面量格式错误")
        else:
            if wildcard:
                problems.append("IPv6 字面量不能与 *. 通配一起使用")
        return problems
    if ":" in body:
        problems.append("IPv6 地址需要写成 [::1]:端口")
        return problems
    if body.endswith("."):
        problems.append("主机名不能以点结尾")
        return problems

    labels = body.split(".")
    if any(label == "" for label in labels):
        problems.append("主机名含空标签（连续的点）")
    for label in labels:
        if label and not LABEL_RE.match(label):
            if len(label) > 63:
                problems.append(f"标签 {label!r} 超过 63 字符")
            elif label.startswith("-") or label.endswith("-"):
                problems.append(f"标签 {label!r} 不能以连字符开头或结尾")
            elif not re.match(r"^[a-z0-9-]+$", label):
                problems.append(f"标签 {label!r} 含非法字符（只允许 a-z 0-9 -）")
    if len(body) > 253:
        problems.append("主机名超过 253 字符")

    if wildcard:
        if len(labels) < 2:
            problems.append(
                f"*.{body} 无效：通配必须落在可注册域名上，至少要写成 *.example.{body} 这样的两级以上域名"
            )
        else:
            tail2 = ".".join(labels[-2:])
            if tail2 in PUBLIC_SUFFIXES and len(labels) < 3:
                problems.append(
                    f"*.{body} 无效：{tail2} 是公共后缀，通配必须落在可注册域名上，"
                    f"例如 *.example.{tail2}"
                )
        if body in PUBLIC_SUFFIXES:
            problems.append(f"*.{body} 无效：{body} 是公共后缀")
        if len(labels) == 1 and labels[0] in COMMON_TLDS:
            problems.append(f"*.{body} 无效：{body} 是顶级域")
    return problems


def validate_listen_host(host: str) -> list[str]:
    """监听地址必须是明确的 IPv4/IPv6 字面量或 localhost，不支持通配域名。"""
    problems: list[str] = []
    lowered = host.lower()
    if lowered.startswith("[") and lowered.endswith("]"):
        inner = lowered[1:-1]
        if ":" not in inner:
            problems.append("IPv6 字面量格式错误")
        return problems
    if lowered == "localhost":
        return problems
    if "*" in lowered:
        problems.append("监听地址不支持通配域名")
        return problems
    parts = lowered.split(".")
    if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
        return problems
    problems.append(
        f"监听地址 {host!r} 必须是明确的 IP 地址或 localhost（不支持域名与通配）"
    )
    return problems


def mentions_public_suffix_hint(host: str) -> str:
    labels = host.lower().lstrip("*.").split(".")
    if len(labels) >= 2:
        tail2 = ".".join(labels[-2:])
        if tail2 in PUBLIC_SUFFIXES:
            return f"（{tail2} 是公共后缀，需要写完整的三级域名，如 *.example.{tail2}）"
    return ""


def collect_files(root: "pathlib.Path"):
    """Return ([(rel, path, size)], [ignored_rel]) with forward-slash relative paths.

    Packaging droppings (__MACOSX/, .DS_Store, Thumbs.db) are separated out: the
    client ignores them, so the tools report them but never fail on them.
    """
    import pathlib

    root = pathlib.Path(root)
    files: list[tuple[str, "pathlib.Path", int]] = []
    ignored: list[str] = []
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix().lower()):
        if path.is_dir():
            continue
        rel = path.relative_to(root).as_posix()
        if is_ignored(rel):
            ignored.append(rel)
            continue
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        files.append((rel, path, size))
    return files, ignored


# ----------------------------------------------------------------- findings ---

class Findings:
    """Tiny three-level reporter shared by the check scripts."""

    def __init__(self, title: str):
        self.title = title
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.notes: list[tuple[str, str]] = []
        self.checks = 0

    def error(self, rule: str, message: str) -> None:
        self.errors.append((rule, message))

    def warn(self, rule: str, message: str) -> None:
        self.warnings.append((rule, message))

    def note(self, rule: str, message: str) -> None:
        self.notes.append((rule, message))

    def expect(self, condition: bool, rule: str, message: str) -> bool:
        """Count a checked rule; log an error when it fails."""
        self.checks += 1
        if not condition:
            self.error(rule, message)
        return condition

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def counts(self) -> tuple[int, int, int]:
        return len(self.errors), len(self.warnings), len(self.notes)

    def emit(self, *, show_notes: bool = True) -> None:
        for rule, message in self.errors:
            print(f"error  [{rule}] {message}")
        for rule, message in self.warnings:
            print(f"warn   [{rule}] {message}")
        if show_notes:
            for rule, message in self.notes:
                print(f"note   [{rule}] {message}")

    def summary(self) -> str:
        errors, warnings, notes = self.counts
        return (f"{self.checks} 条规则 / {errors} error / {warnings} warn / {notes} note"
                f"  ->  {'PASS' if self.ok else 'FAIL'}")

    def as_dict(self) -> dict:
        return {
            "title": self.title,
            "ok": self.ok,
            "checks": self.checks,
            "errors": [{"rule": r, "message": m} for r, m in self.errors],
            "warnings": [{"rule": r, "message": m} for r, m in self.warnings],
            "notes": [{"rule": r, "message": m} for r, m in self.notes],
        }
