from pathlib import Path
import json
import re
from datetime import datetime

import httpx
from lxml import html


# --------------------------------------------------
# Paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

USERNAME = "krishsharma1159-1159"

URL = (
    f"https://github.com/users/"
    f"{USERNAME}/contributions"
)

OUTPUT = ROOT / "assets" / "contributions.json"


# --------------------------------------------------
# Fetch GitHub page
# --------------------------------------------------

def fetch_page():

    print("Fetching GitHub contribution data...")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151 Safari/537.36"
        )
    }

    response = httpx.get(
        URL,
        headers=headers,
        timeout=30.0,
        follow_redirects=True,
    )

    response.raise_for_status()

    print(
        f"HTTP status: {response.status_code}"
    )

    return response.text


# --------------------------------------------------
# Parse contribution count from tooltip
# --------------------------------------------------

def parse_tooltip_count(text):

    if not text:
        return 0

    text = " ".join(
        text.split()
    ).strip()

    # Example:
    # "No contributions on October 12th."
    if re.search(
        r"no contributions?",
        text,
        re.IGNORECASE,
    ):
        return 0

    # Examples:
    #
    # "1 contribution on October 13th."
    # "5 contributions on October 14th."
    # "1,234 contributions on ..."
    match = re.search(
        r"(\d[\d,]*)\s+contributions?",
        text,
        re.IGNORECASE,
    )

    if match:

        return int(
            match.group(1).replace(",", "")
        )

    return 0


# --------------------------------------------------
# Parse contribution calendar
# --------------------------------------------------

def parse_contributions(page):

    print(
        "Parsing contribution calendar..."
    )

    tree = html.fromstring(page)

    # --------------------------------------------------
    # Build tooltip lookup
    # --------------------------------------------------

    tooltip_map = {}

    tooltips = tree.xpath(
        '//tool-tip[@for]'
    )

    for tooltip in tooltips:

        target_id = tooltip.get(
            "for"
        )

        text = " ".join(
            tooltip.itertext()
        ).strip()

        if target_id:

            tooltip_map[target_id] = text

    print(
        f"Tooltips found: {len(tooltip_map)}"
    )

    # --------------------------------------------------
    # Find contribution cells
    # --------------------------------------------------

    cells = tree.xpath(
        '//td[@data-date and @data-level]'
    )

    if not cells:

        raise RuntimeError(
            "No contribution cells found."
        )

    contributions = []

    for cell in cells:

        date = cell.get(
            "data-date"
        )

        level_raw = cell.get(
            "data-level"
        )

        cell_id = cell.get(
            "id"
        )

        # --------------------------------------------------
        # Contribution level
        # --------------------------------------------------

        try:

            level = int(
                level_raw
            )

        except (
            TypeError,
            ValueError,
        ):

            level = 0

        # --------------------------------------------------
        # Contribution count
        # --------------------------------------------------

        tooltip_text = tooltip_map.get(
            cell_id,
            ""
        )

        count = parse_tooltip_count(
            tooltip_text
        )

        contributions.append(
            {
                "date": date,
                "count": count,
                "level": level,
            }
        )

    return contributions


# --------------------------------------------------
# Calculate statistics
# --------------------------------------------------

def calculate_stats(
    contributions
):

    # --------------------------------------------------
    # Total contributions
    # --------------------------------------------------

    total = sum(
        item["count"]
        for item in contributions
    )

    # --------------------------------------------------
    # Current streak
    # --------------------------------------------------

    current_streak = 0

    for item in reversed(
        contributions
    ):

        if item["count"] > 0:

            current_streak += 1

        else:

            break

    # --------------------------------------------------
    # Longest streak
    # --------------------------------------------------

    longest_streak = 0
    running = 0

    for item in contributions:

        if item["count"] > 0:

            running += 1

            longest_streak = max(
                longest_streak,
                running,
            )

        else:

            running = 0

    # --------------------------------------------------
    # Busiest weekday
    # --------------------------------------------------

    weekday_totals = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
    }

    for item in contributions:

        try:

            date = datetime.strptime(
                item["date"],
                "%Y-%m-%d",
            )

            weekday_totals[
                date.weekday()
            ] += item["count"]

        except (
            ValueError,
            TypeError,
        ):

            pass

    busiest_weekday = max(
        weekday_totals,
        key=weekday_totals.get,
    )

    weekday_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "busiest_day": weekday_names[
            busiest_weekday
        ],
    }


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    page = fetch_page()

    contributions = parse_contributions(
        page
    )

    stats = calculate_stats(
        contributions
    )

    output = {
        "username": USERNAME,
        "source": URL,
        "contributions": contributions,
        "stats": stats,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Output
    # --------------------------------------------------

    print()
    print(
        "======================================"
    )
    print(
        "     CONTRIBUTION DATA GENERATED"
    )
    print(
        "======================================"
    )
    print()

    print(
        f"Days parsed: "
        f"{len(contributions)}"
    )

    print(
        f"Total contributions: "
        f"{stats['total_contributions']}"
    )

    print(
        f"Current streak: "
        f"{stats['current_streak']} days"
    )

    print(
        f"Longest streak: "
        f"{stats['longest_streak']} days"
    )

    print(
        f"Busiest day: "
        f"{stats['busiest_day']}"
    )

    print()

    print(
        f"Saved to: {OUTPUT}"
    )

    print()


if __name__ == "__main__":
    main()