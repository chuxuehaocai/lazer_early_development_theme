# Lazer 外壳 chrome — 像素级 HTML/CSS 规格

> 提取自 Flutter 参考实现 `E:\Lazer-3fdf89b40956d1f90f9bff242b67a8a9129d140e`（只读，未修改）。
> 所有数值逐行核对源码，出处格式 `文件:行号`。凡源码为逻辑值（ratio、alpha、枚举）的，另行标注 `（无单位）`。
> 适用范围：桌面标题栏、左侧导航栏、桌面播放栏、compact 底部导航、列表行、通用按钮/卡片/Hairline。

---

## 0. 令牌底座（写 CSS 前先落地）

### 0.1 颜色

| CSS 变量 | 值 | 语义 | 出处 |
|---|---|---|---|
| `--slate-dark` | `#141413` | 主文字、标题、hairline 深色、播放栏同色系 | `lib/theme/design_tokens.dart:19` |
| `--ivory-medium` | `#F0EEE6` | 页面画布、标题栏底色 | `design_tokens.dart:22` |
| `--ivory-light` | `#FAF9F5` | 卡片/面板高空一级的表面 | `design_tokens.dart:25` |
| `--cloud-medium` | `#B0AEA5` | 弱化文字、未激活导航项 | `design_tokens.dart:28` |
| `--cloud-dark` | `#87867F` | outlined 边框、标题栏文字/glyph | `design_tokens.dart:31` |
| `--stone` | `#CCCBC8` | 1px hairline 分隔线 | `design_tokens.dart:34` |
| `--slate-medium` | `#3D3D3A` | 深色面上的边线、禁用图标 | `design_tokens.dart:37` |
| `--oat-warm` | `#E3DACC` | 次级暖色面、hover 底色 | `design_tokens.dart:40` |
| `--manilla` | `#F5E3C7` | 强调卡片底色、主按钮 hover | `design_tokens.dart:43` |
| `--clay` | `#D97757` | 唯一彩色强调（CTA、进度 thumb） | `design_tokens.dart:49` |
| `--clay-deep` | `#C6613F` | clay 的 hover/pressed | `design_tokens.dart:52` |
| `--on-dark` | `#FAF9F5` | 深色面带上的文字 | `design_tokens.dart:55` |
| `--on-dark-muted` | `#B0AEA5` | 深色面上的弱化文字 | `design_tokens.dart:58` |
| `--player-surface` | `#141413` | 播放栏底色（**硬编码，不随明暗主题翻转**） | `lib/theme/app_palette.dart:30` |
| `--on-player` | `#FAF9F5` | 播放栏上的文字/进度已完成段 | `app_palette.dart:31` |

**CSS 要点**：写 `:root{--slate-dark:#141413;--ivory-medium:#F0EEE6;--ivory-light:#FAF9F5;--cloud-medium:#B0AEA5;--cloud-dark:#87867F;--stone:#CCCBC8;--slate-medium:#3D3D3A;--oat-warm:#E3DACC;--manilla:#F5E3C7;--clay:#D97757;--clay-deep:#C6613F;--on-dark:#FAF9F5;--on-dark-muted:#B0AEA5;--player-surface:#141413;--on-player:#FAF9F5}`，全部用变量引用，禁止出现 `#fff` 作为表面色。

### 0.2 字体与字号

| CSS 变量 / 角色 | 规格 | 出处 |
|---|---|---|
| `--font-sans` | `'MiSans'`，fallback `Segoe UI / Microsoft YaHei UI / sans-serif` | `design_tokens.dart:72-78` |
| `--font-serif` | 名义 serif，实际绑定 `'MiSans'`（**没有真衬线**） | `design_tokens.dart:82-87` |
| caption | `12px / 1.4（行高 16.8px） / letter-spacing -0.24px / 400` | `design_tokens.dart:102-109` |
| captionMuted | 同上，色 `--cloud-medium` | `design_tokens.dart:111-118` |
| captionStrong | 同上，`w600`，色 `--slate-dark` | `design_tokens.dart:120-128` |
| bodySm | `16px / 1.3（20.8px） / -0.08px / 400` | `design_tokens.dart:132-139` |
| body | `20px / 1.4（28px） / 400` | `design_tokens.dart:151-157` |
| monoSm | `12px / 1.4（16.8px）`，色 `--cloud-dark` | `design_tokens.dart:207-213` |
| wordmark | `12px / 1.0 / w700 / letter-spacing 3.2px` | `design_tokens.dart:216-224` |
| subheading | `24px / 1.3 / w600 / -0.05px` | `design_tokens.dart:168-176` |

**CSS 要点**：`body{font-family:var(--font-sans);font-size:16px;line-height:1.3;letter-spacing:-0.08px;color:var(--slate-dark)}`；所有「serif」角色在 CSS 里也用 `--font-sans`，不要引入 Georgia。

### 0.3 间距 / 圆角 / 阴影

- 间距基数 `4px`；`xs 4 / sm 8 / md 16 / lg 24 / xl 32 / xxl 48 / section 80 / pageMaxWidth 1280`（`design_tokens.dart:232-242`）。
- 圆角：`card 0`、`outlined 12px`、`filledButton = 上 0 下 8px`（`design_tokens.dart:245-263`）。
- 阴影：**全系统 0 阴影**，层级只靠色调与 1px 描边（`design_tokens.dart:265-269`）。

**CSS 要点**：`*{box-sizing:border-box}` 且全局 `box-shadow:none`；`--radius-card:0;--radius-outlined:12px;--radius-filled-bottom:8px`。

### 0.4 深色主题的边界（只作为事实记录）

`AppPalette` 在深色下会整体换色（`app_palette.dart:11-26`），但 `playerSurface` / `onPlayer` 是硬编码常量（`app_palette.dart:30-31`），**播放栏永远是 #141413**。做 HTML 时若要单主题，锁死亮色即可。

---

## 1. 标题栏（自绘 window frame）

### 1.1 栏体几何
- 高度 `40px`（= 10 × 4px 基数）（`lib/widgets/window_frame.dart:18`，注释 `:16-17`）。
- 底色 `--ivory-medium #F0EEE6`（`window_frame.dart:150`）。
- 整条是拖拽区（`DragToMoveArea`，`window_frame.dart:151`）；Windows 另有窗口边缘 4px 缩放热区（`window_frame.dart:79`）。
- 结构：`Column[ bar(40px), Hairline ]`，栏体在 Navigator 之外，压在所有路由之上（`window_frame.dart:67-75`、`:143-193`）。

**CSS 要点**：`.titlebar{height:40px;display:flex;align-items:center;background:var(--ivory-medium);border-bottom:1px solid var(--stone);-webkit-app-region:drag}` —— 底部 1px 用背景或 `border-bottom` 皆可，但必须是 `--stone`。

### 1.2 左侧内边距
- 非 macOS：左内边距 `16px`（`AppSpacing.md`）（`window_frame.dart:156`）。
- macOS：留给系统红绿灯，`84px`（`window_frame.dart:155-156`）；Windows/Linux 用 `16px`。做 Web/Windows 版只实现 `16px`。

**CSS 要点**：`.titlebar__title{margin-left:16px}`。

### 1.3 标题文本
- 样式 = `caption`：`12px / 1.4（16.8px） / letter-spacing -0.24px / 字重 400`（`caption` 未设 `fontWeight`，取默认 400），颜色被覆盖为 `--cloud-dark #87867F`（`window_frame.dart:143-144`、`:165-168`；`design_tokens.dart:102-109`）。
- 单行、`overflow: ellipsis`（`window_frame.dart:163-164`）。
- 容器 `Expanded`：标题吃满剩余宽度，把按钮顶到最右（`window_frame.dart:158-160`）。
- 文本内容常量 `'Lazer'`（`window_frame.dart:14`）。

**CSS 要点**：`.titlebar__title{flex:1;min-width:0;font:400 12px/1.4 var(--font-sans);letter-spacing:-0.24px;color:var(--cloud-dark);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}`。

