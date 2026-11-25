"""Card surfaces read `AppleShape.cardRadiusOf` instead of token × scale.

Why: a skin that declares `groupedCardRadius = 0` made every card permanently
square — multiplying 0 by the global factor is still 0, so the 设置 → 圆角大小
slider looked like it did nothing. In 自行调节 mode the user's px must *replace*
the card radius; in 跟随主题设置 mode the skin's own token is used verbatim.
Component radii (buttons, pills, avatars) keep the proportional factor.

Idempotent: the old expression no longer appears after the first run.
"""
import io

LITERAL = (
    "BorderRadius.circular(LazerThemeTokens.of(context).groupedCardRadius *\n"
    "              AppleShape.scaleOf(context),\n"
    "            )"
)

FILES_AND_ANCHORS = [
    (
        r"E:\projects\lazer_nextgen\lib\ui\home_pages.dart",
        "LazerThemeTokens.of(context).groupedCardRadius * AppleShape.scaleOf(context)",
        "AppleShape.cardRadiusOf(context, LazerThemeTokens.of(context))",
    ),
    (
        r"E:\projects\lazer_nextgen\lib\network\network_browse_page.dart",
        "LazerThemeTokens.of(context).groupedCardRadius * AppleShape.scaleOf(context)",
        "AppleShape.cardRadiusOf(context, LazerThemeTokens.of(context))",
    ),
    (
        r"E:\projects\lazer_nextgen\lib\widgets\apple_ui.dart",
        "(radius ?? ui.groupedCardRadius) * AppleShape.scaleOf(context)",
        "radius ?? AppleShape.cardRadiusOf(context, ui)",
    ),
]


def main():
    for path, anchor, replacement in FILES_AND_ANCHORS:
        text = io.open(path, encoding="utf-8").read()
        count = text.count(anchor)
        if count == 0:
            print("%-40s nothing to do" % path.rsplit("\\", 1)[-1])
            continue
        text = text.replace(anchor, replacement)
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        print("%-40s replaced %d" % (path.rsplit("\\", 1)[-1], count))


if __name__ == "__main__":
    main()
