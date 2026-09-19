"""
MysticHand - Configuration system.
Tunable parameters for all effects. Press keys 1-9 to adjust live during runtime.
"""

# ─── Visual Effect Settings ──────────────────────────────────────────────────

# Shield
SHIELD_RADIUS_MULTIPLIER = 2.5
SHIELD_ROTATION_SPEED = 0.05
SHIELD_PARTICLE_COUNT = 3

# Attack Beam
BEAM_LENGTH = 500
BEAM_THICKNESS = 8
BEAM_PARTICLE_COUNT = 2
BEAM_SEGMENTS = 15

# Portal
PORTAL_ROTATION_SPEED = 0.06
PORTAL_SPARK_COUNT = 8
PORTAL_ACTIVATION_THRESHOLD = 0.3

# Time Stone
TIME_ROTATION_SPEED = 0.08
TIME_PARTICLE_COUNT = 4

# Crimson Bands
CRIMSON_TRAIL_LENGTH = 20
CRIMSON_PARTICLE_COUNT = 3

# Mirror Dimension
MIRROR_FRACTURE_LINES = 16

# ─── Audio Settings ──────────────────────────────────────────────────────────
SOUND_ENABLED = True
SOUND_VOLUME = 0.15

# ─── Performance ─────────────────────────────────────────────────────────────
MAX_FPS = 30
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# ─── Controls Info ───────────────────────────────────────────────────────────
CONTROLS = """
===============================================================
            MYSTICHAND - DOCTOR STRANGE POWERS
===============================================================
  GESTURES:
    Open Palm (both hands)   -> Mystic Shield (Mandala)
    Index Pointing & Slashing-> Crimson Bands of Cyttorak (Whip)
    Two Fingers (index+mid)  -> Sling Ring Portal
    3 Fingers (thumb+idx+mid)-> Time Stone (Agamotto Rewind)
    Two Palms Close Together -> Mirror Dimension Shatter

  KEYBOARD:
    Q -> Quit
    H -> Hide/Show HUD
===============================================================
"""

def print_controls():
    """Print controls to console."""
    print(CONTROLS)
