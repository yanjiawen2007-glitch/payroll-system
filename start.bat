@echo off
title Payroll Anytime

python main.py

if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to exit...
    pause
)
