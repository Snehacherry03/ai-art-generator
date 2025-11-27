@echo off
echo ========================================
echo    ADVANCED AI ART GENERATOR
echo ========================================
echo.
echo Installing required packages...
pip install flask flask-cors pillow numpy

echo.
echo Starting Server...
python app.py
pause