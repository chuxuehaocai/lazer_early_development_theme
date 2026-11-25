# Material 图标清单

`icons.svg` 与 `icons.md` 由 `tools/build_icons.py` 生成，不要手改；
需要增删图标时改脚本里的 `ICON_SPECS` 再跑一次。

- 精灵图：`docs/icons.svg`（可查看的产物，**不进插件包**）
- 运行时：`plugin/frontend/js/icons.js` 内联同一批 symbol（页面里 `<use href="#i-home">`）
- symbol 数量：**49**
- 来源：`D:\flutter\packages\flutter\lib\src\material\icons.dart`（codePoint）+ `D:\flutter\bin\cache\artifacts\material_fonts\materialicons-regular.otf`（字形轮廓，512 upm → 24x24 归一化）

## 引用方式

```html
<svg class="icon" aria-hidden="true"><use href="#i-home"/></svg>
```

```css
.icon { width: 24px; height: 24px; fill: currentColor; }
.icon-16 { width: 16px; height: 16px; }
```

`<symbol>` 里只有一个 `<path>`，不带 `fill`，所以颜色由 CSS 的 `fill`/`color` 继承决定。

随包前端不要引用外部 svg 文件（`<use href="icons.svg#i-home">` 在 `file://` 下会被同源策略拦住），
包内也不放第二份精灵图。`plugin/frontend/js/icons.js`（同一次生成）会把下面这批 symbol 内联注入
文档，页面里直接 `<use href="#i-home">` 即可；脚本同时暴露 `window.LZ_ICONS.has(name)` 与
`window.LZ_ICONS.svg(name, size)`。

## 图标表

