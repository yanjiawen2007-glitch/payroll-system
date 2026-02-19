@echo off
title 工资核算系统
setlocal EnableDelayedExpansion

REM 设置控制台编码
chcp 65001 >nul 2>&1

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 显示当前目录
echo ======================================
echo     工资核算系统
echo ======================================
echo.
echo 当前目录: %cd%
echo.

REM 检查 Python 是否存在
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 python 命令
    echo.
    echo 请确保已安装 Python 并添加到系统路径
    echo.
    echo 安装 Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 检查 Python 版本
python --version
echo.

REM 检查主程序是否存在
if not exist "main.py" (
    echo [错误] 未找到 main.py 文件
    echo.
    echo 请确保在正确的目录下运行此脚本
    echo.
    pause
    exit /b 1
)

REM 检查 Ollama 是否运行
echo [检查] 检查 Ollama 服务状态...
tasklist /FI "IMAGENAME eq ollama.exe" | find /I "ollama.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo [信息] Ollama 服务正在运行
) else (
    echo [警告] Ollama 服务未运行
    echo [提示] AI 分析功能需要启动 Ollama 服务
    echo.
    echo 启动 Ollama 方法:
    echo   1. 在新的命令提示符中运行: ollama serve
    echo   2. 或者以管理员身份运行: ollama serve --background
    echo.
)

echo.
echo ======================================
echo     正在启动工资核算系统...
echo ======================================
echo.

REM 运行主程序
python main.py

REM 检查程序运行结果
if %errorlevel% equ 0 (
    echo.
    echo ======================================
    echo     程序正常退出
    echo ======================================
) else (
    echo.
    echo ======================================
    echo     程序运行出错
    echo     错误代码: %errorlevel%
    echo ======================================
    echo.
    echo 可能的原因:
    echo   1. Python 依赖未安装 (运行: pip install -r requirements.txt)
    echo   2. 数据库文件权限问题
    echo   3. Python 版本不兼容 (建议: Python 3.8+)
    echo.
)

pause
