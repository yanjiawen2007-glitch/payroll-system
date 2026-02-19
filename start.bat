@echo off
title Payroll Anytime Launcher
chcp 65001 >nul 2>&1

echo ==========================================
echo     Payroll Anytime Launcher
echo ==========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] python not found
    echo Please install Python
    echo.
    pause
    exit /b 1
)

python --version
echo.

if not exist "main.py" (
    echo [ERROR] main.py not found
    echo Please run in correct directory
    echo.
    pause
    exit /b 1
)

echo.
echo Starting Payroll Anytime...
echo.

start "" pythonw main.py
