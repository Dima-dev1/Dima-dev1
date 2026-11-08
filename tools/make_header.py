"""Generate animated terminal-style header SVGs (dark + light) for a GitHub profile README."""
import sys
from pathlib import Path

out_dir = Path(sys.argv[1])
out_dir.mkdir(parents=True, exist_ok=True)

THEMES = {
    "dark": dict(window="#161b22", bar="#0d1117", border="#30363d", text="#e6edf3",
                 prompt="#3fb950", accent="#58a6ff", muted="#8b949e", ok="#3fb950",
                 title="#8b949e"),
    "light": dict(window="#ffffff", bar="#f6f8fa", border="#d0d7de", text="#1f2328",
                  prompt="#1a7f37", accent="#0969da", muted="#59636e", ok="#1a7f37",
                  title="#59636e"),
}

# (kind, segments, reveal_seconds)
# kind: "cmd" types slowly, "out" appears quickly, "gap" is blank spacing
LINES = [
    ("cmd", [("prompt", "$ "), ("text", "whoami")], 0.6),
    ("out", [("text", "Full-stack developer and Software Engineering student")], 0.4),
    ("gap", [], 0),
    ("cmd", [("prompt", "$ "), ("text", "cat about.txt")], 0.8),
    ("out", [("text", "BSc Software Engineering")], 0.3),
    ("out", [("text", "10+ shipped apps  ·  led a team of 8  ·  "), ("accent", "React · Next.js · Node · TypeScript")], 0.45),
]

TITLE = "Dima - Software Engineer"  # text in the window's title bar

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
W, H = 1000, 300
LEFT, TOP, LH = 36, 80, 24
PAUSE = 0.25  # pause between lines


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(theme: dict) -> str:
    clips, texts = [], []
    t, y = 0.4, TOP
    last_y = TOP
    for i, (kind, segs, dur) in enumerate(LINES):
        if kind == "gap":
            y += round(LH * 0.55)
            continue
        clips.append(
            f'<clipPath id="c{i}"><rect x="0" y="{y - 18}" height="26" width="0">'
            f'<animate attributeName="width" from="0" to="{W}" begin="{t:.2f}s" dur="{dur}s" '
            f'fill="freeze"/></rect></clipPath>'
        )
        spans = []
        for style, s in segs:
            color = {"prompt": theme["prompt"], "text": theme["text"], "muted": theme["muted"],
                     "accent": theme["accent"], "ok": theme["ok"], "name": theme["text"]}[style]
            weight = ' font-weight="700"' if style in ("name", "prompt") else ""
            spans.append(f'<tspan fill="{color}"{weight}>{esc(s)}</tspan>')
        texts.append(f'<text x="{LEFT}" y="{y}" clip-path="url(#c{i})">{"".join(spans)}</text>')
        t += dur + PAUSE
        last_y = y
        y += LH
    cursor_y = last_y + LH
    cursor = (
        f'<rect x="{LEFT}" y="{cursor_y - 15}" width="10" height="18" fill="{theme["accent"]}" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.01;0.5;0.51;1" '
        f'dur="1.1s" begin="{t:.2f}s" repeatCount="indefinite"/></rect>'
        f'<text x="{LEFT}" y="{cursor_y}" fill="{theme["prompt"]}" font-weight="700" opacity="0">$'
        f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></text>'
    )
    # shift cursor right of the "$ "
    cursor = cursor.replace(f'<rect x="{LEFT}"', f'<rect x="{LEFT + 20}"', 1)
    H = int(cursor_y + 30)  # window height fits however many lines there are

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Full-stack developer</title>
<desc id="d">{esc(" ".join(s for _, segs, _ in LINES for _, s in segs))}</desc>
<defs>{"".join(clips)}</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{theme["window"]}" stroke="{theme["border"]}" stroke-width="1.5"/>
<path d="M1 13 a12 12 0 0 1 12 -12 H{W - 13} a12 12 0 0 1 12 12 V44 H1 Z" fill="{theme["bar"]}"/>
<line x1="1" y1="44" x2="{W - 1}" y2="44" stroke="{theme["border"]}" stroke-width="1"/>
<circle cx="26" cy="23" r="6" fill="#ff5f57"/><circle cx="46" cy="23" r="6" fill="#febc2e"/><circle cx="66" cy="23" r="6" fill="#28c840"/>
<text x="{W / 2}" y="28" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{theme["title"]}">{TITLE}</text>
<g font-family="{FONT}" font-size="16.5">
{"".join(texts)}
{cursor}
</g>
</svg>
'''


for name, theme in THEMES.items():
    (out_dir / f"header-{name}.svg").write_text(build(theme), encoding="utf-8")
    print("wrote", out_dir / f"header-{name}.svg")
