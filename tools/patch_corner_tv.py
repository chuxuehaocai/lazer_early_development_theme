"""Wire the large-screen (ten-foot) presentation into the global corner scale.

The desktop widget tree multiplies every `BorderRadius` by
`AppleShape.scaleOf(context)`; the TV presentation was written separately and
kept hard-coded radii, so 设置 → 圆角设置 could not reach it. This script is
idempotent: it rewrites plain integer radii once and then reports nothing to do.
"""
import io
import re

FILES = [
    r"E:\projects\lazer_nextgen\lib\tv\large_screen_widgets.dart",
    r"E:\projects\lazer_nextgen\lib\tv\large_screen_chrome.dart",
    r"E:\projects\lazer_nextgen\lib\tv\large_screen_pages.dart",
]

IMPORT = "import '../theme/shape_scale.dart';\n"
IMPORT_AFTER = "import '../theme/apple_design.dart';\n"

# Call sites whose argument is an expression rather than a literal: a pill or a
# circle whose value comes from the metrics table. Scaled through AppleShape.r.
EXPRESSION_SITES = [
    (
        "          ? BorderRadius.circular(size / 2)\n"
        "          : BorderRadius.circular(radius),\n",
        "          ? BorderRadius.circular(AppleShape.r(context, size / 2))\n"
        "          : BorderRadius.circular(AppleShape.r(context, radius)),\n",
    ),
    (
        "                      borderRadius: BorderRadius.circular(\n"
        "                        LargeScreenMetrics.navBarHeight / 2,\n"
        "                      ),\n",
        "                      borderRadius: BorderRadius.circular(\n"
        "                        AppleShape.r(\n"
        "                          context,\n"
        "                          LargeScreenMetrics.navBarHeight / 2,\n"
        "                        ),\n"
        "                      ),\n",
    ),
    (
        "    final BorderRadius radius = BorderRadius.circular(\n"
        "      LargeScreenMetrics.transportHeight / 2,\n"
        "    );\n",
        "    final BorderRadius radius = BorderRadius.circular(\n"
        "      AppleShape.r(context, LargeScreenMetrics.transportHeight / 2),\n"
        "    );\n",
    ),
    (
        "      borderRadius: BorderRadius.circular(widget.size / 2),\n",
        "      borderRadius: BorderRadius.circular(\n"
        "        AppleShape.r(context, widget.size / 2),\n"
        "      ),\n",
    ),
]

LITERAL = re.compile(r"BorderRadius\.circular\((\d+(?:\.\d+)?)\)")


def main():
    total = 0
    for path in FILES:
        text = io.open(path, encoding="utf-8").read()
        before = text

        if "shape_scale.dart" not in text:
            if IMPORT_AFTER in text:
                text = text.replace(IMPORT_AFTER, IMPORT_AFTER + IMPORT, 1)
            else:
                print("MISS import anchor in", path)
                continue

        for anchor, replacement in EXPRESSION_SITES:
            if anchor in text:
                text = text.replace(anchor, replacement, 1)

        text, count = LITERAL.subn(
            lambda m: "BorderRadius.circular(%s * AppleShape.scaleOf(context))" % m.group(1),
            text,
        )
        total += count

        if text != before:
            io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        print(
            "%-52s literal=%d scaleOf=%d raw-left=%d"
            % (
                path.rsplit("\\", 1)[-1],
                count,
                text.count("AppleShape.scaleOf"),
                len(LITERAL.findall(text)) + sum(1 for a, _ in EXPRESSION_SITES if a in text),
            )
        )
    print("literals rewritten this run:", total)


if __name__ == "__main__":
    main()
