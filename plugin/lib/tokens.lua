-- parchment 设计令牌 → 宿主声明式令牌的翻译表。
--
-- 来源：参考快照 lib/theme/design_tokens.dart（颜色/字号/间距/圆角）、
--       lib/theme/paper_widgets.dart（组件几何）、lib/widgets/lyric_viewport.dart（歌词动效）。
--
-- 宿主主题契约只有几何、字重与歌词动效，没有颜色令牌：颜色与表面仍然归宿主所有，
-- 宿主主题契约只有几何、字重与歌词动效，颜色仍归宿主：这份表只表达"几何 1:1"。

local M = {}

local config = require("lib.config")

-- 令牌来源标注（诊断导出会带上这一行）。
local SOURCE = "Lazer @ 3fdf89b4 · parchment（Anthropic Style Reference）"

local ELEMENTS = {
  -- 表面：parchment 的卡片是直角；列表行 64px（TrackRow 实测高度）
  groupedCardRadius = 0,
  cornerScale = 1,
  listTileMinHeight = 64,
  listTileVerticalPadding = 10,
  controlRadius = 12,
  glassBlurSigma = 0,

  -- 窗口胶囊（Inline 标题栏右上角那颗玻璃药丸）与移动端底边栏：parchment 是直角。
  -- 明确给 0，而不是让宿主用 cornerScale × 满圆半径折算 —— 那样会画出满圆。
  capsuleRadius = 0,
  navBarRadius = 0,

  -- 组件几何（宿主新暴露的 API）：侧栏与播放条
  railWidth = 232,             -- 参考实现侧栏固定 232（宿主默认是 216–264 自适应）
  playerBarHeight = 100,       -- 桌面播放条最小高度（参考实现 103 含 1px 顶边）
  compactPlayerBarHeight = 72, -- 紧凑播放条（参考实现 75 含底部进度发丝线）

  -- 正在播放页（宿主新暴露的 API）：参考实现 desktop_now_playing.dart 的版心
  nowPlayingArtworkFraction = 0.34, -- 左栏宽 = clamp(0.34W, 240, 440)
  nowPlayingArtworkMin = 240,
  nowPlayingArtworkMax = 440,
  nowPlayingSidePadding = 32,  -- 主体内边距 32/24/24/24 的左值
  nowPlayingSidePaddingMax = 32,
  nowPlayingTitleSize = 30,    -- 曲名 30px / 行高 1.2
  nowPlayingSubtitleSize = 15, -- 翻译行 15px
  nowPlayingMetaSize = 18,     -- 歌手 18px（专辑 15 由内置档位）
  nowPlayingCoverRadius = 0,   -- 封面直角

  -- 应用背景（宿主新暴露的 API）：该阶段是纯羊皮纸画布，没有专辑色流
  backgroundPlayMode = "off",  -- 不构建 AlbumBlurFlowCanvas
  backgroundOpacity = 1,
  backgroundBlurSigma = 0,     -- 彻底关闭背景模糊
  backgroundVeilAlpha = 1,     -- 遮罩完全盖住（等价于无背景）

  -- 语义颜色（宿主新暴露的 API）：把 design_tokens.dart 的羊皮纸调色板
  -- 映射到宿主的 19 个语义槽。宿主仍然掌管对比度、焦点与所有 Widget，
  -- 这里只换色。别名见 lazer_theme.dart 的 skinColorAliases（canvas/ink/hairline …）。
  colors = {
    background = "#F0EEE6",                 -- ivoryMedium：画布
    secondaryBackground = "#FAF9F5",        -- ivoryLight：上浮一层
    tertiaryBackground = "#FAF9F5",
    groupedBackground = "#F0EEE6",
    secondaryGroupedBackground = "#FAF9F5", -- 卡片 / 列表分组
    tertiaryGroupedBackground = "#FAF9F5",
    label = "#141413",                      -- slateDark：主文字
    secondaryLabel = "#87867F",             -- cloudDark：次级文字
    tertiaryLabel = "#B0AEA5",              -- cloudMedium：弱化文字
    quaternaryLabel = "#CCCBC8",            -- stone
    fill = "#E3DACC",                       -- oatWarm：高亮底
    secondaryFill = "#F5E3C7",              -- manilla：主打卡片
    tertiaryFill = "#FAF9F5",
    separator = "#CCCBC8",                  -- stone：发丝线
    opaqueSeparator = "#87867F",
    accent = "#D97757",                     -- clay：唯一彩色强调
    accentSoft = "#26D97757",               -- clay @15%
    glass = "#E6FAF9F5",                    -- 80% ivoryLight
    glassStrong = "#F2141413",              -- 播放条 #141413（不透明，等价 playerSurface）
  },

  -- 深色（夜读）：app_palette.dart 的 dark 分支；不给的话宿主会沿用 colors。
  darkColors = {
    background = "#191918",
    secondaryBackground = "#242423",
    tertiaryBackground = "#242423",
    groupedBackground = "#191918",
    secondaryGroupedBackground = "#242423",
    tertiaryGroupedBackground = "#242423",
    label = "#F0EEE6",
    secondaryLabel = "#B5B2A9",
    tertiaryLabel = "#A8A69E",
    quaternaryLabel = "#454540",
    fill = "#34312D",
    secondaryFill = "#3E3329",
    tertiaryFill = "#242423",
    separator = "#454540",
    opaqueSeparator = "#B5B2A9",
    accent = "#E68E70",
    accentSoft = "#26E68E70",
    glass = "#E6242423",
    glassStrong = "#F2141413",
  },

  -- 版面标题：HeroHeading 实测 56 / 40 / 32（角色是 heading，字号被覆盖）
  pageTitleCompactSize = 40,
  pageTitleRegularSize = 56,
  sectionHeaderSize = 12, -- InlineLabel：12px 大写 + 1.6 字距

  displayWeight = 400,  -- display 68 w400（serif 角色）
  headingWeight = 700,  -- heading w700
  titleWeight = 600,    -- subheading w600
  bodyWeight = 400,
  labelWeight = 600,    -- captionStrong / InlineLabel strong

  -- 歌词：非聚焦行缩到 .97、左对齐、翻译与原文同为 #87867F(=48% ink)
  lyricWeight = 500,
  lyricTranslationWeight = 400,
  lyricFontScale = 1,
  lyricTranslationScale = 0.73,
  lyricLineHeight = 1.5,
  lyricTranslationLineHeight = 1.45,
  lyricTranslationGap = 5,
  lyricDimAlpha = 0.48,
  lyricTranslationAlpha = 0.48,
  lyricTextAlign = "start",
  lyricSpringMassScale = 1,
  lyricSpringStiffnessScale = 1,
  lyricSpringDampingScale = 1,
  lyricStaggerDelay = 0.05,
  lyricStaggerDecay = 1.05,
  lyricFocusScaleDelta = 3,
}