### 1.4 三个窗口按钮的盒子
- 每个 `46px × 40px`（`_buttonWidth = 46`、`_barHeight = 40`，`window_frame.dart:19`、`:247-248`）。
- 无圆角、无外边距、无阴影，横向紧贴，总占宽 `138px`，右边缘与窗口齐平（`window_frame.dart:16-17` 注释、`:245-250`）。
- 顺序：最小化 → 最大化/还原 → 关闭（`window_frame.dart:170-185`）。
- 点击光标 `click`（`window_frame.dart:239`）。

**CSS 要点**：`.wbtn{width:46px;height:40px;flex:0 0 46px;border:0;border-radius:0;background:transparent;display:grid;place-items:center;cursor:pointer}`，三个连续排列，容器 `padding-right:0`。

### 1.5 默认态与 hover 态配色

| 状态 | 背景 | glyph 颜色 | 出处 |
|---|---|---|---|
| 默认（三个都是） | `transparent` | `--cloud-dark #87867F` | `window_frame.dart:224-233` |
| hover 最小化/最大化 | `--oat-warm #E3DACC` | `--slate-dark #141413` | `window_frame.dart:226-233` |
| hover 关闭 | `--slate-dark #141413`（反相） | `--on-dark #FAF9F5` | `window_frame.dart:224-233` |

- 过渡时长 `100ms`（`AnimatedContainer`，`window_frame.dart:246`）。
- 无 press 态单独定义（点击即执行）。

**CSS 要点**：`.wbtn:hover{background:var(--oat-warm)} .wbtn:hover svg{color:var(--slate-dark)} .wbtn--close:hover{background:var(--slate-dark)} .wbtn--close:hover svg{color:var(--on-dark)}`，容器加 `transition:background-color .1s linear`，glyph 用 `stroke:currentColor;fill:none`。

### 1.6 glyph 盒与笔画几何
- glyph 盒 `18px × 18px`（`_glyphBox = 18`，`window_frame.dart:20`、`:251-253`）。
- 1px stroke，`PaintingStyle.stroke`（`window_frame.dart:280-283`）。
- 最小化：一条水平线，从 `(cx-4.5, cy+0.5)` 到 `(cx+4.5, cy+0.5)` → 宽 `9px`，下沉 `0.5px` 半像素对齐（`window_frame.dart:286-291`）。
- 最大化：`9px × 9px` 空心矩形 `(cx±4.5, cy±4.5)`（`window_frame.dart:292-296`）。
- 还原：后窗只画上+右边，折线 `(cx-1.5, cy-7.5) → (cx+7.5, cy-7.5) → (cx+7.5, cy+1.5)`；前窗 `9px × 9px` 矩形 `(cx-7.5, cy-1.5)` 到 `(cx+1.5, cy+7.5)`（`window_frame.dart:297-308`）。
- 关闭：两条 `9px × 9px` 对角线 `(cx±4.5, cy±4.5)`（`window_frame.dart:309-319`）。
- 即：所有 glyph 实际绘制范围 `15px × 15px`（`±7.5`），住在 `18px` 盒里。

**CSS 要点**：统一 `svg{width:18px;height:18px;stroke:currentColor;stroke-width:1;fill:none}`，坐标按 `viewBox="0 0 18 18"`：线 `x1=4.5 x2=13.5 y=9.5`、方框 `x=4.5 y=4.5 w=9 h=9`、关闭 `M4.5 4.5 L13.5 13.5 M13.5 4.5 L4.5 13.5`。

### 1.7 关闭键的特殊性
- 只有关闭键 hover 走反相（深底浅 glyph），另两个走暖底深 glyph（`window_frame.dart:223-233`）。
- 语义标签分别：`最小化 / 最大化 / 还原窗口 / 关闭窗口`（`window_frame.dart:212-217`），做 DOM 时对应 `aria-label`。

**CSS 要点**：用独立类 `.wbtn--close` 覆盖，不要靠 `:last-child` 顺带改色（顺序变了就错）。

### 1.8 底部分隔线
- 组件 `Hairline()` 默认 = 高 `1px`、满宽、色 `--stone #CCCBC8`（`lib/theme/paper_widgets.dart:353-367`；调用 `window_frame.dart:190`）。
- 不是阴影、不是边框渐变，就是 1px 实色。

**CSS 要点**：`.titlebar{border-bottom:1px solid var(--stone)}` 或同级 `.hairline{height:1px;background:var(--stone)}`；不要用 `box-shadow:0 1px` 模拟。

---

## 2. 左侧导航栏 `_Sidebar`

### 2.1 宽度：**固定 232px，不是 clamp**
- `SizedBox(width: 232)`（`lib/screens/player_page.dart:554-555`）；在 `Row` 中作为非 flex 子项得到紧约束，实际恒为 `232px`。
- 折叠规则是二元的：视口宽 `< 720px`（`_compactBreakpoint`，`player_page.dart:97`、判定 `:174`）时**整条侧栏不渲染**（`player_page.dart:186-196`），改由底部 tab 承担导航；`>= 720px` 恒为 `232px`，没有中间值。
- 计算式（可直接抄）：`sidebarWidth = viewportWidth < 720 ? 0 : 232px`。

**CSS 要点**：`.sidebar{flex:0 0 232px;width:232px}` + `@media (max-width:719px){.sidebar{display:none}}`。

### 2.2 高度与滚动兜底
- 侧栏高度由内容撑出，自身不滚；只有可用高 `< 420px` 时整列包进滚动容器：`SingleChildScrollView(child: SizedBox(height: 420, child: content))`（`player_page.dart:556-562`）。
- 固定块高度可加总：用户区 `92px`（`20+8+36+8+20`）+ 导航组 `176px`（`4×44`）+ 分隔线块 `33px`（`20+1+12`）+ 「我的歌单」行 `40px` + 歌单列表（弹性）+ 底部 hairline `1px` + 设置块 `68px`（`12+44+12`）= `410px + 列表`。
- 也就是说 `420px` 阈值 ≈ 固定块之和 + 10px 列表可视高度（对比 `:369`、`:403-404`、`:506`、`:554-562`）。

**CSS 要点**：`.sidebar{display:flex;flex-direction:column;overflow:hidden}`，列表区 `flex:1 1 auto;min-height:0;overflow-y:auto`；外层 `@media (max-height:419px){.sidebar{overflow-y:auto} .sidebar__inner{min-height:420px}}`。

### 2.3 背景与右侧 1px Hairline
- 侧栏自身不设背景色，直接吃 `Scaffold` 的 `--ivory-medium`（`player_page.dart:168-169`、`:308-310` 的 Column 无 `color`）。
- 右边缘是一条独立 `Hairline(vertical: true)` = 宽 `1px`、色 `--stone`、高度撑满内容区（`player_page.dart:195`；`paper_widgets.dart:363-365`）。
- 这条线在 `Row` 里与侧栏并列，**位于播放栏之上方的内容区**，不穿过深色播放栏（播放栏在 `Column` 外层，`player_page.dart:246-252`）。

**CSS 要点**：`.shell-row{display:flex;height:100%} .sidebar{border-right:1px solid var(--stone)}`（用 border 即可，别额外加元素）。

### 2.4 顶部账号/用户区
- 外框 padding `LTRB(20px, 20px, 16px, 20px)`（`player_page.dart:311-312`）。
- 内层可点区块 padding 垂直 `8px`（`player_page.dart:318-319`），圆角 `0`（`player_page.dart:314`）。
- 头像 `36px × 36px`，圆角 `0`，占位底色 `--oat-warm`，占位图标 `person_outline_rounded` `22px`（`player_page.dart:322-339`）。
- 头像与文字间距 `12px`（`player_page.dart:341`）。
- 主行：`bodySm 16px/1.3` + `w600`，色 `--slate-dark`，单行 ellipsis（`player_page.dart:346-355`）。
- 次行：`captionMuted 12px/1.4`，色 `--cloud-medium`（`player_page.dart:356-359`）。
- 区块总高 `20+8+36+8+20 = 92px`。
- ⚠️ 侧栏**没有** logo / wordmark 区：顶部第一块就是上面这个账号块（`player_page.dart:311-367` 之前无任何元素）。`AppText.wordmark`（`12px / w700 / ls 3.2px`）只在登录卡片里用了一次、写作 `'LAZER'`（`lib/screens/login_page.dart:83`），不属于外壳；compact 顶部那条写的是 `'Lazer'`（`bodySm`，非 wordmark，`player_page.dart:205-209`）。做外壳时不要凭 wordmark 令牌自己加一个 logo 条。

