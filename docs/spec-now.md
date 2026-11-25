# 正在播放 / 歌词 / 队列 / 桌面工作台 — 像素级 UI 规格

> 来源：`E:\Lazer-3fdf89b40956d1f90f9bff242b67a8a9129d140e`（只读参考实现，parchment 阶段）。
> 用途：手写 HTML/CSS 复刻 `#/now`、`#/queue` 与底部播放条呼应。所有数值单位 px，行号均为源码行号。
> 排版口径：`font-size / line-height(倍数) / letter-spacing`（与 `docs/CONTRACT-frontend.md` 的 token 命名对齐）。

---

## 0. 先校准 9 处任务书假设（逐行核对后的偏差）

复刻前必须先看这张表，否则会照着一半错误的印象写 CSS。

| # | 任务书假设 | 源码事实 | 依据 |
| --- | --- | --- | --- |
| 1 | 正在播放页是深色播放面 / 渐变 / 模糊 | 页面底色是**羊皮纸实色** `#F0EEE6`，无渐变、无毛玻璃。深色面 `#141413` 只出现在**全站底部播放条**，不属于本页 | `now_playing_page.dart:352`、`app_theme.dart:31`、`player_page.dart:2646` |
| 2 | 页面有最大宽度（如 1280） | 本页**没有** `pageMaxWidth` 约束，铺满窗口；唯一硬约束是左栏 `clamp(240,440)` | `desktop_now_playing.dart:94`（对比 `design_tokens.dart:241`） |
| 3 | 非聚焦行透明 `lyricDimAlpha .48`、翻译 `.58` | 全仓**无**这两个常量名。等价实现是：未聚焦行用 `cloudDark #87867F → slateDark #141413` 的**颜色插值**（不是透明度）；逐字歌词的未唱底稿为 `α .28`；翻译行固定 `cloudDark`。反解：`cloudDark` 在 `ivoryMedium` 上恰好等于 `slateDark @ 48%`（见 §2.4），所以 `.48` 能从色值推出，`.58` 无对应 | `lyric_viewport.dart:600-623`、`timed_lyric_text.dart:110-118`、`lyric_viewport.dart:322-326` |
| 4 | 队列有拖拽手柄 + 清空按钮 | 队列**没有**排序拖拽、**没有**清空按钮；只有标题行 + 关闭。移动端底表有 Material 默认拖拽把柄（非重排） | `playback_queue_view.dart:48-95`、`now_playing_page.dart:51-63` |
| 5 | 卡片/对话框有圆角 | 卡片 `0`、对话框 `0`、底表 `0`、封面 `0`、播放按钮 `0`（唯一非零：描边按钮 12、填充按钮仅下圆角 8） | `app_theme.dart:68-80`、`design_tokens.dart:245-263` |
| 6 | 封面有阴影 | 全仓 **0 处** `BoxShadow`/`BackdropFilter`，`AppElevation.none` | `design_tokens.dart:267-269`、`animated_track_cover.dart:38-43` |
| 7 | 桌面歌词悬浮条有锁/关闭按钮 | `desktop_now_playing.dart` 是**整窗工作台**，不存在独立悬浮歌词窗；本文件内的"关闭"只出现在错误提示右侧 32×32 按钮上 | `desktop_now_playing.dart:43-149`、`:346-359` |
| 8 | 歌词有罗马音行 | 数据模型只有 `text / translation / words`，**无罗马音字段**；罗马音只能塞进 `translation` 槽位 | `data/lyrics.dart:10-23` |
| 9 | 进度条在页面中部、时间码两侧 | 桌面布局里进度条在**底部 dock**（时间码左/右夹住），不在中栏；中栏（右栏）只有歌词/评论/队列 | `desktop_now_playing.dart:363-377` |

---

## 0.1 色板（含深色主题覆盖）

浅色取 `design_tokens.dart`，深色取 `app_palette.dart:11-31`。写 CSS 时建议全部走 `css/tokens.css` 的变量。

| token | 浅色 | 深色 | 用途 | 依据 |
| --- | --- | --- | --- | --- |
| `slateDark` | `#141413` | `#F0EEE6` | 主文字、已聚焦歌词 | `design_tokens.dart:19` / `app_palette.dart:11` |
| `ivoryMedium` | `#F0EEE6` | `#191918` | 页面画布 | `:22` / `:13` |
| `ivoryLight` | `#FAF9F5` | `#242423` | 面板、dock、悬浮工具条 | `:25` / `:14` |
| `cloudMedium` | `#B0AEA5` | `#A8A69E` | 禁用、弱提示 | `:28` / `:16` |
| `cloudDark` | `#87867F` | `#B5B2A9` | 未聚焦歌词、翻译行、次级图标 | `:31` / `:17` |
| `stone` | `#CCCBC8` | `#454540` | hairline 分隔线、未播轨道 | `:34` / `:18` |
| `slateMedium` | `#3D3D3A` | `#454540` | 深色面内部描边 | `:37` / `:19-20` |
| `oatWarm` | `#E3DACC` | `#34312D` | 队列当前行、按钮 hover | `:40` / `:21` |
| `manilla` | `#F5E3C7` | `#3E3329` | 主播放键 hover、缺图占位 | `:43` / `:22` |
| `clay` | `#D97757` | `#E68E70` | 唯一的行动色：滑块 thumb、队列左侧 2px | `:49` / `:23` |
| `clayDeep` | `#C6613F` | `#F0A084` | 已收藏、激活态、选中歌词 | `:52` / `:24` |
| `onDark` | `#FAF9F5` | 同 | 深色面文字 | `:55` / `:25` |
| `onDarkMuted` | `#B0AEA5` | 同 | 深色面弱文字 | `:58` / `:26` |
| `playerSurface` | `#141413` | 同 | 底部播放条底色（本页不使用） | `app_palette.dart:30` |

字体：全部绑定 MiSans（`design_tokens.dart:69-96`），serif 角色也是 MiSans；CSS 直接用 `--font-ui`。

排版 token（`design_tokens.dart:100-224`）：

| 角色 | size | line-height | letter-spacing | weight |
| --- | --- | --- | --- | --- |
| caption | 12 | 1.4 | -0.24 | 400 |
| captionStrong | 12 | 1.4 | -0.24 | 600 |
| bodySm | 16 | 1.3 | -0.08 | 400 |
| body | 20 | 1.4 | 0 | 400 |
| subheading | 24 | 1.3 | -0.05 | 600 |
| heading | 61 | 1.1 | -0.12 | 700 |
| monoSm | 12 | 1.4 | 0 | 400（色 `cloudDark`） |
| wordmark | 12 | 1.0 | 3.2 | 700 |

间距：`4 / 8 / 16 / 24 / 32 / 48`，节间距 80（`design_tokens.dart:232-242`）。
圆角：`card 0`、`outlined 12`、`filledButton 仅下角 8`（`:245-263`）。阴影：无（`:267-269`）。
描边：`hairline = 1px stone`、`onDark = 1px slateMedium`（`:271-289`）。

---

## 1. 正在播放页整体

