#!/usr/bin/env python3
"""Generate the "Featured Projects" heading and project cards (dark + light SVGs).

Cards match the profile and streak cards (495px wide, shown at width="49%"),
so two of them sit side by side. Description and primary language are pulled
live from GitHub when GH_TOKEN is set; otherwise the fallback text below is used.
"""

import json
import os
import textwrap
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

from connect import (
    CONNECT_CHAR_W,
    CONNECT_FONT_SIZE,
    CONNECT_HEIGHT,
    CONNECT_ICON_SIZE,
    HEADING_DISPLAY_WIDTH,
    HEADING_WIDTH,
    PROFILE_CARD_WIDTH,
    RAW_BASE,
    picture,
)
from profile_card import THEMES as CARD_THEMES

USERNAME = os.environ.get("GH_USERNAME", "haishhun")
TOKEN = os.environ.get("GH_TOKEN", "")
OUT_DIR = Path(os.environ.get("OUT_DIR", "assets"))
API = "https://api.github.com/graphql"

THEMES = CARD_THEMES  # same dark/light palettes as the profile + streak cards

# ---- Edit this list to change which projects are featured -------------------
FEATURED = [
    {
        "repo": "project-management-platform",
        "description": (
            "Backend API for a project management platform, built with "
            "FastAPI, PostgreSQL, SQLAlchemy, and Alembic. Containerized "
            "with Docker and covered by pytest integration tests."
        ),
        "tech": ["FastAPI", "PostgreSQL", "SQLAlchemy", "Alembic", "Docker", "pytest"],
    },
    {
        "repo": "fastapi-degree-planner",
        "description": (
            "Backend API for degree planning, built with FastAPI and "
            "SQLAlchemy, featuring authentication, course management, "
            "prerequisite validation, semester planning, and progress tracking."
        ),
        "tech": ["FastAPI", "SQLAlchemy", "PostgreSQL", "pytest"],
    },
]
# -----------------------------------------------------------------------------

CARD_W = PROFILE_CARD_WIDTH
CARD_H = 164
PAD = 24
DESC_WRAP = 68          # characters per line at 12px
DESC_MAX_LINES = 3
CHIP_CHAR_W = 6.0       # approx. px per char, 10.5px semibold
CHIP_PAD = 9            # horizontal padding inside a chip
CHIP_H = 22
CHIP_GAP = 8
FONT = "Inter, -apple-system, 'Segoe UI', Arial, sans-serif"

LANG_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178C6",
    "JavaScript": "#F1E05A",
    "Go": "#00ADD8",
    "Ruby": "#701516",
    "C++": "#F34B7D",
}

# Gradient for the heading icon (top -> bottom), one pair per theme.
ICON_GRADIENT = {
    "dark": ("#D09FFF", "#7366F2"),
    "light": ("#B07BF0", "#5B4BD6"),
}