local LAYOUT = {
  id = "parchment.field-notes.layout",
  name = "Field Notes",
  compactInset = 24,   -- 内容区 < 560 时
  regularInset = 56,   -- 内容区 > 900 时（560–900 为 32，宿主只有两档）
  tvInsetFactor = 0.043,
  maxContentWidth = 1020, -- 参考实现硬编码的内容列宽
  tvMaxContentWidth = 1560,
  tabletBreakpoint = 720, -- _compactBreakpoint
}

local THEME_META = {
  id = "parchment.field-notes",
  name = "Early Development",
  version = 1,
}

-- 参考快照的调色板，写进令牌说明，方便对照核查。
local PALETTE = {
  slateDark = "#141413",
  ivoryMedium = "#F0EEE6",
  ivoryLight = "#FAF9F5",
  cloudMedium = "#B0AEA5",
  cloudDark = "#87867F",
  stone = "#CCCBC8",
  slateMedium = "#3D3D3A",
  oatWarm = "#E3DACC",
  manilla = "#F5E3C7",
  clay = "#D97757",
  clayDeep = "#C6613F",
  onDark = "#FAF9F5",
  onDarkMuted = "#B0AEA5",
}

local TYPE_SCALE = {
  { role = "caption", size = 12, height = 1.4, letterSpacing = -0.24 },
  { role = "bodySm", size = 16, height = 1.3, letterSpacing = -0.08 },
  { role = "body", size = 20, height = 1.4, letterSpacing = 0 },
  { role = "subheading", size = 24, height = 1.3, letterSpacing = -0.05, weight = 600 },
  { role = "heading", size = 61, height = 1.1, letterSpacing = -0.12, weight = 700 },
  { role = "display", size = 68, height = 1.1, letterSpacing = 0, weight = 400 },
  { role = "wordmark", size = 12, height = 1.0, letterSpacing = 3.2, weight = 700 },
}

-- 卡片圆角是唯一由用户在本插件里调的令牌：它必须每次从配置读，
-- 不然客户端「设置 → 圆角设置」选「跟随主题设置」时拿到的永远是写死的 0。
--
-- 单位是 px，写进 `groupedCardRadius`：客户端「跟随主题设置」时显示/使用的就是它。
-- 组件类表面（按钮、胶囊）仍由 `cornerScale` 决定，本插件保持设计值（1），
-- 所以调这个滑块只会改卡片，不会把播放按钮一起拍方。
local function elements()
  local out = {}
  for key, value in pairs(ELEMENTS) do
    out[key] = value
  end
  local px = tonumber(config.get("cornerPx"))
  if px == nil then
    -- 老配置只存过系数。
    local scale = tonumber(config.get("cornerScale")) or 1
    px = scale * 16
  end
  if px < 0 then
    px = 0
  elseif px > 32 then
    px = 32
  end
  out.groupedCardRadius = math.floor(px + 0.5)
  return out
