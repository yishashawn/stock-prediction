@echo off
chcp 65001 >nul
title 添加Git到PATH
color 0B

echo.
echo ========================================
echo 添加Git到PATH环境变量
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 需要管理员权限！
    echo.
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [OK] 检测到管理员权限
echo.

set "GIT_BIN=C:\Program Files\Git\bin"
set "GIT_CMD=C:\Program Files\Git\cmd"

echo [步骤1] 检查Git路径...
if exist "%GIT_BIN%\git.exe" (
    echo [OK] Git已安装: %GIT_BIN%
) else (
    echo [错误] Git未安装
    pause
    exit /b 1
)

echo.
echo [步骤2] 添加到PATH环境变量...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine'); if ($machinePath -notlike '*%GIT_BIN%*') { $newPath = $machinePath + ';%GIT_BIN%;%GIT_CMD%'; [Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine'); Write-Host '[OK] 已添加到系统PATH' } else { Write-Host '[OK] Git已在PATH中' } }"

echo.
echo ========================================
echo 配置完成！
echo ========================================
echo.
echo 重要提示:
echo   1. 请关闭并重新打开所有PowerShell/命令提示符窗口
echo   2. 或重启电脑（推荐）
echo   3. 然后运行 'git --version' 验证
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

pause

