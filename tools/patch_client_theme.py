"""Patch lazer_nextgen so Lua skins can drive colours and shell geometry.

Run:  python tools/patch_client_theme.py
Idempotent: every replacement is guarded by a marker check.
"""
import io
import os
import sys

ROOT = r"E:\projects\lazer_nextgen"
THEME = os.path.join(ROOT, "lib", "theme", "lazer_theme.dart")
APPLE = os.path.join(ROOT, "lib", "theme", "apple_design.dart")
PLAYER = os.path.join(ROOT, "lib", "ui", "player_bar.dart")
PAGES = os.path.join(ROOT, "lib", "ui", "large_screen_pages.dart")


def read(path):
    with io.open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def replace_once(text, old, new, label):
    if new in text:
        print("skip (already applied):", label)
        return text
    if old not in text:
        print("MISS (skipped):", label)
        return text
    print("patched:", label)
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# 1. lazer_theme.dart — colour slots + geometry tokens
# ---------------------------------------------------------------------------
text = read(THEME)

HELPERS = r'''
// ---------------------------------------------------------------------------
// Skin colours
// ---------------------------------------------------------------------------

/// Semantic colour slots a skin may override.
///
/// They are the same roles the built-in Apple palette uses, so a skin changes
/// tones without the host losing contrast, focus or accessibility guarantees.
const Set<String> skinColorSlots = <String>{
  'background',
  'secondaryBackground',
  'tertiaryBackground',
  'groupedBackground',
  'secondaryGroupedBackground',
  'tertiaryGroupedBackground',
  'label',
  'secondaryLabel',
  'tertiaryLabel',
  'quaternaryLabel',
  'fill',
  'secondaryFill',
  'tertiaryFill',
  'separator',
  'opaqueSeparator',
  'accent',
  'accentSoft',
  'glass',
  'glassStrong',
};

/// Aliases let a paper-style skin speak its own vocabulary.
///
/// `canvas`, `ink`, `hairline` and `playerSurface` are the names the parchment
/// design system uses; they resolve to the semantic slots above.
const Map<String, String> skinColorAliases = <String, String>{
  'page': 'background',
  'canvas': 'background',
  'ivory': 'background',
  'ivorymedium': 'background',
  'surface': 'secondaryGroupedBackground',
  'card': 'secondaryGroupedBackground',
  'ivorylight': 'secondaryGroupedBackground',
  'panel': 'secondaryGroupedBackground',
  'grouped': 'groupedBackground',
  'ink': 'label',
  'text': 'label',
  'slatedark': 'label',
  'muted': 'secondaryLabel',
  'secondaryink': 'secondaryLabel',
  'clouddark': 'secondaryLabel',
  'dim': 'tertiaryLabel',
  'tertiaryink': 'tertiaryLabel',
  'cloudmedium': 'tertiaryLabel',
  'hairline': 'separator',
  'stone': 'separator',
  'highlight': 'fill',
  'oatwarm': 'fill',
  'playerbar': 'glassStrong',
  'playersurface': 'glassStrong',
  'glassstrong': 'glassStrong',
  'glass': 'glass',
  'clay': 'accent',
  'accent': 'accent',
};

/// Resolves a skin colour key (slot or alias, case-insensitive) to a slot.
String? canonicalColorSlot(Object? name) {
  if (name is! String) return null;
  final key = name.trim().toLowerCase();
  if (key.isEmpty) return null;
  if (skinColorSlots.contains(name.trim())) return name.trim();
  final alias = skinColorAliases[key];
  if (alias != null) return alias;
  for (final slot in skinColorSlots) {
    if (slot.toLowerCase() == key) return slot;
  }
  return null;
}

/// Parses `#rgb`, `#rrggbb`, `#aarrggbb`, `0xAARRGGBB` or an integer ARGB.
Color? parseSkinColor(Object? value) {
  if (value is num) {
    final int argb = value.toInt();
    if (argb < 0 || argb > 0xFFFFFFFF) return null;
    return Color(argb);
  }
  if (value is! String) return null;
  var text = value.trim();
  if (text.isEmpty) return null;
  if (text.startsWith('#')) text = text.substring(1);
  if (text.startsWith('0x') || text.startsWith('0X')) text = text.substring(2);
  if (text.length == 3) {
    text = text.split('').map((c) => '$c$c').join();
  }
  if (text.length == 6) text = 'FF$text';
  if (text.length != 8) return null;
  final int? parsed = int.tryParse(text, radix: 16);
  if (parsed == null) return null;
  return Color(parsed);
}

/// Parses the `colors` map of a skin; unknown keys and bad values are ignored.
Map<String, Color> parseSkinColors(Object? raw) {
  if (raw is! Map) return const <String, Color>{};
  final out = <String, Color>{};
  for (final entry in raw.entries) {
    final slot = canonicalColorSlot(entry.key);
    final color = parseSkinColor(entry.value);
    if (slot == null || color == null) continue;
    out[slot] = color;
  }
  return out;
}

/// `#AARRGGBB`, the format [parseSkinColor] accepts back.
String formatSkinColor(Color color) =>
    '#${color.toARGB32().toRadixString(16).padLeft(8, '0').toUpperCase()}';

'''

