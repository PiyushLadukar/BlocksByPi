import cv2
import numpy as np

# Import MediaPipe
import mediapipe as mp

MEDIAPIPE_AVAILABLE = True


class HandTracker:
    """
    Hand tracking using MediaPipe with gesture recognition.
    Detects hand landmarks and recognizes gestures for block building.
    """

    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        """
        Initialize MediaPipe hand tracking.
        """

        # MediaPipe init
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

        # Gesture state
        self.current_gesture = None
        self.hand_center = None
        self.index_tip = None
        self.landmarks_3d = None

    def process_frame(self, frame):
        """Process a frame to detect hands and landmarks."""

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        results = self.hands.process(rgb_frame)

        rgb_frame.flags.writeable = True

        # Reset states
        self.current_gesture = None
        self.hand_center = None
        self.index_tip = None
        self.landmarks_3d = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                # Draw landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

                # Extract landmarks
                self._extract_landmarks(hand_landmarks, frame.shape)

                # Recognize gesture
                self.current_gesture = self._recognize_gesture(hand_landmarks)

        return frame

    def _extract_landmarks(self, hand_landmarks, frame_shape):
        """Extract key landmark positions."""
        h, w, _ = frame_shape

        # Wrist center
        wrist = hand_landmarks.landmark[0]
        self.hand_center = (int(wrist.x * w), int(wrist.y * h), wrist.z)

        # Index finger tip
        index_tip = hand_landmarks.landmark[8]
        self.index_tip = (int(index_tip.x * w), int(index_tip.y * h), index_tip.z)

        # Store all landmarks
        self.landmarks_3d = [(lm.x * w, lm.y * h, lm.z) for lm in hand_landmarks.landmark]

    def _recognize_gesture(self, hand_landmarks):
        """Recognize hand gestures."""
        fingers_up = self._count_fingers(hand_landmarks)

        if fingers_up == 5:
            return "place"
        elif fingers_up == 1:
            return "move"
        elif fingers_up == 0:
            return "delete"
        elif fingers_up == 2:
            return "rotate"
        elif self._is_thumb_up(hand_landmarks):
            return "change_color"

        return None

    def _count_fingers(self, hand_landmarks):
        """Count extended fingers."""
        fingers = 0

        # Thumb
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
            fingers += 1

        # Other fingers
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]

        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                fingers += 1

        return fingers

    def _is_thumb_up(self, hand_landmarks):
        """Check thumb up gesture."""
        thumb_tip = hand_landmarks.landmark[4]
        thumb_mcp = hand_landmarks.landmark[2]

        thumb_up = thumb_tip.y < thumb_mcp.y
        fingers_down = all(
            hand_landmarks.landmark[tip].y > hand_landmarks.landmark[pip].y
            for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]
        )

        return thumb_up and fingers_down

    def get_gesture(self):
        return self.current_gesture

    def get_hand_position(self):
        return self.hand_center

    def get_index_position(self):
        return self.index_tip

    def get_landmarks_3d(self):
        return self.landmarks_3d

    def close(self):
        self.hands.close()
