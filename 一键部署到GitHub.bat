@echo off
chcp 65001 >nul
title GitHub Pages 一键部署
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        GitHub Pages 一键部署工具                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM 检查Python
set PYTHON_EXE=
if exist "C:\Users\syy\Python313\python.exe" (
    set PYTHON_EXE=C:\Users\syy\Python313\python.exe
    goto :found_python
)

where python >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=python
    goto :found_python
)

where py >nul 2>&1
if not errorlevel 1 (
    set PYTHON_EXE=py
    goto :found_python
)

:found_python
if "%PYTHON_EXE%"=="" (
    echo [错误] 未找到Python
    echo 请先安装Python或运行: 运行预测模型.bat
    pause
    exit /b 1
)

REM 检查HTML文件
if not exist "中际旭创_价格预测.html" (
    echo [错误] 未找到HTML文件
    echo 请先运行: 运行预测模型.bat
    pause
    exit /b 1
)

echo [步骤1] 检查Git安装...
where git >nul 2>&1
if errorlevel 1 (
    echo [错误] Git未安装
    echo.
    echo 请先安装Git:
    echo 1. 运行: 安装Git_简化版.bat
    echo 2. 或访问: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Git未正确安装
    pause
    exit /b 1
)

echo [OK] Git已安装
echo.

echo [步骤2] 运行部署脚本...
echo.
"%PYTHON_EXE%" 部署到GitHub_Pages.py
if errorlevel 1 (
    echo.
    echo [错误] 部署失败
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo 部署完成！
echo ═══════════════════════════════════════════════════════════
pause
