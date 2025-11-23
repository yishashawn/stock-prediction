@echo off
chcp 65001 >nul
title 快速推送到GitHub
color 0A

echo.
echo ========================================
echo 快速推送到GitHub
echo ========================================
echo.

set "PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

echo [信息] 远程仓库: https://github.com/yishashawn/zhongji.git
echo.

echo [提示] 即将推送到GitHub
echo [提示] 如果提示输入密码，请使用Personal Access Token
echo.
echo 如果还没有Token，请:
echo   1. 访问: https://github.com/settings/tokens
echo   2. 创建新Token，权限选择 'repo'
echo   3. 复制Token
echo.
pause

echo.
echo [执行] 正在推送...
echo.

git push origin main

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo 推送成功！
    echo ========================================
    echo.
    echo 下一步: 启用GitHub Pages
    echo   1. 访问: https://github.com/yishashawn/zhongji
    echo   2. Settings → Pages
    echo   3. Source: 选择 main 分支
    echo   4. 点击 Save
    echo.
    echo 您的网站地址:
    echo   https://yishashawn.github.io/zhongji/中际旭创_价格预测.html
    echo.
) else (
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
    echo   3. 或查看: 最后一步_推送到GitHub.md
    echo.
)

echo.
pause

