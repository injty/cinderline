"""Check theme contrast, including alpha compositing. Python 3, no dependencies."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def rgba(value):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", value):
        raise ValueError(f"Invalid color: {value}")
    channels = tuple(int(value[i:i + 2], 16) / 255 for i in range(1, len(value), 2))
    return channels if len(channels) == 4 else (*channels, 1.0)


def over(foreground, background):
    """Source-over sRGB compositing onto an opaque background."""
    return tuple(foreground[i] * foreground[3] + background[i] * (1 - foreground[3])
                 for i in range(3)) + (1.0,)


def luminance(color):
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
              for v in color[:3]]
    return sum(v * w for v, w in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(foreground, background):
    values = sorted((luminance(over(foreground, background)), luminance(background)))
    return (values[1] + 0.05) / (values[0] + 0.05)


def main():
    family = json.loads((ROOT / "themes/cinderline.json").read_text(encoding="utf-8"),
                        object_pairs_hook=unique_object)
    assert len(family["themes"]) == 1
    theme = family["themes"][0]
    assert theme["appearance"] == "dark"
    style = theme["style"]
    syntax = style["syntax"]
    colors = []

    def inspect(value):
        if isinstance(value, dict):
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
        elif isinstance(value, str) and value.startswith("#"):
            rgba(value)
            colors.append(value.upper())

    inspect(style)
    for color in colors:
        red, _, blue, _ = rgba(color)
        assert blue <= red, f"Unexpected blue/cyan undertone: {color}"
    css = (ROOT / "palette.css").read_text(encoding="utf-8")
    for color in re.findall(r"#[0-9a-fA-F]{6,8}\b", css):
        assert color.upper() in colors, f"Palette color missing from theme: {color}"

    results = []
    failures = []

    def check(label, foreground, background, minimum=4.5):
        ratio = contrast(rgba(foreground), background)
        results.append((ratio, label))
        if ratio < minimum:
            failures.append(f"{label}: {ratio:.2f}:1 < {minimum}:1")

    editor = rgba(style["editor.background"])
    active = over(rgba(style["editor.active_line.background"]), editor)
    backgrounds = {"editor": editor, "active line": active}
    overlays = ["search.match_background", "search.active_match_background",
                "editor.document_highlight.read_background",
                "editor.document_highlight.write_background",
                "editor.document_highlight.bracket_background",
                "editor.highlighted_line.background", "editor.debugger_active_line.background",
                "editor.diff_hunk.added.background", "editor.diff_hunk.deleted.background",
                "version_control.word_added", "version_control.word_deleted"]
    for key in overlays:
        backgrounds[key] = over(rgba(style[key]), active)
    for index, player in enumerate(style["players"]):
        backgrounds[f"selection {index + 1}"] = over(rgba(player["selection"]), active)

    for name, token in syntax.items():
        for state, bg in backgrounds.items():
            # Ghost completion is intentionally subordinate to actual source text.
            check(f"syntax.{name} / {state}", token["color"], bg,
                  3.0 if name == "predictive" else 4.5)

    for state in ("background", "surface.background", "elevated_surface.background",
                  "element.hover", "element.active", "element.selected"):
        for key in ("text", "text.muted", "text.placeholder", "text.accent"):
            check(f"{key} / {state}", style[key], rgba(style[state]))
    for name in ("error", "warning", "success", "info", "hint", "created", "deleted"):
        bg = over(rgba(style[name + ".background"]), rgba(style["elevated_surface.background"]))
        check(name, style[name], bg)

    for key, color in style.items():
        if key.startswith("terminal.ansi."):
            suffix = key.removeprefix("terminal.ansi.")
            if suffix in ("background", "black", "dim_black"):
                continue  # ANSI black also serves as a background color.
            check(key, color, rgba(style["terminal.background"]),
                  3.0 if suffix.startswith("dim_") else 4.5)
        if key.startswith("vim.") and key.endswith(".foreground"):
            bg_key = key.removesuffix("foreground") + "background"
            if bg_key in style:
                check(key, color, rgba(style[bg_key]))

    # Multiple overlapping decorations are rarer, but text must still be legible.
    selection = rgba(style["players"][0]["selection"])
    for key in ("search.active_match_background", "version_control.word_added",
                "version_control.word_deleted"):
        bg = over(selection, backgrounds[key])
        for name, token in syntax.items():
            if name != "predictive":
                check(f"syntax.{name} / selection + {key}", token["color"], bg, 3.0)

    print(f"{theme['name']}: {len(style)} style entries, {len(syntax)} syntax captures")
    print(f"Valid colors: {len(colors)}; contrast pairs: {len(results)}")
    for key in ("editor.foreground", "text.accent"):
        print(f"{key}: {contrast(rgba(style[key]), editor):.2f}:1")
    print(f"comment: {contrast(rgba(syntax['comment']['color']), editor):.2f}:1")
    if failures:
        raise SystemExit("FAILED\n" + "\n".join(failures))
    print("PASS: colors, duplicate keys, palette consistency, contrast and overlays")


if __name__ == "__main__":
    main()
