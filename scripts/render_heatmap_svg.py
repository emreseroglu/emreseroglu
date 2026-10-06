"""data/contributions.json -> contrib-heatmap.svg (animated, plays once then freezes)"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "contributions.json").read_text())

# teal ramp matching the rest of the profile (00c2a8)
PALETTE = ["#161b22", "#0b3d38", "#0a6b5f", "#00a08b", "#00c2a8", "#5fffe6"]
CELL, GAP, R = 12, 3, 2.5
LEFT, TOP = 34, 54
W = 860

days = data["days"]
first = date.fromisoformat(days[0]["date"])
start = first - timedelta(days=(first.weekday() + 1) % 7)  # back to Sunday

# level 5 = neon top end for the busiest ~5% of days
counts = sorted(d["count"] for d in days if d["count"] > 0)
top = counts[int(len(counts) * 0.95)] if counts else 1 << 30

cells, months, seen = [], [], set()
for d in days:
    dt = date.fromisoformat(d["date"])
    col, row = (dt - start).days // 7, (dt.weekday() + 1) % 7
    lvl = 5 if d["count"] >= top and d["count"] > 0 else d["level"]
    x, y = LEFT + col * (CELL + GAP), TOP + row * (CELL + GAP)
    delay = (col + row) * 0.022
    cells.append(
        f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{R}" '
        f'fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s">'
        f'<title>{d["count"]} on {d["date"]}</title></rect>')
    key = (dt.year, dt.month)
    if dt.day <= 7 and row == 0 and key not in seen:
        seen.add(key)
        months.append(f'<text class="m" x="{x}" y="{TOP-8}">{dt.strftime("%b")}</text>')

ncols = (date.fromisoformat(days[-1]["date"]) - start).days // 7 + 1
grid_w = ncols * (CELL + GAP)
H = TOP + 7 * (CELL + GAP) + 46
legend_x = W - 20 - (34 + 6 * (CELL + GAP) + 30)
legend = "".join(
    f'<rect x="{legend_x + 30 + i*(CELL+GAP)}" y="{H-30}" width="{CELL}" height="{CELL}" rx="{R}" fill="{c}"/>'
    for i, c in enumerate(PALETTE))
end_t = (ncols + 7) * 0.022 + 0.4

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.c{{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.2,.8,.2,1.2) forwards}}
@keyframes pop{{from{{opacity:0;transform:translateY(-6px) scale(.4)}}to{{opacity:1;transform:none}}}}
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#8b949e;font-size:11px}}
.m{{font-size:10px}} .t{{fill:#c9d1d9;font-size:12px}} .p{{fill:#00c2a8}}
.f{{opacity:0;animation:fade .6s ease {end_t:.2f}s forwards}}
@keyframes fade{{to{{opacity:1}}}}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
{''.join(months)}
<text x="4" y="{TOP + 1*(CELL+GAP) + 10}">Mon</text>
<text x="4" y="{TOP + 3*(CELL+GAP) + 10}">Wed</text>
<text x="4" y="{TOP + 5*(CELL+GAP) + 10}">Fri</text>
{''.join(cells)}
<g class="f">
<text x="{LEFT}" y="{H-20}" class="t">{data["total"]:,} contributions in the last year · current streak {data["current_streak"]}d · longest {data["longest_streak"]}d</text>
<text x="{legend_x}" y="{H-20}">Less</text>{legend}
<text x="{legend_x + 34 + 6*(CELL+GAP)}" y="{H-20}">More</text>
</g>
</svg>'''
(ROOT / "contrib-heatmap.svg").write_text(svg)
print("wrote contrib-heatmap.svg")
