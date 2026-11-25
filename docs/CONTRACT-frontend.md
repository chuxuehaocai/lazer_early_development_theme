# 复刻前端实现契约（Lead 定稿，所有前端 agent 必须遵守）

目标：在 `plugin/frontend/` 内用纯 HTML/CSS/JS（无构建、无 npm、无 ES module）1:1 复刻
`E:\Lazer-3fdf89b40956d1f90f9bff242b67a8a9129d140e`（parchment / "Anthropic Style Reference" 阶段）的桌面 UI。
该目录同时作为 Lazer 插件 ZIP 的静态资源，由插件内置 HTTP 服务在 `127.0.0.1:<port>` 提供，
因此**双击 index.html 用 file:// 打开也必须能正常工作**。

## 0. 铁律

1. 只用经典 `<script src>`（不要 `type="module"`，file:// 下会被 CORS 拦）。
2. 不要外链任何字体/图片/图标资源；不允许出现 `.png .jpg .woff2 .ttf` 文件（插件 ZIP 白名单不接受）。
   封面一律用 CSS 渐变 + 噪点纹理占位（`.plate`）。
3. 图标用**内联 sprite**：`js/icons.js` 会把 symbol 注入到文档里，使用时
   `<svg class="icon"><use href="#i-home"></use></svg>`，禁止 `<use href="assets/icons.svg#...">`。
4. 一个 agent 只写自己被分配的 css/js 文件，不要改别人的文件、不要改 index.html（shell agent 独占）。
5. 所有尺寸用 px（不要 rem），颜色/字号/间距/圆角一律走 `css/tokens.css` 里的 CSS 变量。
6. 中文文案直接写死（与参考实现一致），不要 i18n 框架。
7. 允许的容器宽度断点：`>= 1100px` 播放条时间码出现、`720px` 侧栏↔底部导航切换。
   **内容列另有自己的三段 inset（按内容区宽度判，不是窗口宽）**：`>900 → 56px`、`560–900 → 32px`、`<560 → 24px`；
   内容列最大 **1020px 且左对齐（不居中）**。
8. 全站**零阴影、零毛玻璃**；圆角只有三处：ClayButton `10px`、描边按钮 `12px`、IvoryButton 上 0 下 `8px`；
   其余（卡片、封面、播放键、弹窗、队列行）全是直角 0。
9. Hero 标题字号是 **56 / 40 / 32**（断点 720 与 560），不是 68/61——那是 design_tokens 的 display/heading 原始值。
10. 歌词：非聚焦行 `scale(.97)`（origin left center），颜色 `#87867F`，聚焦行 `#141413` 且中心固定视口 35% 高度；
    翻译行同色（不是 58% 透明度）；上下遮罩淡到页面底色。队列行高 **76px**。

## 1. 文件与加载顺序（index.html 由 shell agent 写）

```html
<link rel="stylesheet" href="css/tokens.css">
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/shell.css">
<link rel="stylesheet" href="css/views-home.css">
<link rel="stylesheet" href="css/views-now.css">
<link rel="stylesheet" href="css/views-settings.css">
...
<script src="js/icons.js"></script>
<script src="js/demo-data.js"></script>
<script src="js/core.js"></script>       <!-- LZ 命名空间 / 事件 / 路由 / transport -->
<script src="js/shell.js"></script>      <!-- 标题栏 / 侧栏 / 播放条 / 底部导航 -->
<script src="js/views/home.js"></script>
<script src="js/views/library.js"></script>
<script src="js/views/search.js"></script>
<script src="js/views/detail.js"></script>
<script src="js/views/now.js"></script>
<script src="js/views/queue.js"></script>
<script src="js/views/settings.js"></script>
<script src="js/views/me.js"></script>
<script src="js/views/design.js"></script>
<script src="js/boot.js"></script>       <!-- 最后启动路由 -->
```

## 2. CSS 变量（`css/tokens.css`，shell agent 写，其他人只读）

