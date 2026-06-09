# Birthday-Cake
To the best Mom 


# 🎂 Happy Birthday Mama

## Files
```
birthday_cam.py          ← main Python script (Experimenting with OpenCV)
birthday_blow.ino        ← where the hardware connects with the software
cake_with_candle.png     ← A picture of a birthday cake with candles
cake_blown.png           ← Same photo but with candles turned off
```

---

## 1. Setting up Python

```bash
pip install opencv-python pyserial numpy
```

---

## 2. Arduino Setup

### Hardware needed
- Arduino Uno (or Nano / Mega)
- KY-038 sound sensor module (cheap, ~$2 on Amazon)

### Wiring
| Sensor Pin | Arduino Pin |
|------------|-------------|
| VCC        | 5V          |
| GND        | GND         |
| DO         | Pin 2       |

### Upload the sketch
1. Open `birthday_blow.ino` in Arduino IDE
2. Select your board and port (Tools → Port)
3. Upload
4. Open Serial Monitor at **9600 baud** — blow into the mic, you should see `BLOW`
5. Adjust the **blue potentiometer** on the sensor until it triggers reliably on a blow but not on quiet breathing

---

## 3. Configure the Python Script

Open `birthday_cam.py` and set your serial port at the top:

```python
SERIAL_PORT = "COM3"         # Windows
# SERIAL_PORT = "/dev/ttyUSB0"   # Linux
# SERIAL_PORT = "/dev/cu.usbmodem14101"  # Mac
```

---

## 4. Cake Images

You need two transparent PNG files in the same folder as the script:

| File | Description |
|------|-------------|
| `cake_with_candle.png` | Cake with a lit candle (~200×200px, transparent background) |
| `cake_blown.png`       | Same cake with candle blown out (smoke wisp optional!) |

**Easy options:**
- Search "birthday cake PNG transparent" on Google Images or [pngwing.com](https://www.pngwing.com)
- Use any image editor (Canva, Photoshop, even Paint 3D) to make simple versions
- If images are missing, the app falls back to text placeholders so it still works!

---

## 5. Run It

```bash
python birthday_cam.py
```

### Keyboard shortcuts (while running)
| Key | Action |
|-----|--------|
| `B` | Simulate a blow (test without Arduino) |
| `R` | Reset — relight the candle |
| `Q` | Quit |

---

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

---

## Troubleshooting

**Serial port not found**
- Check Device Manager (Windows) or `ls /dev/tty*` (Mac/Linux)
- Make sure Arduino IDE is closed (it locks the port)

**Face not detecting**
- Make sure you have good lighting
- Adjust `FACE_NEIGHBORS` (lower = more sensitive, more false positives)

**Sensor triggers too easily / not enough**
- Turn the blue potentiometer on the KY-038 slowly
- Clockwise = less sensitive, Counter-clockwise = more sensitive

---

Happy Birthday! 🎉
