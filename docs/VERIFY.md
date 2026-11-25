# 验证手册 · Verification

这台机器上「复刻」是可以被完整验证的：参考实现能编译运行，复刻前端能出图，
插件能在真实客户端里跑通 主题 → 插件页 → WebSocket 实时数据。

## 1. 参考真值（Flutter 快照）

```powershell
# 一次性：复制到可写目录再编译（不动原始快照）
robocopy E:\Lazer-3fdf89b40956d1f90f9bff242b67a8a9129d140e E:\projects\_refsnap_early /E /XD .git build .dart_tool
cd E:\projects\_refsnap_early
flutter pub get
flutter build windows --debug        # 约 3 分钟
```

启动后抓窗口截图（同尺寸下可与复刻截图逐像素比对）：

```powershell
Start-Process .\build\windows\x64\runner\Debug\lazer_nextgen.exe
python tools\capture.py --process lazer_nextgen --title Lazer --out shots\ref-home.png
```

`shots\ref-home.png`（1280×720，深色）是当前的参考真值。实测对照（同一把尺子量两张图）：

| 量 | 参考 | 复刻 |
| --- | --- | --- |
| Hero 两行墨迹高度 | 113 px | 115 px |
| 「推荐歌单」标题墨迹行 | y 248–258 | y 247–257 |
| 侧栏宽 / 标题栏高 | 233 / 41 | 233 / 41 |
| 播放条高 | 103 | 103 |

## 2. 复刻前端（静态）

```powershell
python tools\serve.py --port 8080 --dir plugin\frontend
# 或直接双击 plugin\frontend\index.html（file:// 也可用）
python tools\shot.py "http://127.0.0.1:8080/index.html?still=1#/home" --viewport 1280x720 --out-dir shots\cmp --name home-light
```

`?still=1` 关掉进场动画（headless 的虚拟时间会把 `.view` 冻在 `matrix(.96)` 首帧，
导致所有尺寸少 4%）；`?theme=dark` 切深色；`?measure=1` 把实测几何写进 `<pre id="measure">`，
可 `chrome --headless --dump-dom` 抓取后与 `docs/spec-*.md` 逐项对。

## 3. 插件（真实客户端）

### 3.1 安装到客户端数据目录

Flutter Windows 的 support 目录是 `%APPDATA%\<org>\<app>`（**不是** LocalAppData，
cache 才在 LocalAppData）。本插件：

```powershell
$root = "$env:APPDATA\dev.naominet\lazer_nextgen\lua_plugins\chuxuehaocai.lazer.theme.earlydev"
robocopy plugin $root /E /PURGE
New-Item -ItemType File -Path "$root\.socket-server-enabled" -Force
New-Item -ItemType File -Path "$root\.websocket-server-enabled" -Force
```

授权是「文件存在即授权」：`.socket-server-enabled` / `.websocket-server-enabled` /
`.network-enabled` / `.filesystem-enabled`，数据权限在 `.data-permissions`（JSON 数组）。
不建这两个文件也可以在插件详情里手动打开开关。

### 3.2 验证脚本

```powershell
flutter test test\_tmp_parchment_smoke_test.dart   # 用真实 LuaPluginRuntime 跑 describe/theme/页面/服务器
node tools\host_sim.js --test                       # fengari 宿主模拟器（真实 TCP）
python tools\ws_probe.py --frames 2                 # 握手 ws://127.0.0.1:11581/lazer 并读快照
python tools\verify.py --shots                      # 图标/清单/包/Lua/ZIP/截图 六阶段
```

`ws_probe.py` 的输出就是复刻前端拿到的同一份 JSON：曲目、进度、队列长度、歌词行数、视图配置。

### 3.3 已知的宿主差异（实测，不是猜测）

| 能力 | 实测结果 | 结论 |
| --- | --- | --- |
| `host.socket_server` listen/accept | 正常，能 bind 到 127.0.0.1:11580 并 accept | 可用 |
| `host.socket_server` receive | 恒返回 nil（真实 HTTP 请求收不到），`clients` 里能看到连接 | **当前构建不可用** |
| `host.websocket_server` | 101 握手成功，广播帧稳定到达 | **作为实时通道** |
| `host.timer` | 120 ms 周期稳定回调（心跳计数可查 `storage.json` 的 `tickAt`） | 可用 |

所以插件页把 HTTP 预览标为「实验」，把「磁盘 index.html + `?ws=11581`」作为推荐路径。

