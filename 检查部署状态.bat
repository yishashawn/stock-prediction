@echo off
chcp 65001 >nul
title 检查GitHub部署状态
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        检查GitHub部署状态                                 ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [检查1] 本地Git状态...
git status
echo.

echo [检查2] 最近的提交...
git log --oneline -5
echo.

echo [检查3] 远程仓库信息...
git remote -v
echo.

echo [检查4] 尝试推送到GitHub...
echo.
echo 提示: 如果提示输入凭据:
echo   用户名: 435256553@qq.com
echo   密码: [您的Personal Access Token]
echo.
pause

git push -u origin main
if errorlevel 1 (
    echo.
    echo [信息] 推送可能遇到网络问题
    echo.
    echo 请手动检查:
    echo 1. 访问: https://github.com/yishashawn/stock-prediction
    echo 2. 查看文件是否已上传
    echo 3. 如果文件已存在，说明推送成功
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo [成功] 推送完成！
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo 下一步: 启用GitHub Pages
    echo 1. 访问: https://github.com/yishashawn/stock-prediction/settings/pages
    echo 2. Source: 选择 main 和 / (root)
    echo 3. 点击 Save
    echo 4. 等待1-5分钟，网站即可访问
    echo.
    echo 您的网站地址:
    echo   https://yishashawn.github.io/stock-prediction/
    echo.
)

pause

