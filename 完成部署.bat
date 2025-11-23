@echo off
chcp 65001 >nul
title 完成GitHub Pages部署
color 0A

echo.
echo ========================================
echo 完成GitHub Pages部署
echo ========================================
echo.

set "PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

echo [步骤1] 检查文件...
if not exist "中际旭创_价格预测.html" (
    echo [错误] HTML文件不存在
    echo 请先运行: 运行预测模型.bat
    pause
    exit /b 1
)
echo [OK] HTML文件存在
echo.

echo [步骤2] 添加文件到Git...
git add "中际旭创_价格预测.html" "中际旭创_价格预测模型.png" "中际旭创_多因素散点图.png" "中际旭创_特征重要性详细分析.png" "中际旭创_所有因素散点图_第1页.png" index.html 2>nul
if errorlevel 1 (
    echo [警告] 部分文件可能不存在，继续...
)
echo [OK] 文件已添加
echo.

echo [步骤3] 提交更改...
git commit -m "更新中际旭创股票价格预测网站" 2>&1
if errorlevel 1 (
    echo [信息] 可能没有需要提交的更改
)
echo.

echo [步骤4] 推送到GitHub...
echo [提示] 如果提示输入密码，请使用Personal Access Token
echo.
git push origin main 2>&1
if errorlevel 1 (
    echo.
    echo [错误] 推送失败
    echo.
    echo 可能的原因:
    echo   1. 需要输入GitHub用户名和Token
    echo   2. Token已过期
    echo   3. 网络问题
    echo.
    echo 解决方法:
    echo   1. 确保已创建Personal Access Token
    echo   2. 当提示输入密码时，粘贴Token（不是GitHub密码）
    echo   3. 或手动运行: git push origin main
    echo.
) else (
    echo.
    echo ========================================
    echo 推送成功！
    echo ========================================
    echo.
    echo 下一步: 启用GitHub Pages
    echo   1. 访问: https://github.com/yishashawn/zhongji
    echo   2. 点击 Settings → Pages
    echo   3. Source: 选择 main 分支和 / (root)
    echo   4. 点击 Save
    echo.
    echo 您的网站地址:
    echo   https://yishashawn.github.io/zhongji/中际旭创_价格预测.html
    echo.
)

echo.
pause

