"""Generate a standalone HTML color study from the actual Zed theme tokens."""

import html
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
STYLE = json.loads((ROOT / "themes/ember-room.json").read_text(encoding="utf-8"))["themes"][0]["style"]


def token(capture, text):
    color = STYLE["syntax"][capture]["color"]
    return f'<span style="color:{color}">{html.escape(text)}</span>'


def line(*parts, active=False):
    content = "".join(token(*part) if isinstance(part, tuple) else html.escape(part) for part in parts)
    return f'<div class="line{" active" if active else ""}">{content or " "}</div>'


code = "".join([
    line(("comment.doc", "/** A quiet workspace, lit by a single warm lamp. */")),
    line(("keyword", "type "), ("type", "Material"), " = ", ("string", '"charcoal"'), " | ",
         ("string", '"copper"'), " | ", ("string", '"oak"'), ";"),
    line(),
    line(("keyword", "interface "), ("type", "Room"), " {"),
    line("  ", ("property", "name"), ": ", ("type", "string"), ";"),
    line("  ", ("property", "temperature"), ": ", ("type", "number"), ";"),
    line("  ", ("property", "materials"), ": ", ("type", "Material"), "[];"),
    line("}"),
    line(),
    line(("keyword", "const "), ("constant", "EVENING_KELVIN"), " = ", ("number", "2700"), ";"),
    line(),
    line(("keyword", "export function "), ("function", "createRoom"), "(",
         ("variable.parameter", "name"), ": ", ("type", "string"), "): ", ("type", "Room"), " {", active=True),
    line("  ", ("comment", "// Leave room for the things that matter.")),
    line("  ", ("keyword", "return"), " {"),
    line("    ", ("property", "name"), ","),
    line("    ", ("property", "temperature"), ": ", ("constant", "EVENING_KELVIN"), ","),
    line("    ", ("property", "materials"), ": [", ("string", '"charcoal"'), ", ",
         ("string", '"copper"'), ", ", ("string", '"oak"'), "],"),
    line("  };"),
    line("}"),
])

variables = {
    "base": "background", "editor": "editor.background", "surface": "surface.background",
    "elevated": "elevated_surface.background", "border": "border.variant",
    "text": "text", "muted": "text.muted", "accent": "text.accent",
    "selected": "element.selected", "line": "editor.active_line.background",
    "number": "editor.line_number", "green": "success", "red": "error", "amber": "warning",
    "blue": "info", "search": "search.active_match_background",
}
css = "\n".join(f"--{name}: {STYLE[key]};" for name, key in variables.items())
css += f"\n--selection: {STYLE['players'][0]['selection']};"
swatches = "".join(
    f'<div class="swatch"><i style="background:{STYLE[key]}"></i>'
    f'<span>{name}</span><code>{STYLE[key]}</code></div>'
    for name, key in [("Charcoal", "background"), ("Graphite", "editor.background"),
                      ("Silver", "text"), ("Ember", "text.accent"),
                      ("Sand", "warning"), ("Sage", "success"),
                      ("Slate", "info"), ("Rose", "error")]
)
ansi = "".join(
    '<div class="ansi-row">' + "".join(
        f'<i title="{prefix}{name}" style="background:{STYLE["terminal.ansi." + prefix + name]}"></i>'
        for name in ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
    ) + "</div>" for prefix in ("", "bright_")
)

