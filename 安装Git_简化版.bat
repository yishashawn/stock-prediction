@echo off
chcp 65001 >nul
title Git安装助手
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║          Git for Windows 安装助手                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 此工具将帮您安装Git
echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [✗] 需要管理员权限！
    echo.
    echo 请按照以下步骤操作:
    echo   1. 关闭此窗口
    echo   2. 右键点击此文件
    echo   3. 选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [✓] 检测到管理员权限
echo.

REM 检查是否已安装Git
where git >nul 2>&1
if %errorLevel% equ 0 (
    echo [信息] 检测到Git已安装:
    git --version
    echo.
    set /p choice="是否重新安装? (y/n): "
    if /i not "%choice%"=="y" (
        echo 已取消
        pause
        exit /b 0
    )
)

echo [步骤1/3] 正在下载Git安装程序...
echo 这可能需要几分钟，请耐心等待...
echo.

REM 使用最新稳定版本
set GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe
set INSTALLER=%TEMP%\GitInstaller.exe

REM 使用PowerShell下载（支持TLS 1.2）
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; try { Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%INSTALLER%' -UseBasicParsing -ErrorAction Stop; Write-Host '[✓] 下载完成' } catch { Write-Host '[✗] 下载失败:' $_.Exception.Message; exit 1 } }"

if not exist "%INSTALLER%" (
    echo.
    echo [✗] 下载失败！
    echo.
    echo 请手动下载Git:
    echo   1. 访问: https://git-scm.com/download/win
    echo   2. 下载并运行安装程序
    echo   3. 使用默认安装选项
    echo.
    echo 详细步骤请查看: 手动安装Git指南.md
    echo.
    pause
    exit /b 1
)

echo.
echo [步骤2/3] 正在安装Git...
echo [提示] 安装程序窗口会弹出，请按照提示完成安装
echo [提示] 建议使用默认安装选项（直接点击Next）
echo [提示] 特别重要: 选择"Git from the command line and also from 3rd-party software"
echo.

REM 启动安装程序（非静默，让用户看到安装过程）
start /wait "" "%INSTALLER%"

echo.
echo [步骤3/3] 配置环境变量...
echo.

REM 检查Git是否安装成功
if exist "C:\Program Files\Git\bin\git.exe" (
    echo [✓] Git已安装到: C:\Program Files\Git
    echo.
    
    REM 添加到PATH
    set GIT_BIN=C:\Program Files\Git\bin
    set GIT_CMD=C:\Program Files\Git\cmd
    
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine'); if ($machinePath -notlike '*%GIT_BIN%*') { $newPath = $machinePath + ';%GIT_BIN%;%GIT_CMD%'; [Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine'); Write-Host '[✓] 已添加到PATH环境变量' } else { Write-Host '[✓] Git已在PATH中' } }"
    
    echo.
    echo ╔══════════════════════════════════════════════════════════╗
    echo ║              安装完成！                                 ║
    echo ╚══════════════════════════════════════════════════════════╝
    echo.
    echo ⚠ 重要提示:
    echo   1. 请关闭并重新打开所有PowerShell/命令提示符窗口
    echo   2. 或重启电脑（推荐，确保环境变量生效）
    echo   3. 然后运行 'git --version' 验证安装
    echo.
    echo 下一步操作:
    echo   1. 配置Git用户信息（在新的PowerShell中运行）:
    echo      git config --global user.email "435256553@qq.com"
    echo      git config --global user.name "syy"
    echo.
    echo   2. 创建GitHub Personal Access Token:
    echo      访问: https://github.com/settings/tokens
    echo      创建新Token，权限选择 'repo'
    echo.
    echo   3. 运行部署脚本: 部署到GitHub_Pages.bat
    echo.
    
) else (
    echo [✗] 安装可能未完成
    echo.
    echo 请检查:
    echo   1. 安装程序是否正常完成
    echo   2. 是否有错误提示
    echo.
    echo 如果安装失败，请查看: 手动安装Git指南.md
    echo.
)

REM 清理安装程序
del "%INSTALLER%" >nul 2>&1

echo ═══════════════════════════════════════════════════════════
echo.
pause

