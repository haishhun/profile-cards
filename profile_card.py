#!/usr/bin/env python3
"""Generate a Developer Profile card (dark + light SVG) from your GitHub data."""

import datetime as dt
import json
import math
import os
import sys
import urllib.request
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = os.environ.get("GH_USERNAME", "haishhun")
TOKEN = os.environ.get(
    "GH_TOKEN",
    "",
)
OUT_DIR = Path(os.environ.get("OUT_DIR", "assets"))
API = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    contributionsCollection { contributionYears }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes { stargazerCount primaryLanguage { name } }
    }
  }
}"""

YEAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) { totalCommitContributions }
  }
}"""

# metric: (value that earns full marks, weight in the score, label shown under "Strong in")
WEIGHTS = {
    "commits": (2000, 30, "Activity"),
    "prs": (300, 20, "Collaboration"),
    "stars": (1000, 20, "Impact"),
    "repos": (100, 15, "Repos"),
    "followers": (500, 15, "Community"),
}
GRADES = [
    (100, "S+"),
    (90, "S"),
    (80, "A+"),
    (75, "A"),
    (70, "A-"),
    (60, "B+"),
    (50, "B"),
    (40, "B-"),
    (30, "C+"),
    (25, "C"),
    (20, "C-"),
    (15, "D+"),
    (12, "D"),
    (10, "D-"),
    (0, "F"),
]
GRADE_COLORS = {  # (dark, light)
    "S+": ("#FF007F", "#FF007F"),  # Electric Magenta
    "S": ("#7B2CBF", "#7B2CBF"),  # Neon Violet
    "A+": ("#00F5D4", "#00BFA6"),  # Bright Cyan / Teal
    "A": ("#00B4D8", "#0096B4"),  # Vibrant Cyan
    "A-": ("#38D9A9", "#20A67A"),  # Soft Emerald
    "B+": ("#70E000", "#58B800"),  # Lime Green
    "B": ("#70E000", "#58B800"),
    "B-": ("#9BE564", "#70B83F"),  # Softer Lime
    "C+": ("#FFD166", "#E5AD35"),  # Warm Yellow
    "C": ("#FFD166", "#E5AD35"),
    "C-": ("#E9B949", "#C99A26"),  # Muted Gold
    "D+": ("#FF8C42", "#E56B2F"),  # Orange
    "D": ("#FF6B6B", "#E65353"),  # Deep Orange / Coral
    "D-": ("#E88989", "#C96666"),  # Muted Coral
    "F": ("#D90429", "#B80022"),  # Crimson Red
}
CATEGORY = {
    "Python": "Backend",
    "Go": "Backend",
    "Java": "Backend",
    "Kotlin": "Backend",
    "C#": "Backend",
    "PHP": "Backend",
    "Ruby": "Backend",
    "Rust": "Systems",
    "C": "Systems",
    "C++": "Systems",
    "TypeScript": "Frontend",
    "JavaScript": "Frontend",
    "HTML": "Frontend",
    "CSS": "Frontend",
    "Vue": "Frontend",
    "Svelte": "Frontend",
    "Jupyter Notebook": "ML Engineer",
    "Swift": "Mobile",
    "Dart": "Mobile",
    "Shell": "DevOps",
    "Dockerfile": "DevOps",
    "HCL": "DevOps",
}

THEMES = {
    "dark": dict(
        bg="#0D1116",
        border="#3D444D",
        text="#F0F6FC",
        muted="#9198A1",
        line="#30363D",
        ring_bg="#30363D",
        badges=[
            ("#2b2410", "#4a3d17", "#d9a021"),
            ("#241b3a", "#3f2f69", "#b794f6"),
            ("#14281c", "#1f4a2e", "#4ade80"),
        ],
    ),
    "light": dict(
        bg="#FFFFFF",
        border="#E4E4E7",
        text="#18181B",
        muted="#71717A",
        line="#E4E4E7",
        ring_bg="#E4E4E7",
        badges=[
            ("#FEF6DD", "#F0D98A", "#9A6B00"),
            ("#F3EDFF", "#D6C3FB", "#6D3FD1"),
            ("#E8F8EE", "#A8E0BC", "#15803D"),
        ],
    ),
}

# Lucide icons (24x24 grid)
ICONS = {
    "commits": '<circle cx="12" cy="12" r="3"/><line x1="3" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="21" y2="12"/>',
    "prs": '<circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7"/><line x1="6" y1="9" x2="6" y2="21"/>',
    "stars": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "repos": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/>',
    "followers": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
}
LABELS = {
    "commits": "Commits",
    "prs": "PRs",
    "stars": "Stars",
    "repos": "Repos",
    "followers": "Followers",
}


