@echo off
chcp 65001 >nul 2>&1

echo ==========================================
echo     Payroll Anytime - Diagnostic Mode
echo ==========================================
echo.

REM 显示当前目录
echo [INFO] Current directory: %cd%
echo.

REM 检查Python
echo [INFO] Checking Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH
    echo.
    echo Trying to find Python manually...
    for %%i in (
        "C:\Python39\python.exe"
        "C:\Python38\python.exe"
        "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe"
        "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python38\python.exe"
        "C:\Program Files\Python39\python.exe"
        "C:\Program Files\Python38\python.exe"
    ) do (
        if exist "%%~i" (
            echo [INFO] Found Python at: %%~i
            set PYTHON_EXE=%%~i
            goto :python_found
        )
    )
    echo [ERROR] Python not found anywhere
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo [INFO] Python found in PATH
    for /f "tokens=*" %%i in ('where python') do (
        echo [INFO] Python path: %%~i
        set PYTHON_EXE=%%~i
        goto :python_found
    )
)

:python_found
echo.

REM 测试Python
echo [INFO] Testing Python...
"%PYTHON_EXE%" --version
if %errorlevel% neq 0 (
    echo [ERROR] Python test failed
    pause
    exit /b 1
)
echo [SUCCESS] Python works!
echo.

REM 检查main.py
echo [INFO] Checking main.py...
if not exist "main.py" (
    echo [ERROR] main.py not found in: %cd%
    echo.
    echo Files in current directory:
    dir /b
    echo.
    pause
    exit /b 1
)
echo [SUCCESS] main.py exists!
echo.

REM 检查database.py
echo [INFO] Checking database.py...
if not exist "database.py" (
    echo [ERROR] database.py not found
    pause
    exit /b 1
)
echo [SUCCESS] database.py exists!
echo.

REM 检查其他依赖
echo [INFO] Checking dependencies...
if not exist "excel_handler.py" (
    echo [WARN] excel_handler.py not found
)
if not exist "ollama_analyzer.py" (
    echo [WARN] ollama_analyzer.py not found
)
echo.

REM 检查Ollama
echo [INFO] Checking Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" | find /I "ollama.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Ollama service is running
) else (
    echo [WARN] Ollama service is NOT running
    echo [TIP] Start Ollama with: ollama serve
    echo.
)
echo.

REM 显示准备启动
echo ==========================================
echo     Starting Payroll Anytime...
echo ==========================================
echo.
echo [INFO] Using Python: %PYTHON_EXE%
echo [INFO] Starting: python main.py
echo.

REM 启动程序
"%PYTHON_EXE%" main.py

REM 检查结果
if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo     Program exited normally
    echo ==========================================
) else (
    echo.
    echo ==========================================
    echo     Program ERROR
    echo ==========================================
    echo.
    echo Error code: %errorlevel%
    echo.
    echo Possible reasons:
    echo   1. Missing dependencies (run: pip install -r requirements.txt)
    echo   2. Database file permissions
    echo   3. Python version incompatible (Python 3.8+ recommended)
    echo   4. Code error in main.py
    echo.
)

pause
