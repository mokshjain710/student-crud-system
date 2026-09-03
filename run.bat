@echo off
title Student Management System (DBMS CRUD App)
echo =========================================================
echo       Student Management System (DBMS Mini Project)
echo =========================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b
)

echo [1/3] Installing Python dependencies...
python -m pip install -r requirements.txt --quiet

echo [2/3] Starting Student Records Management Server...
start "" http://127.0.0.1:5000

echo [3/3] Server is running! Press Ctrl+C in this window to stop.
echo.
python app.py
pause