def gql(query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "profile-card",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        sys.exit(f"GitHub API error: {data['errors']}")
    return data["data"]["user"]


def total_commits(years):
    """Sum commit contributions over every year the account has activity (the API caps one query at a year)."""
    now = dt.datetime.now(dt.UTC)
    total = 0
    for year in years:
        end = min(dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.UTC), now)
        u = gql(
            YEAR_QUERY,
            {
                "login": USERNAME,
                "from": f"{year}-01-01T00:00:00Z",
                "to": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        total += u["contributionsCollection"]["totalCommitContributions"]
    return total


def collect():
    u = gql(QUERY, {"login": USERNAME})
    repos = u["repositories"]["nodes"]
    metrics = {
        "commits": total_commits(
            u["contributionsCollection"]["contributionYears"]
        ),  # all time
        "prs": u["pullRequests"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": u["repositories"]["totalCount"],
        "followers": u["followers"]["totalCount"],
    }
    cats = Counter(
        CATEGORY[r["primaryLanguage"]["name"]]
        for r in repos
        if r["primaryLanguage"] and r["primaryLanguage"]["name"] in CATEGORY
    )
    badges = [f"Since {u['createdAt'][:4]}"] + [name for name, _ in cats.most_common(2)]
    return metrics, badges


def score(metrics):
    parts = {
        k: min(1.0, math.log1p(metrics[k]) / math.log1p(cap))
        for k, (cap, _, _) in WEIGHTS.items()
    }
    total = round(sum(parts[k] * WEIGHTS[k][1] for k in parts))
    top = [
        WEIGHTS[k][2]
        for k in sorted(parts, key=parts.get, reverse=True)[:2]
        if parts[k] >= 0.3
    ]
    grade = next(g for floor, g in GRADES if total >= floor)
    return total, grade, top


def fmt(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def render(theme, metrics, badges, total, grade, strong):
    t = THEMES[theme]
    gcolor = GRADE_COLORS[grade][0 if theme == "dark" else 1]
    border_color = gcolor
    border_opacity = 0.30
    divider_color = gcolor
    w, h, pad = 495, 312, 28
    font = "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
    cx, cy, r = 75, 80, 44
    circ = 2 * math.pi * r
    dash = circ * total / 100
    headline = "Strong in " + " · ".join(strong) if strong else "Just getting started"

    stats, col_w = [], (w - pad * 2) / 5
    for i, key in enumerate(WEIGHTS):
        x = pad + col_w * (i + 0.5)
        stats.append(
            f'<g transform="translate({x - 11.4:.1f},166) scale(0.95)" fill="none" stroke="{t["muted"]}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[key]}</g>'
            f'<text x="{x:.1f}" y="216" text-anchor="middle" font-size="22" font-weight="700" fill="{t["text"]}">{fmt(metrics[key])}</text>'
            f'<text x="{x:.1f}" y="236" text-anchor="middle" font-size="12" fill="{t["muted"]}">{LABELS[key]}</text>'
        )

    pills, x = [], pad
    for i, label in enumerate(badges[:3]):
        fill, stroke, color = t["badges"][i % 3]
        bw = len(label) * 7.2 + 28
        pills.append(
            f'<rect x="{x:.1f}" y="266" width="{bw:.1f}" height="28" rx="14" fill="{fill}" stroke="{stroke}"/>'
            f'<text x="{x + bw / 2:.1f}" y="284" text-anchor="middle" font-size="13" font-weight="500" fill="{color}">{escape(label)}</text>'
        )
        x += bw + 10

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Developer profile: grade {grade}, score {total} of 100">
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14"
      fill="{t["bg"]}"
      stroke="{border_color}"
      stroke-opacity="{border_opacity}"/>
  <g font-family="{font}">
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["ring_bg"]}" stroke-width="8"/>
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{gcolor}" stroke-width="8" stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>
    <text x="{cx}" y="{cy + 15}" text-anchor="middle" font-size="42" font-weight="700" fill="{gcolor}">{grade}</text>
    <line x1="140" y1="42" x2="140" y2="118" stroke="{divider_color}" stroke-opacity="0.5"/>
    <text x="160" y="70" font-size="24" font-weight="700" fill="{t["text"]}">Developer Profile</text>
    <text x="160" y="96" font-size="14" fill="{t["muted"]}">{escape(headline)}</text>
    <text x="160" y="120" font-size="14" fill="{t["muted"]}">Score <tspan font-weight="700" fill="{t["text"]}">{total}</tspan> / 100</text>
    <line x1="{pad}" y1="150" x2="{w - pad}" y2="150" stroke="{divider_color}" stroke-opacity="0.45"/>
    {"".join(stats)}
    <line x1="{pad}" y1="250" x2="{w - pad}" y2="250" stroke="{divider_color}" stroke-opacity="0.45"/>
    {"".join(pills)}
  </g>
</svg>
"""


def generate_previews():
    """Generate sample profile cards for every grade in both themes."""
    preview_dir = OUT_DIR / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "commits": 1250,
        "prs": 85,
        "stars": 240,
        "repos": 42,
        "followers": 180,
    }

    badges = ["Since 2020", "Backend", "DevOps"]
    strong = ["Activity", "Collaboration"]

    for floor, grade in GRADES:
        for theme in THEMES:
            svg = render(
                theme=theme,
                metrics=metrics,
                badges=badges,
                total=floor,
                grade=grade,
                strong=strong,
            )

            filename = f"{grade.replace('+', 'plus').replace('-', 'minus')}-{theme}.svg"
            (preview_dir / filename).write_text(svg, encoding="utf-8")

    print(f"Generated {len(GRADES) * len(THEMES)} previews in {preview_dir}")


def main():
    if "--preview" in sys.argv:
        generate_previews()
        return

    if not TOKEN:
        sys.exit("Set GH_TOKEN")

    metrics, badges = collect()
    total, grade, strong = score(metrics)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for theme in THEMES:
        (OUT_DIR / f"profile-{theme}.svg").write_text(
            render(theme, metrics, badges, total, grade, strong),
            encoding="utf-8",
        )

    print(f"grade={grade} score={total} {metrics} badges={badges}")


if __name__ == "__main__":
    main()
