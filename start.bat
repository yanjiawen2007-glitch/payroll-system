@echo off
title Payroll System Launcher
setlocal EnableDelayedExpansion

REM Set code page
chcp 65001 >nul 2>&1

REM Change to script directory
cd /d "%~dp0"

REM Show current directory
echo ======================================
echo     Payroll System Launcher
echo ======================================
echo.
echo Current directory: %cd%
echo.

REM Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] python command not found
    echo.
    echo Please install Python and add to PATH
    echo.
    echo Install Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check Python version
python --version
echo.

REM Check main program
if not exist "main.py" (
    echo [ERROR] main.py not found
    echo.
    echo Please run in correct directory
    echo.
    pause
    exit /b 1
)

REM Check Ollama
echo [CHECK] Checking Ollama service...
tasklist /FI "IMAGENAME eq ollama.exe" | find /I "ollama.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Ollama service is running
) else (
    echo [WARN] Ollama service is NOT running
    echo [TIP] AI analysis needs Ollama service
    echo.
    echo To start Ollama:
    echo   1. Run: ollama serve
    echo   2. Or: ollama serve --background (as admin)
    echo.
)

echo.
echo ======================================
echo     Starting Payroll System in NEW window...
echo ======================================
echo.

REM Start in NEW window
start "Payroll System" pythonw main.py

echo.
echo ======================================
echo     Payroll System started
echo     You can now close this window safely
echo ======================================
echo.
timeout /t 3 >nul
