@echo off
chcp 65001 >nul
title 启动本地网站服务器
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║          启动中际旭创价格预测网站                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM 检查HTML文件
if not exist "中际旭创_价格预测.html" (
    echo [错误] 未找到HTML文件
    echo.
    echo 请先运行: 运行预测模型.bat 生成HTML文件
    echo.
    pause
    exit /b 1
)

echo [OK] HTML文件存在
echo.

REM 检查Python
set PYTHON_EXE=
if exist "C:\Users\syy\Python313\python.exe" (
    set PYTHON_EXE=C:\Users\syy\Python313\python.exe
) else (
    where python >nul 2>&1
    if %errorLevel% equ 0 (
        set PYTHON_EXE=python
    ) else (
        echo [错误] 未找到Python
        pause
        exit /b 1
    )
)

echo [信息] 正在启动Web服务器...
echo [提示] 服务器启动后，会自动打开浏览器
echo [提示] 按 Ctrl+C 停止服务器
echo.

REM 运行Web服务器脚本
"%PYTHON_EXE%" "启动Web服务器.py"

pause

