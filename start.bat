@echo off
title Payroll System
setlocal EnableDelayedExpansion

REM Set code page
chcp 65001 >nul 2>&1

REM Change to script directory
cd /d "%~dp0"

REM Show current directory
echo ======================================
echo     Payroll System
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
echo     Starting Payroll System...
echo ======================================
echo.

REM Run main program
python main.py

REM Check result
if %errorlevel% equ 0 (
    echo.
    echo ======================================
    echo     Program exited normally
    echo ======================================
) else (
    echo.
    echo ======================================
    echo     Program error
    echo     Error code: %errorlevel%
    echo ======================================
    echo.
    echo Possible reasons:
    echo   1. Python dependencies not installed
    echo   2. Database file permission issue
    echo   3. Python version incompatible (Python 3.8+ recommended)
    echo.
)

pause
