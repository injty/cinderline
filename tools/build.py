"""Build the portable palette exports and editor themes. Requires Python 3.10+."""

import argparse
import json
import re
from pathlib import Path
from string import Template

import preview
import vscode
import zed

ROOT = Path(__file__).resolve().parents[1]


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"Duplicate JSON key: {key}")
        obj[key] = value
    return obj


class Palette:
    def __init__(self):
        source = json.loads((ROOT / "palette.json").read_text(encoding="utf-8"),
                            object_pairs_hook=unique_object)
        self.colors, self.roles = source["colors"], source["roles"]
        if self.colors.keys() & self.roles.keys():
            raise ValueError("Palette roles must not shadow colors")
        for color in self.colors.values():
            if not re.fullmatch("#[0-9A-F]{6}", color):
                raise ValueError(f"Expected opaque sRGB color, got {color}")

    def resolve(self, expr, seen=()):
        key, sep, alpha = expr.partition("/")
        if key in seen:
            raise ValueError(f"Cyclic palette alias: {' -> '.join((*seen, key))}")
        value = (self.colors[key] if key in self.colors
                 else self.resolve(self.roles[key], (*seen, key)))
        if sep and (len(value) != 7 or not re.fullmatch("[0-9A-F]{2}", alpha)):
            raise ValueError(f"Invalid alpha in {expr}")
        return value + alpha

    def css(self):
        lines = ["/* Generated from palette.json by tools/build.py. */", ":root {", "  color-scheme: dark;"]
        for key in (*self.colors, *self.roles):
            value = self.resolve(key)
            if key in self.roles and "/" not in self.roles[key]:
                value = f"var(--cinderline-{self.roles[key]})"
            lines.append(f"  --cinderline-{key}: {value};")
        return "\n".join([*lines, "}", ""])


def opaque(color, background):
    if len(color) == 7:
        return color
    alpha = int(color[7:], 16) / 255
    return "#" + "".join(f"{round(int(color[i:i+2], 16) * alpha + int(background[i:i+2], 16) * (1-alpha)):02X}"
                         for i in (1, 3, 5))


def nvim(p):
    template = (ROOT / "tools/nvim.lua.in").read_text(encoding="utf-8")
    rows = []
    for key in sorted(set(re.findall(r"\bp\.(\w+)", template))):
        # 'function' is a Lua keyword.
        role = "function" if key == "callable" else key.replace("_", "-")
        rows.append(f'  {key} = "{opaque(p.resolve(role), p.resolve("editor"))}",')
    ansi = ["  " + ", ".join(f'"{p.resolve(f"ansi-{level}{c}")}"' for c in
                             "black red green yellow blue magenta cyan white".split()) + ","
            for level in ("", "bright-")]
    return Template(template).substitute(palette="\n".join(rows), ansi="\n".join(ansi))


def outputs():
    p = Palette()
    theme = zed.build(p.resolve)
    style = theme["themes"][0]["style"]
    return {
        "palette.css": p.css(),
        "themes/cinderline.json": json.dumps(theme, indent=2) + "\n",
        "vscode-theme/themes/cinderline-color-theme.json": json.dumps(vscode.build_theme(style), indent=2) + "\n",
        "nvim-theme/cinderline.lua": nvim(p),
        "preview.html": preview.render(style),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report stale files without writing")
    args = parser.parse_args()
    stale = []
    for name, content in outputs().items():
        path = ROOT / name
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        stale.append(name)
        if not args.check:
            path.write_text(content, encoding="utf-8", newline="\n")
    if args.check and stale:
        parser.exit(1, "Out of date: " + ", ".join(stale) + ". Run python tools/build.py\n")
    print("Updated: " + ", ".join(stale) if stale else "All palette exports are current.")


if __name__ == "__main__":
    main()
