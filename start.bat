@echo off
chcp 65001 >nul 2>&1

echo ======================================
echo     Payroll System Launcher
echo ======================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] python not found
    echo Please install Python
    pause
    exit /b 1
)

python --version

if not exist "main.py" (
    echo [ERROR] main.py not found
    pause
    exit /b 1
)

echo.
echo Starting Payroll System...
echo.

start "" pythonw main.py
