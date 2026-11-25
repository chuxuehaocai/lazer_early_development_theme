"""Add the `cornerScale` token to LazerThemeTokens (idempotent)."""
import io

PATH = r"E:\projects\lazer_nextgen\lib\theme\lazer_theme.dart"

EDITS = [
    (
        "    this.compactPlayerBarHeight = 0,",
        "    this.compactPlayerBarHeight = 0,\n    this.cornerScale = 1,",
    ),
    (
        "  final double compactPlayerBarHeight;",
        "  final double compactPlayerBarHeight;\n"
        "\n"
        "  /// 全局圆角强度，0 = 全直角，1 = 主题原本的圆角。\n"
        "  ///\n"
        "  /// 用户可以在设置里选择「跟随主题设置」用这个值，或改用自己的滑块。\n"
        "  /// 所有 BorderRadius 都乘上它（见 theme/shape_scale.dart）。\n"
        "  final double cornerScale;",
    ),
    (
        "    'compactPlayerBarHeight': compactPlayerBarHeight,",
        "    'compactPlayerBarHeight': compactPlayerBarHeight,\n"
        "    'cornerScale': cornerScale,",
    ),
    (
        "        compactPlayerBarHeight: number('compactPlayerBarHeight', 0, max: 160),",
        "        compactPlayerBarHeight: number('compactPlayerBarHeight', 0, max: 160),\n"
        "        cornerScale: number('cornerScale', 1, max: 2),",
    ),
    (
        "    double? compactPlayerBarHeight,",
        "    double? compactPlayerBarHeight,\n    double? cornerScale,",
    ),
    (
        "      compactPlayerBarHeight:\n          compactPlayerBarHeight ?? this.compactPlayerBarHeight,",
        "      compactPlayerBarHeight:\n"
        "          compactPlayerBarHeight ?? this.compactPlayerBarHeight,\n"
        "      cornerScale: cornerScale ?? this.cornerScale,",
    ),
]


def main():
    text = io.open(PATH, encoding="utf-8").read()
    applied = 0
    for anchor, addition in EDITS:
        if "cornerScale" in addition and "cornerScale" in text and anchor not in text:
            print("skip (already there):", anchor.strip()[:50])
            continue
        if anchor not in text:
            print("MISS:", anchor.strip()[:60])
            continue
        text = text.replace(anchor, addition, 1)
        applied += 1
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
    print("applied", applied, "of", len(EDITS), "cornerScale mentions:", text.count("cornerScale"))


if __name__ == "__main__":
    main()
