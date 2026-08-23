from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "sysinfo.svg"


# --------------------------------------------------
# Terminal panel content
# --------------------------------------------------

TITLE = "krish@github:~$ whoami --verbose"

ROWS = [
    ("role", "B.Tech CSE (Hons)"),
    ("focus", "AI with Analytics"),
    ("stack", "Python · MERN · ML · Cybersecurity"),
    ("graph", "TigerGraph · MongoDB · SQL"),
    ("build", "Projects · Hackathons · CTFs"),
    ("status", "● ONLINE"),
]


# --------------------------------------------------
# Panel dimensions
# --------------------------------------------------

WIDTH = 760
HEIGHT = 430

BACKGROUND = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#00ff88"


# --------------------------------------------------
# Escape SVG text
# --------------------------------------------------

def escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# --------------------------------------------------
# Build SVG
# --------------------------------------------------

def main():

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}">'
    )

    # --------------------------------------------------
    # Background
    # --------------------------------------------------

    svg.append(
        f'<rect '
        f'x="1" y="1" '
        f'width="{WIDTH - 2}" '
        f'height="{HEIGHT - 2}" '
        f'rx="10" '
        f'fill="{BACKGROUND}" '
        f'stroke="{BORDER}" '
        f'stroke-width="2"/>'
    )

    # --------------------------------------------------
    # Terminal top bar
    # --------------------------------------------------

    svg.append(
        '<rect '
        'x="1" y="1" '
        f'width="{WIDTH - 2}" '
        'height="42" '
        'rx="10" '
        f'fill="{BORDER}"/>'
    )

    # Cover bottom rounded corners of top bar
    svg.append(
        f'<rect '
        f'x="1" y="22" '
        f'width="{WIDTH - 2}" '
        f'height="21" '
        f'fill="{BORDER}"/>'
    )

    # Terminal dots
    dots = [
        (22, "#ff5f56"),
        (42, "#ffbd2e"),
        (62, "#27c93f"),
    ]

    for x, color in dots:
        svg.append(
            f'<circle cx="{x}" cy="22" r="6" fill="{color}"/>'
        )

    # --------------------------------------------------
    # Title
    # --------------------------------------------------

    svg.append(
        f'<text '
        f'x="90" y="27" '
        f'font-family="Courier New, monospace" '
        f'font-size="15" '
        f'fill="{TEXT}">'
        f'{escape(TITLE)}'
        f'</text>'
    )

    # --------------------------------------------------
    # CSS animation
    # --------------------------------------------------

    svg.append("<style>")

    svg.append(
        """
        .panel-row {
            opacity: 0;
            animation: appear 0.5s ease-out forwards;
        }

        .cursor {
            animation: blink 1s step-end infinite;
        }

        @keyframes appear {
            from {
                opacity: 0;
                transform: translateX(-8px);
            }

            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes blink {
            50% {
                opacity: 0;
            }
        }
        """
    )

    svg.append("</style>")

    # --------------------------------------------------
    # Information rows
    # --------------------------------------------------

    start_y = 95
    row_gap = 47

    for index, (label, value) in enumerate(ROWS):

        y = start_y + index * row_gap

        delay = index * 0.12

        # Label
        svg.append(
            f'<text '
            f'class="panel-row" '
            f'x="55" '
            f'y="{y}" '
            f'style="animation-delay:{delay:.2f}s" '
            f'font-family="Courier New, monospace" '
            f'font-size="17" '
            f'font-weight="700" '
            f'fill="{ACCENT}">'
            f'{escape(label):}'
            f'</text>'
        )

        # Separator
        svg.append(
            f'<text '
            f'class="panel-row" '
            f'x="180" '
            f'y="{y}" '
            f'style="animation-delay:{delay:.2f}s" '
            f'font-family="Courier New, monospace" '
            f'font-size="17" '
            f'fill="{MUTED}">'
            f'→'
            f'</text>'
        )

        # Value
        value_color = (
            ACCENT
            if label == "status"
            else TEXT
        )

        svg.append(
            f'<text '
            f'class="panel-row" '
            f'x="215" '
            f'y="{y}" '
            f'style="animation-delay:{delay:.2f}s" '
            f'font-family="Courier New, monospace" '
            f'font-size="17" '
            f'fill="{value_color}">'
            f'{escape(value)}'
            f'</text>'
        )

    # --------------------------------------------------
    # Bottom command
    # --------------------------------------------------

    bottom_y = HEIGHT - 30

    svg.append(
        f'<text '
        f'x="55" '
        f'y="{bottom_y}" '
        f'font-family="Courier New, monospace" '
        f'font-size="14" '
        f'fill="{MUTED}">'
        f'krish@github:~$ '
        f'</text>'
    )

    svg.append(
        f'<text '
        f'class="cursor" '
        f'x="190" '
        f'y="{bottom_y}" '
        f'font-family="Courier New, monospace" '
        f'font-size="14" '
        f'fill="{ACCENT}">'
        f'█'
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
    print("======================================")
    print("       SYSTEM PANEL GENERATED")
    print("======================================")
    print()
    print(f"Saved to: {OUTPUT}")
    print()


if __name__ == "__main__":
    main()