@echo off
title Interstellar Starter Pack
color 0a

echo ============================================
echo        Interstellar Starter Pack Setup
echo ============================================
echo.

REM ==== Cek apakah Python sudah ada ====
echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found. Please install Python 3.11 manually from:
    echo     https://www.python.org/downloads/release/python-3110/
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b
) else (
    for /f "tokens=2 delims= " %%v in ('python --version') do set PYVERSION=%%v
    echo [+] Python %PYVERSION% detected.
)

echo.
echo [*] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [*] Installing required packages...
pip install opencv-python numpy mss pyserial keyboard requests beautifulsoup4

echo.
echo ============================================
echo  Stater_Pack has done.
echo  Please run interstellar.bat to start app
echo ============================================

echo.
pause
