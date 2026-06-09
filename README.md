# Birthday-Cake
For Mama's Birthday


# 🎂 Happy Birthday Mama

https://github.com/user-attachments/assets/859c477e-7748-4240-ab63-e5b3f8150e85


## Overview of what's in this repo
```
birthday_cam.py          // main Python script (Experimenting with OpenCV)
birthday_blow.ino        // where the hardware connects with the software
cake_with_candle.png     // A picture of a birthday cake with candles
cake_blown.png           // Same photo but with candles turned off
```

## The Software

```
For the code/understanding what's going on, go to the files.
I put comments explaining the code and the thought process.

This was a unique project for me because it was the first time hardware and software blended.
I learned along the way with Python and combined it with the C++ code for the hardware.
```

// Note: you'll have to install OpenCV to use the code
```bash
pip install opencv-python pyserial numpy
```

## The Hardware

### Hardware used:
- Arduino Uno 
- KY-038 sound sensor

### Wiring
| Sensor Pin | Arduino Pin |
|------------|-------------|
| VCC        | 5V          |
| GND        | GND         |
| DO         | Pin 2       |

<p align="center">
  <img src="https://github.com/user-attachments/assets/48b76eba-3c20-4886-af10-14a33376ea9b" width="49%" />
  <img src="https://github.com/user-attachments/assets/2c62a1b0-48f9-4958-906d-d0ef26877038" width="49%" />
</p>

```
As for the wiring, you can be creative with your setup.
I had it where the lights turned off alongside the candles.

Just note that you'll need a 220 Ω resistor between your LED and the power source.
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
