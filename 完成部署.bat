@echo off
chcp 65001 >nul
title 完成GitHub部署
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        完成GitHub Pages部署                             ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [步骤1] 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/yishashawn/stock-prediction.git
git remote -v
echo.

echo [步骤2] 配置Git编码...
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
echo.

echo [步骤3] 添加文件...
git add "中际旭创_价格预测.html" 2>nul
git add "index.html" 2>nul
git add "中际旭创_价格预测模型.png" 2>nul
git add "中际旭创_多因素散点图.png" 2>nul
git add "中际旭创_特征重要性详细分析.png" 2>nul
git add "中际旭创_所有因素散点图_*.png" 2>nul
echo [OK] 文件已添加
echo.

echo [步骤4] 提交更改...
git commit -m "首次部署：中际旭创股票价格预测" 2>&1
echo.

echo [步骤5] 推送到GitHub...
echo.
echo ═══════════════════════════════════════════════════════════
echo ⚠️ 重要提示
echo ═══════════════════════════════════════════════════════════
echo.
echo 当提示输入凭据时:
echo   用户名: 435256553@qq.com
echo   密码: [您的Personal Access Token]
echo.
echo 注意: 密码处输入的是Token，不是GitHub密码！
echo ═══════════════════════════════════════════════════════════
echo.
pause

git push -u origin main
if errorlevel 1 (
    echo.
    echo [错误] 推送失败
    echo.
    echo 可能的原因:
    echo 1. Token错误或过期
    echo 2. Token权限不足（需要 'repo' 权限）
    echo 3. 网络问题
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo [成功] 部署完成！
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo 您的网站地址:
    echo   https://yishashawn.github.io/stock-prediction/
    echo.
    echo 下一步: 启用GitHub Pages
    echo 1. 访问: https://github.com/yishashawn/stock-prediction/settings/pages
    echo 2. Source: 选择 main 和 / (root)
    echo 3. 点击 Save
    echo 4. 等待1-5分钟，网站即可访问
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo.
)

pause
