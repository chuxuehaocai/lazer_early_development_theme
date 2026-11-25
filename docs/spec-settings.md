# 设置页 / 我的 / 登录弹窗 — 像素级 HTML/CSS 规格

> 提取自 Flutter 参考实现 `E:\Lazer-3fdf89b40956d1f90f9bff242b67a8a9129d140e`（只读，**未修改任何源文件**）。
> 口径：Flutter 逻辑像素 1:1 映射 CSS px，所有数值带单位 px，出处写作 `文件:行号`。
> 与 `docs/spec-shell.md` 的关系：外壳（标题栏/侧栏/播放栏）、通用按钮与卡片的完整规格在那边；本文沿用**同一套 `--token` 命名**，共用件只写差异并标注「参见 spec-shell §6.x」，但凡是本页手写 HTML 必须用到的几何值都在这里再列一遍，保证本文可单独作业。
> 覆盖：`_SettingsView`、`_MeView`、`_ActionRow`、`_SearchField`、`login_page.dart` 全量、`SquareSwitchListTile`、`ScrollInertiaSetting`、`ScrollAccelerationSetting`、`LyricTypographySetting`、`AccessibleSlider`、`PaperCard / SectionHeading / InlineLabel / Hairline`、`PullDownPageRoute` 视觉参数。

---

## 0. 底座（写 CSS 前先落地）

### 0.1 颜色

| CSS 变量 | 亮色值 | 深色值（`app_palette.dart:11-26`） | 本范围里用在哪 | 出处 |
|---|---|---|---|---|
| `--slate-dark` | `#141413` | `#F0EEE6` | 主文字、图标、选中下划线、focus 描边 | `lib/theme/design_tokens.dart:19` |
| `--ivory-medium` | `#F0EEE6` | `#191918` | 页面画布（设置/我的页底） | `design_tokens.dart:22` |
| `--ivory-light` | `#FAF9F5` | `#242423` | 卡片面、输入框填充、弹窗面 | `design_tokens.dart:25` |
| `--cloud-medium` | `#B0AEA5` | `#A8A69E` | 副标题、未激活 tab、chevron、hint | `design_tokens.dart:28` |
| `--cloud-dark` | `#87867F` | `#B5B2A9` | InlineLabel 默认色、输入框图标、开关关态描边 | `design_tokens.dart:31` |
| `--stone` | `#CCCBC8` | `#454540` | 1px hairline、输入框默认描边、弹窗描边 | `design_tokens.dart:34` |
| `--slate-medium` | `#3D3D3A` | `#454540` | 深色面上的描边（本范围仅深色 invert 用） | `design_tokens.dart:37` |
| `--oat-warm` | `#E3DACC` | `#34312D` | 行 hover 底、VIP 徽章底、滑块未完成轨道 | `design_tokens.dart:40` |
| `--manilla` | `#F5E3C7` | `#3E3329` | 头像/首字母方块底 | `design_tokens.dart:43` |
| `--clay` | `#D97757` | `#E68E70` | 唯一彩色：ClayButton、开关开态、滑块 thumb、chip 选中底 | `design_tokens.dart:49` |
| `--clay-deep` | `#C6613F` | `#F0A084` | CTA hover/pressed、错误文字、VIP 文字 | `design_tokens.dart:52` |
| `--on-dark` | `#FAF9F5` | `#FAF9F5` | 开关开态圆点、ClayButton 文字 | `design_tokens.dart:55` |

**CSS 要点**：`:root` 直接照抄 §6 的汇总块。**禁止出现 `#ffffff` 作为任何表面色**——全部表面都在 ivory 系里（`design_tokens.dart:14-15` 注释）。

### 0.2 字号角色（含行高换算）

| 角色 | 规格 | 行盒高 | 出处 |
|---|---|---|---|
| `caption` | `12px / 1.4 / letter-spacing -0.24px / w400` | `16.8px` | `design_tokens.dart:102-109` |
| `captionMuted` | 同上，色 `--cloud-medium` | `16.8px` | `design_tokens.dart:111-118` |
| `bodySm` | `16px / 1.3 / -0.08px / w400` | `20.8px` | `design_tokens.dart:132-139` |
| `bodySmMuted` | 同上，色 `--cloud-medium` | `20.8px` | `design_tokens.dart:141-148` |
| `body` | `20px / 1.4`（名义 serif，实际绑定 MiSans） | `28px` | `design_tokens.dart:151-157` |
| `bodyMuted` | `20px / 1.4`，色 `--cloud-dark` | `28px` | `design_tokens.dart:159-165` |
| `subheading` | `24px / 1.3 / -0.05px / w600` | `31.2px` | `design_tokens.dart:168-176` |
| `heading` | `61px / 1.1 / -0.12px / w700` | `67.1px` | `design_tokens.dart:179-187` |
| `mono` | `16px / 1.4`（＝ MiSans，无真等宽） | `22.4px` | `design_tokens.dart:199-205` |
| `monoSm` | `12px / 1.4`，色 `--cloud-dark` | `16.8px` | `design_tokens.dart:207-213` |
| `wordmark` | `12px / 1.0 / w700 / letter-spacing 3.2px` | `12px` | `design_tokens.dart:216-224` |

**CSS 要点**：`--font-sans:'MiSans','Segoe UI','Microsoft YaHei UI','Microsoft YaHei',sans-serif`（`design_tokens.dart:72-78`）。`serif`/`mono` 角色在源码里也被绑成 MiSans（`design_tokens.dart:82-95`），HTML 侧**不要引入 Georgia / Consolas**，否则三处「serif 标题」「mono cookie 串」都会走样。

### 0.3 间距 / 圆角 / 阴影 / 描边

- 间距基数 `4px`：`xs 4 / sm 8 / md 16 / lg 24 / xl 32 / xxl 48 / section 80`（`design_tokens.dart:232-242`）；设置页大量用 `section * 0.5 = 40px`、`section * 0.6 = 48px`（`player_page.dart:1663`、`:1946`）。
- 圆角：`card 0px`、`outlined 12px`、`filledButton = 上 0px / 下 8px`（`design_tokens.dart:245-263`）；**例外**：`ClayButton` 实际是四角 `10px`（`lib/theme/paper_widgets.dart:73`，与注释矛盾，见 §5 第 1 条）。
- 阴影：**全系统 0 阴影**，`AppElevation.none = []`（`design_tokens.dart:265-269`）；弹窗、卡片、按钮全部只有 tone + 1px 描边。
- 描边：`hairline = 1px --stone`、`hairlineDark = 1px --slate-dark`、`outlined = 1px --cloud-dark`（`design_tokens.dart:272-288`）。

### 0.4 页面容器（内容列）

| 项目 | 规格 | 出处 |
|---|---|---|
| 画布底色 | `--ivory-medium` | `player_page.dart:169` |
| 左右内边距 | 视口 `> 900px` → `56px`；`560–900px` → `32px`；`< 560px` → `24px` | `player_page.dart:799-810` |
| 上下内边距 | `32px`（底部 = `32px + bottomInset`） | `player_page.dart:805-811` |
| 内容列最大宽 | **`1020px`** | `player_page.dart:818` |
| 滚动容器 | 纵向滚动，内容列 `crossAxisAlignment.start` | `player_page.dart:813-821` |

**CSS 要点**：`.page{padding:32px 56px;overflow-y:auto;background:var(--ivory-medium)} .page > .col{max-width:1020px;display:flex;flex-direction:column;align-items:flex-start}`，`@media (max-width:900px){.page{padding:32px}} @media (max-width:560px){.page{padding:32px 24px}}`。
**注意**：`AppSpacing.pageMaxWidth = 1280px`（`design_tokens.dart:241`）是设计令牌，但内容区实际用的是 `1020px`（`player_page.dart:818`）。以 `1020px` 为准，两者不要混用。

### 0.5 Material 角色回退表（**颜色最容易写错的地方**）

`buildAppTheme` 只给 `ColorScheme` 赋了 8 个角色（`lib/theme/app_theme.dart:15-25`：`primary/onPrimary/secondary/onSecondary/surface/onSurface/error/onError`），其余角色由 Flutter 以「回退链」补齐。这条链直接决定了本页多处颜色：

| 实际看到 | Material 角色 | 回退后实际色（亮色） | 依据 |
|---|---|---|---|
| 方形开关行的**副标题** | `onSurfaceVariant` → `?? onSurface` | `#141413`（**不是 `--cloud-medium`**） | `color_scheme.dart:1288` |
| 未选中 `ChoiceChip` 描边 | `outlineVariant` → `?? onBackground` → `onSurface` | `#141413`，1px | `color_scheme.dart:1299` |
| 滑块未完成轨道 | `secondaryContainer` → `?? secondary` | `--oat-warm #E3DACC` | `color_scheme.dart:1099` |
| 滑块已完成轨道 / thumb | `primary` | `--clay #D97757` | `slider.dart:2201`、`:2231` |
| 滑块未完成刻度点 | `onSurfaceVariant` @ 38% | `rgb(20 20 19 / .38)` | `slider.dart:2222` |
| select 浮动 label | `onSurfaceVariant` | `#141413` | `input_decorator.dart` M3 默认 |
| `TextButton` 文字（如「恢复默认」） | `primary` | `--clay #D97757` | `app_theme.dart:17` |
| 开关行 hover 覆盖层 | `ThemeData.hoverColor` | `rgb(0 0 0 / .04)` | `theme_data.dart:468` |
| 列表/按钮按压涟漪 | `splashColor` | `rgb(20 20 19 / .09)` | `app_theme.dart:35` |