## 4. 数据落点（排查用）

| 路径 | 内容 |
| --- | --- |
| `%APPDATA%\dev.naominet\lazer_nextgen\lua_plugins\<id>\` | 插件安装目录（manifest/lua/frontend） |
| `%APPDATA%\dev.naominet\lazer_nextgen\lua_plugin_data\<id>\storage.json` | `host.storage_*`：配置 + `stats`（含 `tickAt`、`served`、`ws`、`pollError`） |
| `…\lua_plugin_data\<id>\ui-settings.json` | 宿主持久化的设置项值（**本插件已不再注册设置项**，这个文件只是历史遗留；设置都在插件页里，值落在 `storage.json` 的 `parchment.config`） |

## 5. 客户端主题 API 的验证（本轮改动）

插件能把客户端整屏换成羊皮纸，靠的是这轮给 `E:\projects\lazer_nextgen` 补的接口：

```powershell
cd E:\projects\lazer_nextgen
dart analyze lib                 # 期望：No issues found!
flutter build windows --debug    # 约 3 分钟
```

验证步骤：

1. 把 `plugin\` 同步到 `%APPDATA%\dev.naominet\lazer_nextgen\lua_plugins\chuxuehaocai.lazer.theme.earlydev\`，
   并保留 `.socket-server-enabled` / `.websocket-server-enabled`。
2. 客户端设置里的主题模式决定用 `colors` 还是 `darkColors`：
   `%APPDATA%\dev.naominet\lazer_nextgen\shared_preferences.json` 的
   `flutter.lazer_theme_mode` 取 `light` / `dark` / `system`。
3. 截图对照：
   - 浅色：`shots/client-themed-light.png` —— 画布 `#F0EEE6`、卡片 `#FAF9F5`、
     播放条 `#141413`、强调色 clay `#D97757`、侧栏固定 232。
   - 深色：`shots/client-themed-dark-final.png` —— 画布 `#191918`、卡片 `#242423`、
     强调色 `#E68E70`，播放条仍是 `#141413`。

颜色生效路径（改动最小、覆盖面最大）：

| 层 | 位置 | 说明 |
| --- | --- | --- |
| 解析 | `lib/theme/lazer_theme.dart` | `parseSkinColors` / `canonicalColorSlot` / `formatSkinColor`，19 个槽位 + 8 组别名 |
| 合并 | `lib/theme/apple_design.dart` | `applySemanticColorOverrides`，未给的 `fill`/`separator`/`glass` 由 ink 与画布派生 |
| 应用 | `AppleSemanticColors.of(context)`（143 处）/ `context.colors`（91 处） | 一处合并，全应用换色 |

几何令牌：`railWidth` 在 `lib/ui/shell.dart` 的侧栏宽度处生效；
`playerBarHeight` / `compactPlayerBarHeight` 在 `lib/ui/player_bar.dart` 的
`ConstrainedBox(minHeight:)` 生效；`glassBlurSigma` 从硬编码 16 改为读取令牌
（侧栏与播放条两处），设 0 即完全没有毛玻璃。

已知缺口（属客户端 v2 组件的既有实现，不是 API 缺失）：
`controlRadius` 仍未被控件使用；首页卡片的圆角**已在本轮接线**（见下）。

首页卡片的 `groupedCardRadius` 接线（本轮）：`lib/ui/home_pages.dart` 里 7 处
卡片圆角（歌单/专辑横滑架、编辑推荐卡、排行榜卡、快捷卡、占位卡）原来写死
11/16/18 px，现在统一读 `LazerThemeTokens.of(context).groupedCardRadius`。
羊皮纸皮肤声明 `groupedCardRadius = 0`，所以首页卡片现在真的是直角；
默认主题（14）仍然圆角。脚本：`tools\patch_home_card_radius.py`（幂等）。

## 6. 本轮追加：正在播放页 / 背景 / 语义树

