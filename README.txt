================================================================
  Touchless Media Control System
  Using Hand Gesture Recognition
================================================================

----------------------------------------------------------------
OVERVIEW
----------------------------------------------------------------
A real-time hand gesture recognition system that allows users
to control media playback and computer cursor without touching
any device. Uses laptop webcam to detect hand gestures and
converts them into commands.

----------------------------------------------------------------
TWO MODES
----------------------------------------------------------------
Switch between modes using OK Sign 👌

MEDIA MODE
----------
   Gesture               Action
   --------              --------
   Thumb + Index      =  Volume Control
   Fist               =  Play / Pause
   Fist Hold 3 sec    =  Lock / Unlock
   Open Palm          =  Mute / Unmute
   1 Finger Up        =  Previous Track
   2 Fingers Up       =  Next Track
   OK Sign            =  Switch to Cursor Mode

CURSOR MODE
-----------
   Gesture               Action
   --------              --------
   Index Finger       =  Move Cursor
   Thumb Up           =  Left Click
   Thumb Down         =  Right Click
   2 Fingers Tilt     =  Scroll Up / Down
   Fist Hold 3 sec    =  Lock / Unlock
   OK Sign            =  Switch to Media Mode

----------------------------------------------------------------
HOW IT WORKS
----------------------------------------------------------------
1. Webcam captures real-time video
2. OpenCV processes each video frame
3. MediaPipe detects 21 hand landmark points
4. Finger positions are analyzed
5. Gesture is recognized
6. System executes media or cursor command

----------------------------------------------------------------
TECHNOLOGIES USED
----------------------------------------------------------------
* Python 3.11   - Main programming language
* OpenCV        - Video capture and processing
* MediaPipe     - Hand detection and tracking
* NumPy         - Mathematical calculations
* Pycaw         - System volume control
* PyAutoGUI     - Media and cursor control

----------------------------------------------------------------
FILES
----------------------------------------------------------------
* main.py               - Main program
* hand_detector.py      - Hand detection module
* gesture_recognizer.py - Gesture recognition module
* media_controller.py   - Media control module
* cursor_controller.py  - Cursor control module
* README.txt            - This file

----------------------------------------------------------------
FEATURES
----------------------------------------------------------------
* Real time hand detection at 30 FPS
* Two mode system — Media and Cursor
* Gesture lock and unlock in both modes
* Distance warning system
* Gesture history display
* Volume freeze feature
* Smooth cursor with click cooldown

----------------------------------------------------------------
APPLICATIONS
----------------------------------------------------------------
* Hospitals - touchless control in sterile environments
* Smart homes and classrooms
* Public kiosks - hygiene friendly

----------------------------------------------------------------
LIMITATIONS
----------------------------------------------------------------
* Requires good lighting
* Keep hand 40-60cm from camera

----------------------------------------------------------------
FUTURE IMPROVEMENTS
----------------------------------------------------------------
* AI based gesture recognition
* Multi hand gesture support
* Voice and gesture hybrid control
* Smart home device integration
* Mood based music using facial emotion detection

================================================================