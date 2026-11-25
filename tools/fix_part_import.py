"""A `part of` file cannot carry imports: move the sweep's import to the library."""
import io

PART = r"E:\projects\lazer_nextgen\lib\desktop_lyrics\overlay_presentation.dart"
LIBRARY = r"E:\projects\lazer_nextgen\lib\desktop_lyrics\lyrics_overlay.dart"
IMPORT = "import '../theme/shape_scale.dart';\n"


def main():
    part = io.open(PART, encoding="utf-8").read()
    if IMPORT in part:
        part = part.replace(IMPORT, "", 1)
        io.open(PART, "w", encoding="utf-8", newline="\n").write(part)
        print("removed import from part")

    library = io.open(LIBRARY, encoding="utf-8").read()
    if IMPORT not in library:
        anchor = "import 'package:flutter/material.dart';\n"
        if anchor in library:
            library = library.replace(anchor, anchor + IMPORT, 1)
        else:
            library = IMPORT + library
        io.open(LIBRARY, "w", encoding="utf-8", newline="\n").write(library)
        print("added import to library")


if __name__ == "__main__":
    main()
