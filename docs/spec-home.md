# Lazer 内容页 — 像素级 HTML/CSS 规格（首页 / 搜索 / 列表行 / 歌单详情 / 专辑·歌手详情）

> 提取自 Flutter 参考实现 `E:\Lazer-3fdf89b40956d1f90f9bff242b67a8a9129d140e`（**只读，未修改任何文件**）。
> 全部数值逐行核对源码，出处格式 `文件:行号`。字体族在本实现里 serif / sans / mono **全部绑定 MiSans**，所以 CSS 里 serif 角色也用 `--font-ui`，不要引入真衬线（`lib/theme/design_tokens.dart:72-95`）。
> 颜色 / 字号 / 间距基础令牌见 `spec-shell.md` §0，本文件只补内容页新增的变量与推导值，不重复抄写。

---

## 0. 阅读约定

### 0.1 文件别名（下文所有 `别名:行号` 指下述真实路径）

| 别名 | 真实路径 |
|---|---|
| `pp` | `lib/screens/player_page.dart` |
| `pdp` | `lib/screens/playlist_detail_page.dart` |
| `cdp` | `lib/screens/catalog_detail_page.dart` |
| `pw` | `lib/theme/paper_widgets.dart` |
| `tok` | `lib/theme/design_tokens.dart` |
| `pal` | `lib/theme/app_palette.dart` |
| `thm` | `lib/theme/app_theme.dart` |
| `plate` | `lib/widgets/plate_art.dart` |
| `link` | `lib/widgets/catalog_links.dart` |
| `atc` | `lib/widgets/animated_track_cover.dart` |
| `notice` | `lib/widgets/animated_notice.dart` |
| `a11y` | `lib/widgets/accessible_controls.dart` |
| `st` | `lib/state/app_state.dart` |

### 0.2 `[K-01]` 内容页新增的推导值（叠加色与角色映射）

| 语义 | 值 | 出处 |
|---|---|---|
| 当前播放行底色 | `--oat-warm` @ 50% → `rgba(227,218,204,.5)` | `pp:2350` |
| 行 hover 底色 | `--oat-warm` @ 35% → `rgba(227,218,204,.35)` | `pp:2352` |
| 设置/动作行 hover | `--oat-warm` @ 50% | `pp:2249` |
| 导航项激活底 | `--oat-warm` @ 55% | `pp:585` |
| 导航项 hover 底 | `--ivory-light`（不是 oatWarm） | `pp:591` |
| 文本链接 hover 底 | `--oat-warm` @ 40% | `link:99` |
| 文本链接 focus 底 | `--clay` @ 18% | `link:100` |
| outlined 按钮 hover 底 | `--oat-warm` @ 45% | `pw:210` |
| 深色面（slateDark 底）上的前景 | `onInk = #FAF9F5`（亮色主题下） | `pal:29` |
| 全局 splash | `--slate-dark` @ 9%，`highlightColor = transparent` | `thm:35,45` |
| InkWell 默认 hover 叠加 | Material 3 默认（onSurface ≈ 8%，源码未覆盖） | `thm` 无 `hoverColor` 覆盖 |
| 滚动条 | 8px 宽、`--cloud-medium`、圆角 0 | `thm:101-105` |
| 封面缺图占位底（PlateArt fallback） | `--manilla` 底 + `--cloud-dark` 图标 | `plate:25-29` |
| 头像缺图占位底 | `--oat-warm`（与封面占位不同色） | `pp:327` |

### 0.3 `[K-02]` 封面占位（`.plate`）的确定行为

- 组件：`plate` 全文 42 行；`ClipRRect(borderRadius: radius ?? BorderRadius.zero)`（`plate:31-32`）→ **内容页所有封面圆角一律 0**。
- 有图：`Image(fit: BoxFit.cover)`（`plate:35-37`），尺寸由父容器决定，**超出即裁切**。
- 无图 / 加载失败：`--manilla` 纯色底 + 居中 `Icons.music_note_rounded`（尺寸走 Icon 默认 24px）+ `--cloud-dark`（`plate:25-30,38`）。
- 占位不显示首字母、不显示渐变、不显示阴影 —— demo 里的 CSS 渐变占位属于"参考实现没有的替代物"，允许但需在注释里标明偏离。
- 换曲动画（仅 Now Playing 用）：480ms，新封面从右侧滑入（`atc:18-29`）；列表/详情页封面**无换图动画**。

---

## 1. 页面骨架

### 1.1 外壳分区

- `[K-03]` 紧凑断点 `_compactBreakpoint = 720px`（`pp:97`）：`< 720px` 走底部导航 + 悬浮紧凑播放条，`>= 720px` 走左侧导航栏 + 深色播放条。
- `[K-04]` 桌面外壳结构 `Row[ _Sidebar(232px), Hairline(vertical, 1px, --stone), Expanded(内容) ]`，整体上面再叠一条 `_PlayerBar`（`pp:186-196, 246-252, 554-555`）。
- `[K-05]` 播放条在滚动区**之外**（`Column[Expanded(内容), _PlayerBar]`，`pp:247-251`），所以内容页的底部留白与播放条高度无关。
- `[K-06]` 内容页滚动容器是被 `SafeArea(top: compact, bottom: false)` 包住的（`pp:180-182`）；桌面下 top 不额外加安全区。
- `[K-07]` 紧凑外壳顶部自带一行品牌条：padding `24/8/12/0`，左侧 `Lazer`（bodySm 16/1.3），右侧设置图标 `22px`（`pp:200-221`）。
- `[K-08]` 紧凑外壳底部导航：高 `56px`，`--ivory-light` 底 + 1px `--stone` 上边线，3 等分（主页/搜索/我），激活项顶部居中 2px×28px `--slate-dark` 短线（`pp:656-684, 717-730`）。

### 1.2 内容页宽度 clamp 规则

- `[K-09]` 内容列 `max-width = 1020px`（`pp:817-818` `BoxConstraints(maxWidth: 1020)`）。
- `[K-10]` 该 1020 是**在左右 padding 之后**再夹的，且内容**左对齐不居中**（`SingleChildScrollView` 子节点默认左上对齐，`pp:813-840`）。因此宽窗口下右侧会出现"padding + 余量"的复合留白。
- `[K-11]` 实际列宽公式：`col = min(内容区宽 − 2×inset, 1020)`。以 1440px 窗口为例：内容区 `1440 − 232 − 1 = 1207`，inset 56，`1207 − 112 = 1095 → 夹到 1020`，右侧视觉留白 `56 + (1095 − 1020) = 131px`。
- `[K-12]` 注意 `tok:241` 的 `pageMaxWidth = 1280` **在本页未被使用**；内容页真正的上限是硬编码 1020（`pp:818`）。demo 若按 1280 做会整体偏宽。
- `[K-13]` padding 断点判定用的是**本视图自身的约束宽度**（即已扣掉侧栏后的内容区宽），不是窗口宽（`pp:796-798`）。

### 1.3 左右 inset（水平内边距）

- `[K-14]` 三分支（`pp:799-812`）：

| 条件（内容区宽 `w`） | 左 inset | 右 inset |
|---|---|---|
| `w > 900px` | `56px` | `56px` |
| `560px <= w <= 900px` | `32px` | `32px` |
| `w < 560px` | `24px`（`AppSpacing.lg`） | `24px` |

- `[K-15]` 对应的窗口宽换算（内容区宽 = 窗口宽 − 233，即 232 侧栏 + 1px 分隔线）：窗口 `>= 1134px` → 56；`793–1133px` → 32；`720–792px` → 24（`< 720px` 进紧凑外壳，内容区宽 = 窗口宽）。
- `[K-16]` 与 `CONTRACT-frontend.md §0.7` 的 1100/720 双断点是**近似值**；要 1:1 对齐参考实现，内容页 inset 请按上表 900/560 判。

### 1.4 垂直间距（section gap）

- `[K-17]` 页面上下 padding：上 `32px`，下 `32px + bottomInset`；`bottomInset` 当前调用点恒为 `0`（`pp:805,811,236`）。
- `[K-18]` 首页区块垂直节奏（`pp:935-973`）：

| 位置 | 间隔 | 出处 |
|---|---|---|
| 页顶 → HeroHeading | `32px`（页 padding 上） | `pp:805` |
| HeroHeading → 第一个区块 | `48px` = `section(80) × 0.6` | `pp:939` |
| 区块标题（SectionHeading）→ 区块内容 | `16px` | `pp:942,948,963,969` |
| 区块之间 | `48px` | `pp:944,959,965` |
| 最后一个区块 → 页底 | `32px` | `pp:972` + 页 padding `32px` = 视觉 `64px` |