**CSS 要点**：`.user{padding:20px 16px 20px 20px} .user__btn{display:flex;align-items:center;gap:12px;padding:8px 0} .user__avatar{width:36px;height:36px;border-radius:0;background:var(--oat-warm)}`。

### 2.5 导航组容器
- `SizedBox(height: sections.length * 44px)` = `4 × 44px = 176px`（`player_page.dart:368-369`、`:290-295`）。
- 内部 `Stack`：底层 `Column` 四个 `_NavItem`，上层绝对定位的选中指示条（`player_page.dart:370-399`）。
- 四个导航项固定为：主页 / 搜索 / 我喜欢 / 我（`player_page.dart:290-295`）。

**CSS 要点**：`.nav{position:relative;height:176px}`，指示条用 `position:absolute` 挂在 `.nav` 上而不是每项内部。

### 2.6 导航项盒子
- 每项高 `44px`（`player_page.dart:579-580`）。
- 外层水平 padding `12px`（`player_page.dart:581-582`）→ Material 宽 `232-24 = 208px`。
- 内层 padding `left 28px / right 16px`（`player_page.dart:593-594`）→ 内容区宽 `208-44 = 164px`。
- 圆角 `0`，裁剪 `antiAlias`（`player_page.dart:583-588`）。
- 内容左缘推导：图标左缘 x = `12 + 28 = 40px`；文字左缘 x = `40 + 18 + 12 = 70px`；文字右缘内缩 `12 + 16 = 28px`。

**CSS 要点**：`.nav-item{height:44px;margin:0 12px;padding:0 16px 0 28px;display:flex;align-items:center;gap:12px;border-radius:0;overflow:hidden}`。

### 2.7 图标与文字
- 图标 `18px`（`player_page.dart:597-603`）；图标与文字间距 `12px`（`player_page.dart:604`）。
- 文字 `bodySm` 覆盖为 `15px`，行高沿用 `1.3`（`19.5px`）（`player_page.dart:606-610`）。
- 字重：选中 `w600` / 未选中 `w400`（`player_page.dart:610`）。
- 颜色：选中 `--slate-dark`、未选中 `--cloud-dark`（`player_page.dart:600-602`、`:610-613`）。
- 图标名：主页 `home_outlined`、搜索 `search_outlined`、我喜欢 `favorite_border_rounded`、我 `person_outline`、设置 `settings_outlined`（`player_page.dart:86-92`）。

**CSS 要点**：`.nav-item__icon{width:18px;height:18px;flex:0 0 18px} .nav-item__label{font-size:15px;line-height:1.3;letter-spacing:-0.08px;color:var(--cloud-dark)}`，选中态切 `font-weight:600` 与 `color:var(--slate-dark)`。

### 2.8 选中 / hover 态（两套不同底色）
- 选中：`--oat-warm` + `alpha 0.55`（`player_page.dart:584-586`）。
- hover：`InkWell.hoverColor = --ivory-light`（**全不透明**，`player_page.dart:591`）。这意味着 hover 一个已选中的项时，`--ivory-light` 会整块覆盖掉 `--oat-warm 55%`——不是叠加变深。
- 无左边框、无圆角变化；指示条单独存在（见 2.9）。
- 过渡：Material ink 默认（主题 `splashColor = slateDark 9%`、`highlightColor transparent`，`lib/theme/app_theme.dart:34-35`、`:45`）。

**CSS 要点**：`.nav-item[aria-selected=true]{background:rgb(227 218 204 / .55)} .nav-item:hover{background:var(--ivory-light)}` —— hover 规则必须写在选中规则之后（同优先级后者胜），才能复刻「hover 覆盖选中」的行为。

### 2.9 左侧选中指示条
- 绝对定位在导航 `Stack` 内：`left: 24px`、`top: index*44px + 13px`、`width: 2px`、`height: 18px`、色 `--slate-dark`（`player_page.dart:383-397`）。
- 移动动画 `240ms` `easeInOutCubic`；透明度 `160ms`，无选中项时 `opacity: 0`（`player_page.dart:385-394`）。
- `18px` 在 `44px` 项内垂直居中（上下各 `13px`）。
- 关键：指示条**不属于** `_NavItem`，它盖在项外面，x 落在项外层 padding 的 `12~40px` 空档里。

**CSS 要点**：`.nav__marker{position:absolute;left:24px;width:2px;height:18px;background:var(--slate-dark);opacity:1;transition:top .24s cubic-bezier(.65,0,.35,1),opacity .16s linear}`，`top:calc(var(--idx) * 44px + 13px)`；不要把指示条放进 `.nav-item` 的 `padding-left` 里。

### 2.10 分隔线 +「我的歌单」标题行
- 分隔线：`Padding LTRB(24px, 20px, 24px, 12px)` 包一个水平 `Hairline`（`player_page.dart:402-405`）→ 线宽 `232-48 = 184px`，块高 `20+1+12 = 33px`。
- 标题行：`Padding(only(left: 24px, right: 12px))`（`player_page.dart:406-407`）；文本 `captionStrong` = `12px/1.4` `w600` `-0.24px` 色 `--slate-dark`（`player_page.dart:410-411`；`design_tokens.dart:120-128`）。
- 行尾（登录态）一个刷新按钮：`AccessibleIconButton`，`Icons.refresh_rounded` `17px`（`player_page.dart:413-419`）；尺寸沿用 Material `IconButton` 默认（padding `8px`，命中区约 `40px`，代码未覆写）。
- 行高由该按钮撑起约 `40px`，文本在垂直居中位置。

**CSS 要点**：`.sidebar__divider{margin:20px 24px 12px} .sidebar__heading{display:flex;align-items:center;padding:0 12px 0 24px;min-height:40px;font:600 12px/1.4 var(--font-sans);letter-spacing:-0.24px}`。

### 2.11 歌单列表区
- 列表 padding 水平 `12px`（`player_page.dart:450-451`）。
- 每项底部间距 `4px`（`player_page.dart:455-456`）→ 行节奏 `56px`。
- 行内：圆角 `0`，裁剪（`player_page.dart:461-462`）；内层 padding `10px` 四边（`player_page.dart:469-470`）。
- 缩略图 `32px × 32px`，圆角 `0`（`player_page.dart:473-480`）。
- 缩略图与文字间距 `10px`（`player_page.dart:481`）。
- 文字：`caption` 覆盖为 `13px`，行高 `1.4`（`18.2px`），单行 `ellipsis` 截断（`player_page.dart:482-491`）。
- 单行高 `10+32+10 = 52px`；加上间距共 `56px`。
- 选中：底色 `--oat-warm`（**全不透明**）；hover：`--oat-warm` `alpha 0.5`（`player_page.dart:457-467`）。
- 空态/未登录：`Padding(all: 24px)` + `captionMuted('登录后同步你的歌单')`（`player_page.dart:423-449`）。

**CSS 要点**：`.playlist{padding:0 12px} .playlist__row{display:flex;align-items:center;gap:10px;padding:10px;margin-bottom:4px;border-radius:0;background:transparent} .playlist__row:hover{background:rgb(227 218 204 / .5)} .playlist__row[aria-selected=true]{background:var(--oat-warm)} .playlist__thumb{width:32px;height:32px;border-radius:0} .playlist__name{font-size:13px;line-height:1.4;letter-spacing:-0.24px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}`。

