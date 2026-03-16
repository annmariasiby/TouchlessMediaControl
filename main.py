import cv2
import numpy as np
import pyautogui
import time
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from media_controller import MediaController
from cursor_controller import CursorController
from collections import deque

# Setup
detector = HandDetector()
recognizer = GestureRecognizer()
controller = MediaController()
cursor = CursorController()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 840)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 620)
cap.set(cv2.CAP_PROP_FPS, 30)

vol_percent = 0
status_text = ""
status_timer = 0
gesture_history = deque(maxlen=4)

MEDIA_MODE = "MEDIA"
CURSOR_MODE = "CURSOR"
current_mode = MEDIA_MODE
mode_cooldown = 0

cursor_fist_start = None
CURSOR_FIST_HOLD = 3
cursor_locked = False

ok_hold_count = 0
OK_HOLD_FRAMES = 8

def get_finger_status(landmarks):
    if len(landmarks) < 21:
        return []
    fingers = []
    if landmarks[4][1] < landmarks[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)
    for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
        if landmarks[tip][2] < landmarks[pip][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

def is_thumb_up(landmarks, fingers):
    if len(landmarks) < 21:
        return False
    if fingers != [1, 0, 0, 0, 0]:
        return False
    thumb_tip_y = landmarks[4][2]
    wrist_y = landmarks[0][2]
    middle_y = landmarks[9][2]
    return thumb_tip_y < wrist_y - 30 and thumb_tip_y < middle_y

def is_thumb_down(landmarks, fingers):
    if len(landmarks) < 21:
        return False
    if fingers != [1, 0, 0, 0, 0]:
        return False
    thumb_tip_y = landmarks[4][2]
    wrist_y = landmarks[0][2]
    middle_y = landmarks[9][2]
    return thumb_tip_y > wrist_y + 30 and thumb_tip_y > middle_y

def is_ok_sign(landmarks, fingers):
    if len(landmarks) < 21:
        return False
    if fingers == [0, 0, 1, 1, 1]:
        thumb_x, thumb_y = landmarks[4][1], landmarks[4][2]
        index_x, index_y = landmarks[8][1], landmarks[8][2]
        dist = np.hypot(index_x - thumb_x, index_y - thumb_y)
        return dist < 40
    return False

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img = cv2.resize(img, (840, 620))
    img = detector.find_hands(img)
    landmarks = detector.get_landmarks(img)

    fingers = get_finger_status(landmarks)

    if mode_cooldown > 0:
        mode_cooldown -= 1

    # ── MEDIA MODE ──
    if current_mode == MEDIA_MODE:

        # OK Sign toggle — ONLY when media unlocked
        if not recognizer.system_locked:
            if is_ok_sign(landmarks, fingers) and mode_cooldown == 0:
                ok_hold_count += 1
                if ok_hold_count >= OK_HOLD_FRAMES:
                    current_mode = CURSOR_MODE
                    cursor.reset_position()
                    cursor_locked = False
                    mode_cooldown = 40
                    ok_hold_count = 0
                    status_text = "Mode: CURSOR"
                    status_timer = 40
                    gesture_history.appendleft("CURSOR Mode")
            else:
                ok_hold_count = 0
        else:
            ok_hold_count = 0

        gesture = recognizer.recognize(landmarks)
        controller.update_cooldown()

        distance_warning = ""
        if len(landmarks) >= 21:
            hand_size = np.hypot(
                landmarks[0][1] - landmarks[9][1],
                landmarks[0][2] - landmarks[9][2]
            )
            if hand_size < 80:
                distance_warning = "Move Hand Closer!"
            elif hand_size > 200:
                distance_warning = "Move Hand Further!"
            else:
                distance_warning = "Optimal Distance"

        if status_timer > 0:
            status_timer -= 1
        else:
            status_text = ""

        if gesture == "LOCK":
            status_text = "System LOCKED"
            status_timer = 60
            gesture_history.appendleft("Locked")

        elif gesture == "UNLOCK":
            status_text = "System UNLOCKED"
            status_timer = 60
            gesture_history.appendleft("Unlocked")

        elif gesture == "PLAY_PAUSE":
            controller.play_pause()
            status_text = "Play / Pause"
            status_timer = 40
            gesture_history.appendleft("Play / Pause")

        elif gesture == "MUTE":
            controller.mute()
            status_text = controller.last_action
            status_timer = 40
            gesture_history.appendleft(controller.last_action)

        elif gesture == "NEXT":
            controller.next_track()
            status_text = ">> Next Track"
            status_timer = 40
            gesture_history.appendleft("Next Track")

        elif gesture == "PREV":
            controller.prev_track()
            status_text = "<< Previous Track"
            status_timer = 40
            gesture_history.appendleft("Previous Track")

        elif gesture is not None and isinstance(gesture, tuple) and gesture[0] == "VOLUME":
            if distance_warning == "Optimal Distance":
                vol_percent = controller.set_volume(gesture[1])
                status_text = f"Volume: {vol_percent}%"
            else:
                status_text = f"Volume Frozen: {vol_percent}%"
            status_timer = 10

            bar_x, bar_y = 50, 180
            bar_height = 300
            fill = int(bar_height * vol_percent / 100)
            bar_color = (0,255,0) if distance_warning == "Optimal Distance" else (0,165,255)
            cv2.rectangle(img, (bar_x, bar_y), (bar_x+40, bar_y+bar_height), (200,200,200), 2)
            cv2.rectangle(img, (bar_x, bar_y+bar_height-fill), (bar_x+40, bar_y+bar_height), bar_color, -1)
            cv2.putText(img, f'{vol_percent}%', (bar_x-5, bar_y+bar_height+35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, bar_color, 2)

        if distance_warning:
            warn_color = (0,255,0) if distance_warning == "Optimal Distance" else (0,165,255)
            cv2.rectangle(img, (5, 105), (320, 138), (0,0,0), -1)
            cv2.putText(img, distance_warning, (10, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, warn_color, 2)

    # ── CURSOR MODE ──
    else:
        if status_timer > 0:
            status_timer -= 1
        else:
            status_text = ""

        # OK Sign toggle back — ONLY when cursor unlocked
        if not cursor_locked:
            if is_ok_sign(landmarks, fingers) and mode_cooldown == 0:
                ok_hold_count += 1
                if ok_hold_count >= OK_HOLD_FRAMES:
                    current_mode = MEDIA_MODE
                    mode_cooldown = 40
                    ok_hold_count = 0
                    status_text = "Mode: MEDIA"
                    status_timer = 40
                    gesture_history.appendleft("MEDIA Mode")
            else:
                ok_hold_count = 0
        else:
            ok_hold_count = 0

        if len(fingers) == 5:

            # Fist hold 3sec = Lock/Unlock cursor
            if fingers == [0, 0, 0, 0, 0]:
                now = time.time()
                if cursor_fist_start is None:
                    cursor_fist_start = now
                elif now - cursor_fist_start >= CURSOR_FIST_HOLD:
                    cursor_fist_start = None
                    cursor_locked = not cursor_locked
                    status_text = "Cursor LOCKED" if cursor_locked else "Cursor UNLOCKED"
                    status_timer = 60
                    gesture_history.appendleft("Cursor Locked" if cursor_locked else "Cursor Unlocked")
            else:
                cursor_fist_start = None

            # Block ALL cursor gestures when locked
            if not cursor_locked:

                # Move cursor — index finger
                if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                    cursor.move_cursor(landmarks, img)
                    status_text = "Moving Cursor"
                    status_timer = 5

                # Left click — thumb up
                elif is_thumb_up(landmarks, fingers):
                    if cursor.left_click():
                        status_text = "Left Click!"
                        status_timer = 20
                        gesture_history.appendleft("Left Click")

                # Right click — thumb down
                elif is_thumb_down(landmarks, fingers):
                    if cursor.right_click():
                        status_text = "Right Click!"
                        status_timer = 20
                        gesture_history.appendleft("Right Click")

                # Scroll — two fingers
                elif fingers == [0, 1, 1, 0, 0]:
                    if landmarks[8][2] < landmarks[12][2]:
                        cursor.scroll_up()
                        status_text = "Scroll Up"
                    else:
                        cursor.scroll_down()
                        status_text = "Scroll Down"
                    status_timer = 5

        if len(landmarks) == 0:
            cursor.reset_position()
            cursor_fist_start = None

    # ── UI ──

    # Mode indicator
    mode_color = (0, 255, 0) if current_mode == MEDIA_MODE else (255, 150, 0)
    cv2.rectangle(img, (img.shape[1]//2 - 90, 5), (img.shape[1]//2 + 90, 40), (0,0,0), -1)
    cv2.putText(img, f"MODE: {current_mode}", (img.shape[1]//2 - 75, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color, 2)

    # Lock indicator
    if current_mode == MEDIA_MODE:
        lock_text = "LOCKED" if recognizer.system_locked else "UNLOCKED"
        lock_color = (0, 0, 255) if recognizer.system_locked else (0, 255, 0)
    else:
        lock_text = "LOCKED" if cursor_locked else "UNLOCKED"
        lock_color = (0, 0, 255) if cursor_locked else (0, 255, 0)
    cv2.rectangle(img, (img.shape[1]//2 - 80, 42), (img.shape[1]//2 + 80, 70), (0,0,0), -1)
    cv2.putText(img, lock_text, (img.shape[1]//2 - 65, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, lock_color, 2)

    # Status text
    if status_text:
        text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
        cv2.rectangle(img, (5, 75), (text_size[0] + 25, 118), (0,0,0), -1)
        cv2.putText(img, status_text, (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,255), 3)

    # Gesture guide
    if current_mode == MEDIA_MODE:
        guide = [
            "Thumb+Index  = Volume",
            "Fist         = Play/Pause",
            "Fist 3sec    = Lock/Unlock",
            "Open Palm    = Mute",
            "1 Finger     = Previous",
            "2 Fingers    = Next",
            "OK Sign      = Cursor Mode",
        ]
    else:
        guide = [
            "1 Finger     = Move Cursor",
            "Thumb Up     = Left Click",
            "Thumb Down   = Right Click",
            "2 Fingers    = Scroll Up/Down",
            "Fist 3sec    = Lock/Unlock",
            "OK Sign      = Media Mode",
        ]

    box_x = img.shape[1] - 320
    box_y = 45
    box_w = 310
    box_h = len(guide) * 28 + 15
    overlay = img.copy()
    cv2.rectangle(overlay, (box_x, box_y), (box_x+box_w, box_y+box_h), (0,0,0), -1)
    cv2.addWeighted(overlay, 0.55, img, 0.45, 0, img)
    for i, text in enumerate(guide):
        cv2.putText(img, text, (box_x+10, box_y+24+i*28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1)

    # Gesture history
    cv2.rectangle(img, (5, img.shape[0]-170), (240, img.shape[0]-40), (0,0,0), -1)
    cv2.putText(img, "Gesture History", (10, img.shape[0]-150),
                cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0,255,255), 1)
    cv2.line(img, (10, img.shape[0]-138), (235, img.shape[0]-138), (100,100,100), 1)
    for i, h in enumerate(gesture_history):
        alpha = 255 - i * 55
        color = (alpha, alpha, alpha)
        cv2.putText(img, f"- {h}", (10, img.shape[0]-118+i*26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)

    # Bottom title bar
    cv2.rectangle(img, (0, img.shape[0]-35), (img.shape[1], img.shape[0]), (0,0,0), -1)
    cv2.putText(img, "Touchless Media Control System  |  Press Q to quit",
                (10, img.shape[0]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

    cv2.imshow("Touchless Media Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()