- `[K-19]` 空区块会连同它的 48px 间隔一起被跳过（`if (...) ...[ ... ]` 展开写法，`pp:940-971`）；但 hero 后的 48px 是无条件渲染的（`pp:939`）。
- `[K-20]` 播放错误提示条 `AnimatedNotice` 占内容列第 0 位：无消息时高度 0（`pp:822-825`、`notice:21-22`）；有消息时上下各 `8px` padding、文案 14px `--clay-deep`、右侧关闭图标 16px（`notice:23-46`）。

### 1.5 滚动区 padding / 底部留白

| 页面 | 上 | 下 | 出处 |
|---|---|---|---|
| 首页 / 搜索 / 我 / 设置（`_LibraryView`） | `32px` | `32px` | `pp:805,811` |
| 歌单详情（desktop 内嵌） | `20px`（头部） | `96px` 尾部 spacer | `pdp:225,408` |
| 专辑/歌手详情 | `0`（AppBar 顶） | `40px` 尾部 spacer | `cdp:458` |

- `[K-21]` 歌单详情的 96px 是为了让最后一行滚出播放条遮挡区（`pdp:408`）；它不是 padding 而是末尾 `SliverToBoxAdapter(SizedBox(height: 96))`。
- `[K-22]` 专辑详情的 40px 同理（`cdp:458`）。
- `[K-23]` 桌面播放条高度**未写死**：`_surface` padding `24/16/24/16` + 进度条 + `8px` + 传输行（封面 48px）= 约 `104–110px`（`pp:2643-2657, 2676-2677, 2696-2705`）。HTML 里给 `min-height:96px`，内容区用 flex 分走剩余高度即可。

### 1.6 `[K-24]` CSS 实现要点（骨架）+ 建议变量名

```css
:root{
  /* 内容页骨架 */
  --content-max:1020px;
  --gutter-lg:56px;      /* 内容区宽 >900 */
  --gutter-md:32px;      /* 560–900 */
  --gutter-sm:24px;      /* <560 */
  --pad-page-y:32px;
  --gap-block:48px;      /* section*0.6 */
  --gap-block-half:40px; /* section*0.5，搜索页用 */
  --gap-heading:16px;    /* SectionHeading → 内容 */
  --rail-w:232px;        /* 侧栏 */
  --player-bar-min:96px;
  --row-h:64px;
  --row-h-translated:80px;
  --cover-xs:40px;
  --idx-w:24px;
  --dur-hover-in:120ms;
  --dur-focus:160ms;
  --dur-card:140ms;
}
```

```css
/* 内容页滚区：左对齐、不居中 */
.page{overflow-y:auto;padding:var(--pad-page-y) var(--gutter-lg);}
.page__column{max-width:var(--content-max);} /* 不设 margin:auto */
/* inset 三分支用容器查询或 JS 断点切换 --gutter-* */
@media (max-width:1133px){ .page{padding-inline:var(--gutter-md)} }
@media (max-width:792px){  .page{padding-inline:var(--gutter-sm)} }
/* 滚动条 = 参考实现样式 */
.page::-webkit-scrollbar{width:8px}
.page::-webkit-scrollbar-thumb{background:var(--cloud-medium);border-radius:0}
```

---

## 2. 首页 `_HomeView`（`pp:905-976`）

### 2.1 `_HeroHeading`（`pp:848-903`）

- `[H-01]` **字号不是 display 68 / heading 61**。角色是 `heading`（sans、w700、`line-height 1.1`、`letter-spacing -0.12px`，`tok:179-187`），字号被三档覆盖（`pp:861-867`）：

| 断点（本组件可用宽度 `c`） | font-size | 行高 |
|---|---|---|
| `c > 720px` | `56px` | `61.6px`（×1.1） |
| `560px <= c <= 720px` | `40px` | `44px` |
| `c < 560px` | `32px` | `35.2px` |

- `[H-02]` 排版断点同一处判定：`wide = c.maxWidth > 720`（`pp:858`）。
- `[H-03]` 宽布局：`Row[ title(3fr), 32px 间隙, body(2fr) ]`，两列均为 `Expanded`（`pp:886-899`）→ 左列宽 `(W−32)×3/5`、右列 `(W−32)×2/5`，`align-items: flex-start`。
- `[H-04]` 右列（副文案）额外 `padding-top: 8px`（`pp:893-894`），用于与 56px 大标题的基线做视觉对齐。
- `[H-05]` 窄布局：`Column[ title, 16px, body ]`，左对齐（`pp:876-885`）。
- `[H-06]` 副文案角色：`body`（serif 20px、`lh 1.4`，`tok:151-157`）覆盖为 `color: --cloud-dark`、`height: 1.5`（`pp:870-874`）→ 实际 `20px / 30px / #87867F`。
- `[H-07]` 首页 hero 文案：标题 `今天想听\n哪一首？`（含硬换行），`body = ''` 空字符串（`pp:938`）。**空 body 仍占据 2/5 宽度**——右半边是纯留白，不是把标题拉满。
- `[H-08]` 首页空态/加载态的 hero 换成 `发现音乐` + `浏览真实歌单，挑一首开始播放。`（`pp:917`）。
- `[H-09]` 搜索页 hero：`搜索` + `搜索曲名、音乐人、专辑或歌单。`（`pp:1482`）。
- `[H-10]` CSS 要点：

```css
.hero{display:grid;grid-template-columns:3fr 2fr;gap:32px;align-items:start}
.hero__title{font-size:56px;font-weight:700;line-height:1.1;letter-spacing:-.12px;color:var(--slate-dark);white-space:pre-line}
.hero__body{font-size:20px;line-height:1.5;color:var(--cloud-dark);padding-top:8px}
@media (max-width:720px){ .hero{grid-template-columns:1fr;gap:16px} .hero__title{font-size:40px} }
@media (max-width:560px){ .hero__title{font-size:32px} }
```
变量：`--hero-title-lg:56px; --hero-title-md:40px; --hero-title-sm:32px; --hero-body:20px; --hero-body-lh:1.5`。

### 2.2 推荐歌单区 `_RecommendedPlaylists`（`pp:978-1036`）

- `[H-11]` 列数：`columns = floor(可用宽 / 180)`，再 `clamp(2, 4)`（`pp:985`）→ `>=720px→4`、`>=540px→3`、`<360px→2`。
- `[H-12]` 单卡宽：`(可用宽 − 16×(columns−1)) / columns`（`pp:986`）；间距 `Wrap(spacing:16, runSpacing:24)`（`pp:988-989`）。
- `[H-13]` **只渲染一行**：`playlists.take(columns)`（`pp:991`）——最多 4 个，不换行、不滚动。
- `[H-14]` 卡片内部（自上而下）：正方形封面（`AspectRatio 1`，`plate` 圆角 0，`pp:1001-1007`）→ `10px`（`pp:1009`）→ 标题 `bodySm 16px / 1.3 / w600 / -0.08px`，最多 2 行省略（`pp:1010-1017`）→ 有描述时 `4px` + 描述 `captionMuted 12px / 1.4 / #B0AEA5`，1 行省略（`pp:1018-1026`）。
- `[H-15]` 无卡片底、无描边、无 padding（`Material(color: transparent)`，`pp:994-997`）；整块可点，hover 就是 Material 默认 ink 叠加。
- `[H-16]` CSS 要点：

```css
.shelf{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px 16px}
.shelf__card{display:flex;flex-direction:column;align-items:flex-start;cursor:pointer}
.shelf__cover{width:100%;aspect-ratio:1/1;border-radius:0;overflow:hidden}
.shelf__title{margin-top:10px;font-size:16px;line-height:1.3;font-weight:600;letter-spacing:-.08px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.shelf__desc{margin-top:4px;font-size:12px;line-height:1.4;color:var(--cloud-medium);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (max-width:719px){ .shelf{grid-template-columns:repeat(3,minmax(0,1fr))} }
@media (max-width:539px){ .shelf{grid-template-columns:repeat(2,minmax(0,1fr))} }
```
变量：`--shelf-min:180px; --shelf-gap-x:16px; --shelf-gap-y:24px; --shelf-title-gap:10px; --shelf-desc-gap:4px`。

### 2.3 歌单网格 `_PlaylistGrid`（`pp:1040-1070`）+ `_PlaylistCard`（`pp:1072-1148`）

