@echo off
chcp 65001 >nul
title Git自动安装工具
color 0A

echo.
echo ========================================
echo    Git for Windows 自动安装工具
echo ========================================
echo.
echo 此工具将帮您自动下载并安装Git
echo.
echo 安装步骤:
echo   1. 自动下载Git安装程序
echo   2. 自动安装Git
echo   3. 自动配置PATH环境变量
echo.
echo 注意: 需要管理员权限
echo.
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 需要管理员权限！
    echo.
    echo 解决方法:
    echo   1. 右键点击此文件
    echo   2. 选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [信息] 检测到管理员权限，继续安装...
echo.

REM 检查是否已安装Git
where git >nul 2>&1
if %errorLevel% equ 0 (
    echo [检测] Git似乎已经安装
    git --version
    echo.
    set /p choice="是否重新安装? (y/n): "
    if /i not "%choice%"=="y" (
        echo 已取消安装
        pause
        exit /b 0
    )
)

echo [步骤1] 正在下载Git安装程序...
echo.

REM Git下载URL（使用官方最新稳定版）
set GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe
set INSTALLER=%TEMP%\GitInstaller.exe

REM 使用PowerShell下载
powershell.exe -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%INSTALLER%' -UseBasicParsing}"

if not exist "%INSTALLER%" (
    echo [错误] 下载失败！
    echo.
    echo 请手动下载Git:
    echo   1. 访问: https://git-scm.com/download/win
    echo   2. 下载并运行安装程序
    echo.
    pause
    exit /b 1
)

echo [成功] 下载完成: %INSTALLER%
echo.

echo [步骤2] 正在安装Git...
echo [提示] 安装程序窗口会弹出，请按照提示完成安装
echo [提示] 建议使用默认安装选项
echo.

REM 静默安装
start /wait "" "%INSTALLER%" /SILENT /NORESTART /DIR="C:\Program Files\Git"

echo.
echo [步骤3] 配置环境变量...
echo.

REM 添加到PATH（使用PowerShell）
set GIT_PATH=C:\Program Files\Git\bin
powershell.exe -Command "$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine'); if ($env:Path -notlike '*%GIT_PATH%*') { $newPath = $env:Path + ';%GIT_PATH%'; [Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine'); Write-Host '已添加到PATH' } else { Write-Host '已在PATH中' }"

echo.
echo ========================================
echo    安装完成！
echo ========================================
echo.
echo 重要提示:
echo   1. 请关闭并重新打开PowerShell/命令提示符
echo   2. 或重启电脑（推荐）
echo   3. 然后运行 'git --version' 验证安装
echo.
echo 下一步操作:
echo   1. 配置Git用户信息:
echo      git config --global user.email "435256553@qq.com"
echo      git config --global user.name "syy"
echo.
echo   2. 创建GitHub Personal Access Token
echo      访问: https://github.com/settings/tokens
echo.
echo   3. 运行部署脚本: 部署到GitHub_Pages.bat
echo.
echo ========================================
echo.

REM 清理安装程序
del "%INSTALLER%" >nul 2>&1

pause

