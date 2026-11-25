"""Append this round's findings to README.md and docs/VERIFY.md (UTF-8 safe)."""
import io

README = "README.md"
VERIFY = "docs/VERIFY.md"

README_SECTION = """
## 本轮：正在播放页与应用背景也能被 Lua 驱动

### 客户端新暴露的令牌（`E:\\projects\\lazer_nextgen`）

| 令牌 | 默认 | 作用 |
| --- | --- | --- |
| `nowPlayingArtworkFraction` / `Min` / `Max` | 0 / 0 / 0 | 左栏宽 = `clamp(W × fraction, min, max)`；0 沿用内置等比两栏 |
| `nowPlayingSidePadding` / `…Max` | 0 / 0 | 监听画布左右留白；0 跟随 4% clamp 28–80 |
| `nowPlayingTitleSize` / `SubtitleSize` / `MetaSize` | 0 / 0 / 0 | 曲名 / 翻译 / 歌手字号；0 跟随 22-26-32 / 12-14-15 / 14-17-19 档位 |
| `nowPlayingCoverRadius` | 0 | 封面圆角；0 = 直角，同时去掉封面投影 |
| `nowPlayingDockHeight` | 0 | 底部传输 dock 高度 |
| `backgroundPlayMode` | `""` | `off` = **完全不构建专辑色流**，画布直接铺 `colors.background` |
| `backgroundOpacity` / `backgroundBlurSigma` / `backgroundVeilAlpha` | 1 / -1 / -1 | 背景层不透明度、模糊、遮罩；-1 表示沿用用户设置 |

`desktop_artwork_layout.dart` 新增了皮肤版心：给了 `nowPlayingArtworkFraction`
就按参考实现的「左栏 + 32px + 1px 竖发丝线 + 16px + 右栏」排；没给则完全保持
原来的居中两栏。折叠阅读面（封面居中放大）的弹簧动画两种模式都有。

三处顺带修正，都是「不做就无法 1:1」的硬前提：

1. **歌词墨色**（`lib/lyrics/viewport.dart`）原本写死 `Colors.white`，纸面浅色
   画布上等于看不见；现在取皮肤解析出的 `label`。
2. **播放页强制深色**（`lib/player/now_playing_page.dart`）原本固定
   `brightness: Brightness.dark`；`backgroundPlayMode == 'off'` 时改为跟随应用明暗，
   并把皮肤令牌传进 `buildAppleTheme(ui:)`。
3. **播放页背景**同样认 `backgroundPlayMode == 'off'`：不再建 `AlbumBlurFlow`，
   不铺黑底，直接一块皮肤画布。

### 一个必须记住的插件侧坑

宿主对 `text_field` 的 `value` 有 **2048 字符**上限。超了不是截断，而是
`FormatException` → 整张页面被拒 → 该插件**整个启动失败**，主题当然也不会应用。
排查时看到的最终错误是「插件启动失败，请检查 Lua 源码。」，而日志顶端才有
`Plugin page text is too long`。

所以「令牌对照表」那一页不再塞整份令牌 JSON（原来那一栏已经涨到 2 KB 以上），
改成 `tokens.key_lines()` 的六行摘要 + `GET /api/theme` 指向完整内容。

同理，不要在模块加载阶段调用异步宿主绑定（例如 `host.update_page_element`）：
`register()` 已经把地址写进页面了，之后再改由 `page_event` 负责。

### 验证

- `dart analyze lib test` → No issues found
- `flutter build windows --debug` → 成功
- `python tools\\verify.py` → 5/5 PASS（icons / manifest / package / lua / zip）
- 截图：`shots/final-home.png`（扁平画布 + 232 侧栏 + clay 强调）、
  `shots/final-now4.png`（正在播放：直角封面、0.34W 左栏、竖发丝线、深墨歌词）
"""

VERIFY_SECTION = """
## 6. 本轮追加：正在播放页 / 背景 / 语义树

```powershell
cd E:\\projects\\lazer_nextgen
dart analyze lib test          # No issues found
flutter build windows --debug  # 成功
```

正在播放页验收（`shots/final-now4.png`）：

- 封面直角、左栏 = `clamp(0.34W, 240, 440)`
- 左栏与右栏之间一条 1px 竖发丝线，间距 32 + 16
- 画布 `#F0EEE6`，无专辑色流、无毛玻璃、无封面投影
- 歌词为深墨 `label`（原来是写死的纯白，在浅色画布上不可读）

无障碍树报错 `Failed to update ui::AXTree, error: N will not be in the tree`：
这是引擎侧 `accessibility_bridge` 的桥接错误，触发条件是语义树里出现了
「父节点已被排除、子节点仍在」的孤立容器节点。本轮把两处高频重建的控件
（`AccessibleIconButton` / `SemanticsPortal`）从 `Semantics(container: true)`
改成合并语义（`container: false`），不再产生额外的容器节点。若仍复现，需要
接一个真实 AT 客户端（UIA 订阅）才能稳定复现并定位到具体控件。
"""


def append(path, text):
    with io.open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("appended", len(text), "chars to", path)


append(README, README_SECTION)
append(VERIFY, VERIFY_SECTION)
