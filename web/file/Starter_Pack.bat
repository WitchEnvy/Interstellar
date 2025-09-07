@echo off
setlocal enabledelayedexpansion
title Interstellar Starter Pack
color 0a

echo ============================================
echo        Interstellar Starter Pack Setup
echo ============================================
echo.

echo [*] Installing required packages for Interstellar app...
python -m pip install --upgrade pip || echo [ERROR] Failed to upgrade pip
python -m pip install pyserial keyboard opencv-python mss numpy || echo [ERROR] Failed installing some packages

echo.
echo ============================================
echo  ✅ Starter_Pack has done.
echo  Please run interstellar.bat to start the app
echo ============================================

pause
