@echo off
chcp 65001 >nul
title 配置Git环境
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              配置Git环境变量                              ║
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

REM 检查Git是否已安装
if exist "C:\Program Files\Git\bin\git.exe" (
    echo [✓] 检测到Git已安装: C:\Program Files\Git
    echo.
    
    REM 测试Git是否可用
    "C:\Program Files\Git\bin\git.exe" --version
    echo.
) else (
    echo [✗] 未找到Git安装
    echo.
    echo 请先安装Git
    pause
    exit /b 1
)

echo [步骤1] 检查PATH环境变量...
echo.

REM 检查PATH中是否包含Git
set GIT_BIN=C:\Program Files\Git\bin
set GIT_CMD=C:\Program Files\Git\cmd

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine'); $userPath = [Environment]::GetEnvironmentVariable('Path', 'User'); $currentPath = $machinePath + ';' + $userPath; if ($currentPath -like '*%GIT_BIN%*' -or $currentPath -like '*%GIT_CMD%*') { Write-Host '[✓] Git已在PATH中' } else { Write-Host '[✗] Git未在PATH中，正在添加...'; $newMachinePath = $machinePath + ';%GIT_BIN%;%GIT_CMD%'; [Environment]::SetEnvironmentVariable('Path', $newMachinePath, 'Machine'); Write-Host '[✓] 已添加到系统PATH环境变量' } }"

echo.
echo [步骤2] 配置Git用户信息...
echo.

REM 配置Git用户信息
"C:\Program Files\Git\bin\git.exe" config --global user.email "435256553@qq.com"
"C:\Program Files\Git\bin\git.exe" config --global user.name "syy"

echo.
echo [✓] Git用户信息已配置:
"C:\Program Files\Git\bin\git.exe" config --global --list | findstr "user"
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
echo 下一步:
echo   1. 创建GitHub Personal Access Token
echo      访问: https://github.com/settings/tokens
echo.
echo   2. 创建GitHub仓库
echo      访问: https://github.com/new
echo.
echo   3. 运行部署脚本: 部署到GitHub_Pages.bat
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause

