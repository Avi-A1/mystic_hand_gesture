"""
MysticHand - Doctor Strange Powers with Computer Vision
========================================================

Use hand gestures in front of your webcam to wield Doctor Strange's powers:

  Open Palm (both hands)   -> Mystic Shield (Mandala of Vishanti)
  Index Pointing & Slashing-> Crimson Bands of Cyttorak (Energy Whip)
  Two Fingers (index+mid)  -> Sling Ring Portal
  3 Fingers Extended       -> Time Stone (Eye of Agamotto)
  Two Palms Together       -> Mirror Dimension Shatter

Press 'Q' to quit | 'H' to toggle HUD
"""

import sys
import cv2
from hand_tracker import HandTracker
from gesture_recognizer import (
    GestureRecognizer,
    GESTURE_SHIELD, GESTURE_ATTACK, GESTURE_PORTAL,
    GESTURE_TIME_STONE, GESTURE_MIRROR, GESTURE_CRIMSON_BANDS,
)
from effects_engine import EffectsEngine
from audio_engine import AudioEngine
import config
from utils import distance


WINDOW_NAME = "MysticHand - Doctor Strange Powers"
CAMERA_INDEX = 0


def draw_hud(frame, gesture_label, fps, show_hud, sound_enabled):
    """Draw HUD showing current gesture and FPS."""
    if not show_hud:
        return

    h, w = frame.shape[:2]

    icon_map = {
        "shield": "SHIELD",
        "portal": "PORTAL",
        "time_stone": "TIME STONE",
        "mirror_dimension": "MIRROR DIMENSION",
        "crimson_bands": "CRIMSON BANDS OF CYTTORAK",
    }
    label = icon_map.get(gesture_label, "")
    if label:
        cv2.putText(frame, label, (20, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 80, 180), 4, cv2.LINE_AA)
        cv2.putText(frame, label, (20, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 180, 255), 2, cv2.LINE_AA)

    cv2.putText(frame, f"FPS: {int(fps)}", (w - 140, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 1, cv2.LINE_AA)

    sound_status = "Sound: ON" if sound_enabled else "Sound: OFF"
    cv2.putText(frame, sound_status, (w - 140, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)

    instructions = "Q: Quit | H: Hide HUD"
    cv2.putText(frame, instructions, (20, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1, cv2.LINE_AA)


def main():
    # Initialize
    tracker = HandTracker(max_hands=2, detection_conf=0.7, tracking_conf=0.6)
    gesture = GestureRecognizer()
    effects = EffectsEngine()
    audio = AudioEngine(enabled=False)  # Sound disabled

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

    if not cap.isOpened():
        print("ERROR: Cannot open webcam. Check your camera connection.")
        sys.exit(1)

    config.print_controls()

    fps = 0
    prev_time = cv2.getTickCount()
    current_gesture = ""
    prev_gesture = ""
    show_hud = True
    sound_enabled = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Failed to read from webcam.")
            break

        frame = cv2.flip(frame, 1)
        hands = tracker.process(frame)

        # Track states
        shields_active = [False, False]
        portal_active = False
        time_stone_active = False
        mirror_active = False
        crimson_active = False

        shields_data = [None, None]
        portal_data = None
        time_stone_data = None
        mirror_data = None
        crimson_data = None

        # ── Two-hand gestures (highest priority) ──────────────────────
        if len(hands) >= 2:
            two_hand_gesture, center, radius, rotation = gesture.recognize_two_hands(hands)

            if two_hand_gesture == GESTURE_PORTAL:
                portal_active = True
                effects.update_portal(center, radius, rotation)
                portal_data = (center, radius)
                current_gesture = "portal"

            elif two_hand_gesture == GESTURE_MIRROR:
                mirror_active = True
                effects.update_mirror(center)
                mirror_data = center
                current_gesture = "mirror_dimension"

        # ── Single-hand gestures ──────────────────────────────────────
        if not portal_active and not mirror_active:
            for hand_idx, hand in enumerate(hands):
                lm = hand['landmarks']
                g = gesture.recognize(hand)

                if g == GESTURE_SHIELD and hand_idx < 2:
                    shields_active[hand_idx] = True
                    center = tracker.get_palm_center(lm)
                    radius = tracker.get_palm_radius(lm) * config.SHIELD_RADIUS_MULTIPLIER
                    effects.update_shield(hand_idx, center, radius)
                    shields_data[hand_idx] = (center, radius)
                    current_gesture = "shield"

                elif g == GESTURE_PORTAL:
                    portal_active = True
                    center = tracker.get_palm_center(lm)
                    radius = tracker.get_palm_radius(lm) * 3.5
                    rotation = 0
                    effects.update_portal(center, radius, rotation)
                    portal_data = (center, radius)
                    current_gesture = "portal"

                elif g == GESTURE_TIME_STONE:
                    time_stone_active = True
                    center = tracker.get_palm_center(lm)
                    radius = tracker.get_palm_radius(lm) * 3.0
                    effects.update_time_stone(center, radius)
                    time_stone_data = (center, radius)
                    current_gesture = "time_stone"

                elif g == GESTURE_CRIMSON_BANDS:
                    crimson_active = True
                    tip = lm[HandTracker.INDEX_TIP]
                    effects.update_crimson(tip)
                    crimson_data = tip
                    current_gesture = "crimson_bands"

        # ── Deactivate unused effects ─────────────────────────────────
        for idx in range(2):
            if not shields_active[idx]:
                effects.deactivate_shield(idx)
        if not portal_active:
            effects.deactivate_portal()
        if not time_stone_active:
            effects.deactivate_time_stone()
        if not mirror_active:
            effects.deactivate_mirror()
        if not crimson_active:
            effects.deactivate_crimson()

        if not any(shields_active + [portal_active, time_stone_active, mirror_active, crimson_active]):
            current_gesture = ""

        # ── Draw effects ──────────────────────────────────────────────
        effects.draw(frame, shields_data, None, portal_data,
                     time_stone_data, mirror_data, crimson_data)

        # ── FPS calculation ───────────────────────────────────────────
        current_time = cv2.getTickCount()
        time_diff = (current_time - prev_time) / cv2.getTickFrequency()
        if time_diff > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / time_diff)
        prev_time = current_time

        # ── HUD ───────────────────────────────────────────────────────
        draw_hud(frame, current_gesture, fps, show_hud, sound_enabled)

        # ── Display ───────────────────────────────────────────────────
        cv2.imshow(WINDOW_NAME, frame)

        # ── Keyboard input ────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('h'):
            show_hud = not show_hud

        prev_gesture = current_gesture

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    tracker.release()
    audio.stop()
    print("MysticHand closed. The mystic arts await your return.")


if __name__ == "__main__":
    main()
