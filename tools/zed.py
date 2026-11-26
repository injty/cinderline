"""Map Cinderline palette roles to Zed UI and syntax tokens."""

# Multiple captures from Tree-sitter queries and LSP rules can describe the same role.
SYNTAX = {
    "text": "variable embedded primary parent",
    "text-bright": "emphasis.strong",
    "linen": "emphasis",
    "parameter": "parameter variable.parameter",
    "property": "property property.json_key variable.member field",
    "attribute": "attribute tag.attribute",
    "namespace": "namespace module function.decorator function.annotation decorator",
    "function": "function function.call function.method function.method.call link_uri",
    "brushed-bronze": "function.builtin selector selector.pseudo",
    "type": ("type type.definition type.class type.class.definition type.interface "
             "type.interface.definition type.enum type.enum.definition type.struct "
             "type.struct.definition type.parameter type.parameter.definition type.event "
             "type.super concept enum constructor"),
    "amber": "type.builtin function.macro constant.macro preproc keyword.directive keyword.directive.define label",
    "constant": "constant",
    "literal": ("constant.builtin boolean number number.float float variant type.enum.member "
                "variable.special variable.builtin symbol string.special.symbol punctuation.special.symbol"),
    "keyword": ("keyword keyword.type keyword.function keyword.import keyword.export keyword.coroutine "
                "keyword.repeat keyword.return keyword.debug keyword.exception keyword.conditional "
                "keyword.conditional.ternary tag title punctuation.list_marker punctuation.markup"),
    "peach": "keyword.modifier",
    "operator": "operator keyword.operator",
    "text-muted": "punctuation punctuation.delimiter punctuation.bracket tag.delimiter tag.doctype predictive",
    "comment": "comment comment.doc comment.documentation predoc",
    "hint": "hint comment.hint",
    "info": "comment.info comment.note",
    "error": "comment.error",
    "warning": "comment.warning comment.warn comment.todo",
    "string": "string string.doc string.documentation character text.literal",
    "escape": "string.escape character.special punctuation.special string.special",
    "regex": "string.regex string.regexp",
    "pale-copper": "string.special.path string.special.url link_text",
    "added": "diff.plus",
    "deleted": "diff.minus",
    "modified": "diff.delta",
}

UI = {
    "base": ("background title_bar.background title_bar.inactive_background status_bar.background "
             "tab_bar.background tab.inactive_background panel.background"),
    "editor": ("toolbar.background tab.active_background editor.background editor.gutter.background "
               "terminal.background terminal.ansi.background"),
    "surface": ("surface.background element.disabled panel.overlay_background editor.subheader.background "
                "editor.active_line.background"),
    "elevated": "elevated_surface.background element.background",
    "border": "border hidden.border ignored.border predictive.border unreachable.border",
    "divider": "border.variant pane_group.border panel.indent_guide",
    "focus": "border.focused drop_target.border text.accent icon.accent editor.active_line_number link_text.hover",
    "guide-active": "border.selected panel.indent_guide_active",
    "guide-hover": "panel.indent_guide_hover",
    "guide-focus": "panel.focused_border pane.focused_border hint.border",
    "border-disabled": "border.disabled",
    "black/00": ("border.transparent ghost_element.background ghost_element.disabled scrollbar.thumb.border "
                 "scrollbar.track.background scrollbar.track.border"),
    "hover": "element.hover panel.overlay_hover",
    "pressed": "element.active",
    "selected": "element.selected",
    "selection": "element.selection_background editor.document_highlight.bracket_background vim.yank.background",
    "chalk/0A": "ghost_element.hover",
    "silver/1A": "ghost_element.active",
    "read-highlight": "ghost_element.selected drop_target.background editor.document_highlight.read_background",
    "text": "text editor.foreground terminal.foreground",
    "text-muted": ("text.muted text.placeholder icon.muted icon.placeholder editor.code_lens.foreground "
                   "predictive unreachable terminal.dim_foreground"),
    "text-disabled": "text.disabled icon.disabled editor.line_number hidden",
    "text-bright": "terminal.bright_foreground",
    "silver": "icon editor.hover_line_number",
    "error": "debugger.accent",
    "ash/30": "scrollbar.thumb.background minimap.thumb.border",
    "ash/50": "scrollbar.thumb.hover_background",
    "silver/60": "scrollbar.thumb.active_background",
    "ash/14": "minimap.thumb.background",
    "ash/24": "minimap.thumb.hover_background",
    "silver/30": "minimap.thumb.active_background",
    "silver/0E": "editor.highlighted_line.background",
    "silver/18": "editor.debugger_active_line.background",
    "invisible": "editor.invisible",
    "chalk/0C": "editor.wrap_guide",
    "chalk/20": "editor.active_wrap_guide",
    "chalk/12": "editor.indent_guide",
    "silver/50": "editor.indent_guide_active",
    "write-highlight": "editor.document_highlight.write_background",
    "search": "search.match_background",
    "search-active": "search.active_match_background",
    "diff-add-line": "editor.diff_hunk.added.background",
    "diff-delete-line": "editor.diff_hunk.deleted.background",
    "diff-add-word": "version_control.word_added",
    "diff-delete-word": "version_control.word_deleted",
    "brushed-bronze/32": "version_control.conflict_marker.ours",
    "mauve/32": "version_control.conflict_marker.theirs",
    "ash/0A": "hidden.background ignored.background predictive.background unreachable.background",
    "hint/12": "hint.background",
}


