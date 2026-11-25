"""Covers and small cards follow 设置 → 圆角大小 (idempotent).

`AppCover` now derives its corner from `AppleShape.cardRadiusOf` by default, so a
playlist cover and the 最近播放 small cards all use the same px. A handful of
places need a fixed shape instead (circular avatars, tiles a parent already
clips), and those get an explicit `followCornerSetting: false`.
"""
import io

FLAGS = [
    # 圆形头像 / 圆形正在播放指示
    (r"E:\projects\lazer_nextgen\lib\ui\search_page.dart",
     "                              url: artist.coverUrl,\n"
     "                              size: 44,\n"
     "                              radius: 22,\n",
     "                              url: artist.coverUrl,\n"
     "                              size: 44,\n"
     "                              radius: 22,\n"
     "                              followCornerSetting: false,\n"),
    (r"E:\projects\lazer_nextgen\lib\ui\shell.dart",
     "child: AppCover(url: track.coverUrl, size: 44, radius: 22),",
     "child: AppCover(\n"
     "                    url: track.coverUrl,\n"
     "                    size: 44,\n"
     "                    radius: 22,\n"
     "                    followCornerSetting: false,\n"
     "                  ),"),
    # 大图直角 / 外层已经裁过
    (r"E:\projects\lazer_nextgen\lib\ui\artist_pages.dart",
     "              url: artist.coverUrl,\n"
     "              size: 180,\n"
     "              radius: 0,\n",
     "              url: artist.coverUrl,\n"
     "              size: 180,\n"
     "              radius: 0,\n"
     "              followCornerSetting: false,\n"),
    (r"E:\projects\lazer_nextgen\lib\ui\home_pages.dart",
     "AppCover(url: url, size: tile, radius: 0),",
     "AppCover(\n"
     "                      url: url,\n"
     "                      size: tile,\n"
     "                      radius: 0,\n"
     "                      followCornerSetting: false,\n"
     "                    ),"),
    (r"E:\projects\lazer_nextgen\lib\ui\home_pages.dart",
     "                        size: tile,\n"
     "                        radius: 0,\n",
     "                        size: tile,\n"
     "                        radius: 0,\n"
     "                        followCornerSetting: false,\n"),
    (r"E:\projects\lazer_nextgen\lib\ui\home_pages.dart",
     "                      url: playlist.coverUrl,\n"
     "                      size: compact ? 270 : 330,\n"
     "                      radius: 0,\n",
     "                      url: playlist.coverUrl,\n"
     "                      size: compact ? 270 : 330,\n"
     "                      radius: 0,\n"
     "                      followCornerSetting: false,\n"),
]

# 卡片容器：库里的歌单/专辑格子跟着同一套圆角
CARDS = [
    (r"E:\projects\lazer_nextgen\lib\ui\library_page.dart",
     "borderRadius: BorderRadius.circular(14 * AppleShape.scaleOf(context)),",
     "borderRadius: BorderRadius.circular(\n"
     "                AppleShape.cardRadiusOf(context, LazerThemeTokens.of(context)),\n"
     "              ),"),
    (r"E:\projects\lazer_nextgen\lib\ui\library_page.dart",
     "child: AppCover(url: playlist.coverUrl, size: side, radius: 14),",
     "child: AppCover(url: playlist.coverUrl, size: side, radius: 14),"),
    (r"E:\projects\lazer_nextgen\lib\ui\album_library_page.dart",
     "borderRadius: BorderRadius.circular(14 * AppleShape.scaleOf(context)),",
     "borderRadius: BorderRadius.circular(\n"
     "          AppleShape.cardRadiusOf(context, LazerThemeTokens.of(context)),\n"
     "        ),"),
    (r"E:\projects\lazer_nextgen\lib\ui\artist_pages.dart",
     "borderRadius: BorderRadius.circular(10 * AppleShape.scaleOf(context)),",
     "borderRadius: BorderRadius.circular(\n"
     "                  AppleShape.cardRadiusOf(context, LazerThemeTokens.of(context)),\n"
     "                ),"),
]

IMPORT = "import '../theme/lazer_theme.dart';\n"
IMPORT_ANCHOR = "import '../theme/shape_scale.dart';\n"


def patch(entries, label):
    for path, anchor, replacement in entries:
        text = io.open(path, encoding="utf-8").read()
        if anchor == replacement:
            continue
        count = text.count(anchor)
        if count == 0:
            print("%-28s %s: nothing to do" % (label, path.rsplit("\\", 1)[-1]))
            continue
        if IMPORT not in text:
            text = text.replace(IMPORT_ANCHOR, IMPORT + IMPORT_ANCHOR, 1)
        text = text.replace(anchor, replacement)
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        print("%-28s %s: %d" % (label, path.rsplit("\\", 1)[-1], count))


def main():
    patch(FLAGS, "cover-shape")
    patch(CARDS, "card-radius")


if __name__ == "__main__":
    main()
