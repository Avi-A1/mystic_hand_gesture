"""
MysticHand - Hand tracking module using MediaPipe.
Wraps MediaPipe Hands to detect and return hand landmarks.
"""

import mediapipe as mp
import cv2


class HandTracker:
    """Detects hands and returns normalized + pixel-space landmarks."""

    # MediaPipe landmark indices for quick reference
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20

    INDEX_MCP = 5
    MIDDLE_MCP = 9
    RING_MCP = 13
    PINKY_MCP = 17

    INDEX_PIP = 6
    MIDDLE_PIP = 10
    RING_PIP = 14
    PINKY_PIP = 18

    def __init__(self, max_hands=2, detection_conf=0.7, tracking_conf=0.6):
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        # Create HandLandmarker using the new task API
        base_options = python.BaseOptions(
            model_asset_path='hand_landmarker.task'
        )
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_conf,
            min_hand_presence_confidence=tracking_conf,
            min_tracking_confidence=tracking_conf
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.frame_counter = 0

    def process(self, frame):
        """
        Detect hands in a BGR frame.

        Returns a list of hand dicts, each containing:
          - 'landmarks': list of 21 (x, y) tuples in pixel coords
          - 'handedness': 'Left' or 'Right'
          - 'raw_landmarks': original MediaPipe normalized landmarks
        """
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        self.frame_counter += 1
        timestamp_ms = int(self.frame_counter * 1000 / 30)

        results = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        hands = []
        if not results.hand_landmarks:
            return hands

        for hand_lms, handedness_info in zip(
            results.hand_landmarks,
            results.handedness,
        ):
            # Convert normalized landmarks → pixel coordinates
            landmarks = []
            for lm in hand_lms:
                px = int(lm.x * w)
                py = int(lm.y * h)
                landmarks.append((px, py))

            hands.append({
                'landmarks': landmarks,
                'handedness': handedness_info[0].category_name,
                'raw_landmarks': hand_lms,
            })

        return hands

    def get_palm_center(self, landmarks):
        """Average of wrist and MCP joints — approximate palm center."""
        palm_indices = [
            self.WRIST,
            self.INDEX_MCP,
            self.MIDDLE_MCP,
            self.RING_MCP,
            self.PINKY_MCP,
        ]
        xs = [landmarks[i][0] for i in palm_indices]
        ys = [landmarks[i][1] for i in palm_indices]
        return (int(sum(xs) / len(xs)), int(sum(ys) / len(ys)))

    def get_palm_radius(self, landmarks):
        """Rough palm radius based on distance from wrist to middle MCP."""
        from utils import distance
        return distance(landmarks[self.WRIST], landmarks[self.MIDDLE_MCP]) * 0.5

    def release(self):
        """Clean up MediaPipe resources."""
        self.landmarker.close()
