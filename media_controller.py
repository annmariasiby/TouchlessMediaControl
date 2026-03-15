import pyautogui
import numpy as np
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import comtypes

class MediaController:
    def __init__(self):
        # New pycaw compatible method
        from pycaw.pycaw import AudioUtilities
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        import comtypes.client

        comtypes.CoInitialize()
        from pycaw.pycaw import IAudioEndpointVolume
        import comtypes.client

        devices = AudioUtilities.GetSpeakers()
        self.volume_interface = devices.EndpointVolume
        vol_range = self.volume_interface.GetVolumeRange()
        self.min_vol = vol_range[0]
        self.max_vol = vol_range[1]

        self.muted = False
        self.last_action = ""
        self.action_cooldown = 0

    def set_volume(self, distance):
        vol = np.interp(distance, [30, 200], [self.min_vol, self.max_vol])
        self.volume_interface.SetMasterVolumeLevel(vol, None)
        vol_percent = np.interp(distance, [30, 200], [0, 100])
        return int(vol_percent)

    def play_pause(self):
        if self.action_cooldown == 0:
            pyautogui.press('playpause')
            self.last_action = "Play / Pause"
            self.action_cooldown = 20

    def mute(self):
        if self.action_cooldown == 0:
            self.muted = not self.muted
            self.volume_interface.SetMute(self.muted, None)
            self.last_action = "Muted" if self.muted else "Unmuted"
            self.action_cooldown = 20

    def next_track(self):
        if self.action_cooldown == 0:
            pyautogui.press('nexttrack')
            self.last_action = "Next Track"
            self.action_cooldown = 20

    def prev_track(self):
        if self.action_cooldown == 0:
            pyautogui.press('prevtrack')
            self.last_action = "Previous Track"
            self.action_cooldown = 20

    def update_cooldown(self):
        if self.action_cooldown > 0:
            self.action_cooldown -= 1