- `[H-17]` 列数：可用宽 `> 760px → 2` 列，否则 `1` 列（`pp:1050`）。
- `[H-18]` 行高：`mainAxisExtent = 180 + clamp(textScale−16, 0, 24)×4`（`pp:1054-1057`）→ 常规文本缩放下**固定 180px**。
- `[H-19]` 间距：`main/cross` 均 `16px`（`pp:1058-1059`）；`shrinkWrap` + 禁滚（`pp:1061-1062`），即整页由外层滚。
- `[H-20]` 卡面：底 `--ivory-light`、1px `--stone` 全边框、**圆角 0**、`clipBehavior: antiAlias`（`pp:1078-1084`）。
- `[H-21]` 结构：`Row(stretch)[ 封面 100px 宽 × 满高(180px，object-fit:cover 裁切), Expanded(内容 padding 16px) ]`（`pp:1087-1100`）。
- `[H-22]` 内容列：标题 `bodySm 16/1.3 w600` 最多 2 行省略（`pp:1104-1111`）→ `6px`（`pp:1112`）→ 描述 `captionMuted 12/1.4` 1 行省略（`pp:1113-1118`）→ `Spacer()` 撑开（`pp:1119`）→ 底部 `Row[ TextButton('播放'), '${trackCount} 首'(captionMuted) ]`（`pp:1120-1139`）。
- `[H-23]` `'播放'` 文字按钮只覆盖了 `foregroundColor: --slate-dark`（`pp:1122-1125`），其余是 Material 默认 TextButton（`min-height 40px`、左右 padding 12–16px、16px 字号）。demo 用 `padding:0 16px;height:40px;font-size:16px` 即可。
- `[H-24]` hover 态：整卡一个 `InkWell`，无自定义 `hoverColor` → Material 默认 ink 叠加（≈8% onSurface）+ 全局 splash `--slate-dark` 9%（`thm:35`）。**没有**描边变色、**没有**封面缩放。
- `[H-25]` CSS 要点：

```css
.pcard{display:flex;height:180px;background:var(--ivory-light);border:1px solid var(--stone);
  border-radius:0;overflow:hidden;cursor:pointer}
.pcard__cover{width:100px;flex:0 0 100px}          /* 图 100×180 裁切，圆角 0 */
.pcard__body{flex:1;padding:16px;display:flex;flex-direction:column;min-width:0}
.pcard__title{font-size:16px;line-height:1.3;font-weight:600;letter-spacing:-.08px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pcard__desc{margin-top:6px;font-size:12px;line-height:1.4;color:var(--cloud-medium);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pcard__foot{margin-top:auto;display:flex;align-items:center;gap:4px}
.pcard__play{height:40px;padding:0 16px;font:400 16px/1 var(--font-ui);color:var(--slate-dark);
  background:none;border:0;cursor:pointer}
.pcard__count{font-size:12px;line-height:1.4;color:var(--cloud-medium)}
.grid-playlists{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
@media (max-width:760px){ .grid-playlists{grid-template-columns:1fr} }
```
变量：`--pcard-h:180px; --pcard-cover-w:100px; --pcard-pad:16px; --pcard-title-gap:6px`。

### 2.4 专辑网格 `_AlbumGrid`（`pp:1150-1178`）+ `_AlbumCard`（`pp:1181-1246`）

- `[H-26]` 列数：`> 820px → 4`；`> 560px → 3`；否则 `2`（`pp:1160-1164`）。
- `[H-27]` 间距 `16/16`，格子宽高比 `0.74`（`pp:1169-1171`）。以 1020px 内容宽算：列宽 `(1020−48)/4 = 243px`，格高 `243/0.74 ≈ 328px`。
- `[H-28]` 卡内结构：`Column(start)[ Expanded(正方形封面 + 右下角播放圆钮), 8px, 专辑名, 歌手名 ]`（`pp:1189-1243`）。
- `[H-29]` 封面：`AspectRatio 1` + `plate`（圆角 0），右下角悬浮按钮 `Positioned(right:10, bottom:10)`，底 `--slate-dark`、前景 `onInk #FAF9F5`、`play_arrow_rounded` 24px（`pp:1202-1224`）。**按钮常显，不是 hover 才出现**。
- `[H-30]` 专辑名：`body` 角色覆盖 `font-size 16px`、`height 1.3`（`pp:1235`）→ 16/20.8，字色 `--slate-dark`，1 行省略（`link:77`）。hover 底 `--oat-warm` 40%、focus 底 `--clay` 18%（`link:99-100`）。
- `[H-31]` 歌手名：`captionMuted` 12/1.4 `#B0AEA5`，1 行省略（`pp:1237-1242`）。
- `[H-32]` 因 `Expanded` + 正方形封面：格子高于封面时，封面顶对齐，文案下方**留空**（以 1440 窗口为例约 `40px`）——HTML 用 `align-items:start`，不要 `space-between` 拉开。
- `[H-33]` CSS 要点：

```css
.grid-albums{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}
.acard{display:flex;flex-direction:column;align-items:flex-start;aspect-ratio:.74}
.acard__art{position:relative;width:100%;aspect-ratio:1/1;overflow:hidden}
.acard__play{position:absolute;right:10px;bottom:10px;width:40px;height:40px;border:0;
  background:var(--slate-dark);color:var(--on-dark);display:grid;place-items:center;cursor:pointer}
.acard__title{margin-top:8px;font-size:16px;line-height:1.3;color:var(--slate-dark);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
.acard__artist{font-size:12px;line-height:1.4;color:var(--cloud-medium);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (max-width:820px){ .grid-albums{grid-template-columns:repeat(3,minmax(0,1fr))} }
@media (max-width:560px){ .grid-albums{grid-template-columns:repeat(2,minmax(0,1fr))} }
```
变量：`--acard-ratio:0.74; --acard-title-gap:8px; --acard-play-inset:10px`。

### 2.5 空态 `_EmptyHint`（`pp:1280-1313`）

- `[H-34]` 容器 = `PaperCard` 默认：`--ivory-light` 底、1px `--stone` 边框、圆角 0、padding `24px`（`pw:305-338`，`tok:246`）。
- `[H-35]` 内部垂直居中排列：图标 `28px` `--cloud-dark`（`pp:1296`）→ `16px`（`pp:1297`）→ 标题 `subheading` 覆盖 `18px`（w600、`lh 1.3`、`ls -0.05px`、居中，`pp:1298-1302`）→ `4px`（`pp:1303`）→ 正文 `captionMuted` 覆盖 `height 1.5`、居中（`pp:1304-1308`）。
- `[H-36]` 空态不设最小高度、不设背景图；宽度撑满内容列。
- `[H-37]` 已知的三种用法：首页加载/失败（`cloud_off_outlined`，`pp:919-923`）、搜索初始态（`search_rounded`，`pp:1496-1500`）、搜索无结果（`search_off_rounded`，`pp:1502-1506`）、我喜欢空态（`favorite_border_rounded`，`pp:829-833`）。
- `[H-38]` CSS 要点：

```css
.empty{background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;
  padding:24px;display:flex;flex-direction:column;align-items:center;text-align:center}
.empty__icon{color:var(--cloud-dark)}   /* 28px */
.empty__title{margin-top:16px;font-size:18px;font-weight:600;line-height:1.3;letter-spacing:-.05px}
.empty__body{margin-top:4px;font-size:12px;line-height:1.5;color:var(--cloud-medium)}
```

### 2.6 `_HomeView` 区块顺序总表

- `[H-39]` 顺序与条件（`pp:935-973`）：

| # | 区块 | 渲染条件 | 标题 | 组件 |
|---|---|---|---|---|
| 1 | Hero | 恒有 | `今天想听\n哪一首？` | `_HeroHeading` |
| 2 | 推荐歌单 | `recommended.isNotEmpty` | `SectionHeading('推荐歌单')` | `_RecommendedPlaylists` |
| 3 | 快速开始 | `quick.isNotEmpty` | `SectionHeading('快速开始')` | `_stackedRows(TrackRow, indent:64)` |
| 4 | 歌单 | `playlists.isNotEmpty` | `SectionHeading('歌单')` | `_PlaylistGrid` |
| 5 | 专辑 | `albums.isNotEmpty` | `SectionHeading('专辑')` | `_AlbumGrid` |

