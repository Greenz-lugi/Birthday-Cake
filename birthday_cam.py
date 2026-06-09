import cv2
import numpy as np
import random
import threading
import time
import sys
import os

# for mama :)
from PIL import ImageFont, ImageDraw, Image
import arabic_reshaper # this is to write/shape in arabic so I can be sure it looks well for my mom
from bidi.algorithm import get_display

# ── CONFIGURE THESE ──────────────────────────────────────────────────────────
SERIAL_PORT  = "COM6"      # COM6 will connect the .ino to the python script 
BAUD_RATE    = 9600         # to me was COM6 you can tell in arduino IDE
CAMERA_INDEX = 0            # 0 = built-in webcam
CAKE_HEIGHT  = 300          # cake is 300 pixels tall
# ─────────────────────────────────────────────────────────────────────────────

try:
    import serial as _serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("[Warning] pyserial not installed — serial disabled. Press B to simulate.")


# ── IMAGE UTILITIES ───────────────────────────────────────────────────────────

def black_bg_to_alpha(bgr):
    """
    Convert a BGR image with pure black background to BGRA with transparency.
    Uses luminance-based alpha so cake edges stay smooth and anti-aliased.
    """
    bgra = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Pixels near 0 → transparent, brighter → opaque (ramp over first ~72 levels)
    alpha = np.clip(gray.astype(np.float32) * 3.5, 0, 255).astype(np.uint8)
    bgra[:, :, 3] = alpha
    return bgra


def load_cake(path, target_height):
    """Load cake PNG, remove black background, resize to target height."""
    if not os.path.exists(path):
        print(f"[Warning] Image not found: {path}")
        return None
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"[Warning] Could not read: {path}")
        return None
    # If already has alpha channel use it, otherwise extract from black bg
    if img.shape[2] == 4:
        bgra = img
    else:
        bgra = black_bg_to_alpha(img)
    # Resize keeping aspect ratio
    h, w = bgra.shape[:2]
    scale = target_height / h
    new_w = int(w * scale)
    return cv2.resize(bgra, (new_w, target_height), interpolation=cv2.INTER_AREA)


def overlay_png(frame, img, x, y):
    """Paste a BGRA image onto a BGR frame at pixel position (x, y)."""
    if img is None:
        return
    fh, fw = frame.shape[:2]
    ih, iw = img.shape[:2]

    x1 = max(x, 0);  y1 = max(y, 0)
    x2 = min(x + iw, fw);  y2 = min(y + ih, fh)
    if x2 <= x1 or y2 <= y1:
        return

    roi = frame[y1:y2, x1:x2]
    src = img[y1 - y: y2 - y, x1 - x: x2 - x]
    a   = src[:, :, 3:4].astype(np.float32) / 255.0
    roi[:] = (src[:, :, :3] * a + roi * (1.0 - a)).astype(np.uint8)


# ── TEXT HELPERS ──────────────────────────────────────────────────────────────

def put_text(frame, text, pos, scale=1.0, color=(255, 255, 255), thickness=2):
    x, y = pos
    cv2.putText(frame, text, (x + 2, y + 2), cv2.FONT_HERSHEY_DUPLEX,
                scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_DUPLEX,
                scale, color, thickness, cv2.LINE_AA)


def text_center(frame, text, y, scale=1.0, color=(255, 255, 255), thickness=2):
    (tw, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, thickness)
    x = (frame.shape[1] - tw) // 2
    put_text(frame, text, (x, y), scale, color, thickness)


# ── CONFETTI ──────────────────────────────────────────────────────────────────

CONFETTI_COLORS = [
    (100, 100, 255), (100, 255, 100), (255, 100, 100),
    (255, 255, 100), (255, 100, 255), (100, 255, 255),
    (255, 180, 100), (180, 100, 255),
]


def spawn_confetti(frame_w, n=140):
    return [
        {
            "x":     random.uniform(0, frame_w),
            "y":     random.uniform(-300, -10),
            "vx":    random.uniform(-2.5, 2.5),
            "vy":    random.uniform(4, 9),
            "color": random.choice(CONFETTI_COLORS),
            "w":     random.randint(8, 18),
            "h":     random.randint(5, 10),
            "angle": random.uniform(0, 360),
            "spin":  random.uniform(-6, 6),
        }
        for _ in range(n)
    ]


