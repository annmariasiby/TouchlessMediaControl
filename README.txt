================================================================
  Touchless Media Control System
  Using Hand Gesture Recognition
================================================================

----------------------------------------------------------------
OVERVIEW
----------------------------------------------------------------
A real-time hand gesture recognition system that allows users
to control media playback without touching any device. Uses
laptop webcam to detect hand gestures and converts them into
media control commands.

----------------------------------------------------------------
GESTURES
----------------------------------------------------------------

   Gesture            Action
   --------           --------
   OK Sign         =  Lock System
   Thumbs Up       =  Unlock System
   Closed Fist     =  Play / Pause
   Open Palm       =  Mute / Unmute
   1 Finger Up     =  Previous Track
   2 Fingers Up    =  Next Track
   Thumb + Index   =  Volume Control
   3 Fingers Up    =  Skip Ad(YouTube)

----------------------------------------------------------------
HOW IT WORKS
----------------------------------------------------------------
1. Webcam captures real-time video
2. OpenCV processes each video frame
3. MediaPipe detects 21 hand landmark points
4. Finger positions are analyzed
5. Gesture is recognized
6. System executes media control command

----------------------------------------------------------------
TECHNOLOGIES USED
----------------------------------------------------------------
* Python 3.11   - Main programming language
* OpenCV        - Video capture and processing
* MediaPipe     - Hand detection and tracking
* NumPy         - Mathematical calculations
* Pycaw         - System volume control
* PyAutoGUI     - Keyboard media commands

----------------------------------------------------------------
FILES
----------------------------------------------------------------
* main.py               - Main program
* hand_detector.py      - Hand detection module
* gesture_recognizer.py - Gesture recognition module
* media_controller.py   - Media control module
* README.txt            - This file

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
* Custom gesture training

================================================================