- `[H-40]` "快速开始"用的是序号列表卡（`_stackedRows`，`pp:949-958`），行规格见 §3，卡片左右不留额外 padding。
- `[H-41]` `SectionHeading` 结构（`pw:394-413`）：`InlineLabel(w600, --slate-dark, 12px, ls 1.6px, 大写)` + `16px` + `Expanded(Hairline 1px --stone)`；无 `trailing` 时 hairline 撑满剩余宽度。
- `[H-42]` 首页空/加载分支（`pp:913-931`）：`_HeroHeading('发现音乐', '浏览真实歌单，挑一首开始播放。')` → `24px` → `_EmptyHint` → `16px` → `IvoryButton('重新加载')`；容器底部没有额外 32px 尾巴（与正常分支不同）。

### 2.7 首页需要的中文文案（含出处）

| 位置 | 文案 | 出处 |
|---|---|---|
| Hero 标题 | `今天想听\n哪一首？` | `pp:938` |
| 区块 1 标题 | `推荐歌单` | `pp:941` |
| 区块 2 标题 | `快速开始` | `pp:947` |
| 区块 3 标题 | `歌单` | `pp:962` |
| 区块 4 标题 | `专辑` | `pp:968` |
| 歌单卡按钮 | `播放` | `pp:1132` |
| 歌单卡计数 | `{n} 首` | `pp:1135` |
| 空态 hero 标题 | `发现音乐` | `pp:917` |
| 空态 hero 副文案 | `浏览真实歌单，挑一首开始播放。` | `pp:917` |
| 加载中标题 | `正在加载曲库` | `pp:921` |
| 加载失败标题 | `曲库暂时不可用` | `pp:921` |
| 加载中副文案 | `请稍候。` | `pp:922` |
| 重试按钮 | `重新加载` | `pp:926` |
| 我喜欢空态标题 | `喜欢的音乐` | `pp:831` |
| 我喜欢空态正文 | `登录后查看喜欢的音乐。` / `正在读取喜欢的音乐…` | `pp:832` |
| 列表行序号 | `01`、`02`…（`padLeft(2,'0')`） | `pp:2378` |
| 时长 | `m:ss`（分钟不补零） | `pp:2459`、`st:1186-1190` |

---

## 3. 列表行 `TrackRow`（`pp:2282-2468`）

### 3.1 行容器

- `[R-01]` 内边距：水平 `24px`、垂直 `12px`（`pp:2355-2358`）。
- `[R-02]` 圆角 0 + `clipBehavior: antiAlias`（`pp:2346-2348`）。
- `[R-03]` 行高实测：内容行 = `max(封面 40px, 标题 20.8 + 歌手 16.8 = 37.6px)` + 上下 24px = **64px**；带翻译标题时为 `40 → 54.4` + 24 → 约 `78.4px`（`pdp:154-164` 的 `_normalRowHeight = 64`、`_translatedRowHeight = 80` 印证）。
- `[R-04]` 底色三态（`pp:2349-2353`）：当前播放 `--oat-warm` 50%；普通 hover `--oat-warm` 35%；默认透明。
- `[R-05]` 过渡**非对称**：进入 `120ms`，离开 `0ms`（`pp:2343-2345`）→ CSS `transition: background-color 120ms` 只写在 `:hover` 上。
- `[R-06]` 整行是点击热区（`GestureDetector(behavior: opaque)`，`pp:2339-2341`），鼠标 `cursor:pointer`（`pp:2336`）。

### 3.2 列结构（左 → 右，`pp:2364-2460`）

| # | 列 | 宽度 | 说明 |
|---|---|---|---|
| 1 | 序号 / 播放图标 | `24px`（`clamp(digits×7.5, 24, 140)`，`pp:2367-2370`；≤999 首恒为 24） | 默认 `01`（monoSm 12/1.4 `--cloud-dark`）；hover 时整格换成 `play_arrow_rounded` 18px `--slate-dark`（`pp:2371-2383`） |
| 2 | 间隙 | `8px` | `pp:2385` |
| 3 | 封面 | `40×40`，圆角 0 | `pp:2386-2395`，`plate` 圆角 0 |
| 4 | 间隙 | `16px` | `pp:2396` |
| 5 | 主列（标题/歌手/译名） | `flex 3` | `pp:2397-2437` |
| 6 | 间隙 | `16px` | `pp:2439` |
| 7 | 专辑列 | `flex 2`，仅当行内可用宽 `> 520px` | `pp:2363, 2438-2457` |
| 8 | 间隙 | `8px` | `pp:2458` |
| 9 | 时长 | 内容自适应（无固定宽），右端顶齐 | `pp:2459`，`monoSm 12px --cloud-dark` |

### 3.3 文字规格

- `[R-07]` 标题：`body` 角色覆盖 → `16px / 1.3`（20.8px 行高）；当前播放 `w600`，否则 `w400`；1 行省略（`pp:2402-2412`）。颜色恒为 `--slate-dark`（**播放中不变色**）。
- `[R-08]` 歌手：`captionMuted` → `12px / 1.4`（16.8px）`#B0AEA5`，1 行省略；有 `state` 时是文本链接（hover 底 oatWarm 40%），否则纯文本（`pp:2414-2427`、`link:99`）。
- `[R-09]` 译名（可选第三行）：`captionMuted` 同样式，1 行省略（`pp:2428-2434`）→ 此时行高变 80px（`pdp:159-160`）。
- `[R-10]` 专辑列：有 `state` 时 `captionMuted` 链接，否则 `caption`（12px）覆盖 `--cloud-dark`（`pp:2442-2456`）——两者视觉都是 12px 灰字，实现上统一成 `--cloud-medium`/`--cloud-dark` 二选一即可（源码两条路径颜色不同：链接是 `#B0AEA5`，纯文本是 `#87867F`）。
- `[R-11]` 时长：`monoSm` 12px `--cloud-dark`，`m:ss`（`pp:2459`、`st:1186-1190`）。

### 3.4 播放中高亮

- `[R-12]` **没有左侧指示条**。参考实现里唯一的"正在播放"信号是：整行底色 `--oat-warm` 50% + 标题字重 `w600`（`pp:2349-2350, 2409-2411`）。轨号、图标、颜色都不变。
- `[R-13]` 行本身也没有"播放中图标"占位；hover 才会把序号换成播放三角（`pp:2371-2376`）。所以"播放中 + hover"= 底色 50%（当前态优先，`pp:2349`）。
- `[R-14]` 侧栏导航的 2×18 竖线（`pp:383-398`）属于外壳，**不要**搬到列表行上。

### 3.5 操作按钮出现规则

- `[R-15]` 行内**没有**更多/收藏/时长右侧的按钮组。唯一"操作"是整行点击播放；hover 时序号列替换为播放图标即是唯一的显式 affordance（`pp:2371-2383`）。
- `[R-16]` 在歌单详情里行高被 `SliverVariedExtentList` 固定为 `64/80px`（`pdp:383-386`）→ 文本超长会被裁切，而不是把行撑高。

### 3.6 `_stackedRows` 卡片包（首页「快速开始」、搜索三组结果）

- `[R-17]` 卡容器：`PaperCard(padding: 0)` → `--ivory-light` 底、1px `--stone` 边框、圆角 0（`pp:1256-1263`、`pw:305-338`）。
- `[R-18]` 行与行之间插 1px `Hairline`（`--stone`），除最后一行外每行后都有；分隔线左缩进 `64px`（`pp:1266-1273`，调用处 `indent: 64` 见 `pp:958, 1520, 1540, 1556`）。
- `[R-19]` 注意缩进 64 < 序号24+8+封面40 = 72，所以分隔线起点落在封面左侧之内，视觉上从封面内缘附近开始。

### 3.7 `[R-20]` CSS 实现要点

