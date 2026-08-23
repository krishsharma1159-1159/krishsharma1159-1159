from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "my-photo.jpeg"
OUTPUT = ROOT / "assets" / "photo-ready.png"


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Input photo not found: {INPUT}")

    print("Reading photo...")
    image = Image.open(INPUT).convert("RGBA")

    print("Removing background...")
    foreground = remove(image)

    # Convert RGBA image to NumPy
    rgba = np.array(foreground)

    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    # White background
    white = np.full_like(rgb, 255)

    alpha_float = alpha.astype(np.float32) / 255.0
    alpha_float = alpha_float[:, :, None]

    composited = (
        rgb.astype(np.float32) * alpha_float
        + white.astype(np.float32) * (1 - alpha_float)
    ).astype(np.uint8)

    # Convert to grayscale
    gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)

    # Improve local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    # Slightly increase contrast
    enhanced = cv2.normalize(
        enhanced,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    # Save as RGB PNG
    final_image = Image.fromarray(enhanced).convert("RGB")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    final_image.save(OUTPUT)

    print(f"Saved cleaned photo to: {OUTPUT}")


if __name__ == "__main__":
    main()