end

function M.bundle()
  return {
    theme = {
      id = THEME_META.id,
      name = THEME_META.name,
      version = THEME_META.version,
      elements = elements(),
    },
    layout = LAYOUT,
  }
end

function M.json()
  return host.json_encode({
    source = SOURCE,
    theme = { id = THEME_META.id, name = THEME_META.name, version = THEME_META.version, elements = elements() },
    layout = LAYOUT,
    palette = PALETTE,
    typeScale = TYPE_SCALE,
  })
end

-- 令牌摘要：给宿主日志、诊断导出或外部探针看，不再是页面上的对照表。
function M.summary()
  local rows = {
    "【主题令牌】来源 " .. SOURCE,
    "groupedCardRadius = " .. tostring(elements().groupedCardRadius)
      .. " px（卡片圆角；parchment 用色阶与 1px 发丝线分层，全站零阴影。"
      .. "客户端「设置 → 外观 → 圆角设置」选「跟随主题设置」时用这个值，"
      .. "选「自行调节」时以用户滑块为准）",
    "cornerScale = " .. tostring(elements().cornerScale) .. "（组件类表面：按钮、胶囊的系数）",
    "listTileMinHeight = 64 / listTileVerticalPadding = 10（TrackRow 实测 64px 行高）",
    "controlRadius = 12（描边按钮 12px）",
    "glassBlurSigma = 0（该阶段完全没有毛玻璃）",
    "pageTitleCompactSize = 40 / pageTitleRegularSize = 56（HeroHeading 三档 56/40/32）",
    "sectionHeaderSize = 12（InlineLabel：12px 大写 + 1.6 字距）",
    "displayWeight = 400 / headingWeight = 700 / titleWeight = 600 / labelWeight = 600",
    "lyricLineHeight = 1.5 / lyricTranslationScale = 0.73 / lyricTranslationGap = 5",
    "lyricDimAlpha = 0.48 / lyricTranslationAlpha = 0.48（原文与翻译同为 #87867F）",
    "lyricFocusScaleDelta = 3（非聚焦行缩到 .97，聚焦行中心固定在视口 35% 高度）",
    "lyricStaggerDelay = 0.05 / lyricStaggerDecay = 1.05 / lyricTextAlign = start",
    "",
    "【布局令牌】",
    "compactInset = 24 / regularInset = 56（内容区 <560 / >900）",
    "maxContentWidth = 1020 / tabletBreakpoint = 720",
    "",
    "【调色板】宿主令牌不含颜色，这里仅作对照：",
    "slateDark #141413 · ivoryMedium #F0EEE6 · ivoryLight #FAF9F5 · oatWarm #E3DACC",
    "manilla #F5E3C7 · stone #CCCBC8 · cloudMedium #B0AEA5 · cloudDark #87867F",
    "slateMedium #3D3D3A · clay #D97757 · clayDeep #C6613F · playerSurface #141413",
  }
  return table.concat(rows, "\n")
end

-- 完整令牌 JSON（诊断导出 / 外部探针）。
function M.token_json()
  return host.json_encode({
    theme = { id = THEME_META.id, elements = elements() },
    layout = LAYOUT,
  })
end

-- 关键令牌短清单。
function M.key_lines()
  local function first(map)
    local keys = {}
    for key in pairs(map) do
      keys[#keys + 1] = tostring(key)
    end
    table.sort(keys)
    if #keys == 0 then
      return "—"
    end
    return keys[1] .. " … 共 " .. #keys .. " 项"
  end
  local rows = {
    "主题 " .. tostring(THEME_META.id) .. " v" .. tostring(THEME_META.version),
    "颜色槽 " .. first(ELEMENTS.colors) .. "（深浅两套）",
    "几何 railWidth " .. tostring(ELEMENTS.railWidth) .. " · playerBarHeight "
      .. tostring(ELEMENTS.playerBarHeight) .. " · glassBlurSigma "
      .. tostring(ELEMENTS.glassBlurSigma) .. " · 卡片圆角 "
      .. tostring(elements().groupedCardRadius) .. " px",
    "正在播放 左栏 " .. tostring(ELEMENTS.nowPlayingArtworkFraction) .. "W（"
      .. tostring(ELEMENTS.nowPlayingArtworkMin) .. "–"
      .. tostring(ELEMENTS.nowPlayingArtworkMax) .. "）· 封面直角 "
      .. tostring(ELEMENTS.nowPlayingCoverRadius),
  }
  return table.concat(rows, "\n")
end

return M