page = Template('''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>Ember Room — color study</title>
<style>
:root { $css }
* { box-sizing: border-box; }
body { margin: 0; background: var(--base); color: var(--text); font: 14px/1.6 "Segoe UI", sans-serif; }
main { max-width: 1232px; margin: 0 auto; padding: 52px 36px 32px; }
header { display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; margin-bottom: 28px; }
.eyebrow { color: var(--accent); font: 11px "Cascadia Code", Consolas, monospace; letter-spacing: .2em; }
h1 { font: 52px/1.1 Georgia, serif; letter-spacing: -.04em; margin: 14px 0 10px; }
h1 span { color: var(--accent); }
header p { color: var(--muted); margin: 0; }
.edition { color: var(--muted); text-align: right; font-size: 12px; }
.edition strong { display: block; color: var(--text); font-weight: 400; }
.window { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.titlebar { height: 39px; display: flex; align-items: center; justify-content: space-between; padding: 0 16px; color: var(--muted); border-bottom: 1px solid var(--border); font-size: 12px; }
.titlebar b { color: var(--accent); font-weight: 400; }
.workspace { display: grid; grid-template-columns: 190px minmax(0, 1fr); }
aside { padding: 18px 9px; border-right: 1px solid var(--border); color: var(--muted); }
.folder { padding: 6px 10px; color: var(--text); }
.file { padding: 5px 12px 5px 25px; font-size: 13px; }
.file.chosen { background: var(--selected); color: var(--text); border-radius: 4px; }
.file small { float: right; color: var(--amber); }
.file .ts { color: var(--blue); margin-right: 9px; }
.side-label { padding: 24px 10px 7px; font-size: 10px; letter-spacing: .12em; }
.side-note { padding: 4px 10px; font-size: 12px; color: var(--muted); }
.editor { background: var(--editor); min-width: 0; }
.tabs { display: flex; background: var(--base); border-bottom: 1px solid var(--border); font-size: 12px; }
.tab { padding: 10px 20px; color: var(--muted); border-right: 1px solid var(--border); }
.tab.current { background: var(--editor); color: var(--text); box-shadow: inset 0 2px var(--accent); }
.breadcrumbs { color: var(--muted); font-size: 11px; padding: 8px 20px; }
.source { overflow-x: auto; padding: 7px 0 20px; counter-reset: line; font: 14px/25px "Cascadia Code", Consolas, monospace; color: var(--text); }
.line { min-width: 720px; white-space: pre; padding-right: 24px; }
.line::before { counter-increment: line; content: counter(line); color: var(--number); display: inline-block; width: 50px; padding-right: 21px; text-align: right; user-select: none; }
.line.active { background: var(--line); }
.line.active::before { color: var(--accent); }
.terminal { border-top: 1px solid var(--border); padding: 12px 20px 17px; }
.terminal-heading { display: flex; gap: 25px; font-size: 11px; color: var(--muted); margin-bottom: 11px; }
.terminal-heading span:first-child { color: var(--text); }
.prompt { font: 12px/1.8 "Cascadia Code", Consolas, monospace; }
.prompt b { color: var(--accent); font-weight: 400; }
.prompt .ok { color: var(--green); }
.prompt .muted { color: var(--muted); }
.ansi { display: flex; gap: 6px; margin-top: 9px; flex-direction: column; }
.ansi-row { display: flex; gap: 5px; }
.ansi i { width: 23px; height: 7px; border-radius: 2px; }
.status { display: flex; justify-content: space-between; border-top: 1px solid var(--border); padding: 5px 14px; color: var(--muted); font-size: 11px; }
.status .branch { color: var(--amber); }
.details { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }
.card { padding: 18px 20px; border: 1px solid var(--border); border-radius: 8px; background: var(--surface); }
.card h2 { font-size: 11px; letter-spacing: .12em; font-weight: 400; color: var(--muted); margin: 0 0 12px; }
.samples { display: flex; flex-wrap: wrap; gap: 12px 20px; font: 13px/1.7 "Cascadia Code", Consolas, monospace; }
.selection { background: var(--selection); color: var(--text); padding: 0 3px; }
mark { background: var(--search); color: var(--text); padding: 0 3px; }
.success { color: var(--green); } .warning { color: var(--amber); } .error { color: var(--red); }
.swatches { display: grid; grid-template-columns: repeat(8, 1fr); gap: 18px; margin-top: 28px; }
.swatch i { display: block; height: 36px; border: 1px solid var(--border); border-radius: 4px; margin-bottom: 9px; }
.swatch span { display: block; font-size: 12px; }
.swatch code { font: 10px "Cascadia Code", Consolas, monospace; color: var(--muted); }
footer { margin-top: 26px; color: var(--muted); font-size: 11px; display: flex; justify-content: space-between; gap: 20px; }
::selection { background: var(--selection); }
@media (max-width: 760px) {
  main { padding: 28px 16px; } header { align-items: flex-start; } h1 { font-size: 40px; }
  .edition { display: none; } .workspace { grid-template-columns: minmax(0, 1fr); } aside { display: none; }
  .details { grid-template-columns: 1fr; } .swatches { grid-template-columns: repeat(4, 1fr); }
  footer { flex-direction: column; gap: 4px; }
}
</style>
</head>
<body><main>
<header>
  <div><div class="eyebrow">GRAPHITE / ORANGE / SLATE</div><h1>Ember Room<span>.</span></h1>
  <p>Глубокий графит. Дымчатый синий. Оранжевый свет.</p></div>
  <div class="edition"><strong>A personal dark theme for Zed</strong>Graphite revision · 02</div>
</header>
<section class="window" aria-label="Схематичное превью темы Zed">
  <div class="titlebar"><span><b>◈</b> &nbsp; ember-room</span><span>main &nbsp; / &nbsp; Zed</span><span>− &nbsp; □ &nbsp; ×</span></div>
  <div class="workspace">
    <aside>
      <div class="folder">⌄ &nbsp; ember-room</div><div class="folder">&nbsp; ⌄ &nbsp; examples</div>
      <div class="file chosen"><span class="ts">TS</span>room.ts <small>M</small></div>
      <div class="file">&nbsp; &nbsp; room.py</div><div class="file">&nbsp; &nbsp; notes.md</div>
      <div class="folder">&nbsp; › &nbsp; themes</div><div class="file">palette.css</div><div class="file">README.md</div>
      <div class="side-label">WORKSPACE</div><div class="side-note">Dark graphite.<br>A spark of orange.<br>A little space to think.</div>
    </aside>
    <div class="editor">
      <div class="tabs"><div class="tab current">room.ts &nbsp; ·</div><div class="tab">notes.md</div></div>
      <div class="breadcrumbs">examples &nbsp; › &nbsp; room.ts &nbsp; › &nbsp; createRoom</div>
      <div class="source">$code</div>
      <div class="terminal"><div class="terminal-heading"><span>Terminal</span><span>Diagnostics</span></div>
        <div class="prompt"><b>❯</b> python examples/room.py<br><span class="ok">Ember Room:</span> 2700K / 65%<br><span class="muted">Graphite surfaces. A little warm light.</span></div>
        <div class="ansi" aria-label="Normal and bright ANSI colors">$ansi</div>
      </div>
    </div>
  </div>
  <div class="status"><span><span class="branch">⑂ main*</span> &nbsp; 0 errors &nbsp; 0 warnings</span><span>12:28 &nbsp; UTF-8 &nbsp; TypeScript &nbsp; Ember Room</span></div>
</section>
<div class="details">
  <section class="card"><h2>FOCUS &amp; SELECTION</h2><div class="samples"><span class="selection">selected text</span><span>find <mark>createRoom</mark></span></div></section>
  <section class="card"><h2>SEMANTIC COLORS</h2><div class="samples"><span class="success">+ added</span><span class="warning">~ modified</span><span class="error">− removed</span></div></section>
</div>
<section class="swatches" aria-label="Основная палитра">$swatches</section>
<footer><span>Сгенерировано из themes/ember-room.json. Эскиз, не скриншот редактора.</span><span>Dark only · Graphite surfaces · Ember orange</span></footer>
</main></body></html>
''').substitute(css=css, code=code, ansi=ansi, swatches=swatches)

if __name__ == "__main__":
    path = ROOT / "preview.html"
    path.write_text(page, encoding="utf-8")
    print(f"Generated {path.name} from Ember Room theme tokens")