### 2.12 底部设置入口
- 底部 hairline：`Padding(horizontal: 24px)` 包水平 Hairline（`player_page.dart:501-504`）→ 线宽 `184px`。
- 设置块：`Padding(vertical: 12px)`（`player_page.dart:505-506`），内含一个标准 `_NavItem('设置', settings_outlined)`（`player_page.dart:509-514`），规格与 2.6/2.7 完全一致。
- 该块的选中指示条：`left: 24px; top: 13px; width: 2px; height: 18px`，位置相对内部 `Stack`（块内顶距 `12px`），色 `--slate-dark`；切换动画 `220ms`（淡入 + `Offset(0,1)→0` 上移）（`player_page.dart:515-548`）。
- 块总高 `12+44+12 = 68px`。

**CSS 要点**：`.sidebar__footer{padding:12px 0;position:relative} .sidebar__footer .nav-item{margin:0 12px}`，指示条 `top:calc(12px + 13px)`（相对 footer）。

---

## 3. 播放栏 `_PlayerBar`（桌面，非 compact）

### 3.1 外壳
- 底色 `--player-surface #141413`（`player_page.dart:2644-2648`；`app_palette.dart:30`）。
- 顶边 1px `--slate-medium #3D3D3A`（`player_page.dart:2647`）。
- padding `LTRB(24px, 16px, 24px, 16px)`（`AppSpacing.lg / md`，`player_page.dart:2649-2654`）。
- 无圆角、无阴影；位于 shell 的 `Column` 底部，是实体栏（不浮层、不半透明）（`player_page.dart:246-252`）。
- 内部无竖直分隔线；唯一分隔元素就是顶部那条 1px 横线。

**CSS 要点**：`.playerbar{background:var(--player-surface);border-top:1px solid var(--slate-medium);padding:16px 24px;border-radius:0}`。

### 3.2 总高度 = 103px（由内容决定）
- 组成：`border-top 1px` + `padding-top 16px` + 内容 `70px` + `padding-bottom 16px`。
- 内容 `70px` = 进度条 `14px` + 间距 `8px` + 主行 `48px`（`player_page.dart:2673-2677`）。
- 主行高 `48px` 由左段 `48×48` 封面与右段 `minHeight 48px` 的音量图标按钮决定（中段主按钮只有 `44px`）（`player_page.dart:2696-2699`、`lib/widgets/volume_control.dart:43`）。
- 展开式：`barH = 1 + 16 + (14 + 8 + 48) + 16 = 103px`。
- 宽高都不写死，靠 flex 撑满；栏高随字号缩放会略变（textScaler 影响文本列），CSS 里可用 `min-height:103px`。

**CSS 要点**：`.playerbar{display:flex;flex-direction:column;gap:8px}` + `.playerbar__row{display:flex;align-items:center;height:48px}`；总高用 `min-height:103px` 保险。

### 3.3 进度条 `_SeekSlider`
- 容器高 `14px`（`player_page.dart:2945-2946`）。
- 轨道高 `3px`（`player_page.dart:2949`）。
- 已完成段色 `--on-player #FAF9F5`；未完成段色 `--slate-medium #3D3D3A`（`player_page.dart:2950-2951`）。
- thumb：`--clay` 实心圆，半径 `6px` → 直径 `12px`（`player_page.dart:2952-2954`）。
- hover/拖拽 overlay：`--clay` `alpha 0.18`，半径 `13px`（`player_page.dart:2953`、`:2955`）。
- 代码未设置 `SliderThemeData.padding`（对比音量滑块的 `horizontal 8px`），即轨道按组件默认内缩，做 1:1 复刻建议 `padding: 0`（`player_page.dart:2947-2956`）。

**CSS 要点**：`.seek{height:14px;display:flex;align-items:center;position:relative} .seek__track{height:3px;width:100%;background:var(--slate-medium)} .seek__fill{height:3px;background:var(--on-player)} .seek__thumb{width:12px;height:12px;border-radius:50%;background:var(--clay);position:absolute;transform:translateX(-50%)}`，hover 加 `.seek::after{...background:rgb(217 119 87 / .18);width:26px;height:26px;border-radius:50%}`。

### 3.4 左段（flex 3）：封面 + 元信息
- 占位比例 `flex: 3`（`player_page.dart:2681-2683`）。
- 整段可点（打开 Now Playing），cursor `click`（`player_page.dart:2690-2694`）。
- 封面 `48px × 48px`，圆角 `0`（`player_page.dart:2696-2705`）。
- 封面与文字列间距 `16px`（`player_page.dart:2706`）。
- 文字列与尾部图标间距 `8px`（`player_page.dart:2733`）。
- 尾部 `expand_less_rounded` `20px`，色 `--on-dark-muted`（`player_page.dart:2734-2738`）。
- 空态文本「未选择曲目」：`bodySm 16px/1.3`，色 `--on-dark-muted`（`player_page.dart:2683-2689`）。

**CSS 要点**：`.playerbar__left{flex:3 1 0;min-width:0;display:flex;align-items:center;gap:16px;cursor:pointer} .cover-48{width:48px;height:48px;border-radius:0;object-fit:cover}`。

### 3.5 标题 / 歌手排版
- 标题：`body`（20px）覆盖为 `fontSize 16px`、`height 1.25`（`20px`）、色 `--on-dark #FAF9F5`、字重 `400`（未设 `fontWeight`）、单行 ellipsis（`player_page.dart:2712-2721`）。
- 歌手：`caption` `12px/1.4（16.8px）`、`-0.24px`、字重 `400`、色 `--on-dark-muted #B0AEA5`、单行 ellipsis（`player_page.dart:2722-2729`）。
- 两行紧排，无额外间距；文字列高约 `36.8px`，小于封面 `48px`，垂直居中。

**CSS 要点**：`.ptitle{font:400 16px/1.25 var(--font-sans);letter-spacing:-0.08px;color:var(--on-dark);white-space:nowrap;overflow:hidden;text-overflow:ellipsis} .partist{font:400 12px/1.4 var(--font-sans);letter-spacing:-0.24px;color:var(--on-dark-muted)}`。

### 3.6 中段（flex 2）：传输控制簇
- 占位比例 `flex: 2`，内容整体居中，外包 `FittedBox(scaleDown)`：窗口变窄时整簇等比缩小而不是换行/溢出（`player_page.dart:2747-2753`）。
- 顺序：随机 → 上一首 → 播放/暂停 → 下一首 → 循环（`player_page.dart:2754-2790`）。
- 每个图标按钮盒子 `36px × 36px`（`player_page.dart:3001`）。
- 图标尺寸：随机/循环 `20px`（默认值，`player_page.dart:2969`）；上一首/下一首 `26px`（`:2766`、`:2779`）。
- 按钮之间统一 `6px` 间距（`player_page.dart:2762`、`:2769`、`:2775`、`:2782`）。
- 簇总宽 = `36×4 + 44 + 6×4 = 212px`；簇高 = `44px`。
- 播放主按钮 `44px × 44px`（见 3.7）。

**CSS 要点**：`.playerbar__center{flex:2 1 0;display:flex;justify-content:center;align-items:center} .transport{display:flex;align-items:center;gap:6px} .tbtn{width:36px;height:36px;display:grid;place-items:center}`；窄屏用 `transform:scale()` 或 `zoom` 复刻 `FittedBox`，别让簇换行。

### 3.7 播放主按钮 `_PlayPauseButton`
- 尺寸 `44px × 44px`，**圆角 0**（`BoxShape.rectangle`，未给 radius）（`player_page.dart:3038-3049`）。
- 可用态底色 `--ivory-light #FAF9F5`，hover `--manilla #F5E3C7`，禁用 `--slate-medium`（`player_page.dart:3044-3049`）。
- 图标 `26px`：暂停 `pause_rounded` / 播放 `play_arrow_rounded`；色可用 `--slate-dark`，禁用 `--on-dark-muted`（`player_page.dart:3050-3056`）。
- 过渡 `120ms`（`player_page.dart:3039`）。
- 它是深色栏上唯一的浅色实心块；clay 不参与主按钮。

**CSS 要点**：`.pp{width:44px;height:44px;border:0;border-radius:0;background:var(--ivory-light);color:var(--slate-dark);display:grid;place-items:center;transition:background-color .12s linear} .pp:hover{background:var(--manilla)}`。