**CSS 要点**：手写 HTML 时把上表当成硬编码色值用，不要套「muted = 灰」的直觉。**开关行副标题是近黑 `#141413`**。

### 0.6 共用件速查（细节见 `spec-shell.md`）

| 组件 | 本文用到的关键几何 | 详见 |
|---|---|---|
| `PaperCard` | padding 默认 `24px`、圆角 `0`、`1px --stone`、底色 `--ivory-light`、无阴影 | spec-shell §6.5 / `paper_widgets.dart:305-350` |
| `SectionHeading` | InlineLabel + `16px` + 弹性 1px 线 | §1.3 / `paper_widgets.dart:394-414` |
| `InlineLabel` | `12px w500(strong:w600) / ls 1.6px / 大写` | §1.3 / `paper_widgets.dart:372-390` |
| `Hairline` | `1px --stone` | `paper_widgets.dart:353-368` |
| `ClayButton` | `min-height 48px`、padding `31/12`、圆角 `10px`、`--clay` → hover `--clay-deep` | spec-shell §6.1 / `paper_widgets.dart:46-89` |
| `IvoryButton` | 上角 `0` / 下角 `8px`、hover `--manilla` | spec-shell §6.2 / `paper_widgets.dart:111-164` |
| `OutlinedButton2` | 圆角 `12px`、`1px --cloud-dark`、padding `16/8` | spec-shell §6.3 / `paper_widgets.dart:187-239` |
| `TextLinkButton` | 无容器、垂直 padding `2px`、hover 出下划线 | spec-shell §6.4 / `paper_widgets.dart:263-297` |

---

## 1. 设置页 `_SettingsView`（`player_page.dart:1649-1859`）

### 1.1 结构树与间距链（逐像素）

内容列 `crossAxisAlignment.start`（`player_page.dart:1658-1660`），下表「前置间距」＝源码里紧邻的 `SizedBox`：

| # | 元素 | 前置间距 | 自身高度 | 出处 |
|---|---|---|---|---|
| 1 | 内容列上内边距 | — | `32px` | `player_page.dart:805` |
| 2 | `_HeroHeading('设置', '管理登录账户和曲库同步。')` | `0` | `61.6px`（宽屏 56px 行高 1.1） | `:1662` |
| 3 | 间距 | `40px` | — | `:1663` |
| 4 | `SectionHeading('账户')` | `0` | `16.8px` | `:1666` |
| 5 | 间距 | `16px` | — | `:1667` |
| 6 | 账户组卡片（`_stackedRows`，头部用户行 + `_ActionRow`） | `0` | `≈135.8px` | `:1668-1720` |
| 7 | 间距 | `16px` | — | `:1721` |
| 8 | `_ActionRow('刷新曲库')` | `0` | `48.8px` | `:1722-1726` |
| 9 | 间距 | `24px` | — | `:1727` |
| 10 | `SectionHeading('外观')` | `0` | `16.8px` | `:1728` |
| 11 | 间距 | `12px` | — | `:1729` |
| 12 | select（主题） | `0` | `56px`（M3 outlined 默认） | `:1730-1758` |
| 13 | 间距 | `24px` | — | `:1759` |
| 14 | `SectionHeading('语言')` | `0` | `16.8px` | `:1760` |
| 15 | 间距 | `12px` | — | `:1761` |
| 16 | select（界面语言） | `0` | `56px` | `:1762-1790` |
| 17 | 间距 | `24px` | — | `:1791` |
| 18 | `SectionHeading('交互')` | `0` | `16.8px` | `:1792` |
| 19 | 方形开关行「震动反馈」 | **`0`（无间距！）** | `72px` | `:1793-1798` |
| 20 | 文本「震动强度 · N%」（仅 iOS） | `0` | `20.8px` | `:1799-1803` |
| 21 | 滑块（仅 iOS） | `0` | `48px` | `:1804-1813` |
| 22 | 文本「歌词控件自动隐藏 · N.N 秒」 | `0` | `20.8px` | `:1815-1818` |
| 23 | 滑块 | `0` | `48px` | `:1819-1828` |
| 24 | 间距 | `16px` | — | `:1829` |
| 25 | `SectionHeading('歌词与滚动')` | `0` | `16.8px` | `:1830` |
| 26 | 间距 | `16px` | — | `:1831` |
| 27 | `LyricTypographySetting` | `0` | `≈284px` | `:1832` |
| 28 | 方形开关行「歌词模糊」 | `0` | `72px` | `:1833-1838` |
| 29 | `ScrollInertiaSetting` | `0` | `≈120px` | `:1839` |
| 30 | `ScrollAccelerationSetting` | `0` | `≈105px` | `:1840` |
| 31 | 文本「手动浏览后恢复跟随 · N.N 秒」 | `0` | `20.8px` | `:1841-1844` |
| 32 | 滑块 | `0` | `48px` | `:1845-1854` |
| 33 | 底部间距 | — | `32px` | `:1855` |

**CSS 要点**：设置页**只有「账户」一组是卡片**；「外观/语言/交互/歌词与滚动」全部裸排在画布上，靠 `SectionHeading` 的横线分组，**没有卡片底、没有行分隔线、没有逐行 hover 包裹**。
全页估算高度（桌面亮色、不含 iOS 专属滑块）`≈1498px`。

### 1.2 Hero 标题块 `_HeroHeading`（`:848-903`）

- 宽屏（可用宽 `> 720px`）：`Row` 两栏，左 `flex 3`、右 `flex 2`，中间 `32px`；右栏额外 `padding-top: 8px`（`player_page.dart:886-899`）。
- 标题：`heading` 覆盖字号 → 可用宽 `> 720px` 时 `56px`；`< 560px` 时 `32px`；中间 `40px`；`w700 / lh 1.1 / ls -0.12px / --slate-dark`（`:859-868`）。
- 说明文字：`body 20px` → `lh 1.5 / --cloud-dark`（`:869-875`，`:107`）。
- 窄屏（`≤ 720px`）：`Column`，标题与说明之间 `16px`（`:876-885`）。

**CSS 要点**：`.hero{display:flex;gap:32px;align-items:flex-start} .hero__title{flex:3;font:700 56px/1.1 var(--font-sans);letter-spacing:-.12px} .hero__desc{flex:2;padding-top:8px;font:400 20px/1.5 var(--font-sans);color:var(--cloud-dark)}`；`@media (max-width:720px){.hero{display:block}.hero__desc{margin-top:16px;padding-top:0}}`。
变量：`--hero-title:56px; --hero-gap:32px`。

### 1.3 组标题 `SectionHeading` + `InlineLabel`（`paper_widgets.dart:372-414`）

- 结构：`InlineLabel(label, strong: true, color: --slate-dark)` + `16px` + `Expanded(Hairline)` + 可选 `16px` + trailing（`:400-411`）。
- `InlineLabel`：`text.toUpperCase()`（`:381-382`）→ 中文分组名（账户/外观/语言/交互/歌词与滚动）**不变形**，ASCII（如 `Cookie`→`COOKIE`）会变大写。
- 字体：`caption 12px` 覆盖为 `letter-spacing: 1.6px`；`strong` → `w600`，非 strong → `w500`；默认色 `--cloud-dark`，`strong` 用 `--slate-dark`（`:383-387`）。
- 行高：`16.8px`；横线在该行内**垂直居中**（`Row` 默认 `crossAxisAlignment.center`）。
- 横线：`1px --stone`，吃掉剩余宽度（`:406`）。

**CSS 要点**：`.sec-head{display:flex;align-items:center;gap:16px} .sec-head__label{font:600 12px/1.4 var(--font-sans);letter-spacing:1.6px;text-transform:uppercase;color:var(--slate-dark);white-space:nowrap} .sec-head__rule{flex:1 1 auto;height:1px;background:var(--stone)}`。
变量：`--ls-label:1.6px`。

### 1.4 账户组卡片（`_stackedRows` + `PaperCard`，`:1256-1277`、`:1668-1720`）

- 容器：`PaperCard(padding: EdgeInsets.zero, radius: AppRadius.none = 0)`（`:1261-1263`、`:1720`），即 `--ivory-light` 底 + `1px --stone` 边 + **圆角 0** + 内部无缝。
- 第一行（用户行）：`padding: 24px` 四边（`:1670`），`Row`：
  - 首字母方块 **`38px × 38px`**，`--manilla` 底，`BoxShape.rectangle`（**方角，无圆角**），字符居中，字号 `body 20px` 覆盖为 **`18px`**、`height: 1`（`:1673-1687`）。
  - 间距 `16px`（`:1688`）。
  - 姓名：`bodySm 16px w600`、单行 ellipsis（`:1693-1700`）。
  - 第二行：`captionMuted 12px`，内容 `'{登录方式} · {详情}'`，单行 ellipsis（`:1701-1706`）。
  - 行高 = `24 + max(38, 20.8+16.8=37.6) + 24 = 86px`。
- 行间分隔：`1px --stone` 全宽（`indent` 默认 `0`，`:1269-1272`）。
- 第二行：`_ActionRow`（登录/退出登录）。
- 卡片总高 = `86 + 1 + 48.8 = 135.8px`。

