@echo off
chcp 65001 >nul
title 配置Git环境变量
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║          Git环境配置工具                                 ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [✗] 需要管理员权限！
    echo.
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [✓] 检测到管理员权限
echo.

REM 查找Git安装位置
echo [步骤1] 正在查找Git安装位置...
echo.

set GIT_PATH=
set GIT_BIN=
set GIT_CMD=

REM 检查常见位置
if exist "C:\Program Files\Git\bin\git.exe" (
    set "GIT_PATH=C:\Program Files\Git"
    set "GIT_BIN=C:\Program Files\Git\bin"
    set "GIT_CMD=C:\Program Files\Git\cmd"
    echo [✓] 找到Git: %GIT_PATH%
    goto :found
)

if exist "C:\Program Files\Git\cmd\git.exe" (
    set "GIT_PATH=C:\Program Files\Git"
    set "GIT_BIN=C:\Program Files\Git\bin"
    set "GIT_CMD=C:\Program Files\Git\cmd"
    echo [✓] 找到Git: %GIT_PATH%
    goto :found
)

if exist "C:\Program Files (x86)\Git\bin\git.exe" (
    set "GIT_PATH=C:\Program Files (x86)\Git"
    set "GIT_BIN=C:\Program Files (x86)\Git\bin"
    set "GIT_CMD=C:\Program Files (x86)\Git\cmd"
    echo [✓] 找到Git: %GIT_PATH%
    goto :found
)

REM 如果都没找到，尝试搜索
echo [信息] 在标准位置未找到，正在搜索...
for /f "delims=" %%i in ('dir /s /b "C:\Program Files\Git\git.exe" 2^>nul') do (
    set "GIT_EXE=%%i"
    for %%j in ("%%~dpi.") do set "GIT_BIN=%%~dpjbin"
    for %%j in ("%%~dpi.") do set "GIT_CMD=%%~dpjcmd"
    for %%j in ("%%~dpi..") do set "GIT_PATH=%%~fj"
    echo [✓] 找到Git: %GIT_PATH%
    goto :found
)

echo [✗] 未找到Git安装
echo.
echo 请确认:
echo   1. Git是否已正确安装
echo   2. 或者运行: 安装Git_简化版.bat 重新安装
echo.
pause
exit /b 1

:found
echo.
echo [步骤2] 测试Git是否可用...
"%GIT_BIN%\git.exe" --version
if %errorLevel% neq 0 (
    echo [✗] Git无法运行
    pause
    exit /b 1
)
echo.

echo [步骤3] 检查PATH环境变量...
echo.

REM 使用PowerShell检查并添加PATH
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine'); $userPath = [Environment]::GetEnvironmentVariable('Path', 'User'); $currentPath = $machinePath + ';' + $userPath; $gitBinInPath = $currentPath -like '*%GIT_BIN%*' -or $currentPath -like '*%GIT_CMD%*'; if ($gitBinInPath) { Write-Host '[✓] Git已在PATH中' } else { Write-Host '[信息] Git未在PATH中，正在添加...'; $newMachinePath = $machinePath; if ($newMachinePath -notlike '*%GIT_BIN%*') { $newMachinePath = $newMachinePath + ';%GIT_BIN%' }; if ($newMachinePath -notlike '*%GIT_CMD%*') { $newMachinePath = $newMachinePath + ';%GIT_CMD%' }; [Environment]::SetEnvironmentVariable('Path', $newMachinePath, 'Machine'); Write-Host '[✓] 已添加到系统PATH环境变量'; Write-Host '[信息] 添加的路径:'; Write-Host '  - %GIT_BIN%'; Write-Host '  - %GIT_CMD%' } }"

echo.
echo [步骤4] 配置Git用户信息...
echo.

"%GIT_BIN%\git.exe" config --global user.email "435256553@qq.com"
"%GIT_BIN%\git.exe" config --global user.name "syy"

echo.
echo [✓] Git用户信息已配置:
"%GIT_BIN%\git.exe" config --global --list | findstr "user"
echo.

echo ╔══════════════════════════════════════════════════════════╗
echo ║              配置完成！                                  ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo ⚠ 重要提示:
echo   1. 请关闭并重新打开所有PowerShell/命令提示符窗口
echo   2. 或重启电脑（推荐，确保环境变量生效）
echo   3. 然后运行 'git --version' 验证
echo.
echo 验证步骤:
echo   1. 关闭此窗口
echo   2. 打开新的PowerShell或命令提示符
echo   3. 运行: git --version
echo   4. 如果显示版本号，说明配置成功！
echo.
echo 下一步:
echo   1. 创建GitHub Personal Access Token
echo      访问: https://github.com/settings/tokens
echo      创建新Token，权限选择 'repo'
echo.
echo   2. 创建GitHub仓库
echo      访问: https://github.com/new
echo      创建Public仓库
echo.
echo   3. 运行部署脚本: 部署到GitHub_Pages.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause

