"""Add now-playing + background tokens to the client's LazerThemeTokens.

Run:  python tools/patch_client_theme2.py
Idempotent: each replacement is guarded by an already-applied check.
"""
import io

PATH = r"E:\projects\lazer_nextgen\lib\theme\lazer_theme.dart"

NEW_FIELDS = """    this.nowPlayingArtworkMax = 0,
    this.nowPlayingArtworkMin = 0,
    this.nowPlayingArtworkFraction = 0,
    this.nowPlayingSidePadding = 0,
    this.nowPlayingSidePaddingMax = 0,
    this.nowPlayingTitleSize = 0,
    this.nowPlayingSubtitleSize = 0,
    this.nowPlayingMetaSize = 0,
    this.nowPlayingDockHeight = 0,
    this.nowPlayingCoverRadius = 0,
    this.backgroundOpacity = 1,
    this.backgroundBlurSigma = -1,
    this.backgroundVeilAlpha = -1,
    this.backgroundPlayMode = '',
    this.artworkRadius = 0,
  });
"""

NEW_DECLS = """
  /// Widest artwork square on the listening canvas; `0` keeps 440.
  final double nowPlayingArtworkMax;

  /// Narrowest artwork square; `0` keeps 240.
  final double nowPlayingArtworkMin;

  /// Share of the canvas the artwork column takes; `0` keeps .34.
  final double nowPlayingArtworkFraction;

  /// Base horizontal padding of the listening canvas; `0` keeps 28.
  final double nowPlayingSidePadding;

  /// Upper clamp of that padding; `0` keeps 80.
  final double nowPlayingSidePaddingMax;

  /// Track title size on the listening canvas; `0` keeps the built-in ramp.
  final double nowPlayingTitleSize;

  /// Translator line size; `0` keeps the built-in ramp.
  final double nowPlayingSubtitleSize;

  /// Artist / album line size; `0` keeps the built-in ramp.
  final double nowPlayingMetaSize;

  /// Height of the transport dock; `0` keeps the built-in metric.
  final double nowPlayingDockHeight;

  /// Artwork corner radius on the listening canvas; `0` is square.
  final double nowPlayingCoverRadius;

  /// Artwork corner radius everywhere else; `0` is square.
  final double artworkRadius;

  /// Opacity of the painted backdrop, 1 keeps it fully drawn.
  final double backgroundOpacity;

  /// Backdrop blur; negative keeps the host preference, `0` disables it.
  final double backgroundBlurSigma;

  /// Strength of the veil painted over the backdrop; negative keeps the host
  /// default (.60), `1` hides the backdrop completely.
  final double backgroundVeilAlpha;

  /// Backdrop mode the skin wants: `''` keeps the user setting, `off` paints a
  /// flat canvas (what a paper design needs), `nowPlayingStatic` /
  /// `nowPlayingDynamic` keep the album flow.
  final String backgroundPlayMode;
"""

JSON_FIELDS = """      'nowPlayingArtworkMax': nowPlayingArtworkMax,
      'nowPlayingArtworkMin': nowPlayingArtworkMin,
      'nowPlayingArtworkFraction': nowPlayingArtworkFraction,
      'nowPlayingSidePadding': nowPlayingSidePadding,
      'nowPlayingSidePaddingMax': nowPlayingSidePaddingMax,
      'nowPlayingTitleSize': nowPlayingTitleSize,
      'nowPlayingSubtitleSize': nowPlayingSubtitleSize,
      'nowPlayingMetaSize': nowPlayingMetaSize,
      'nowPlayingDockHeight': nowPlayingDockHeight,
      'nowPlayingCoverRadius': nowPlayingCoverRadius,
      'artworkRadius': artworkRadius,
      'backgroundOpacity': backgroundOpacity,
      'backgroundBlurSigma': backgroundBlurSigma,
      'backgroundVeilAlpha': backgroundVeilAlpha,
      'backgroundPlayMode': backgroundPlayMode,
"""