| # | Flutter 图标名 | symbol id | codePoint | 用途 |
| --- | --- | --- | --- | --- |
| 1 | `home` | `i-home` | `0xe318` | 侧栏/底栏「主页」标签，选中态 |
| 2 | `home_outlined` | `i-home-outlined` | `0xf107` | 「主页」标签未选中态 |
| 3 | `search` | `i-search` | `0xe567` | 搜索入口、搜索框前缀图标（激活态） |
| 4 | `search_outlined` | `i-search-outlined` | `0xf34b` | 「搜索」标签未选中态 |
| 5 | `favorite_border_rounded` | `i-favorite-border-rounded` | `0xf737` | 未收藏的心形按钮 |
| 6 | `favorite_rounded` | `i-favorite-rounded` | `0xf738` | 已收藏的心形按钮 |
| 7 | `person_outline` | `i-person-outline` | `0xe497` | 「我的」标签未选中态、默认头像 |
| 8 | `person` | `i-person` | `0xe491` | 「我的」标签选中态 |
| 9 | `settings_outlined` | `i-settings-outlined` | `0xf36e` | 设置入口（未选中） |
| 10 | `settings` | `i-settings` | `0xe57f` | 设置页标题图标、插件页面默认图标 |
| 11 | `play_arrow_rounded` | `i-play-arrow-rounded` | `0xf00a0` | 播放按钮 |
| 12 | `pause_rounded` | `i-pause-rounded` | `0xf0056` | 暂停按钮 |
| 13 | `skip_next_rounded` | `i-skip-next-rounded` | `0xf0192` | 下一首 |
| 14 | `skip_previous_rounded` | `i-skip-previous-rounded` | `0xf0193` | 上一首 |
| 15 | `shuffle_rounded` | `i-shuffle-rounded` | `0xf0177` | 随机播放开关 |
| 16 | `repeat_rounded` | `i-repeat-rounded` | `0xf00f7` | 列表循环 |
| 17 | `repeat_one_rounded` | `i-repeat-one-rounded` | `0xf00f6` | 单曲循环 |
| 18 | `volume_up_rounded` | `i-volume-up-rounded` | `0xf029a` | 音量开启 |
| 19 | `volume_down_rounded` | `i-volume-down-rounded` | `0xf0297` | 音量中等（0 < volume < 0.5，外壳播放条按音量换图标） |
| 20 | `volume_off_rounded` | `i-volume-off-rounded` | `0xf0299` | 静音 / 音量关闭 |
| 21 | `queue_music_rounded` | `i-queue-music-rounded` | `0xf00d0` | 播放队列按钮 |
| 22 | `expand_more_rounded` | `i-expand-more-rounded` | `0xf720` | 折叠、下拉箭头 |
| 23 | `expand_less_rounded` | `i-expand-less-rounded` | `0xf71f` | 展开、上收箭头 |
| 24 | `close_rounded` | `i-close-rounded` | `0xf647` | 关闭对话框、清除搜索 |
| 25 | `remove_rounded` | `i-remove-rounded` | `0xf00f1` | 移出队列、静音滑杆端点 |
| 26 | `crop_square_rounded` | `i-crop-square-rounded` | `0xf68a` | 逐字歌词方框（选中） |
| 27 | `filter_none_rounded` | `i-filter-none-rounded` | `0xf75c` | 逐行歌词标记（未选中） |
| 28 | `refresh_rounded` | `i-refresh-rounded` | `0xf00e9` | 刷新、重试 |
| 29 | `add_rounded` | `i-add-rounded` | `0xf537` | 新建歌单、添加曲目 |
| 30 | `more_vert_rounded` | `i-more-vert-rounded` | `0xf8dc` | 正在播放页右上角「三个点」菜单 |
| 31 | `chevron_right_rounded` | `i-chevron-right-rounded` | `0xf63b` | 列表行尾箭头 |
| 32 | `arrow_back_rounded` | `i-arrow-back-rounded` | `0xf572` | 返回上一页 |
| 33 | `check_rounded` | `i-check-rounded` | `0xf636` | 已选中、已完成 |
| 34 | `content_copy` | `i-content-copy` | `0xe190` | 复制歌曲 ID / 复制链接 |
| 35 | `drag_handle_rounded` | `i-drag-handle-rounded` | `0xf6e2` | 拖动排序把手 |
| 36 | `fullscreen_rounded` | `i-fullscreen-rounded` | `0xf7a6` | 全屏歌词 |
| 37 | `open_in_new_rounded` | `i-open-in-new-rounded` | `0xf0034` | 在浏览器中打开 |
| 38 | `image_rounded` | `i-image-rounded` | `0xf80d` | 封面占位图 |
| 39 | `link_rounded` | `i-link-rounded` | `0xf85a` | 分享链接 |
| 40 | `lock_rounded` | `i-lock-rounded` | `0xf889` | 需要登录 / 已锁定 |
| 41 | `music_note_rounded` | `i-music-note-rounded` | `0xf8ed` | 歌曲占位图标 |
| 42 | `tune_rounded` | `i-tune-rounded` | `0xf0258` | 均衡器、播放设置 |
| 43 | `search_off_rounded` | `i-search-off-rounded` | `0xf013c` | 空搜索结果 |
| 44 | `error_outline_rounded` | `i-error-outline-rounded` | `0xf712` | 错误、网络失败提示 |
| 45 | `playlist_play_rounded` | `i-playlist-play-rounded` | `0xf00a9` | 歌单播放按钮 |
| 46 | `album_rounded` | `i-album-rounded` | `0xf554` | 专辑 |
| 47 | `mic_rounded` | `i-mic-rounded` | `0xf8bd` | 识曲、麦克风 |
| 48 | `radio_rounded` | `i-radio-rounded` | `0xf00d9` | 电台 |
| 49 | `star_rounded` | `i-star-rounded` | `0xf01d4` | 收藏、评分 |

## 生成命令

```powershell
python tools\build_icons.py
```

## 备注

- 全部 49 个图标都成功生成，没有缺失。
- 路径坐标按 512 upm → 24 缩放并保留 3 位小数，与 Material 官方 24 网格路径一致。

## 产物

- `docs/icons.svg` — symbol 精灵图（可查看的产物，不进插件包）
- `docs/icons.md` — 本清单
- `plugin/frontend/js/icons.js` — 随包前端的注入脚本（同批 symbol 内联）
