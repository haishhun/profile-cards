#!/usr/bin/env python3
"""Generate the "Hi, I'm ..." intro banner (dark + light SVGs)."""

import math
from pathlib import Path
from xml.sax.saxutils import escape

from connect import THEMES, picture

OUT_DIR = Path("assets")

# Same drawing width as the "Let's Connect" heading.
WIDTH = 990
HEIGHT = 186
MARGIN_X = 12

# ---- Content: edit these ---------------------------------------------------

GREETING = "Hi, I'm Dzmitry Haishun"
EMOJI = "\U0001f44b"  # waving hand

BADGE = "Currently Building"
BADGE_SIZE = 17
BADGE_CHAR_W = 9.0
BADGE_HEIGHT = 40
BADGE_COLOR = "#3fb950"

DESCRIPTION = [
    ("Computer Science student at Hunter College and a backend-focused "
    "software engineer"),
    "who enjoys building scalable, maintainable, and real-world systems.",
]

CHIPS = [
    ("cap", "CS @ Hunter College"),
    ("code", "Python Backend Development"),
    ("target", "Seeking SWE Internship 2027"),
]

# ----------------------------------------------------------------------------

DESC_SIZE = 18
CHIP_SIZE = 16
CHIP_CHAR_W = 8.6
CHIP_HEIGHT = 42
CHIP_GAP = 26
ICON_SIZE = 22

FONT = "Inter, -apple-system, 'Segoe UI', Arial, sans-serif"

# Simple outline icons drawn in a 16 x 16 box.
ICONS = {
    "cap": """
        <path d="M8 2.5 15 6 8 9.5 1 6z"/>
        <path d="M4 7.8v3.1c0 1.1 1.8 2.1 4 2.1s4-1 4-2.1V7.8"/>
        <path d="M15 6v4"/>
    """,
    "code": """
        <path d="M5 4.5 1.5 8 5 11.5"/>
        <path d="M11 4.5 14.5 8 11 11.5"/>
        <path d="M9.4 3 6.6 13"/>
    """,
    "target": """
        <circle cx="8" cy="8" r="6"/>
        <circle cx="8" cy="8" r="3.2"/>
        <circle cx="8" cy="8" r=".9" fill="currentColor"/>
    """,
}


def chip_width(label: str) -> int:
    """Pill width: left pad + icon + gap + text + right pad."""
    return math.ceil(22 + ICON_SIZE + 14 + len(label) * CHIP_CHAR_W + 24)


def render_chips(c: dict, y: float) -> str:
    out = []
    x = MARGIN_X + 0.75

    for icon, label in CHIPS:
        w = chip_width(label)
        scale = ICON_SIZE / 16

        out.append(f"""
        <rect x="{x}" y="{y}"
              width="{w}" height="{CHIP_HEIGHT}"
              rx="{CHIP_HEIGHT / 2}"
              fill="{c["bg"]}" fill-opacity="0.55"
              stroke="{c["border"]}" stroke-width="1.2"/>

        <g transform="translate({x + 22:.1f} {y + (CHIP_HEIGHT - ICON_SIZE) / 2:.1f}) scale({scale:.3f})"
           fill="none"
           stroke="{c["accent"]}"
           color="{c["accent"]}"
           stroke-width="1.3"
           stroke-linecap="round"
           stroke-linejoin="round">
            {ICONS[icon]}
        </g>

        <text x="{x + 22 + ICON_SIZE + 14:.1f}"
              y="{y + CHIP_HEIGHT / 2 + CHIP_SIZE * 0.35:.1f}"
              font-family="{FONT}"
              font-size="{CHIP_SIZE}"
              font-weight="500"
              fill="{c["text"]}">{escape(label)}</text>
        """)

        x += w + CHIP_GAP

    return "".join(out)


def render(theme: str) -> str:
    """Render the intro banner for one theme."""

    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}")

    c = THEMES[theme]

    title_y = 46

    # Green status badge.
    badge_w = math.ceil(len(BADGE) * BADGE_CHAR_W + 72)
    badge_h = BADGE_HEIGHT
    badge_x = WIDTH - MARGIN_X - badge_w - 0.75
    badge_y = 16

    desc_y = 92
    desc_gap = 26
    chips_y = HEIGHT - CHIP_HEIGHT - 4

    desc = "".join(
        f"""
        <text x="{MARGIN_X}" y="{desc_y + i * desc_gap}"
              font-family="{FONT}"
              font-size="{DESC_SIZE}"
              fill="{c["text"]}"
              fill-opacity="0.78">{escape(line)}</text>
        """
        for i, line in enumerate(DESCRIPTION)
    )

    return f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="{WIDTH}"
         height="{HEIGHT}"
         viewBox="0 0 {WIDTH} {HEIGHT}"
         role="img"
         aria-label="{escape(GREETING)}. {escape(BADGE)}.">

        <!-- Greeting -->
        <text x="{MARGIN_X}" y="{title_y}"
              font-family="{FONT}"
              font-size="36"
              font-weight="800"
              fill="{c["text"]}">{escape(GREETING)} {EMOJI}</text>

        <!-- Green badge background -->
        <rect x="{badge_x}" y="{badge_y}"
              width="{badge_w}" height="{badge_h}"
              rx="20"
              fill="{BADGE_COLOR}"
              fill-opacity="0.12"
              stroke="{BADGE_COLOR}"
              stroke-opacity="0.75"
              stroke-width="1.2"/>

        <!-- Centered status indicator -->
        <circle cx="{badge_x + badge_w / 2 - 78}"
                cy="{badge_y + badge_h / 2}"
                r="5"
                fill="{BADGE_COLOR}"/>
        
        <!-- Centered badge text -->
        <text x="{badge_x + badge_w / 2 - 62}"
              y="{badge_y + badge_h / 2 + BADGE_SIZE * 0.35:.1f}"
              font-family="{FONT}"
              font-size="{BADGE_SIZE}"
              font-weight="600"
              fill="{BADGE_COLOR}">{escape(BADGE)}</text>

        <!-- Description -->
        {desc}

        <!-- Information chips -->
        {render_chips(c, chips_y)}

    </svg>
    """


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for theme in THEMES:
        output = OUT_DIR / f"intro-{theme}.svg"
        output.write_text(render(theme), encoding="utf-8")
        print(f"Generated {output}")

    print("\nREADME markup:\n")
    print('<p align="center">')
    print("  " + picture("intro", GREETING, width="98%"))
    print("</p>")


if __name__ == "__main__":
    main()