### 1.1 容器、背景、断点

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 页面背景 | 纯色 `ivoryMedium #F0EEE6`（深色 `#191918`），**无渐变、无模糊、无噪点** | `now_playing_page.dart:352`；主题同值 `app_theme.dart:31` |
| 页面最大宽度 | 无（全宽铺满窗口） | `desktop_now_playing.dart:43-148` 无 ConstrainedBox |
| 断点 | `< 720` 走移动布局；`>= 720` 走桌面工作台 | `now_playing_page.dart:362` |
| 安全区 | 桌面分支套 `SafeArea`；移动分支同样 `SafeArea` 后 Column | `now_playing_page.dart:364-384`、`:395-403` |
| 页面进入/退出 | 从底部整体上滑：`translateY(100%→0)`，进入 420ms `easeOutCubic`，退出 340ms `easeInCubic`；桌面可用顶部 64px 边带下拉返回 | `pull_down_page_route.dart:21-23,157-169,174-176` |
| 空状态 | 居中：`subheading` 文案 + 8 + `bodyMuted 16` + 24 + IvoryButton | `now_playing_page.dart:797-819` |

### 1.2 顶部条（桌面）

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 内边距 | `16 / 8 / 20 / 8`（左/上/右/下） | `desktop_now_playing.dart:46` |
| 返回按钮 | `keyboard_arrow_down_rounded`，IconButton 默认 24 图标 + 48×48 触控区 | `:49-53`；`accessible_controls.dart:97-136` |
| 间距 | 返回 与 标签 8 | `:54` |
| 页标题 | `InlineLabel('正在播放')`：12px、w500、大写、letter-spacing 1.6、色 `cloudDark`，占满剩余宽度 | `:55`、`paper_widgets.dart:381-388` |
| 右侧三个 tab | `歌词` / `评论` / `播放队列`，tab 间 8 | `:56-81` |
| tab 规格 | 底部 2px 边框（激活 `slateDark`，否则透明）；按钮最小高 44；直角；图标 19；文字用 TextButton 默认 labelLarge（14 / w500） | `:163-188` |
| tab 动画 | 边框颜色 AnimatedContainer 180ms | `:165-166` |
| 分隔线 | 头部下方整宽 1px `stone` | `:85` |

### 1.3 分栏比例（封面区 / 阅读区）

固定公式，不用百分比网格：

```
left  = clamp(W * 0.34, 240, 440)      // 封面栏，W = 窗口宽
gap1  = 32
rule  = 1                               // 竖直 hairline，色 stone
gap2  = 16
right = W - 32(left pad) - 24(right pad) - left - 32 - 1 - 16   // 阅读区
```

依据：`desktop_now_playing.dart:88-104`（内容内边距 `32/24/24/24`，左栏宽、32 间距、竖线、16 间距）。

实测：

| 窗口宽 | 左栏 | 右栏（歌词区） |
| --- | --- | --- |
| 1440 | 440（0.34×1440=489.6 被 440 截断） | 895 |
| 1280 | 435 | 740 |
| 1024 | 348 | 571 |
| 900 | 306 | 489 |
| 720 | 245 | 370 |

（右栏 = `W − 105 − 左栏`；105 = 32 + 24 内边距 + 32 + 1 + 16。）

右栏切换（歌词/评论/队列）：AnimatedSwitcher 240ms，淡入 + `translateX(2.5%→0)`，`easeOutCubic` / `easeInCubic`（`desktop_now_playing.dart:106-121`）。

### 1.4 封面

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 形状 | 正方形，边长 = `min(左栏宽, 可用高度)`（1440×900 时为 440）；可用高度不足时按高收缩 | `desktop_now_playing.dart:283-293` |
| 圆角 | 0（`BorderRadius.zero`，ClipRRect 生效但不裁圆角） | `animated_track_cover.dart:42`、`plate_art.dart:31-32` |
| 边框 | 无 | `plate_art.dart:31-40` |
| 阴影 | 无 | 全仓无 BoxShadow |
| 缺图占位 | 底 `manilla #F5E3C7` + 居中 `music_note_rounded`（`cloudDark`） | `plate_art.dart:25-30` |
| 换曲动画 | 480ms slide：新封面从右（或左）滑入、`easeOutCubic` | `animated_track_cover.dart:18-43` |
| 长按 | 弹「保存封面图片？」确认框（取消/保存） | `now_playing_page.dart:237-285` |
| 矮窗降级 | 内容高 `< 320×textScale` 时改为「72 封面 + 16 + 元信息」横排，整体可滚动 | `desktop_now_playing.dart:268-282` |

### 1.5 标题 / 歌手 / 专辑（桌面左栏）

| 元素 | 规格 | 依据 |
| --- | --- | --- |
| 歌曲名 | `heading` 派生：MiSans **30px w700**，行高 **1.2**，ls -0.12，色 `slateDark`，最多 2 行省略；矮窗 22px | `desktop_now_playing.dart:209-217` |
| 收藏图标 | 标题右侧 IconButton：`favorite_rounded`（已收藏 `clayDeep`）/ `favorite_border_rounded`（`cloudDark`） | `:219-232` |
| 译名 | `bodySmMuted` **15px**，色 `cloudMedium #B0AEA5`，1 行省略，与标题间距 4 | `:235-246` |
| 歌曲名 → 歌手 | 间距 **12**（矮窗 8） | `:247` |
| 歌手 | `body` 派生 **18px**（矮窗 14），w400，行高 1.4，色 `slateDark`，最多 2 行 | `:248-254` |
| 歌手 → 专辑 | 间距 **6**（矮窗 4） | `:255` |
| 专辑 | `bodySmMuted` **15px**（矮窗 12），色 `cloudMedium` | `:256-260` |
| 封面 → 元信息 | 间距 **24** | `:294` |

### 1.6 移动端（< 720）标题与布局

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 页面内边距 | `24 / 4 / 24 / 20` | `now_playing_page.dart:504` |
| 封面区 | 居中方形，边长 `min(H-16, min(W,380))` | `:437-445` |
| 歌曲名 | `subheading` **24px w600**，1 行（窄屏分支不会再放大） | `:565-567` |
| 译名 | 15px，`cloudDark`，间距 4 | `:586-597` |
| 歌手 · 专辑 | `body` **17px**，`cloudDark`，中间 ` · ` 分隔 | `:599-620` |
| 元信息 → 传输控件 | 间距 16 | `:543` |
| 控件显隐 | SizeTransition + Fade 360ms，纵向折叠 | `:507-526` |
| 手机横屏（H<500 且 W>H） | 左：阅读区；右：控件栏宽 `clamp(W*0.6,280,400)`，左侧 20 内边距，整页内边距 `20/8` | `:452-501` |
| 移动顶部条 | 内边距 `12/4/12/4`；返回 + Spacer + （保存中转圈 20×20）+ 歌词开关 + 评论 + 队列；显隐 AnimatedOpacity 200ms | `:307-348` |

