"""Generate the VS Code theme from the Zed source, without dependencies."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "themes/cinderline.json"
OUTPUT = ROOT / "vscode-theme/themes/cinderline-color-theme.json"

# Zed style token -> one or more VS Code UI color IDs.
COLORS = {
    "background": "activityBar.background sideBar.background panel.background",
    "title_bar.background": "titleBar.activeBackground titleBar.inactiveBackground",
    "status_bar.background": "statusBar.background statusBar.noFolderBackground statusBar.debuggingBackground statusBarItem.remoteBackground",
    "tab_bar.background": "editorGroupHeader.tabsBackground",
    "tab.inactive_background": "tab.inactiveBackground tab.unfocusedInactiveBackground",
    "tab.active_background": "tab.activeBackground tab.unfocusedActiveBackground editorGroup.emptyBackground",
    "toolbar.background": "breadcrumb.background",
    "surface.background": "editorStickyScroll.background peekViewEditor.background",
    "elevated_surface.background": "menu.background dropdown.background input.background quickInput.background editorWidget.background editorHoverWidget.background editorSuggestWidget.background notifications.background peekViewResult.background",
    "border": "input.border dropdown.border menu.border editorWidget.border editorHoverWidget.border editorSuggestWidget.border notifications.border widget.border peekView.border",
    "border.variant": "activityBar.border sideBar.border panel.border statusBar.border titleBar.border editorGroup.border editorGroupHeader.tabsBorder tab.border editorOverviewRuler.border notificationCenterHeader.background",
    "border.focused": "focusBorder list.focusOutline",
    "drop_target.background": "list.dropBackground editorGroup.dropBackground",
    "element.hover": "list.hoverBackground toolbar.hoverBackground button.secondaryHoverBackground menu.selectionBackground",
    "element.selected": "list.activeSelectionBackground list.inactiveSelectionBackground quickInputList.focusBackground editorSuggestWidget.selectedBackground",
    "element.active": "toolbar.activeBackground",
    "element.background": "button.secondaryBackground badge.background",
    "ghost_element.hover": "statusBarItem.hoverBackground",
    "ghost_element.active": "statusBarItem.activeBackground",
    "text": "foreground editor.foreground sideBar.foreground sideBarTitle.foreground titleBar.activeForeground statusBar.foreground statusBar.noFolderForeground statusBar.debuggingForeground statusBarItem.remoteForeground tab.activeForeground tab.unfocusedActiveForeground list.activeSelectionForeground list.inactiveSelectionForeground quickInputList.focusForeground input.foreground button.secondaryForeground menu.foreground menu.selectionForeground dropdown.foreground badge.foreground editorSuggestWidget.selectedForeground",
    "text.muted": "descriptionForeground titleBar.inactiveForeground tab.inactiveForeground tab.unfocusedInactiveForeground breadcrumb.foreground input.placeholderForeground sideBarSectionHeader.foreground activityBar.inactiveForeground",
    "text.disabled": "disabledForeground",
    "icon": "icon.foreground activityBar.foreground editorBracketHighlight.foreground1 editorBracketHighlight.foreground3 editorBracketHighlight.foreground5",
    "text.accent": "activityBar.activeBorder tab.activeBorderTop panelTitle.activeBorder progressBar.background activityBarBadge.background button.background button.hoverBackground list.highlightForeground list.focusHighlightForeground editorSuggestWidget.highlightForeground textLink.foreground textLink.activeForeground",
    "panel.overlay_background": "sideBarSectionHeader.background",
    "panel.indent_guide": "tree.inactiveIndentGuidesStroke",
    "panel.indent_guide_active": "tree.indentGuidesStroke",
    "scrollbar.thumb.background": "scrollbarSlider.background",
    "scrollbar.thumb.hover_background": "scrollbarSlider.hoverBackground",
    "scrollbar.thumb.active_background": "scrollbarSlider.activeBackground",
    "minimap.thumb.background": "minimapSlider.background",
    "minimap.thumb.hover_background": "minimapSlider.hoverBackground",
    "minimap.thumb.active_background": "minimapSlider.activeBackground",
    "editor.background": "editor.background button.foreground activityBarBadge.foreground",
    "editor.gutter.background": "editorGutter.background",
    "editor.active_line.background": "editor.lineHighlightBackground",
    "editor.highlighted_line.background": "editor.rangeHighlightBackground",
    "editor.debugger_active_line.background": "editor.stackFrameHighlightBackground",
    "editor.line_number": "editorLineNumber.foreground",
    "text.placeholder": "editorBracketHighlight.foreground2 editorBracketHighlight.foreground4 editorBracketHighlight.foreground6",
    "editor.active_line_number": "editorLineNumber.activeForeground",
    "editor.code_lens.foreground": "editorCodeLens.foreground",
    "editor.invisible": "editorWhitespace.foreground",
    "editor.wrap_guide": "editorRuler.foreground",
    "editor.document_highlight.read_background": "editor.wordHighlightBackground editor.wordHighlightTextBackground editor.inactiveSelectionBackground",
    "editor.document_highlight.write_background": "editor.wordHighlightStrongBackground",
    "editor.document_highlight.bracket_background": "editorBracketMatch.background",
    "border.selected": "editorBracketMatch.border",
    "element.selection_background": "editor.selectionBackground editor.selectionHighlightBackground terminal.selectionBackground minimap.selectionHighlight",
    "search.match_background": "editor.findMatchHighlightBackground terminal.findMatchHighlightBackground",
    "search.active_match_background": "editor.findMatchBackground terminal.findMatchBackground minimap.findMatchHighlight",
    "predictive": "editorGhostText.foreground",
    "hint": "editorHint.foreground editorInlayHint.foreground",
    "hint.background": "editorInlayHint.background",
    "editor.diff_hunk.added.background": "diffEditor.insertedLineBackground",
    "editor.diff_hunk.deleted.background": "diffEditor.removedLineBackground",
    "version_control.word_added": "diffEditor.insertedTextBackground",
    "version_control.word_deleted": "diffEditor.removedTextBackground",
    "version_control.added": "gitDecoration.addedResourceForeground gitDecoration.untrackedResourceForeground editorGutter.addedBackground minimapGutter.addedBackground editorOverviewRuler.addedForeground",
    "version_control.modified": "gitDecoration.modifiedResourceForeground gitDecoration.stageModifiedResourceForeground editorGutter.modifiedBackground minimapGutter.modifiedBackground editorOverviewRuler.modifiedForeground",
    "version_control.deleted": "gitDecoration.deletedResourceForeground gitDecoration.stageDeletedResourceForeground editorGutter.deletedBackground minimapGutter.deletedBackground editorOverviewRuler.deletedForeground",
    "version_control.renamed": "gitDecoration.renamedResourceForeground",
    "version_control.conflict": "gitDecoration.conflictingResourceForeground",
    "version_control.ignored": "gitDecoration.ignoredResourceForeground",
    "version_control.conflict_marker.ours": "merge.currentContentBackground",
    "version_control.conflict_marker.theirs": "merge.incomingContentBackground",
    "created.border": "merge.currentHeaderBackground",
    "deleted.border": "merge.incomingHeaderBackground",
    "error": "errorForeground editorError.foreground list.errorForeground problemsErrorIcon.foreground notificationsErrorIcon.foreground minimap.errorHighlight editorOverviewRuler.errorForeground editorBracketHighlight.unexpectedBracket.foreground",
    "warning": "editorWarning.foreground list.warningForeground problemsWarningIcon.foreground notificationsWarningIcon.foreground minimap.warningHighlight editorOverviewRuler.warningForeground",
    "info": "editorInfo.foreground problemsInfoIcon.foreground notificationsInfoIcon.foreground editorOverviewRuler.infoForeground",
    "debugger.accent": "debugIcon.breakpointForeground",
    "terminal.background": "terminal.background",
    "terminal.foreground": "terminal.foreground",
}

# More specific TextMate scopes override their generic parent scopes.
TEXTMATE = {
    "comment": "comment punctuation.definition.comment",
    "string": "string string.quoted string.template",
    "string.regex": "string.regexp",
    "string.escape": "constant.character.escape",
    "string.special.symbol": "constant.other.symbol",
    "number": "constant.numeric",
    "boolean": "constant.language.boolean",
    "constant": "constant",
    "constant.builtin": "constant.language",
    "keyword": "keyword storage storage.modifier",
    "operator": "keyword.operator",
    "preproc": "meta.preprocessor keyword.control.directive",
    "type": "entity.name.type entity.name.class entity.other.inherited-class storage.type.support",
    "type.builtin": "support.type support.class storage.type.primitive",
    "enum": "variable.other.enummember entity.name.type.enum",
    "function": "entity.name.function support.function variable.function meta.function-call.generic",
    "constructor": "entity.name.function.constructor",
    "property": "variable.other.property variable.other.object.property support.type.property-name meta.object-literal.key",
    "property.json_key": "support.type.property-name.json string.json support.type.property-name.toml entity.name.tag.yaml",
    "variable": "variable",
    "variable.parameter": "variable.parameter",
    "variable.special": "variable.language",
    "namespace": "entity.name.namespace entity.name.module",
    "attribute": "entity.other.attribute-name",
    "selector": "entity.other.attribute-name.class.css entity.other.attribute-name.id.css entity.name.tag.css",
    "selector.pseudo": "entity.other.attribute-name.pseudo-class.css entity.other.attribute-name.pseudo-element.css",
    "tag": "entity.name.tag punctuation.definition.tag",
    "tag.doctype": "meta.tag.sgml.doctype",
    "punctuation": "punctuation",
    "punctuation.special": "punctuation.definition.template-expression",
    "punctuation.list_marker": "punctuation.definition.list",
    "punctuation.markup": "punctuation.definition.heading punctuation.definition.quote",
    "embedded": "meta.embedded source.embedded",
    "title": "markup.heading entity.name.section",
    "emphasis": "markup.italic",
    "emphasis.strong": "markup.bold",
    "link_text": "string.other.link.title markup.underline.link",
    "link_uri": "markup.underline.link.image meta.link.inline.markdown markup.underline.link.markdown",
    "text.literal": "markup.inline.raw markup.fenced_code",
    "diff.plus": "markup.inserted",
    "diff.minus": "markup.deleted",
}

SEMANTIC = {
    "variable": "variable",
    "variable.readonly": "constant",
    "variable.defaultLibrary": "variable.special",
    "parameter": "variable.parameter",
    "property": "property",
    "function": "function",
    "method": "function.method",
    "class": "type",
    "interface": "type",
    "type": "type",
    "typeParameter": "type",
    "struct": "type",
    "enum": "enum",
    "enumMember": "variant",
    "namespace": "namespace",
    "decorator": "attribute",
    "macro": "preproc",
    "keyword": "keyword",
    "modifier": "keyword",
    "operator": "operator",
    "string": "string",
    "regexp": "string.regex",
    "number": "number",
    "comment": "comment",
}


def build_theme(zed):
    syntax = zed["syntax"]
    colors = {key: zed[token] for token, keys in COLORS.items() for key in keys.split()}
    colors["editorCursor.foreground"] = zed["players"][0]["cursor"]
    for level in range(1, 7):
        colors[f"editorIndentGuide.background{level}"] = zed["editor.indent_guide"]
        colors[f"editorIndentGuide.activeBackground{level}"] = zed["editor.indent_guide_active"]
    for color in "Black Red Green Yellow Blue Magenta Cyan White".split():
        colors[f"terminal.ansi{color}"] = zed[f"terminal.ansi.{color.lower()}"]
        colors[f"terminal.ansiBright{color}"] = zed[f"terminal.ansi.bright_{color.lower()}"]

    token_colors = []
    for token, scopes in TEXTMATE.items():
        source = syntax[token]
        settings = {"foreground": source["color"]}
        styles = []
        if source.get("font_style") == "italic":
            styles.append("italic")
        if source.get("font_weight", 0) >= 600:
            styles.append("bold")
        if styles or "font_style" in source:
            settings["fontStyle"] = " ".join(styles)
        token_colors.append({"name": token, "scope": scopes.split(), "settings": settings})

    return {
        "$schema": "vscode://schemas/color-theme",
        "name": "Cinderline",
        "type": "dark",
        "colors": dict(sorted(colors.items())),
        "tokenColors": token_colors,
        "semanticHighlighting": True,
        "semanticTokenColors": {key: syntax[token]["color"] for key, token in SEMANTIC.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the generated theme is stale")
    args = parser.parse_args()
    family = json.loads(SOURCE.read_text(encoding="utf-8"))
    zed = next(theme for theme in family["themes"] if theme["name"] == "Cinderline")
    generated = json.dumps(build_theme(zed["style"]), indent=2) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != generated:
            parser.exit(1, "VS Code theme is stale. Run python tools/vscode.py.\n")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(generated, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
