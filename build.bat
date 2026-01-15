@echo off
echo Building executable...
echo.
echo Installing PyInstaller if needed...
pip install pyinstaller

echo.
echo Building single exe file...
pyinstaller --onefile --windowed --name "QR-Text-Overlay" --icon=NONE main.py

echo.
echo Build complete!
echo Executable is in: dist\QR-Text-Overlay.exe
echo.
pause
