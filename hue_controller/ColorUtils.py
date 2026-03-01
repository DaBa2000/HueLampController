"""
Color conversion helpers for the Hue API.

Hue lights use the CIE XY color space internally.
This module converts common formats (RGB, color temperature) to/from XY.
"""


def rgb_to_xy(red: int, green: int, blue: int) -> tuple[float, float]:
    """
    Convert an RGB color (0–255 each) to the CIE XY color space used by Hue.

    Uses the wide color gamut (sRGB) D65 matrix recommended by Philips.

    Returns:
        (x, y) values clamped to the [0, 1] range.
    """
    # Linearize sRGB values
    def linearize(c: int) -> float:
        v = c / 255.0
        return ((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92

    r, g, b = linearize(red), linearize(green), linearize(blue)

    # Wide gamut D65 conversion matrix
    X = r * 0.664511 + g * 0.154324 + b * 0.162028
    Y = r * 0.283881 + g * 0.668433 + b * 0.047685
    Z = r * 0.000088 + g * 0.072310 + b * 0.986039

    total = X + Y + Z
    if total == 0:
        return 0.0, 0.0

    x = round(X / total, 4)
    y = round(Y / total, 4)
    return x, y


def kelvin_to_mired(kelvin: int) -> int:
    """
    Convert a color temperature in Kelvin to Mired (micro reciprocal degrees).

    Hue accepts color temperature as mired (153–500, roughly 6500 K–2000 K).

    Example:
        kelvin_to_mired(4000)  →  250
    """
    if kelvin <= 0:
        raise ValueError("Kelvin value must be positive.")
    return round(1_000_000 / kelvin)


def mired_to_kelvin(mired: int) -> int:
    """Convert a Mired value back to Kelvin."""
    if mired <= 0:
        raise ValueError("Mired value must be positive.")
    return round(1_000_000 / mired)


def clamp(value: int, low: int, high: int) -> int:
    """Clamp an integer to the [low, high] range."""
    return max(low, min(high, value))