```css
.trow{display:grid;
  grid-template-columns:24px 40px minmax(0,3fr) minmax(0,2fr) auto;
  grid-column-gap:0;align-items:center;
  padding:12px 24px;border-radius:0;overflow:hidden;cursor:pointer;
  background:transparent}
.trow--current{background:rgba(227,218,204,.5)}
.trow:hover{background:rgba(227,218,204,.35);transition:background-color 120ms}
.trow__idx{width:24px;font-size:12px;line-height:1.4;color:var(--cloud-dark);font-variant-numeric:tabular-nums}
.trow__play{display:none;width:18px;height:18px;color:var(--slate-dark)}
.trow:hover .trow__idx{display:none}
.trow:hover .trow__play{display:block}
.trow__cover{width:40px;height:40px;margin-left:8px;border-radius:0;overflow:hidden}
.trow__main{margin-left:16px;min-width:0}
.trow__title{font-size:16px;line-height:1.3;letter-spacing:-.08px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.trow--current .trow__title{font-weight:600}
.trow__artist{font-size:12px;line-height:1.4;color:var(--cloud-medium);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.trow__album{margin-left:16px;min-width:0;font-size:12px;line-height:1.4;color:var(--cloud-medium);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.trow__dur{margin-left:8px;font-size:12px;line-height:1.4;color:var(--cloud-dark);
  font-variant-numeric:tabular-nums}
@media (max-width:520px){ .trow__album{display:none}
  .trow{grid-template-columns:24px 40px minmax(0,1fr) auto} }
/* 行卡 */
.rowstack{background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;overflow:hidden}
.rowstack > * + *{border-top:1px solid var(--stone);margin-left:64px}
```
变量：`--row-pad-x:24px; --row-pad-y:12px; --row-cover:40px; --row-idx-w:24px; --row-gap-1:8px; --row-gap-2:16px; --row-album-min:521px; --divider-indent:64px; --row-current:rgba(227,218,204,.5); --row-hover:rgba(227,218,204,.35)`。

> ⚠️ 行宽度断点 520px 判定的是**行内可用宽**（`pp:2363` 读的是 `LayoutBuilder` 的 `c.maxWidth`），即已扣掉外层卡与页面 padding 之后的宽度。

---

## 4. 搜索页 `_SearchView`（`pp:1405-1563`）+ `_SearchField`（`pp:1321-1400`）

### 4.1 页面顺序与间距

- `[S-01]` 结构（`pp:1479-1560`）：`_HeroHeading('搜索', '搜索曲名、音乐人、专辑或歌单。')` → `40px`（`section×0.5`，`pp:1483`）→ `_SearchField` →（有输入时）`8px` + 命中数/状态行 → `24px` → 内容区 → 末尾 `32px`。
- `[S-02]` 有输入时状态行：`captionMuted` 12/1.4，文案三态 `正在检索…` / `搜索失败，请检查网络后重试。` / `{hits} 条匹配`（`pp:1486-1490`）。
- `[S-03]` 搜索防抖 `350ms`（`pp:1446`）；空查询时清空结果（`pp:1432-1440`）。

### 4.2 搜索框几何

- `[S-04]` 外框：`min-height: 52px`，底 `--ivory-light`，圆角 0，1px 边框；边框色默认 `--stone`、**聚焦时变 `--slate-dark`**，过渡 `160ms`（`pp:1338-1348`）。
- `[S-05]` 水平内边距 `16px`，垂直 `0`（`pp:1349`）。
- `[S-06]` 左侧图标 `Icons.search_outlined` `17px`，色 `--cloud-dark`；图标与输入框间距 `10px`（`pp:1352-1357`）。
- `[S-07]` 输入文本 16px（`bodySm`），`contentPadding: vertical 12px`（`pp:1362-1366`）→ 单行输入实际高 `20.8 + 24 ≈ 44.8px`，加上外框 min-height 52px 撑开后栏高 52px。
- `[S-08]` placeholder：`搜索曲目、专辑或歌单`，16px `--cloud-medium`（`pp:1368-1372`）。
- `[S-09]` 清除按钮仅在输入非空时出现：热区 padding `6px`，`close_rounded` `16px` `--cloud-dark`（`pp:1376-1394`），`cursor:pointer`。
- `[S-10]` 没有搜索按钮、没有 label、没有右侧分隔；回车触发 `TextInputAction.search`（`pp:1363`）。

### 4.3 结果分组

- `[S-11]` 三组，顺序固定：曲目 → 专辑 → 歌单；组标题 `SectionHeading('曲目 · {n}')` / `('专辑 · {n}')` / `('歌单 · {n}')`（`pp:1509, 1524, 1544`）。
- `[S-12]` 组内：标题后 `16px` → `_stackedRows(..., indent: 64)` 列表卡（`pp:1510-1520`，专辑组 `pp:1525-1541`，歌单组 `pp:1545-1557`）。
- `[S-13]` 组间间隔 `40px`（`pp:1523, 1543`）；**第一组（曲目）前没有 40px**，它直接跟在 24px 之后（`pp:1492`）。

### 4.4 `_MediaRow`（`pp:1567-1643`）

- `[S-14]` 内边距：水平 `24px`、垂直 `10px`（`pp:1596-1599`）。
- `[S-15]` 结构：`40×40` 封面（圆角 0，`pp:1602-1611`）→ `16px` → `Expanded(标题 16/1.3 1 行 + 副标题 12/1.4 1 行)` → `8px` → 尾部计数 `monoSm 12px --cloud-dark`（`pp:1612-1636`）。行高 ≈ `max(40, 20.8+16.8) + 20 = 60px`。
- `[S-16]` 标题是 `body` 角色覆盖 `16px / 1.3`（`pp:1617-1625`）；副标题 `captionMuted`，两行之间**无额外 gap**（`pp:1626-1631`）。
- `[S-17]` **没有 hover 底色**：外层只是 `MouseRegion + GestureDetector`，没有 `InkWell`（`pp:1588-1594`）→ demo 里 `.media-row:hover` 不要加背景。
- `[S-18]` 尾部文案内容：专辑 `{artist} · {year}` + `{trackCount} 首`（`pp:1530-1533`）；歌单 `description` + `{trackCount} 首`（`pp:1550-1551`）；计数为 0 时传空串（`pp:1533, 1551`）。

### 4.5 `[S-19]` CSS 实现要点

```css
.search{display:flex;flex-direction:column;gap:0}
.search__field{display:flex;align-items:center;min-height:52px;padding:0 16px;
  background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;
  transition:border-color 160ms}
.search__field:focus-within{border-color:var(--slate-dark)}
.search__icon{width:17px;height:17px;color:var(--cloud-dark);flex:0 0 17px}
.search__input{flex:1;margin-left:10px;height:44.8px;font-size:16px;line-height:1.3;
  letter-spacing:-.08px;background:none;border:0;outline:none;color:var(--slate-dark)}
.search__input::placeholder{color:var(--cloud-medium)}
.search__clear{padding:6px;color:var(--cloud-dark);cursor:pointer;border:0;background:none}
.search__status{margin-top:8px;font-size:12px;line-height:1.4;color:var(--cloud-medium)}
.search__body{margin-top:24px}
.search__group + .search__group{margin-top:40px}
.media-row{display:flex;align-items:center;padding:10px 24px}
.media-row__cover{width:40px;height:40px;flex:0 0 40px;border-radius:0;overflow:hidden}
.media-row__body{flex:1;min-width:0;margin-left:16px}
.media-row__title{font-size:16px;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.media-row__sub{font-size:12px;line-height:1.4;color:var(--cloud-medium);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.media-row__count{margin-left:8px;font-size:12px;line-height:1.4;color:var(--cloud-dark)}
```
变量：`--search-h:52px; --search-pad-x:16px; --search-icon:17px; --search-icon-gap:10px; --media-row-pad-y:10px; --media-row-gap:16px`。

---

## 5. 歌单详情 `PlaylistDetailView`（`pdp:42-458`）

### 5.1 头部块

- `[D-01]` 桌面内嵌参数：`horizontal = 32px`；移动（Route 推入）`24px`（`pdp:203-204`，`desktop = onBack != null`）。
- `[D-02]` 头部 padding：`左 horizontal / 上 20px / 右 horizontal / 下 24px`（`pdp:223-228`）。
- `[D-03]` 返回按钮（仅桌面内嵌时渲染）：`TextButton.icon`，`arrow_back_rounded` `18px` + 文案 `返回`，`foregroundColor --slate-dark`，按钮下方 `16px`（`pdp:232-245`）。
- `[D-04]` 封面：正方形 `152×152px`；但 `box.maxWidth < 600px` 时缩到 `100×100px`（`pdp:249-250`）。封面圆角 0（`pdp:251-254` 未传 `radius`）。
- `[D-05]` 封面右间距 `24px`（`pdp:256`）。
- `[D-06]` 元信息列（自上而下）：`InlineLabel('歌单')` 12px w600 大写 `ls 1.6px` `--slate-dark`（`pdp:261`）→ `8px`（`pdp:262`）→ 标题 `subheading` 覆盖 `28px`（桌面）/ `23px`（移动），w600、`lh 1.3`、`ls -0.05px`、最多 2 行省略（`pdp:263-270`）→ `8px` → `'{n} 首'`（`captionMuted`，`pdp:272-275`）→ `16px` → 按钮组。
- `[D-07]` 按钮组：`Wrap(spacing: 8px, crossAxisAlignment: center)`（`pdp:277-281`）：
  - `ClayButton(label:'播放全部', compact:true)` → padding `16/8`、`min-height 48px`、圆角 **`10px`**、底 `--clay`、hover/press `--clay-deep`、字 `bodySm 16px w500`、白字、`letter-spacing 0`（`pdp:282-290`、`pw:52-86`）。`tracks` 为空时 `onPressed: null` → 底 `--stone`、字 `--cloud-dark`（`pw:62,70`）。
  - `AccessibleIconButton(tooltip:'刷新歌单', icon: refresh_rounded 20px)`，Material 默认 IconButton 40×40 热区、8px padding（`pdp:291-302`、`a11y:97-137`）。