### 3.8 图标按钮 `_DarkIconButton` 状态色
- 盒子 `36px × 36px`，图标居中，`HitTestBehavior.opaque`，cursor 可用时 `click`（`player_page.dart:2994-3002`）。
- 颜色解析顺序（重要）：禁用 → `--slate-medium #3D3D3A`；`active || hovering` → `--on-dark #FAF9F5`；其余 → `--on-dark-muted #B0AEA5`（`player_page.dart:2988-2992`）。
- 即：**默认是弱化的 #B0AEA5，不是白色**；hover 或激活才提到纯象牙白。
- 激活态（shuffle/repeat）同时会换图标：`shuffle_on_rounded` / `repeat_one_on_rounded`（`player_page.dart:2755-2760`、`:2784-2790`）。
- 无背景块、无圆角、无边框；hover 只变 glyph 颜色。

**CSS 要点**：`.tbtn{color:var(--on-dark-muted)} .tbtn:hover,.tbtn[aria-pressed=true]{color:var(--on-dark)} .tbtn:disabled{color:var(--slate-medium);cursor:default}`；尺寸用 `width:36px;height:36px;display:grid;place-items:center`，图标本身 `20px`/`26px`。

### 3.9 右段（flex 3）：时间 + 音量 + 队列
- 占位比例 `flex: 3`，内容右对齐（`player_page.dart:2797-2801`）。
- 时间文本 `monoSm 12px/1.4`，色 `--on-dark-muted`，仅当视口宽 `>= 1100px` 且有待播曲目时出现（`player_page.dart:2802-2809`）。
- 时间与音量间距 `16px`（`player_page.dart:2810`）。
- 尾部队列按钮 `queue_music_rounded` `20px`，盒子 `36px × 36px`（`player_page.dart:2814-2818`）。
- 右段高度 `48px`，由音量图标按钮 `minHeight 48px` 决定（`volume_control.dart:43`）。
- 音量控件用 `Flexible` 包裹，可被压缩（`player_page.dart:2811-2813`）。

**CSS 要点**：`.playerbar__right{flex:3 1 0;display:flex;align-items:center;justify-content:flex-end;gap:16px} .ptime{font:400 12px/1.4 var(--font-sans);color:var(--on-dark-muted);letter-spacing:0}`；时间用 `@media (max-width:1099px){.ptime{display:none}}`。

### 3.10 音量控件 `VolumeControl`
- 总宽 `min(168px, 可用宽)`（`volume_control.dart:35-36`）。
- 静音/音量图标按钮：`iconSize 22px`，`constraints minWidth 40px / minHeight 48px`，`padding 8px`，颜色 `--on-player`（`volume_control.dart:39-54`）。
- 图标按音量切换：`0` → `volume_off_rounded`；`< .5` → `volume_down_rounded`；否则 `volume_up_rounded`（`volume_control.dart:48-52`）。
- 滑块：轨道 `3px`；已完成 `--on-player`；未完成 `--on-player` `alpha 0.25`；thumb `--clay` 半径 `5px`（直径 `10px`）；overlay `--clay` `alpha 0.12` 半径 `10px`；滑块自身水平 padding `8px`（`volume_control.dart:57-70`）。
- 无外框、无背景；与播放栏同底色。

**CSS 要点**：`.volume{display:flex;align-items:center;max-width:168px;width:100%} .volume__btn{min-width:40px;min-height:48px;padding:8px;color:var(--on-player)} .volume__track{height:3px;background:rgb(250 249 245 / .25);margin:0 8px} .volume__fill{height:3px;background:var(--on-player)} .volume__thumb{width:10px;height:10px;border-radius:50%;background:var(--clay)}`。

### 3.11 hover / 禁用汇总（桌面播放栏）

| 元素 | 默认 | hover | 激活/选中 | 禁用 | 出处 |
|---|---|---|---|---|---|
| 左段整体 | 无底色 | 无底色变化（仅 cursor pointer） | — | — | `player_page.dart:2690-2694` |
| 图标按钮 | glyph `--on-dark-muted` | glyph `--on-dark` | glyph `--on-dark` | glyph `--slate-medium` | `player_page.dart:2988-2992` |
| 播放主按钮 | 底 `--ivory-light` / glyph `--slate-dark` | 底 `--manilla` | — | 底 `--slate-medium` / glyph `--on-dark-muted` | `player_page.dart:3044-3056` |
| 进度 thumb | `--clay` r6 | overlay `--clay .18` r13 | — | — | `player_page.dart:2950-2955` |
| 音量图标/滑块 | `--on-player` | overlay `--clay .12` r10 | — | — | `volume_control.dart:57-70` |

**CSS 要点**：把这些写成语义化类（`.is-active` / `[disabled]`），颜色全部走变量；hover 不改变尺寸、不加阴影、不加下划线。

### 3.12 compact 播放栏（`_PlayerBar(compact: true)`）
- 外边 `Material` 底色 `--ivory-light`，`Container` 只加 `border-top: 1px --stone`（`player_page.dart:2614-2620`）。
- 结构（`player_page.dart:2621-2636`）：
  1. 传输行 padding `LTRB(16px, 10px, 12px, 6px)`；
  2. 进度行 padding 水平 `16px`；
  3. 底部占位 `4px`（有安全区时 `safe-area-bottom + 4px`）。
- 传输行内容（`player_page.dart:2494-2566`）：封面 `42px × 42px` 圆角 0 → 间距 `10px`（`AppSpacing.sm + 2`）→ 标题 `15px / 1.25`（`18.75px`）色 `--slate-dark` → 歌手 `captionMuted 12px`；右侧间距 `4px` → `_LightIconButton` `34px × 38px`（图标 `22px`）→ `2px` → `_LightPlayButton` `40px × 40px`（图标 `24px`）→ `2px` → `_LightIconButton`。
- `_LightIconButton`：色 normal `--slate-dark` / hover `--clay-deep` / disabled `--stone`（`player_page.dart:2857-2876`）。
- `_LightPlayButton`：底色 `--clay`，hover `--clay-deep`，禁用 `--stone`；图标 `24px`，色 `--on-dark` / 禁用 `--cloud-dark`；圆角 `0`；过渡 `120ms`（`player_page.dart:2915-2932`）。
- 进度条：高 `12px` 的命中区，轨道 `2px` `--stone` 贴底，已完成 `2px` `--clay`，可点/拖整条（`player_page.dart:2571-2610`）。
- 总高 = `1 + 10 + 42 + 6 + 12 + 4 = 75px`（无安全区时）。

**CSS 要点**：`.playerbar--compact{background:var(--ivory-light);border-top:1px solid var(--stone)} .playerbar--compact .row{padding:10px 12px 6px 16px;display:flex;align-items:center;gap:10px} .seek-mini{height:12px;margin:0 16px;position:relative} .seek-mini__track{position:absolute;left:0;right:0;bottom:0;height:2px;background:var(--stone)} .seek-mini__fill{position:absolute;left:0;bottom:0;height:2px;background:var(--clay)}`。

---

## 4. compact 顶部条与 `_BottomNav`（视口 < 720px）

### 4.1 compact 顶部条
- 只在 compact 出现：`Padding LTRB(24px, 8px, 12px, 0)`，左侧文本 `'Lazer'` 用 `bodySm 16px/1.3`，右侧 `settings_outlined` `22px` 的 `IconButton`（`player_page.dart:200-221`）。
- 无底色、无底边线——直接浮在 `--ivory-medium` 上；`SafeArea(top: compact)` 由外层负责（`player_page.dart:180-182`）。
- 标题用 `--slate-dark`（`bodySm` 默认色），不是标题栏那种 `--cloud-dark`。

**CSS 要点**：`.compact-top{display:flex;align-items:center;padding:8px 12px 0 24px;background:transparent}`。

### 4.2 `_BottomNav` 容器
- 底色 `--ivory-light`，`border-top: 1px --stone`（`player_page.dart:656-660`）。
- `SafeArea(top: false)` 后固定高 `56px`（`player_page.dart:661-664`）。
- 三个等分项，`crossAxisAlignment.stretch`（`player_page.dart:665-680`）。
- 总高 = `1 + 56 (+ 底部安全区)`。