anchor = "@immutable\nclass LazerThemeTokens extends ThemeExtension<LazerThemeTokens> {"
text = replace_once(text, anchor, HELPERS.lstrip("\n") + "\n" + anchor, "colour helpers")

text = replace_once(
    text,
    "    this.controlRadius = 12,\n    this.glassBlurSigma = 16,\n  });",
    "    this.controlRadius = 12,\n"
    "    this.glassBlurSigma = 16,\n"
    "    this.colors = const <String, Color>{},\n"
    "    this.railWidth = 0,\n"
    "    this.playerBarHeight = 0,\n"
    "    this.compactPlayerBarHeight = 0,\n"
    "  });",
    "constructor params",
)

text = replace_once(
    text,
    "  final double glassBlurSigma;\n",
    "  final double glassBlurSigma;\n"
    "\n"
    "  /// Semantic colour overrides keyed by [skinColorSlots]. Empty keeps the\n"
    "  /// built-in palette; aliases are normalised by [parseSkinColors].\n"
    "  final Map<String, Color> colors;\n"
    "\n"
    "  /// Sidebar rail width in logical pixels; `0` keeps the adaptive metric.\n"
    "  final double railWidth;\n"
    "\n"
    "  /// Desktop player-bar minimum height; `0` keeps the built-in 92.\n"
    "  final double playerBarHeight;\n"
    "\n"
    "  /// Compact player-bar minimum height; `0` keeps the built-in 56/60.\n"
    "  final double compactPlayerBarHeight;\n",
    "fields",
)

text = replace_once(
    text,
    "    'glassBlurSigma': glassBlurSigma,\n  };",
    "    'glassBlurSigma': glassBlurSigma,\n"
    "    'colors': <String, Object?>{\n"
    "      for (final entry in colors.entries)\n"
    "        entry.key: formatSkinColor(entry.value),\n"
    "    },\n"
    "    'railWidth': railWidth,\n"
    "    'playerBarHeight': playerBarHeight,\n"
    "    'compactPlayerBarHeight': compactPlayerBarHeight,\n"
    "  };",
    "toJson",
)

text = replace_once(
    text,
    "      glassBlurSigma: number('glassBlurSigma', 16, max: 48),\n    );",
    "      glassBlurSigma: number('glassBlurSigma', 16, max: 48),\n"
    "      colors: parseSkinColors(elements['colors']),\n"
    "      railWidth: number('railWidth', 0, max: 420),\n"
    "      playerBarHeight: number('playerBarHeight', 0, max: 200),\n"
    "      compactPlayerBarHeight: number('compactPlayerBarHeight', 0, max: 160),\n"
    "    );",
    "fromJson",
)

text = replace_once(
    text,
    "    double? controlRadius,\n    double? glassBlurSigma,\n  }) => LazerThemeTokens(",
    "    double? controlRadius,\n"
    "    double? glassBlurSigma,\n"
    "    Map<String, Color>? colors,\n"
    "    double? railWidth,\n"
    "    double? playerBarHeight,\n"
    "    double? compactPlayerBarHeight,\n"
    "  }) => LazerThemeTokens(",
    "copyWith params",
)

text = replace_once(
    text,
    "    glassBlurSigma: glassBlurSigma ?? this.glassBlurSigma,\n  );",
    "    glassBlurSigma: glassBlurSigma ?? this.glassBlurSigma,\n"
    "    colors: colors ?? this.colors,\n"
    "    railWidth: railWidth ?? this.railWidth,\n"
    "    playerBarHeight: playerBarHeight ?? this.playerBarHeight,\n"
    "    compactPlayerBarHeight:\n"
    "        compactPlayerBarHeight ?? this.compactPlayerBarHeight,\n"
    "  );",
    "copyWith body",
)

