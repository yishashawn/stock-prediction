@echo off
chcp 65001 >nul
title 从指定位置安装Git
color 0B

echo.
echo ========================================
echo 从指定位置安装Git
echo ========================================
echo.

set "INSTALLER=C:\工作\项目\13-github\Git-2.49.0-64-bit.exe"

if not exist "%INSTALLER%" (
    echo [错误] 未找到安装程序: %INSTALLER%
    echo.
    pause
    exit /b 1
)

echo [信息] 找到安装程序: %INSTALLER%
echo.
echo [步骤1] 正在安装Git...
echo [提示] 安装程序窗口会弹出，请按照提示完成安装
echo [提示] 建议使用默认安装选项
echo [提示] 特别重要: 选择"Git from the command line and also from 3rd-party software"
echo.

REM 启动安装程序（非静默，让用户看到安装过程）
start /wait "" "%INSTALLER%"

echo.
echo [步骤2] 等待安装完成...
timeout /t 3 /nobreak >nul

echo.
echo [步骤3] 检查安装结果...
if exist "C:\Program Files\Git\bin\git.exe" (
    echo [OK] Git安装成功！
    echo.
    "C:\Program Files\Git\bin\git.exe" --version
    echo.
    echo [步骤4] 配置Git用户信息...
    "C:\Program Files\Git\bin\git.exe" config --global user.email "435256553@qq.com"
    "C:\Program Files\Git\bin\git.exe" config --global user.name "syy"
    echo [OK] 用户信息已配置
    echo.
    echo [步骤5] 验证配置...
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
    echo [警告] 未找到git.exe，可能安装未完成
    echo.
    echo 请检查:
    echo   1. 安装程序是否正常完成
    echo   2. 是否有错误提示
    echo.
    echo 如果安装失败，请手动运行安装程序:
    echo   %INSTALLER%
    echo.
)

echo.
pause

