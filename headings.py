#!/usr/bin/env python3
"""Generate left-aligned section headings (dark + light SVGs).

Same look as the "TechStack" heading: gradient icon and title on the left,
one line running from the title to the right edge.
"""

from pathlib import Path
from xml.sax.saxutils import escape

from connect import (
    CONNECT_CHAR_W,
    CONNECT_FONT_SIZE,
    CONNECT_HEIGHT,
    CONNECT_ICON_SIZE,
    HEADING_DISPLAY_WIDTH,
    HEADING_WIDTH,
    THEMES,
    picture,
)

OUT_DIR = Path("assets")

ICON_X = 1             # small inset so the icon lines up with the cards below
ICON_GAP = 10          # space between icon and title
LINE_GAP = 24          # space between title and the line

# Gradient for the icon (top -> bottom), one pair per theme.
ICON_GRADIENT = {
    "dark": ("#D09FFF", "#7366F2"),
    "light": ("#B07BF0", "#5B4BD6"),
}

FONT = "Inter, -apple-system, 'Segoe UI', Arial, sans-serif"

# name -> label + Lucide icon (24x24 grid, stroke based)
HEADINGS = {
    "about": {
        "label": "About me",
        "icon": """
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>""",
    },
    "contributions": {
        "label": "Contributions",
        "icon": """
    <circle cx="12" cy="12" r="3"/>
    <line x1="3" y1="12" x2="9" y2="12"/>
    <line x1="15" y1="12" x2="21" y2="12"/>""",
    },
    "stats": {
        "label": "Stats",
        "icon": """
    <path d="M3 3v16a2 2 0 0 0 2 2h16"/>
    <path d="M18 17V9"/>
    <path d="M13 17V5"/>
    <path d="M8 17v-3"/>""",
    },
}


def render(name: str, theme: str) -> str:
    """Render one heading for one theme."""

    if name not in HEADINGS:
        raise ValueError(f"Unknown heading: {name}")
    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}")

    item = HEADINGS[name]
    label = item["label"]
    c = THEMES[theme]
    top, bottom = ICON_GRADIENT[theme]

    width = HEADING_WIDTH
    height = CONNECT_HEIGHT
    cy = height / 2

    size = CONNECT_ICON_SIZE
    scale = size / 24                       # icons are drawn in a 24 x 24 box
    icon_y = cy - size / 2

    text_x = ICON_X + size + ICON_GAP
    line_x = text_x + len(label) * CONNECT_CHAR_W + LINE_GAP

    # userSpaceOnUse so the gradient also paints perfectly horizontal strokes.
    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}" height="{height}"
    viewBox="0 0 {width} {height}"
    role="img"
    aria-label="{escape(label)}">

  <defs>
    <linearGradient id="g" gradientUnits="userSpaceOnUse"
                    x1="0" y1="2" x2="0" y2="22">
      <stop offset="0" stop-color="{top}"/>
      <stop offset="1" stop-color="{bottom}"/>
    </linearGradient>
  </defs>

  <g transform="translate({ICON_X} {icon_y:.1f}) scale({scale:.5f})"
     fill="none" stroke="url(#g)" stroke-width="2.2"
     stroke-linecap="round" stroke-linejoin="round">{item['icon']}
  </g>

  <text x="{text_x}" y="{cy + CONNECT_FONT_SIZE * 0.35:.1f}"
        font-family="{FONT}"
        font-size="{CONNECT_FONT_SIZE}" font-weight="700"
        fill="{c['text']}">{escape(label)}</text>

  <line x1="{line_x:.1f}" y1="{cy}" x2="{width}" y2="{cy}"
        stroke="{c['border']}" stroke-width="1"/>
</svg>
"""


def generate():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in HEADINGS:
        for theme in THEMES:
            (OUT_DIR / f"{name}-{theme}.svg").write_text(
                render(name, theme), encoding="utf-8"
            )


def main():
    generate()
    print("README markup:\n")
    for name, item in HEADINGS.items():
        print('<p align="center">')
        print("  " + picture(name, item["label"], width=HEADING_DISPLAY_WIDTH))
        print("</p>\n")


if __name__ == "__main__":
    main()