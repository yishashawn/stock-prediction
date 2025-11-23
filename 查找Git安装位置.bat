@echo off
chcp 65001 >nul
title 查找Git安装位置

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              查找Git安装位置                              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo 正在搜索Git安装位置...
echo.

REM 检查常见安装位置
set "PATHS[0]=C:\Program Files\Git\bin\git.exe"
set "PATHS[1]=C:\Program Files\Git\cmd\git.exe"
set "PATHS[2]=C:\Program Files (x86)\Git\bin\git.exe"
set "PATHS[3]=C:\Program Files (x86)\Git\cmd\git.exe"
set "PATHS[4]=C:\Users\syy\AppData\Local\Programs\Git\bin\git.exe"
set "PATHS[5]=C:\Users\syy\AppData\Local\Programs\Git\cmd\git.exe"

set FOUND=0

for /L %%i in (0,1,5) do (
    call set "TEST_PATH=%%PATHS[%%i]%%"
    if exist "!TEST_PATH!" (
        echo [✓] 找到Git: !TEST_PATH!
        "!TEST_PATH!" --version
        set FOUND=1
        echo.
    )
)

if %FOUND%==0 (
    echo [✗] 未找到Git安装
    echo.
    echo 请检查:
    echo   1. Git是否已正确安装
    echo   2. 安装路径是否正确
    echo.
    echo 或者运行: 安装Git_简化版.bat 重新安装
) else (
    echo [✓] Git已找到并可用
    echo.
    echo 下一步:
    echo   1. 运行: 配置Git环境.bat（需要管理员权限）
    echo   2. 或手动添加到PATH环境变量
)

echo.
pause

