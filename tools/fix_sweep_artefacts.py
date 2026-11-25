"""Repair sweep artefacts: trailing commas swallowed into the scaled argument,
and the self-import inside shape_scale.dart."""
import io
import os

LIB = r"E:\projects\lazer_nextgen\lib"
BAD = ", * AppleShape.scaleOf(context))"
GOOD = " * AppleShape.scaleOf(context))"


def main():
    fixed = 0
    for root, _dirs, files in os.walk(LIB):
        for name in files:
            if not name.endswith(".dart"):
                continue
            path = os.path.join(root, name)
            text = io.open(path, encoding="utf-8").read()
            if BAD in text:
                text = text.replace(BAD, GOOD)
                io.open(path, "w", encoding="utf-8", newline="\n").write(text)
                fixed += 1
                print("fixed", os.path.relpath(path, LIB))

    target = os.path.join(LIB, "theme", "shape_scale.dart")
    text = io.open(target, encoding="utf-8").read()
    self_import = "import 'shape_scale.dart';\n"
    if self_import in text:
        text = text.replace(self_import, "", 1)
        io.open(target, "w", encoding="utf-8", newline="\n").write(text)
        print("self-import removed")

    print("files repaired:", fixed)


if __name__ == "__main__":
    main()
