#!/usr/bin/env python3
"""Generate GitHub streak cards (dark + light SVG) from your contributions calendar."""

import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GH_USERNAME", "haishhun")
TOKEN = os.environ.get(
    "GH_TOKEN",
    "",
)
OUT_DIR = Path(os.environ.get("OUT_DIR", "assets"))
API = "https://api.github.com/graphql"

YEARS_Q = """
query($login: String!) {
  user(login: $login) { contributionsCollection { contributionYears } }
}"""

YEAR_Q = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""

THEMES = {
    "dark": dict(
        bg="#161B22",
        border="#30363D",
        text="#F0F6FC",
        muted="#8B949E",
        label="#8B949E",
        line="#30363D",
        bar_bg="#30363D",
        divider="#30363D",
        date="#8B949E",
    ),
    "light": dict(
        bg="#FFFFFF",
        border="#E4E4E7",
        text="#18181B",
        muted="#71717A",
        label="#71717A",
        line="#E4E4E7",
        bar_bg="#E4E4E7",
        divider="#E4E4E7",
        date="#71717A",
    ),
}


def gql(query, variables):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "streak-card",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        sys.exit(f"GitHub API error: {data['errors']}")
    return data["data"]


def fetch_counts(now):
    """Return {date: contribution_count} for every year the account has activity."""
    years = gql(YEARS_Q, {"login": USERNAME})["user"]["contributionsCollection"][
        "contributionYears"
    ]
    counts = {}
    for year in years:
        start = f"{year}-01-01T00:00:00Z"
        end = min(dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.UTC), now)
        data = gql(
            YEAR_Q,
            {
                "login": USERNAME,
                "from": start,
                "to": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
        weeks = data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        for week in weeks:
            for day in week["contributionDays"]:
                counts[dt.date.fromisoformat(day["date"])] = day["contributionCount"]
    return counts


def compute_streaks(counts, today):
    """Return (current, current_range, longest, longest_range)."""
    one = dt.timedelta(days=1)
    longest, longest_range = 0, None
    run, run_start = 0, None
    d = min(counts)
    while d <= today:
        if counts.get(d, 0) > 0:
            if run == 0:
                run_start = d
            run += 1
            if run >= longest:
                longest, longest_range = run, (run_start, d)
        else:
            run = 0
        d += one

    # Today may not have a contribution yet, so the streak can still be alive from yesterday.
    end = today if counts.get(today, 0) > 0 else today - one
    d, current = end, 0
    while counts.get(d, 0) > 0:
        current += 1
        d -= one
    current_range = (d + one, end) if current else None
    return current, current_range, longest, longest_range


def fmt_range(rng):
    if not rng:
        return ""
    a, b = rng
    if a == b:
        return f"{a:%b} {a.day}, {a.year}"
    if a.year == b.year:
        return f"{a:%b} {a.day} - {b:%b} {b.day}, {b.year}"
    return f"{a:%b} {a.day}, {a.year} - {b:%b} {b.day}, {b.year}"


def render(theme, current, current_range, longest, longest_range, grade_color):
    c = THEMES[theme]
    w, h, pad = 495, 312, 28
    bar_w = w - pad * 2
    fill = bar_w * min(current / longest, 1) if longest else 0
    font = "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
    left_date = fmt_range(current_range)
    right_date = fmt_range(longest_range)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub streaks: current {current}, longest {longest}">
      <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>
      <g font-family="{font}">
        <text x="{pad}" y="37" font-size="13" font-weight="600" letter-spacing="2.5" fill="{c["label"]}">STREAKS</text>

        <line x1="{w / 2}" y1="82" x2="{w / 2}" y2="188" stroke="{c["divider"]}"/>

        <text x="{w / 4}" y="102" text-anchor="middle" font-size="12" font-weight="600" letter-spacing="2.5" fill="{c["label"]}">CURRENT</text>
        <text x="{w / 4}" y="172" text-anchor="middle" font-size="68" font-weight="700" fill="{grade_color}">{current}</text>

        <text x="{w * 3 / 4}" y="102" text-anchor="middle" font-size="12" font-weight="600" letter-spacing="2.5" fill="{c["label"]}">LONGEST</text>
        <text x="{w * 3 / 4}" y="172" text-anchor="middle" font-size="68" font-weight="700" fill="{grade_color}">{longest}</text>

        <rect x="{pad}" y="236" width="{bar_w}" height="8" rx="4" fill="{c["bar_bg"]}"/>
        <rect x="{pad}" y="236" width="{fill:.1f}" height="8" rx="4" fill="{grade_color}"/>

        <text x="{pad}" y="274" font-size="12" fill="{c["date"]}">{left_date}</text>
        <text x="{w - pad}" y="274" text-anchor="end" font-size="12" fill="{c["date"]}">{right_date}</text>
      </g>
    </svg>
    """


def main():
    if not TOKEN:
        sys.exit("Set GH_TOKEN")
    now = dt.datetime.now(dt.UTC)
    counts = fetch_counts(now)
    current, current_range, longest, longest_range = compute_streaks(counts, now.date())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        svg = render(theme, current, current_range, longest, longest_range)
        (OUT_DIR / f"streak-{theme}.svg").write_text(svg, encoding="utf-8")
    print(f"current={current} longest={longest} ({fmt_range(longest_range)})")


if __name__ == "__main__":
    main()
