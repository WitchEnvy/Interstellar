# pip install pyserial keyboard opencv-python mss numpy
import time, math, random, threading, ctypes, sys, re, os
import keyboard
import cv2
import numpy as np
import serial as pyserial
import serial.tools.list_ports as list_ports
import mss

# ── KONFIGURASI GLOBAL ────────────────────────────────────────
BAUD_RATE = 115200
user32    = ctypes.windll.user32
GetKey    = user32.GetAsyncKeyState
GetState  = user32.GetKeyState
VK_CAPS   = 0x14
VK_LMB    = 0x01
VK_RMB    = 0x02
caps  = lambda: GetState(VK_CAPS) & 1
lmb   = lambda: GetKey(VK_LMB) & 0x8000
rmb   = lambda: GetKey(VK_RMB) & 0x8000

REQUIRED_KEY1 = "OM3CMgYkXXh9ADbGUAtapPaknh64vybp"   # Jitter
REQUIRED_KEY2 = "lyWlPOcUN1LR8JHESWOoThm1T3Xrr1Ax"   # Magnet
REQUIRED_KEY3 = "Xk48g9mA5JYqCzK0Gh12ReUtDp99LmQv"   # Gabungan

def find_port(default="COM3"):
    for p in list_ports.comports():
        if re.search(r"(Arduino|USB Serial Device)", p.description, re.I):
            return rf"\\.\{p.name}"
    return rf"\\.\{default}"

# ============================================================== #
# 1. ONLY JITTER MODE
# ============================================================== #

SHAKE_PX   = 4
SHAKE_HZ   = 25
PULL_DOWN  = 0.3
RANDOMIZE  = False

def jitter_loop(ser):
    phase = 0.0
    dt    = 1 / 240
    acc_dy = 0.0
    paused = False

    print("🔄 Jitter: Tahan CAPSLOCK + LMB + RMB untuk aktif.")
    print("⛔ Tekan F11 untuk pause/resume, F10 untuk kembali ke menu.")

    while True:
        start = time.time()

        if keyboard.is_pressed("f11"):
            paused = not paused
            if paused:
                print("⏸️  Jitter *PAUSED* (F11)")
                ser.write(b'x\n')
            else:
                print("▶️  Jitter *AKTIF* (F11)")
            time.sleep(0.4)

        if keyboard.is_pressed("f10"):
            print("⬅️  Jitter: Kembali ke menu utama...")
            time.sleep(1)
            break

        if paused:
            time.sleep(0.01)
            continue

        if caps() and lmb() and rmb():
            phase += dt * SHAKE_HZ * 2 * math.pi
            dx = random.uniform(-SHAKE_PX, SHAKE_PX) if RANDOMIZE else SHAKE_PX * math.sin(phase)
            acc_dy += PULL_DOWN
            dy = int(acc_dy)
            acc_dy -= dy
            ser.write(f"{int(round(dx))},{dy}\n".encode())
            ser.flush()
        else:
            phase = 0
            acc_dy = 0.0
            time.sleep(0.005)

        elapsed = time.time() - start
        if elapsed < dt:
            time.sleep(dt - elapsed)

def run_jitter_mode():
    key = input("Masukkan Key untuk Jitter Mode: ").strip()
    if key != REQUIRED_KEY1:
        print("❌ Key salah! Akses ditolak.")
        time.sleep(2)
        return

    port = find_port()
    print(f"⏳ Menghubungkan ke {port} ...")
    try:
        ser = pyserial.Serial(port, BAUD_RATE, timeout=0, write_timeout=0.01)
    except pyserial.SerialException as e:
        sys.exit(f"❌ Port gagal dibuka: {e}")
    print("✅ Terhubung ke Arduino.")
    jitter_loop(ser)

# ============================================================== #
# 2. MAGNET COLOR RED
# ============================================================== #

SCAN_WIDTH = 48
SCAN_HEIGHT = 36
PULL_STRENGTH_COLOR = 0.7  # <= Disesuaikan untuk sensitivitas tinggi
SLEEP_DELAY = 1 / 165
HSV_RED_1 = (0, 150, 150)
HSV_RED_2 = (10, 255, 255)
HSV_RED_3 = (160, 150, 150)
HSV_RED_4 = (179, 255, 255)

def get_color_mask_red(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, np.array(HSV_RED_1), np.array(HSV_RED_2))
    mask2 = cv2.inRange(hsv, np.array(HSV_RED_3), np.array(HSV_RED_4))
    return cv2.bitwise_or(mask1, mask2)

