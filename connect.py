#!/usr/bin/env python3
"""Generate individual, proportionally sized contact SVG cards."""

import math
from pathlib import Path
from xml.sax.saxutils import escape

OUT_DIR = Path("assets")

CARD_HEIGHT = 47
TEXT_X = 73
RIGHT_PADDING = 25
TITLE_CHAR_W = 7.2     # approx. px per char, 12px bold
SUBTITLE_CHAR_W = 5.6  # approx. px per char, 10px regular

THEMES = {
    "dark": {
        "bg": "#161B22",
        "border": "#6D5A91",
        "text": "#F0F6FC",
        "muted": "#8B949E",
        "accent": "#B794F6",
    },
    "light": {
        "bg": "#FFFFFF",
        "border": "#C4A8E8",
        "text": "#18181B",
        "muted": "#71717A",
        "accent": "#7B2CBF",
    },
}

CONTACTS = {
    "github": {
        "title": "GitHub",
        "subtitle": "@haishhun",
        "url": "https://github.com/haishhun",
        "icon": """
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53
            5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49
            -2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13
            -.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82
            .72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07
            -1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15
            -.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82
            .64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04
            2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12
            .51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65
            3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01
            2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8
            c0-4.42-3.58-8-8-8"/>
        """,
    },

    "linkedin": {
        "title": "LinkedIn",
        "subtitle": "in/dzmitry-haishun",
        "url": "https://www.linkedin.com/in/dzmitry-haishun/",
        "icon": """
            <path d="M0 1.146C0 .513.526 0 1.175 0h13.65
            C15.474 0 16 .513 16 1.146v13.708
            c0 .633-.526 1.146-1.175 1.146H1.175
            C.526 16 0 15.487 0 14.854zm4.943 12.248
            V6.169H2.542v7.225zm-1.2-8.212
            c.837 0 1.358-.554 1.358-1.248
            -.015-.709-.52-1.248-1.342-1.248S2.4
            3.226 2.4 3.934c0 .694.521 1.248
            1.327 1.248zm4.908 8.212V9.359
            c0-.216.016-.432.08-.586.173-.431.568-.878
            1.232-.878.869 0 1.216.662 1.216 1.634
            v3.865h2.401V9.25c0-2.22-1.184-3.252
            -2.764-3.252-1.274 0-1.845.7-2.165
            1.193v.025h-.016l.016-.025V6.169h-2.4
            c.03.678 0 7.225 0 7.225z"/>
        """,
    },

    "email": {
        "title": "Email",
        "subtitle": "dzhaishun@gmail.com",
        "url": "mailto:dzhaishun@gmail.com",
        # Outlined envelope: transparent inside, colored border.
        "icon": """
            <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1
            2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm2-1
            a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4
            a1 1 0 0 0-1-1zm13 2.383-4.708
            2.825L15 11.105zm-.034 6.876-5.64
            -3.471L8 9.583l-1.326-.795-5.64
            3.47A1 1 0 0 0 2 13h12a1 1 0 0 0
            .966-.741M1 11.105l4.708-2.897L1 5.383z"/>
        """,
    },
}


def text_width(item: dict) -> int:
    """Width one card needs to fit its own text."""
    text_w = max(
        len(item["title"]) * TITLE_CHAR_W,
        len(item["subtitle"]) * SUBTITLE_CHAR_W,
    )
    return math.ceil(TEXT_X + text_w + RIGHT_PADDING)


def card_width() -> int:
    """One shared width for every card: the widest card sets the size."""
    return max(text_width(item) for item in CONTACTS.values())


def render(contact_key: str, theme: str) -> str:
    """Render one contact card.

    Note: links inside an SVG do not work when it is embedded with <img>
    (as on GitHub), so the link is added around the image in the README.
    """

    if contact_key not in CONTACTS:
        raise ValueError(f"Unknown contact: {contact_key}")

    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}")

    item = CONTACTS[contact_key]
    c = THEMES[theme]

    width = card_width()
    height = CARD_HEIGHT

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}" height="{height}"
    viewBox="0 0 {width} {height}"
    role="img"
    aria-label="{escape(item['title'])}: {escape(item['subtitle'])}">

  <rect x="0.75" y="0.75"
        width="{width - 1.5}" height="{height - 1.5}"
        rx="10"
        fill="{c['bg']}"
        stroke="{c['border']}"
        stroke-width="1"/>

  <g transform="translate(25 10.5) scale(1.625)"
     fill="{c['accent']}">
    {item['icon']}
  </g>

  <g font-family="Inter, -apple-system, 'Segoe UI', Arial, sans-serif">
    <text x="{TEXT_X}" y="19" font-size="12" font-weight="700"
          fill="{c['text']}">{escape(item['title'])}</text>

    <text x="{TEXT_X}" y="34" font-size="10"
          fill="{c['muted']}">{escape(item['subtitle'])}</text>
  </g>
</svg>
"""


def readme_snippet(contact_key: str) -> str:
    """Return the README markup that makes a card clickable and theme-aware."""
    item = CONTACTS[contact_key]
    return (
        f'<a href="{escape(item["url"])}">'
        f'<picture>'
        f'<source media="(prefers-color-scheme: dark)" '
        f'srcset="assets/{contact_key}-dark.svg" />'
        f'<source media="(prefers-color-scheme: light)" '
        f'srcset="assets/{contact_key}-light.svg" />'
        f'<img src="assets/{contact_key}-dark.svg" height="{CARD_HEIGHT}" '
        f'alt="{escape(item["title"])}" />'
        f'</picture></a>'
    )


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for contact in CONTACTS:
        for theme in THEMES:
            output = OUT_DIR / f"{contact}-{theme}.svg"
            output.write_text(
                render(contact, theme),
                encoding="utf-8",
            )
            print(f"Generated {output}")

    print("\nREADME markup:\n")
    print('<p align="center">')
    for contact in CONTACTS:
        print("  " + readme_snippet(contact))
    print("</p>")


if __name__ == "__main__":
    main()