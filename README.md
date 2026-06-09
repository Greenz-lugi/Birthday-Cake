# Birthday-Cake
For Mama's Birthday


# 🎂 Happy Birthday Mama

## Files
```
birthday_cam.py          // main Python script (Experimenting with OpenCV)
birthday_blow.ino        // where the hardware connects with the software
cake_with_candle.png     // A picture of a birthday cake with candles
cake_blown.png           // Same photo but with candles turned off
```

## 1. The Software

```
For the code/understanding what's going on, go to the files.
I put comments explaining the code and the thought process.

This was a unique project for me because it was the first time hardware and software blended in together, so having to learn along the way with Python and combining it with the C++ code for the hardware was unique and new to me.
```

```bash
// Note: you'll have to install OpenCV to use the code
pip install opencv-python pyserial numpy
```

## Arduino Setup

### Hardware used:
- Arduino Uno 
- KY-038 sound sensor

### Wiring
| Sensor Pin | Arduino Pin |
|------------|-------------|
| VCC        | 5V          |
| GND        | GND         |
| DO         | Pin 2       |

```
As for the wiring, you can be creative with your setup.
I had it where the lights turned off alongside the candles.

Just note that you'll need a 220 Ω resistor between your led and where your power comes from.
```

## Keyboard shortcuts (while running)
| Key | Action |
|-----|--------|
| `B` | Simulate a blow (test without Arduino) |
| `R` | Reset — relight the candle |
| `Q` | Quit |

## How It Works

```
Webcam (OpenCV)
  └─ Haar cascade face detection
       └─ if face found → show "Happy Birthday Mom!" + cake overlay

Arduino (sound sensor)
  └─ detects blow (DO pin goes LOW)
       └─ sends "BLOW\n" over USB Serial

Python serial thread
  └─ reads "BLOW"
       └─ swaps cake_with_candle → cake_blown
       └─ spawns confetti particles
       └─ shows "Wish granted!" flash
```

And that's how I made my mother's birthday cake!!