def aim_loop(ser):
    last_offset = None
    with mss.mss() as sct:
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        monitor = {
            "left": (screen_w // 2) - SCAN_WIDTH // 2,
            "top": (screen_h // 2) - SCAN_HEIGHT // 2,
            "width": SCAN_WIDTH,
            "height": SCAN_HEIGHT
        }
        print("🎯 Magnet aktif: Titik Hijau ke Merah")
        print("- CAPSLOCK ON + Klik Kiri + Kanan")
        print("- CAPSLOCK OFF + Klik Kanan saja")
        print("⛔ Tekan F11 untuk pause/resume, F10 untuk kembali ke menu.")

        paused = False
        while True:
            if keyboard.is_pressed("f11"):
                paused = not paused
                print("⏸️  Magnet *PAUSED* (F11)" if paused else "▶️  Magnet *AKTIF* (F11)")
                time.sleep(0.4)

            if keyboard.is_pressed("f10"):
                print("⬅️  Magnet: Kembali ke menu utama...")
                time.sleep(1)
                break

            if paused:
                time.sleep(0.01)
                continue

            aktif = (caps() and lmb() and rmb()) or (not caps() and rmb())
            if not aktif:
                time.sleep(0.01)
                last_offset = None
                continue

            img = np.array(sct.grab(monitor))
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            mask_red = get_color_mask_red(img)
            center_x = img.shape[1] // 2
            center_y = img.shape[0] // 2
            contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                def dist(cnt):
                    M = cv2.moments(cnt)
                    if M["m00"] == 0: return float("inf")
                    cx = M["m10"] / M["m00"]
                    cy = M["m01"] / M["m00"]
                    return (cx - center_x)**2 + (cy - center_y)**2
                closest = min(contours, key=dist)
                M = cv2.moments(closest)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    dx = int((cx - center_x) * PULL_STRENGTH_COLOR)
                    dy = int((cy - center_y) * PULL_STRENGTH_COLOR)
                    last_offset = (dx, dy, cx, cy)
                else:
                    last_offset = None
            else:
                last_offset = None

            if last_offset:
                dx, dy, cx, cy = last_offset
                try:
                    cmd = f"{dx},{dy}\n"
                    ser.write(cmd.encode())
                    ser.flush()
                except Exception as e:
                    print(f"Error kirim serial: {e}")
                cv2.circle(img, (center_x, center_y), 5, (0, 255, 0), -1)
                cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)
            else:
                cv2.circle(img, (center_x, center_y), 5, (0, 255, 0), -1)

            cv2.imshow("Magnet Titik Hijau ke Merah", img)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            time.sleep(SLEEP_DELAY)

def run_magnet_mode():
    key = input("Masukkan Key untuk Magnet Mode: ").strip()
    if key != REQUIRED_KEY2:
        print("❌ Key salah! Akses ditolak.")
        time.sleep(2)
        return

    port = find_port()
    print(f"⏳ Menghubungkan ke {port}...")
    try:
        ser = pyserial.Serial(port, BAUD_RATE, timeout=0, write_timeout=0.01)
    except pyserial.SerialException as e:
        sys.exit(f"⚠️ Port gagal dibuka: {e}")
    print("✅ Terhubung ke Arduino.")
    aim_loop(ser)
    cv2.destroyAllWindows()

# ============================================================== #
# 3. COMBINED MODE (JITTER + MAGNET)
# ============================================================== #

def run_combined_mode():
    key = input("Masukkan Key untuk Mode Gabungan (Jitter + Magnet): ").strip()
    if key != REQUIRED_KEY3:
        print("❌ Key salah! Akses ditolak.")
        time.sleep(2)
        return

    port = find_port()
    print(f"⏳ Menghubungkan ke {port}...")
    try:
        ser = pyserial.Serial(port, BAUD_RATE, timeout=0, write_timeout=0.01)
    except pyserial.SerialException as e:
        sys.exit(f"⚠️ Port gagal dibuka: {e}")
    print("✅ Terhubung ke Arduino.")

    jitter_thread = threading.Thread(target=jitter_loop, args=(ser,))
    magnet_thread = threading.Thread(target=aim_loop, args=(ser,))

    jitter_thread.start()
    magnet_thread.start()

    jitter_thread.join()
    magnet_thread.join()
    cv2.destroyAllWindows()

# ============================================================== #
# MENU UTAMA
# ============================================================== #

def main_menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("=======================================")
        print("           Interstellar | M&K")
        print("=======================================")
        print("1. Only Jitter Mode")
        print("2. Aim Assist For M&K (Only Recon Legends)")
        print("3. Gabungkan Jitter + Magnet")
        print("4. Keluar")
        print("=======================================")
        pilihan = input("Pilih menu (1/2/3/4): ")

        if pilihan == "1":
            run_jitter_mode()
        elif pilihan == "2":
            run_magnet_mode()
        elif pilihan == "3":
            run_combined_mode()
        elif pilihan == "4":
            print("Keluar...")
            break
        else:
            print("Pilihan tidak valid!")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
