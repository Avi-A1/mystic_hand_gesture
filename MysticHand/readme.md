# 🔮 MysticHand — Doctor Strange Powers with Computer Vision

Use hand gestures in front of your webcam to wield Doctor Strange's mystic powers in real-time!

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange)

## ✨ Powers

| Gesture | Power | Description |
|---------|-------|-------------|
| 🖐 **Open Palm** | Mystic Shield | Rotating mandala with geometric rune patterns |
| 🤏 **Pinch** | Energy Attack Beam | Glowing beam trail with sparks from fingertips |
| ✌✌ **Two-Hand Rotate** | Sling Ring Portal | Spinning sparking ring between both hands |

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- A webcam

### Installation

```bash
# Navigate to the project
cd MysticHand

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

Press **Q** to quit.

## 🏗 Architecture

```
Webcam → OpenCV → MediaPipe Hand Tracking → Gesture Recognition → Magic Effects Engine → Display
```

### File Structure

| File | Purpose |
|------|---------|
| `main.py` | App entry point, webcam loop, orchestration |
| `hand_tracker.py` | MediaPipe hand detection wrapper |
| `gesture_recognizer.py` | Gesture classification from landmarks |
| `effects_engine.py` | Particle system + all magic visual effects |
| `utils.py` | Color palette, math helpers |

## 🎨 How It Works

1. **Hand Tracking** — MediaPipe detects 21 hand landmarks per hand in real-time
2. **Gesture Recognition** — Finger extension states and distances classify the gesture
3. **Effects Engine** — A particle system renders Doctor Strange-style glowing effects directly on the camera feed

## 🔧 Customization

- **Colors**: Edit the color palette in `utils.py` (BGR format)
- **Sensitivity**: Adjust detection/tracking confidence in `main.py`
- **Effects**: Tweak particle count, lifetime, and glow in `effects_engine.py`

## 📝 License

This project is for educational and personal use.
