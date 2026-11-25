"""Point apple_design's radius shapes at an explicit `cornerScale` argument.

`buildAppleTheme` is a plain function with no BuildContext, so the sweep's
`AppleShape.scaleOf(context)` cannot resolve there. It takes the scale as a
parameter instead.
"""
import io
import re

PATH = r"E:\projects\lazer_nextgen\lib\theme\apple_design.dart"
IMPORT = "import 'shape_scale.dart';\n"


def main():
    text = io.open(PATH, encoding="utf-8").read()
    original = text

    text = text.replace(
        "  LazerThemeTokens ui = LazerThemeTokens.apple,\n}) {",
        "  LazerThemeTokens ui = LazerThemeTokens.apple,\n"
        "  /// 全局圆角强度（见 theme/shape_scale.dart）。主题层形状同样缩放。\n"
        "  double cornerScale = 1,\n}) {",
        1,
    )
    text = text.replace(" * AppleShape.scaleOf(context)", " * cornerScale")
    if text.count(IMPORT) == 1 and "AppleShape" not in text:
        text = text.replace(IMPORT, "", 1)

    io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
    print("cornerScale uses:", text.count("cornerScale"))
    print("changed:", text != original)


if __name__ == "__main__":
    main()
