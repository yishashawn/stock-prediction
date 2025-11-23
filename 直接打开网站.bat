@echo off
chcp 65001 >nul
title 直接打开网站

echo.
echo ========================================
echo 直接打开中际旭创价格预测网站
echo ========================================
echo.

if not exist "中际旭创_价格预测.html" (
    echo [错误] 未找到HTML文件
    echo.
    echo 请先运行: 运行预测模型.bat
    echo.
    pause
    exit /b 1
)

echo [信息] 正在打开网站...
echo.

REM 使用默认浏览器打开HTML文件
start "" "中际旭创_价格预测.html"

echo [OK] 网站已在浏览器中打开
echo.
echo 注意: 这是本地文件，只能在本机访问
echo 如需分享给他人，请使用: 启动本地网站.bat
echo.
pause