**CSS 要点**：`.bottomnav{background:var(--ivory-light);border-top:1px solid var(--stone);height:56px;display:flex;padding-bottom:env(safe-area-inset-bottom)}`。

### 4.3 `_BottomNavItem` 内容
- 图标 `20px`（`player_page.dart:735`）。
- 图标与文字间距 `4px`（`player_page.dart:736`）。
- 文字：`caption` 覆盖为 `11px`，行高 `1.4`（`15.4px`），外包 `FittedBox(scaleDown)`（`player_page.dart:737-751`）。
- 垂直居中（`MainAxisAlignment.center`）（`player_page.dart:732-733`）。
- 图标色：选中 `--slate-dark` / 未选中 `--cloud-dark`（`player_page.dart:701-703`、`:735`）。
- 文字色：选中 `--slate-dark` / 未选中 `--cloud-medium`；字重 `w600` / `w400`（`player_page.dart:741-749`）。
- 只列三项：主页、搜索、我（「我喜欢」不上底栏）（`player_page.dart:668-672`）。

**CSS 要点**：`.tabnav-item{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;color:var(--cloud-dark)} .tabnav-item__label{font:400 11px/1.4 var(--font-sans);letter-spacing:-0.24px;color:var(--cloud-medium)}`。

### 4.4 `_BottomNavItem` 选中态
- 整项底色 `--oat-warm` `alpha 0.55`，未选中 `--ivory-light`（`player_page.dart:708-711`）。
- 顶部指示条：宽 `28px`、高 `2px`、色 `--slate-dark`，水平居中贴顶（`player_page.dart:717-730`）。
- 无圆角、无边框、无阴影。

**CSS 要点**：`.tabnav-item[aria-selected=true]{background:rgb(227 218 204 / .55)} .tabnav-item[aria-selected=true]::before{content:"";position:absolute;top:0;left:50%;transform:translateX(-50%);width:28px;height:2px;background:var(--slate-dark)}`（项需 `position:relative`）。

### 4.5 compact 层的叠放顺序
- 外层 `Column`：`Expanded(内容) → _PlayerBar(compact) → _BottomNav`（`player_page.dart:254-264`）。
- 即播放栏压在底栏**之上**、内容区之下；三者都是实体块，不重叠。

**CSS 要点**：`.shell--compact{display:flex;flex-direction:column;height:100dvh}`，内容 `flex:1;min-height:0;overflow:auto`。

---

## 5. 列表行与操作行（内容区 chrome）

### 5.1 `TrackRow` 行盒
- padding 水平 `24px`、垂直 `12px`（`player_page.dart:2355-2358`）。
- 圆角 `0` + `overflow: hidden`（`player_page.dart:2346-2348`）。
- 背景三态：当前播放 `--oat-warm 0.5`；hover `--oat-warm 0.35`；其余 `--oat-warm 0`（透明）（`player_page.dart:2349-2353`）。
- 过渡：进入 `120ms`，离开 `0ms`（`player_page.dart:2343-2345`）。
- 整行可点，cursor `click`（`player_page.dart:2335-2341`）。

**CSS 要点**：`.track{display:flex;align-items:center;padding:12px 24px;border-radius:0;transition:background-color 0s} .track:hover{background:rgb(227 218 204 / .35);transition-duration:.12s} .track[aria-current=true]{background:rgb(227 218 204 / .5)}`。

### 5.2 序号列
- 宽度 = `clamp(位数 × 7.5px × textScale, 24px, 140px)`（`player_page.dart:2366-2370`）。
- 文本：`monoSm 12px/1.4`，色 `--cloud-dark`，左补零两位，单行 ellipsis（`player_page.dart:2377-2383`）。
- hover 时**整列换成图标**：`play_arrow_rounded` `18px`，色 `--slate-dark`（`player_page.dart:2371-2376`）。

**CSS 要点**：`.track__idx{width:24px;font:400 12px/1.4 var(--font-sans);color:var(--cloud-dark)}`，hover 用 `.track:hover .track__idx .num{display:none}` + `.play{display:none}` 互换，别用 JS。

### 5.3 封面与标题列
- 序号后间距 `8px`（`player_page.dart:2385`）。
- 封面 `40px × 40px`，圆角 `0`（`player_page.dart:2386-2395`）。
- 封面后间距 `16px`（`player_page.dart:2396`）。
- 标题列 `flex: 3`（`player_page.dart:2397-2398`）。
- 标题：`body 20px` 覆盖为 `16px / 1.3`（`20.8px`），当前曲目 `w600`，否则 `w400`，单行 ellipsis（`player_page.dart:2402-2413`）。
- 歌手：`captionMuted 12px/1.4`（`player_page.dart:2414-2427`）。
- 可选第三行翻译标题：`captionMuted`（`player_page.dart:2428-2434`）。

**CSS 要点**：`.track__cover{width:40px;height:40px;border-radius:0} .track__title{font:400 16px/1.3 var(--font-sans);letter-spacing:-0.08px;color:var(--slate-dark)} .track__sub{font:400 12px/1.4 var(--font-sans);letter-spacing:-0.24px;color:var(--cloud-medium)}`。

### 5.4 专辑列与时长
- 专辑列仅当行宽 `> 520px` 出现（`player_page.dart:2363`），`flex: 2`，前置间距 `16px`（`player_page.dart:2438-2441`）。
- 专辑文字：`caption 12px/1.4` 色 `--cloud-dark`（或 `captionMuted`），单行 ellipsis（`player_page.dart:2442-2456`）。
- 时长：前置 `8px`，`monoSm 12px/1.4`（`player_page.dart:2458-2459`）。

**CSS 要点**：`.track__album{flex:2 1 0;min-width:0;font:400 12px/1.4 var(--font-sans);color:var(--cloud-dark)} @media (max-width:520px){.track__album{display:none}}`。

### 5.5 行高计算
- 盒高 = `12 + max(40px 封面, 文字列高) + 12`。
- 两行文字时文字列 `20.8 + 16.8 = 37.6px < 40px` → 行高 `64px`。
- 带翻译标题（三行）时文字列 `54.4px` → 行高 `78.4px`。
- 结论：常规行 `64px`，最多 `78.4px`；CSS 用 `min-height:64px` + `align-items:center` 复刻。

**CSS 要点**：`.track{min-height:64px}`，不要写死 `height`，否则三行变体被裁。

### 5.6 设置项行 `_ActionRow`
- padding 水平 `24px`、垂直 `14px`（`player_page.dart:2251-2254`）。
- 背景：hover `--oat-warm 0.5`，常态 `--oat-warm 0`；进入 `120ms`，离开 `0ms`（`player_page.dart:2244-2250`）。
- 前置图标 `16px` 色 `--slate-dark`；图标后间距 `10px`（`player_page.dart:2257-2258`）。
- 文本 `bodySm 16px/1.3` `w600`（`player_page.dart:2260-2265`）。
- 尾部 `chevron_right_rounded` `18px` 色 `--cloud-medium`（`player_page.dart:2267-2271`）。
- 行高 ≈ `14 + 20.8 + 14 = 48.8px`（由文本行高决定，chevron 18px 更矮）。

**CSS 要点**：`.action-row{display:flex;align-items:center;gap:10px;padding:14px 24px;transition:background-color 0s} .action-row:hover{background:rgb(227 218 204 / .5);transition-duration:.12s} .action-row__chev{margin-left:auto;width:18px;height:18px;color:var(--cloud-medium)}`。

---

## 6. 通用组件（`lib/theme/paper_widgets.dart`）

### 6.1 `ClayButton`（唯一彩色 CTA）
- 最小尺寸 `Size(0, 48)` → `min-height: 48px`（`paper_widgets.dart:55`）。
- 内边距：常规 `31px / 12px`，`compact` 版 `16px / 8px`（`paper_widgets.dart:15-22`）。
- 圆角：`BorderRadius.circular(10)` → 四角 `10px`（`paper_widgets.dart:72-74`）。
  - ⚠️ 与设计意图不符：文件头注释与 `AppRadius.filledButton`（`0 0 8px 8px`）都说 "bottom-only 8px"，但实际代码是 `10px` 全圆角（`paper_widgets.dart:8-11`、`design_tokens.dart:245-263` 对比 `paper_widgets.dart:73`）。**照代码实现 `10px`**。
- 底色 `--clay`；hover 与 pressed 都是 `--clay-deep`；禁用 `--stone`（`paper_widgets.dart:61-68`）。
- 前景：可用 `#FFFFFF`；禁用 `--cloud-dark`（`paper_widgets.dart:69-71`）。
- 文本：`bodySm 16px/1.3`，`w500`，`letter-spacing: 0`，居中（`paper_widgets.dart:77-84`）。
- `overlayColor` 透明——没有 Material 水波纹（`paper_widgets.dart:75`）。
- 文字宽度撑开；`expand: true` 时宽 `100%`（`paper_widgets.dart:50-51`）。

**CSS 要点**：`.btn-clay{min-height:48px;padding:12px 31px;border:0;border-radius:10px;background:var(--clay);color:#fff;font:500 16px/1.3 var(--font-sans);letter-spacing:0;display:inline-flex;align-items:center;justify-content:center} .btn-clay:hover,.btn-clay:active{background:var(--clay-deep)} .btn-clay:disabled{background:var(--stone);color:var(--cloud-dark)}`。

### 6.2 `IvoryButton`（浅面上的主操作）
- 内边距 `31px / 12px`（`paper_widgets.dart:125`，`:15-18`）。
- 底色 `--ivory-light`；hover `--manilla`；禁用 `--ivory-medium`（`paper_widgets.dart:127-132`）。
- 圆角 `AppRadius.filledButton` = 上角 `0`、下角 `8px`（`paper_widgets.dart:133`；`design_tokens.dart:251-255`）。
- 无边框、无阴影；过渡 `120ms`（`paper_widgets.dart:123-124`）。
- 可选前置图标 `16px`，图标后间距 `8px`（`paper_widgets.dart:139-148`）。
- 文本 `bodySm 16px/1.3` `w600`；色 `--slate-dark`，禁用 `--cloud-medium`（`paper_widgets.dart:149-157`）。
- 图标色同文本色规则（`paper_widgets.dart:142-145`）。

**CSS 要点**：`.btn-ivory{padding:12px 31px;border:0;border-radius:0 0 8px 8px;background:var(--ivory-light);color:var(--slate-dark);font:600 16px/1.3 var(--font-sans);display:inline-flex;align-items:center;gap:8px;justify-content:center;transition:background-color .12s linear} .btn-ivory:hover{background:var(--manilla)}`。

### 6.3 `OutlinedButton2`（次级 ghost 按钮）
- 内边距 `16px / 8px`（`compactPadding`，`paper_widgets.dart:205`、`:19-22`）。
- 边框 `1px`：可用 `--cloud-dark`，禁用 `--stone`（`paper_widgets.dart:212-215`）。
- 圆角 `12px`（`paper_widgets.dart:216`；`design_tokens.dart:260-262`）。
- 底色：常态透明；hover 时浅色面 `--oat-warm` `alpha 0.45`，`invert`（深色面）用 `--slate-medium`（`paper_widgets.dart:206-211`）。
- 可选前置图标 `14px`，图标后间距 `6px`（`paper_widgets.dart:221-224`）。
- 文本：`caption` 覆盖为 `13px / 1.4（18.2px）`，`w500`，`-0.24px`（`paper_widgets.dart:225-232`）。
- 前景：`invert` → `--on-dark`；否则可用 `--slate-dark` / 禁用 `--cloud-medium`（`paper_widgets.dart:193-195`）。
- 过渡 `120ms`（`paper_widgets.dart:204`）。

**CSS 要点**：`.btn-outlined{padding:8px 16px;border:1px solid var(--cloud-dark);border-radius:12px;background:transparent;color:var(--slate-dark);font:500 13px/1.4 var(--font-sans);letter-spacing:-0.24px;display:inline-flex;align-items:center;gap:6px;transition:background-color .12s linear} .btn-outlined:hover{background:rgb(227 218 204 / .45)}`；深色变体 `.btn-outlined--invert{color:var(--on-dark);border-color:var(--cloud-dark)}` + hover `background:var(--slate-medium)`。

### 6.4 `TextLinkButton`
- 无容器、无背景、无边框（`paper_widgets.dart:241-246`）。
- 内边距仅垂直 `2px`（`paper_widgets.dart:280-281`）。
- 文本 `bodySm 16px/1.3`，无 `w` 覆盖（即 `w400`）（`paper_widgets.dart:282-292`）。
- 下划线：hover 出现，或 `underlined` 常显；`decorationColor = 前景色`，`decorationThickness: 1`（`paper_widgets.dart:272`、`:286-291`）。
- 颜色：`--slate-dark`；禁用 `--cloud-medium`；`invert` → `--on-dark`（`paper_widgets.dart:269-271`）。
- 行内元素语义，不是按钮块。

**CSS 要点**：`.link{display:inline;padding:2px 0;color:var(--slate-dark);font:400 16px/1.3 var(--font-sans);text-decoration:none;text-decoration-thickness:1px;text-underline-offset:2px;cursor:pointer} .link:hover{text-decoration:underline}`。

### 6.5 `PaperCard`
- 内边距默认 `24px` 四边（`AppSpacing.lg`）（`paper_widgets.dart:309`）。
- 圆角默认 `AppRadius.card = 0`（`paper_widgets.dart:313`、`:321`、`:325`）。
  - ⚠️ 类注释写「24px radius」（`paper_widgets.dart:303`），但默认参数是 `AppRadius.card`（= `0`），全仓调用点也没有传 `radius`（`player_page.dart:1261/1293/1956/2017/2089/2100`、`login_page.dart:114/587`）。**照 `0` 实现**。
- 底色默认 `--ivory-light`，可外部覆盖（`paper_widgets.dart:331`）。
- 边框：`bordered`（默认 `true`）时 `1px --stone`（`paper_widgets.dart:333-335`）。
- `clipBehavior: Clip.antiAlias`（`paper_widgets.dart:327`）；无阴影、无 elevation。
- 可点卡片：cursor `click`（`paper_widgets.dart:339-347`），但 hover **不改任何视觉**（动画 `140ms` 只服务尺寸/内容变化）。

**CSS 要点**：`.card{background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;padding:24px;overflow:hidden;box-shadow:none}`。

### 6.6 `SectionHeading`
- 结构：`InlineLabel(label, strong: true, color: --slate-dark)` + `16px` 间距 + 弹性 `Hairline` + （可选）`16px` + trailing（`paper_widgets.dart:400-413`）。
- 行高由最大子元素决定（文本 `16.8px`，trailing 可能是按钮）。
- 无下边距、无字体号额外设定。

**CSS 要点**：`.section-heading{display:flex;align-items:center;gap:16px} .section-heading__rule{flex:1 1 auto;height:1px;background:var(--stone)}`。

### 6.7 `InlineLabel`
- 强制大写（`text.toUpperCase()`）（`paper_widgets.dart:381-382`）。
- `caption` 底：`12px/1.4（16.8px）`、`letter-spacing` 覆盖为 `1.6px`（`paper_widgets.dart:386`）。
- 颜色默认 `--cloud-dark`；`strong` 时 `w600`，否则 `w500`（`paper_widgets.dart:384-387`）。
- 无 padding、无背景、无边框——纯文字。

**CSS 要点**：`.inline-label{font:500 12px/1.4 var(--font-sans);letter-spacing:1.6px;text-transform:uppercase;color:var(--cloud-dark)}`。

### 6.8 `Hairline`
- 水平：`height: 1px`、宽度默认撑满（可传 `length`）；垂直：`width: 1px`、高度撑满（`paper_widgets.dart:353-368`）。
- 颜色默认 `--stone`，可覆写（如深色面用 `--slate-medium`）（`paper_widgets.dart:362`）。
- 这是全站唯一分隔件：不用阴影、不用渐变。

