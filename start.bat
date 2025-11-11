@echo off
echo Starting File Gallery Viewer...

if not exist "venv\" (
    echo Setting up environment...
    python setup.py
)

echo Starting backend...
call venv\Scripts\activate.bat
start /b python backend/app.py

echo Opening frontend...
timeout /t 3 /nobreak >nul
start frontend/index.html

echo File Gallery Viewer is running!
echo Backend: http://localhost:5000
echo Press any key to stop...
pause >nul

echo Stopping backend...
taskkill /f /im python.exe >nul 2>&1