移动端传输组（`_PlaybackTransport`，`now_playing_page.dart:635-700`）：

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 进度条 | `PlayerSeekBar` 默认：轨道 **4**、thumb 半径 **7**（直径 14）、overlay 15 `clay@16%` | `:648`、`player_seek_bar.dart:10-31` |
| 进度条 → 时间码 | 8 | `:649` |
| 时间码行 | 左右两端对齐，`monoSm` 12，`cloudDark` | `:654-660` |
| 时间码 → 控制行 | 12 | `:662` |
| 控制行 | `spaceBetween`：随机 / 上一首 / 播放键 / 下一首 / 循环；每个按钮命中区 **48×48** | `:664-746` |
| 图标尺寸 | 随机 **26**、上一首 **34**、下一首 **34**、循环 **26**、播放键图标 **38** | `:675-695`、`:789` |
| 主播放键 | **直径 68 的圆**，底 `slateDark`、图标 `onInk`；hover 底色换 `manilla`、图标 `slateDark`；容器过渡 130ms | `:775-791` |
| 图标色 | 禁用 `cloudMedium`；激活或 hover `slateDark`；常态 `cloudDark` | `:727-731` |

### 1.7 底部 dock（进度条 + 时间码 + 控制组 + 音量）

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 容器 | 底色 `ivoryLight`，顶部 1px `stone` hairline，内边距 `24 / 8 / 24 / 16`（左/上/右/下） | `desktop_now_playing.dart:308-314` |
| 第一行 | 时间码(54) + 12 + 进度条(flex) + 12 + 时间码(54) | `:363-377` |
| 时间码 | `monoSm` **12px**，`cloudDark`；起点左对齐、终点右对齐；宽度 **54×textScale**；格式 `m:ss`（分钟不补零） | `:474-483`、`app_state.dart:1186-1190` |
| 进度条 | 轨道高 **3**，thumb 半径 **5**；已播 `slateDark`、未播 `stone`、thumb `clay`、overlay `clay@16%` 半径 15 | `:368-372`、`player_seek_bar.dart:6-35` |
| 控制行 | `Spacer(flex2)` + 居中簇 `Expanded(flex3, FittedBox)` + 12 + 音量 `Expanded(flex2)`；整体 FittedBox scaleDown 防溢出 | `:378-460` |
| 图标尺寸 | 随机 23、上一首 28、播放键 48×48、下一首 28、循环 23 | `:387-447` |
| 播放键 | 48×48，**直角**（RoundedRectangleBorder 0），底 `slateDark`、图标 `onInk`，图标 28；图标切换 AnimatedSwitcher 180ms | `:409-428` |
| 间距 | 主簇内统一 8（播放键两侧也是 8） | `:408,429` |
| 激活色 | 随机/循环激活时图标 `clayDeep`，否则 `cloudDark` | `:390-392,438-440` |
| 错误条 | 播放错误时在进度条之上出现：16 图标 + 8 + 文案 `caption`（`clayDeep`）+ 关闭按钮 32×32（图标 18，padding 4） | `:319-361` |

### 1.8 右侧动作（队列 / 音量 / 更多）

- **队列**：桌面在顶部条第三个 tab（`播放队列`），不占 dock 右侧；dock 右侧只有音量（`desktop_now_playing.dart:56-81,453-459`）。
- **音量**：见 §5。
- **更多**：参考实现**没有** more 菜单；不要凭空加三点图标。
- 呼应（不重复提取）：全站底部播放条 `_PlayerBar` 深色面 `playerSurface #141413` + 顶部 1px `slateMedium`，内边距 24/16/24/16，封面 48，标题 16/1.25 `onDark`，歌手 12 `onDarkMuted`，右侧时间码 + 音量 + 队列（`player_page.dart:2641-2657,2678-2821`）。

### 1.9 CSS 实现要点（整页）

```css
.now {
  display: grid;
  grid-template-columns: clamp(240px, 34vw, 440px) 32px 1px 16px 1fr;
  height: 100%;
  background: var(--ivory-medium);      /* 纯色，不要加渐变/滤镜 */
  padding: 24px 24px 0 32px;
  box-sizing: border-box;
}
.now__rule { width: 1px; background: var(--stone); }
.now__cover { aspect-ratio: 1 / 1; border-radius: 0; box-shadow: none;
              max-height: 100%; margin: 0 auto; }   /* 高不够时按高收缩，与 §1.4 一致 */
.now__title { font: 700 30px/1.2 var(--font-ui); letter-spacing: -0.12px; color: var(--slate-dark); }
.now__artist { font: 400 18px/1.4 var(--font-ui); color: var(--slate-dark); }
.now__album, .now__translated { font: 400 15px/1.3 var(--font-ui); color: var(--cloud-medium); }

.dock {
  display: flex; flex-direction: column;      /* 行与行之间无额外 gap，靠 Slider 自带高度撑开 */
  background: var(--ivory-light);
  border-top: 1px solid var(--stone);
  padding: 8px 24px 16px;
}
.dock__seek {
  flex: 1; height: 3px; border-radius: 0;
  background: linear-gradient(to right, var(--slate-dark) var(--progress), var(--stone) 0);
}
.dock__seek::after {           /* thumb：12px 圆，clay */
  content: ""; position: absolute; left: var(--progress); top: 50%;
  width: 10px; height: 10px; margin: -5px 0 0 -5px;
  border-radius: 50%; background: var(--clay);
}
```

注意：桌面 dock 与移动端的滑块是**两种**规格（3/5 vs 4/7），见 `desktop_now_playing.dart:368-372` 与 `now_playing_page.dart:648`＋`player_seek_bar.dart:10-12`。

### 1.10 本节 demo 文案

- 页标题：`正在播放`
- 歌曲名：`夜航西飞`
- 译名：`Night Flight Westward`
- 歌手：`林间晚风`
- 专辑：`第五轨`
- 时间码：`1:47` / `4:12`

---

## 2. 歌词视图（重点）

组件根：`LyricViewport`（`lyric_viewport.dart`），被 `Expanded` 撑满右栏；移动整屏模式内边距 `4 / 16`，上方 `InlineLabel('歌词')` + 16（`now_playing_page.dart:220-235`）。

### 2.1 视口与水平边距

| 项 | 公式 | 依据 |
| --- | --- | --- |
| gutter（左右留白） | `min(18, W * 0.1)` | `lyric_viewport.dart:57-58`、`lyric_edge_fade.dart:15` |
| 文本宽 | `max(1, W - 2*gutter)` → 1440 窗（右栏 895）时 gutter 18、文本宽 859 | `:59` |
| 剪裁 | 外层 ClipRect；行位置 `top:0 + translateY(y)`，`left:gutter`、`width:textWidth` | `:801-810`、`lyric_edge_fade.dart:45` |

### 2.2 排版（原文 / 翻译 / 罗马音）

| 行 | 规格 | 依据 |
| --- | --- | --- |
| 原文 | `bodySm` 派生：**22px（默认，可 14–40）**，行高 **1.5**，ls -0.08，字重 **w600（默认，可 400–700）** | `lyric_viewport.dart:317-321`、`app_state.dart:182-185` |
| 翻译 | 字号 `clamp(22 × 16/22, 12, 30)` = **16px**，行高 **1.45**，色 `cloudDark #87867F`，w400 | `:322-326` |
| 罗马音 | **无独立行**。若需 romaji，占 `translation` 槽位（即同 16px / 1.45 / `cloudDark`） | `data/lyrics.dart:10-23` |
| 原文→翻译 间距 | **5** | `lyric_viewport.dart:370-378,648` |
| 行块高 | `原文高 + (有翻译 ? 5 + 翻译高 : 0) + 20` | `:367-380` |
| 默认行块高 | 22×1.5=33；翻译 16×1.45≈23.2；合计 **≈ 81.2**（含 20 的下方留白） | 同上 |
| 行单位 `rowUnit` | 所有行块高的平均值（用于模糊与遮罩计算） | `:390` |
| 对齐 | 左对齐，`textDirection: ltr`，无首行缩进、无两端对齐 | `:640-643` |
| 空行 | 空字符串渲染为单个空格，保证行高稳定 | `:640` |

