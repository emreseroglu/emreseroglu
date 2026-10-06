"""Photo -> monochrome ASCII portrait SVG that types itself in row by row (plays once).

Usage:  python scripts/make_ascii_svg.py photo.jpg
Optional: pip install rembg opencv-python  -> background removal + local contrast boost (better results).
"""
import sys
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
RAMP = " .`:-=+*cs#%@"          # sparse -> dense
COLS = 92
CHAR_W, CHAR_H = 4.0, 7.4        # px per glyph in the SVG (monospace ~0.55 aspect)
W = 370


def prep(path):
    """returns (gray 0-255, alpha 0-255) - alpha masks out the background"""
    img = Image.open(path).convert("RGBA")
    try:
        from rembg import new_session, remove
        img = remove(img, session=new_session("u2net_human_seg"))
    except ImportError:
        print("rembg not installed - skipping background removal")
    alpha = np.array(img.split()[-1])
    gray = np.array(img.convert("L"))
    try:
        import cv2
        gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    except ImportError:
        gray = np.array(ImageOps.autocontrast(Image.fromarray(gray), cutoff=2))
    return Image.fromarray(gray), Image.fromarray(alpha)


def main(path):
    img, alpha = prep(path)
    rows = int(COLS * img.height / img.width * (CHAR_W / CHAR_H))
    px = np.array(img.resize((COLS, rows), Image.LANCZOS)) / 255.0
    al = np.array(alpha.resize((COLS, rows), Image.LANCZOS)) / 255.0
    # light glyphs on a dark terminal: bright skin -> dense glyph, dark hair -> sparse
    lines = ["".join(RAMP[int(v * (len(RAMP) - 1) + 0.5)] if a > 0.5 else " "
                     for v, a in zip(prow, arow)).rstrip()
             for prow, arow in zip(px, al)]
    while lines and not lines[0].strip(): lines.pop(0)
    while lines and not lines[-1].strip(): lines.pop()

    x0 = (W - COLS * CHAR_W) / 2
    top = 40
    H = int(top + len(lines) * CHAR_H + 16)
    per_row = 0.045
    out = []
    for i, line in enumerate(lines):
        y = top + (i + 1) * CHAR_H
        d = i * per_row
        lw = max(len(line), 1) * CHAR_W
        out.append(
            f'<clipPath id="r{i}"><rect x="{x0}" y="{y-CHAR_H}" height="{CHAR_H+1}" width="0">'
            f'<animate attributeName="width" from="0" to="{lw+2}" begin="{d:.3f}s" dur=".22s" fill="freeze"/></rect></clipPath>'
            f'<text x="{x0}" y="{y-1.4}" clip-path="url(#r{i})" xml:space="preserve">{escape(line)}</text>')
    total = len(lines) * per_row + 0.3
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:{CHAR_W/0.6:.2f}px;fill:#c9d1d9}}</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
<text x="70" y="20" style="font-size:12px;fill:#8b949e">emre@github ~ $ cat me.txt</text>
{"".join(out)}
<rect x="{x0}" y="{top}" width="{CHAR_W*1.6}" height="{CHAR_H}" fill="#00c2a8">
<animate attributeName="y" values="{top};{top + len(lines)*CHAR_H}" dur="{total:.2f}s" fill="freeze"/>
<animate attributeName="opacity" values="1;0" begin="{total:.2f}s" dur=".3s" fill="freeze"/></rect>
</svg>'''
    (ROOT / "ascii-portrait.svg").write_text(svg)
    print(f"wrote ascii-portrait.svg ({len(lines)} rows)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