```powershell
cd E:\projects\lazer_nextgen
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

## 7. 圆角设置（跟随主题 / 自行调节）

设置页的两个出口在 Dart 层合流成一个「卡片 px + 组件系数」：

```powershell
cd E:\projects\lazer_nextgen
flutter test test\corner_scale_test.dart        # 令牌 + px↔系数 + cardRadiusOf 两种模式
flutter analyze lib test                        # No issues found
flutter build windows --debug                   # 成功
```

- `lib/theme/shape_scale.dart` → `AppleShape.resolve(followTheme, customPx, theme)` 算组件系数；
  `AppleShape.cardRadiusOf(context, theme)` 给卡片圆角（手动模式下**直接用用户 px**，
  不再乘系数，否则皮肤写 0 就永远调不动）；`cardPxFor()` 给设置页显示生效值。
- `lib/main.dart` → `MaterialApp` 外包 `AppleShape(scale:, cardPx:, manual:)`。
- 皮肤令牌必须能被用户改，否则「跟随主题设置」只是常数：

```powershell
cd E:\projects\lazer_early_development_theme
node tools\check_corner.js      # 12 条断言：默认 0 px / 8 px / 夹取 / 旧百分数 id 兼容
python tools\verify.py          # 6/6 PASS（icons/manifest/package/lua/corner/zip）
```

真实客户端里的点法（截图在 `shots\px*.png`、`shots\live-*.png`、`shots\final2-*.png`）：

1. 皮肤声明 `groupedCardRadius = 0` → `设置 → 外观 → 圆角设置` 显示「跟随主题设置」，
   下面的「圆角大小」写着 **`0 px（主题）`**（`shots/final2-corner.png`）——显示的必须是
   真正生效的那个数，不能写 16 px。
2. 把滑块往里拖 → 自动切到「自行调节」，页面当场重排（`shots/live-a-before.png` 32 px →
   `shots/live-b-after.png` 2 px，同一张设置卡片从大圆角变回直角，不重启）。
3. 自行调节 24 px → 首页卡片明显变圆（`shots/px3-a-home24.png`），组件按钮不变方。
4. 插件页把「主题卡片圆角 px」改成别的值 —— 不重启，宿主重读 `theme` 后一起变
   （`plugin_manager_io.dart` 的 `_reloadSkin()`）。

**为什么要进 `_RootUiSignature`**：`AppleShape` 包在 `MaterialApp.builder` 里，
而 `_LazerAppState._onRootUiChanged()` 只有在 `_rootUiSignature` 变化时才 `setState`。
第一版没把 `cornerFollowsTheme` / `cornerPx` 放进签名，于是拖滑块只更新了设置页上的
数字，根 widget 不重建、`AppleShape` 还是旧值 —— 表现就是「改了没用，不会实时刷新」。
`lib/main.dart` 的签名元组现在包含这两个字段（`fontPreferences` 与
`pluginSkinRevision` 本来就在里面，所以字体与换肤一直是实时的）。

持久化落点：

| 键 | 含义 |
| --- | --- |
| `flutter.lazer_corner_follows_theme` | true = 跟随主题设置，false = 自行调节 |
| `flutter.lazer_corner_px` | 自行调节的卡片圆角，单位 px（0–32） |
| `flutter.lazer_corner_strength` | 旧版本的 0–2 系数，只在没有 `corner_px` 时按 ×16 迁移一次 |
| `parchment.config.cornerPx`（插件 storage） | 皮肤的卡片圆角 px，写进 `groupedCardRadius` |

## 8. 字体：皮肤是默认值，用户的选择优先

```powershell
cd E:\projects\lazer_nextgen
flutter test test/font_precedence_test.dart     # 页面标题 / 段落头 / 列表行 / 歌词字重
```

- 用户动过的分类字重（`lazer_font_preferences`）与歌词字重（`lazer_lyric_font_weight` +
  `lazer_lyric_font_weight_custom`）压过皮肤的 `*Weight` 令牌；字体族只有用户能决定。
- `lib/widgets/apple_ui.dart` 的标题、段落头、列表行都走 `context.fonts.apply(category, …)`
  —— 之前段落头与列表行直接用 `ui.titleFontWeight` / `ui.bodyFontWeight`，皮肤一装就把
  用户选的粗细盖掉。
- 字体自定义页、登录弹窗、歌单选择弹窗补上 `ui: state.pluginTheme`，不再把皮肤颜色丢掉。

首页卡片的最终形态见 `shots/final-corner-home.png`：同一份羊皮纸皮肤下，
Hero 四卡与「最近播放」六格都是直角（`groupedCardRadius = 0`），
而侧栏仍是 232、播放条仍是 `#141413`、强调色仍是 clay —— 换皮与圆角各自独立。

自动化辅助：`python tools\prefs.py --dump-corner` 读前两个键，
`python tools\scroll.py --drag X,Y X,Y` 拖滑块，`python tools\click.py --at X,Y` 点按钮。