> 关键细节：`+20` 是**加在行块尾部**，不是上下均分。文本贴着行块顶部排，因此视觉行距≈20，但"行块高度"比"文本高度"多 20。

### 2.3 聚焦缩放 / 字重 / 颜色

| 状态 | scale | 颜色 | 依据 |
| --- | --- | --- | --- |
| 聚焦行 | **1.00** | `slateDark #141413` | `:282`、`:600-623` |
| 非聚焦行 | **0.97**（缩小 3%，不是放大聚焦行） | `cloudDark #87867F` | 同上 |
| 插值 | `emphasis = clamp((scale-97)/3, 0, 1)`，颜色 `cloudDark → slateDark` 线性插值；用 `ColorFilter(srcIn)` 上色（整行统一，包括逐字层） | `:600-623` |
| 变换原点 | **左中**（`Alignment.centerLeft`） | `:812-813` |
| 缩放弹簧 | mass **2**、stiffness **100**、damping **25**（ζ≈0.88，≈0.64s 稳定，轻微回弹） | `:397-407` |
| 字重变化 | 聚焦行**不**改变 `fontWeight`；字重只受用户设置影响（默认 600） | `:317-321` |

### 2.4 非聚焦行的"透明度"（校准项）

源码里没有名为 `lyricDimAlpha` / `lyricTranslationAlpha` 的常量，实际有四层弱化，复刻时按这四层来：

| 机制 | 数值 | 依据 |
| --- | --- | --- |
| 颜色弱化 | `cloudDark #87867F`。反解：`#87867F` 在 `#F0EEE6` 上 = `slateDark #141413 @ 48.0%`（R 105/220、G 104/218、B 103/211），这就是任务书里 `lyricDimAlpha 0.48` 的真实来源；`.58` 在源码中无对应 | `lyric_viewport.dart:613-618`；算术见 `design_tokens.dart:19-31` |
| 距离模糊 | 高斯 σ = `min(5, (|行中心 − 0.35H| / rowUnit) × 1.55) × blurFactor`；blurFactor 0/1 由开关控制，切换 320ms `easeOutCubic`；σ ≤ 0.02 时关闭滤镜 | `:234-239,223-228,814-820` |
| 选择态弱化 | 未选中行 `opacity = 0.54`，选中行 `0.54 + 0.46 = 1.0`（Tween 260ms / 之后 AnimatedOpacity 180ms） | `:584-595` |
| 逐字未唱底稿 | 整行先以 `原文色 @ α .28` 打底，已唱部分由逐字遮罩露出全亮 | `timed_lyric_text.dart:110-118,227-296` |

CSS 映射建议：`--lyric-dim: #87867F` 直接写实色（不要用 `opacity: .48`，否则会与选择态 `opacity .54` 相乘变成 .26）；翻译行同样是 `cloudDark` 实色，不需要单独 alpha。

### 2.5 上下渐变遮罩

| 项 | 公式 / 数值 | 依据 |
| --- | --- | --- |
| 纵向遮罩高度 | `verticalExtent = min(H × 0.22, max(28, rowUnit × 1.15))` → 默认 rowUnit≈81 时 = `min(0.22H, 93.2)` | `lyric_viewport.dart:243-249` |
| 遮罩占全长比例 | `fraction = min(0.24, verticalExtent / H)`（H=700 → 0.133） | `lyric_edge_fade.dart:22` |
| 颜色停靠 | 9 级 smoothstep alpha：`0, 11, 40, 81, 128, 174, 215, 244, 255`（/255 = `0, .043, .157, .318, .502, .682, .843, .957, 1`），上下镜像 | `lyric_edge_fade.dart:24-35` |
| 实现方式 | 双层 `ShaderMask(dstIn)`：先纵向、再横向；外层再 ClipRect | `lyric_edge_fade.dart:44-55` |
| 横向遮罩 | 固定 18 宽（gutter 内），同一组停靠点 → 首尾字符的模糊光晕不被切边 | `:15,49-53` |
| 效果 | 行在视口边缘**渐隐到页面底色**（不是白、不是黑），因为遮罩是 alpha 0 的 `dstIn`；blur 光晕一起淡出 | `lyric_viewport.dart:243-249` |

### 2.6 滚动位置计算（核心公式）

```
focus   = 当前行索引（二分查找 time <= position 的最后一个，可为 -1）
H       = 视口高度
anchor  = prefix[focus] - H*0.35 + heights[focus]/2     // 行块中心落在 35% 高度
target_i = prefix[i] - anchor                            // 每行目标 y
```

依据：`lyric_viewport.dart:140-153,289-293`。

要点：

- 焦点带在**视口 35% 高度**，不是垂直居中（`:290,236-237`）。
- 焦点行之外的行全部参与计算（不裁剪数据），但绘制时只画 `y+h >= -80 且 y <= H+80` 的行（`:799-800`）。
- 行位置由 **封闭解弹簧** 驱动，不是 `AnimationController + Curves`（`lyric_spring.dart:96-119`）。
- 手动拖动偏移 `offset` 有夹紧区间：`[ -0.35H + h0/2 , prefix.last - 0.35H + h_last/2 ]`（`:430-435`）。

### 2.7 滚动动画参数（spring + 交错）

位置弹簧按场景切换（`lyric_spring.dart:122-142`）：

| 场景 | mass | stiffness | damping | ζ | 观感 |
| --- | --- | --- | --- | --- | --- |
| 拖动松手回落 / 跳转 / 前奏 | 0.9 | 90 | 15 | ≈0.83 | 轻微回弹，≈0.48s |
| 歌曲结尾 | 0.9 | 140 | 22 | ≈0.98 | 临界阻尼 |
| 正常换行（间隔 100–800ms） | 0.9 | `170 + r×50`，`r=(1-(interval-100)/700)^0.2` | `sqrt(stiffness)×2.2` | ≈1.16 | 过阻尼、无过冲 |

缩放弹簧：mass 2 / stiffness 100 / damping 25（`:400-405`）。

交错（stagger，`lyric_spring.dart:145-161`）：

- 基准延迟 **50ms/行**，从第 0 行开始累积。
- 焦点行之后的每一行把基准衰减 `/1.05`（即 50 → 47.6 → 45.3 …）。
- 只对 `y + h >= 0` 的可见行计入延迟；跳转（seeking）时全部延迟置 0。

拖动惯性（`lyric_viewport.dart:262-267,766-784`、`scroll_motion.dart`）：

- 惯性衰减：每帧 `velocity *= 0.90^(dt*60)`（默认 retention 0.90，可 0.85–0.98）。
- 速度阈值 5 px/s 以下停止。
- 滚轮冲量：`delta × -ln(0.95) × 60 × acceleration`（默认 acceleration 1.0，可 0.5–3.0），累加后夹紧 ±12000。
- 拖动离开时的携带速度：`velocity × 0.65 × acceleration`，夹紧 ±8000。
- 手动浏览后 **2s** 自动回落到当前行（`app_state.dart:222`、`lyric_viewport.dart:442-455`）。