- `[D-08]` 简介（有内容时）：`20px` 间隔 → 正文 `body` 覆盖 `15px / 1.5`（`pdp:310-326`），折叠 2 行省略，`AnimatedSize 220ms`（`pdp:312-314`）→ 其后紧跟 `TextButton('展开简介'/'收起简介')`，`foregroundColor --cloud-dark`（`pdp:327-334`）。
- `[D-09]` 加载失败：`20px` + `歌单加载失败，请重试。` + `重新加载` 文字按钮（`pdp:336-342`）；加载中：`20px` + `LinearProgressIndicator`（`pdp:343-346`，轨道 `--oat-warm`、进度 `--clay`，`thm:96-100`）。

### 5.2 曲目表头（桌面且 `maxWidth > 600`）

- `[D-10]` 容器 padding：水平 `horizontal + 24` = `56px`（桌面向量）、垂直 `12px`（`pdp:355-358`）。移动下这个表头**整块不渲染**（`pdp:351` 的 `desktop && box.maxWidth > 600` 条件），公式里的 48px 仅是取值，没有实际用例。
- `[D-11]` 列：前导 `SizedBox(88px)` → `Expanded(flex 3) '歌曲 / 歌手'` → `Expanded(flex 2) '专辑'` → `'时长'`（自适应宽）；全部 `captionMuted` 12px（`pdp:359-377`）。
- `[D-12]` 88px 的来历：序号 `24` + 间隙 `8` + 封面 `40` + 间隙 `16` = 88，正好让表头文字与行内标题左缘对齐。
- `[D-13]` 表头不是 sticky（是普通 `SliverToBoxAdapter`，`pdp:351-380`）。

### 5.3 行列表

- `[D-14]` 行列表外面还包了一层 `SliverPadding(horizontal: 32/24px)`（`pdp:381-382`），叠加 `TrackRow` 自身的 24px padding（`pp:2355-2358`）后：行容器的内容左缘距页面 `56/48px`，标题文字再 `+88px`（序号 24 + 8 + 封面 40 + 16）= `144/136px`。
- `[D-15]` 行高固定：`_normalRowHeight = max(标题 20.8 + 歌手 16.8, 40) + 24 = 64px`；带译名 `= max(20.8 + 16.8×2, 40) + 24 ≈ 78.4px`（默认缓存值 80）（`pdp:154-164`、`pdp:383-386`）。
- `[D-16]` 行之间**没有分隔线**（与首页/搜索的行卡不同，`pdp:387-399` 只有 `TrackRow`）。
- `[D-17]` 空列表：`padding: 24px` + `歌单里还没有歌曲。`（`pdp:401-407`）。
- `[D-18]` 尾部 spacer `96px`（`pdp:408`）。

### 5.4 定位按钮（FAB）

- `[D-19]` 位置 `right: 24px; bottom: 24px`，`elevation 0`、方形（圆角 0）、底 `--slate-dark`、前景 `onInk`、图标 `my_location_rounded` 24px（`pdp:411-451`）。
- `[D-20]` 出现条件：当前曲目在列表中但滚出视口（`pdp:97-113`）；显示/隐藏动画 = `scale .7→1` 280ms + `opacity 0→1` 220ms，均为 `easeOutCubic`（`pdp:418-425`）。

### 5.5 `[D-21]` CSS 实现要点

```css
.pl-detail{overflow-y:auto}
.pl-head{padding:20px 32px 24px}
.pl-back{display:inline-flex;align-items:center;gap:8px;margin-bottom:16px;
  color:var(--slate-dark);font-size:16px;background:none;border:0;cursor:pointer}
.pl-back svg{width:18px;height:18px}
.pl-head__row{display:flex;align-items:flex-start;gap:24px}
.pl-head__cover{width:152px;height:152px;flex:0 0 152px;border-radius:0;overflow:hidden}
.pl-head__meta{flex:1;min-width:0}
.pl-head__eyebrow{font-size:12px;font-weight:600;letter-spacing:1.6px;text-transform:uppercase;color:var(--slate-dark)}
.pl-head__title{margin-top:8px;font-size:28px;font-weight:600;line-height:1.3;letter-spacing:-.05px;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pl-head__count{margin-top:8px;font-size:12px;line-height:1.4;color:var(--cloud-medium)}
.pl-head__actions{margin-top:16px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.pl-desc{margin-top:20px;font-size:15px;line-height:1.5;color:var(--slate-dark);
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.pl-tablehead{display:flex;align-items:center;padding:12px 56px;
  font-size:12px;line-height:1.4;color:var(--cloud-medium)}
.pl-tablehead__lead{width:88px;flex:0 0 88px}
.pl-rows{padding:0 32px}
.pl-tail{height:96px}
@media (max-width:600px){
  .pl-head__cover{width:100px;height:100px;flex-basis:100px}
  .pl-head__title{font-size:23px}
  .pl-tablehead{display:none}
}
```
变量：`--pl-gutter:32px; --pl-gutter-compact:24px; --pl-cover:152px; --pl-cover-sm:100px; --pl-title:28px; --pl-title-sm:23px; --pl-desc:15px; --pl-table-lead:88px; --pl-tail:96px`。

---

## 6. 专辑 / 歌手详情 `CatalogDetailPage`（`cdp:18-542`）

### 6.1 页面壳

- `[D-22]` `Scaffold` + `AppBar`：高 `56px`、底 `--ivory-medium`、前景 `--slate-dark`、`elevation 0`、`centerTitle: false`、标题 `专辑详情` / `歌手详情`，右侧刷新图标（`cdp:299-311`、`thm:89-95`）。标题字号走 Material 3 `titleLarge` 默认 `22px`（源码未覆盖）。
- `[D-23]` 内容滚动区尾部 `40px` spacer（`cdp:458`）；播放条在滚动区外（`cdp:463-470`）。

### 6.2 头部

- `[D-24]` 头部整体 padding `24px`（`cdp:238-239`）。
- `[D-25]` 排版断点 `narrow = maxWidth < 640px`（`cdp:319`）。
- `[D-26]` 封面：`216×216px`；窄布局 `152×152px`（`cdp:152-154`）。歌手无图时用 `--oat-warm` 底 + `person_outline_rounded` `64px` `--cloud-dark`（`cdp:156-164`）。
- `[D-27]` 布局：宽 → `Row[ 封面, 32px, Expanded(详情列) ]`；窄 → `Column[ 封面, 24px, 详情列 ]`（`cdp:243-255`）。
- `[D-28]` 详情列（自上而下）：
  1. `InlineLabel('专辑' / '歌手')` 12px w600 大写 `ls 1.6` `--slate-dark`（`cdp:174`）；
  2. `12px`；
  3. 标题：`heading` 覆盖 `40px`（宽）/ `30px`（窄），`height 1.2`，w700（`cdp:176-182`）；
  4. `12px`；
  5. 专辑：歌手名 `bodyMuted`（serif 20px / 1.4，`--cloud-dark`）（`cdp:184-190`）；歌手：`{musicCount} 首歌曲 · {albumCount} 张专辑` `bodySmMuted`（16px `--cloud-medium`）（`cdp:191-195`）；
  6. 专辑额外：`8px` + `发行日期 · 唱片公司` `captionMuted`（`cdp:196-209`）+ `8px` + `{n} 首曲目` `bodySmMuted`（`cdp:210-214`）；
  7. `20px` + 主 CTA（`cdp:216-235`）。
