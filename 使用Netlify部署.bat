@echo off
chcp 65001 >nul
title 使用Netlify部署网站
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║          使用Netlify部署网站（公网访问）                 ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [步骤1] 检查文件...
if not exist "中际旭创_价格预测.html" (
    echo [错误] 未找到HTML文件
    echo 请先运行: 运行预测模型.bat
    pause
    exit /b 1
)

echo [OK] HTML文件存在
echo.

echo [步骤2] 准备部署文件...
echo.

REM 创建临时部署文件夹
set DEPLOY_DIR=netlify_deploy
if exist "%DEPLOY_DIR%" (
    rmdir /s /q "%DEPLOY_DIR%"
)
mkdir "%DEPLOY_DIR%"

REM 复制文件到部署文件夹
copy "中际旭创_价格预测.html" "%DEPLOY_DIR%\" >nul
copy "中际旭创_价格预测模型.png" "%DEPLOY_DIR%\" >nul 2>&1
copy "中际旭创_多因素散点图.png" "%DEPLOY_DIR%\" >nul 2>&1
copy "中际旭创_特征重要性详细分析.png" "%DEPLOY_DIR%\" >nul 2>&1
copy "中际旭创_所有因素散点图_第1页.png" "%DEPLOY_DIR%\" >nul 2>&1
if exist "index.html" copy "index.html" "%DEPLOY_DIR%\" >nul 2>&1

echo [OK] 文件已准备到: %DEPLOY_DIR% 文件夹
echo.

echo ╔══════════════════════════════════════════════════════════╗
echo ║          部署步骤                                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 1. 访问: https://www.netlify.com/
echo.
echo 2. 注册/登录账号（可用GitHub账号）
echo.
echo 3. 在Netlify首页，找到拖拽区域
echo    "Want to deploy a new site without connecting to Git?"
echo    "Drag and drop your site output folder here"
echo.
echo 4. 打开文件夹: %CD%\%DEPLOY_DIR%
echo.
echo 5. 将整个文件夹拖拽到Netlify页面
echo.
echo 6. 等待几秒钟，Netlify会自动生成网站地址
echo.
echo 7. 您的网站地址类似:
echo    https://random-name-12345.netlify.app
echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM 打开文件夹
explorer "%CD%\%DEPLOY_DIR%"

echo [信息] 已打开部署文件夹
echo [提示] 请按照上述步骤在Netlify上部署
echo.

pause

