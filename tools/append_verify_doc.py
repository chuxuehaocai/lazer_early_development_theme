"""Append the client-patch verification section to docs/VERIFY.md (UTF-8 safe)."""
import io

PATH = "docs/VERIFY.md"
SECTION = """
## 5. 客户端主题 API 的验证（本轮改动）

插件能把客户端整屏换成羊皮纸，靠的是这轮给 `E:\\projects\\lazer_nextgen` 补的接口：

```powershell
cd E:\\projects\\lazer_nextgen
dart analyze lib                 # 期望：No issues found!
flutter build windows --debug    # 约 3 分钟
```

验证步骤：

1. 把 `plugin\\` 同步到 `%APPDATA%\\dev.naominet\\lazer_nextgen\\lua_plugins\\community.naominet.parchment-field-notes\\`，
   并保留 `.socket-server-enabled` / `.websocket-server-enabled`。
2. 客户端设置里的主题模式决定用 `colors` 还是 `darkColors`：
   `%APPDATA%\\dev.naominet\\lazer_nextgen\\shared_preferences.json` 的
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

已知缺口（本轮未接线，属客户端 v2 组件的既有实现，不是 API 缺失）：
`controlRadius` 仍未被控件使用；首页「最近播放」卡片的圆角走组件内置值，
只有 `AppleGroupedCard` / 网络浏览页读 `groupedCardRadius`。要让像素级 1:1，
这些还需要逐组件接线。
"""

with io.open(PATH, "a", encoding="utf-8", newline="\n") as handle:
    handle.write(SECTION)
print("appended", len(SECTION), "chars")
