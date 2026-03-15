import cv2
import numpy as np
import pyautogui
import time
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from media_controller import MediaController
from collections import deque

# Setup
detector = HandDetector()
recognizer = GestureRecognizer()
controller = MediaController()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 840)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 620)
cap.set(cv2.CAP_PROP_FPS, 30)

vol_percent = 0
status_text = ""
status_timer = 0
gesture_history = deque(maxlen=4)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img = cv2.resize(img, (840, 620))
    img = detector.find_hands(img)
    landmarks = detector.get_landmarks(img)

    gesture = recognizer.recognize(landmarks)
    controller.update_cooldown()

    # Distance warning
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

    # Handle gestures
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

    elif gesture == "SKIP_AD":
        pyautogui.press('escape')
        time.sleep(0.3)
        pyautogui.moveTo(1232, 797, duration=0.2)
        pyautogui.click()
        status_text = "Ad Skipped!"
        status_timer = 40
        gesture_history.appendleft("Skip Ad")

    elif gesture is not None and isinstance(gesture, tuple) and gesture[0] == "VOLUME":
        # Only change volume at optimal distance
        if distance_warning == "Optimal Distance":
            vol_percent = controller.set_volume(gesture[1])
            status_text = f"Volume: {vol_percent}%"
        else:
            status_text = f"Volume Frozen: {vol_percent}%"
        status_timer = 10

        # Volume bar
        bar_x, bar_y = 50, 180
        bar_height = 300
        fill = int(bar_height * vol_percent / 100)
        bar_color = (0,255,0) if distance_warning == "Optimal Distance" else (0,165,255)
        cv2.rectangle(img, (bar_x, bar_y), (bar_x+40, bar_y+bar_height), (200,200,200), 2)
        cv2.rectangle(img, (bar_x, bar_y+bar_height-fill), (bar_x+40, bar_y+bar_height), bar_color, -1)
        cv2.putText(img, f'{vol_percent}%', (bar_x-5, bar_y+bar_height+35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, bar_color, 2)

    # Lock indicator
    lock_text = "LOCKED" if recognizer.system_locked else "UNLOCKED"
    lock_color = (0, 0, 255) if recognizer.system_locked else (0, 255, 0)
    cv2.rectangle(img, (img.shape[1]//2 - 80, 5), (img.shape[1]//2 + 80, 40), (0,0,0), -1)
    cv2.putText(img, lock_text, (img.shape[1]//2 - 65, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, lock_color, 2)

    # Status text
    if status_text:
        text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 1.4, 3)[0]
        cv2.rectangle(img, (5, 48), (text_size[0] + 25, 100), (0,0,0), -1)
        cv2.putText(img, status_text, (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0,255,255), 3)

    # Distance warning
    if distance_warning:
        warn_color = (0,255,0) if distance_warning == "Optimal Distance" else (0,165,255)
        cv2.rectangle(img, (5, 105), (320, 138), (0,0,0), -1)
        cv2.putText(img, distance_warning, (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, warn_color, 2)

    # Gesture guide
    guide = [
        "Thumb+Index  = Volume",
        "Fist         = Play/Pause",
        "Open Palm    = Mute",
        "1 Finger     = Previous",
        "2 Fingers    = Next",
        "3 Fingers    = Skip Ad",
        "Thumbs Up    = Unlock",
        "OK Sign      = Lock",
    ]
    box_x = img.shape[1] - 320
    box_y = 45
    box_w = 310
    box_h = len(guide) * 30 + 15
    overlay = img.copy()
    cv2.rectangle(overlay, (box_x, box_y), (box_x+box_w, box_y+box_h), (0,0,0), -1)
    cv2.addWeighted(overlay, 0.55, img, 0.45, 0, img)
    for i, text in enumerate(guide):
        cv2.putText(img, text, (box_x+10, box_y+26+i*30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255,255,255), 1)

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