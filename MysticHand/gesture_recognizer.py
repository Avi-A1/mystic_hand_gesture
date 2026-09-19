"""
MysticHand - Gesture recognition from hand landmarks.

Gestures:
  OPEN_PALM         -> Shield (all fingers extended)
  PINCH             -> Attack beam (thumb + index close)
  PORTAL            -> Portal (two hands rotating)
  TIME_STONE        -> Eye of Agamotto / Time Rewind (three fingers extended: thumb + index + middle)
  MIRROR_DIMENSION  -> Mirror Dimension (two hands touching/praying/palms facing)
  CRIMSON_BANDS     -> Crimson Bands whip (index finger pointing alone)
  NONE              -> No recognized gesture
"""

import math
from hand_tracker import HandTracker
from utils import distance, angle_between

# Gesture labels
GESTURE_NONE = "none"
GESTURE_SHIELD = "shield"
GESTURE_ATTACK = "attack"
GESTURE_PORTAL = "portal"
GESTURE_TIME_STONE = "time_stone"
GESTURE_MIRROR = "mirror_dimension"
GESTURE_CRIMSON_BANDS = "crimson_bands"


class GestureRecognizer:
    """Classifies hand landmarks into Doctor Strange gestures."""

    def __init__(self):
        self._prev_angle = None
        self._rotation_accumulator = 0.0
        self._portal_active = False

    def recognize(self, hand):
        """Classify a single hand into a gesture."""
        lm = hand['landmarks']

        # 1. Check Crimson Bands (pointing with index finger only)
        if self._is_pointing_index(lm):
            return GESTURE_CRIMSON_BANDS

        # 2. Check Portal (index + middle extended, others curled)
        if self._is_two_fingers(lm):
            return GESTURE_PORTAL

        # 3. Check Time Stone (thumb + index + middle extended, ring + pinky curled)
        if self._is_time_stone_gesture(lm):
            return GESTURE_TIME_STONE

        # 4. Check open palm (shield)
        if self._is_open_palm(lm):
            return GESTURE_SHIELD

        return GESTURE_NONE

    def recognize_two_hands(self, hands):
        """
        Check for two-hand gestures:
        - Portal: two hands with index+middle rotating
        - Mirror Dimension: two hands facing each other/palms touching closely
        """
        if len(hands) < 2:
            self._reset_portal()
            return GESTURE_NONE, None, None, 0

        h1, h2 = hands[0], hands[1]
        lm1, lm2 = h1['landmarks'], h2['landmarks']

        # Check Mirror Dimension: both palms open and close to each other
        if self._is_open_palm(lm1) and self._is_open_palm(lm2):
            w1 = lm1[HandTracker.WRIST]
            w2 = lm2[HandTracker.WRIST]
            dist = distance(w1, w2)
            if dist < 250:  # Hands close together
                center = ((w1[0] + w2[0]) // 2, (w1[1] + w2[1]) // 2)
                return GESTURE_MIRROR, center, dist, 0

        # Check Portal: index + middle extended on both hands
        if (self._fingers_extended(lm1, [1, 2]) and
                self._fingers_extended(lm2, [1, 2])):
            center1 = self._extended_fingers_center(lm1)
            center2 = self._extended_fingers_center(lm2)
            angle = angle_between(center1, center2)

            if self._prev_angle is not None:
                delta = angle - self._prev_angle
                if delta > math.pi:
                    delta -= 2 * math.pi
                elif delta < -math.pi:
                    delta += 2 * math.pi
                self._rotation_accumulator += abs(delta)

            self._prev_angle = angle

            if self._rotation_accumulator > 0.3:
                self._portal_active = True

            portal_center = (
                (center1[0] + center2[0]) // 2,
                (center1[1] + center2[1]) // 2,
            )
            portal_radius = distance(center1, center2) / 2

            return (
                GESTURE_PORTAL if self._portal_active else GESTURE_NONE,
                portal_center,
                max(portal_radius, 40),
                self._rotation_accumulator,
            )

        self._reset_portal()
        return GESTURE_NONE, None, None, 0

    # ─── Gesture tests ───────────────────────────────────────────────────

    def _is_finger_extended(self, landmarks, finger_idx):
        tip_ids = [
            HandTracker.THUMB_TIP,
            HandTracker.INDEX_TIP,
            HandTracker.MIDDLE_TIP,
            HandTracker.RING_TIP,
            HandTracker.PINKY_TIP,
        ]
        pip_ids = [
            3,
            HandTracker.INDEX_PIP,
            HandTracker.MIDDLE_PIP,
            HandTracker.RING_PIP,
            HandTracker.PINKY_PIP,
        ]

        tip = landmarks[tip_ids[finger_idx]]
        pip = landmarks[pip_ids[finger_idx]]

        if finger_idx == 0:
            ref = landmarks[HandTracker.INDEX_MCP]
            return distance(tip, ref) > distance(pip, ref)
        else:
            wrist = landmarks[HandTracker.WRIST]
            return distance(tip, wrist) > distance(pip, wrist)

    def _fingers_extended(self, landmarks, finger_indices):
        return all(self._is_finger_extended(landmarks, i) for i in finger_indices)

    def _is_open_palm(self, landmarks):
        return self._fingers_extended(landmarks, [0, 1, 2, 3, 4])

    def _is_pointing_index(self, landmarks):
        """Index finger extended, other fingers curled."""
        index_ext = self._is_finger_extended(landmarks, 1)
        others_curled = all(
            not self._is_finger_extended(landmarks, i)
            for i in [2, 3, 4]
        )
        return index_ext and others_curled

    def _is_two_fingers(self, landmarks):
        """Index + middle extended, thumb/ring/pinky curled."""
        two_ext = (
            self._is_finger_extended(landmarks, 1) and
            self._is_finger_extended(landmarks, 2)
        )
        others_curled = all(
            not self._is_finger_extended(landmarks, i)
            for i in [0, 3, 4]
        )
        return two_ext and others_curled

    def _is_time_stone_gesture(self, landmarks):
        """Thumb + index + middle extended (3-finger time dial), ring + pinky curled."""
        three_ext = (
            self._is_finger_extended(landmarks, 0) and
            self._is_finger_extended(landmarks, 1) and
            self._is_finger_extended(landmarks, 2)
        )
        two_curled = (
            not self._is_finger_extended(landmarks, 3) and
            not self._is_finger_extended(landmarks, 4)
        )
        return three_ext and two_curled

    def _is_pinch(self, landmarks):
        thumb_tip = landmarks[HandTracker.THUMB_TIP]
        index_tip = landmarks[HandTracker.INDEX_TIP]
        palm_size = distance(
            landmarks[HandTracker.WRIST],
            landmarks[HandTracker.MIDDLE_MCP],
        )
        if palm_size < 1:
            return False

        pinch_dist = distance(thumb_tip, index_tip)
        if pinch_dist / palm_size > 0.4:
            return False

        curled_count = sum(
            1 for i in [2, 3, 4]
            if not self._is_finger_extended(landmarks, i)
        )
        return curled_count >= 2

    def _extended_fingers_center(self, landmarks):
        idx = landmarks[HandTracker.INDEX_TIP]
        mid = landmarks[HandTracker.MIDDLE_TIP]
        return ((idx[0] + mid[0]) // 2, (idx[1] + mid[1]) // 2)

    def _reset_portal(self):
        self._prev_angle = None
        self._rotation_accumulator = 0.0
        self._portal_active = False
