@echo off
REM Production startup script for File Gallery Viewer (Windows)

echo === File Gallery Viewer - Production Startup ===
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Error: Virtual environment not found. Please run setup.py first.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if gunicorn is installed
pip show gunicorn >nul 2>&1
if errorlevel 1 (
    echo Installing gunicorn...
    pip install gunicorn==21.2.0
)

REM Load environment variables if .env exists
if exist ".env" (
    echo Loading environment variables from .env...
    for /f "usebackq tokens=*" %%a in (".env") do (
        set "%%a"
    )
)

REM Set default values
if not defined FLASK_ENV set FLASK_ENV=production
if not defined DATA_DIR set DATA_DIR=%cd%\data
if not defined PORT set PORT=9000
if not defined GUNICORN_WORKERS set GUNICORN_WORKERS=4
if not defined GUNICORN_TIMEOUT set GUNICORN_TIMEOUT=120

REM Create data directory if it doesn't exist
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

echo.
echo Configuration:
echo   Environment: %FLASK_ENV%
echo   Data Directory: %DATA_DIR%
echo   Port: %PORT%
echo   Workers: %GUNICORN_WORKERS%
echo   Timeout: %GUNICORN_TIMEOUT%s
echo.

REM Start gunicorn
echo Starting File Gallery Viewer with Gunicorn...
echo.

gunicorn --bind 0.0.0.0:%PORT% --workers %GUNICORN_WORKERS% --timeout %GUNICORN_TIMEOUT% --access-logfile - --error-logfile - --log-level info backend.app:app