**CSS 要点**：`.hairline{height:1px;background:var(--stone);border:0} .hairline--v{width:1px;height:auto;align-self:stretch}`。

---

## 7. 交互反馈与主题默认（影响 chrome 观感）

### 7.1 点击反馈
- 所有可点组件通过 `feedbackAction(context, action)` 包装：先触发 `state.feedback()`（触感/声音，视觉无关），再执行回调（`lib/widgets/interaction_feedback.dart:22-28`）。

**CSS 要点**：CSS 侧无需复刻；若要触感反馈，加 `navigator.vibrate`（移动端）即可。

### 7.2 水波纹与高亮
- `splashFactory = InkRipple`；`splashColor = --slate-dark` `alpha 0.09`；`highlightColor = transparent`（`app_theme.dart:34-35`、`:45`）。
- 也就是说：按下只有一层极淡的深色涟漪，没有长按高亮块。

**CSS 要点**：`::selection`/active 态别用亮色；如需复刻，用 `.ripple{background:rgb(20 20 19 / .09)}` 的伪元素径向扩散（150~250ms）。

### 7.3 Tooltip
- 背景 `--slate-dark`；文字 `--on-ink`（深色面 = `--on-dark`）；字号 `12px`，字体 `MiSans`（`app_theme.dart:46-53`）。
- 图标按钮和非图标按钮的 hover 提示都走这一套（`player_page.dart:2800` 等调用 `AccessibleTooltip`）。

**CSS 要点**：`.tooltip{background:var(--slate-dark);color:var(--on-dark);font:400 12px/1.4 var(--font-sans);padding:4px 8px;border-radius:0}`（radius 取全局平角约定，`app_theme.dart` 未单独设圆角）。

### 7.4 滚动条
- thumb `--cloud-medium`，粗细 `8px`，圆角 `0`（`app_theme.dart:101-105`）。

**CSS 要点**：`::-webkit-scrollbar{width:8px} ::-webkit-scrollbar-thumb{background:var(--cloud-medium);border-radius:0}`。

### 7.5 弹层与卡片默认
- dialog / bottomSheet：圆角 `0`、elevation `0`、无 tint、无阴影（`app_theme.dart:68-80`）。
- Card：底色 `--ivory-light`、圆角 `0`、margin `0`（`app_theme.dart:81-88`）。
- AppBar：底色 `--ivory-medium`、前景 `--slate-dark`、elevation `0`（`app_theme.dart:89-95`）。

**CSS 要点**：`dialog, .sheet, .appbar{box-shadow:none;border-radius:0}`。

---

## 8. 图标清单（本范围内出现的 `Icons.xxx`）

| 图标 | 尺寸 | 用途 | 出处 |
|---|---|---|---|
| `home_outlined` | `18px`（侧栏）/ `20px`（底栏） | 导航「主页」 | `player_page.dart:87` |
| `search_outlined` | `18px` / `20px` | 导航「搜索」 | `player_page.dart:88` |
| `favorite_border_rounded` | `18px` | 导航「我喜欢」 | `player_page.dart:89` |
| `person_outline` | `18px` | 导航「我」 | `player_page.dart:91` |
| `settings_outlined` | `18px` / `22px` | 侧栏底部「设置」；compact 顶部设置键 | `player_page.dart:511`、`:215` |
| `person_outline_rounded` | `22px` | 无头像时的占位 glyph（`--oat-warm` 底） | `player_page.dart:330-333` |
| `refresh_rounded` | `17px` | 「我的歌单」标题行刷新 | `player_page.dart:416` |
| `shuffle_rounded` / `shuffle_on_rounded` | `20px` | 随机播放（激活换 `_on`） | `player_page.dart:2756-2757` |
| `skip_previous_rounded` | `26px`（桌面）/ `22px`（compact） | 上一首 | `player_page.dart:2764`、`:2547` |
| `pause_rounded` / `play_arrow_rounded` | `26px`（桌面主按钮）/ `24px`（compact） | 播放/暂停切换 | `player_page.dart:3051`、`:2926` |
| `skip_next_rounded` | `26px`（桌面）/ `22px`（compact） | 下一首 | `player_page.dart:2777`、`:2560` |
| `repeat_rounded` / `repeat_one_on_rounded` | `20px` | 循环（单曲换 `_one_on`） | `player_page.dart:2785-2786` |
| `expand_less_rounded` | `20px` | 播放栏左段「展开正在播放」 | `player_page.dart:2735` |
| `queue_music_rounded` | `20px` | 播放队列入口 | `player_page.dart:2815` |
| `volume_up_rounded` / `volume_down_rounded` / `volume_off_rounded` | `22px` | 音量按档位切换图标 | `lib/widgets/volume_control.dart:48-52` |
| `play_arrow_rounded` | `18px` | 曲目行 hover 时替换序号 | `player_page.dart:2373` |
| `chevron_right_rounded` | `18px` | 设置项行尾 chevron | `player_page.dart:2268` |

- 全部为 Material **Rounded** 风格；HTML 侧建议用 Material Symbols Rounded 字体的对应 codepoint，或直接内联 SVG。
- 标题栏无 Material 图标：三个窗口键 counters 全部是 `CustomPaint` 手绘 1px 线（`window_frame.dart:270-321`）。

**CSS 要点**：图标统一 `[class^="i-"]{width:var(--sz,20px);height:var(--sz,20px);fill:currentColor}`，尺寸只由变量控制，不要在每个组件里重复写死。

---

## 9. 一次性可抄的 `:root` 汇总

```css
:root{
  /* color */
  --slate-dark:#141413; --ivory-medium:#F0EEE6; --ivory-light:#FAF9F5;
  --cloud-medium:#B0AEA5; --cloud-dark:#87867F; --stone:#CCCBC8;
  --slate-medium:#3D3D3A; --oat-warm:#E3DACC; --manilla:#F5E3C7;
  --clay:#D97757; --clay-deep:#C6613F; --on-dark:#FAF9F5;
  --on-dark-muted:#B0AEA5; --player-surface:#141413; --on-player:#FAF9F5;
  /* type */
  --font-sans:'MiSans','Segoe UI','Microsoft YaHei UI','Microsoft YaHei',sans-serif;
  --fs-caption:12px; --lh-caption:1.4; --ls-caption:-0.24px;
  --fs-body-sm:16px; --lh-body-sm:1.3; --ls-body-sm:-0.08px;
  --fs-mono-sm:12px; --lh-mono-sm:1.4;
  /* space */
  --s-xs:4px; --s-sm:8px; --s-md:16px; --s-lg:24px; --s-xl:32px;
  --s-xxl:48px; --s-section:80px; --page-max:1280px;
  /* geometry */
  --radius-card:0; --radius-outlined:12px; --radius-filled-bottom:8px;
  --titlebar-h:40px; --wbtn-w:46px; --glyph-box:18px;
  --sidebar-w:232px; --nav-item-h:44px; --playlist-thumb:32px;
  --playerbar-h:103px; --player-cover:48px; --pp-size:44px; --tbtn-size:36px;
  --bottomnav-h:56px; --track-cover:40px;
}
```

---

## 10. 三处「照着注释写会错」的地方（先看这里再动手）

1. **`ClayButton` 圆角**：注释说「bottom-only 8px」，代码是 `BorderRadius.circular(10)`（全角 `10px`）。以代码为准：`border-radius:10px`（`paper_widgets.dart:73` vs `:8-11`）。
2. **`PaperCard` 圆角**：注释说「24px radius」，默认参数是 `AppRadius.card = 0`，全仓无调用点覆盖。以代码为准：`border-radius:0`（`paper_widgets.dart:303`、`:313`）。
3. **播放主按钮不是 clay 圆钮**：`_PlayPauseButton` 是 `44px × 44px`、圆角 `0`、`--ivory-light` 底 + `--slate-dark` glyph，hover 变 `--manilla`；clay 只出现在进度 thumb、compact 的 `_LightPlayButton`（40px、方角）与 `ClayButton`（`player_page.dart:3038-3056`、`:2915-2932`）。