播放跟随：5ms 定时器比对 `precisePosition`，行变化时 setState（`app_state.dart:122`、`lyric_viewport.dart:112-138`）。时间码/进度按 100ms tick 推进（`player_seek_bar.dart:19-20`）。

### 2.8 逐字高亮（逐字歌词）

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 触发条件 | 该行有 `words` 时间轴（YRC） | `lyric_viewport.dart:630-638` |
| 遮罩边界 | `elapsed / duration × 该行文本宽` | `lyric_word_motion.dart:45-49` |
| 边缘软过渡 | 渐变宽 `max(1, 字形高 × 0.5)`，`white → transparent` | `timed_lyric_text.dart:248,283-292` |
| 字形裁剪 | 上/下各扩 `0.15 × fontSize`（保住 ascender/descender） | `:146-151,257-262` |
| 逐字位移 | `x = -emp × 0.03em × amount × (count/2 - index)`，`y = -emp × 0.025em × amount - float × 0.05em` | `lyric_word_motion.dart:89-93` |
| 逐字缩放 | `1 + emp × 0.1 × amount`（amount ≤ 1.2） | `:90` |
| 发光 | `glow = emp × blur`（blur ≤ 0.8），半径 `min(0.3, blur×0.3) em` | `:93-94,266-281` |
| 强调判定 | 词时长 ≥ 1000ms 且（含 CJK 或去空格后 2–7 字） | `timed_lyric_text.dart:135-138` |
| 末词 | amount ×1.6、blur ×1.5、时长 ×1.2 | `lyric_word_motion.dart:76-80` |
| 聚焦过渡 | 逐字层透明度 = `emphasis()`，随行缩放弹簧一起淡出，不硬切 | `timed_lyric_text.dart:207-223` |

### 2.9 交互

| 交互 | 行为 | 依据 |
| --- | --- | --- |
| 点击某行 | 触发 `feedback()` 并 seek 到该行时间（`line.time / duration` 作为进度比例） | `lyric_viewport.dart:475-489` |
| 点击热区 | 只覆盖真实字形框（多行文本逐行 rect），不是整行通栏 | `lyric_text_hit_region.dart:85-97` |
| 长按 | 进入选词模式；拖动扩展选区；再点击=切换单行选中 | `lyric_viewport.dart:560-578` |
| 选择工具条 | 底部 `left/right 12, bottom 12`，`maxWidth 480`，AnimatedSwitcher 260ms（上滑 35%） | `:834-872` |
| 工具条外观 | 底 `ivoryLight`，1px `stone` 边框，内边距 `12/6/4/6`；文案 `captionStrong`（"已选择 N 行"/"已复制"）；按钮 21（复制 20） | `lyric_selection_toolbar.dart:25-97` |
| 点空白（移动） | 控件可见时折叠歌词模式；控件隐藏时先唤回控件 | `now_playing_page.dart:153-162` |
| 滚动/拖动 | 鼠标中键拖动、纵向拖动、滚轮均可 | `lyric_viewport.dart:724-790` |
| 加载中 | 居中 `CircularProgressIndicator(strokeWidth 2)` | `:674-676` |
| 空/纯音乐 | `captionMuted` 文案（"纯音乐" / "这首歌暂未提供歌词"）+ TextButton「重新加载歌词」 | `:677-697` |

### 2.10 CSS 实现要点（歌词）

```css
.lyrics {
  position: relative;
  height: 100%;
  overflow: hidden;
  --gutter: min(18px, 10%);
  --row-unit: 81.2px;                                        /* 所有行块高的平均值 */
  --fade: min(22%, max(28px, calc(var(--row-unit) * 1.15))); /* 见 §2.5 的 verticalExtent */
  /* 纵向 9 级 smoothstep 遮罩（上下镜像），写成变量复用给纵向/横向两层 */
  --lyric-mask: linear-gradient(to bottom,
    rgba(0,0,0,0)   0,
    rgba(0,0,0,.043) calc(var(--fade) * .125),
    rgba(0,0,0,.157) calc(var(--fade) * .25),
    rgba(0,0,0,.318) calc(var(--fade) * .375),
    rgba(0,0,0,.502) calc(var(--fade) * .5),
    rgba(0,0,0,.682) calc(var(--fade) * .625),
    rgba(0,0,0,.843) calc(var(--fade) * .75),
    rgba(0,0,0,.957) calc(var(--fade) * .875),
    rgba(0,0,0,1)    var(--fade),
    rgba(0,0,0,1)    calc(100% - var(--fade)),
    rgba(0,0,0,.957) calc(100% - var(--fade) * .875),
    rgba(0,0,0,.843) calc(100% - var(--fade) * .75),
    rgba(0,0,0,.682) calc(100% - var(--fade) * .625),
    rgba(0,0,0,.502) calc(100% - var(--fade) * .5),
    rgba(0,0,0,.318) calc(100% - var(--fade) * .375),
    rgba(0,0,0,.157) calc(100% - var(--fade) * .25),
    rgba(0,0,0,.043) calc(100% - var(--fade) * .125),
    rgba(0,0,0,0)   100%);
  -webkit-mask-image: var(--lyric-mask);
  mask-image: var(--lyric-mask);
}

.lyrics__track { position: absolute; inset: 0 auto auto 0; width: 100%; }

.lyric {
  position: absolute;
  left: var(--gutter); right: var(--gutter);
  height: calc(var(--h) * 1px);
  transform: translateY(calc(var(--y) * 1px)) scale(.97);
  transform-origin: left center;
  color: var(--cloud-dark);
  transition: transform 460ms cubic-bezier(.2,.9,.25,1),
              color 320ms cubic-bezier(.22,.61,.36,1),
              opacity 180ms linear;
  will-change: transform;
}
.lyric.is-focus { transform: translateY(calc(var(--y) * 1px)) scale(1); color: var(--slate-dark); }
.lyric p      { margin: 0; font: 600 22px/1.5 var(--font-ui); letter-spacing: -0.08px; }
.lyric span   { display: block; margin-top: 5px; color: var(--cloud-dark);
                font: 400 16px/1.45 var(--font-ui); }

/* 未聚焦模糊：σ 用 CSS blur 近似，距离越远越大，上限 5px */
.lyric:not(.is-focus) { filter: blur(calc(var(--sigma, 0) * 1px)); }
```

要点：

- 遮罩用 `mask-image`（`-webkit-mask-image` 双写，Chrome 144 已支持裸 `mask-image`），**不要**用两层绝对定位的白色渐变块盖住——页面底色是羊皮纸，白块会露馅。
- 聚焦缩放永远用"非聚焦缩到 0.97"来表达，`transform-origin: left center`；如果只放大聚焦行，行宽会溢出 gutter。
- 弹簧→CSS：推荐 `linear()`（Chrome 支持）逐帧还原；退而求其次：位置 `cubic-bezier(.22,.85,.25,1) 420ms`、缩放 `cubic-bezier(.2,.9,.25,1.08) 460ms`。
- 逐字高亮：`background-clip: text` + `background: linear-gradient(90deg, #141413 var(--p), transparent 0)` 铺在文字上，`--p` 由 JS 每帧更新；软边用 `linear-gradient(90deg, #141413 calc(var(--p) - 8px), transparent calc(var(--p) + 8px))`。

