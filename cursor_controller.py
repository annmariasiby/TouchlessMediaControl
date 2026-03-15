import pyautogui
import numpy as np
import cv2
import time

SCREEN_W, SCREEN_H = pyautogui.size()
pyautogui.FAILSAFE = False

class CursorController:
    def __init__(self):
        self.prev_x = 0
        self.prev_y = 0
        self.click_cooldown = 0
        self.SMOOTH = 3
        self.last_click_time = 0
        self.CLICK_DELAY = 1.0

    def move_cursor(self, landmarks, img):
        if len(landmarks) < 21:
            return

        h, w, _ = img.shape
        ix, iy = landmarks[8][1], landmarks[8][2]

        screen_x = np.interp(ix, [50, w-50], [0, SCREEN_W])
        screen_y = np.interp(iy, [50, h-50], [0, SCREEN_H])

        if self.prev_x == 0 and self.prev_y == 0:
            self.prev_x = screen_x
            self.prev_y = screen_y

        smooth_x = self.prev_x + (screen_x - self.prev_x) / self.SMOOTH
        smooth_y = self.prev_y + (screen_y - self.prev_y) / self.SMOOTH

        if abs(smooth_x - self.prev_x) > 1 or abs(smooth_y - self.prev_y) > 1:
            pyautogui.moveTo(int(smooth_x), int(smooth_y))

        self.prev_x = smooth_x
        self.prev_y = smooth_y

        cv2.circle(img, (ix, iy), 15, (255, 0, 255), -1)
        cv2.circle(img, (ix, iy), 18, (255, 255, 255), 2)

        if self.click_cooldown > 0:
            self.click_cooldown -= 1

    def _can_click(self):
        now = time.time()
        if now - self.last_click_time >= self.CLICK_DELAY:
            self.last_click_time = now
            return True
        return False

    def left_click(self):
        if self._can_click():
            pyautogui.click()
            return True
        return False

    def right_click(self):
        if self._can_click():
            pyautogui.rightClick()
            return True
        return False

    def scroll_up(self):
        pyautogui.scroll(10)  # increased scroll speed

    def scroll_down(self):
        pyautogui.scroll(-10)  # increased scroll speed

    def reset_position(self):
        self.prev_x = 0
        self.prev_y = 0