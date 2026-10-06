"""Neofetch-style info card -> info-card.svg. Edit ROWS to change content. STATIC=1 for a frozen frame."""
import os
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

HEADER = "emre@github"
ROWS = [
    ("Role",      "Computer Engineer"),
    ("Focus",     "AI-powered software & backend systems"),
    ("",          ""),
    ("Stack",     "Python · FastAPI · PostgreSQL"),
    ("AI",        "LLMs · AI Agents · RAG · Vector Search"),
    ("Ops",       "Docker · Cloud · CI/CD"),
    ("Also",      "TS · React Native · Flutter · Java · C/C++"),
    ("",          ""),
    ("Interests", "AI Eng · Backend · Distributed Systems"),
    ("",          "Software Architecture"),
    ("",          ""),
    ("Motto",     "AI → reliable, production-grade software"),
    ("",          ""),
    ("Web",       "emreseroglu.com"),
]
COLORS = ["#ff5f56", "#ffbd2e", "#27c93f", "#00c2a8", "#3b82f6", "#a855f7", "#ffb703", "#c9d1d9"]

W, LINE, TOP = 490, 22, 74
H = TOP + LINE * len(ROWS) + 54

lines = []
for i, (k, v) in enumerate(ROWS):
    y = TOP + i * LINE
    d = f' style="animation-delay:{0.35 + i*0.09:.2f}s"'
    key = f'<tspan class="k">{escape(k)}</tspan>' + ('<tspan class="s">: </tspan>' if k else "")
    lines.append(f'<text class="l" x="24" y="{y}"{d}>{key}<tspan x="128" class="v">{escape(v)}</tspan></text>')

swatches = "".join(
    f'<rect class="l" x="{24 + i*30}" y="{H-38}" width="26" height="14" rx="2" fill="{c}" '
    f'style="animation-delay:{0.35 + len(ROWS)*0.09 + i*0.05:.2f}s"/>' for i, c in enumerate(COLORS))

anim = "" if STATIC else """
.l{opacity:0;animation:in .35s ease-out forwards}
@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}
.cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"""

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13.5px}}
.k{{fill:#00c2a8;font-weight:700}} .s{{fill:#8b949e}} .v{{fill:#e6edf3}} .h{{fill:#ffb703;font-weight:700;font-size:15px}}
{anim}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
<text x="70" y="20" fill="#8b949e" font-size="12">emre@github ~ $ neofetch</text>
<text class="l h" x="24" y="48" style="animation-delay:.1s">{HEADER}</text>
<rect class="l" x="24" y="54" width="{len(HEADER)*9}" height="2" fill="#30363d" style="animation-delay:.2s"/>
{chr(10).join(lines)}
{swatches}
<rect class="cur" x="{24 + len(COLORS)*30 + 6}" y="{H-38}" width="8" height="14" fill="#e6edf3"/>
</svg>'''
(ROOT / "info-card.svg").write_text(svg)
print("wrote info-card.svg")
