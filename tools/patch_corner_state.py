"""Wire the user-facing corner strength preference into AppState (idempotent)."""
import io

STATE = r"E:\projects\lazer_nextgen\lib\state\app_state.dart"
MAIN = r"E:\projects\lazer_nextgen\lib\main.dart"

STATE_EDITS = [
    # fields
    (
        "  bool backgroundBlurEnabled = false;\n",
        "  bool backgroundBlurEnabled = false;\n"
        "\n"
        "  /// 全局圆角强度是否跟随主题令牌（true）还是用用户自己的滑块（false）。\n"
        "  bool cornerFollowsTheme = true;\n"
        "\n"
        "  /// 用户自定义的圆角强度：0 = 全直角，1 = 原样，2 = 加倍。\n"
        "  double cornerStrength = 1;\n",
    ),
    # load
    (
        "      backgroundBlurEnabled =\n"
        "          prefs.getBool('lazer_background_blur_enabled') ?? false;\n",
        "      backgroundBlurEnabled =\n"
        "          prefs.getBool('lazer_background_blur_enabled') ?? false;\n"
        "      cornerFollowsTheme =\n"
        "          prefs.getBool('lazer_corner_follows_theme') ?? true;\n"
        "      cornerStrength = (prefs.getDouble('lazer_corner_strength') ?? 1)\n"
        "          .clamp(kCornerStrengthMin, kCornerStrengthMax);\n",
    ),
    # setters, right after setBackgroundBlur's closing brace
    (
        "  Future<void> setBackgroundBlurEnabled(\n",
        "  /// 在「跟随主题设置」和「自行调节」之间切换。\n"
        "  Future<void> setCornerFollowsTheme(bool value) async {\n"
        "    if (cornerFollowsTheme == value) return;\n"
        "    cornerFollowsTheme = value;\n"
        "    notifyListeners();\n"
        "    await (await SharedPreferences.getInstance()).setBool(\n"
        "      'lazer_corner_follows_theme',\n"
        "      value,\n"
        "    );\n"
        "  }\n"
        "\n"
        "  /// 用户自定义的圆角强度。\n"
        "  Future<void> setCornerStrength(double value) async {\n"
        "    final double next = value.clamp(kCornerStrengthMin, kCornerStrengthMax);\n"
        "    if (cornerStrength == next) return;\n"
        "    cornerStrength = next;\n"
        "    notifyListeners();\n"
        "    await (await SharedPreferences.getInstance()).setDouble(\n"
        "      'lazer_corner_strength',\n"
        "      next,\n"
        "    );\n"
        "  }\n"
        "\n"
        "  Future<void> setBackgroundBlurEnabled(\n",
    ),
]

CONST_ANCHOR = "const double kBackgroundBlurMin"
CONST_BLOCK = """/// 全局圆角强度的取值范围：0 = 全直角，2 = 加倍。
const double kCornerStrengthMin = 0;
const double kCornerStrengthMax = 2;
"""

MAIN_EDITS = [
    (
        "                        child: Builder(\n"
        "                          builder: (context) => Theme(\n",
        "                        child: Builder(\n"
        "                          builder: (context) => AppleShape(\n"
        "                            scale: AppleShape.resolve(\n"
        "                              followTheme: _state.cornerFollowsTheme,\n"
        "                              custom: _state.cornerStrength,\n"
        "                              theme: LazerThemeTokens.of(context),\n"
        "                            ),\n"
        "                            child: Theme(\n",
    ),
    (
        "                            ),\n"
        "                            child: SharedBrowseBackground(\n",
        "                              state: _state,\n"
        "                              navigation: _browseNavigation,\n"
        "                              // Pages consume the frame's safe inset themselves.\n"
        "                              // The desktop rail extends into the Inline row;\n"
        "                              // reserving it for the whole Navigator would push\n"
        "                              // both the logo and page padding down a second time.\n"
        "                              child: child!,\n"
        "                            ),\n"
        "                          ),\n",
        "                              ),\n"
        "                              child: SharedBrowseBackground(\n"
        "                                state: _state,\n"
        "                                navigation: _browseNavigation,\n"
        "                                // Pages consume the frame's safe inset\n"
        "                                // themselves. The desktop rail extends into\n"
        "                                // the Inline row; reserving it for the whole\n"
        "                                // Navigator would push both the logo and page\n"
        "                                // padding down a second time.\n"
        "                                child: child!,\n"
        "                              ),\n"
        "                            ),\n"
        "                          ),\n",
    ),
]


def apply(path, edits):
    text = io.open(path, encoding="utf-8").read()
    for anchor, addition in edits:
        if anchor not in text:
            print("MISS in", path, "->", anchor.strip().splitlines()[0][:70])
            continue
        text = text.replace(anchor, addition, 1)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)
    return text


def main():
    state = io.open(STATE, encoding="utf-8").read()
    if "kCornerStrengthMin" not in state:
        if CONST_ANCHOR not in state:
            print("MISS const anchor")
        else:
            state = state.replace(
                CONST_ANCHOR, CONST_BLOCK + CONST_ANCHOR, 1
            )
            io.open(STATE, "w", encoding="utf-8", newline="\n").write(state)
            print("inserted constants")

    text = apply(STATE, STATE_EDITS)
    print("cornerFollowsTheme mentions:", text.count("cornerFollowsTheme"))
    main_text = apply(MAIN, MAIN_EDITS)
    print("AppleShape mentions in main:", main_text.count("AppleShape"))


if __name__ == "__main__":
    main()