def build(resolve):
    style = {"background.appearance": "opaque"}
    for role, keys in UI.items():
        style.update(dict.fromkeys(keys.split(), resolve(role)))
    for vcs in ("added", "modified", "deleted", "renamed", "conflict", "ignored"):
        style["version_control." + vcs] = resolve(vcs)
    for state in ("created", "modified", "deleted", "renamed", "conflict", "success",
                  "warning", "error", "info", "ignored", "hint"):
        role = "added" if state == "created" else state
        style[state] = resolve(role)
        if state not in ("ignored", "hint"):
            for suffix, alpha in (("background", "18"), ("border", "80")):
                style[f"{state}.{suffix}"] = resolve(f"{role}/{alpha}")
    for hunk, role in (("added", "added"), ("deleted", "deleted")):
        for suffix, alpha in (("hollow_background", "14"), ("hollow_border", "AB")):
            style[f"editor.diff_hunk.{hunk}.{suffix}"] = resolve(f"{role}/{alpha}")
    for level in ("", "bright_", "dim_"):
        for color in "black red green yellow blue magenta cyan white".split():
            slot = level + color
            style["terminal.ansi." + slot] = resolve("ansi-" + slot.replace("_", "-"))
    for mode, role in (("normal", "vim-normal"), ("insert", "sage"), ("replace", "terracotta"),
                       ("visual", "orange"), ("visual_line", "orange"), ("visual_block", "orange"),
                       ("helix_normal", "orange"), ("helix_select", "orange")):
        style[f"vim.{mode}.background"] = resolve(role)
        style[f"vim.{mode}.foreground"] = resolve("on-accent")
    style["vim.helix_jump_label.foreground"] = resolve("orange")
    accents = "orange pale-copper sage terracotta amber mauve brushed-bronze silver".split()
    style["accents"] = [resolve(key) for key in accents]
    style["players"] = [{"cursor": resolve(key), "background": resolve(key),
                         "selection": resolve(key + "/20" if i else "selection")}
                        for i, key in enumerate(accents)]
    syntax = {name: {"color": resolve(role), "font_style": "normal"}
              for role, names in SYNTAX.items() for name in names.split()}
    syntax["emphasis.strong"]["font_weight"] = 700
    syntax["title"]["font_weight"] = 600
    style["syntax"] = dict(sorted(syntax.items()))
    return {"$schema": "https://zed.dev/schema/themes/v0.2.0.json",
            "name": "Cinderline", "author": "Nijat",
            "themes": [{"name": "Cinderline", "appearance": "dark", "style": style}]}
