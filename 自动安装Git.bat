@echo off
chcp 65001 >nul
echo ========================================
echo Git for Windows 自动安装工具
echo ========================================
echo.
echo 此脚本将自动下载并安装Git
echo.
echo 注意: 需要管理员权限
echo.
pause

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo 错误: 需要管理员权限
    echo.
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo.
echo 正在启动PowerShell安装脚本...
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0自动安装Git.ps1"

pause

