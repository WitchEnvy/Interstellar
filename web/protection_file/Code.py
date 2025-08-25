import cv2
import numpy as np
import mss
import serial
import time
import threading
import win32api
import win32con
import ctypes

# --- SETTING SERIAL ---
ser = serial.Serial('COM4', 115200, timeout=0)

# --- SETTING RESOLUSI GAME ---
game_w, game_h = 1440, 900   # resolusi game
user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)

# offset biar pas kalau game ditengah (centered)
offset_x = (screen_w - game_w) // 2
offset_y = (screen_h - game_h) // 2

# --- AIM CONFIG ---
scan_box = 200  # area deteksi sekitar crosshair
target_color_low = np.array([0, 120, 120])   # HSV merah lower
target_color_high = np.array([10, 255, 255]) # HSV merah upper

SMOOTH = 0.3   # smoothing gerakan
last_dx, last_dy = 0, 0

# state
running = True
last_offset = None

def is_pressed(key_hex):
    return win32api.GetAsyncKeyState(key_hex) & 0x8000 != 0

def aim_loop():
    global running, last_dx, last_dy
    global last_offset

    with mss.mss() as sct:
        # posisi crosshair (tengah layar game, bukan monitor)
        cx = offset_x + game_w // 2
        cy = offset_y + game_h // 2

        while running:
            # kalau F2 ditekan -> stop
            if is_pressed(win32con.VK_F2):
                running = False
                break

            # ambil gambar area sekitar crosshair
            monitor = {
                "top": cy - scan_box // 2,
                "left": cx - scan_box // 2,
                "width": scan_box,
                "height": scan_box
            }
            img = np.array(sct.grab(monitor))

            # convert ke HSV biar gampang cari merah
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, target_color_low, target_color_high)

            # cari kontur (objek merah)
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                if cv2.contourArea(c) > 30:  # skip noise kecil
                    (x, y, w, h) = cv2.boundingRect(c)
                    target_x = x + w // 2
                    target_y = y + h // 2

                    dx = target_x - scan_box // 2
                    dy = target_y - scan_box // 2

                    # smoothing biar ga loncat2
                    smooth_dx = int(last_dx * (1 - SMOOTH) + dx * SMOOTH)
                    smooth_dy = int(last_dy * (1 - SMOOTH) + dy * SMOOTH)

                    last_dx, last_dy = smooth_dx, smooth_dy

                    try:
                        cmd = f"{smooth_dx},{smooth_dy}\n"
                        ser.write(cmd.encode())
                        ser.flush()
                    except Exception as e:
                        print(f"Error serial: {e}")

            time.sleep(0.01)  # delay biar CPU ga 100%


if __name__ == "__main__":
    t = threading.Thread(target=aim_loop, daemon=True)
    t.start()

    print("Aim assist jalan. Tekan F2 untuk stop.")
    while running:
        time.sleep(0.1)

    ser.close()
    print("Stopped.")