### 2.11 本节 demo 歌词（6 行，原文 + 翻译）

| time | 原文 | 翻译 |
| --- | --- | --- |
| 0:12.0 | 夜色沿着窗框缓缓流下来 | Night slips slowly down the window frame |
| 0:18.5 | 我把旧唱片翻到背面 | I turn the old record to its other side |
| 0:25.0 | 你的名字停在第五轨 | Your name rests on the fifth track |
| 0:31.5 | 唱针落下，房间轻轻一亮 | The needle drops, the room glows softly |
| 0:38.0 | 我们说过的话结了霜 | The words we spoke have gathered frost |
| 0:44.5 | 等天亮，再一起融化 | When morning comes, we melt together |

### 2.12 歌词选词工具条 / 歌词图片对话框（视觉规格）

**工具条**（见 §2.9）：`ivoryLight` 底 + 1px `stone` 边框，圆角 0，内边距 `12 / 6 / 4 / 6`，左文案 `captionStrong`（12 w600），右四个按钮 21 / 21 / 20 / 21，图标间距 0（各自 IconButton 自带 48 触控）；进入 260ms（淡入 + `translateY(35%→0)`），复制成功后按钮图标 180ms 从 `content_copy_rounded` 换成 `check_rounded`（`lyric_selection_toolbar.dart:25-97`）。

**歌词图片对话框**（`lyric_image_dialog.dart`）：

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 容器 | `Dialog`：宽 **520**，高 `min(780, H - 安全区 - 24)`，`insetPadding 12`，圆角 **0** + 1px `stone` 边框，底 `ivoryLight` | `:367-385` |
| 遮罩 | 黑 `@30%`（深色 `@60%`），入场 300ms（淡入 + `translateY(3.5%)` + `scale(.96→1)`，`easeOutCubic`） | `:33-57` |
| 头部 | 内边距 `20 / 16 / 8 / 16`；左 40×40 图标块（`clay@12%` 底 + `image_outlined` 22 `clayDeep`）；标题 `subheading` 20/1.25；副标题 `captionMuted` 12；右侧关闭 20 | `:269-318` |
| 分隔 | 1px `stone` | `:389,448` |
| 预览区 | 外框 `ivoryMedium` + 1px `stone`；上下渐隐 `fade = min(.12, 12/H)` 的 4 段渐变（transparent→black→black→transparent） | `:411-442` |
| 页脚 | 内边距 16；「返回选择」文字按钮最小高 48；主按钮最小高 48，底 `clay`（已保存后 `slateDark`），白字，圆角 0，按下 `scale .97`（140ms） | `:320-361`、`:493-506` |
| 导出卡片 | 固定宽 **360**，底 `ivoryMedium`，内边距 `18 / 26 / 18 / 30`；封面 1:1；标题 `heading` 28/1.25；专辑/歌手 `bodySm` `cloudDark`；分隔线 `Divider(height 20, cloudDark)`；每行歌词 **20/1.5 w600**、翻译 **14/1.5 `cloudDark`**，行间 24，原文与翻译间 4 | `:561-628` |

---

## 3. 队列视图

### 3.1 容器

| 形态 | 规格 | 依据 |
| --- | --- | --- |
| 桌面（W ≥ 720） | `Dialog`：宽 **580**，高 **自窗口 76%**，`insetPadding 32`，遮罩 `slateDark@20%` | `now_playing_page.dart:33-49` |
| 桌面内嵌（右栏 tab） | 无外框，直接铺满右栏（宽见 §1.3，高 = 内容区剩余高度） | `desktop_now_playing.dart:130-137` |
| 移动 | `showModalBottomSheet`：高 76%，底 `ivoryLight`，`showDragHandle: true`（M3 默认把柄 32×4、圆角 2） | `now_playing_page.dart:51-63` |
| 圆角 | **0**（DialogTheme / BottomSheetTheme 都是 0），elevation 0，无阴影 | `app_theme.dart:68-80` |
| 背景 | `ivoryLight #FAF9F5` | 同上 |

### 3.2 头部

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 内边距 | `20 / 8 / 8 / 12` | `playback_queue_view.dart:57` |
| 标题 | `SectionHeading('播放队列 · N 首')`：`InlineLabel` 强版（12px **w600**、大写、ls **1.6**、`slateDark`）+ 16 + 弹性 1px `stone` 横线 | `:61`、`paper_widgets.dart:394-412` |
| 关闭 | `close_rounded` IconButton（24 图标，48 触控），仅在传入 `onClose` 时出现 | `:63-69` |

### 3.3 行规格

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 行高 | `max(76, 15×1.3 + 12×1.4 + 23)` → **76**（`itemExtent` 固定，虚拟列表） | `playback_queue_view.dart:22-26,76` |
| 行内边距 | 上下 **10**、左右 **12** | `:122` |
| 列表内边距 | `16 / 0 / 16 / 16` | `:77` |
| 序号 | 宽 **22**，`monoSm` 12px，"01" 补零；当前行 `slateDark`，否则 `cloudMedium` | `:138-148` |
| 封面 | **48×48**，直角，无边框 | `:149-155` |
| 封面→文本 | 12 | `:156` |
| 曲名 | `body` 派生 **15px / 1.3**，当前行 **w600** 否则 w400，1 行省略 | `:162-172` |
| 曲名→歌手 | 3 | `:174` |
| 歌手 | `captionMuted` **12px**，`cloudMedium` | `:175-180` |
| 右侧 | 播放中显示 3 根跳动条；否则 `monoSm` 时长（`m:ss`） | `:184-188` |

### 3.4 当前行高亮

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 底色 | `oatWarm @ 60%`；非当前 `oatWarm @ 0%`（保留过渡位） | `:124-126` |
| 左侧条 | **2px** `clay`，非当前为 `clay @ 0%` | `:127-134` |
| 文本 | 曲名加粗 w600、序号 `slateDark` | `:142-146,169-171` |
| 无圆角、无外发光 | — | 同上 |

### 3.5 播放指示条

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 形态 | 3 根竖条，宽 **2.5**，右外边距 **2.5**，底对齐 | `:259-267` |
| 高度序列 | `[5,11,8] → [9,6,12] → [12,10,5] → [7,12,9]` 轮播 | `:243-248` |
| 动画 | AnimatedContainer **220ms** `easeOut`，由 100ms tick 驱动（非 repeat 控制器） | `:260-266` |
| 颜色 | `slateDark`（暖中性，不用 clay） | `:266` |

### 3.6 拖拽手柄 / 清空按钮（参考实现缺失）

- **没有**行重排拖拽：`_QueueRow` 只有 `onTap`（`playback_queue_view.dart:118-120`）。
- **没有**"清空队列"按钮：头部只有标题与关闭（`:56-71`）。
- 唯一"手柄"是移动端 bottom sheet 的 Material 默认把柄（`now_playing_page.dart:55`，规格 32×4、圆角 2）。
- 若产品要求补：按本系统语言，把柄用 `stone`，清空按钮用文字按钮（`caption` + `cloudDark`，hover 下划 1px），**不要**用红色/危险色——系统里没有 danger 色，只有 `clayDeep`。

