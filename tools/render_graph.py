from pathlib import Path
import json
from datetime import datetime


ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "assets" / "contributions.json"
OUTPUT = ROOT / "assets" / "graph.svg"


# --------------------------------------------------
# Graph configuration
# --------------------------------------------------

CELL = 13
GAP = 4
RADIUS = 3

LEFT = 45
TOP = 35

ACCENT = "#00ff88"

LEVELS = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]


# --------------------------------------------------
# Load data
# --------------------------------------------------

def load_data():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Contribution data not found:\n{INPUT}"
        )

    data = json.loads(
        INPUT.read_text(
            encoding="utf-8"
        )
    )

    return data


# --------------------------------------------------
# Organize contribution days
# --------------------------------------------------

def build_calendar(contributions):

    days = {}

    for item in contributions:

        date = datetime.strptime(
            item["date"],
            "%Y-%m-%d"
        )

        days[date] = {
            "count": item["count"],
            "level": item["level"],
        }

    if not days:
        raise RuntimeError(
            "No contribution data available."
        )

    # Sort dates.
    dates = sorted(days)

    # Find Sunday before first date.
    first = dates[0]

    start = first.replace(
        day=first.day
    )

    # Python weekday:
    # Monday=0 ... Sunday=6
    days_to_sunday = (
        first.weekday() + 1
    ) % 7

    from datetime import timedelta

    start = first - timedelta(
        days=days_to_sunday
    )

    # Find Saturday after last date.
    last = dates[-1]

    days_to_saturday = (
        6 - last.weekday()
    )

    end = last + timedelta(
        days=days_to_saturday
    )

    calendar = []

    current = start

    while current <= end:

        calendar.append(
            (
                current,
                days.get(
                    current,
                    {
                        "count": 0,
                        "level": 0,
                    },
                ),
            )
        )

        current += timedelta(
            days=1
        )

    return calendar


# --------------------------------------------------
# Build SVG
# --------------------------------------------------

