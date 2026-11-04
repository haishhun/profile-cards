#!/usr/bin/env python3
"""Generate the left-aligned "TechStack" heading (dark + light SVGs).

Same look as the "Let's Connect" heading, but the icon and title sit on the
left and a single line runs from the title to the right edge.
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

LABEL = "TechStack"
ICON_X = 1             # small inset so the icon lines up with the cards below
ICON_GAP = 10          # space between icon and title
LINE_GAP = 24          # space between title and the line

# Gradient for the </> icon (top -> bottom), one pair per theme.
ICON_GRADIENT = {
    "dark": ("#D09FFF", "#7366F2"),
    "light": ("#B07BF0", "#5B4BD6"),
}

FONT = "Inter, -apple-system, 'Segoe UI', Arial, sans-serif"


def render(theme: str) -> str:
    """Render the TechStack heading for one theme."""

    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}")

    c = THEMES[theme]
    top, bottom = ICON_GRADIENT[theme]

    width = HEADING_WIDTH
    height = CONNECT_HEIGHT
    cy = height / 2

    size = CONNECT_ICON_SIZE
    scale = size / 512                      # icon is drawn in a 512 x 512 box
    icon_y = cy - size / 2

    text_x = ICON_X + size + ICON_GAP
    text_w = len(LABEL) * CONNECT_CHAR_W
    line_x = text_x + text_w + LINE_GAP

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}" height="{height}"
    viewBox="0 0 {width} {height}"
    role="img"
    aria-label="{escape(LABEL)}">

  <defs>
    <linearGradient id="g" gradientUnits="userSpaceOnUse"
                    x1="0" y1="56" x2="0" y2="452">
      <stop offset="0" stop-color="{top}"/>
      <stop offset="1" stop-color="{bottom}"/>
    </linearGradient>
  </defs>

  <g transform="translate({ICON_X} {icon_y:.1f}) scale({scale:.5f})"
     fill="none" stroke="url(#g)" stroke-width="52"
     stroke-linecap="round" stroke-linejoin="round">
    <polyline points="119,160 26,253 119,347"/>
    <polyline points="393,167 486,253 393,357"/>
    <line x1="333" y1="82" x2="179" y2="426"/>
  </g>

  <text x="{text_x}" y="{cy + CONNECT_FONT_SIZE * 0.35:.1f}"
        font-family="{FONT}"
        font-size="{CONNECT_FONT_SIZE}" font-weight="700"
        fill="{c['text']}">{escape(LABEL)}</text>

  <line x1="{line_x:.1f}" y1="{cy}" x2="{width}" y2="{cy}"
        stroke="{c['border']}" stroke-width="1"/>
</svg>
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for theme in THEMES:
        output = OUT_DIR / f"techstack-{theme}.svg"
        output.write_text(render(theme), encoding="utf-8")
        print(f"Generated {output}")

    print("\nREADME markup:\n")
    print('<p align="center">')
    print("  " + picture("techstack", LABEL, width=HEADING_DISPLAY_WIDTH))
    print("</p>")


if __name__ == "__main__":
    main()