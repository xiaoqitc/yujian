@echo off
chcp 65001 >nul
title 御锋V1网络安全工具箱启动器

echo.
echo ========================================
echo        御锋V1网络安全工具箱
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查主程序文件是否存在
if not exist "御锋V1网络安全工具箱.py" (
    echo [错误] 未找到主程序文件: 御锋V1网络安全工具箱.py
    pause
    exit /b 1
)

:: 检查并安装依赖
echo [信息] 检查依赖包...
pip install -r requirements.txt --quiet

:: 启动程序
echo [信息] 启动御锋V1网络安全工具箱...
echo.
python "御锋V1网络安全工具箱.py"

:: 如果程序异常退出，暂停显示错误信息
if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出，错误代码: %errorlevel%
    pause
)

echo.
echo [信息] 程序已退出
pause 