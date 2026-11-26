"""Check theme contrast, including alpha compositing. Python 3, no dependencies."""

import json
import re
from itertools import combinations
from math import dist

from build import Palette, ROOT, unique_object


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
    palette = Palette()
    for key, value in palette.colors.items():
        r, g, b, _ = rgba(value)
        assert not (b > r and b >= g), f"Blue hue in the global palette: {key}"
    for color in colors:
        assert color[:7] in palette.colors.values(), f"Color outside global palette: {color}"
    for name, token in syntax.items():
        assert token["font_style"] == "normal", f"Not upright: {name}"
    assert syntax["emphasis.strong"]["font_weight"] >= 600
    for key in ("property", "property.json_key", "variable.member", "field"):
        assert syntax[key]["color"] == style["editor.foreground"], f"Tinted property: {key}"
    assert len({syntax[key]["color"] for key in (
        "variable", "variable.parameter", "function", "type", "keyword",
        "string", "number", "comment")}) == 8, "Core syntax roles collapsed"

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
    for name in ("error", "warning", "success", "info", "hint", "created", "deleted",
                 "modified", "renamed", "conflict"):
        bg = over(rgba(style[name + ".background"]), rgba(style["elevated_surface.background"]))
        check(name, style[name], bg)

    states = ("modified", "created", "deleted", "renamed", "conflict")
    assert style["modified"] == palette.resolve("orange")
    assert style["warning"] == syntax["constant"]["color"] != style["error"]
    assert luminance(rgba(style["warning"])) > luminance(rgba(style["modified"]))
    assert style["error"] == palette.resolve("terracotta")
    # Contrast against the panel alone would allow silver modified vs. white clean.
    # Guard against near-identical foregrounds (sRGB distance, not a WCAG metric).
    for a, b in combinations(("text", *states), 2):
        assert dist(rgba(style[a])[:3], rgba(style[b])[:3]) > 0.12, f"File colors too close: {a}, {b}"
    panel = rgba(style["panel.background"])
    for state in ("panel.background", "element.hover", "element.selected",
                  "ghost_element.hover", "ghost_element.selected"):
        bg = over(rgba(style[state]), panel)
        for key in (*states, "warning", "error"):
            check(f"file {key} / {state}", style[key], bg)
        check(f"file ignored / {state}", style["ignored"], bg, 2.8)
    assert luminance(rgba(style["ignored"])) < luminance(rgba(style["text.muted"])) * 0.5
    for vcs, state in (("added", "created"), ("modified", "modified"), ("deleted", "deleted"),
                       ("renamed", "renamed"), ("conflict", "conflict"), ("ignored", "ignored")):
        assert style[f"version_control.{vcs}"] == style[state], f"Inconsistent Git color: {vcs}"
    for key in ("version_control.added", "version_control.modified", "version_control.deleted"):
        check(f"gutter {key}", style[key], editor, 3.0)
    for key in ("editor.diff_hunk.added.background", "editor.diff_hunk.deleted.background",
                "version_control.word_added", "version_control.word_deleted",
                "search.match_background", "search.active_match_background"):
        check(f"visible overlay {key}", style[key], active, 1.15)
    for key in ("editor.diff_hunk.added.hollow_border", "editor.diff_hunk.deleted.hollow_border"):
        check(f"diff border {key}", style[key], active, 3.0)
    for change in ("added", "deleted"):
        line = backgrounds[f"editor.diff_hunk.{change}.background"]
        word = style[f"version_control.word_{change}"]
        check(f"changed word visible on {change} line", word, line, 1.35)
        for name, token in syntax.items():
            check(f"{name} / {change} word on line", token["color"], over(rgba(word), line), 3.0)

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
