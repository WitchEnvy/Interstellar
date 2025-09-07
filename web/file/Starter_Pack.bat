@echo off
title Interstellar Starter Pack
color 0a

echo ============================================
echo     Interstellar Starter Pack Setup
echo ============================================
echo.

echo [*] Installing required packages for Interstellar app...

python -m pip install --upgrade pip
python -m pip install pyserial keyboard opencv-python mss numpy

echo.
echo ============================================
echo  ✅ Semua paket berhasil diinstal.
echo  Silakan jalankan interstellar.bat untuk memulai app.
echo ============================================

pause