### 3.7 CSS 实现要点

```css
.queue {
  width: 580px; max-height: 76vh;
  background: var(--ivory-light);
  border-radius: 0; box-shadow: none;
  border: 1px solid var(--stone);      /* 参考实现靠遮罩分隔，边框可选，但不加阴影 */
  display: flex; flex-direction: column;
}
.queue__head { display: flex; align-items: center; gap: 16px; padding: 8px 8px 12px 20px; }
.queue__head .label { font: 600 12px/1.4 var(--font-ui); letter-spacing: 1.6px;
                      text-transform: uppercase; color: var(--slate-dark); }
.queue__head .rule  { flex: 1; height: 1px; background: var(--stone); }

.queue__list { padding: 0 16px 16px; overflow: auto; }
.queue__row {
  display: grid;
  grid-template-columns: 22px 48px 1fr auto;
  align-items: center;
  column-gap: 0;                 /* 序号与封面紧贴，文本前才有 12 间距 */
  height: 76px; padding: 10px 12px; box-sizing: border-box;
  border-left: 2px solid transparent;
  background: transparent;
  cursor: pointer;
}
.queue__row.is-current { background: rgb(227 218 204 / .6); border-left-color: var(--clay); }
.queue__row .idx  { font: 400 12px/1.4 var(--font-ui); color: var(--cloud-medium); }
.queue__row.is-current .idx { color: var(--slate-dark); }
.queue__row .text { padding-left: 12px; min-width: 0; }
.queue__row .title { font: 400 15px/1.3 var(--font-ui); color: var(--slate-dark);
                     white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.queue__row.is-current .title { font-weight: 600; }
.queue__row .artist { margin-top: 3px; font: 400 12px/1.4 var(--font-ui); color: var(--cloud-medium); }
.bars { display: flex; align-items: flex-end; gap: 2.5px; }
.bars i { width: 2.5px; background: var(--slate-dark); transition: height 220ms ease-out; }
```

---

## 4. 桌面工作台与"桌面歌词悬浮条"

### 4.1 事实校准（必读）

`desktop_now_playing.dart` 是**整窗三栏工作台**（头部 tab / 封面栏 / 阅读栏 / 底部 dock），**不存在**独立悬浮歌词窗，也没有锁定、置顶、穿透等桌面歌词常见控件（全仓搜 `alwaysOnTop`、`桌面歌词`、`悬浮` 均 0 命中）。

因此本节分两部分：**4.2–4.3 = 源码实测**；**4.4 = 若产品确需悬浮条时的推导规格**（标注为推导，数值全部取自已有 token，不引入新色）。

### 4.2 工作台骨架实测

| 区域 | 规格 | 依据 |
| --- | --- | --- |
| 头部 | 见 §1.2；高度 ≈ **64**（上 8 + 48 触控行 + 下 8，tab 最小 44 居中） | `desktop_now_playing.dart:45-84` |
| 内容区 | 内边距 `32 / 24 / 24 / 24`，左栏 `clamp(W*.34,240,440)` | `:88-104` |
| 底部 dock | 内边距 `24 / 8 / 24 / 16`，`ivoryLight` + 顶部 1px `stone` | `:308-314` |
| 整体圆角/阴影 | 0 / 无 | `app_theme.dart:68-80`、`design_tokens.dart:267-269` |

### 4.3 dock 内"贴底信息条"规格（可视为悬浮条的现实原型）

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 背景 | `ivoryLight #FAF9F5`（不透明，**无半透明、无模糊**） | `desktop_now_playing.dart:310` |
| 边框 | 顶部 1px `stone #CCCBC8` | `:311` |
| 圆角 | 0 | 主题 |
| 高度 | 内容驱动：8 + 48（进度行，Material Slider 最小触控高）+ 48（控制行）+ 16 ≈ **120** | `:313-461` |
| 主文字 | 本 dock **不含曲名**（只有时间码 + 控制 + 音量）；呼应参考：浅色 mini 条曲名 15/1.25 + 歌手 `captionMuted`，深色播放条曲名 16/1.25 `onDark` + 歌手 `caption 12` `onDarkMuted` | `player_page.dart:2522-2536`、`player_page.dart:2712-2729` |
| 关闭类按钮 | 32×32，padding 4，图标 18，`close_rounded` | `desktop_now_playing.dart:346-359` |
| 图标按钮 | 默认 24 图标 / 48 触控；dock 内显式 23–28 | `:387-447` |

### 4.4 悬浮歌词条推导规格（源码无此物，供前端需要时使用）

按现有 token 组合，最贴近系统语言的写法：

| 项 | 值 | 来源 |
| --- | --- | --- |
| 尺寸 | 宽 `min(720, 100% - 32)`，高 **56**（单行原文 + 可选翻译时 76） | 由 dock 行高与 lyrics 行块推导 |
| 圆角 | **0**（系统全直角；若要软一档，用 `--radius-outlined 12`，不要 20+ 胶囊） | `design_tokens.dart:246` |
| 背景 | `ivoryLight` 100%；若要浮起感，用 `ivoryLight` + 1px `stone` 边框，**不要**投影/毛玻璃 | 无 BoxShadow 事实 |
| 内边距 | `16 / 8`（左右/上下） | 参照 dock `24/8` 收敛 |
| 原文 | 16px / 1.5 / w600 / `slateDark`，单行省略 | 歌词原文缩小一档 |
| 翻译 | 12px / 1.45 / `cloudDark`，与原文间距 5 | `lyric_viewport.dart:370-378` |
| 锁按钮 | 32×32，图标 18，默认 `cloudDark`，锁定后 `clayDeep` | 由关闭按钮规格推导（`:346-359`） |
| 关闭按钮 | 32×32，图标 18，`close_rounded`，hover 变 `slateDark` | 同上 |
| 拖拽区 | 整条可拖（除按钮），`cursor: grab`；无可见把柄 | 参照 bottom sheet 把柄 32×4 仅在移动端 |
| 交互 | 点击跳回 `#/now`；hover 时按钮才显现（180–200ms 淡入） | 参照 header 200ms 显隐（`now_playing_page.dart:309-311`） |

### 4.5 CSS 实现要点

```css
.dock {
  position: sticky; bottom: 0;
  background: var(--ivory-light);
  border-top: 1px solid var(--stone);
  padding: 8px 24px 16px;
  border-radius: 0;
}

/* 推导版悬浮歌词条 */
.lyric-float {
  position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%);
  width: min(720px, calc(100% - 32px));
  min-height: 56px;
  display: flex; align-items: center; gap: 12px;
  padding: 8px 8px 8px 16px;
  background: var(--ivory-light);
  border: 1px solid var(--stone);
  border-radius: 0; box-shadow: none;
  cursor: grab;
}
.lyric-float__text { flex: 1; min-width: 0; }
.lyric-float__text b { display: block; font: 600 16px/1.5 var(--font-ui); color: var(--slate-dark);
                       white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lyric-float__text i { font: 400 12px/1.45 var(--font-ui); font-style: normal; color: var(--cloud-dark); }
.lyric-float__btn { width: 32px; height: 32px; display: grid; place-items: center;
                    color: var(--cloud-dark); opacity: 0; transition: opacity 180ms ease-out; }
.lyric-float:hover .lyric-float__btn { opacity: 1; }
```

