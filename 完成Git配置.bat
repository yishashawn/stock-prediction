@echo off
chcp 65001 >nul
title Git配置完成

echo.
echo ========================================
echo Git配置完成
echo ========================================
echo.

if exist "C:\Program Files\Git\bin\git.exe" (
    echo [OK] Git已安装
    echo.
    "C:\Program Files\Git\bin\git.exe" --version
    echo.
    echo [配置] 用户信息已配置:
    "C:\Program Files\Git\bin\git.exe" config --global --list | findstr "user"
    echo.
    echo ========================================
    echo 配置完成！
    echo ========================================
    echo.
    echo 下一步:
    echo   1. 运行: 配置Git并添加到PATH.bat（以管理员身份运行）
    echo     这将把Git添加到PATH，让您可以在任何地方使用git命令
    echo.
    echo   2. 或重启电脑（推荐）
    echo.
    echo   3. 然后创建GitHub Personal Access Token
    echo      访问: https://github.com/settings/tokens
    echo.
    echo   4. 创建GitHub仓库
    echo      访问: https://github.com/new
    echo.
    echo   5. 运行部署脚本: 部署到GitHub_Pages.bat
    echo.
) else (
    echo [错误] Git未安装
    echo.
    echo 请先运行: install_git.bat
    echo.
)

pause