- `[D-29]` 主 CTA：`FilledButton.icon`，底 `--clay`、白字、方形（`shape: RoundedRectangleBorder()` = 圆角 0）、`min-height 48px`、图标 `play_arrow_rounded` 24px、文案 `播放全部`（专辑）/ `播放热门歌曲`（歌手）（`cdp:219-234`）。
- `[D-30]` 介绍区：相距 `28px` → `SectionHeading('介绍')` → `12px` → 正文 `bodySm` 覆盖 `height: 1.7`（16/27.2），最多 4 行省略；空则 `正在加载资料…` / `暂无介绍`（`cdp:256-275`）；描述长度 `> 120` 时追加 `展开介绍/收起介绍` 文字按钮（`cdp:276-280`）。

### 6.3 标签栏（仅歌手）

- `[D-31]` 吸顶 `SliverPersistentHeader`，高度固定 `56px`，底 `--ivory-medium`（`cdp:321-328, 492-503`）。
- `[D-32]` 两个等宽 tab（`热门歌曲` / `专辑`），每个 tab 底部 `2px` 指示线：激活 `--slate-dark`、未激活透明；文字 `bodySm 16px`，激活 `--slate-dark`、未激活 `--cloud-dark`；切换动画 `180ms`（`cdp:504-536`）。

### 6.4 曲目/专辑内容

- `[D-33]` 专辑页顶部有 `SectionHeading('曲目')`，padding `24/4/24/12`（`cdp:330-334`）；歌手页的"热门歌曲"tab 没有这个标题。
- `[D-34]` 行列表：`SliverList` 直接铺 `TrackRow`，行自带 24px 水平 padding，**没有外层 SliverPadding、没有分隔线**（`cdp:353-367`）→ 行内容左缘距页面 `24px`，标题文字在 `24 + 88 = 112px` 处。
- `[D-35]` 专辑 tab 网格：`SliverGridDelegateWithMaxCrossAxisExtent(maxCrossAxisExtent: 240px, crossAxisSpacing: 20px, mainAxisSpacing: 24px, childAspectRatio: 0.74)`，外层 padding `24px`（`cdp:369-378`）。
- `[D-36]` 网格项：正方形封面（`plate` 圆角 0）→ `8px` → 专辑名 `bodySm 16px` 1 行 → 年份 `captionMuted` 1 行（`cdp:395-415`）。
- `[D-37]` 状态文案：加载中 `CircularProgressIndicator(strokeWidth: 2)` + `40px` padding（`cdp:335-343`）；错误/空 `_message`：`padding 24px`、`bodySmMuted`、可选 `重试` 文字按钮（`cdp:286-296, 344-352`）；分页 `加载更多专辑` 居中文字按钮（`cdp:448-456`）。

### 6.5 `[D-38]` CSS 实现要点

```css
.detail{overflow-y:auto}
.detail__head{padding:24px}
.detail__head--wide{display:flex;align-items:flex-start;gap:32px}
.detail__head--narrow{display:flex;flex-direction:column;gap:24px}
.detail__cover{width:216px;height:216px;flex:0 0 216px;border-radius:0;overflow:hidden}
.detail__eyebrow{font-size:12px;font-weight:600;letter-spacing:1.6px;text-transform:uppercase;color:var(--slate-dark)}
.detail__title{margin-top:12px;font-size:40px;font-weight:700;line-height:1.2;letter-spacing:-.12px}
.detail__sub{margin-top:12px;font-size:20px;line-height:1.4;color:var(--cloud-dark)}
.detail__meta{margin-top:8px;font-size:12px;line-height:1.4;color:var(--cloud-medium)}
.detail__count{margin-top:8px;font-size:16px;line-height:1.3;color:var(--cloud-medium)}
.detail__cta{margin-top:20px;height:48px;padding:0 24px;display:inline-flex;align-items:center;gap:8px;
  background:var(--clay);color:#fff;border:0;border-radius:0;font-size:16px;cursor:pointer}
.detail__intro{margin-top:28px}
.detail__desc{margin-top:12px;font-size:16px;line-height:1.7;display:-webkit-box;
  -webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.detail__tabs{position:sticky;top:0;height:56px;display:flex;background:var(--ivory-medium);z-index:1}
.detail__tab{flex:1;border:0;background:none;font-size:16px;color:var(--cloud-dark);
  border-bottom:2px solid transparent;transition:border-color 180ms}
.detail__tab--active{color:var(--slate-dark);border-bottom-color:var(--slate-dark)}
.detail__albumgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,240px));
  gap:24px 20px;padding:24px}
.detail__tail{height:40px}
@media (max-width:640px){ .detail__cover{width:152px;height:152px;flex-basis:152px}
  .detail__title{font-size:30px} }
```
变量：`--detail-cover:216px; --detail-cover-sm:152px; --detail-title:40px; --detail-title-sm:30px; --detail-gap:32px; --detail-gap-sm:24px; --detail-tail:40px; --tabs-h:56px; --album-cell-max:240px`。

---

## 7. 文案总表（demo 直接抄，含出处）

| 场景 | 文案 | 出处 |
|---|---|---|
| 歌单详情 AppBar | `歌单` | `pdp:23` |
| 歌单详情返回 | `返回` | `pdp:239` |
| 歌单详情 eyebrow | `歌单` | `pdp:261` |
| 歌单详情计数 | `{n} 首` | `pdp:273` |
| 歌单详情主按钮 | `播放全部` | `pdp:283` |
| 歌单详情刷新 tooltip | `刷新歌单` | `pdp:292` |
| 歌单简介折叠 | `展开简介` / `收起简介` | `pdp:333` |
| 歌单加载失败 | `歌单加载失败，请重试。` | `pdp:338` |
| 歌单重试按钮 | `重新加载` | `pdp:341` |
| 表头（三列） | `歌曲 / 歌手`、`专辑`、`时长` | `pdp:365, 371, 376` |
| 歌单空列表 | `歌单里还没有歌曲。` | `pdp:405` |
| 定位按钮 tooltip | `定位正在播放的歌曲` | `pdp:434` |
| 专辑/歌手 AppBar | `专辑详情` / `歌手详情` | `cdp:301` |
| eyebrow | `专辑` / `歌手` | `cdp:174` |
| 专辑计数 | `{n} 首曲目` | `cdp:212` |
| 歌手计数 | `{n} 首歌曲 · {m} 张专辑` | `cdp:193` |
| 专辑/歌手主按钮 | `播放全部` / `播放热门歌曲` | `cdp:233` |
| 介绍标题 | `介绍` | `cdp:257` |
| 介绍占位 | `暂无介绍` / `正在加载资料…` | `cdp:264` |
| 介绍折叠 | `展开介绍` / `收起介绍` | `cdp:279` |
| 曲目标题 | `曲目` | `cdp:333` |
| 空/分页 | `暂无歌曲` / `暂无专辑` / `加载更多专辑` | `cdp:352, 447, 453` |
| 标签 | `热门歌曲` / `专辑` | `cdp:524` |
| 刷新 tooltip | `刷新` | `cdp:304` |
| 通用重试 | `重试` | `cdp:293` |
| 通知关闭 tooltip | `关闭提示` | `notice:41` |
| 搜索 hero | `搜索` / `搜索曲名、音乐人、专辑或歌单。` | `pp:1482` |
| 搜索 placeholder | `搜索曲目、专辑或歌单` | `pp:1368` |
| 搜索状态 | `正在检索…` / `{n} 条匹配` | `pp:1488` |
| 搜索错误 | `搜索失败，请检查网络后重试。` | `pp:1463` |
| 搜索重试 | `重试搜索` | `pp:1494` |
| 搜索初始空态 | `开始搜索` / `输入你想听的曲名或音乐人。` | `pp:1498-1499` |
| 搜索无结果 | `没有找到结果` / `换一个关键词再试。` | `pp:1504-1505` |
| 搜索分组 | `曲目 · {n}` / `专辑 · {n}` / `歌单 · {n}` | `pp:1509, 1524, 1544` |
| 首页 hero | `今天想听\n哪一首？` | `pp:938` |
| 首页区块标题 | `推荐歌单` / `快速开始` / `歌单` / `专辑` | `pp:941, 947, 962, 968` |
| 首页歌单卡 | `播放`、`{n} 首` | `pp:1132, 1135` |
| 首页加载/失败 | `发现音乐`、`浏览真实歌单，挑一首开始播放。` | `pp:917` |
| 首页空态 | `正在加载曲库` / `曲库暂时不可用`、`请稍候。` | `pp:921-922` |
| 首页重试 | `重新加载` | `pp:926` |

---

## 8. Material 图标清单（内联 sprite 需要准备的 symbol）

| 图标名 | 用于 | 出处 |
|---|---|---|
| `home_outlined` | 侧栏/底栏 主页 | `pp:87` |
| `search_outlined` | 侧栏/底栏 搜索、搜索框左图标（17px） | `pp:88, 1353` |
| `favorite_border_rounded` | 侧栏 我喜欢、我喜欢空态 | `pp:89, 830` |
| `settings_outlined` | 侧栏/紧凑顶栏 设置 | `pp:90, 215, 511` |
| `person_outline` | 侧栏 我 | `pp:91` |
| `person_outline_rounded` | 头像占位、歌手封面占位（64px） | `pp:331, cdp:160` |
| `music_note_rounded` | 封面缺图占位 | `plate:28` |
| `play_arrow_rounded` | 专辑卡播放钮（24px）、行 hover（18px）、详情主 CTA、播放键 | `pp:1222, 2373, 2926, cdp:232` |
| `pause_rounded` | 播放中按钮 | `pp:2926, 3051` |
| `chevron_right_rounded` | 动作行箭头（18px）、歌手选择对话框（24px） | `pp:2268, link:38` |
| `arrow_back_rounded` | 歌单详情返回（18px） | `pdp:236` |
| `refresh_rounded` | 侧栏歌单刷新（17px）、歌单详情刷新（20px）、详情页刷新（24px） | `pp:416, pdp:299, cdp:308` |
| `close_rounded` | 搜索清除（16px）、通知关闭（16px） | `pp:1388, notice:43` |
| `search_rounded` | 搜索初始空态 | `pp:1497` |
| `search_off_rounded` | 搜索无结果空态 | `pp:1503` |
| `cloud_off_outlined` | 首页曲库不可用空态 | `pp:920, 2171` |
| `library_music_outlined` | 我/歌单空态 | `pp:2187` |
| `my_location_rounded` | 歌单详情定位 FAB | `pdp:447` |
| `expand_less_rounded` | 播放条展开提示 | `pp:2735` |
| `skip_previous_rounded` / `skip_next_rounded` | 播放条上一/下一首 | `pp:2547, 2560, 2764, 2777` |
| `shuffle_rounded` / `shuffle_on_rounded` | 随机播放 | `pp:2756-2757` |
| `repeat_rounded` / `repeat_one_on_rounded` | 循环播放 | `pp:2785-2786` |
| `queue_music_rounded` | 播放队列 | `pp:2815` |
| `login_rounded` / `logout_rounded` | 登录/退出 | `pp:1715, 2081` |
| `favorite_rounded` | 已喜欢标记（clay 色） | `pp:1982` |

---

## 9. 实现前必读：最容易做错的细节

1. **Hero 标题不是 68 / 61px**：角色是 `heading` 但字号被覆盖成 `56 / 40 / 32`（`pp:861-867`），断点 720 与 560；且首页 `body` 是空串，右列仍占 2/5 宽（`pp:938`）。
2. **卡片圆角是 0，不是 24**：`PaperCard` 注释写 "24px radius"（`pw:303`）但令牌 `AppRadius.card = 0`（`tok:246`）；`PlaylistCard` 也显式 `BorderRadius.zero` + 1px `--stone` 边框（`pp:1080-1083`）。同理 `ClayButton` 实际圆角 `10px`（`pw:72-74`），不是令牌里的"上 0 下 8"。
3. **播放中没有左侧指示条**：只有 `--oat-warm` 50% 底 + 标题 `w600`（`pp:2349, 2409-2411`）；hover 才把序号换成播放三角；离开 hover 的过渡时长是 `0ms`（`pp:2343-2345`）。另外专辑列在行宽 `<= 520px` 时整列消失（`pp:2363`），搜索页的 `_MediaRow` 完全没有 hover 底色（`pp:1588-1594`）。

---

## 10. 规格条目索引（用于验收核对）

**骨架 K（24 条）**：K-01 叠加色/角色映射 · K-02 封面占位行为 · K-03 紧凑断点 720 · K-04 桌面外壳结构 232+1 · K-05 播放条在滚动区外 · K-06 SafeArea top · K-07 紧凑顶栏 · K-08 底栏 56 · K-09 内容列 1020 · K-10 左对齐不居中 · K-11 列宽公式 · K-12 pageMaxWidth 1280 未用 · K-13 断点看内容区宽 · K-14 inset 三分支 · K-15 窗口宽换算 · K-16 与契约断点的差异 · K-17 页上下 padding 32 · K-18 首页垂直节奏表 · K-19 空区块跳过 48 · K-20 错误通知条 · K-21 歌单尾 96 · K-22 详情尾 40 · K-23 播放条高度 · K-24 CSS 要点。

**首页 H（42 条）**：H-01 hero 字号三档 · H-02 wide 720 · H-03 3:2 分栏 · H-04 右列 top 8 · H-05 窄布局 16 gap · H-06 副文案 20/1.5 cloudDark · H-07 首页文案与空 body · H-08 空态 hero · H-09 搜索 hero · H-10 hero CSS · H-11 推荐列数 clamp · H-12 卡宽公式 · H-13 take(columns) 单行 · H-14 推荐卡内部 · H-15 无卡片底 · H-16 推荐 CSS · H-17 歌单网格 2/1 · H-18 行高 180 · H-19 间距 16 · H-20 卡面 ivoryLight+stone+0 · H-21 封面 100 满高 · H-22 内容列内部 · H-23 播放按钮默认 TextButton · H-24 hover 默认 ink · H-25 歌单卡 CSS · H-26 专辑列数 4/3/2 · H-27 比例 0.74 · H-28 卡结构 · H-29 播放钮常显 10/10 · H-30 专辑名字号 · H-31 歌手名 captionMuted · H-32 底部留白成因 · H-33 专辑卡 CSS · H-34 空态容器 · H-35 空态内部 · H-36 空态无最小高 · H-37 空态四种用法 · H-38 空态 CSS · H-39 区块顺序表 · H-40 快速开始用行卡 · H-41 SectionHeading 结构 · H-42 首页空/加载分支。

**列表行 R（20 条）**：R-01 padding 24/12 · R-02 圆角 0 · R-03 行高 64/80 · R-04 三态底色 · R-05 非对称过渡 · R-06 整行热区 · R-07 标题字号字重 · R-08 歌手链接 · R-09 译名第三行 · R-10 专辑列颜色差异 · R-11 时长格式 · R-12 无左侧指示条 · R-13 当前+hover 优先级 · R-14 侧栏竖线不属于行 · R-15 无操作按钮组 · R-16 固定行高裁切 · R-17 行卡容器 · R-18 分隔线缩进 64 · R-19 缩进小于头像列 · R-20 CSS 要点。

**搜索 S（19 条）**：S-01 页面顺序与间距 · S-02 状态行 · S-03 防抖 350 · S-04 外框 52/1px/0 · S-05 水平 16 · S-06 图标 17+10 · S-07 文本 16/v-pad 12 · S-08 placeholder · S-09 清除按钮 · S-10 无搜索按钮 · S-11 三组顺序 · S-12 组内 16 · S-13 组间 40（首组无） · S-14 行 padding 24/10 · S-15 行结构 40+16+8 · S-16 标题副标题无 gap · S-17 无 hover 底 · S-18 尾部文案内容 · S-19 CSS 要点。

**详情 D（38 条）**：D-01 horizontal 32/24 · D-02 头部 padding · D-03 返回按钮 · D-04 封面 152/100 · D-05 gap 24 · D-06 元信息列 · D-07 按钮组（clay 圆角 10） · D-08 简介 15/1.5 折叠 · D-09 加载/失败 · D-10 表头 padding 56/12 · D-11 表头三列 · D-12 88px 来历 · D-13 表头不吸顶 · D-14 行容器水平 padding · D-15 固定行高 · D-16 无分隔线 · D-17 空列表 24 · D-18 尾 96 · D-19 FAB 24/24 · D-20 FAB 出现条件与动画 · D-21 歌单详情 CSS · D-22 AppBar 56 · D-23 详情尾 40 · D-24 头部 padding 24 · D-25 narrow 640 · D-26 封面 216/152 + 歌手占位 · D-27 宽窄布局 · D-28 详情列七段 · D-29 CTA 方形 clay 48 · D-30 介绍区 · D-31 吸顶 tab 56 · D-32 tab 2px 指示线 · D-33 曲目标题 padding · D-34 行无外层 padding · D-35 专辑网格 240/20/24/0.74 · D-36 网格项 · D-37 状态文案 · D-38 专辑/歌手详情 CSS。

**合计 143 条规格条目**（K 24 + H 42 + R 20 + S 19 + D 38）。
