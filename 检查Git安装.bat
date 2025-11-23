@echo off
chcp 65001 >nul
title 检查Git安装

echo.
echo 正在检查Git安装...
echo.

if exist "C:\Program Files\Git" (
    echo [✓] Git目录存在: C:\Program Files\Git
    echo.
    echo 目录内容:
    dir "C:\Program Files\Git" /b
    echo.
    echo 正在搜索git.exe...
    dir "C:\Program Files\Git" /s /b | findstr /i "git.exe"
) else (
    echo [✗] Git目录不存在
)

echo.
pause

