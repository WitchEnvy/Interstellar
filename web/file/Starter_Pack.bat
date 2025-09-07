@echo off
setlocal enabledelayedexpansion
title Interstellar Starter Pack
color 0a

echo ============================================
echo     Interstellar Starter Pack Setup
echo ============================================
echo.

:: Step 1: Install pip jika belum ada
echo [*] Memastikan pip tersedia...

python -m pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [*] pip tidak ditemukan, mencoba menginstal pip...
    curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    del get-pip.py
)

:: Step 2: Upgrade pip
echo [*] Meng-upgrade pip...
python -m pip install --upgrade pip
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Gagal upgrade pip
    goto selesai
)

:: Step 3: Install dependencies
echo [*] Menginstal paket: pyserial, keyboard, opencv-python, mss, numpy
python -m pip install pyserial keyboard opencv-python mss numpy
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Gagal menginstal paket
    goto selesai
)

echo.
echo ============================================
echo  ✅ Semua paket berhasil diinstal!
echo  Silakan jalankan interstellar.bat
echo ============================================

:selesai
pause
exit
