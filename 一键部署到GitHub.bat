@echo off
chcp 65001 >nul
title 一键部署到GitHub Pages
color 0A

echo.
echo ========================================
echo 一键部署到GitHub Pages
echo ========================================
echo.

REM 添加Git到PATH
set "PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

echo [步骤1] 检查Git...
where git >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] Git未在PATH中
    echo 请先运行: 添加Git到PATH.bat（以管理员身份运行）
    pause
    exit /b 1
)

git --version
echo [OK] Git可用
echo.

echo [步骤2] 检查文件...
if not exist "中际旭创_价格预测.html" (
    echo [警告] 未找到HTML文件
    echo 请先运行: 运行预测模型.bat
    pause
    exit /b 1
)
echo [OK] HTML文件存在
echo.

echo ========================================
echo 部署前准备
echo ========================================
echo.
echo 请确保已完成:
echo   1. ✓ 创建GitHub Personal Access Token
echo      访问: https://github.com/settings/tokens
echo      创建新Token，权限选择 'repo'
echo.
echo   2. ✓ 创建GitHub仓库
echo      访问: https://github.com/new
echo      创建Public仓库，复制仓库URL
echo.
echo ========================================
echo.

set /p ready="是否已完成上述准备? (y/n): "
if /i not "%ready%"=="y" (
    echo.
    echo 请先完成准备工作:
    echo   1. 查看: 创建GitHub_Token指南.md
    echo   2. 创建Token和仓库后，再次运行此脚本
    echo.
    pause
    exit /b 0
)

echo.
echo [步骤3] 运行部署脚本...
echo.

if exist "C:\Users\syy\Python313\python.exe" (
    "C:\Users\syy\Python313\python.exe" "部署到GitHub_Pages.py"
) else (
    python "部署到GitHub_Pages.py"
)

echo.
pause