PARSE_FIELDS = """      nowPlayingArtworkMax: number('nowPlayingArtworkMax', 0, max: 1200),
      nowPlayingArtworkMin: number('nowPlayingArtworkMin', 0, max: 1200),
      nowPlayingArtworkFraction: number(
        'nowPlayingArtworkFraction',
        0,
        max: .9,
      ),
      nowPlayingSidePadding: number('nowPlayingSidePadding', 0, max: 200),
      nowPlayingSidePaddingMax: number(
        'nowPlayingSidePaddingMax',
        0,
        max: 400,
      ),
      nowPlayingTitleSize: number('nowPlayingTitleSize', 0, max: 96),
      nowPlayingSubtitleSize: number('nowPlayingSubtitleSize', 0, max: 72),
      nowPlayingMetaSize: number('nowPlayingMetaSize', 0, max: 72),
      nowPlayingDockHeight: number('nowPlayingDockHeight', 0, max: 240),
      nowPlayingCoverRadius: number('nowPlayingCoverRadius', 0, max: 64),
      artworkRadius: number('artworkRadius', 0, max: 64),
      backgroundOpacity: number('backgroundOpacity', 1, max: 1),
      backgroundBlurSigma: number('backgroundBlurSigma', -1, min: -1, max: 96),
      backgroundVeilAlpha: number('backgroundVeilAlpha', -1, min: -1, max: 1),
      backgroundPlayMode: skinMode(elements['backgroundPlayMode']),
"""

COPY_PARAMS = """    double? nowPlayingArtworkMax,
    double? nowPlayingArtworkMin,
    double? nowPlayingArtworkFraction,
    double? nowPlayingSidePadding,
    double? nowPlayingSidePaddingMax,
    double? nowPlayingTitleSize,
    double? nowPlayingSubtitleSize,
    double? nowPlayingMetaSize,
    double? nowPlayingDockHeight,
    double? nowPlayingCoverRadius,
    double? artworkRadius,
    double? backgroundOpacity,
    double? backgroundBlurSigma,
    double? backgroundVeilAlpha,
    String? backgroundPlayMode,
"""

COPY_BODY = """    nowPlayingArtworkMax: nowPlayingArtworkMax ?? this.nowPlayingArtworkMax,
    nowPlayingArtworkMin: nowPlayingArtworkMin ?? this.nowPlayingArtworkMin,
    nowPlayingArtworkFraction:
        nowPlayingArtworkFraction ?? this.nowPlayingArtworkFraction,
    nowPlayingSidePadding:
        nowPlayingSidePadding ?? this.nowPlayingSidePadding,
    nowPlayingSidePaddingMax:
        nowPlayingSidePaddingMax ?? this.nowPlayingSidePaddingMax,
    nowPlayingTitleSize: nowPlayingTitleSize ?? this.nowPlayingTitleSize,
    nowPlayingSubtitleSize:
        nowPlayingSubtitleSize ?? this.nowPlayingSubtitleSize,
    nowPlayingMetaSize: nowPlayingMetaSize ?? this.nowPlayingMetaSize,
    nowPlayingDockHeight: nowPlayingDockHeight ?? this.nowPlayingDockHeight,
    nowPlayingCoverRadius:
        nowPlayingCoverRadius ?? this.nowPlayingCoverRadius,
    artworkRadius: artworkRadius ?? this.artworkRadius,
    backgroundOpacity: backgroundOpacity ?? this.backgroundOpacity,
    backgroundBlurSigma: backgroundBlurSigma ?? this.backgroundBlurSigma,
    backgroundVeilAlpha: backgroundVeilAlpha ?? this.backgroundVeilAlpha,
    backgroundPlayMode: backgroundPlayMode ?? this.backgroundPlayMode,
"""

LERB_BODY = """      nowPlayingArtworkMax: mix(
        nowPlayingArtworkMax,
        other.nowPlayingArtworkMax,
      ),
      nowPlayingArtworkMin: mix(
        nowPlayingArtworkMin,
        other.nowPlayingArtworkMin,
      ),
      nowPlayingArtworkFraction: mix(
        nowPlayingArtworkFraction,
        other.nowPlayingArtworkFraction,
      ),
      nowPlayingSidePadding: mix(
        nowPlayingSidePadding,
        other.nowPlayingSidePadding,
      ),
      nowPlayingSidePaddingMax: mix(
        nowPlayingSidePaddingMax,
        other.nowPlayingSidePaddingMax,
      ),
      nowPlayingTitleSize: mix(nowPlayingTitleSize, other.nowPlayingTitleSize),
      nowPlayingSubtitleSize: mix(
        nowPlayingSubtitleSize,
        other.nowPlayingSubtitleSize,
      ),
      nowPlayingMetaSize: mix(nowPlayingMetaSize, other.nowPlayingMetaSize),
      nowPlayingDockHeight: mix(
        nowPlayingDockHeight,
        other.nowPlayingDockHeight,
      ),
      nowPlayingCoverRadius: mix(
        nowPlayingCoverRadius,
        other.nowPlayingCoverRadius,
      ),
      artworkRadius: mix(artworkRadius, other.artworkRadius),
      backgroundOpacity: mix(backgroundOpacity, other.backgroundOpacity),
      backgroundBlurSigma: mix(backgroundBlurSigma, other.backgroundBlurSigma),
      backgroundVeilAlpha: mix(
        backgroundVeilAlpha,
        other.backgroundVeilAlpha,
      ),
      backgroundPlayMode: t < .5 ? backgroundPlayMode : other.backgroundPlayMode,
"""