**CSS 要点**：`.grp-card{background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;overflow:hidden} .user-row{display:flex;align-items:center;gap:16px;padding:24px} .user-row__avatar{width:38px;height:38px;background:var(--manilla);display:grid;place-items:center;font:400 18px/1 var(--font-sans);color:var(--slate-dark)} .user-row__name{font:600 16px/1.3 var(--font-sans);letter-spacing:-.08px} .user-row__sub{font:400 12px/1.4 var(--font-sans);letter-spacing:-.24px;color:var(--cloud-medium)}`。
变量：`--avatar-sm:38px; --row-divider:1px`。

### 1.5 设置项行 `_ActionRow`（`:2217-2278`）

| 项目 | 规格 | 出处 |
|---|---|---|
| 盒 | `padding: 14px 24px`，无圆角，整行可点（`HitTestBehavior.opaque`） | `:2241-2254` |
| 背景 | 常态 `--oat-warm` @ 0（透明）；hover `--oat-warm` @ 0.5 | `:2248-2250` |
| 过渡 | **进入 `120ms`，离开 `0ms`**（`Duration.zero`） | `:2245-2247` |
| 前图标 | `16px`，`--slate-dark` | `:2257` |
| 图标后间距 | `10px` | `:2258` |
| 标签 | `bodySm 16px w600`（`--slate-dark`） | `:2260-2265` |
| 尾图标 | `chevron_right_rounded 18px`，`--cloud-medium` | `:2267-2271` |
| 行高 | `14 + 20.8 + 14 = 48.8px` | 计算 |

**CSS 要点**：`.action-row{display:flex;align-items:center;gap:10px;padding:14px 24px;background:rgb(227 218 204 / 0);transition:background-color 0s;cursor:pointer} .action-row:hover{background:rgb(227 218 204 / .5);transition-duration:.12s} .action-row__label{font:600 16px/1.3 var(--font-sans);letter-spacing:-.08px;flex:1} .action-row__chev{width:18px;height:18px;color:var(--cloud-medium)}`。
变量：`--row-h:48.8px; --oat-50:rgb(227 218 204 / .5)`。

### 1.6 `select`（`DropdownButtonFormField`，`:1730-1758`、`:1762-1790`）

- 容器：`filled: true`，`fillColor: --ivory-light`，`OutlineInputBorder(borderRadius: 0)`，`enabledBorder = 1px --stone`（`:1734-1743`、`:1766-1775`）。
- 高 `≈56px`（M3 outlined 默认；`contentPadding` 未覆盖，`isDense: false`）；`isExpanded: true` 撑满内容列宽。
- 浮动 label：`主题` / `界面语言`，浮动后 `12px`，色 `#141413`（`onSurfaceVariant` 回退，见 §0.5）。
- 值文本：`titleMedium` → `16px / w500 / ls 0.15px / --slate-dark`。
- 下拉项：`跟随系统 / 浅色 / 深色`（`:1749-1753`）、`跟随系统 / 简体中文 / 繁體中文 / 日本語 / English`（`:1776-1786`，取自 `AppLanguage.name`，见 `lib/l10n/app_language.dart:3-16`）。
- ⚠️ **focus 态描边会消失**：源码只给了 `border`（`borderSide` 未指定 → `none`）与 `enabledBorder`，未给 `focusedBorder`；Flutter 会回退到 `border` → 聚焦时 1px 描边不再绘制。截图/静态 demo 按未聚焦态做（`1px --stone`）。

**CSS 要点**：`.select{position:relative;width:100%;height:56px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;display:flex;align-items:center;padding:0 12px;font:500 16px/1.5 var(--font-sans);letter-spacing:.15px;color:var(--slate-dark)} .select__label{position:absolute;top:-8px;left:12px;padding:0 4px;background:var(--ivory-light);font:400 12px/1.4 var(--font-sans);color:#141413} .select::after{content:'';position:absolute;right:12px;border-left:5px solid transparent;border-right:5px solid transparent;border-top:6px solid var(--slate-dark)}`。
变量：`--select-h:56px`。

### 1.7 方形开关行 `SquareSwitchListTile`（`lib/widgets/square_switch_list_tile.dart:8-81`）

行盒（`ListTile`，未覆盖 `listTileTheme`，走 M3 默认）：

| 项目 | 规格 | 出处 |
|---|---|---|
| 内容内边距 | `EdgeInsets.zero` → **左右 0**，行内容贴到内容列左右边 | `square_switch_list_tile.dart:32` |
| 形状 | `RoundedRectangleBorder()` → 方角 | `:33` |
| 行高 | `72px`（含副标题的两行 ListTile，standard density） | `list_tile.dart:1503-1511` |
| 最小垂直内边距 | `8px` | `list_tile.dart:1831` |
| 标题 | `16px / 1.5（24px）/ ls 0.5px / w400`，色 `#141413` | `list_tile.dart:1844` |
| 副标题 | `14px / 1.43（20px）/ ls 0.25px / w400`，色 `#141413`（`onSurfaceVariant` 回退） | `list_tile.dart:1847` |
| 行 hover | `rgb(0 0 0 / .04)`（几乎不可见） | `theme_data.dart:468` |
| 行点击 | 涟漪 `rgb(20 20 19 / .09)`；整行可切换 | `app_theme.dart:35`、`square_switch_list_tile.dart:37-39` |

开关本体（`AnimatedContainer`，`:41-76`）：

| 项目 | 规格 | 出处 |
|---|---|---|
| 轨道 | **`48px × 28px`**，方角，`padding: 4px`，`1px` 描边 | `:44-58` |
| 开态 | 轨道底 `--clay`，描边 `--clay` | `:52`、`:56` |
| 关态 | 轨道底 `--oat-warm`，描边 `--cloud-medium` | `:53`、`:57` |
| 禁用 | 轨道底 `--stone`，圆点 `--cloud-dark` | `:49-50`、`:70-71` |
| 圆点 | **`18px × 18px` 正方形**（`SizedBox.square` + `ColoredBox`，无圆角） | `:66-73` |
| 圆点色 | 开 `--on-dark #FAF9F5`；关 `--cloud-dark #87867F` | `:69-71` |
| 位移 | `48 − 2×4(padding) − 2×1(border) − 18 = 20px` → `translateX(20px)` | 计算（`:45-47`、`:54-58`、`:67`） |
| 动画 | `180ms / Curves.easeOutCubic`，`disableAnimations` 时 `0ms` | `:23-25`、`:44`、`:62` |

**CSS 要点**：
```css
.tile-row{display:flex;align-items:center;min-height:72px;padding:8px 0;cursor:pointer;border-radius:0}
.tile-row:hover{background:rgb(0 0 0 / .04)}
.tile-row__text{flex:1 1 auto;min-width:0}
.tile-row__title{font:400 16px/1.5 var(--font-sans);letter-spacing:.5px;color:#141413}
.tile-row__sub{font:400 14px/1.43 var(--font-sans);letter-spacing:.25px;color:#141413}
.switch{position:relative;flex:0 0 auto;width:48px;height:28px;padding:4px;border:1px solid var(--cloud-medium);background:var(--oat-warm);box-sizing:border-box}
.switch__knob{width:18px;height:18px;background:var(--cloud-dark);transition:transform .18s cubic-bezier(.215,.61,.355,1),background-color .18s}
.switch[aria-checked=true]{background:var(--clay);border-color:var(--clay)}
.switch[aria-checked=true] .switch__knob{background:var(--on-dark);transform:translateX(20px)}
.switch[aria-disabled=true]{background:var(--stone)}
```
变量：`--switch-w:48px; --switch-h:28px; --switch-pad:4px; --switch-knob:18px; --switch-travel:20px; --tile-h:72px`。
**注意**：`border` 必须用 `box-sizing:border-box` 否则 20px 位移会算错（Flutter 的 `Border` 画在盒内）。

### 1.8 滑块 `AccessibleSlider`（`lib/widgets/accessible_controls.dart:23-74` + M3 year2023 默认）

源码未设 `SliderTheme`，走的默认是 `_SliderDefaultsM3Year2023`（`slider.dart:834-836`，`year2023` 未关闭）：

| 项目 | 规格 | 出处 |
|---|---|---|
| 组件盒高 | `48px`（overlay 半径决定的 `_maxSliderPartHeight`） | `slider.dart:1723-1738` + `:2359` |
| 轨道高 | `4px`，两端半圆（`RoundedRectSliderTrackShape`） | `slider.dart:2195`、`:2266` |
| 已完成段 | `--clay #D97757` | `slider.dart:2201` |
| 未完成段 | `--oat-warm #E3DACC`（`secondaryContainer` 回退） | `slider.dart:2204` |
| Thumb | 圆点直径 `20px`（`enabledThumbRadius = 10px`），`--clay` | `slider.dart:2231`、`slider_parts.dart:675-678` |
| 按压 overlay | 直径 `48px`，`--clay` @ 10%（拖拽）/ 8%（hover） | `slider.dart:2238-2250`、`slider_value_indicator_shape.dart:188` |
| 刻度点 | **会画出来**：半径 `trackHeight/4 = 1px`（直径 `2px`），已完成白 @38%、未完成 `#141413` @38% | `slider_parts.dart:590`、`slider.dart:2219-2222` |
| 拖动值气泡 | 底色 `--clay`、文字 `labelMedium 12px` 白、`DropSliderValueIndicatorShape` | `slider.dart:2253-2260` |
| 位置 | 轨道横跨整宽（两端半圆），thumb 圆心在 `10px … 宽度−10px` 之间移动 | `slider.dart:2266`（`RoundedRectSliderTrackShape`） |

本项目各滑块的取值域（写 demo 时用来算 thumb 位置）：