颜色（来自 `lib/theme/design_tokens.dart`，**不得改动数值**）：

```css
--slate-dark:#141413; --ivory-medium:#F0EEE6; --ivory-light:#FAF9F5;
--cloud-medium:#B0AEA5; --cloud-dark:#87867F; --stone:#CCCBC8;
--slate-medium:#3D3D3A; --oat-warm:#E3DACC; --manilla:#F5E3C7;
--clay:#D97757; --clay-deep:#C6613F; --on-dark:#FAF9F5; --on-dark-muted:#B0AEA5;
--player-surface:#141413;
/* 深色主题覆盖：html[data-theme="dark"] 里重定义，值见 app_palette.dart */
```

字体：

```css
--font-ui:'MiSans','Segoe UI','Microsoft YaHei UI','Microsoft YaHei',system-ui,sans-serif;
--font-serif:var(--font-ui);   /* 参考实现里 serif 角色也绑定到 MiSans */
--font-mono:var(--font-ui);
```

字号/行高（工程值为 `font-size/line-height/letter-spacing`）：

```css
--text-caption:12px; --lh-caption:1.4; --ls-caption:-0.24px;
--text-body-sm:16px; --lh-body-sm:1.3; --ls-body-sm:-0.08px;
--text-body:20px;   --lh-body:1.4;
--text-subheading:24px; --lh-subheading:1.3; --ls-subheading:-0.05px;
--text-heading:61px; --lh-heading:1.1; --ls-heading:-0.12px;
--text-display:68px; --lh-display:1.1;
--text-wordmark:12px; --ls-wordmark:3.2px;
--text-inline-label-ls:1.6px;   /* InlineLabel 大写小标签 */
--text-mono:16px; --text-mono-sm:12px; --lh-mono:1.4;
```

间距 / 圆角 / 其他：

```css
--u-xs:4px; --u-sm:8px; --u-md:16px; --u-lg:24px; --u-xl:32px; --u-xxl:48px;
--section-gap:80px; --page-max:1280px;
--radius-card:0px; --radius-outlined:12px; --radius-filled-bottom:8px; --radius-control:12px;
--hairline:1px;
--sidebar-width:232px; --titlebar-height:40px;
--ease-out-quart:cubic-bezier(0.25,1,0.5,1);
--dur-fast:120ms; --dur-med:140ms; --dur-view:360ms; --dur-marker:240ms;
```

## 3. 基础组件类（`css/base.css`，shell agent 写；其他 view 只复用，不重定义）

| 类名 | 规格出处 | 说明 |
| --- | --- | --- |
| `.hairline` / `.hairline--v` | paper_widgets.dart Hairline | 1px stone 分隔线 |
| `.paper-card` | PaperCard | ivoryLight 底、1px stone 边框、圆角 `--radius-card`、padding 24px、**无阴影** |
| `.clay-button` | ClayButton | clay 底、白字、bodySm w500、min-height 48、padding 31/12、圆角 10px、hover/focus 底 clayDeep |
| `.ivory-button` | IvoryButton | ivoryLight 底、slateDark 字 w600、padding 31/12、圆角 0 0 8px 8px、hover 底 manilla |
| `.outlined-button` | OutlinedButton2 | 透明底、1px cloudDark 边框、圆角 12px、padding 16/8、字 13px w500、hover 底 oatWarm/45% |
| `.text-link` | TextLinkButton | 无容器、bodySm、hover 下划线 1px |
| `.inline-label` | InlineLabel | 12px w500/600、大写、letter-spacing 1.6px、cloudDark（strong 用 slateDark） |
| `.section-heading` | SectionHeading | 行内 label + 16px 间隔 + 弹性 hairline |
| `.icon` | — | 24x24 viewBox、`fill:currentColor`、`width/height` 由上下文定 |
| `.plate` | plate_art.dart | 封面占位：CSS 渐变（用 `--plate-hue` 变量 + `conic/linear gradient`），圆角 0，`object-fit:cover` |
| `.seek` | _SeekSlider | 高 14、轨道 3px、已播 onDark、未播 slateMedium、thumb 直径 12 clay |
| `.icon-button` / `.icon-button--light` / `.icon-button--dark` | _LightIconButton/_DarkIconButton | 见 spec-shell.md；hover 变色，键盘 focus 用 1px slateDark 描边 |