REPO_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    description
    primaryLanguage { name }
  }
}"""


def gql(query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "profile-cards",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def collect(project: dict) -> dict:
    """Return the project with live description/language when available."""
    info = dict(project, language="Python")
    info["url"] = f"https://github.com/{USERNAME}/{project['repo']}"

    if TOKEN:
        try:
            repo = gql(REPO_QUERY, {"owner": USERNAME, "name": project["repo"]})[
                "repository"
            ]
            if repo.get("description"):
                info["description"] = repo["description"]
            if repo.get("primaryLanguage"):
                info["language"] = repo["primaryLanguage"]["name"]
        except Exception as exc:  # keep the card even if the API hiccups
            print(f"warning: using fallback data for {project['repo']}: {exc}")

    return info


def wrap(text: str) -> list[str]:
    lines = textwrap.wrap(text, DESC_WRAP)
    if len(lines) > DESC_MAX_LINES:
        lines = lines[:DESC_MAX_LINES]
        lines[-1] = lines[-1].rstrip(" .,;") + "..."
    return lines


def render_card(theme: str, project: dict) -> str:
    """Render one project card."""

    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}")

    c = THEMES[theme]
    chip_bg, chip_border, chip_text = c["badges"][1]  # purple badge
    lang = project["language"]
    lang_color = LANG_COLORS.get(lang, "#8B949E")

    desc = "\n".join(
        f'    <text x="{PAD}" y="{66 + i * 18}" font-size="12" '
        f'fill="{c["muted"]}">{escape(line)}</text>'
        for i, line in enumerate(wrap(project["description"]))
    )

    # Tech chips, left to right; stop before they overflow the card.
    chips = []
    x = PAD
    y = CARD_H - PAD - CHIP_H
    for label in project["tech"]:
        w = round(len(label) * CHIP_CHAR_W + CHIP_PAD * 2)
        if x + w > CARD_W - PAD:
            break
        chips.append(
            f'    <rect x="{x}" y="{y}" width="{w}" height="{CHIP_H}" rx="11" '
            f'fill="{chip_bg}" stroke="{chip_border}" stroke-width="1"/>\n'
            f'    <text x="{x + w / 2}" y="{y + 15}" font-size="10.5" '
            f'font-weight="600" text-anchor="middle" '
            f'fill="{chip_text}">{escape(label)}</text>'
        )
        x += w + CHIP_GAP
    chips = "\n".join(chips)

    lang_w = len(lang) * 6.2
    lang_x = CARD_W - PAD - lang_w

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="{CARD_W}" height="{CARD_H}"
    viewBox="0 0 {CARD_W} {CARD_H}"
    role="img"
    aria-label="{escape(project['repo'])}: {escape(project['description'])}">

  <rect x="0.75" y="0.75"
        width="{CARD_W - 1.5}" height="{CARD_H - 1.5}"
        rx="12"
        fill="{c['bg']}"
        stroke="{c['border']}"
        stroke-width="1"/>

  <g font-family="{FONT}">
    <!-- repo icon (Octicons "repo", 16px grid) -->
    <g transform="translate({PAD} 20) scale(1.125)" fill="none"
       stroke="{c['muted']}" stroke-width="1.2" stroke-linejoin="round">
      <path d="M2.5 13V3.5A1.5 1.5 0 0 1 4 2h8.5v10.5H4A1.5 1.5 0 0 0 2.5 14z"/>
      <path d="M4 12.5h8.5V15H4"/>
    </g>

    <text x="{PAD + 28}" y="35" font-size="15" font-weight="700"
          fill="{c['text']}">{escape(project['repo'])}</text>

    <circle cx="{lang_x - 10:.1f}" cy="30.5" r="4.5" fill="{lang_color}"/>
    <text x="{lang_x:.1f}" y="35" font-size="11"
          fill="{c['muted']}">{escape(lang)}</text>

{desc}

{chips}
  </g>
</svg>
"""


def render_heading(theme: str) -> str:
    """Render the left-aligned "Featured Projects" heading (matches TechStack)."""

    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}")

    from connect import THEMES as CONNECT_THEMES

    label = "Featured Projects"
    c = CONNECT_THEMES[theme]
    top, bottom = ICON_GRADIENT[theme]

    width = HEADING_WIDTH
    height = CONNECT_HEIGHT
    cy = height / 2
    size = CONNECT_ICON_SIZE
    icon_x, icon_gap, line_gap = 1, 10, 24
    icon_y = cy - size / 2

    text_x = icon_x + size + icon_gap
    line_x = text_x + len(label) * CONNECT_CHAR_W + line_gap

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}" height="{height}"
    viewBox="0 0 {width} {height}"
    role="img"
    aria-label="{escape(label)}">

  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{top}"/>
      <stop offset="1" stop-color="{bottom}"/>
    </linearGradient>
  </defs>

  <g transform="translate({icon_x} {icon_y:.1f}) scale({size / 24:.5f})"
     fill="none" stroke="url(#g)" stroke-width="2.2"
     stroke-linecap="round" stroke-linejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </g>

  <text x="{text_x}" y="{cy + CONNECT_FONT_SIZE * 0.35:.1f}"
        font-family="{FONT}"
        font-size="{CONNECT_FONT_SIZE}" font-weight="700"
        fill="{c['text']}">{escape(label)}</text>

  <line x1="{line_x:.1f}" y1="{cy}" x2="{width}" y2="{cy}"
        stroke="{c['border']}" stroke-width="1"/>
</svg>
"""


def generate(projects=None):
    """Write the heading and one card per project, for both themes."""
    projects = projects or [collect(p) for p in FEATURED]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for theme in THEMES:
        (OUT_DIR / f"featured-{theme}.svg").write_text(
            render_heading(theme), encoding="utf-8"
        )
        for project in projects:
            (OUT_DIR / f"project-{project['repo']}-{theme}.svg").write_text(
                render_card(theme, project), encoding="utf-8"
            )
    return projects


def readme_markup(projects) -> str:
    cards = "\n  ".join(
        f'<a href="{p["url"]}">'
        f'{picture("project-" + p["repo"], p["repo"], width="49%")}'
        f"</a>"
        for p in projects
    )
    return (
        '<p align="center">\n'
        f'  {picture("featured", "Featured Projects", width=HEADING_DISPLAY_WIDTH)}\n'
        "</p>\n"
        '<p align="center">\n'
        f"  {cards}\n"
        "</p>"
    )


def main():
    projects = generate()
    for p in projects:
        print(f"Generated cards for {p['repo']}")
    print("\nREADME markup:\n")
    print(readme_markup(projects))


if __name__ == "__main__":
    main()