def main():

    print()
    print("======================================")
    print("       CONTRIBUTION GRAPH")
    print("======================================")
    print()

    data = load_data()

    contributions = data[
        "contributions"
    ]

    stats = data[
        "stats"
    ]

    calendar = build_calendar(
        contributions
    )

    # --------------------------------------------------
    # Group into weeks
    # --------------------------------------------------

    weeks = []

    current_week = []

    for date, item in calendar:

        current_week.append(
            (date, item)
        )

        # Saturday = 6
        if date.weekday() == 5:
            weeks.append(
                current_week
            )

            current_week = []

    if current_week:
        weeks.append(
            current_week
        )

    print(
        f"Weeks: {len(weeks)}"
    )

    # --------------------------------------------------
    # SVG dimensions
    # --------------------------------------------------

    graph_width = (
        LEFT
        + len(weeks) * (CELL + GAP)
        + 30
    )

    graph_height = (
        TOP
        + 7 * (CELL + GAP)
        + 110
    )

    svg = []

    svg.append(
        f'<svg '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {graph_width} {graph_height}" '
        f'width="{graph_width}" '
        f'height="{graph_height}">'
    )

    # --------------------------------------------------
    # Background
    # --------------------------------------------------

    svg.append(
        f'<rect '
        f'width="{graph_width}" '
        f'height="{graph_height}" '
        f'rx="12" '
        f'fill="#0d1117"/>'
    )

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    svg.append("<style>")

    svg.append(
        """
        .cell {
            opacity: 0;
            animation: reveal 0.45s ease-out forwards;
        }

        .fade {
            opacity: 0;
            animation: fadein 0.8s ease-out forwards;
        }

        @keyframes reveal {

            from {
                opacity: 0;
                transform: scale(0.4);
            }

            to {
                opacity: 1;
                transform: scale(1);
            }

        }

        @keyframes fadein {

            from {
                opacity: 0;
            }

            to {
                opacity: 1;
            }

        }
        """
    )

    svg.append("</style>")

    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    svg.append(
        f'<text '
        f'x="25" '
        f'y="25" '
        f'font-family="Courier New, monospace" '
        f'font-size="14" '
        f'font-weight="700" '
        f'fill="{ACCENT}">'
        f'$ contribution_log --year'
        f'</text>'
    )

    # --------------------------------------------------
    # Day labels
    # --------------------------------------------------

    day_labels = [
        ("Mon", 1),
        ("Wed", 3),
        ("Fri", 5),
    ]

    for label, row in day_labels:

        y = (
            TOP
            + row * (CELL + GAP)
            + 10
        )

        svg.append(
            f'<text '
            f'x="8" '
            f'y="{y}" '
            f'font-family="Courier New, monospace" '
            f'font-size="9" '
            f'fill="#8b949e">'
            f'{label}'
            f'</text>'
        )

    # --------------------------------------------------
    # Contribution cells
    # --------------------------------------------------

    for week_index, week in enumerate(weeks):

        x = (
            LEFT
            + week_index * (CELL + GAP)
        )

        # Wave animation by column.
        column_delay = (
            week_index * 0.035
        )

        for date, item in week:

            # Python weekday:
            # Monday=0
            # Sunday=6
            row = date.weekday()

            y = (
                TOP
                + row * (CELL + GAP)
            )

            level = item["level"]

            level = max(
                0,
                min(
                    level,
                    len(LEVELS) - 1
                )
            )

            fill = LEVELS[level]

            svg.append(
                f'<rect '
                f'class="cell" '
                f'x="{x}" '
                f'y="{y}" '
                f'width="{CELL}" '
                f'height="{CELL}" '
                f'rx="{RADIUS}" '
                f'fill="{fill}" '
                f'style="'
                f'animation-delay:'
                f'{column_delay:.3f}s'
                f'"/>'
            )

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    stats_y = (
        TOP
        + 7 * (CELL + GAP)
        + 35
    )

    svg.append(
        f'<text '
        f'class="fade" '
        f'x="25" '
        f'y="{stats_y}" '
        f'font-family="Courier New, monospace" '
        f'font-size="12" '
        f'fill="#c9d1d9" '
        f'style="animation-delay:'
        f'{len(weeks) * 0.035 + 0.3:.2f}s">'
        f'{stats["total_contributions"]} contributions'
        f' · '
        f'{stats["current_streak"]} day streak'
        f' · '
        f'longest {stats["longest_streak"]}'
        f'</text>'
    )

    # --------------------------------------------------
    # Legend
    # --------------------------------------------------

    legend_y = (
        stats_y + 28
    )

    svg.append(
        f'<text '
        f'x="25" '
        f'y="{legend_y}" '
        f'font-family="Courier New, monospace" '
        f'font-size="10" '
        f'fill="#8b949e">'
        f'less'
        f'</text>'
    )

    legend_x = 60

    for index, color in enumerate(
        LEVELS
    ):

        svg.append(
            f'<rect '
            f'x="{legend_x}" '
            f'y="{legend_y - 10}" '
            f'width="{CELL}" '
            f'height="{CELL}" '
            f'rx="{RADIUS}" '
            f'fill="{color}"/>'
        )

        legend_x += (
            CELL + GAP
        )

    svg.append(
        f'<text '
        f'x="{legend_x + 5}" '
        f'y="{legend_y}" '
        f'font-family="Courier New, monospace" '
        f'font-size="10" '
        f'fill="#8b949e">'
        f'more'
        f'</text>'
    )

    # --------------------------------------------------
    # Footer
    # --------------------------------------------------

    footer_y = (
        graph_height - 10
    )

    svg.append(
        f'<text '
        f'x="{graph_width - 190}" '
        f'y="{footer_y}" '
        f'font-family="Courier New, monospace" '
        f'font-size="9" '
        f'fill="#6e7681">'
        f'updated from GitHub'
        f'</text>'
    )

    # --------------------------------------------------
    # Close SVG
    # --------------------------------------------------

    svg.append("</svg>")

    OUTPUT.write_text(
        "\n".join(svg),
        encoding="utf-8"
    )

    print()
    print(
        f"Graph saved to:\n{OUTPUT}"
    )

    print()
    print("======================================")
    print("              COMPLETE")
    print("======================================")


if __name__ == "__main__":
    main()