MODE_HELPER = """
/// Normalises `backgroundPlayMode`; unknown values mean "keep the user setting".
String skinMode(Object? value) {
  if (value is! String) return '';
  switch (value.trim()) {
    case 'off':
    case 'none':
      return 'off';
    case 'nowPlayingStatic':
    case 'static':
      return 'nowPlayingStatic';
    case 'nowPlayingDynamic':
    case 'dynamic':
      return 'nowPlayingDynamic';
    default:
      return '';
  }
}
"""


def read():
    with io.open(PATH, "r", encoding="utf-8") as handle:
        return handle.read()


def write(text):
    with io.open(PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def once(text, old, new, label, guard=None):
    marker = guard if guard is not None else old
    if marker in text:
        print("skip:", label)
        return text
    if old not in text:
        print("MISS:", label)
        raise SystemExit(1)
    print("patched:", label)
    return text.replace(old, new, 1)


text = read()

text = once(
    text,
    "    this.compactPlayerBarHeight = 0,\n  });",
    "    this.compactPlayerBarHeight = 0,\n" + NEW_FIELDS,
    "constructor",
    guard="this.nowPlayingArtworkMax = 0,",
)

text = once(
    text,
    "  /// Compact player-bar minimum height; `0` keeps the built-in 56/60.\n  final double compactPlayerBarHeight;\n",
    "  /// Compact player-bar minimum height; `0` keeps the built-in 56/60.\n"
    "  final double compactPlayerBarHeight;\n"
    + NEW_DECLS,
    "fields",
    guard="final double nowPlayingArtworkMax;",
)

text = once(
    text,
    "      'compactPlayerBarHeight': compactPlayerBarHeight,\n    },\n  };",
    "      'compactPlayerBarHeight': compactPlayerBarHeight,\n"
    + JSON_FIELDS
    + "    },\n  };",
    "toJson",
    guard="'nowPlayingArtworkMax': nowPlayingArtworkMax,",
)

text = once(
    text,
    "      compactPlayerBarHeight: number('compactPlayerBarHeight', 0, max: 160),\n    );",
    "      compactPlayerBarHeight: number('compactPlayerBarHeight', 0, max: 160),\n"
    + PARSE_FIELDS
    + "    );",
    "fromJson",
    guard="nowPlayingArtworkMax: number(",
)

text = once(
    text,
    "    double? compactPlayerBarHeight,\n  }) => LazerThemeTokens(",
    "    double? compactPlayerBarHeight,\n" + COPY_PARAMS + "  }) => LazerThemeTokens(",
    "copyWith params",
    guard="double? nowPlayingArtworkMax,",
)

text = once(
    text,
    "    compactPlayerBarHeight:\n        compactPlayerBarHeight ?? this.compactPlayerBarHeight,\n  );",
    "    compactPlayerBarHeight:\n        compactPlayerBarHeight ?? this.compactPlayerBarHeight,\n"
    + COPY_BODY
    + "  );",
    "copyWith body",
    guard="nowPlayingArtworkMax: nowPlayingArtworkMax ?? this.nowPlayingArtworkMax,",
)

text = once(
    text,
    "      compactPlayerBarHeight: mix(\n        compactPlayerBarHeight,\n        other.compactPlayerBarHeight,\n      ),\n    );",
    "      compactPlayerBarHeight: mix(\n        compactPlayerBarHeight,\n        other.compactPlayerBarHeight,\n      ),\n"
    + LERB_BODY
    + "    );",
    "lerp",
    guard="nowPlayingArtworkMax: mix(",
)

text = once(
    text,
    "@immutable\nclass LazerThemeTokens extends ThemeExtension<LazerThemeTokens> {",
    MODE_HELPER.lstrip("\n") + "\n@immutable\nclass LazerThemeTokens extends ThemeExtension<LazerThemeTokens> {",
    "mode helper",
)

write(text)
print("\ndone")
