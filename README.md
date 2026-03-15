# Touchless Media Control System
### Using Hand Gesture Recognition

Real-time hand gesture recognition system that controls media 
playback and computer cursor without touching any device.

## Modes

The system has two modes switchable with OK Sign 👌

### Media Mode
| Gesture | Action |
|---------|--------|
| 🤏 Thumb + Index Distance | Volume Control |
| ✊ Closed Fist | Play / Pause |
| ✊ Fist Hold 3 sec | Lock / Unlock |
| 🖐 Open Palm | Mute / Unmute |
| ☝️ 1 Finger Up | Previous Track |
| ✌️ 2 Fingers Up | Next Track |
| 👌 OK Sign | Switch to Cursor Mode |

### Cursor Mode
| Gesture | Action |
|---------|--------|
| ☝️ Index Finger | Move Cursor |
| 👍 Thumb Up | Left Click |
| 👎 Thumb Down | Right Click |
| ✌️ 2 Fingers Tilt | Scroll Up / Down |
| ✊ Fist Hold 3 sec | Lock / Unlock |
| 👌 OK Sign | Switch to Media Mode |

## Technologies Used
- Python 3.11
- OpenCV
- MediaPipe
- NumPy
- pycaw
- pyautogui

## Features
- Real time hand detection at 30 FPS
- Two mode system — Media and Cursor
- Gesture lock and unlock system
- Distance warning for optimal placement
- Gesture history display
- Volume freeze feature
- Smooth cursor movement with cooldown clicks

## Applications
- Hospitals and sterile environments
- Accessibility for people with disabilities
- Hands free media control
- Public kiosks
- Smart classrooms