text = replace_once(
    text,
    "      controlRadius: mix(controlRadius, other.controlRadius),\n      glassBlurSigma: mix(glassBlurSigma, other.glassBlurSigma),\n    );",
    "      controlRadius: mix(controlRadius, other.controlRadius),\n"
    "      glassBlurSigma: mix(glassBlurSigma, other.glassBlurSigma),\n"
    "      colors: t < .5 ? colors : other.colors,\n"
    "      railWidth: mix(railWidth, other.railWidth),\n"
    "      playerBarHeight: mix(playerBarHeight, other.playerBarHeight),\n"
    "      compactPlayerBarHeight: mix(\n"
    "        compactPlayerBarHeight,\n"
    "        other.compactPlayerBarHeight,\n"
    "      ),\n"
    "    );",
    "lerp",
)

write(THEME, text)

# ---------------------------------------------------------------------------
# 2. apple_design.dart — merge skin colours over the preset
# ---------------------------------------------------------------------------
text = read(APPLE)

MERGE = r'''
/// Applies a skin's semantic colour overrides on top of a built-in preset.
///
/// Only the slots the skin actually supplies are replaced. When a skin sets
/// `label`/`background` but leaves the fill and separator roles out, those are
/// re-derived from the supplied ink so highlights and hairlines stay coherent
/// instead of inheriting the Apple tint.
AppleSemanticColors applySemanticColorOverrides(
  AppleSemanticColors base,
  Map<String, Color> overrides, {
  required bool dark,
}) {
  if (overrides.isEmpty) return base;
  final Color label = overrides['label'] ?? base.label;
  final Color background = overrides['background'] ?? base.background;
  final bool ink = overrides.containsKey('label');
  Color pick(String slot, [Color? fallback]) => overrides[slot] ?? fallback ?? base.label;
  return base.copyWith(
    background: background,
    secondaryBackground: pick(
      'secondaryBackground',
      overrides['background'] == null
          ? base.secondaryBackground
          : Color.alphaBlend(
              label.withValues(alpha: dark ? .08 : .03),
              background,
            ),
    ),
    tertiaryBackground: pick('tertiaryBackground', base.tertiaryBackground),
    groupedBackground: pick(
      'groupedBackground',
      overrides['background'] ?? base.groupedBackground,
    ),
    secondaryGroupedBackground: pick(
      'secondaryGroupedBackground',
      overrides['background'] == null
          ? base.secondaryGroupedBackground
          : Color.alphaBlend(
              label.withValues(alpha: dark ? .10 : .04),
              background,
            ),
    ),
    tertiaryGroupedBackground: pick(
      'tertiaryGroupedBackground',
      base.tertiaryGroupedBackground,
    ),
    label: label,
    secondaryLabel: pick(
      'secondaryLabel',
      ink ? label.withValues(alpha: .72) : base.secondaryLabel,
    ),
    tertiaryLabel: pick(
      'tertiaryLabel',
      ink ? label.withValues(alpha: .50) : base.tertiaryLabel,
    ),
    quaternaryLabel: pick(
      'quaternaryLabel',
      ink ? label.withValues(alpha: .30) : base.quaternaryLabel,
    ),
    fill: pick(
      'fill',
      ink ? label.withValues(alpha: dark ? .14 : .06) : base.fill,
    ),
    secondaryFill: pick(
      'secondaryFill',
      ink ? label.withValues(alpha: dark ? .10 : .04) : base.secondaryFill,
    ),
    tertiaryFill: pick(
      'tertiaryFill',
      ink ? label.withValues(alpha: dark ? .07 : .03) : base.tertiaryFill,
    ),
    separator: pick(
      'separator',
      ink ? label.withValues(alpha: .18) : base.separator,
    ),
    opaqueSeparator: pick(
      'opaqueSeparator',
      ink ? label.withValues(alpha: .32) : base.opaqueSeparator,
    ),
    accent: pick('accent', base.accent),
    accentSoft: pick('accentSoft', base.accentSoft),
    glass: pick(
      'glass',
      overrides['background'] == null
          ? base.glass
          : background.withValues(alpha: dark ? .62 : .72),
    ),
    glassStrong: pick(
      'glassStrong',
      overrides['background'] == null
          ? base.glassStrong
          : background.withValues(alpha: dark ? .82 : .88),
    ),
  );
}
'''

