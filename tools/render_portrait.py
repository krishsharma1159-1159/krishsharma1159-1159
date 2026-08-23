from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps


# --------------------------------------------------
# Paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "assets" / "photo-ready.png"
OUTPUT = ROOT / "assets" / "portrait.svg"


# --------------------------------------------------
# ASCII settings
# --------------------------------------------------

# Light -> dark
GLYPHS = " .,:;~+*xXO#"

# Number of characters across
COLS = 76

# Approximate terminal character dimensions
CHAR_WIDTH = 8
CHAR_HEIGHT = 12

# GitHub/terminal accent color
ACCENT = "#00ff88"


# --------------------------------------------------
# Brightness -> ASCII character
# --------------------------------------------------

def brightness_to_glyph(value):
    """
    Convert a grayscale brightness value into
    an ASCII character.

    0   = darkest
    255 = brightest
    """

    normalized = value / 255.0

    # Gamma adjustment.
    # This helps preserve facial details.
    normalized = normalized ** 0.75

    index = int(
        normalized * (len(GLYPHS) - 1)
    )

    return GLYPHS[index]


# --------------------------------------------------
# SVG text escaping
# --------------------------------------------------

def escape_svg_text(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# --------------------------------------------------
# Prepare image
# --------------------------------------------------

def prepare_image():

    print("Loading photo-ready image...")

    image = Image.open(INPUT).convert("L")

    width, height = image.size

    print(
        f"Source image: {width} x {height}"
    )

    # --------------------------------------------------
    # Face-focused crop
    # --------------------------------------------------
    #
    # Your original image is a tall portrait.
    # We intentionally remove most of the lower torso
    # because it doesn't contribute much to the face ASCII.
    #
    # These values are chosen for the supplied photo.
    #

    left = int(width * 0.12)
    top = 0

    right = width
    bottom = int(height * 0.55)

    image = image.crop(
        (
            left,
            top,
            right,
            bottom
        )
    )

    print(
        f"Cropped image: {image.width} x {image.height}"
    )

    # --------------------------------------------------
    # Improve contrast
    # --------------------------------------------------

    image = ImageOps.autocontrast(
        image,
        cutoff=2
    )

    image = ImageEnhance.Contrast(
        image
    ).enhance(1.20)

    # Slight brightness boost so facial details
    # don't become too dark.
    image = ImageEnhance.Brightness(
        image
    ).enhance(1.05)

    return image


# --------------------------------------------------
# Main renderer
# --------------------------------------------------

def main():

    if not INPUT.exists():

        raise FileNotFoundError(
            f"\nInput image not found:\n{INPUT}\n\n"
            "Make sure assets/photo-ready.png exists."
        )

    print()
    print("======================================")
    print("       ASCII PORTRAIT GENERATOR")
    print("======================================")
    print()

    print("Preparing portrait...")

    image = prepare_image()

    width, height = image.size

    # --------------------------------------------------
    # Calculate number of rows
    # --------------------------------------------------
    #
    # Terminal characters are taller than they are wide,
    # so compensate for character aspect ratio.
    #

    rows = max(
        1,
        int(
            COLS
            * (height / width)
            * CHAR_WIDTH
            / CHAR_HEIGHT
        )
    )

    # Resize image to ASCII grid.
    image = image.resize(
        (COLS, rows),
        Image.Resampling.LANCZOS
    )

    pixels = np.array(image)

    print(
        f"ASCII grid: {COLS} x {rows}"
    )

    # --------------------------------------------------
    # SVG dimensions
    # --------------------------------------------------

    svg_width = COLS * CHAR_WIDTH
    svg_height = rows * CHAR_HEIGHT

    svg = []

    # --------------------------------------------------
    # SVG opening
    # --------------------------------------------------

    svg.append(
        f'<svg '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {svg_width} {svg_height}" '
        f'width="{svg_width}" '
        f'height="{svg_height}">'
    )

    # --------------------------------------------------
    # Animation CSS
    # --------------------------------------------------

    svg.append("<style>")

    svg.append(
        f"""
        .ascii {{
            font-family: "Courier New", monospace;
            font-size: {CHAR_HEIGHT}px;
            font-weight: 700;
            fill: {ACCENT};
            white-space: pre;
        }}

        .row {{
            clip-path: inset(0 100% 0 0);
            animation:
                reveal 0.75s ease-out forwards;
        }}

        @keyframes reveal {{

            from {{
                clip-path: inset(0 100% 0 0);
            }}

            to {{
                clip-path: inset(0 0 0 0);
            }}

        }}
        """
    )

    svg.append("</style>")

    # --------------------------------------------------
    # Render every row
    # --------------------------------------------------

    for row in range(rows):

        chars = []

        for col in range(COLS):

            brightness = int(
                pixels[row, col]
            )

            character = brightness_to_glyph(
                brightness
            )

            chars.append(character)

        # Convert row to string.
        line = "".join(chars)

        # Escape characters that could interfere
        # with SVG markup.
        line = escape_svg_text(line)

        # Each row starts slightly after the previous row.
        delay = row * 0.035

        svg.append(
            f'<text '
            f'class="ascii row" '
            f'x="0" '
            f'y="{(row + 1) * CHAR_HEIGHT}" '
            f'style="animation-delay:{delay:.3f}s">'
            f'{line}'
            f'</text>'
        )

    # --------------------------------------------------
    # Close SVG
    # --------------------------------------------------

    svg.append("</svg>")

    # --------------------------------------------------
    # Write file
    # --------------------------------------------------

    OUTPUT.write_text(
        "\n".join(svg),
        encoding="utf-8"
    )

    print()
    print(
        f"Portrait saved to:"
    )
    print(
        OUTPUT
    )
    print()
    print("======================================")
    print("             COMPLETE")
    print("======================================")


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()