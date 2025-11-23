@echo off
chcp 65001 >nul
title 快速部署到GitHub Pages
color 0A

echo.
echo ========================================
echo 快速部署到GitHub Pages
echo ========================================
echo.

REM 添加Git到PATH（临时）
set "PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

REM 检查Git
where git >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] Git未在PATH中
    echo.
    echo 请先运行: 添加Git到PATH.bat（以管理员身份运行）
    echo 或重启电脑
    echo.
    pause
    exit /b 1
)

echo [OK] Git已可用
git --version
echo.

REM 检查文件
if not exist "中际旭创_价格预测.html" (
    echo [警告] 未找到HTML文件
    echo.
    echo 请先运行: 运行预测模型.bat 生成HTML文件
    echo.
    pause
    exit /b 1
)

echo [OK] 找到HTML文件
echo.

REM 检查是否已有Git仓库
if exist ".git" (
    echo [信息] 当前目录已是Git仓库
    git remote -v
    echo.
) else (
    echo [信息] 当前目录不是Git仓库，将初始化
    echo.
)

echo ========================================
echo 部署步骤
echo ========================================
echo.
echo 1. 创建GitHub Personal Access Token
echo    访问: https://github.com/settings/tokens
echo    创建新Token，权限选择 'repo'
echo.
echo 2. 创建GitHub仓库
echo    访问: https://github.com/new
echo    创建Public仓库
echo.
echo 3. 运行Python部署脚本
echo.
echo ========================================
echo.

set /p choice="是否现在运行Python部署脚本? (y/n): "
if /i not "%choice%"=="y" (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo 正在启动部署脚本...
echo.

REM 运行Python脚本
if exist "C:\Users\syy\Python313\python.exe" (
    "C:\Users\syy\Python313\python.exe" 部署到GitHub_Pages.py
) else (
    python 部署到GitHub_Pages.py
)

pause

