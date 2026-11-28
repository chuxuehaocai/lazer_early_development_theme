# Early Development

给 [chuxuehaocai/Lazer](https://github.com/chuxuehaocai/Lazer) 写的早期开发主题插件。

仓库：<https://github.com/chuxuehaocai/lazer_early_development_theme>

包名（plugin id）：`chuxuehaocai.lazer.theme.earlydev`

Lazer 最早那版界面（`3fdf89b4`）是羊皮纸配色：卡片切得方方正正，靠一层层浅色和 1px
细线分层，全站一个阴影都没有。这个插件把那一版的排版和手感翻成宿主认识的令牌交回去 ——
分组卡片直角、列表行 64、侧栏 232、播放条 100、毛玻璃一点不要、背景就是一张干净的纸。
歌词那边，原文和翻译用同一个 48% 灰，没在唱的行缩到 0.97。

它只管外观。不接音乐平台，不联网，不起本地服务，也没有自己的页面和设置项；装上之后
客户端读它的令牌，仅此而已。

## 安装

从 `build/` 拿 zip，走客户端 设置 → 账户与扩展 → 插件管理 → 导入 ZIP。

不爱点界面就把目录拷过去：

```
%APPDATA%\dev.naominet\lazer_nextgen\lua_plugins\chuxuehaocai.lazer.theme.earlydev\
```

装完还得去 **设置 → 界面与布局 → 外观 → 主题风格** 选「跟随插件皮肤」。那里默认是客户端
自带的 **Mio** —— 同一套几何，不同来源；想用插件这版就手动切过去。

## 它给了哪些值

| 令牌 | 值 | 说明 |
| --- | --- | --- |
| `groupedCardRadius` | 0 | 卡片直角 |
| `listTileMinHeight` / `listTileVerticalPadding` | 64 / 10 | 参考实现里量出来的行高 |
| `trackHoverDurationMs` | 240 | 歌曲行悬浮遮罩的过渡时长，避免鼠标移动时闪烁 |
| `railWidth` | 232 | 侧栏固定宽 |
| `playerBarHeight` / `compactPlayerBarHeight` | 100 / 72 | 桌面与紧凑播放条 |
| `glassBlurSigma` | 0 | 不模糊 |
| `backgroundPlayMode` | `off` | 不画专辑色流 |
| `capsuleRadius` / `navBarRadius` | 0 / 0 | 窗口胶囊、移动端底边栏也是直角 |
| `controlRadius` | 12 | 描边按钮 |
| `pageTitleRegularSize` / `pageTitleCompactSize` | 56 / 40 | 版面大标题 |
| `lyricDimAlpha` / `lyricTranslationAlpha` | 0.48 / 0.48 | 原文与翻译同色 |
| `lyricFocusScaleDelta` | 3 | 没在唱的行缩到 .97 |
| `colors` / `darkColors` | 19 个语义槽 ×2 | 浅色 `#F0EEE6` 画布、`#141413` 墨、`#D97757` clay；深色是 `#191918` / `#242423` / `#E68E70` |

要核对拼写就翻 [`plugin/lib/tokens.lua`](plugin/lib/tokens.lua)，别处没有副本。

## 目录

```
plugin/              打进 ZIP 的全部内容（ZIP 根 = 这个目录）
  manifest.json      id / 版本 / 权限（只要 storage）
  main.lua           describe、theme、skin、session 四个入口
  lib/tokens.lua     令牌、调色板、摘要
  lib/config.lua     cornerPx / cornerScale
  LICENSE            MIT，跟仓库根是同一份
build/               打出来的 zip
```

仓库里只有这四样东西：插件本体、许可、打包好的 zip 和这份说明。没有构建脚本、
没有本地服务、没有需要装的东西 —— 插件是纯 Lua，客户端直接读。

`cornerPx` 是唯一还留着的可调项：客户端「设置 → 外观 → 圆角设置」选「跟随主题设置」时
读它。写 0 是直角，写 16 大概就是宿主原本那个圆角。值存在宿主的插件存储里，默认 0。

## 重新打包

改完 `plugin/` 之后自己压一份即可，注意 **zip 的根就是 `plugin/` 的内容**
（`manifest.json` 必须在根，外面不能再套一层 `plugin/` 目录）：

```powershell
cd plugin
Compress-Archive -Path manifest.json, main.lua, lib, LICENSE `
                 -DestinationPath ..\build\chuxuehaocai.lazer.theme.earlydev-1.0.0.zip -Force
```

客户端只认 `manifest.json` / `*.lua` / 文本资源 / 根目录的 `LICENSE`，包里别塞别的。

## 许可

本项目使用 MIT 许可，全文见 [LICENSE](LICENSE)。

Copyright (c) 2026 chuxuehaocai