| 滑块 | min | max | divisions | 出处 |
|---|---|---|---|---|
| 震动强度（仅 iOS） | `0` | `1` | `20` | `player_page.dart:1804-1813` |
| 歌词控件自动隐藏 | `1 秒` | `10 秒` | `18` | `:1819-1828` |
| 歌词字号 | `14` | `40` | `26` | `lyric_typography_setting.dart:25-33` |
| 滚动惯性 | `0.85` | `0.98` | `13` | `scroll_inertia_setting.dart:142-151` |
| 滚动加速度 | `0.5` | `3.0` | `25` | `scroll_acceleration_setting.dart:42-52` |
| 恢复自动跟随 | `1 秒` | `10 秒` | `18` | `player_page.dart:1845-1854` |

**CSS 要点**：用 `input[type=range]` 自绘：
```css
.slider{width:100%;height:48px;-webkit-appearance:none;background:transparent;cursor:pointer}
.slider::-webkit-slider-runnable-track{height:4px;border-radius:2px;background:var(--oat-warm)}
.slider::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;border-radius:50%;background:var(--clay);margin-top:-8px}
```
刻度点若要严格复刻：在轨道上叠 `repeating-linear-gradient` 的 `2px` 圆点（色 `rgb(20 20 19 / .38)`），间距 = 轨道宽 / divisions。
变量：`--slider-h:48px; --slider-track:4px; --slider-thumb:20px`。

### 1.9 数值输入 + 重置（`ScrollInertiaSetting`，`scroll_inertia_setting.dart:67-153`）

- 一行三段（`:70-138`）：`Expanded(标签 16px)` + `100px` 输入框 + `8px` + `TextButton('恢复默认')`。
- 输入框（`:73-129`）：
  - 宽 **`100px`**；`filled: true` + `--ivory-light`；`isDense: true`；`suffixText: '%'`（色 `--cloud-dark`）。
  - `contentPadding: 12px / 13px`（水平/垂直）→ 高度 = `26 + 20.8 + 2×1 = 48.8px`。
  - 描边：默认 `1px --stone`；**focus `1.5px --slate-dark`**（`:108-114`）。
  - 文本右对齐，`bodySm 16px`，`--slate-dark`；`maxLength 3`。
- 说明行：`captionMuted 12px`，与上排间距 `6px`（`:140-141`）。
- 滑块紧随其后，无额外间距（`:142`）。
- 「恢复默认」按钮：`TextButton` 未覆盖样式 → 高 `40px`、文字 `labelLarge 14px / w500 / ls 0.1px`、色 **`--clay`**、方角（`:132-137`）。
- 整块高 ≈ `48.8 + 6 + 16.8 + 48 = 119.6px`。

**CSS 要点**：`.numrow{display:flex;align-items:center;gap:8px} .numrow__label{flex:1;font:400 16px/1.3 var(--font-sans)} .numrow__input{width:100px;height:48.8px;box-sizing:border-box;padding:13px 12px;text-align:right;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;font:400 16px/1.3 var(--font-sans);color:var(--slate-dark)} .numrow__input:focus{outline:0;border:1.5px solid var(--slate-dark)} .numrow__unit{color:var(--cloud-dark);margin-left:2px} .btn-text{height:40px;padding:0 12px;border:0;background:none;color:var(--clay);font:500 14px/1.43 var(--font-sans);cursor:pointer}`。
变量：`--num-w:100px; --num-h:48.8px`。

### 1.10 分段选择 `ChoiceChip`（歌词粗细，`lyric_typography_setting.dart:36-57`）

- `Wrap(spacing: 8px, runSpacing: 8px)`（`:36-38`）。
- 每个 chip：`showCheckmark: false`、**方角**（`RoundedRectangleBorder()`）、`backgroundColor: --ivory-light`、`selectedColor: --clay @ 0.16`（`:48-52`）。
- 视觉高 ≈ `32.8px`（padding 上下各 `8px` + 12px 文本 16.8px）；`Wrap` 内因 `materialTapTargetSize: padded` 占位高 `48px`。
- 内边距：chip `padding: 8px`；`labelPadding` 水平 `8px`（14px 基准字号下）。
- 文本：`caption 12px`，字重按选项 `400/500/600/700`；未选中文字色 `#141413`。
- 未选中描边：`1px #141413`（`outlineVariant` 回退，§0.5）；选中描边透明。
- 选中底（`--clay @ .16` 叠在 `--ivory-light` 上）= **`#F5E4DC`**。
- 选项文案：`常规 / 中等 / 半粗 / 粗体`（对应 `400/500/600/700`，`:13`）。

**CSS 要点**：`.chips{display:flex;flex-wrap:wrap;gap:8px} .chip{height:33px;padding:0 16px;border:1px solid #141413;border-radius:0;background:var(--ivory-light);color:#141413;font:400 12px/1.4 var(--font-sans);letter-spacing:-.24px;cursor:pointer} .chip[aria-pressed=true]{background:#F5E4DC;border-color:transparent}`（左右 16px = chip padding 8 + labelPadding 8）。
变量：`--chip-h:33px; --chip-sel:#F5E4DC`。

### 1.11 预览块（`lyric_typography_setting.dart:59-86`）

- 容器：`width: 100%`，`padding: 16px`，`--ivory-light` 底，`1px --stone` 描边，**圆角 0**，无阴影（`:59-65`）。
- 眉标：`captionMuted 12px`「歌词样式预览」（`:69`）。
- 间距 `12px`。
- 样例文字：`body 20px` 覆盖为当前字号（`14–40px`）、字重随选项、`lh 1.5`，`200ms easeOutCubic` 过渡（`:71-83`）。
- 块后间距 `20px`（`:87`）。

**CSS 要点**：`.preview{width:100%;padding:16px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0} .preview__label{font:400 12px/1.4 var(--font-sans);color:var(--cloud-medium)} .preview__text{margin-top:12px;font:400 var(--lyric-size,28px)/1.5 var(--font-sans);color:var(--slate-dark);transition:font-size .2s ease-out}`。

### 1.12 设置页文案（可直接抄进 demo）

| 文案 | 位置 | 出处 |
|---|---|---|
| `设置` | Hero 标题 | `player_page.dart:1662` |
| `管理登录账户和曲库同步。` | Hero 说明 | `player_page.dart:1662` |
| `账户` / `外观` / `语言` / `交互` / `歌词与滚动` | 5 个分组标题 | `:1666`、`:1728`、`:1760`、`:1792`、`:1830` |
| `手机号 · 已登录`（模板 `'{方式} · {详情}'`） | 账户卡副行 | `:1702` |
| `登录` / `退出登录` | 账户卡第二行 | `:1714` |
| `刷新曲库` | 独立 action 行 | `:1723` |
| `主题` + `跟随系统` / `浅色` / `深色` | select | `:1735`、`:1749-1751` |
| `界面语言` + `跟随系统` / `简体中文` / `繁體中文` / `日本語` / `English` | select | `:1767`、`:1776-1786` |
| `震动反馈` | 开关行标题 | `:1794` |
| `点击可操作的元素和拖动进度条时反馈` | 开关行副标题 | `:1795` |
| `震动强度 · 60%`（模板 `'震动强度 · N%'`） | 滑块标签 | `:1801` |
| `歌词控件自动隐藏 · 4.0 秒`（模板 `'… · N.N 秒'`） | 滑块标签 | `:1816` |
| `歌词字号 · 28` | 标签 | `lyric_typography_setting.dart:22` |
| `歌词粗细` | 标签 | `lyric_typography_setting.dart:34` |
| `常规` / `中等` / `半粗` / `粗体` | 4 个 chip | `lyric_typography_setting.dart:13` |
| `歌词样式预览` | 预览眉标 | `lyric_typography_setting.dart:69` |
| `让音乐陪你慢慢走` | 预览样例 | `lyric_typography_setting.dart:82` |
| `歌词模糊` | 开关行标题 | `:1834` |
| `距离当前歌词越远，模糊越强；手动浏览时渐隐` | 开关行副标题 | `:1835` |
| `滚动惯性` | 输入行标签 | `scroll_inertia_setting.dart:72` |
| `恢复默认` | 重置按钮 | `scroll_inertia_setting.dart:136`、`scroll_acceleration_setting.dart:37` |
| `85–98%；数值越高，松手后滑行越久、越远。` | 说明 | `scroll_inertia_setting.dart:141` |
| `滚动加速度 · 100%` | 标签 | `scroll_acceleration_setting.dart:25` |
| `50–300%；数值越高，滚轮和连续甩动提速越明显。` | 说明 | `scroll_acceleration_setting.dart:41` |
| `手动浏览后恢复跟随 · 3.0 秒` | 滑块标签 | `:1842` |

---

## 2. 我的页 `_MeView`（`player_page.dart:1869-2213`）

### 2.1 访客态（`:2011-2047`）

| # | 元素 | 规格 | 出处 |
|---|---|---|---|
| 1 | `_HeroHeading('我的音乐', '登录后，自己的歌单都会出现在这里。')` | 同 §1.2 | `:2015` |
| 2 | 间距 | `40px` | `:2016` |
| 3 | `PaperCard` | padding **`48px`** 四边、圆角 `0`、`1px --stone`、`--ivory-light` | `:2017-2018` |
| 4 | `InlineLabel('账户')` | `12px w500 ls 1.6 --cloud-dark`（中文不变形） | `:2022` |
| 5 | 间距 / 标题 | `8px` → `还没有登录`：`subheading 24px` 覆盖 **`22px`**、`w600`、`lh 1.3` | `:2023-2027` |
| 6 | 间距 / 说明 | `6px` → `支持二维码、短信、密码或 Cookie 登录。`：`body 20px`、`lh 1.5`、`--cloud-dark` | `:2028-2035` |
| 7 | 间距 / 按钮 | `24px` → `ClayButton('登录网易云账户')`，**非 expand**（宽度由文字+`62px` padding 决定），高 `48px`、圆角 `10px`、`--clay` 底、白字 `16px w500` | `:2036-2040` |
| 8 | 底部间距 | `32px` | `:2044` |

