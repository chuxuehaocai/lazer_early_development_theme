"""Make the modal dialogs honour the active skin (idempotent).

`buildAppleTheme` takes `ui:` for the skin tokens, but the login dialog and the
playlist pickers were built without it, so installing a skin left those modals on
the stock palette while everything behind them changed. Same argument as the
font settings page: a dialog is part of the app, not a separate island.
"""
import io
import re

FILES = [
    (
        r"E:\projects\lazer_nextgen\lib\ui\login.dart",
        [("        fonts: state.fontPreferences,\n",
          "        fonts: state.fontPreferences,\n"
          "        ui: state.pluginTheme ?? LazerThemeTokens.apple,\n")],
    ),
    (
        r"E:\projects\lazer_nextgen\lib\widgets\playlist_picker_dialog.dart",
        [("        fonts: state.fontPreferences,\n",
          "        fonts: state.fontPreferences,\n"
          "        ui: state.pluginTheme ?? LazerThemeTokens.apple,\n")],
    ),
]

IMPORT = "import '../theme/lazer_theme.dart';\n"
IMPORT_ANCHOR = "import '../theme/apple_design.dart';\n"


def main():
    for path, edits in FILES:
        text = io.open(path, encoding="utf-8").read()
        if IMPORT not in text:
            if IMPORT_ANCHOR in text:
                text = text.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + IMPORT, 1)
            else:
                print("MISS import anchor in", path)
        applied = 0
        for anchor, replacement in edits:
            count = text.count(anchor)
            text = text.replace(anchor, replacement)
            applied += count
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        print("%-46s ui: %d" % (path.rsplit("\\", 1)[-1], text.count("ui: state.pluginTheme")))


if __name__ == "__main__":
    main()