---

## 5. 音量控件

出处 `volume_control.dart`，被桌面 dock 右区（`flex:2`，右对齐）与底部播放条复用，深色面传 `onDark: true`。

| 项 | 规格 | 依据 |
| --- | --- | --- |
| 整体宽 | `min(168, 父宽)` | `volume_control.dart:36` |
| 静音按钮 | 图标 **22**，最小 **40×48**，padding **8** | `:39-44` |
| 图标切换 | `volume == 0` → `volume_off_rounded`；`< 0.5` → `volume_down_rounded`；否则 `volume_up_rounded` | `:48-53` |
| 图标色 | 浅色面 `slateDark`；`onDark` 时 `onPlayer #FAF9F5` | `:33` |
| 滑块轨道 | 高 **3**；已播 `color`（`slateDark`/`onPlayer`）；未播同色 **@ 25%** | `:58-60` |
| thumb | `clay`，半径 **5**（直径 10） | `:61-65` |
| overlay | `clay @ 12%`，半径 **10** | `:62,66-68` |
| 滑块内边距 | 水平 **8** | `:69` |
| 语义 | label「音量」，格式化 `NN%` | `:71-78` |
| 失败提示 | SnackBar「音量调节失败，请重试。」 | `:20-25` |

对比：进度条（`player_seek_bar.dart`）与音量条的差异——进度条 thumb 半径 7、overlay 15、overlay `clay@16%`、轨道 4（默认）或 3（dock 显式传参）。写 CSS 时用两个修饰类，别共用一个。

### 5.1 CSS 实现要点

```css
.volume { display: flex; align-items: center; width: min(168px, 100%); }
.volume__btn { width: 40px; height: 48px; padding: 8px; display: grid; place-items: center;
               color: var(--slate-dark); }
.volume__track { flex: 1; height: 3px; margin: 0 8px; position: relative;
                 background: linear-gradient(to right,
                   currentColor var(--vol), rgb(20 20 19 / .25) 0); }
.volume__track::after {
  content: ""; position: absolute; top: 50%; left: var(--vol);
  width: 10px; height: 10px; margin: -5px 0 0 -5px;
  border-radius: 50%; background: var(--clay);
}
```

---

## 6. 各个"有没有"清单（防止凭空造 UI）

| 元素 | 有/无 | 说明 |
| --- | --- | --- |
| 页面渐变 / 毛玻璃 | 无 | 只有纯色面 |
| 阴影 | 无 | 全系统 0 处 BoxShadow |
| 圆角卡片 | 无 | card/panel/dialog/sheet/cover 全 0 |
| 更多菜单（⋯） | 无 | 桌面头部只有返回 + 3 个 tab |
| 音量控件在 now playing 页面中部 | 无 | 只在底部 dock |
| 队列清空 / 重排 | 无 | 见 §3.6 |
| 罗马音独立行 | 无 | 见 §0 表 #8 |
| 播放速度 / 音质切换 | 无 | 本页没有 |
| 歌词"翻译开关" | 无 | 有翻译就显示，无则不显示 |
| 歌词模糊开关 | 有（默认开） | `app_state.dart:181`，σ 公式见 §2.4 |

---

## 7. Material 图标名清单（Icons.*，按出现顺序）

正在播放页 / 头部 / 传输（`now_playing_page.dart`、`desktop_now_playing.dart`）：

| 图标名 | 出现处 | 尺寸 |
| --- | --- | --- |
| `keyboard_arrow_down_rounded` | 返回（移动 + 桌面头部） | 24 默认 |
| `lyrics_outlined` | 移动歌词开关 / 桌面「歌词」tab | 24 / 19 |
| `chat_bubble_outline_rounded` | 评论（移动头部 / 桌面 tab） | 24 / 19 |
| `queue_music_rounded` | 播放队列（移动头部 / 桌面 tab） | 24 / 19 |
| `favorite_border_rounded` | 未收藏 | 24 |
| `favorite_rounded` | 已收藏（`clayDeep`） | 24 |
| `shuffle_rounded` | 随机（关） | 26 / 23 |
| `shuffle_on_rounded` | 随机（开，`clayDeep`） | 26 / 23 |
| `skip_previous_rounded` | 上一首 | 34 / 28 |
| `skip_next_rounded` | 下一首 | 34 / 28 |
| `play_arrow_rounded` | 播放 | 38 / 28 |
| `pause_rounded` | 暂停 | 38 / 28 |
| `repeat_rounded` | 循环（关） | 26 / 23 |
| `repeat_one_on_rounded` | 单曲循环（开） | 26 / 23 |
| `volume_off_rounded` | 静音 | 22 |
| `volume_down_rounded` | 音量 < 50% | 22 |
| `volume_up_rounded` | 音量 ≥ 50% | 22 |
| `info_outline_rounded` | dock 错误提示 | 16 |
| `close_rounded` | 关闭提示 / 队列关闭 / 选词工具条 / 歌词图对话框 | 18 / 24 / 21 / 20 |
| `music_note_rounded` | 缺图占位 | 默认 |
| `expand_less_rounded` | 底部播放条"展开"（呼应） | 20 |

歌词选择 / 歌词图片（`lyric_selection_toolbar.dart`、`lyric_image_dialog.dart`）：

| 图标名 | 出现处 | 尺寸 |
| --- | --- | --- |
| `select_all_rounded` | 全选 | 21 |
| `image_outlined` | 生成歌词图片 / 空态 / 对话框头部 | 21 / 40 / 22 |
| `content_copy_rounded` | 复制所选 | 20 |
| `check_rounded` | 已复制 / 已保存 | 20 / 18 |
| `check_circle_outline_rounded` | 保存成功 | 18 |
| `error_outline_rounded` | 保存失败 | 18 |
| `save_alt_rounded` | 保存图片 | 18 |

队列（`playback_queue_view.dart`）：本组件只用 `close_rounded`；播放指示条为 3 个 2.5×N 的 `AnimatedContainer`，**不是**图标。

---

## 8. 复刻自检清单（对着 1440×900 截图逐项看）

1. 页面底色是 `#F0EEE6`，没有任何渐变/阴影/毛玻璃。
2. 左栏 = 440（1440 窗），右栏 = 895；中间 32 + 1px 竖线 + 16。
3. 封面 440×440 直角、无边框、无投影；换曲是左右滑入（480ms）。
4. 歌词首行会"半出画"：焦点带在 **35%** 高度，第一行未到时可被上方遮罩吃掉一半。
5. 非聚焦行 0.97 缩放 + `#87867F` + 距离模糊（σ 上限 5），聚焦行 1.0 + `#141413`。
6. 上下遮罩高度 ≈ `min(0.22H, 1.15×rowUnit)`，边缘淡到**页面底色**而不是白色。
7. 点歌词某行 → 进度跳到该行时间；长按出现底部 480 宽工具条。
8. 队列行高 76（不是 56/60），当前行 `oatWarm 60%` + 左侧 2px `clay`。
9. 音量条 thumb 10px（clay），进度条 thumb 14px（clay），两者不要混用。
10. 全站没有任何圆角面板/阴影；唯一的"圆"是播放键（68 移动 / 48 桌面直角）、滑块 thumb、指示点。