**CSS 要点**：`.guest-card{padding:48px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0} .guest-card h2{margin:8px 0 6px;font:600 22px/1.3 var(--font-sans);letter-spacing:-.05px} .guest-card p{margin:0 0 24px;font:400 20px/1.5 var(--font-sans);color:var(--cloud-dark)}`。

### 2.2 已登录：资料卡（`:2049-2163`）

- 上间距 `40px`（`:1940`）。
- 卡片：**桌面 `padding: 32px`**（`:2101`）；`PaperCard` 默认样式（`--ivory-light` / `1px --stone` / 圆角 `0`）。
- 布局：`Wrap(spacing: 24px, runSpacing: 16px, crossAxisAlignment: center)`（`:2102-2106`）——不是 grid，窄了就换行。
- 头像：**`64px × 64px`**（`:2053-2055`）：
  - 无头像 URL：`--manilla` 底、**方角**（`BoxShape.rectangle`）、首字符居中、字号 `heading 61px` 覆盖为 **`26px`**、`height: 1`（`:2057-2069`）。
  - 有头像：`PlateArt(radius: 0)` 裁成方图，无边框（`:2070-2074`）。
- 文字列：宽度 `clamp(可用宽 − 360px, 180px, 500px)`（`:2108-2109`）。
  - 昵称：`subheading` 覆盖 **`22px`**、`w600`、`lh 1.3`、单行 ellipsis（`:2115-2124`）。
  - VIP 徽章（可选）：紧跟昵称 `8px`，`--oat-warm` 底、`padding: 8px/2px`、**方角**、文字 `caption 12px w600`、色 `--clay-deep`（`:2125-2144`）。
  - 账号 handle：间距 `4px`，`captionMuted 12px`（`--cloud-medium`），单行 ellipsis（`:2147-2153`）。
- 退出按钮（`TextButton.icon`）：`icon 18px`、`padding: 16px/14px`、`foregroundColor: --slate-dark`、文字 `labelLarge 14px w500`、按钮高 `48px`（`:2079-2087`）。
- 移动端（视口 `< 720px`，`:2078`）：卡片 `padding: 16px`，`Wrap(spaceBetween, spacing 16px, runSpacing 12px)`，只放「头像 + 退出」（`:2088-2098`）。

**CSS 要点**：`.profile{display:flex;flex-wrap:wrap;align-items:center;gap:16px 24px;padding:32px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0} .profile__avatar{width:64px;height:64px;flex:0 0 auto;background:var(--manilla);display:grid;place-items:center;font:400 26px/1 var(--font-sans)} .profile__meta{flex:1 1 180px;max-width:500px;min-width:0} .profile__name{font:600 22px/1.3 var(--font-sans);letter-spacing:-.05px} .profile__handle{margin-top:4px;font:400 12px/1.4 var(--font-sans);color:var(--cloud-medium)} .badge-vip{margin-left:8px;padding:2px 8px;background:var(--oat-warm);color:var(--clay-deep);font:600 12px/1.4 var(--font-sans);border-radius:0}`。
变量：`--avatar-lg:64px; --profile-pad:32px`。

### 2.3 「统计块」的事实说明（重要）

源码里**没有独立的统计块 / 数据面板**。用户的「数量」只以三处计数文字出现，写 demo 时不要凭空造统计卡：

1. 「我喜欢」入口卡的副行：`'{trackCount} 首'`，`captionMuted 12px`（`:1991-1996`）。
2. 歌单架标题内联：`'{分组名} · {count}'`，`SectionHeading` 的 `12px w600 ls 1.6`（`:2197`）。
3. 单张歌单卡底部：`'{trackCount} 首'`，`captionMuted 12px`（`:1134-1137`）。

### 2.4 「我喜欢」入口卡（仅视口 `< 720px` 出现，`:1942-1945`、`:1954-2009`）

- 卡片：`PaperCard(padding: EdgeInsets.zero)` + `InkWell`，圆角 `0`、`1px --stone`（`:1956-1958`）。
- 内层 `padding: 16px`；`Row`：封面 **`48px × 48px`**（`--manilla` 底）+ `favorite_rounded`（默认 `24px`，色 `--clay`）→ `16px` → 文字列 → 尾部 `chevron_right_rounded`（默认 `24px`，`--cloud-dark`）（`:1974-2004`）。
- 文字列：`我喜欢` = `subheading 24px w600`；`4px`；副行 `captionMuted 12px`。
- 卡片与资料卡之间 `16px`（`:1943`）。

**CSS 要点**：`.liked{display:flex;align-items:center;gap:16px;padding:16px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;cursor:pointer} .liked__art{width:48px;height:48px;background:var(--manilla);display:grid;place-items:center;color:var(--clay)} .liked h3{margin:0;font:600 24px/1.3 var(--font-sans)} .liked small{display:block;margin-top:4px;font:400 12px/1.4 var(--font-sans);color:var(--cloud-medium)}`。

### 2.5 歌单架（`:2165-2212` + `_PlaylistGrid` `:1040-1148`）

- 资料卡 → 歌单架：间距 `48px`（`section * 0.6`，`:1946`）。
- 每架结构：`SectionHeading('我创建的歌单 · N')` → `16px` → 网格；两架之间 `48px`（`:2193-2203`）。
- 网格：可用宽 `> 760px` → 2 列，否则 1 列；`mainAxisExtent: 180px`；间距 `16px / 16px`（`:1050-1060`）。
- 单卡（`:1072-1148`）：`--ivory-light` 底 + `1px --stone` + 方角，`Row`：
  - 封面列固定 **`100px`** 宽（`:1090-1097`，`PlateArt` 铺满）。
  - 内容 `padding: 16px`；标题 `bodySm 16px w600`、最多 2 行（`:1104-1111`）；`6px`；描述 `captionMuted 12px` 单行（`:1113-1118`）。
  - 底部行：`TextButton('播放')`（`foregroundColor: --slate-dark`、`labelLarge 14px w500`）+ `'{N} 首'`（`captionMuted 12px`）（`:1120-1139`）。

**CSS 要点**：`.shelf-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px} @media (max-width:760px){.shelf-grid{grid-template-columns:1fr}} .pl-card{display:flex;height:180px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;overflow:hidden} .pl-card__art{flex:0 0 100px;background:var(--manilla)} .pl-card__body{flex:1 1 auto;display:flex;flex-direction:column;padding:16px;min-width:0} .pl-card__name{font:600 16px/1.3 var(--font-sans);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}`。
变量：`--cover-100:100px; --playlist-h:180px`。

### 2.6 空态 / 错误态（`_EmptyHint`，`:1280-1313`；错误分支 `:2166-2181`）

- 卡片：`PaperCard` 默认（`padding: 24px`、`--ivory-light`、`1px --stone`、圆角 `0`），内容居中列。
- 图标 `28px`、`--cloud-dark`；间距 `16px`。
- 标题：`subheading` 覆盖 **`18px`**、居中；间距 `4px`。
- 说明：`captionMuted` 覆盖 `height: 1.5`、居中。
- 错误态额外：说明块下 `16px` + `IvoryButton('重新加载')`（上角 `0` / 下角 `8px`、`padding 31/12`、底 `--ivory-light`、hover `--manilla`、文字 `16px w600`）。

**CSS 要点**：`.empty{padding:24px;text-align:center;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0} .empty__icon{width:28px;height:28px;color:var(--cloud-dark)} .empty__title{margin:16px 0 4px;font:600 18px/1.3 var(--font-sans)} .empty__body{margin:0;font:400 12px/1.5 var(--font-sans);color:var(--cloud-medium)}`。

### 2.7 我的页文案

| 文案 | 位置 | 出处 |
|---|---|---|
| `我的音乐` | 访客 Hero 标题 | `player_page.dart:2015` |
| `登录后，自己的歌单都会出现在这里。` | 访客 Hero 说明 | `:2015` |
| `账户` | 访客卡眉标 | `:2022` |
| `还没有登录` | 访客卡标题 | `:2025` |
| `支持二维码、短信、密码或 Cookie 登录。` | 访客卡说明 | `:2030` |
| `登录网易云账户` | 访客卡 CTA | `:2038` |
| `退出登录` | 资料卡操作 | `:2082` |
| `我喜欢` / `12 首` | 入口卡标题 / 计数 | `:1989`、`:1994`（模板 `'${liked.trackCount} 首'`） |
| `正在同步歌单…` / `暂无歌单` | 入口卡副行占位 | `:1993` |
| `我创建的歌单` / `我收藏的歌单` | 两架分组名（实际渲染带 ` · N`） | `:2206`、`:2207`、`:2197` |
| `还没有歌单。` | 空架占位 | `:2201` |
| `播放` | 歌单卡按钮 | `:1132` |
| `歌单暂时不可用` / `重新加载` | 错误态 | `:2172`、`:2177` |
| `正在加载歌单` / `从你的账户读取我创建和我收藏的歌单。` | 加载态 | `:2188-2189` |
| `歌单加载失败，请检查网络后重试。` | 失败文案 | `:1928` |