anchor = "/// Apple HIG type ramp with bundled MiSans on every platform."
text = replace_once(text, anchor, MERGE.lstrip("\n") + "\n" + anchor, "applySemanticColorOverrides")

text = replace_once(
    text,
    "  final AppleSemanticColors base = brightness == Brightness.dark\n"
    "      ? AppleSemanticColors.dark\n"
    "      : AppleSemanticColors.light;\n"
    "  final Color accent = seedAccent == null\n"
    "      ? base.accent\n"
    "      : adaptiveAccent(seedAccent, base.background);\n"
    "  final AppleSemanticColors apple = base.copyWith(\n"
    "    accent: accent,\n"
    "    accentSoft: accent.withValues(\n"
    "      alpha: brightness == Brightness.dark ? .18 : .12,\n"
    "    ),\n"
    "  );",
    "  final bool dark = brightness == Brightness.dark;\n"
    "  final AppleSemanticColors preset = dark\n"
    "      ? AppleSemanticColors.dark\n"
    "      : AppleSemanticColors.light;\n"
    "  // A Lua skin supplies semantic colours; the host keeps ownership of\n"
    "  // contrast, focus and every widget, it only honours the tones.\n"
    "  final AppleSemanticColors skinned = applySemanticColorOverrides(\n"
    "    preset,\n"
    "    ui.colors,\n"
    "    dark: dark,\n"
    "  );\n"
    "  final Color accent = seedAccent == null\n"
    "      ? (ui.colors['accent'] ?? skinned.accent)\n"
    "      : adaptiveAccent(seedAccent, skinned.background);\n"
    "  final AppleSemanticColors apple = skinned.copyWith(\n"
    "    accent: accent,\n"
    "    accentSoft:\n"
    "        ui.colors['accentSoft'] ??\n"
    "        accent.withValues(alpha: dark ? .18 : .12),\n"
    "  );",
    "buildAppleTheme colour merge",
)

write(APPLE, text)

# ---------------------------------------------------------------------------
# 3. player_bar.dart — height + glass blur from tokens
# ---------------------------------------------------------------------------
text = read(PLAYER)

text = replace_once(
    text,
    "  final AppleSemanticColors apple = AppleSemanticColors.of(context);\n"
    "    return AppleGlass(",
    "  final AppleSemanticColors apple = AppleSemanticColors.of(context);\n"
    "    final ui = LazerThemeTokens.of(context);\n"
    "    return AppleGlass(",
    "player bar tokens local",
)

text = replace_once(
    text,
    "      blurSigma: state.backgroundMode == AppBackgroundMode.windowsMica ? 0 : 16,\n"
    "      color: state.backgroundMode == AppBackgroundMode.windowsMica\n"
    "          ? apple.glassStrong.withValues(alpha: .58)\n"
    "          : apple.glassStrong,",
    "      blurSigma: state.backgroundMode == AppBackgroundMode.windowsMica\n"
    "          ? 0\n"
    "          : ui.glassBlurSigma,\n"
    "      color: state.backgroundMode == AppBackgroundMode.windowsMica\n"
    "          ? apple.glassStrong.withValues(alpha: .58)\n"
    "          : apple.glassStrong,",
    "player bar blur sigma",
)

text = replace_once(
    text,
    "        ConstrainedBox(\n          constraints: const BoxConstraints(minHeight: 92),",
    "        ConstrainedBox(\n"
    "          constraints: BoxConstraints(\n"
    "            minHeight: ui.playerBarHeight > 0 ? ui.playerBarHeight : 92,\n"
    "          ),",
    "player bar height",
)

write(PLAYER, text)

# ---------------------------------------------------------------------------
# 4. large_screen_pages.dart — rail width from tokens
# ---------------------------------------------------------------------------
text = read(PAGES)
text = replace_once(
    text,
    "    final double rail = LargeScreenMetrics.railWidth(width);",
    "    final double railToken = LazerThemeTokens.of(context).railWidth;\n"
    "    final double rail = railToken > 0\n"
    "        ? railToken\n"
    "        : LargeScreenMetrics.railWidth(width);",
    "rail width token",
)
write(PAGES, text)

print("\nall patches applied")