def update_confetti(frame, particles):
    alive = []
    fh = frame.shape[0]
    for p in particles:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["angle"] += p["spin"]
        if p["y"] < fh + 20:
            cv2.ellipse(frame, (int(p["x"]), int(p["y"])),
                        (p["w"] // 2, p["h"] // 2),
                        p["angle"], 0, 360, p["color"], -1)
            alive.append(p)
    return alive


# ── SERIAL THREAD ─────────────────────────────────────────────────────────────

class ArduinoListener(threading.Thread):
    """Background thread: reads 'BLOW' from Arduino over USB serial."""

    def __init__(self, port, baud):
        super().__init__(daemon=True)
        self.port       = port
        self.baud       = baud
        self.blow_event = threading.Event()
        self.connected  = False

    def run(self):
        if not SERIAL_AVAILABLE:
            return
        try:
            ser = _serial.Serial(self.port, self.baud, timeout=1)
            self.connected = True
            print(f"[Serial] Connected on {self.port} at {self.baud} baud")
            time.sleep(2)   # wait for Arduino bootloader to finish
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    print(f"[Arduino] {line!r}")
                if line == "BLOW":
                    self.blow_event.set()
        except Exception as e:
            print(f"[Serial] Could not open {self.port}: {e}")
            print("[Serial] Running in demo mode — press B to simulate a blow.")

# to write in arabic for us
def draw_arabic(frame, text, y, size=72, color=(255, 240, 100)):
    reshaped = arabic_reshaper.reshape(text)
    display  = get_display(reshaped)
    pil_img  = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw     = ImageDraw.Draw(pil_img)
    font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", size)
    bbox     = draw.textbbox((0, 0), display, font=font)
    x        = (frame.shape[1] - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), display, font=font, fill=(color[2], color[1], color[0]))
    frame[:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    # Load images from same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cake_lit   = load_cake(os.path.join(script_dir, "cake_with_candle.png"), CAKE_HEIGHT)
    cake_blown = load_cake(os.path.join(script_dir, "cake_blown.png"),       CAKE_HEIGHT)

    # Face detectors — frontal + profile so side-blowing poses still register
    face_cascade   = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    profile_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_profileface.xml"
    )

    # Start Arduino listener thread
    arduino = ArduinoListener(SERIAL_PORT, BAUD_RATE)
    arduino.start()

    # Open webcam
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[Error] Cannot open camera {CAMERA_INDEX}.")
        sys.exit(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # State
    blown_out    = False
    confetti     = []
    flash_frames = 0       # countdown for "Wish Granted!" banner

    print("[App] Running!   B = simulate blow  |  R = reset candle  |  Q = quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)   # mirror so it feels natural
        fh, fw = frame.shape[:2]

        # ── Check Arduino blow event ──────────────────────────────────────
        if arduino.blow_event.is_set() and not blown_out:
            arduino.blow_event.clear()
            blown_out    = True
            flash_frames = 100
            confetti     = spawn_confetti(fw)
            print("[Event] Candle blown out!")

        # ── Face detection (frontal + profile) ───────────────────────────
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frontal = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )
        # Profile cascade runs on normal AND flipped to catch both left/right sides
        profile_normal  = profile_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )
        profile_flipped = profile_cascade.detectMultiScale(
            cv2.flip(gray, 1), scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )
        faces = list(frontal) + list(profile_normal) + list(profile_flipped)
        face_visible = len(faces) > 0 or blown_out

        # Draw face rectangles (subtle highlight)
        for (fx, fy, fw2, fh2) in faces:
            cv2.rectangle(frame, (fx, fy), (fx + fw2, fy + fh2),
                          (255, 200, 80), 2)

        # ── Birthday overlay ──────────────────────────────────────────────
        if face_visible:
            text_center(frame, "Happy Birthday Mama!",
                        y=65, scale=1.6, color=(255, 210, 60), thickness=3)

            # Choose lit or blown image
            cake_img = cake_blown if blown_out else cake_lit
            if cake_img is not None:
                cw = cake_img.shape[1]
                ch = cake_img.shape[0]
                overlay_png(frame, cake_img,
                            x=(fw - cw) // 2,
                            y=fh - ch - 20)
            else:
                label = "[ cake_blown.png missing ]" if blown_out else "[ cake_with_candle.png missing ]"
                text_center(frame, label, fh - 40, 0.8, (255, 160, 80))

            if not blown_out:
                text_center(frame, "Blow out the candles to make a wish!",
                            fh - 15, 0.72, (180, 255, 180), 1)
        else:
            text_center(frame, "I can't see you, come closer! :)",
                        fh // 2, 1.0, (180, 180, 255), 2)

        # ── Confetti ──────────────────────────────────────────────────────
        if confetti:
            confetti = update_confetti(frame, confetti)

        # ── "Wish Granted!" flash ─────────────────────────────────────────
        if flash_frames > 0:
            t = flash_frames / 100.0
            intensity = (1.0 - abs(t - 0.5) * 2) * 0.35
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (fw, fh), (80, 60, 220), -1)
            cv2.addWeighted(overlay, intensity, frame, 1 - intensity, 0, frame)
            draw_arabic(frame, "كل سنة وأنتِ سالمة ماما", fh // 2 - 45)
            flash_frames -= 1

        # ── Arduino status dot (top-left) ─────────────────────────────────
        dot_color = (80, 220, 80) if arduino.connected else (80, 80, 220)
        dot_label = "Arduino OK" if arduino.connected else "Demo mode  (B to blow)"
        cv2.circle(frame, (14, 14), 7, dot_color, -1)
        put_text(frame, dot_label, (26, 19), 0.5, dot_color, 1)

        cv2.imshow("Happy Birthday Mama! ", frame)

        # ── Keys ──────────────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("b") and not blown_out:
            blown_out    = True
            flash_frames = 500
            confetti     = spawn_confetti(fw)
            print("[Demo] Simulated blow!")
        elif key == ord("r"):
            blown_out    = False
            confetti     = []
            flash_frames = 0
            print("[Demo] Reset — candle relit!")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__": # entry point
    main()