---

## 3. 登录弹窗（`lib/screens/login_page.dart`）

### 3.1 遮罩与卡片几何（`login_page.dart:27-49`）

| 项目 | 规格 | 出处 |
|---|---|---|
| 遮罩色 | **`rgba(0,0,0,.54)`**（`Colors.black54`，`showDialog` 默认，源码未覆盖） | `login_page.dart:28-48`；`dialog.dart:1655-1659` |
| 点击遮罩关闭 | `barrierDismissible: true` | `login_page.dart:30` |
| 卡片底色 | `--ivory-light` | `:32` |
| 阴影 / tint | `elevation: 0`、`shadowColor: transparent`、`surfaceTintColor: transparent` → **0 阴影** | `:33-35` |
| 圆角 | `BorderRadius.zero` → **方角 `0`** | `:39-40` |
| 描边 | `1px --stone`（`context.borders.hairline`） | `:41` |
| 外边距 | `insetPadding: 24px` 四边 | `:36` |
| 宽度 | 上限 **`480px`**（`ConstrainedBox(maxWidth: 480)`）；Flutter `Dialog` 另有 `minWidth: 280px` | `:43-45`、`dialog.dart:275` |
| 裁剪 | `Clip.antiAlias` | `:37` |
| 内边距 | 卡片内 `padding: 24px`，内容列 `maxWidth: 440px`；内部 `Column` 是 `stretch`（`:74-75`），会把内容拉满上限 → 宽视口下卡片宽 `480px`、内容栏 **`432px`** | `:70-76` |
| 高度 | 由内容决定，可纵向滚动 | `:70` |
| 入场动画 | `150ms` 纯淡入，`Curves.easeOut`（`showDialog` 路由默认） | `dialog.dart:1853-1879` |

**CSS 要点**：
```css
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.54);display:grid;place-items:center;padding:24px;animation:fade .15s ease-out}
.dialog{width:480px;max-width:calc(100vw - 48px);max-height:calc(100vh - 48px);overflow:auto;padding:24px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;box-shadow:none;box-sizing:border-box}
@keyframes fade{from{opacity:0}to{opacity:1}}
```
变量：`--barrier:rgba(0,0,0,.54); --dialog-w:480px; --dialog-pad:24px`。

### 3.2 页面级弹出动画（`lib/navigation/pull_down_page_route.dart`，只取视觉参数）

- 进入 `420ms`、退出 `340ms`（`:21-23`）。
- 位移：`Offset(0, 1 - progress)` 自上而下整屏滑入/滑出，进入曲线 `Curves.easeOutCubic`、退出 `easeInCubic`（`:157-169`）。
- 该路由 `canTransitionFrom` 恒 `false` → **不叠加页面级遮罩变暗**，靠新页面整屏覆盖（`:19`）。
- 手势回落：下拉超过 `28%` 或速度 `> 700px/s` 即脱离，回落动画时长按剩余比例 `120–340ms`、`easeOutCubic`（`:56-90`）。

**CSS 要点**：`@keyframes slideDown{from{transform:translateY(100%)}to{transform:translateY(0)}} .page--push{animation:slideDown .42s cubic-bezier(.215,.61,.355,1)}`。登录弹窗本身不用这条，它是 §3.1 的淡入。

### 3.3 头部行（`:78-94`）

- `Row(spaceBetween)`：左侧 `LAZER`（`wordmark 12px w700 ls 3.2px lh 1.0`）+ `10px` + `InlineLabel('FIELD PLAYER')`（`12px w500 ls 1.6px`，色 `--cloud-dark`）。
- 右侧：`TextLinkButton('取消')`（`bodySm 16px`、`--slate-dark`、垂直 `padding 2px`、hover 出下划线）。
- **没有 X 图标**，关闭入口就是这行文字（`:91`；`_close()` `:66`）。
- 行后 `24px` 间距（`:94`）。

**CSS 要点**：`.dlg-head{display:flex;align-items:center;justify-content:space-between} .dlg-head__brand{display:flex;align-items:center;gap:10px} .wordmark{font:700 12px/1 var(--font-sans);letter-spacing:3.2px} .dlg-head .link{font:400 16px/1.3 var(--font-sans);color:var(--slate-dark);padding:2px 0;cursor:pointer} .dlg-head .link:hover{text-decoration:underline;text-underline-offset:2px}`。

### 3.4 标题与说明（`:96-112`）

| 项目 | 规格 | 出处 |
|---|---|---|
| 标题 | `登录你的曲库`：`subheading` 覆盖 **`26px`**、`w600`、`lh 1.3`、`ls -0.05px`、居中 | `:97-101` |
| 间距 | `8px` | `:102` |
| 说明 | `登录后同步你的歌单和每日推荐。`：`body 20px` 覆盖 **`15px`**、`lh 1.55`、`--cloud-dark`、居中 | `:103-111` |
| 间距 | `24px` | `:112` |

**CSS 要点**：`.dlg-title{margin:0;text-align:center;font:600 26px/1.3 var(--font-sans);letter-spacing:-.05px;color:var(--slate-dark)} .dlg-sub{margin:8px 0 24px;text-align:center;font:400 15px/1.55 var(--font-sans);color:var(--cloud-dark)}`。

### 3.5 登录方式切换（`_ModeTabs`，`:172-218`）+ 卡片容器（`:114-156`）

- 卡片（包裹 tab 与面板）：`PaperCard(padding: EdgeInsets.fromLTRB(24, 16, 24, 24))` → CSS `padding: 16px 24px 24px`；默认 `--ivory-light` 底 + `1px --stone` + 圆角 `0`（`:114-120`）。
- tab 行：`Row(spaceBetween)`，4 个 tab 均分两端对齐（`:180-182`）。
- 单个 tab：`padding: 6px 4px`；文字 `bodySm 16px`，选中 `w600` + `--slate-dark`，未选中 `w400` + `--cloud-medium`；下方 `4px` 后跟 **`44px × 1px`** 指示条，选中 `--slate-dark`，未选中透明（`:189-210`）。
- tab 文案：`二维码 / 验证码 / 密码 / Cookie`（`:17-22`）。
- 分隔：tab 行 → `16px` → `1px --stone` 横线 → `16px` → 面板（`:128-130`）。
- 面板切换动画：`AnimatedSize 220ms easeOut`，对齐 `topCenter`（`:131-134`）。
- 卡片下：`8px` → 页脚说明 `使用网易云音乐账户登录`（`captionMuted` 覆盖 **`11px`**、居中）（`:157-162`）。

**CSS 要点**：
```css
.dlg-card{padding:16px 24px 24px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0}
.tabs{display:flex;justify-content:space-between}
.tab{padding:6px 4px;display:flex;flex-direction:column;align-items:center;cursor:pointer;border:0;background:none}
.tab__label{font:400 16px/1.3 var(--font-sans);letter-spacing:-.08px;color:var(--cloud-medium)}
.tab[aria-selected=true] .tab__label{font-weight:600;color:var(--slate-dark)}
.tab__rule{width:44px;height:1px;margin-top:4px;background:transparent}
.tab[aria-selected=true] .tab__rule{background:var(--slate-dark)}
.tabs-rule{height:1px;background:var(--stone);margin:16px 0}
.dlg-foot{margin-top:8px;text-align:center;font:400 11px/1.4 var(--font-sans);color:var(--cloud-medium)}
```
变量：`--tab-rule-w:44px; --dlg-card-pad:16px 24px 24px`。

### 3.6 二维码区（`QrPanel`，`:574-713`）

| 项目 | 规格 | 出处 |
|---|---|---|
| 外框 | 居中 `208px × 208px`（`Stack` 中心对齐） | `:580-585` |
| 二维码卡 | `PaperCard(padding: 14px)` → **`206px × 206px`**，`--ivory-light` 底 + `1px --stone` + 圆角 `0` | `:587-589` |
| 二维码图 | **`178px × 178px`**，`eye square`、`data module square`，均 `--slate-dark`；背景 `--ivory-light` | `:591-602` |
| 图下说明 | 间距 `16px`，`打开手机 App 扫描 · 60 秒后过期`：`captionMuted 12px`、居中 | `:675-681` |
| 图下间距 | `24px` | `:682` |
| 加载态 | `CircularProgressIndicator` 默认（`--clay` 前景） | `:604-606` |
| 失败态 | 错误文案 `captionMuted 12px` 居中 + `IvoryButton('重试')` | `:607-611`、`:686-689` |
| 已扫描遮罩 | `Positioned.fill` → **`208px × 208px`**，`--ivory-light` @ **0.92**，圆角 `0`；内容：`phone_android_rounded 30px --slate-dark` → `10px` → `已扫描`（`subheading` 覆盖 **`18px`**）→ `4px` → `请在手机上确认`（`captionMuted 12px`） | `:614-646` |
| 已过期遮罩 | 同尺寸，底色同上；`hourglass_empty_rounded 26px --cloud-dark` → `10px` → `二维码已过期`（`bodySm 16px --cloud-dark`）→ `12px` → `IvoryButton('刷新二维码')` | `:647-668` |
| 扫码成功附加行 | `扫码成功 · 等待手机确认`（`bodySm 16px --cloud-dark`、居中）→ `10px` → `返回二维码`（`TextLinkButton`） | `:690-707` |
| 轮询/倒计时（行为，非视觉） | 每 `2 秒` 轮询；`60 秒` 过期；`802→已扫描`、`800→过期`、`803→关闭弹窗` | `:511-555` |

