"""Let `groupedCardRadius` reach the home shelves (idempotent).

`docs/VERIFY.md` listed this as the remaining pixel-level gap: only
`AppleGroupedCard` and the network browse page read `groupedCardRadius`, while
the home shelves kept their own 11/16/18 px literals. With the parchment skin
(which declares `groupedCardRadius = 0`) those cards stayed rounded even though
the reference build is all square.

Every radius in this file is a card surface: shelf tile (InkWell), playlist card
(InkWell + clip), chart card (Material + tap target), cover card and its
placeholder tile. Buttons keep `controlRadius` — they are not cards.
"""
import io

PATH = r"E:\projects\lazer_nextgen\lib\ui\home_pages.dart"

TOKEN = "LazerThemeTokens.of(context).groupedCardRadius * AppleShape.scaleOf(context)"

EDITS = [
    (
        "borderRadius: BorderRadius.circular(11 * AppleShape.scaleOf(context)),",
        "borderRadius: BorderRadius.circular(%s)," % TOKEN,
    ),
    (
        "BorderRadius.circular(16 * AppleShape.scaleOf(context))",
        "BorderRadius.circular(%s)" % TOKEN,
    ),
    (
        "BorderRadius.circular(18 * AppleShape.scaleOf(context))",
        "BorderRadius.circular(%s)" % TOKEN,
    ),
    (
        "final BorderRadius radius = BorderRadius.circular((large ? 18 : 16) * AppleShape.scaleOf(context));",
        "final BorderRadius radius = BorderRadius.circular(\n"
        "      LazerThemeTokens.of(context).groupedCardRadius *\n"
        "          AppleShape.scaleOf(context),\n"
        "    );",
    ),
    (
        "import '../theme/apple_design.dart';\n",
        "import '../theme/apple_design.dart';\nimport '../theme/lazer_theme.dart';\n",
    ),
]


def main():
    text = io.open(PATH, encoding="utf-8").read()
    before = text
    for anchor, replacement in EDITS:
        if anchor not in text:
            print("skip (absent or already applied):", anchor.splitlines()[0][:64])
            continue
        count = text.count(anchor)
        text = text.replace(anchor, replacement)
        print("replaced %-2d x %s" % (count, anchor.splitlines()[0][:64]))
    if text == before:
        print("nothing to do")
        return
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
    print("groupedCardRadius reads in file:", text.count("groupedCardRadius"))


if __name__ == "__main__":
    main()
