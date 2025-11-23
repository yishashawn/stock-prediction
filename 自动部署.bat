@echo off
chcp 65001 >nul
title 自动部署到GitHub Pages
color 0A

echo.
echo ========================================
echo 自动部署到GitHub Pages
echo ========================================
echo.

REM 添加Git到PATH
set "PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

echo [检查] Git状态...
where git >nul 2>&1
if %errorLevel% neq 0 (
    echo [警告] Git未在PATH中，尝试使用完整路径...
    set "GIT_EXE=C:\Program Files\Git\bin\git.exe"
    if not exist "%GIT_EXE%" (
        echo [错误] Git未找到
        echo 请运行: 添加Git到PATH.bat（以管理员身份运行）
        pause
        exit /b 1
    )
) else (
    git --version
    echo [OK] Git可用
)
echo.

echo [检查] 文件状态...
if not exist "中际旭创_价格预测.html" (
    echo [警告] 未找到HTML文件
    echo.
    set /p gen="是否现在运行预测模型生成HTML? (y/n): "
    if /i "%gen%"=="y" (
        echo.
        echo [信息] 正在运行预测模型...
        if exist "C:\Users\syy\Python313\python.exe" (
            "C:\Users\syy\Python313\python.exe" predict_stock_price_advanced.py
        ) else (
            python predict_stock_price_advanced.py
        )
        echo.
        if not exist "中际旭创_价格预测.html" (
            echo [错误] HTML文件生成失败
            pause
            exit /b 1
        )
        echo [OK] HTML文件已生成
    ) else (
        echo [错误] 需要HTML文件才能部署
        pause
        exit /b 1
    )
) else (
    echo [OK] HTML文件存在
)
echo.

echo ========================================
echo 准备部署
echo ========================================
echo.
echo 请确保您已:
echo   1. 创建GitHub Personal Access Token
echo      访问: https://github.com/settings/tokens
echo.
echo   2. 创建GitHub仓库（Public）
echo      访问: https://github.com/new
echo.
echo ========================================
echo.

set /p ready="是否已完成上述准备? (y/n): "
if /i not "%ready%"=="y" (
    echo.
    echo 请先完成准备工作，然后再次运行此脚本
    echo 详细步骤请查看: 部署说明_完整版.md
    echo.
    pause
    exit /b 0
)

echo.
echo [信息] 正在启动部署脚本...
echo [提示] 请按照提示输入信息
echo.

REM 运行Python部署脚本
if exist "C:\Users\syy\Python313\python.exe" (
    "C:\Users\syy\Python313\python.exe" "部署到GitHub_Pages.py"
) else (
    python "部署到GitHub_Pages.py"
)

echo.
echo ========================================
echo 部署脚本已运行完成
echo ========================================
echo.
echo 如果部署成功，请:
echo   1. 在GitHub仓库页面启用GitHub Pages
echo      设置 → Pages → Source选择main分支
echo.
echo   2. 等待1-2分钟，然后访问您的网站
echo.
pause