**CSS 要点**：
```css
.qr{position:relative;width:208px;height:208px;margin:0 auto}
.qr__frame{width:206px;height:206px;margin:1px;padding:14px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;box-sizing:border-box;display:grid;place-items:center}
.qr__img{width:178px;height:178px;background:var(--ivory-light)}
.qr__veil{position:absolute;inset:0;background:rgb(250 249 245 / .92);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px}
.qr__hint{margin-top:16px;text-align:center;font:400 12px/1.4 var(--font-sans);color:var(--cloud-medium)}
```
变量：`--qr-box:208px; --qr-frame:206px; --qr-img:178px; --qr-veil:rgb(250 249 245 / .92)`。

### 3.7 Cookie 输入面板（`CookiePanel`，`:956-1022`）+ 字段通用 chrome（`PaperField`，`:225-345`）

字段（`PaperField`）通用规格：

| 项目 | 单行 | 多行（Cookie） | 出处 |
|---|---|---|---|
| 标签 | `InlineLabel(label)`：`12px w500 ls 1.6px --cloud-dark`，**大写**（`Cookie` → `COOKIE`） | 同 | `:268`、`paper_widgets.dart:381-387` |
| 标签下间距 | `6px` | `6px` | `:269` |
| 盒 | `--ivory-light` 底、圆角 `0`、`1px` 描边 | 同 | `:276-287` |
| 最小高 | `52px` | **`120px`** | `:273-275` |
| 内边距 | 水平 `14px`、垂直 `0`（内容自带 `12px`） | 水平 `14px`、垂直 `8px` | `:288-291`、`:315` |
| 描边色 | 默认 `--stone`；聚焦 `--slate-dark`；错误 `--clay-deep` | 同 | `:280-286` |
| 文本 | `bodySm` 覆盖 `15px` | `mono` 覆盖 `13px / lh 1.5` | `:310-312` |
| hint | `bodySm 15px --cloud-medium` | 同 | `:321-324` |
| 错误行 | `6px` + `caption 12px w500 --clay-deep` | 同 | `:332-341` |

面板内容（`:996-1021`）：
1. `PaperField(label: 'Cookie', hint: 'MUSIC_U=…; __csrf=…', maxLines: 5, mono: true)`。
2. 间距 `8px`。
3. `ClayButton('登录', expand: true)` → 满宽、高 `48px`、圆角 `10px`。
4. 间距 `16px`。
5. 说明：`从浏览器中复制网易云音乐的登录 Cookie，粘贴后会验证账户。`（`captionMuted 12px`、`height: 1.5`，可折 2 行）。

**CSS 要点**：
```css
.field__label{font:500 12px/1.4 var(--font-sans);letter-spacing:1.6px;text-transform:uppercase;color:var(--cloud-dark)}
.field{margin-top:6px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;padding:8px 14px;box-sizing:border-box}
.field--single{min-height:52px;padding:0 14px;display:flex;align-items:center}
.field:focus-within{border-color:var(--slate-dark)}
.field--error{border-color:var(--clay-deep)}
.field textarea{width:100%;min-height:102px;border:0;outline:0;resize:none;background:transparent;font:400 13px/1.5 var(--font-sans);color:var(--slate-dark);padding:4px 0}
.field__err{margin-top:6px;font:500 12px/1.4 var(--font-sans);color:var(--clay-deep)}
```
变量：`--field-min-h:52px; --field-area-h:120px; --field-pad-x:14px`。

### 3.8 短信 / 密码面板（同一 chrome 的差异点）

- 短信（`:802-848`）：`PhoneField`（`:348-390`）→ `16px` → `Row[验证码字段(flex) + 8px + 获取验证码按钮]`（按钮 `padding-top: 22px` 对齐基线）→ `24px` → `BusyRow(ClayButton('登录', expand))`。
- `PhoneField` 前缀：`+86`（`bodySm 15px --cloud-dark`）+ `8px` + 竖线 `1px × 18px --stone`（`:375-387`）；输入格式 `3-4-4`（`:393-411`）。
- 验证码字段 hint：无倒计时 `4 位数字`，倒计时中 `查收短信验证码`（`:821`）。
- 「获取验证码」按钮：`OutlinedButton2`，倒计时显示 `'{N} 秒'` 且 `onPressed: null`（禁用态描边 `--stone`、文字 `--cloud-medium`）（`:834-838`）。
- 密码（`:905-949`）：`PhoneField` → `16px` → 密码字段（`prefix` = `visibility_off_outlined / visibility_outlined` `17px --cloud-dark` 切换）（`:916-936`）→ `8px` → 右对齐 `TextLinkButton('忘记密码？')` → `16px` → `ClayButton('登录', expand)`。
- `BusyRow`（`:445-467`）：忙碌时替换按钮 → 居中 `16px` 圆环（`strokeWidth 2`）+ `12px` + `正在登录…`（`bodySmMuted 16px`）。

**CSS 要点**：`.phone-prefix{display:flex;align-items:center;gap:8px;color:var(--cloud-dark);font:400 15px/1.3 var(--font-sans)} .phone-prefix::after{content:'';width:1px;height:18px;background:var(--stone)} .code-row{display:flex;align-items:flex-start;gap:8px} .code-row .btn-outlined{margin-top:22px}`。

### 3.9 CTA 的位置与尺寸（`ClayButton`，`paper_widgets.dart:46-89`）

| 项目 | 规格 | 出处 |
|---|---|---|
| 高度 | `min-height: 48px`（`minimumSize: Size(0, 48)`） | `paper_widgets.dart:55` |
| 内边距 | `31px / 12px`（compact 版 `16px / 8px`） | `paper_widgets.dart:15-22` |
| 圆角 | **四角 `10px`** | `paper_widgets.dart:73` |
| 底色 | `--clay`；hover 与 pressed 都变 `--clay-deep`；禁用 `--stone` | `paper_widgets.dart:61-68` |
| 文字 | `bodySm 16px w500`、`ls 0`、居中；可用白 `#FFFFFF`，禁用 `--cloud-dark` | `paper_widgets.dart:69-84` |
| 覆盖层 | `overlayColor: transparent`（无 Material 涟漪） | `paper_widgets.dart:75` |
| 宽度 | `expand: true` → `100%`（短信/密码/Cookie 三个面板的「登录」都是 expand） | `paper_widgets.dart:50-51`、`login_page.dart:844`、`:945`、`:1012` |
| 位置 | 面板最后一块：短信面板上方 `24px`；密码面板上方 `16px`；Cookie 面板上方 `8px`、下方 `16px` | `login_page.dart:841-845`、`:942-946`、`:1009-1014` |

**CSS 要点**：`.btn-clay{display:flex;align-items:center;justify-content:center;width:100%;min-height:48px;padding:12px 31px;border:0;border-radius:10px;background:var(--clay);color:#fff;font:500 16px/1.3 var(--font-sans);letter-spacing:0;box-shadow:none}`（未点出 `box-shadow:none` 是本项目最容易「多画一层阴影」的地方）。

### 3.10 登录弹窗文案

| 文案 | 位置 | 出处 |
|---|---|---|
| `LAZER` | 弹窗左上 wordmark | `login_page.dart:83` |
| `FIELD PLAYER` | wordmark 旁 InlineLabel | `:86` |
| `取消` | 右上关闭（文字，无图标） | `:91` |
| `登录你的曲库` | 主标题 | `:98` |
| `登录后同步你的歌单和每日推荐。` | 说明 | `:104` |
| `二维码` / `验证码` / `密码` / `Cookie` | 4 个切换 tab | `:18-21` |
| `使用网易云音乐账户登录` | 卡片下页脚 | `:159` |
| `打开手机 App 扫描 · 60 秒后过期` | 二维码说明 | `:678` |
| `已扫描` / `请在手机上确认` | 扫码遮罩 | `:635`、`:642` |
| `二维码已过期` / `刷新二维码` | 过期遮罩 + 按钮 | `:657`、`:664` |
| `扫码成功 · 等待手机确认` / `返回二维码` | 已扫描附加行 | `:693`、`:702` |
| `重试` | 取码失败 | `:688` |
| `二维码获取失败，请检查网络后重试。` | 取码失败文案 | `:505` |
| `手机号` / `11 位手机号码` / `+86` | 手机号字段 | `:364-365`、`:378` |
| `验证码` / `4 位数字` / `查收短信验证码` | 验证码字段 | `:820-821` |
| `获取验证码` / `N 秒` | 发送按钮 | `:835` |
| `密码` / `至少 6 位` / `忘记密码？` | 密码字段 | `:918-919`、`:940` |
| `Cookie` / `MUSIC_U=…; __csrf=…` | Cookie 字段 | `:1003-1004` |
| `从浏览器中复制网易云音乐的登录 Cookie，粘贴后会验证账户。` | Cookie 说明 | `:1016` |
| `登录` | CTA（三个面板同名） | `:844`、`:945`、`:1012` |
| `正在登录…` | 忙碌行 | `:463` |
| `请输入有效的 11 位手机号` / `验证码为 4 位数字` / `请先获取验证码` / `请粘贴 Cookie 字符串` / `格式不正确 — 应包含键值对，例如 MUSIC_U=…` | 校验错误 | `:747`、`:785`、`:782`、`:979`、`:983` |

---

