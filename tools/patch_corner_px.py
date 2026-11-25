"""Insert the px helper used by the 圆角设置 row (idempotent)."""
import io

PATH = r"E:\projects\lazer_nextgen\lib\ui\settings_page.dart"

HELPER = (
    "/// 设置页显示的圆角数值（px）：跟随主题时显示皮肤令牌换算出的角。\n"
    "double _cornerPx(AppState state, BuildContext context) =>\n"
    "    state.cornerFollowsTheme\n"
    "    ? AppleShape.pxOfScale(LazerThemeTokens.of(context).cornerScale)\n"
    "    : state.cornerPx;\n\n"
)


def main():
    text = io.open(PATH, encoding="utf-8").read()
    if "_cornerPx(" in text:
        print("helper already present")
        return
    if "import '../theme/lazer_theme.dart';" not in text:
        anchor = "import '../theme/shape_scale.dart';\n"
        text = text.replace(
            anchor, anchor + "import '../theme/lazer_theme.dart';\n", 1
        )
    marker = "class SettingsPage"
    index = text.find(marker)
    if index < 0:
        marker = "\n\n"
        index = text.find(marker, text.find("import '../theme/lazer_theme.dart';"))
    if index < 0:
        raise SystemExit("could not find an insertion point")
    text = text[:index] + HELPER + text[index:]
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
    print("helper inserted; _cornerPx mentions:", text.count("_cornerPx"))


if __name__ == "__main__":
    main()
