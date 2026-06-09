@echo off
setlocal
echo 🚀 Launching EduCare Full Build Pipeline...
echo --------------------------------------------------
echo.

:: 1. Activate Virtual Environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found. Please run: python -m venv venv
    pause
    exit /b
)

:: 2. Database Migrations
echo [1/6] Initializing Database Schema...
python manage.py migrate

:: 3. Seed Synthetic Data
echo [2/6] Seeding 100%% Synthetic Data (Teacher/Counselor Sync)...
python seed_data.py

:: 4. Upgrade UI
echo [3/6] Applying Professional Enterprise UI Templates...
python upgrade_ui.py

:: 5. Run AI Scraper
echo [4/6] Executing MCP/A2A AI Scraper (Decision Support Data)...
python advanced_scraper.py

:: 6. Verification (NEW)
echo [5/6] Running System Integrity & Security Tests...
python manage.py test school_app

:: 7. Launch Server
echo [6/6] ✅ System Ready. Launching Server...
echo Portal accessible at: http://127.0.0.1:8000/
echo.
python manage.py runserver

pause
