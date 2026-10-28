#!/usr/bin/env python3

import datetime as dt
import sys

import profile_card
import streak


def main():
    if not profile_card.TOKEN or not streak.TOKEN:
        sys.exit("Set GH_TOKEN")

    # 1. Fetch profile metrics and calculate the grade once.
    metrics, badges = profile_card.collect()
    total, grade, strong = profile_card.score(metrics)

    # 2. Generate profile cards.
    profile_card.OUT_DIR.mkdir(parents=True, exist_ok=True)

    for theme in profile_card.THEMES:
        svg = profile_card.render(theme, metrics, badges, total, grade, strong)
        output = profile_card.OUT_DIR / f"profile-{theme}.svg"
        output.write_text(svg, encoding="utf-8")

    # 3. Fetch contribution data and calculate streaks.
    now = dt.datetime.now(dt.UTC)
    counts = streak.fetch_counts(now)

    current, current_range, longest, longest_range = streak.compute_streaks(
        counts, now.date()
    )

    # 4. Use the exact grade colors from profile_card.py.
    for theme in streak.THEMES:
        color_index = 0 if theme == "dark" else 1
        grade_color = profile_card.GRADE_COLORS[grade][color_index]

        svg = streak.render(
            theme,
            current,
            current_range,
            longest,
            longest_range,
            grade_color,
        )

        output = streak.OUT_DIR / f"streak-{theme}.svg"
        output.write_text(svg, encoding="utf-8")

    print(
        f"Generated all cards | Grade: {grade} | Score: {total} | "
        f"Current streak: {current} | Longest streak: {longest}"
    )


if __name__ == "__main__":
    main()