## 4. 附：搜索框 `_SearchField`（`player_page.dart:1321-1400`）

登录字段同源的输入 chrome，写 demo 时可直接复用：

| 项目 | 规格 | 出处 |
|---|---|---|
| 盒 | `min-height: 52px`，`--ivory-light` 底，圆角 `0` | `:1340-1348` |
| 描边 | 默认 `1px --stone`；聚焦 `1px --slate-dark`；过渡 `160ms` | `:1338-1347` |
| 内边距 | 水平 `16px`，垂直 `0` | `:1349` |
| 放大镜 | `search_outlined 17px --cloud-dark` + `10px` | `:1352-1357` |
| 输入文本 | `bodySm 16px`，内容内边距垂直 `12px` | `:1362-1366` |
| hint | `搜索曲目、专辑或歌单`，`16px --cloud-medium` | `:1368-1372` |
| 清除键 | 有内容时右侧出现：`padding 6px` + `close_rounded 16px --cloud-dark` | `:1376-1394` |

**CSS 要点**：`.search{display:flex;align-items:center;gap:10px;min-height:52px;padding:0 16px;background:var(--ivory-light);border:1px solid var(--stone);border-radius:0;transition:border-color .16s} .search:focus-within{border-color:var(--slate-dark)} .search input{flex:1;border:0;outline:0;background:none;padding:12px 0;font:400 16px/1.3 var(--font-sans)} .search input::placeholder{color:var(--cloud-medium)}`。

---

## 5. 最易做错的细节（写 HTML 前先看这 8 条）

1. **`ClayButton` 圆角是 `10px` 四角**（`paper_widgets.dart:73`），而设计令牌写的是「上 0 / 下 8px」（`design_tokens.dart:251-255`）。带「上 0 下 8」的是 `IvoryButton`（`paper_widgets.dart:133`）。登录弹窗里的「登录」是 ClayButton → `10px`，「刷新二维码 / 重试 / 重新加载」是 IvoryButton → `0 0 8px 8px`。
2. **设置页的开关行不在卡片里**：`SquareSwitchListTile` 是 `Column` 的直接子节点，`contentPadding: EdgeInsets.zero`（`square_switch_list_tile.dart:32`、`player_page.dart:1793/1833`）→ 开关贴齐内容列右边缘，行间**没有分隔线**，也没有设置页常见的行底。只有「账户」组有一张 `radius: 0` 的卡片（`player_page.dart:1668-1720`）。
3. **方形开关的圆点位移是 `20px`，不是 `22px`**：`48 − 2×4(padding) − 2×1(border) − 18 = 20px`（`square_switch_list_tile.dart:44-58`、`:66-73`）。Flutter 的 `Border` 画在盒内，CSS 必须 `box-sizing: border-box` 才能对上；轨道与圆点都是**方角**，没有任何 `border-radius`。
4. **开关行副标题不是灰色**：`ListTile` 用 `onSurfaceVariant`，本主题没定义该角色 → 回退到 `onSurface = #141413`（`app_theme.dart:15-25`、`list_tile.dart:1847`、`color_scheme.dart:1288`）。写成 `--cloud-medium` 会明显偏灰。
5. **登录弹窗 0 阴影 + 方角 + `1px --stone`，遮罩是 `rgba(0,0,0,.54)`**（`login_page.dart:32-42`、`dialog.dart:1655-1659`）。任何 `box-shadow`、圆角、`backdrop-filter` 都是加戏；卡片「浮起」只靠 `--ivory-light` 与画布 `--ivory-medium` 的色差。
6. **弹窗没有 X 关闭图标**：关闭入口是右上角文字「取消」（`login_page.dart:91`），另外点遮罩也能关（`:30`）。
7. **滑块会画出刻度点**：所有设置滑块都带 `divisions`（如 `18`），默认 `RoundSliderTickMarkShape` 半径 = `trackHeight/4 = 1px` → `2px` 点（`slider_parts.dart:590`、`slider.dart:2219-2222`）；同时未完成轨道色是 `--oat-warm`，不是灰（`secondaryContainer` 回退，`slider.dart:2204`、`color_scheme.dart:1099`）。
8. **未选中 `ChoiceChip` 的描边是近黑 `#141413`**（`outlineVariant → onBackground → onSurface`，`color_scheme.dart:1299`、`choice_chip.dart:353-356`），不是 `--stone`；选中态才变成 `--clay @ .16` 底 + 无描边。

---

## 6. 追加 `:root`（可与 `spec-shell.md` §9 合并）

```css
:root{
  /* 组件几何（本文新增） */
  --row-h:48.8px;
  --tile-h:72px;
  --switch-w:48px; --switch-h:28px; --switch-pad:4px;
  --switch-knob:18px; --switch-travel:20px;
  --field-min-h:52px; --field-area-h:120px; --field-pad-x:14px;
  --select-h:56px; --num-w:100px; --num-h:48.8px;
  --slider-h:48px; --slider-track:4px; --slider-thumb:20px;
  --chip-h:33px; --chip-sel:#F5E4DC;
  --avatar-sm:38px; --avatar-lg:64px;
  --cover-100:100px; --playlist-h:180px;
  --dialog-w:480px; --dialog-pad:24px;
  --barrier:rgba(0,0,0,.54);
  --qr-box:208px; --qr-frame:206px; --qr-img:178px;
  --qr-veil:rgb(250 249 245 / .92);
  --tab-rule-w:44px;
  --ls-label:1.6px;
  --oat-50:rgb(227 218 204 / .5);
  /* 过渡 */
  --dur-hover:120ms; --dur-field:160ms; --dur-switch:180ms;
  --dur-size:220ms; --dur-dialog:150ms;
}
```

---

## 7. 源码中「不存在」的元素（别照设计稿脑补）

| 常见误加 | 事实 | 依据 |
|---|---|---|
| 我的页统计卡（听歌数/时长/关注） | **不存在**，只有 3 处计数文字 | §2.3 |
| 设置页每组的卡片底 | 只有「账户」组是卡片，其余裸排 | `player_page.dart:1792-1854` |
| 开关行的分隔线 | `ListTile` 无 divider，`_stackedRows` 只用于卡片 | `square_switch_list_tile.dart:31-77` |
| 弹窗的 X 关闭图标 | 只有文字「取消」 | `login_page.dart:91` |
| 弹窗阴影/圆角/模糊背景 | 0 阴影、圆角 `0`、无 blur | `login_page.dart:33-42` |
| 输入框圆角 | 全部 `0`（连 `OutlinedButton2` 的 `12px` 都不用于输入框） | `login_page.dart:278`、`:1738` |
| 复选框 / radio | 全站开关只有方形 switch，没有 checkbox | `square_switch_list_tile.dart:41-76` |
| 滑块渐变色 / 双色轨道 | 单色 `--clay` + `--oat-warm`，无渐变 | `slider.dart:2201-2204` |

---

## 8. Material 图标清单（末尾清单，本范围内出现的 `Icons.xxx`）

| 图标 | 尺寸 | 颜色 | 用途 | 出处 |
|---|---|---|---|---|
| `settings_outlined` | `22px` | 默认（`--slate-dark`） | compact 顶栏设置入口 | `player_page.dart:215` |
| `search_outlined` | `17px` | `--cloud-dark` | 搜索框放大镜 | `player_page.dart:1353` |
| `close_rounded` | `16px` | `--cloud-dark` | 搜索框清除 | `player_page.dart:1388` |
| `login_rounded` | `16px` | `--slate-dark` | 账户行「登录」 | `player_page.dart:1715` |
| `logout_rounded` | `16px` | `--slate-dark` | 账户行「退出登录」 | `player_page.dart:1715` |
| `logout_rounded` | `18px` | `--slate-dark` | 我的页资料卡「退出登录」 | `player_page.dart:2081` |
| `refresh_rounded` | `16px` | `--slate-dark` | 设置项「刷新曲库」 | `player_page.dart:1724` |
| `chevron_right_rounded` | `18px` | `--cloud-medium` | 设置项行尾 | `player_page.dart:2268` |
| `chevron_right_rounded` | `24px`（默认） | `--cloud-dark` | 「我喜欢」入口卡行尾 | `player_page.dart:2001-2003` |
| `favorite_rounded` | `24px`（默认） | `--clay` | 「我喜欢」入口卡封面 glyph | `player_page.dart:1982` |
| `cloud_off_outlined` | `28px` | `--cloud-dark` | 空态/错误态（我的页、首页） | `player_page.dart:2171`、`:920`、`:1296` |
| `library_music_outlined` | `28px` | `--cloud-dark` | 「正在加载歌单」空态 | `player_page.dart:2187` |
| `phone_android_rounded` | `30px` | `--slate-dark` | 二维码已扫描遮罩 | `login_page.dart:629` |
| `hourglass_empty_rounded` | `26px` | `--cloud-dark` | 二维码过期遮罩 | `login_page.dart:651` |
| `visibility_off_outlined` / `visibility_outlined` | `17px` | `--cloud-dark` | 密码显隐切换 | `login_page.dart:929-930` |
| `music_note_rounded` | `24px`（默认） | `--cloud-dark` | 封面/头像缺图兜底 | `lib/widgets/plate_art.dart:28` |

- 全部为 Material **Rounded / Outlined** 风格；HTML 侧用 Material Symbols Rounded 对应字符或内联 SVG。
- 图标统一受 `IconTheme` 约束（`app_theme.dart` 未覆盖 iconTheme），未显式给色的图标落到 `--slate-dark`。