## 4. JS 契约（`js/core.js` 提供，shell agent 写，其他人只调用）

```js
LZ.registerView({ id:'home', title:'首页', mount(root, params){}, enter(params){}, leave(){}, update(state){} });
LZ.navigate('home' | 'search' | 'likes' | 'me' | 'settings' | 'now' | 'queue' | 'design' | 'playlist:<id>' | 'album:<id>');
LZ.on('state', fn);           // 播放状态变化（demo 时钟或 HTTP 轮询都会触发）
LZ.getState();                // {playing, positionMs, durationMs, volume, shuffle, repeat, track, queue, lyrics}
LZ.player.toggle(); LZ.player.next(); LZ.player.prev(); LZ.player.seek(ms); LZ.player.volume(v);
LZ.demo                         // demo-data.js 暴露的数据集（albums/playlists/tracks/lyrics/account）
LZ.config                       // {theme:'light'|'dark', lyricScale, ...} 来自 /api/config，缺省用默认
LZ.icon(name, size)             // 返回 <svg class="icon"> 字符串
```

路由：`#/home`、`#/search`、`#/likes`、`#/me`、`#/settings`、`#/now`、`#/queue`、`#/design`、
`#/playlist/<id>`、`#/album/<id>`。`#/now` 与 `#/queue` 是全屏浮层（`.view--overlay`，铺在播放条之上）。
视图切换动画严格照 `_ViewEntry`：360ms `--ease-out-quart`，`translateY(32px→0)` + `scale(.96→1)` + opacity `0→1`。

## 5. 演示数据（`js/demo-data.js`，shell agent 写）

```js
LZ.demo = {
  account: { name:'林间晚风', handle:'@field-notes', signature:'今夜有风，适合耳机。' },
  hero: { eyebrow:'FIELD NOTES · 第 12 期', title:'把耳朵借给一片安静', body:'每晚 21:00 更新…',
          primary:'开始收听', secondary:'查看本期歌单' },
  tracks: [ {id:'t1', title:'<中文歌名>', artist:'<歌手>', album:'<专辑>', durationMs:243000, hue: 18}, … 12 条 ],
  playlists: [ {id:'p1', name:'深夜书房', description:'…', trackCount:24, hue:38}, … 6 条 ],
  albums: [ {id:'a1', title:'羊皮纸', artist:'…', year:2025, trackCount:9, hue:12}, … 6 条 ],
  lyrics: [ {time:0, text:'…', translation:'…'} … 18 行 ]
};
```

数据必须**全中文、有编辑气质**，与 parchment 设计（田野笔记、安静、夜读）一致；不要出现英文占位词。

## 6. 实时数据（可选增强）

若页面由插件 HTTP 服务提供（`location.protocol === 'http:'`），`js/core.js` 每 700ms 拉 `/api/state`：
`{track:{title,artist,album,coverUrl,durationMs}, positionMs, durationMs, playing, volume, shuffle, repeat,
  queue:[…], lyrics:{lines:[{time,text,translation}]}}`；字段缺失时回退 demo 数据。
`file://` 下不轮询，使用 demo 时钟（1s 推进 positionMs，循环播放）。

## 7. 验收

- `python tools/serve.py --port 8080` + Chrome 1440x900 截图，与 `docs/spec-*.md` 中的数值逐项核对。
- 控制台零报错、零 404（favicon 除外）。
- 1440 / 1024 / 480 三个宽度下布局不溢出、不出现横向滚动条。
- 所有交互（导航、播放控制、进度拖动、队列开关、歌词滚动）都能在无后端时工作。
