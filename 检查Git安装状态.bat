@echo off
chcp 65001 >nul
title 检查Git安装状态

echo.
echo ========================================
echo 检查Git安装状态
echo ========================================
echo.

if exist "C:\Program Files\Git\bin\git.exe" (
    echo [OK] Git已安装！
    echo.
    "C:\Program Files\Git\bin\git.exe" --version
    echo.
    echo [配置] 配置Git用户信息...
    "C:\Program Files\Git\bin\git.exe" config --global user.email "435256553@qq.com"
    "C:\Program Files\Git\bin\git.exe" config --global user.name "syy"
    echo [OK] 用户信息已配置
    echo.
    echo [验证] 验证配置...
    "C:\Program Files\Git\bin\git.exe" config --global --list | findstr "user"
    echo.
    echo ========================================
    echo 配置完成！
    echo ========================================
    echo.
    echo 下一步:
    echo   1. 运行: 配置Git并添加到PATH.bat（以管理员身份运行）
    echo   2. 或重启电脑
    echo   3. 然后运行 'git --version' 验证
    echo.
) else (
    echo [警告] Git未安装或安装未完成
    echo.
    echo 请确认:
    echo   1. Git安装程序是否已完成
    echo   2. 是否选择了正确的安装选项
    echo.
    echo 如果未安装，请运行: install_git.bat
    echo.
)

pause

