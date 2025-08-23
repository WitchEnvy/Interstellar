@echo off
cd /d %~dp0

echo Menjalankan Envy System Final
echo.

REM Pastikan Python tersedia
where python >nul 2>nul || (
    echo ❌ Python tidak ditemukan di PATH.
    pause
    exit /b
)

REM Jalankan rev01.py
python RevFinal.py

echo.
echo [✅] Program selesai. Tekan tombol apapun untuk keluar...
pause
