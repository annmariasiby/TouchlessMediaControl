import numpy as np

class GestureRecognizer:
    def __init__(self):
        self.gesture_cooldown = 0
        self.last_gesture = None
        self.gesture_hold_count = 0
        self.pending_gesture = None
        self.HOLD_FRAMES = 8
        self.system_locked = False

    def get_finger_status(self, landmarks):
        if len(landmarks) < 21:
            return []

        fingers = []

        # Thumb
        if landmarks[4][1] < landmarks[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 Fingers
        for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
            if landmarks[tip][2] < landmarks[pip][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def detect_raw_gesture(self, fingers, landmarks):

        # THUMBS UP - Unlock
        if fingers == [1, 0, 0, 0, 0]:
            return "UNLOCK"

        # OK SIGN - Lock (thumb + index touching, others up)
        if fingers == [0, 0, 1, 1, 1]:
            thumb_x, thumb_y = landmarks[4][1], landmarks[4][2]
            index_x, index_y = landmarks[8][1], landmarks[8][2]
            distance = np.hypot(index_x - thumb_x, index_y - thumb_y)
            if distance < 40:
                return "LOCK"

        # If system locked block all gestures
        if self.system_locked:
            return None

        # FIST - Play/Pause
        if fingers == [0, 0, 0, 0, 0]:
            return "PLAY_PAUSE"

        # OPEN PALM - Mute
        if fingers == [1, 1, 1, 1, 1]:
            return "MUTE"

        # ONE FINGER - Previous
        if fingers == [0, 1, 0, 0, 0]:
            return "PREV"

        # TWO FINGERS - Next
        if fingers == [0, 1, 1, 0, 0]:
            return "NEXT"

        # THREE FINGERS - Skip Ad
        if fingers == [0, 1, 1, 1, 0]:
            return "SKIP_AD"

        # VOLUME - Thumb + Index only
        if fingers == [1, 1, 0, 0, 0]:
            thumb_x, thumb_y = landmarks[4][1], landmarks[4][2]
            index_x, index_y = landmarks[8][1], landmarks[8][2]
            distance = np.hypot(index_x - thumb_x, index_y - thumb_y)
            return ("VOLUME", distance)

        return None

    def recognize(self, landmarks):
        if len(landmarks) < 21:
            self.last_gesture = None
            self.gesture_cooldown = 0
            self.gesture_hold_count = 0
            self.pending_gesture = None
            return None

        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= 1
            return None

        fingers = self.get_finger_status(landmarks)
        if len(fingers) < 5:
            return None

        raw = self.detect_raw_gesture(fingers, landmarks)

        # Volume is continuous
        if raw is not None and isinstance(raw, tuple) and raw[0] == "VOLUME":
            self.last_gesture = "VOLUME"
            self.pending_gesture = None
            self.gesture_hold_count = 0
            return raw

        if raw is None:
            self.pending_gesture = None
            self.gesture_hold_count = 0
            self.last_gesture = None
            return None

        # Hold gesture for HOLD_FRAMES before triggering
        if raw == self.pending_gesture:
            self.gesture_hold_count += 1
        else:
            self.pending_gesture = raw
            self.gesture_hold_count = 1

        if self.gesture_hold_count >= self.HOLD_FRAMES:
            if raw != self.last_gesture:
                if raw == "LOCK":
                    self.system_locked = True
                elif raw == "UNLOCK":
                    self.system_locked = False

                self.last_gesture = raw
                self.gesture_hold_count = 0
                self.gesture_cooldown = 30
                return raw

        return None