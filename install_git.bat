@echo off
chcp 65001 >nul
title 安装Git
color 0B

echo.
echo ========================================
echo 安装Git
echo ========================================
echo.

REM 安装程序路径
set "INSTALLER=C:\工作\项目\13-github\Git-2.49.0-64-bit.exe"

echo [信息] 安装程序路径: %INSTALLER%
echo.

if not exist "%INSTALLER%" (
    echo [错误] 未找到安装程序
    echo 请确认路径是否正确
    echo.
    pause
    exit /b 1
)

echo [步骤1] 正在启动Git安装程序...
echo [提示] 安装程序窗口会弹出，请按照提示完成安装
echo [提示] 特别重要: 选择"Git from the command line and also from 3rd-party software"
echo.

REM 启动安装程序
start "" "%INSTALLER%"

echo.
echo [信息] 安装程序已启动
echo [提示] 请按照安装向导完成安装
echo [提示] 安装完成后，按任意键继续配置...
echo.
pause

echo.
echo [步骤2] 检查安装结果...
timeout /t 2 /nobreak >nul

if exist "C:\Program Files\Git\bin\git.exe" (
    echo [OK] Git安装成功！
    echo.
    "C:\Program Files\Git\bin\git.exe" --version
    echo.
    echo [步骤3] 配置Git用户信息...
    "C:\Program Files\Git\bin\git.exe" config --global user.email "435256553@qq.com"
    "C:\Program Files\Git\bin\git.exe" config --global user.name "syy"
    echo [OK] 用户信息已配置
    echo.
    echo [步骤4] 验证配置...
    "C:\Program Files\Git\bin\git.exe" config --global --list | findstr "user"
    echo.
    echo ========================================
    echo 安装和配置完成！
    echo ========================================
    echo.
    echo 重要提示:
    echo   1. 请关闭并重新打开所有PowerShell/命令提示符窗口
    echo   2. 或重启电脑（推荐）
    echo   3. 然后运行 'git --version' 验证
    echo.
    echo 如果git命令仍无法使用，请运行:
    echo   配置Git并添加到PATH.bat（以管理员身份运行）
    echo.
) else (
    echo [警告] 未找到git.exe
    echo [提示] 可能安装还未完成，请等待安装程序完成
    echo.
)

echo.
pause

