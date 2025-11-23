@echo off
chcp 65001 >nul
title 启用GitHub Pages
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        启用GitHub Pages                                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [步骤1] 检查文件是否已推送...
git status
echo.

echo [步骤2] 检查远程仓库...
git remote -v
echo.

echo ═══════════════════════════════════════════════════════════
echo 重要提示
echo ═══════════════════════════════════════════════════════════
echo.
echo 如果文件还未推送，请先推送:
echo   git push -u origin main
echo.
echo 然后启用GitHub Pages:
echo 1. 访问: https://github.com/yishashawn/stock-prediction/settings/pages
echo 2. Source: 选择 main 和 / (root)
echo 3. 点击 Save
echo 4. 等待1-5分钟生效
echo.
echo ═══════════════════════════════════════════════════════════
echo.

echo 正在打开GitHub Pages设置页面...
start https://github.com/yishashawn/stock-prediction/settings/pages

echo.
echo 页面已打开，请按照提示操作:
echo 1. Source: 选择 main 和 / (root)
echo 2. 点击 Save
echo 3. 等待1-5分钟
echo.
echo 完成后，访问:
echo   https://yishashawn.github.io/stock-prediction/
echo.

pause

