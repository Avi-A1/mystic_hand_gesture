"""
MysticHand - Utility constants and math helpers.
"""

import math
import numpy as np

# ─── Doctor Strange color palette (BGR for OpenCV) ───────────────────────────
ORANGE_CORE = (0, 140, 255)       # Bright inner core
ORANGE_GLOW = (0, 100, 220)       # Softer outer glow
GOLD = (0, 200, 255)              # Highlights and sparks
AMBER = (0, 120, 200)             # Warm mid-tone
WHITE_HOT = (200, 220, 255)       # Intense center glow
PORTAL_ORANGE = (20, 100, 255)    # Portal ring color
SPARK_YELLOW = (0, 240, 255)      # Bright spark accents
SHIELD_BLUE = (255, 180, 0)       # Subtle blue accent for shield runes

# Time Stone (Agamotto Green)
TIME_GREEN_CORE = (0, 255, 100)
TIME_GREEN_GLOW = (0, 200, 50)
TIME_GREEN_DARK = (0, 120, 30)

# Crimson Bands of Cyttorak (Ruby/Crimson Red)
CRIMSON_CORE = (50, 50, 255)
CRIMSON_GLOW = (20, 20, 200)
CRIMSON_HOT = (120, 120, 255)

# Mirror Dimension (Prismatic / Glass Cyan & Magenta)
GLASS_CYAN = (255, 240, 100)
GLASS_MAGENTA = (200, 50, 200)
GLASS_SHINE = (255, 255, 240)

# ─── Effect tuning ──────────────────────────────────────────────────────────
PARTICLE_LIFETIME = 30            # Frames before particle dies
TRAIL_LENGTH = 15                 # Frames a trail point lingers
GLOW_INTENSITY = 0.6              # Additive glow strength (0-1)


def distance(p1, p2):
    """Euclidean distance between two (x, y) points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def midpoint(p1, p2):
    """Midpoint between two (x, y) points."""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def angle_between(p1, p2):
    """Angle in radians from p1 to p2."""
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


def lerp(a, b, t):
    """Linear interpolation between a and b by factor t (0-1)."""
    return a + (b - a) * t


def clamp(value, lo, hi):
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, value))


def rotate_point(point, center, angle_rad):
    """Rotate a point around a center by angle_rad."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    return (
        center[0] + dx * cos_a - dy * sin_a,
        center[1] + dx * sin_a + dy * cos_a,
    )


def normalize(vec):
    """Normalize a 2D vector. Returns (0, 0) for zero vectors."""
    mag = math.hypot(vec[0], vec[1])
    if mag < 1e-6:
        return (0.0, 0.0)
    return (vec[0] / mag, vec[1] / mag)
